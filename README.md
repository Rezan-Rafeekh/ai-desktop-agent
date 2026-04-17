<div align="center">

<br/>

```
██████╗ ███████╗███████╗██╗  ██╗████████╗ ██████╗ ██████╗ 
██╔══██╗██╔════╝██╔════╝██║ ██╔╝╚══██╔══╝██╔═══██╗██╔══██╗
██║  ██║█████╗  ███████╗█████╔╝    ██║   ██║   ██║██████╔╝
██║  ██║██╔══╝  ╚════██║██╔═██╗    ██║   ██║   ██║██╔═══╝ 
██████╔╝███████╗███████║██║  ██╗   ██║   ╚██████╔╝██║     
╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     
```

# 🧠 Intelligent Desktop Agent

### *"Tell it what you want. Watch it work."*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq_LLM-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-00d9ff?style=for-the-badge)](LICENSE)

<br/>

> **A natural-language-driven desktop automation agent that plans, executes, and self-heals — powered by Vision LLMs, autonomous retry logic, and persistent memory.**

<br/>

</div>

---

## 🎯 The Problem We're Solving

> Every day, knowledge workers lose **hours** to repetitive, multi-app workflows — opening Excel, writing reports in Word, composing emails in Outlook — one by one, manually, every single time.

**What if you could just say:** *"Create a sales report and email it to the team"* — and walk away?

---

## ✨ What Is Desktop Agent?

Desktop Agent is an **AI-powered autonomous workflow engine** that:

- 🗣️ **Understands natural language** commands — no scripting, no macros
- 🧩 **Decomposes goals** into ordered executable steps using an LLM planner
- 🖥️ **Controls real desktop apps** — Excel, Word, Outlook, VS Code — via GUI automation
- 👁️ **Sees the screen** using a Vision LLM to verify each action was successful
- 🔁 **Self-heals** — autonomously retries failed steps up to 3 times
- 🧠 **Remembers** — stores successful workflows and reuses them intelligently

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│           Streamlit UI  ←→  FastAPI WebSocket API               │
└───────────────────────────┬─────────────────────────────────────┘
                            │  Natural Language Command
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     🧠 LLM PLANNER                              │
│         Groq (llama-3.1-8b-instant) — Zero-shot intent mapping  │
│         Input: "create report and email it"                     │
│         Output: ["write_excel", "generate_report_doc",          │
│                  "send_email"]                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │  Structured Plan
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ⚙️  EXECUTOR ENGINE                          │
│                                                                 │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│   │  Excel   │   │  Word    │   │  Email   │   │  VSCode  │   │
│   │  Action  │   │  Action  │   │  Action  │   │  Action  │   │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘   │
│                                                                 │
│   Retry Logic: 3 attempts per step + cooldown delay            │
└───────────────────────────┬─────────────────────────────────────┘
                            │  PyAutoGUI Commands
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   👁️  VISION LAYER (agent.py)                   │
│        Observe → Plan → Act → Verify  loop                      │
│        llama-3.2-11b-vision-preview                             │
│        Screenshots compared before/after each action            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   💾  MEMORY SYSTEM                             │
│        Successful plans saved to tasks_memory.json              │
│        60%+ keyword match → reuse historical plan               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 🗣️ **Natural Language Input** | Plain English commands — no syntax to learn |
| 🧩 **LLM Task Planner** | Groq-powered zero-shot decomposition of goals into steps |
| 👁️ **Vision-Based Verification** | Screenshots before/after every action confirm success |
| 🔁 **Autonomous Retry** | 3-attempt self-healing with cooldown, no human needed |
| 🧠 **Persistent Memory** | Learns from past runs; reuses patterns intelligently |
| 📊 **Live UI Dashboard** | Real-time thought stream, step timeline, and screen feed |
| 🌐 **Dual Interface** | Streamlit UI for demos + FastAPI WebSocket API for integration |
| ⛔ **Abort Control** | Mid-execution stop signal with graceful step finalization |

---

## 🛠️ Tech Stack

```
┌─────────────────┬────────────────────────────────────────────┐
│ Layer           │ Technology                                 │
├─────────────────┼────────────────────────────────────────────┤
│ LLM Brain       │ Groq API — llama-3.1-8b-instant            │
│ Vision          │ Groq — llama-3.2-11b-vision-preview        │
│ GUI Automation  │ PyAutoGUI + win32com                        │
│ Screen Capture  │ Pillow (ImageGrab)                         │
│ Frontend        │ Streamlit (dashboard)                       │
│ Backend API     │ FastAPI + WebSockets                        │
│ Memory Store    │ JSON (tasks_memory.json)                   │
│ Office Actions  │ openpyxl, python-docx, win32com Outlook    │
│ Config          │ python-dotenv                               │
└─────────────────┴────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
desktop-agent/
│
├── 🎯 app.py               # Streamlit UI — live dashboard & agent controls
├── 🌐 api.py               # FastAPI WebSocket server for programmatic access
│
├── 🧠 planner.py           # LLM-powered task decomposition
├── ⚙️  executor.py          # Core execution engine with retry logic
├── 🤖 agent.py             # Observe→Plan→Act→Verify vision loop
│
├── 👁️  vision.py            # Screen capture + Vision LLM analysis
├── 🔤 llm.py               # All LLM calls: planning, extraction, summarization
├── 💾 memory.py            # Persistent memory: save, load, similarity search
│
├── actions/
│   ├── 📊 excel.py         # Excel automation — tables, charts, save
│   ├── 📝 word.py          # Word doc generation with LLM-written content
│   ├── 📧 email.py         # Outlook email compose + attach + send
│   ├── 💻 vscode.py        # VS Code Python file generation
│   └── 📁 file_reader.py   # Desktop file discovery + content extraction
│
├── 🎭 demo.py              # 3-stage ideathon demo runner
└── 📋 prompt_history.json  # Recent successful prompts
```

---

## ⚡ Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/your-org/desktop-agent.git
cd desktop-agent
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Launch Dashboard

```bash
streamlit run app.py
```

### 4. Or run the Ideathon Demo directly

```bash
python demo.py
```

---

## 🎭 Demo Workflow (3 Stages)

The `demo.py` runs a live end-to-end showcase:

```
Stage 1 → 📊 Excel
          "Open Excel, enter a 5-row sales table, add a chart, save as SalesReport.xlsx"

Stage 2 → 📝 Word
          "Open Word, write a 3-paragraph project summary report, save as Report.docx"

Stage 3 → 📧 Outlook
          "Open Outlook, compose email to test@example.com, attach files above, send it"
```

Each stage runs fully autonomously. The agent plans, acts, verifies, and retries — no human in the loop.

---

## 🧠 How the LLM Planner Works

Given the command:

```
"Create a student report and email it"
```

The planner sends it to `llama-3.1-8b-instant` with strict mapping rules and gets back:

```json
["generate_report_doc", "send_email"]
```

The executor resolves these step names and runs them sequentially — with the Memory system checking for similar past tasks first.

---

## 👁️ Vision Verification Loop

After every PyAutoGUI action, the agent:

1. **Captures** a screenshot (before)
2. **Executes** the action (click / type / hotkey)
3. **Captures** another screenshot (after)
4. **Asks the Vision LLM:** *"Did the expected change happen?"*
5. If not → logs it and continues to next attempt

This makes the agent resilient to UI lag, focus loss, and unexpected popups.

---

## 💾 Memory System

```python
# After every successful run:
save_task(task, plan, result_summary)

# Before every new run:
similar = find_similar_task(new_task)
# If >60% keyword overlap → reuse historical plan
```

Memory is stored at `~/Desktop/tasks_memory.json` and surfaced in the Streamlit sidebar as clickable prompt history.

---

## 🌐 API Usage (WebSocket)

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/agent");

ws.send(JSON.stringify({
  task: "Create a sales report and email it to boss@company.com",
  use_llm: true
}));

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // { type: "log", step: "write_excel", status: "done", msg: "..." }
  // { type: "done" }
};
```

---

## 🔒 Design Principles

- **Precision over hallucination** — LLM planner uses temperature=0.0 and strict allowlists
- **No phantom apps** — steps filtered against `VALID_STEPS`; unknown steps are skipped, never guessed
- **Fail loudly, recover quietly** — errors surface in UI with full context; retries are silent
- **Real data only** — data extraction pipeline never invents records; empty result = validation error
- **Deduplication** — consecutive identical steps in a plan are collapsed before execution

---

## 🧪 Running Tests

```bash
# Unit test the planner
python -c "from planner import create_plan, detect_goals; print(create_plan(detect_goals('write excel report')))"

# Test memory
python -c "from memory import get_memory_stats; print(get_memory_stats())"

# Full demo
python demo.py
```

---

## 🗺️ Roadmap

- [ ] 🔊 Voice input (Whisper integration)
- [ ] 🪟 Multi-monitor support
- [ ] 🐍 Python REPL action type
- [ ] 🔗 MCP (Model Context Protocol) tool integrations
- [ ] ☁️ Cloud execution mode (remote desktop)
- [ ] 📱 Mobile trigger via REST API

---

## 👥 Team

> Built for **Philips Ideathon 2026** — *Automating the Future of Knowledge Work*

| Role | Contribution |
|---|---|
| 🧠 AI & Planning | LLM planner, prompt engineering, memory system |
| 👁️ Vision & Control | Screen capture, PyAutoGUI, verification loop |
| 🎨 UI & API | Streamlit dashboard, FastAPI WebSocket server |
| ⚙️ Actions | Excel, Word, Outlook, VS Code automation modules |

---

<div align="center">

<br/>

### *"The best automation is the kind you never have to think about."*

<br/>

**Made with 🧠 + ☕ for Philips Ideathon 2026**

<br/>

![Visitors](https://img.shields.io/badge/Built%20for-Philips%20Ideathon%202026-0B5ED7?style=for-the-badge)

</div>
