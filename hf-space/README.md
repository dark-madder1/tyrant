---
title: Red Team Coder 4B Demo
emoji: 🔴
colorFrom: red
colorTo: gray
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Chat with the Red Team Coder 4B security model
models:
  - frEEtom3/redteam-coder-4b
tags:
  - cybersecurity
  - red-team
  - code-generation
  - qwen3
---

# Red Team Coder 4B — Interactive Demo

Chat with **frEEtom3/redteam-coder-4b**, a fine-tuned Qwen3-4B model specialized in offensive security and code generation.

## Features
- Streaming chat interface with full conversation history
- Adjustable generation parameters (temperature, top-p, max tokens)
- System prompt customization
- Runs on ZeroGPU (free A10G allocation)

## Model Details
- **Base model:** Qwen3-4B-Instruct (heretic4 variant)
- **Training:** QLoRA fine-tune with Unsloth on cybersecurity + coding datasets
- **License:** Apache 2.0

Requires `HF_TOKEN` secret with read access to the private model.
