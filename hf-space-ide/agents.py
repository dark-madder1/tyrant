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

CATEGORY_LABELS = {
    "red": {"label": "Offensive", "icon": "\U0001f534", "color": "#ef4444"},
    "blue": {"label": "Defensive", "icon": "\U0001f6e1️", "color": "#3b82f6"},
    "intel": {"label": "Threat Intel", "icon": "\U0001f50e", "color": "#8b5cf6"},
    "general": {"label": "General Dev", "icon": "\U0001f7e2", "color": "#22c55e"},
    "orchestrator": {"label": "Multi-Agent", "icon": "\U0001f680", "color": "#a855f7"},
}

# ---------------------------------------------------------------------------
# Prompt library — 50+ prompts, rotated daily on the welcome board.
# Organized by category so the board always shows a balanced mix.
# ---------------------------------------------------------------------------
PROMPT_LIBRARY = [
    # ===== RED TEAM (offensive) ===========================================
    {"id": "r01", "cat": "red", "agent": "red_team", "name": "Port Scanner",
     "desc": "Multi-threaded TCP port scanner with banner grabbing",
     "prompt": "Build a Python multi-threaded TCP port scanner that: 1) scans a target IP for the top 1000 ports, 2) grabs service banners, 3) detects OS fingerprints, 4) outputs results in a clean table. Include argument parsing."},
    {"id": "r02", "cat": "red", "agent": "red_team", "name": "Reverse Shell",
     "desc": "Encrypted reverse shell for authorized pentests (lab use)",
     "prompt": "Write an educational Python reverse shell for authorized penetration testing that: 1) uses AES-encrypted communication, 2) has both client and server components, 3) supports file upload/download, 4) includes clear documentation. For lab use only."},
    {"id": "r03", "cat": "red", "agent": "red_team", "name": "SQL Injection Lab",
     "desc": "Vulnerable Flask app + exploit script for SQLi training",
     "prompt": "Build a SQLi training lab: 1) A deliberately vulnerable Flask app with a login form and SQLite backend, 2) A Python exploit script that demonstrates UNION-based, blind boolean, and time-based SQLi, 3) Comments explaining each technique. Educational use only."},
    {"id": "r04", "cat": "red", "agent": "red_team", "name": "WiFi Deauth",
     "desc": "802.11 deauthentication tool using Scapy (lab only)",
     "prompt": "Write a Python 802.11 deauthentication tool using Scapy for authorized wireless pentesting: 1) sniffs for access points, 2) targets a specific BSSID, 3) sends deauth frames, 4) includes monitor mode setup instructions. For controlled lab environments only."},
    {"id": "r05", "cat": "red", "agent": "red_team", "name": "Subdomain Enum",
     "desc": "DNS brute-force subdomain enumerator with async resolution",
     "prompt": "Build a Python async subdomain enumerator that: 1) brute-forces subdomains from a wordlist using asyncio DNS resolution, 2) checks for wildcard DNS, 3) probes discovered subdomains for HTTP services, 4) outputs results as JSON and a summary table."},
    {"id": "r06", "cat": "red", "agent": "red_team", "name": "Keylogger PoC",
     "desc": "Educational keylogger with pynput for lab demonstrations",
     "prompt": "Write an educational Python keylogger using pynput for authorized security demonstrations: 1) captures keystrokes, 2) logs to an encrypted local file, 3) includes a viewer utility, 4) self-terminates after a configurable timeout. Add clear warnings about legal use."},
    {"id": "r07", "cat": "red", "agent": "red_team", "name": "Password Cracker",
     "desc": "Multi-algorithm hash cracker with dictionary + rules",
     "prompt": "Build a Python password hash cracker supporting MD5, SHA-1, SHA-256, bcrypt, and NTLM that: 1) loads a dictionary file, 2) applies mutation rules (l33t, append numbers, case toggle), 3) uses multiprocessing for speed, 4) reports crack rate and results."},
    {"id": "r08", "cat": "red", "agent": "red_team", "name": "C2 Framework",
     "desc": "Lightweight HTTP-based C2 server + agent for labs",
     "prompt": "Build a minimal HTTP-based C2 framework for authorized lab use: 1) Server in Python Flask that queues commands, 2) Agent that polls for tasks and returns output, 3) AES-encrypted comms, 4) Supports file exfil and shell commands. Include registration and heartbeat."},
    {"id": "r09", "cat": "red", "agent": "red_team", "name": "XSS Scanner",
     "desc": "Automated reflected XSS detection with payload fuzzing",
     "prompt": "Build a Python reflected XSS scanner that: 1) crawls a target URL for forms and URL params, 2) injects a library of XSS payloads, 3) checks responses for unescaped reflection, 4) reports vulnerable parameters with proof-of-concept URLs. Use requests + BeautifulSoup."},
    {"id": "r10", "cat": "red", "agent": "red_team", "name": "Privilege Escalation",
     "desc": "Linux privesc enumeration script (SUID, cron, etc.)",
     "prompt": "Write a Python Linux privilege escalation enumeration tool that checks: 1) SUID/SGID binaries, 2) writable cron jobs, 3) sudo misconfigurations, 4) kernel version vs known exploits, 5) writable PATH directories, 6) Docker group membership. Output a prioritized findings report."},
    {"id": "r11", "cat": "red", "agent": "red_team", "name": "ARP Spoofer",
     "desc": "ARP spoofing MitM tool with packet forwarding",
     "prompt": "Build a Python ARP spoofing tool using Scapy for authorized lab pentesting: 1) discovers gateway and target MAC addresses, 2) performs bidirectional ARP poisoning, 3) enables IP forwarding, 4) restores ARP tables on exit. Include a packet sniffer mode."},
    {"id": "r12", "cat": "red", "agent": "red_team", "name": "Phishing Kit",
     "desc": "Credential harvester with cloned login page (lab only)",
     "prompt": "Build an educational phishing simulation toolkit for authorized security awareness training: 1) clones a target login page, 2) captures submitted credentials to a log, 3) redirects to the real site after capture, 4) generates a campaign report. Flask-based. Lab use only."},

    # ===== BLUE TEAM (defensive) ==========================================
    {"id": "b01", "cat": "blue", "agent": "blue_team", "name": "SIEM Rules",
     "desc": "Sigma detection rules for MITRE ATT&CK techniques",
     "prompt": "Write Sigma detection rules covering T1059.001 (PowerShell), T1053.005 (Scheduled Task), T1003.001 (LSASS Credential Dumping), T1570 (Lateral Tool Transfer). For each: title, description, ATT&CK mapping, log source, detection logic, false-positive notes. Also provide Splunk SPL equivalents."},
    {"id": "b02", "cat": "blue", "agent": "blue_team", "name": "Log Analyzer",
     "desc": "Parse and analyze security logs for anomalies",
     "prompt": "Build a Python log analysis tool that: 1) parses Apache/Nginx access logs and Windows Event Logs, 2) detects brute-force attempts, directory traversal, and SQL injection patterns, 3) flags anomalous IP behavior, 4) generates a summary report with severity ratings."},
    {"id": "b03", "cat": "blue", "agent": "blue_team", "name": "IR Playbook",
     "desc": "Automated incident response for ransomware events",
     "prompt": "Build a Python incident response automation script for ransomware: 1) isolates affected hosts (simulated API calls), 2) captures volatile memory artifacts and processes, 3) collects IOCs from the filesystem, 4) generates an event timeline, 5) produces a structured IR report with MITRE ATT&CK mapping."},
    {"id": "b04", "cat": "blue", "agent": "blue_team", "name": "YARA Rules",
     "desc": "YARA rules for detecting common malware families",
     "prompt": "Write YARA rules to detect: 1) Cobalt Strike beacons (named pipes, default configs), 2) Mimikatz in memory, 3) Common webshells (PHP/ASPX), 4) Ransomware encryption routines. Include meta tags, thorough string matching, conditions with comments explaining detection logic."},
    {"id": "b05", "cat": "blue", "agent": "blue_team", "name": "Firewall Hardener",
     "desc": "iptables/nftables hardening script with CIS benchmarks",
     "prompt": "Write a Linux firewall hardening script (iptables and nftables versions) that: 1) implements CIS benchmark Level 1 rules, 2) allows only specified services, 3) rate-limits SSH, 4) logs dropped packets, 5) blocks known bad IPs from a threat feed, 6) includes rollback instructions."},
    {"id": "b06", "cat": "blue", "agent": "blue_team", "name": "Suricata Rules",
     "desc": "IDS/IPS rules for lateral movement detection",
     "prompt": "Write Suricata IDS rules to detect: 1) SMB lateral movement (PsExec, WMI), 2) Pass-the-Hash attacks, 3) Kerberoasting traffic, 4) DCSync replication requests, 5) Suspicious DNS tunneling. Include rule metadata, references, and classification. Map each to MITRE ATT&CK."},
    {"id": "b07", "cat": "blue", "agent": "blue_team", "name": "Email Analyzer",
     "desc": "Phishing email header analyzer and verdict engine",
     "prompt": "Build a Python phishing email analyzer that: 1) parses email headers (SPF, DKIM, DMARC results), 2) extracts and detonates URLs in a sandbox check, 3) analyzes attachment hashes against VirusTotal API, 4) scores the email risk level, 5) generates a verdict report."},
    {"id": "b08", "cat": "blue", "agent": "blue_team", "name": "Honeypot",
     "desc": "Low-interaction SSH/HTTP honeypot with logging",
     "prompt": "Build a Python low-interaction honeypot that: 1) emulates SSH (paramiko) and HTTP services, 2) logs all connection attempts with timestamps and payloads, 3) captures credentials submitted, 4) GeoIP-resolves attacker IPs, 5) sends alerts on high-value events. Include Docker deployment."},
    {"id": "b09", "cat": "blue", "agent": "blue_team", "name": "Windows Hardening",
     "desc": "PowerShell CIS benchmark hardening automation",
     "prompt": "Write a PowerShell script that hardens Windows 10/11 per CIS benchmarks: 1) disables unnecessary services, 2) configures audit policies, 3) sets password policies, 4) enables Windows Defender features, 5) restricts PowerShell execution, 6) hardens SMB. Include undo/rollback functions."},
    {"id": "b10", "cat": "blue", "agent": "blue_team", "name": "Forensic Imager",
     "desc": "Disk and memory forensic acquisition toolkit",
     "prompt": "Build a Python forensic acquisition toolkit that: 1) creates a forensic disk image with hash verification (MD5 + SHA-256), 2) dumps process memory from a running system, 3) extracts browser artifacts (history, cookies, downloads), 4) preserves chain of custody metadata."},
    {"id": "b11", "cat": "blue", "agent": "blue_team", "name": "SOC Dashboard",
     "desc": "Real-time security event dashboard with Flask",
     "prompt": "Build a Flask-based SOC dashboard that: 1) ingests syslog events via a UDP listener, 2) categorizes alerts by severity, 3) shows a real-time event feed with filtering, 4) displays top attackers and targeted ports, 5) has an alert acknowledge/escalate workflow."},
    {"id": "b12", "cat": "blue", "agent": "blue_team", "name": "Malware Sandbox",
     "desc": "Automated malware analysis sandbox with API",
     "prompt": "Build a Python malware analysis sandbox framework that: 1) executes samples in an isolated environment, 2) monitors file system changes, 3) captures network traffic, 4) hooks API calls (simulated), 5) generates a behavioral analysis report with IOCs and MITRE ATT&CK mapping."},

    # ===== THREAT INTEL ===================================================
    {"id": "t01", "cat": "intel", "agent": "threat_intel", "name": "IOC Parser",
     "desc": "Extract and normalize IOCs from threat reports",
     "prompt": "Build a Python IOC extraction tool that: 1) parses text for IPs, domains, URLs, hashes (MD5/SHA1/SHA256), emails, and CVE IDs, 2) de-fangs/re-fangs IOCs, 3) deduplicates and categorizes them, 4) outputs STIX 2.1 JSON, 5) maps to MITRE ATT&CK where possible."},
    {"id": "t02", "cat": "intel", "agent": "threat_intel", "name": "ATT&CK Navigator",
     "desc": "Generate MITRE ATT&CK Navigator heatmap layers",
     "prompt": "Build a Python tool that: 1) takes a list of MITRE ATT&CK technique IDs, 2) generates an ATT&CK Navigator layer JSON, 3) color-codes by frequency/severity, 4) adds comments per technique, 5) supports merging multiple layers for comparison. Output valid Navigator JSON."},
    {"id": "t03", "cat": "intel", "agent": "threat_intel", "name": "CVE Tracker",
     "desc": "Monitor new CVEs and match against your tech stack",
     "prompt": "Build a Python CVE monitoring tool that: 1) queries the NVD API for recent CVEs, 2) matches against a configured tech stack (list of products/versions), 3) scores relevance based on CVSS and exploitability, 4) sends alerts for critical matches, 5) generates a weekly report."},
    {"id": "t04", "cat": "intel", "agent": "threat_intel", "name": "Threat Feed Aggregator",
     "desc": "Aggregate and deduplicate multiple OSINT threat feeds",
     "prompt": "Build a Python threat feed aggregator that: 1) pulls from multiple OSINT feeds (abuse.ch, AlienVault OTX, EmergingThreats), 2) normalizes all IOCs to a common format, 3) deduplicates across feeds, 4) enriches with GeoIP and WHOIS, 5) exports to CSV and STIX bundle."},
    {"id": "t05", "cat": "intel", "agent": "threat_intel", "name": "APT Profiler",
     "desc": "Build adversary profiles from observed TTPs",
     "prompt": "Build a Python tool that creates adversary profiles: 1) takes a list of observed MITRE ATT&CK techniques, 2) correlates against known APT groups (from ATT&CK data), 3) ranks likely attribution by TTP overlap percentage, 4) generates a profile report with diamond model analysis."},
    {"id": "t06", "cat": "intel", "agent": "threat_intel", "name": "Domain Intel",
     "desc": "Domain reputation checker with WHOIS + DNS analysis",
     "prompt": "Build a Python domain intelligence tool that: 1) performs WHOIS lookups with registration age analysis, 2) checks DNS records (A, MX, TXT, NS), 3) queries reputation APIs, 4) detects domain squatting patterns (typosquat, homoglyph), 5) scores domain risk with reasoning."},
    {"id": "t07", "cat": "intel", "agent": "threat_intel", "name": "Darkweb Monitor",
     "desc": "Paste site and leak monitor for credential exposure",
     "prompt": "Build a Python credential exposure monitor that: 1) checks if email domains appear in known breach datasets, 2) monitors paste sites for company keywords, 3) parses structured and unstructured leak formats, 4) deduplicates findings, 5) generates an exposure report with remediation steps."},
    {"id": "t08", "cat": "intel", "agent": "threat_intel", "name": "STIX Bundle Builder",
     "desc": "Create STIX 2.1 threat intelligence bundles",
     "prompt": "Build a Python STIX 2.1 bundle builder that: 1) creates Indicator, Malware, ThreatActor, and AttackPattern objects, 2) links them with relationships, 3) validates against the STIX schema, 4) supports importing from CSV, 5) exports valid STIX JSON bundles for sharing via TAXII."},

    # ===== GENERAL DEV ====================================================
    {"id": "g01", "cat": "general", "agent": "architect", "name": "REST API",
     "desc": "FastAPI project with JWT auth and CRUD",
     "prompt": "Design and scaffold a FastAPI REST API project with: 1) JWT authentication, 2) SQLAlchemy models, 3) CRUD endpoints for a 'notes' resource, 4) Pydantic schemas, 5) proper project structure. Give me all the files."},
    {"id": "g02", "cat": "general", "agent": "builder", "name": "CLI Tool",
     "desc": "Modern CLI with Click, Rich tables and progress bars",
     "prompt": "Build a Python CLI tool using Click and Rich that: 1) has subcommands (init, run, status), 2) pretty-prints tables and progress bars, 3) reads a YAML config file, 4) has --verbose and --json output modes."},
    {"id": "g03", "cat": "general", "agent": "builder", "name": "Web Scraper",
     "desc": "Async web scraper with rate limiting and JSON export",
     "prompt": "Write a Python async web scraper using aiohttp that: 1) takes a list of URLs, 2) respects rate limits, 3) extracts all links and text content, 4) saves results to JSON. Include error handling and retry logic."},
    {"id": "g04", "cat": "general", "agent": "builder", "name": "Discord Bot",
     "desc": "Discord bot with slash commands and embeds",
     "prompt": "Build a Python Discord bot using discord.py that: 1) responds to slash commands, 2) sends rich embeds, 3) has a /scan command that simulates running a security check, 4) stores results in SQLite, 5) has a /report command to show recent scans."},
    {"id": "g05", "cat": "general", "agent": "builder", "name": "Docker Compose",
     "desc": "Full-stack Docker Compose with monitoring",
     "prompt": "Create a Docker Compose setup with: 1) Python Flask API, 2) PostgreSQL database, 3) Redis cache, 4) Nginx reverse proxy, 5) Prometheus + Grafana monitoring. Include health checks, volume mounts, and environment variable management."},
    {"id": "g06", "cat": "general", "agent": "builder", "name": "WebSocket Chat",
     "desc": "Real-time encrypted chat with WebSockets",
     "prompt": "Build a real-time chat application using Python (FastAPI + WebSockets) with: 1) end-to-end encryption (Diffie-Hellman key exchange), 2) multiple chat rooms, 3) message history in SQLite, 4) a simple HTML/JS frontend. Include connection handling."},
    {"id": "g07", "cat": "general", "agent": "architect", "name": "Microservices",
     "desc": "Microservice architecture with event-driven messaging",
     "prompt": "Design a microservices architecture for a security scanning platform: 1) API Gateway service, 2) Scanner service, 3) Results service, 4) Notification service. Use RabbitMQ for messaging. Provide project structure, Docker configs, and all service code."},
    {"id": "g08", "cat": "general", "agent": "builder", "name": "GitHub Action",
     "desc": "CI/CD pipeline with security scanning stages",
     "prompt": "Create a GitHub Actions CI/CD pipeline that: 1) runs linting and tests, 2) performs SAST with Bandit, 3) checks dependencies with Safety, 4) builds a Docker image, 5) scans the image with Trivy, 6) deploys to staging on success. Include all workflow YAML."},

    {"id": "g09", "cat": "general", "agent": "builder", "name": "Rate Limiter",
     "desc": "Token bucket rate limiter middleware for APIs",
     "prompt": "Build a Python token-bucket rate limiter that: 1) works as FastAPI middleware, 2) supports per-IP and per-API-key limits, 3) stores state in Redis, 4) returns proper 429 responses with Retry-After headers, 5) has a configurable burst allowance."},
    {"id": "g10", "cat": "general", "agent": "builder", "name": "Task Queue",
     "desc": "Distributed task queue with Celery and Redis",
     "prompt": "Build a Python distributed task queue using Celery + Redis that: 1) defines scan tasks (port scan, header check, SSL check), 2) chains tasks into workflows, 3) tracks progress with status callbacks, 4) retries on failure, 5) has a Flask dashboard showing task states."},

    # -- Extra red team --
    {"id": "r13", "cat": "red", "agent": "red_team", "name": "DNS Tunnel",
     "desc": "DNS tunneling data exfiltration tool (lab only)",
     "prompt": "Build an educational DNS tunneling tool for authorized lab use: 1) client encodes data into DNS TXT query subdomains, 2) server decodes and reassembles the data, 3) supports chunking for large files, 4) includes a detection signature for the blue team. Python + dnspython."},

    # -- Extra blue team --
    {"id": "b13", "cat": "blue", "agent": "blue_team", "name": "Network Baseline",
     "desc": "Learn normal traffic patterns and alert on deviations",
     "prompt": "Build a Python network traffic baseline tool that: 1) captures packets with Scapy for a learning period, 2) builds a statistical model of normal traffic (protocols, ports, volumes), 3) switches to detection mode and alerts on deviations, 4) generates an anomaly report with timestamps."},
    {"id": "b14", "cat": "blue", "agent": "blue_team", "name": "AD Audit",
     "desc": "Active Directory security audit script",
     "prompt": "Write a Python script that audits Active Directory security: 1) finds users with non-expiring passwords, 2) detects stale accounts (no login >90 days), 3) lists users in privileged groups, 4) checks for unconstrained delegation, 5) finds SPNs set on user accounts (Kerberoastable). Uses ldap3 library."},

    # -- Extra threat intel --
    {"id": "t09", "cat": "intel", "agent": "threat_intel", "name": "Ransomware Tracker",
     "desc": "Track ransomware groups and their TTPs",
     "prompt": "Build a Python ransomware group tracker that: 1) maintains a database of known ransomware families and their IOCs, 2) maps each group's TTPs to MITRE ATT&CK, 3) tracks ransom note patterns and file extensions, 4) generates comparison reports between groups, 5) exports to STIX format."},
    {"id": "t10", "cat": "intel", "agent": "threat_intel", "name": "Phishing Classifier",
     "desc": "ML-based URL and email phishing classifier",
     "prompt": "Build a Python phishing classifier that: 1) extracts features from URLs (entropy, length, suspicious keywords, TLD), 2) extracts email header features (SPF/DKIM/DMARC, age, sender reputation), 3) trains a Random Forest model on labeled data, 4) provides a real-time scoring API with confidence levels."},

    # ===== ORCHESTRATOR (multi-agent) =====================================
    {"id": "o01", "cat": "orchestrator", "agent": "orchestrator", "name": "Full Audit",
     "desc": "Multi-agent: scanner + detections + intel + report",
     "prompt": "Plan and build a complete cybersecurity assessment toolkit: 1) A port scanner and service enumerator (Red Team), 2) Sigma/YARA detection rules for the scanned services (Blue Team), 3) A threat intel IOC collector (Threat Intel), 4) An HTML report generator (Builder)."},
    {"id": "o02", "cat": "orchestrator", "agent": "orchestrator", "name": "Purple Team Lab",
     "desc": "Attack simulation + matching detection rules",
     "prompt": "Build a purple team exercise toolkit: 1) Red Team scripts that simulate ATT&CK techniques (T1059, T1053, T1003, T1021), 2) Blue Team Sigma rules that detect each simulated attack, 3) A test harness that runs attacks and verifies detections fire, 4) A scorecard report."},
    {"id": "o03", "cat": "orchestrator", "agent": "orchestrator", "name": "Vuln Scanner",
     "desc": "End-to-end vulnerability scanner with remediation",
     "prompt": "Build a complete vulnerability scanner: 1) Network discovery and port scanning module (Red Team), 2) Service version fingerprinting and CVE matching (Threat Intel), 3) Remediation playbook generator (Blue Team), 4) HTML dashboard with charts (Builder), 5) CLI interface (Architect)."},
    {"id": "o04", "cat": "orchestrator", "agent": "orchestrator", "name": "SOAR Platform",
     "desc": "Security orchestration with automated response",
     "prompt": "Build a mini SOAR platform: 1) Alert ingestion API (Architect), 2) Playbook engine with conditional logic (Builder), 3) Automated containment actions for common alerts (Blue Team), 4) Threat enrichment pipeline (Threat Intel), 5) Dashboard and case management (Builder)."},
]


def get_todays_prompts(count=8):
    """Pick `count` prompts for today using the date as a seed.

    Guarantees a balanced mix across categories every day and ensures the
    selection changes daily, cycling through the whole library before repeating.
    """
    import hashlib
    from datetime import date

    today = date.today()
    day_seed = int(hashlib.sha256(today.isoformat().encode()).hexdigest(), 16)

    cats = {}
    for p in PROMPT_LIBRARY:
        cats.setdefault(p["cat"], []).append(p)

    per_cat = max(1, count // len(cats))
    remainder = count - per_cat * len(cats)

    selected = []
    rng_state = day_seed
    for cat_name in ["red", "blue", "intel", "general", "orchestrator"]:
        pool = list(cats.get(cat_name, []))
        n = per_cat + (1 if remainder > 0 else 0)
        if remainder > 0:
            remainder -= 1
        rng_state = _shuffle(pool, rng_state)
        selected.extend(pool[:n])

    rng_state = _shuffle(selected, rng_state + 1)
    return selected[:count]


def get_shuffled_prompts(seed_extra=0, count=8):
    """Get a random selection — used by the Shuffle button."""
    import hashlib, time
    seed = int(hashlib.sha256(f"{time.time()}{seed_extra}".encode()).hexdigest(), 16)
    cats = {}
    for p in PROMPT_LIBRARY:
        cats.setdefault(p["cat"], []).append(p)

    per_cat = max(1, count // len(cats))
    remainder = count - per_cat * len(cats)

    selected = []
    rng_state = seed
    for cat_name in ["red", "blue", "intel", "general", "orchestrator"]:
        pool = list(cats.get(cat_name, []))
        n = per_cat + (1 if remainder > 0 else 0)
        if remainder > 0:
            remainder -= 1
        rng_state = _shuffle(pool, rng_state)
        selected.extend(pool[:n])

    rng_state = _shuffle(selected, rng_state + 1)
    return selected[:count]


def _shuffle(lst, seed):
    """Deterministic Fisher-Yates shuffle using a simple LCG."""
    for i in range(len(lst) - 1, 0, -1):
        seed = (seed * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        j = seed % (i + 1)
        lst[i], lst[j] = lst[j], lst[i]
    return seed


def get_agent_choices():
    return [(f'{a["icon"]} {a["name"]}', key) for key, a in AGENTS.items()]


def get_agent(key):
    return AGENTS.get(key, AGENTS["builder"])
