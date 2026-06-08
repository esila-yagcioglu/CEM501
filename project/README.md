# CEM501 Communication Agent

**CEM501 Communication Skills for CEM — Spring 2026** Bogazici University | Dr. Eyuphan Koc

---

## Student Information


|                |                                                                                        |
| -------------- | -------------------------------------------------------------------------------------- |
| **Name**       | Hilal Esila Yağcıoğlu                                                                  |
| **Student ID** | 2025722042                                                                             |
| **Email**      | [esilayagcioglu@gmail.com](mailto:esilayagcioglu@gmail.com)                            |
| **GitHub**     | [https://github.com/esila-yagcioglu/CEM501](https://github.com/esila-yagcioglu/CEM501) |


---

## Description

An AI-powered email communication agent designed for construction project engineers. The agent connects to a dedicated Gmail folder (CEM501), reads incoming emails, classifies them into URGENT / ACTION / FYI / ARCHIVE categories using keyword-based triage, and generates context-aware professional draft replies using Claude AI. Drafts can be reviewed and approved via a web dashboard or Telegram bot.

The system addresses a real CEM pain point: project managers spend 2–3 hours daily managing email across subcontractors, clients, and consultants. This agent cuts that to minutes by automating triage, drafting, and sending.

---

## Architecture Overview

See [ARCHITECTURE.md](http://ARCHITECTURE.md) for the full system architecture, component descriptions, and data flow diagram.

**High-level summary:** A modular pipeline that reads incoming emails from Gmail via IMAP, classifies them by urgency using keyword triage, drafts context-aware replies using the Anthropic Claude API, and routes them for approval via a Flask web dashboard or Telegram bot before sending via SMTP.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/esila-yagcioglu/CEM501.git
cd CEM501/project

```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

```

### 3. Install dependencies

```bash
pip install -r requirements.txt

```

### 4. Configure environment variables

```bash
cp .env.example .env

```

Edit `.env` with your credentials:

```env
# Gmail (use an App Password, not your account password)
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
IMAP_SERVER=imap.gmail.com

# Anthropic
ANTHROPIC_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
PROJECT_MANAGER_EMAIL=pm@example.com

```

> **Gmail setup:** Enable IMAP in Gmail settings, create an App Password under Google Account → Security → 2-Step Verification → App Passwords. Create a label/folder called `CEM501` in Gmail.

### 5. Verify setup

```bash
python -c "import anthropic; print('Anthropic OK')"
python -c "from reader import fetch_recent_emails; print('Reader OK')"

```

---

## How to Run

### Start everything (dashboard + Telegram bot)

```bash
python run.py

```

Then open your browser at: **[http://localhost:5050](http://localhost:5050)**

This single command starts:

- The **web dashboard** at `localhost:5050`
- The **Telegram bot** in the background

### Dashboard features

- **▶ Run Agent** button — fetches unread emails from CEM501 folder, classifies, and generates drafts
- **Pending Drafts** panel — review AI-generated replies, approve to send or skip to discard
- **Message History** — log of all received and sent emails
- **Live statistics** — URGENT, ACTION, pending drafts, total count

### Telegram bot commands


| Command       | Action                           |
| ------------- | -------------------------------- |
| `/list`       | Show pending drafts              |
| `/approve_N`  | Approve and send draft N         |
| `/skip_N`     | Discard draft N                  |
| Send any text | Generate draft from field report |


### Run agent only (without dashboard)

```bash
python agent.py --dry-run

```

---

## Project Structure

```
project/
├── agent.py              # Main orchestrator
├── reader.py             # Gmail IMAP reader + email triage classifier
├── drafter.py            # Claude AI draft generator
├── sender.py             # SMTP email sender
├── memory.py             # SQLite message history (memory.db)
├── digest.py             # Morning digest generator
├── scheduler.py          # Automated scheduling (every 30 min)
├── shared_state.py       # pending_drafts.json read/write
├── dashboard.py          # Flask web dashboard + API
├── run.py                # Launcher: dashboard + Telegram bot together
├── telegram_channel.py   # Telegram bot (approve/skip via chat)
├── requirements.txt
├── .env.example
├── README.md
├── ARCHITECTURE.md
├── REFLECTION.md
├── agent.log
└── logs/                 # Digest log files

```

---

## Milestones Completed


| Milestone | Description                                                                              |
| --------- | ---------------------------------------------------------------------------------------- |
| M0        | Environment setup, API key configuration, Gmail IMAP connection                          |
| M1        | Email reading via IMAP from dedicated CEM501 Gmail folder                                |
| M2        | Keyword-based email triage classifier (URGENT / ACTION / FYI / ARCHIVE)                  |
| M3        | AI draft generation via Claude API with CEM-specific prompting                           |
| M4        | Email sending via SMTP with rate limiting and safety checks                              |
| M5        | Architecture documentation and code review                                               |
| M6        | SQLite conversation memory and message history logging                                   |
| M7        | Automated scheduling (daily digest at 08:00, email check every 30 min)                   |
| M8        | Telegram bot integration (notifications, /list, /approve, /skip)                         |
| M9        | Flask web dashboard, [run.py](http://run.py) launcher, final polish and demo preparation |


---

## AI Tools Used


| Tool / Model                           | How It Was Used                                                  |
| -------------------------------------- | ---------------------------------------------------------------- |
| Claude Haiku (claude-haiku-4-5)        | Email draft generation in [drafter.py](http://drafter.py)        |
| Claude ([claude.ai](http://claude.ai)) | Architecture design, debugging, code review, prompt engineering  |
| Claude Code                            | Iterative development of all modules, debugging IMAP/SMTP issues |


---

## Reflection

See [REFLECTION.md](http://REFLECTION.md) for the full project reflection, including communication lessons, AI-assisted development insights, and connection to professional practice.

---

*CEM501 — Spring 2026 — Dr. Eyuphan Koc — Bogazici University*