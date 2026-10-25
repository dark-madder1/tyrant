"""
RedTeam Code Studio — AI-powered multi-agent coding IDE.
VS Code / Cursor-inspired interface running on HuggingFace ZeroGPU.
"""

import os
import re
import json
import spaces
import torch
import gradio as gr
from threading import Thread
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

from agents import AGENTS, WELCOME_TEMPLATES, get_agent, get_agent_choices

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL_ID = "frEEtom3/redteam-coder-4b"

tokenizer = None
model = None


def load_model():
    global tokenizer, model
    if model is not None:
        return
    token = os.environ.get("HF_TOKEN")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, token=token, trust_remote_code=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()


# ---------------------------------------------------------------------------
# Virtual file system (session-scoped, lives in gr.State)
# ---------------------------------------------------------------------------
DEFAULT_FILES = {
    "main.py": (
        '"""Your project starts here."""\n\n'
        "def main():\n"
        '    print("Hello from RedTeam Code Studio!")\n\n\n'
        'if __name__ == "__main__":\n'
        "    main()\n"
    ),
    "README.md": "# My Project\n\nBuilt with RedTeam Code Studio.\n",
}


def new_fs():
    return dict(DEFAULT_FILES)


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
@spaces.GPU(duration=120)
def run_inference(agent_key, chat_history, user_msg, temperature, top_p, max_tokens):
    """Run model inference for a given agent. Streams tokens back."""
    load_model()

    agent = get_agent(agent_key)
    messages = [{"role": "system", "content": agent["system_prompt"]}]
    for turn in chat_history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_msg})

    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    gen_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=int(max_tokens),
        temperature=float(temperature) if temperature > 0 else 1e-7,
        top_p=float(top_p),
        do_sample=temperature > 0,
        streamer=streamer,
    )
    thread = Thread(target=model.generate, kwargs=gen_kwargs)
    thread.start()

    output = ""
    for chunk in streamer:
        output += chunk
        yield output
    thread.join()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

LANG_EXTENSIONS = {
    "python": ".py", "py": ".py", "javascript": ".js", "js": ".js",
    "typescript": ".ts", "ts": ".ts", "rust": ".rs", "go": ".go",
    "c": ".c", "cpp": ".cpp", "java": ".java", "html": ".html",
    "css": ".css", "bash": ".sh", "sh": ".sh", "sql": ".sql",
    "yaml": ".yaml", "yml": ".yaml", "json": ".json", "toml": ".toml",
    "dockerfile": "Dockerfile", "markdown": ".md", "md": ".md",
}

EXT_TO_GRADIO_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".rs": "rust", ".go": "go", ".c": "c", ".cpp": "cpp",
    ".java": "java", ".html": "html", ".css": "css", ".sh": "shell",
    ".sql": "sql", ".yaml": "yaml", ".json": "json", ".toml": "toml",
    ".md": "markdown",
}


def detect_lang(filename):
    for ext, lang in EXT_TO_GRADIO_LANG.items():
        if filename.endswith(ext):
            return lang
    return "python"


def extract_code_blocks(text):
    """Pull fenced code blocks from an agent response."""
    blocks = []
    for lang, code in CODE_BLOCK_RE.findall(text):
        blocks.append((lang.strip().lower(), code.strip()))
    return blocks


def code_to_filename(lang, index, fs):
    """Generate a sensible filename for extracted code."""
    ext = LANG_EXTENSIONS.get(lang, ".py")
    if ext.startswith("."):
        base = f"generated_{index}{ext}"
    else:
        base = ext
    counter = 1
    name = base
    while name in fs:
        name = f"generated_{index}_{counter}{LANG_EXTENSIONS.get(lang, '.py')}"
        counter += 1
    return name


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------
def send_message(user_msg, agent_key, chat_history, fs, temperature, top_p, max_tokens):
    """Stream agent response, then extract code blocks into the file system."""
    if not user_msg or not user_msg.strip():
        yield chat_history, fs, file_list_html(fs), "", gr.update(), gr.update()
        return

    chat_history = list(chat_history) + [{"role": "user", "content": user_msg}]
    partial = ""

    for chunk in run_inference(agent_key, chat_history[:-1], user_msg, temperature, top_p, max_tokens):
        partial = chunk
        streaming_history = chat_history + [{"role": "assistant", "content": partial}]
        yield streaming_history, fs, file_list_html(fs), "", gr.update(), gr.update()

    chat_history.append({"role": "assistant", "content": partial})

    blocks = extract_code_blocks(partial)
    first_new_file = None
    first_new_content = None
    for i, (lang, code) in enumerate(blocks):
        fname = code_to_filename(lang, i + 1, fs)
        fs[fname] = code
        if first_new_file is None:
            first_new_file = fname
            first_new_content = code

    if first_new_file:
        lang = detect_lang(first_new_file)
        yield (
            chat_history, fs, file_list_html(fs), "",
            gr.update(value=first_new_content, language=lang, label=first_new_file),
            gr.update(value=first_new_file),
        )
    else:
        yield chat_history, fs, file_list_html(fs), "", gr.update(), gr.update()


def open_file(filename, fs):
    """Open a file from the virtual file system into the editor."""
    content = fs.get(filename, "")
    lang = detect_lang(filename)
    return gr.update(value=content, language=lang, label=filename), filename


def save_file(filename, content, fs):
    """Save current editor content back to the virtual file system."""
    if filename:
        fs[filename] = content
    return fs, file_list_html(fs)


def create_new_file(filename, fs):
    """Create a new empty file."""
    if not filename or not filename.strip():
        return fs, file_list_html(fs), gr.update(), ""
    filename = filename.strip()
    if filename not in fs:
        fs[filename] = ""
    lang = detect_lang(filename)
    return (
        fs,
        file_list_html(fs),
        gr.update(value="", language=lang, label=filename),
        filename,
    )


def delete_file(filename, fs):
    """Delete a file from the virtual file system."""
    if filename in fs:
        del fs[filename]
    remaining = list(fs.keys())
    if remaining:
        first = remaining[0]
        lang = detect_lang(first)
        return (
            fs, file_list_html(fs),
            gr.update(value=fs[first], language=lang, label=first), first,
        )
    return fs, file_list_html(fs), gr.update(value="", label="No file open"), ""


def load_template(idx, fs):
    """Load a starter template prompt."""
    t = WELCOME_TEMPLATES[int(idx)]
    return t["prompt"], t["agent"]


def run_orchestrator(task_description, fs, temperature, top_p, max_tokens):
    """Run the orchestrator to decompose a task, then execute each subtask."""
    if not task_description.strip():
        yield "", [], fs, file_list_html(fs)
        return

    status_lines = [f"Orchestrator analyzing task...\n"]
    yield "\n".join(status_lines), [], fs, file_list_html(fs)

    plan_text = ""
    for chunk in run_inference("orchestrator", [], task_description, 0.3, 0.9, max_tokens):
        plan_text = chunk

    try:
        json_match = re.search(r"\{.*\}", plan_text, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            plan = {"plan": []}
    except json.JSONDecodeError:
        plan = {"plan": []}

    subtasks = plan.get("plan", [])
    if not subtasks:
        status_lines.append("Could not parse plan. Raw response:\n" + plan_text)
        yield "\n".join(status_lines), [], fs, file_list_html(fs)
        return

    status_lines.append(f"Plan: {len(subtasks)} subtasks\n")
    for i, st in enumerate(subtasks):
        agent = get_agent(st.get("agent", "builder"))
        status_lines.append(
            f"  [{i+1}] {agent['icon']} {agent['name']}: {st['task']}"
        )
    status_lines.append("")
    yield "\n".join(status_lines), subtasks, fs, file_list_html(fs)

    results = []
    for i, st in enumerate(subtasks):
        agent_key = st.get("agent", "builder")
        agent = get_agent(agent_key)
        prompt = (
            f"Task: {st['task']}\n"
            f"Expected output file: {st.get('output', 'code')}\n"
            f"Write the complete code or content. Be thorough."
        )
        status_lines.append(
            f"Running [{i+1}/{len(subtasks)}] {agent['icon']} {st['task']}..."
        )
        yield "\n".join(status_lines), subtasks, fs, file_list_html(fs)

        response = ""
        for chunk in run_inference(agent_key, [], prompt, temperature, top_p, max_tokens):
            response = chunk

        blocks = extract_code_blocks(response)
        if blocks:
            for j, (lang, code) in enumerate(blocks):
                output_name = st.get("output", "")
                if output_name and "." in output_name and j == 0:
                    fname = output_name
                else:
                    fname = code_to_filename(lang, len(fs) + 1, fs)
                fs[fname] = code
                status_lines.append(f"  -> Created {fname}")
        else:
            fname = st.get("output", f"task_{i+1}.txt")
            fs[fname] = response
            status_lines.append(f"  -> Created {fname}")

        results.append({"task": st["task"], "agent": agent_key, "done": True})
        status_lines.append(f"  Done!\n")
        yield "\n".join(status_lines), subtasks, fs, file_list_html(fs)

    status_lines.append("All subtasks complete!")
    yield "\n".join(status_lines), subtasks, fs, file_list_html(fs)


# ---------------------------------------------------------------------------
# UI renderers
# ---------------------------------------------------------------------------
FILE_ICONS = {
    ".py": "\U0001f40d", ".js": "\U0001f7e8", ".ts": "\U0001f535",
    ".html": "\U0001f310", ".css": "\U0001f3a8", ".json": "{ }",
    ".md": "\U0001f4dd", ".sh": "⚡", ".rs": "⚙️",
    ".go": "\U0001f439", ".c": "\U0001f1e8", ".cpp": "\U0001f1e8",
    ".toml": "⚙️", ".yaml": "⚙️", ".sql": "\U0001f4be",
}


def file_icon(name):
    for ext, icon in FILE_ICONS.items():
        if name.endswith(ext):
            return icon
    return "\U0001f4c4"


def file_list_html(fs):
    if not fs:
        return "<div class='file-empty'>No files yet</div>"
    items = []
    for name in sorted(fs.keys()):
        icon = file_icon(name)
        size = len(fs[name])
        items.append(
            f"<div class='file-item' title='{name} ({size} bytes)'>"
            f"<span class='file-icon'>{icon}</span>"
            f"<span class='file-name'>{name}</span>"
            f"</div>"
        )
    return "\n".join(items)


def agent_status_html(subtasks):
    if not subtasks:
        return ""
    rows = []
    for i, st in enumerate(subtasks):
        agent = get_agent(st.get("agent", "builder"))
        done = st.get("done", False)
        status = "Done" if done else "Pending"
        badge = "badge-done" if done else "badge-pending"
        rows.append(
            f"<div class='task-row'>"
            f"<span class='task-num'>#{i+1}</span>"
            f"<span class='task-agent'>{agent['icon']}</span>"
            f"<span class='task-desc'>{st.get('task', '')}</span>"
            f"<span class='task-badge {badge}'>{status}</span>"
            f"</div>"
        )
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# CSS — VS Code / Cursor dark theme
# ---------------------------------------------------------------------------
CSS = """
/* ── Base ── */
.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    background: #1e1e1e !important;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}
.main, .contain { gap: 0 !important; }
footer { display: none !important; }

/* ── Top bar ── */
.topbar {
    background: #323233;
    color: #cccccc;
    padding: 6px 16px;
    font-size: 13px;
    border-bottom: 1px solid #3c3c3c;
    display: flex;
    align-items: center;
    gap: 12px;
}
.topbar-title {
    font-weight: 600;
    color: #ffffff;
    font-size: 14px;
}
.topbar-subtitle { color: #888; font-size: 12px; }

/* ── Sidebar ── */
.sidebar {
    background: #252526 !important;
    border-right: 1px solid #3c3c3c;
    min-height: 75vh;
    padding: 0 !important;
}
.sidebar-header {
    color: #bbbbbb;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px 16px 8px;
    border-bottom: 1px solid #3c3c3c;
}

/* ── File explorer ── */
.file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 16px;
    cursor: pointer;
    color: #cccccc;
    font-size: 13px;
    font-family: 'Segoe UI', sans-serif;
    transition: background 0.1s;
}
.file-item:hover { background: #2a2d2e; }
.file-icon { font-size: 14px; width: 18px; text-align: center; }
.file-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-empty { color: #666; padding: 16px; font-size: 13px; text-align: center; }

/* ── Editor area ── */
.editor-area {
    background: #1e1e1e !important;
    min-height: 75vh;
    padding: 0 !important;
}
.editor-area .cm-editor {
    font-size: 14px !important;
    min-height: 50vh !important;
}
.editor-area textarea {
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace !important;
    font-size: 14px !important;
}

/* ── Chat panel ── */
.chat-panel {
    background: #252526 !important;
    border-left: 1px solid #3c3c3c;
    min-height: 75vh;
    padding: 0 !important;
}
.chat-panel .chatbot {
    background: #1e1e1e !important;
    border: none !important;
}

/* ── Agent selector ── */
.agent-card {
    background: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 4px 12px;
    cursor: pointer;
    transition: all 0.15s;
}
.agent-card:hover {
    background: #37373d;
    border-color: #007acc;
}
.agent-card-active {
    border-color: #007acc !important;
    background: #1a3a5c !important;
}

/* ── Task board ── */
.task-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    font-size: 13px;
    color: #cccccc;
    border-bottom: 1px solid #333;
}
.task-num { color: #666; font-weight: 600; width: 24px; }
.task-agent { font-size: 16px; width: 24px; }
.task-desc { flex: 1; }
.task-badge {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
}
.badge-done { background: #1a3a2a; color: #4ade80; }
.badge-pending { background: #3a2a1a; color: #fbbf24; }

/* ── Buttons ── */
.action-btn {
    background: #0e639c !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    transition: background 0.15s !important;
}
.action-btn:hover { background: #1177bb !important; }
.danger-btn {
    background: #c53030 !important;
    border: none !important;
    color: #fff !important;
}

/* ── Template cards ── */
.template-card {
    background: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 14px;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    min-height: 100px;
}
.template-card:hover {
    background: #37373d;
    border-color: #007acc;
    transform: translateY(-2px);
}
.template-icon { font-size: 28px; margin-bottom: 6px; }
.template-name { font-weight: 600; color: #fff; font-size: 14px; }
.template-desc { color: #999; font-size: 12px; margin-top: 4px; }

/* ── Status bar ── */
.statusbar {
    background: #007acc;
    color: #fff;
    font-size: 12px;
    padding: 3px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.statusbar-section { display: flex; gap: 16px; align-items: center; }

/* ── Misc overrides ── */
.dark .block { border: none !important; }
.dark label { color: #ccc !important; }
.dark .tab-nav button {
    color: #999 !important;
    border: none !important;
    background: #2d2d2d !important;
}
.dark .tab-nav button.selected {
    color: #fff !important;
    background: #1e1e1e !important;
    border-bottom: 2px solid #007acc !important;
}
"""


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
theme = gr.themes.Base(
    primary_hue="blue",
    neutral_hue="gray",
    font=gr.themes.GoogleFont("Inter"),
    font_mono=gr.themes.GoogleFont("JetBrains Mono"),
).set(
    body_background_fill="#1e1e1e",
    block_background_fill="#1e1e1e",
    input_background_fill="#3c3c3c",
    button_primary_background_fill="#0e639c",
)

with gr.Blocks(css=CSS, theme=theme, title="RedTeam Code Studio") as demo:

    # -- State --
    fs_state = gr.State(new_fs)
    current_file = gr.State("main.py")
    subtasks_state = gr.State([])

    # ================================================================
    # TOP BAR
    # ================================================================
    gr.HTML(
        "<div class='topbar'>"
        "<span class='topbar-title'>\U0001f9e0 RedTeam Code Studio</span>"
        "<span class='topbar-subtitle'>AI-Powered Multi-Agent IDE</span>"
        "</div>"
    )

    # ================================================================
    # MAIN LAYOUT
    # ================================================================
    with gr.Tabs() as main_tabs:

        # ============================================================
        # TAB 1: WELCOME / QUICK START
        # ============================================================
        with gr.Tab("⌂ Home", id="home"):
            gr.Markdown(
                "## Welcome to RedTeam Code Studio\n"
                "Pick a template to get started, or switch to the **Editor** "
                "tab to start from scratch.\n\n"
                "**How it works:** Choose an AI agent, describe what you want, "
                "and the agent writes the code directly into your editor. "
                "For big projects, use the **Orchestrator** to split work "
                "across multiple agents automatically."
            )
            gr.Markdown("### Quick Start Templates")
            with gr.Row():
                template_btns = []
                for i, t in enumerate(WELCOME_TEMPLATES):
                    with gr.Column(scale=1, min_width=140):
                        btn = gr.Button(
                            f"{t['icon']}\n{t['name']}\n{t['description']}",
                            elem_classes=["template-card"],
                            size="lg",
                        )
                        template_btns.append((btn, i))

            gr.Markdown(
                "### Your Agents\n"
                "Each agent is a specialist. Pick the right one for the job:"
            )
            with gr.Row():
                for key, agent in AGENTS.items():
                    with gr.Column(scale=1, min_width=140):
                        gr.Markdown(
                            f"**{agent['icon']} {agent['name']}**\n\n"
                            f"{agent['description']}"
                        )

        # ============================================================
        # TAB 2: EDITOR + CHAT (the main IDE view)
        # ============================================================
        with gr.Tab("✎ Editor", id="editor"):
            with gr.Row(equal_height=True):

                # ---- LEFT SIDEBAR: Files ----
                with gr.Column(scale=1, min_width=200, elem_classes=["sidebar"]):
                    gr.HTML("<div class='sidebar-header'>Explorer</div>")
                    file_list = gr.HTML(value=file_list_html(DEFAULT_FILES))

                    file_selector = gr.Dropdown(
                        choices=list(DEFAULT_FILES.keys()),
                        value="main.py",
                        label="Open File",
                        interactive=True,
                    )
                    open_btn = gr.Button("Open", size="sm", elem_classes=["action-btn"])

                    gr.HTML("<div class='sidebar-header'>New File</div>")
                    new_file_name = gr.Textbox(
                        placeholder="e.g. exploit.py",
                        label="Filename",
                        show_label=False,
                    )
                    with gr.Row():
                        create_btn = gr.Button(
                            "+ New", size="sm", elem_classes=["action-btn"]
                        )
                        delete_btn = gr.Button(
                            "Delete", size="sm", elem_classes=["danger-btn"]
                        )

                    gr.HTML("<div class='sidebar-header'>Agent</div>")
                    agent_select = gr.Radio(
                        choices=get_agent_choices(),
                        value="red_team",
                        label="Active Agent",
                        show_label=False,
                    )

                # ---- CENTER: Code Editor ----
                with gr.Column(scale=3, elem_classes=["editor-area"]):
                    code_editor = gr.Code(
                        value=DEFAULT_FILES["main.py"],
                        language="python",
                        label="main.py",
                        lines=28,
                        interactive=True,
                    )
                    with gr.Row():
                        save_btn = gr.Button(
                            "\U0001f4be Save", size="sm", elem_classes=["action-btn"]
                        )
                        insert_info = gr.Markdown(
                            "*Code from AI responses is auto-saved to new files.*",
                        )

                # ---- RIGHT SIDEBAR: AI Chat ----
                with gr.Column(scale=2, min_width=300, elem_classes=["chat-panel"]):
                    gr.HTML("<div class='sidebar-header'>AI Chat</div>")
                    chatbot = gr.Chatbot(
                        type="messages",
                        height=380,
                        show_copy_button=True,
                        placeholder="Ask your agent to write code...",
                    )
                    with gr.Row():
                        chat_input = gr.Textbox(
                            placeholder="Describe what you want to build...",
                            label="Message",
                            show_label=False,
                            scale=4,
                            lines=2,
                        )
                        send_btn = gr.Button(
                            "▶", size="sm", scale=1,
                            elem_classes=["action-btn"],
                        )

                    with gr.Accordion("Generation Settings", open=False):
                        temperature = gr.Slider(
                            0.0, 2.0, value=0.7, step=0.05, label="Temperature"
                        )
                        top_p = gr.Slider(
                            0.0, 1.0, value=0.9, step=0.05, label="Top-p"
                        )
                        max_tokens = gr.Slider(
                            128, 4096, value=2048, step=128, label="Max Tokens"
                        )
                    clear_btn = gr.Button(
                        "Clear Chat", size="sm", variant="secondary"
                    )

        # ============================================================
        # TAB 3: ORCHESTRATOR (multi-agent task runner)
        # ============================================================
        with gr.Tab("\U0001f680 Orchestrator", id="orchestrator"):
            gr.Markdown(
                "## Multi-Agent Task Runner\n"
                "Describe a **big project** and the Orchestrator will break it "
                "into subtasks, assign each to the best agent, and run them "
                "all automatically. Results land in your file explorer.\n\n"
                "**Example:** *Build a complete vulnerability scanner with port "
                "scanning, HTTP header checks, SSL analysis, and HTML reports.*"
            )
            with gr.Row():
                with gr.Column(scale=2):
                    task_input = gr.Textbox(
                        placeholder=(
                            "Describe a large project or complex task...\n"
                            "The orchestrator will split it into subtasks "
                            "and assign agents."
                        ),
                        label="Task Description",
                        lines=4,
                    )
                    run_btn = gr.Button(
                        "\U0001f680 Run Orchestrator",
                        variant="primary",
                        size="lg",
                        elem_classes=["action-btn"],
                    )
                with gr.Column(scale=1):
                    orch_temp = gr.Slider(
                        0.0, 2.0, value=0.7, step=0.05, label="Temperature"
                    )
                    orch_top_p = gr.Slider(
                        0.0, 1.0, value=0.9, step=0.05, label="Top-p"
                    )
                    orch_max_tokens = gr.Slider(
                        256, 4096, value=2048, step=128, label="Max Tokens"
                    )

            orch_status = gr.Textbox(
                label="Orchestrator Log",
                lines=18,
                interactive=False,
            )
            task_board = gr.HTML(label="Task Board")

    # ================================================================
    # STATUS BAR
    # ================================================================
    gr.HTML(
        "<div class='statusbar'>"
        "<div class='statusbar-section'>"
        "<span>\U0001f534 RedTeam Code Studio</span>"
        "<span>Model: frEEtom3/redteam-coder-4b</span>"
        "</div>"
        "<div class='statusbar-section'>"
        "<span>ZeroGPU (A10G)</span>"
        "<span>UTF-8</span>"
        "</div>"
        "</div>"
    )

    # ================================================================
    # EVENT WIRING
    # ================================================================

    # -- Chat --
    send_btn.click(
        send_message,
        inputs=[chat_input, agent_select, chatbot, fs_state, temperature, top_p, max_tokens],
        outputs=[chatbot, fs_state, file_list, chat_input, code_editor, current_file],
    )
    chat_input.submit(
        send_message,
        inputs=[chat_input, agent_select, chatbot, fs_state, temperature, top_p, max_tokens],
        outputs=[chatbot, fs_state, file_list, chat_input, code_editor, current_file],
    )
    clear_btn.click(lambda: [], outputs=[chatbot])

    # -- File management --
    def _open_file(filename, fs):
        if filename in fs:
            content = fs[filename]
            lang = detect_lang(filename)
            return gr.update(value=content, language=lang, label=filename), filename
        return gr.update(), filename

    open_btn.click(
        _open_file,
        inputs=[file_selector, fs_state],
        outputs=[code_editor, current_file],
    )
    file_selector.change(
        _open_file,
        inputs=[file_selector, fs_state],
        outputs=[code_editor, current_file],
    )

    save_btn.click(
        save_file,
        inputs=[current_file, code_editor, fs_state],
        outputs=[fs_state, file_list],
    )

    def _create_file(name, fs):
        if not name or not name.strip():
            return fs, file_list_html(fs), gr.update(), gr.update(), ""
        name = name.strip()
        fs[name] = ""
        lang = detect_lang(name)
        choices = sorted(fs.keys())
        return (
            fs, file_list_html(fs),
            gr.update(value="", language=lang, label=name),
            gr.update(choices=choices, value=name),
            name,
        )

    create_btn.click(
        _create_file,
        inputs=[new_file_name, fs_state],
        outputs=[fs_state, file_list, code_editor, file_selector, current_file],
    )

    def _delete_file(name, fs):
        if name in fs:
            del fs[name]
        remaining = sorted(fs.keys())
        if remaining:
            first = remaining[0]
            lang = detect_lang(first)
            return (
                fs, file_list_html(fs),
                gr.update(value=fs[first], language=lang, label=first),
                gr.update(choices=remaining, value=first),
                first,
            )
        return (
            fs, file_list_html(fs),
            gr.update(value="", label="No file"),
            gr.update(choices=[], value=None),
            "",
        )

    delete_btn.click(
        _delete_file,
        inputs=[current_file, fs_state],
        outputs=[fs_state, file_list, code_editor, file_selector, current_file],
    )

    # -- Update dropdown when fs changes --
    def _sync_dropdown(fs):
        return gr.update(choices=sorted(fs.keys()))

    fs_state.change(_sync_dropdown, inputs=[fs_state], outputs=[file_selector])

    # -- Templates --
    for btn, idx in template_btns:
        def _make_loader(i):
            def _load(fs):
                t = WELCOME_TEMPLATES[i]
                return t["prompt"], t["agent"], gr.update(selected="editor")
            return _load

        btn.click(
            _make_loader(idx),
            inputs=[fs_state],
            outputs=[chat_input, agent_select, main_tabs],
        )

    # -- Orchestrator --
    run_btn.click(
        run_orchestrator,
        inputs=[task_input, fs_state, orch_temp, orch_top_p, orch_max_tokens],
        outputs=[orch_status, subtasks_state, fs_state, file_list],
    )

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
