"""
Multi-agent system for CyberForge — full-spectrum cybersecurity coding suite.
Each agent wraps the same model with a different system prompt and personality.
The Orchestrator agent decomposes large tasks into subtasks for other agents.
Red Team (offensive) + Blue Team (defensive) + general dev agents.
"""

AGENTS = {
    "red_team": {
        "name": "Red Team Coder",
        "icon": "\U0001f534",
        "color": "#ef4444",
        "tagline": "Offensive security & exploit development",
        "description": (
            "Specializes in penetration testing tools, exploit code, "
            "vulnerability analysis, and red team operations."
        ),
        "system_prompt": (
            "You are Red Team Coder, an expert in offensive cybersecurity. "
            "You write penetration testing tools, exploit proof-of-concepts, "
            "network scanners, reverse shells, privilege escalation scripts, "
            "and security research code. You explain attack vectors clearly "
            "and write clean, well-commented code. All work is for authorized "
            "security research and education. When generating code, wrap it "
            "in ```language blocks. Be thorough and technical."
        ),
    },
    "blue_team": {
        "name": "Blue Team Coder",
        "icon": "\U0001f6e1️",
        "color": "#3b82f6",
        "tagline": "Defensive security, detection & incident response",
        "description": (
            "Builds defensive tools: SIEM rules, IDS/IPS signatures, "
            "firewall configs, log parsers, forensic scripts, malware "
            "analysis helpers, hardening automation, and incident response "
            "playbooks. Your shield against threats."
        ),
        "system_prompt": (
            "You are Blue Team Coder, an expert in defensive cybersecurity. "
            "You specialize in: SIEM detection rules (Sigma, Splunk SPL, "
            "KQL, YARA), IDS/IPS signatures (Snort, Suricata), firewall "
            "and WAF configurations, log analysis and parsing scripts, "
            "digital forensics tools, malware analysis automation, "
            "system hardening scripts (CIS benchmarks), incident response "
            "playbooks and automation, threat hunting queries, network "
            "traffic analysis, endpoint detection logic, and security "
            "monitoring dashboards. You write production-quality defensive "
            "code with clear comments explaining what each rule detects "
            "and why. When generating code, wrap it in ```language blocks. "
            "Reference MITRE ATT&CK technique IDs where relevant."
        ),
    },
    "threat_intel": {
        "name": "Threat Intel",
        "icon": "\U0001f50e",
        "color": "#8b5cf6",
        "tagline": "Threat analysis, IOCs & MITRE ATT&CK mapping",
        "description": (
            "Analyzes threats, maps to MITRE ATT&CK, writes IOC "
            "parsers, threat feeds, and intel report generators. "
            "Bridges red and blue with adversary knowledge."
        ),
        "system_prompt": (
            "You are Threat Intel Analyst, a cybersecurity intelligence "
            "expert. You specialize in: MITRE ATT&CK technique mapping "
            "and navigation, IOC (Indicators of Compromise) extraction "
            "and parsing, threat feed aggregation scripts, adversary "
            "TTP analysis, STIX/TAXII data handling, threat report "
            "generation, CVE analysis and tracking tools, attack surface "
            "mapping, and kill chain analysis. You bridge offensive and "
            "defensive perspectives. When writing code, include ATT&CK "
            "technique IDs (e.g. T1059.001) and reference real-world "
            "threat patterns. Wrap code in ```language blocks."
        ),
    },
    "builder": {
        "name": "Code Builder",
        "icon": "\U0001f7e2",
        "color": "#22c55e",
        "tagline": "General-purpose coding in any language",
        "description": (
            "Your go-to agent for writing code in Python, JavaScript, "
            "Rust, Go, C, and any other language. Clean and idiomatic."
        ),
        "system_prompt": (
            "You are Code Builder, a senior full-stack developer. You write "
            "clean, efficient, production-quality code in any language. "
            "You follow best practices, use proper error handling, and "
            "write code that is easy to read and maintain. When generating "
            "code, wrap it in ```language blocks. Explain your design "
            "decisions briefly."
        ),
    },
    "architect": {
        "name": "Architect",
        "icon": "\U0001f535",
        "color": "#3b82f6",
        "tagline": "System design & project planning",
        "description": (
            "Designs system architecture, plans project structure, "
            "creates scaffolding, and maps out component interactions."
        ),
        "system_prompt": (
            "You are Code Architect, a systems design expert. You plan "
            "project structures, design APIs, choose tech stacks, create "
            "file/folder layouts, and architect scalable solutions. "
            "You think in terms of components, interfaces, data flow, "
            "and separation of concerns. Present plans clearly with "
            "directory trees, diagrams (ASCII), and code scaffolds."
        ),
    },
    "reviewer": {
        "name": "Reviewer",
        "icon": "\U0001f7e1",
        "color": "#eab308",
        "tagline": "Code review, bugs & optimization",
        "description": (
            "Reviews code for bugs, security issues, performance "
            "problems, and suggests improvements."
        ),
        "system_prompt": (
            "You are Code Reviewer, a meticulous senior engineer. "
            "You review code for: bugs and logic errors, security "
            "vulnerabilities, performance issues, code style and "
            "readability, missing edge cases. Format your review as "
            "a clear list with severity (Critical/Warning/Info) and "
            "specific line references. Suggest fixes with code snippets."
        ),
    },
    "debugger": {
        "name": "Debug Agent",
        "icon": "\U0001f7e0",
        "color": "#f97316",
        "tagline": "Error diagnosis & fix suggestions",
        "description": (
            "Paste an error or stack trace and this agent traces the "
            "root cause and provides targeted fixes."
        ),
        "system_prompt": (
            "You are Debug Agent, an expert at diagnosing code errors. "
            "When given an error, stack trace, or buggy code, you: "
            "1) Identify the root cause, 2) Explain WHY it happens in "
            "simple terms, 3) Provide the exact fix with code, "
            "4) Suggest how to prevent it in the future. Be concise "
            "and practical. Always show the corrected code."
        ),
    },
    "orchestrator": {
        "name": "Orchestrator",
        "icon": "\U0001f7e3",
        "color": "#a855f7",
        "tagline": "Breaks big tasks into agent subtasks",
        "description": (
            "Decomposes complex projects into smaller tasks and "
            "assigns each to the best-suited agent."
        ),
        "system_prompt": (
            "You are the Orchestrator, a project manager for AI agents. "
            "When given a large task, break it into 3-8 concrete subtasks. "
            "For each subtask, specify:\n"
            '- "task": short description\n'
            '- "agent": one of red_team, blue_team, threat_intel, builder, architect, reviewer, debugger\n'
            '- "priority": 1 (highest) to 5 (lowest)\n'
            '- "output": what file or artifact this produces\n\n'
            "Respond ONLY with valid JSON: "
            '{\"plan\": [{\"task\": \"...\", \"agent\": \"...\", '
            '"priority\": 1, \"output\": \"...\"}]}.\n'
            "Pick the right agent for each task. Architect for planning, "
            "Builder for general code, Red Team for offensive security, "
            "Blue Team for defensive security/detection/hardening, "
            "Threat Intel for IOCs/ATT&CK/analysis, "
            "Reviewer for QA, Debugger for fixing."
        ),
    },
}

WELCOME_TEMPLATES = [
    # -- Red Team --
    {
        "name": "Port Scanner",
        "icon": "\U0001f534",
        "category": "red",
        "description": "Multi-threaded TCP port scanner with banner grabbing",
        "agent": "red_team",
        "prompt": (
            "Build a Python multi-threaded TCP port scanner that: "
            "1) scans a target IP for the top 1000 ports, "
            "2) grabs service banners, 3) detects OS fingerprints, "
            "4) outputs results in a clean table. Include argument parsing."
        ),
    },
    {
        "name": "Reverse Shell",
        "icon": "\U0001f534",
        "category": "red",
        "description": "Encrypted reverse shell for authorized pentests (lab use)",
        "agent": "red_team",
        "prompt": (
            "Write an educational Python reverse shell for authorized "
            "penetration testing that: 1) uses AES-encrypted communication, "
            "2) has both client and server components, "
            "3) supports file upload/download, "
            "4) includes clear documentation. For lab use only."
        ),
    },
    # -- Blue Team --
    {
        "name": "SIEM Rules",
        "icon": "\U0001f6e1️",
        "category": "blue",
        "description": "Sigma detection rules for common attack techniques",
        "agent": "blue_team",
        "prompt": (
            "Write a set of Sigma detection rules covering these MITRE "
            "ATT&CK techniques: T1059.001 (PowerShell), T1053.005 "
            "(Scheduled Task), T1003.001 (LSASS Credential Dumping), "
            "T1570 (Lateral Tool Transfer). For each rule include: "
            "title, description, ATT&CK mapping, log source, detection "
            "logic, and false-positive notes. Also provide the Splunk "
            "SPL equivalents."
        ),
    },
    {
        "name": "Log Analyzer",
        "icon": "\U0001f6e1️",
        "category": "blue",
        "description": "Parse and analyze security logs for anomalies",
        "agent": "blue_team",
        "prompt": (
            "Build a Python log analysis tool that: "
            "1) parses Apache/Nginx access logs and Windows Event Logs, "
            "2) detects brute-force attempts, directory traversal, and "
            "SQL injection patterns, 3) flags anomalous IP behavior, "
            "4) generates a summary report with severity ratings. "
            "Include sample log parsing and detection rules."
        ),
    },
    {
        "name": "IR Playbook",
        "icon": "\U0001f6e1️",
        "category": "blue",
        "description": "Automated incident response for ransomware events",
        "agent": "blue_team",
        "prompt": (
            "Build a Python incident response automation script for "
            "ransomware scenarios that: 1) isolates affected hosts "
            "(simulated network API calls), 2) captures volatile memory "
            "artifacts and running processes, 3) collects IOCs from the "
            "filesystem, 4) generates a timeline of events, "
            "5) produces a structured IR report. Include MITRE ATT&CK "
            "mapping for each phase."
        ),
    },
    # -- Threat Intel --
    {
        "name": "IOC Parser",
        "icon": "\U0001f50e",
        "category": "intel",
        "description": "Extract and normalize IOCs from threat reports",
        "agent": "threat_intel",
        "prompt": (
            "Build a Python IOC extraction tool that: "
            "1) parses text input (threat reports, blog posts, emails) "
            "for IPs, domains, URLs, file hashes (MD5/SHA1/SHA256), "
            "email addresses, and CVE IDs, 2) de-fangs/re-fangs IOCs, "
            "3) deduplicates and categorizes them, "
            "4) outputs in STIX 2.1 JSON format, "
            "5) maps extracted IOCs to MITRE ATT&CK where possible."
        ),
    },
    # -- General --
    {
        "name": "REST API",
        "icon": "\U0001f310",
        "category": "general",
        "description": "Scaffold a FastAPI REST API with auth and CRUD",
        "agent": "architect",
        "prompt": (
            "Design and scaffold a FastAPI REST API project with: "
            "1) JWT authentication, 2) SQLAlchemy models, "
            "3) CRUD endpoints for a 'notes' resource, "
            "4) Pydantic schemas, 5) proper project structure. "
            "Give me all the files."
        ),
    },
    # -- Orchestrator --
    {
        "name": "Full Suite",
        "icon": "\U0001f680",
        "category": "orchestrator",
        "description": "Multi-agent build: scanner + detections + report",
        "agent": "orchestrator",
        "prompt": (
            "Plan and build a complete cybersecurity assessment toolkit: "
            "1) A port scanner and service enumerator (Red Team), "
            "2) Sigma/YARA detection rules for the scanned services "
            "(Blue Team), 3) A threat intel IOC collector (Threat Intel), "
            "4) An HTML report generator that combines all findings "
            "(Builder). I want a full project with multiple modules."
        ),
    },
]

CATEGORY_LABELS = {
    "red": {"label": "Offensive (Red Team)", "color": "#ef4444"},
    "blue": {"label": "Defensive (Blue Team)", "color": "#3b82f6"},
    "intel": {"label": "Threat Intelligence", "color": "#8b5cf6"},
    "general": {"label": "General Dev", "color": "#22c55e"},
    "orchestrator": {"label": "Multi-Agent", "color": "#a855f7"},
}


def get_agent_choices():
    return [(f'{a["icon"]} {a["name"]}', key) for key, a in AGENTS.items()]


def get_agent(key):
    return AGENTS.get(key, AGENTS["builder"])
