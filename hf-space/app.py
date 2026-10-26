"""
Red Team Coder 4B — Interactive Demo
Gradio chat interface running on ZeroGPU (Hugging Face Spaces).
"""

import os
import spaces
import torch
import gradio as gr
from threading import Thread
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL_ID = "frEEtom3/redteam-coder-4b"

DEFAULT_SYSTEM_PROMPT = (
    "You are Red Team Coder, an expert AI assistant specialized in "
    "offensive security, penetration testing, exploit development, "
    "and security-focused code generation. You provide detailed, "
    "technically accurate responses for authorized security research "
    "and educational purposes."
)

tokenizer = None
model = None


def load_model():
    global tokenizer, model
    if model is not None:
        return

    token = os.environ.get("HF_TOKEN")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        token=token,
        trust_remote_code=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()


@spaces.GPU(duration=120)
def generate(
    message: str,
    history: list[dict],
    system_prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    repetition_penalty: float,
):
    load_model()

    messages = [{"role": "system", "content": system_prompt}]
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": message})

    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    gen_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature if temperature > 0 else 1e-7,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        do_sample=temperature > 0,
        streamer=streamer,
    )

    thread = Thread(target=model.generate, kwargs=gen_kwargs)
    thread.start()

    output = ""
    for token_text in streamer:
        output += token_text
        yield output

    thread.join()


EXAMPLES = [
    ["Write a Python port scanner that detects the top 100 common ports."],
    ["Explain how SQL injection works and show a safe demo with SQLite."],
    ["Create a reverse shell payload in Python for a penetration test."],
    ["Write a script to enumerate subdomains using DNS brute-forcing."],
    ["Explain buffer overflow exploitation with a simple C example."],
]

css = """
.gradio-container { max-width: 900px !important; }
footer { display: none !important; }
"""

with gr.Blocks(css=css, title="Red Team Coder 4B", theme=gr.themes.Base(
    primary_hue="red", neutral_hue="gray",
    font=gr.themes.GoogleFont("JetBrains Mono"),
)) as demo:
    gr.Markdown(
        "# \U0001f534 Red Team Coder 4B\n"
        "**Offensive security & code generation model** "
        "| [Model Card](https://huggingface.co/frEEtom3/redteam-coder-4b)\n\n"
        "Fine-tuned Qwen3-4B for cybersecurity research. "
        "Running on ZeroGPU."
    )

    chatbot = gr.Chatbot(
        type="messages",
        height=500,
        placeholder="Ask about security tools, exploits, or code...",
        show_copy_button=True,
    )

    with gr.Accordion("Settings", open=False):
        system_prompt = gr.Textbox(
            value=DEFAULT_SYSTEM_PROMPT,
            label="System Prompt",
            lines=3,
        )
        with gr.Row():
            max_new_tokens = gr.Slider(
                64, 4096, value=1024, step=64, label="Max New Tokens"
            )
            temperature = gr.Slider(
                0.0, 2.0, value=0.7, step=0.05, label="Temperature"
            )
        with gr.Row():
            top_p = gr.Slider(
                0.0, 1.0, value=0.9, step=0.05, label="Top-p"
            )
            repetition_penalty = gr.Slider(
                1.0, 2.0, value=1.1, step=0.05, label="Repetition Penalty"
            )

    gr.ChatInterface(
        fn=generate,
        type="messages",
        chatbot=chatbot,
        additional_inputs=[
            system_prompt,
            max_new_tokens,
            temperature,
            top_p,
            repetition_penalty,
        ],
        examples=EXAMPLES,
        cache_examples=False,
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
