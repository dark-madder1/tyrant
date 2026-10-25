---
title: CyberForge
emoji: "⚒️"
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: AI cybersecurity coding suite — Red Team + Blue Team + Threat Intel
models:
  - frEEtom3/redteam-coder-4b
tags:
  - ide
  - multi-agent
  - cybersecurity
  - red-team
  - blue-team
  - threat-intelligence
  - code-generation
  - qwen3
---

# CyberForge — AI Cybersecurity Coding Suite

A browser-based AI-powered coding environment with **multi-agent orchestration**
for full-spectrum cybersecurity. Think VS Code meets Cursor — offensive, defensive,
and intel agents powered by fine-tuned models, running free on ZeroGPU.

## Agents

| Agent | Role | Use For |
|-------|------|---------|
| \U0001f534 Red Team Coder | Offensive security | Exploits, scanners, pentesting tools, privilege escalation |
| \U0001f6e1️ Blue Team Coder | Defensive security | SIEM rules, IDS signatures, hardening, incident response |
| \U0001f50e Threat Intel | Intelligence & analysis | IOC parsing, MITRE ATT&CK mapping, STIX/TAXII, threat feeds |
| \U0001f7e2 Code Builder | General development | Any language, any framework, clean production code |
| \U0001f535 Architect | System design | Project scaffolding, API design, architecture planning |
| \U0001f7e1 Reviewer | Code review | Bug hunting, security audit, optimization suggestions |
| \U0001f7e0 Debug Agent | Error diagnosis | Stack traces, root cause analysis, targeted fixes |
| \U0001f7e3 Orchestrator | Task decomposition | Splits big projects across agents automatically |

## Features

- VS Code-inspired dark editor with syntax highlighting
- Virtual file system with multi-tab editing
- Streaming AI chat with agent selection
- One-click templates for offensive, defensive, and intel tasks
- Multi-agent orchestrator for large projects
- Beginner-friendly — tooltips, templates, clear labels

## Getting Started

1. Pick a **template** from the Home tab (or go straight to the Editor)
2. Choose an **agent** in the left sidebar
3. Describe what you want in the **chat panel**
4. Code appears in your **editor** automatically
5. For big projects, use the **Orchestrator** tab

Requires `HF_TOKEN` secret with read access to the model.
