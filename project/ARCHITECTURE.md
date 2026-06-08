# System Architecture

**CEM501 Communication Skills for CEM — Spring 2026** Hilal Esila Yağcıoğlu

---

## System Overview

The CEM501 Communication Agent is an AI-powered email management system designed for construction project managers. It automatically reads incoming project emails from a dedicated Gmail folder, classifies them by urgency (URGENT / ACTION / FYI / ARCHIVE), generates professional draft replies using Claude AI, and enables approval via a web dashboard or Telegram before sending. The system is built on modular design principles.

---

## Architecture Diagram

```
┌─────────────────────────┐
│       scheduler.py       │
│  (every 30 min + 08:00) │
└───────────┬─────────────┘
            │
            v
┌───────────────────────────────────────────┐
│                 agent.py                  │
│                                           │
│  reader.py ──> classifier ──> drafter.py  │
│      │              │              │      │
│   (IMAP)        (keywords)     (Claude)   │
└───────────────────────┬───────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            v                       v
┌───────────────────┐   ┌───────────────────┐
│  shared_state.py  │   │    digest.py       │
│  (pending drafts) │   │  (daily summary)   │
└─────────┬─────────┘   └───────────────────┘
          │
          ├─────────────────────────────────┐
          │                                 │
          v                                 v
┌─────────────────────┐         ┌───────────────────────┐
│  dashboard.py       │         │  telegram_channel.py   │
│  (Flask web UI)     │         │  /list /approve /skip  │
│  localhost:5050     │         └──────────┬────────────┘
│  ▶ Run Agent        │                    │
│  Approve / Skip     │                    │
└────────┬────────────┘                    │
         │                                 │
         └──────────────┬──────────────────┘
                        │
                        v
          ┌─────────────────────────┐
          │        sender.py        │
          │    (SMTP → email sent)  │
          └─────────────┬───────────┘
                        │
                        v
          ┌─────────────────────────┐
          │        memory.py        │
          │    (SQLite — audit log) │
          └─────────────────────────┘

┌─────────────────────────┐
│         run.py           │
│  Launches dashboard.py  │
│  + telegram_channel.py  │
│  with a single command  │
└─────────────────────────┘

```

---

## Components

### Reader

- **File:** `reader.py`
- **Responsibility:** Connects to Gmail via IMAP, fetches all **unread (UNSEEN)** emails from the CEM501 folder, parses sender, subject, date, and body preview. Emails are marked as read after fetching to prevent duplicate processing.
- **Key dependencies:** `imaplib`, `email`, `python-dotenv`

### Classifier

- **File:** `reader.py` (`assign_triage_category` function)
- **Responsibility:** Classifies each email into URGENT, ACTION, FYI, or ARCHIVE using keyword-based rules. URGENT keywords include "stop work", "urgent", "failed", "leak", "emergency". ACTION keywords include "RFI", "approval", "review", "action", "confirm".
- **Key dependencies:** Built-in Python string matching

### Drafter

- **File:** `drafter.py`
- **Responsibility:** Generates professional draft email replies using Claude AI (`claude-haiku-4-5`). Takes email category, sender, subject, and preview as input and returns a context-appropriate reply within 150 words.
- **Key dependencies:** `anthropic`, `python-dotenv`

### Sender

- **File:** `sender.py`
- **Responsibility:** Sends approved drafts via SMTP. Two modes: interactive (y/n confirmation in terminal) and silent (for dashboard and Telegram bot use). Includes rate limiting (10 emails per 10 minutes) and `sent_log.txt` logging.
- **Key dependencies:** `smtplib`, `python-dotenv`

### Shared State

- **File:** `shared_state.py`
- **Responsibility:** Saves and loads pending drafts as a JSON file (`pending_drafts.json`). Bridges `agent.py`, `dashboard.py`, and `telegram_channel.py` so drafts produced by the agent can be approved from either interface.
- **Key dependencies:** `json`

### Web Dashboard *(NEW — Week 14)*

- **File:** `dashboard.py`
- **Responsibility:** Flask web application serving a real-time dashboard at `localhost:5050`. Features: **▶ Run Agent** button (triggers `agent.py --dry-run` as subprocess), pending drafts panel (approve/skip with one click), message history, and live statistics (URGENT, ACTION, pending drafts, total). Auto-refreshes every 30 seconds.
- **Key dependencies:** `flask`, `sqlite3`, `json`, `smtplib`

### Launcher *(NEW — Week 14)*

- **File:** `run.py`
- **Responsibility:** Single-command launcher that starts both `dashboard.py` (main thread) and `telegram_channel.py` (background thread) simultaneously. Eliminates the need for multiple terminals.
- **Key dependencies:** `threading`, `subprocess`

### Telegram Bot

- **File:** `telegram_channel.py`
- **Responsibility:** Two functions: (1) **Field reports** — receives free-text messages from field workers, classifies and drafts email replies, sends on `/send` approval. (2) **Draft approval** — lists pending drafts from agent via `/list`, approves via `/approve_N`, discards via `/skip_N`. Receives URGENT and ACTION alerts automatically after each agent run.
- **Key dependencies:** `python-telegram-bot`, `python-dotenv`

### Memory

- **File:** `memory.py`
- **Responsibility:** SQLite database tracking all sent and received messages. Three tables: `contacts`, `message_history`, `scheduled_tasks`. Provides full audit trail for all communications.
- **Key dependencies:** `sqlite3`

### Digest

- **File:** `digest.py`
- **Responsibility:** Generates a formatted morning summary of all emails by category. Saves to `logs/` folder with timestamp.
- **Key dependencies:** `datetime`

### Scheduler

- **File:** `scheduler.py`
- **Responsibility:** Runs the agent pipeline automatically — daily digest at 08:00 and email check every 30 minutes. No manual intervention needed.
- **Key dependencies:** `schedule`

### Agent (Main Pipeline)

- **File:** `agent.py`
- **Responsibility:** Orchestrates the full pipeline — fetch → classify → digest → log → draft → save to shared state → Telegram alert. Supports `--dry-run` mode (no direct sending; routes to dashboard/Telegram for approval).
- **Key dependencies:** All modules above

---

## Data Flow

1. `run.py` starts `dashboard.py` and `telegram_channel.py` simultaneously
2. User clicks **▶ Run Agent** on dashboard → triggers `agent.py --dry-run`
3. `reader.py` connects to Gmail CEM501 folder via IMAP, fetches UNSEEN emails
4. `classifier` categorizes each email (URGENT / ACTION / FYI / ARCHIVE)
5. `digest.py` generates morning summary, saves to `logs/`
6. `memory.py` logs all received emails to SQLite
7. `drafter.py` generates AI reply for URGENT and ACTION emails
8. `shared_state.py` saves drafts to `pending_drafts.json`
9. Telegram bot receives alert for URGENT and ACTION emails
10. User approves via **dashboard** (Approve button) or **Telegram** (`/approve_N`)
11. `sender.py` dispatches email via SMTP
12. `memory.py` logs sent email

---

## Design Decisions

**Decision: Keyword-based classification instead of LLM-based.** Context: Keyword matching is faster, cheaper, and more predictable for construction-specific terminology. LLM classification adds latency and cost for every email. Consequences: Less flexible for novel email types, but reliable and free for standard CEM categories.

**Decision: Human confirmation required before every send (via dashboard or Telegram).** Context: AI-generated emails can contain errors. In construction, a misdirected email can have legal and contractual consequences worth millions. Consequences: No emails sent without explicit user approval. Slower but safer.

**Decision: Dual approval interface (dashboard + Telegram).** Context: Project managers are often away from their desk. Telegram enables approval from mobile; the web dashboard provides a full review interface at the desk. Consequences: More complex architecture, but significantly better usability in real CEM scenarios.

**Decision: Shared state via JSON file instead of database.** Context: A simple JSON file allows `agent.py`, `dashboard.py`, and `telegram_channel.py` to share data without running in the same process. Easy to inspect and debug. Consequences: Not suitable for concurrent access by multiple users, but sufficient for a single-user agent.

**Decision: UNSEEN-only email fetching.** Context: Fetching all emails repeatedly caused duplicate drafts. Switching to UNSEEN ensures each email is processed exactly once. Consequences: Emails must be marked unread to be re-processed (intentional behavior).

---

## API Keys & Configuration


| Variable                | Purpose                                    |
| ----------------------- | ------------------------------------------ |
| `ANTHROPIC_API_KEY`     | Claude AI for draft generation             |
| `EMAIL_ADDRESS`         | Gmail account for IMAP/SMTP                |
| `EMAIL_PASSWORD`        | App-specific password                      |
| `IMAP_SERVER`           | `imap.gmail.com`                           |
| `TELEGRAM_BOT_TOKEN`    | Telegram bot authentication                |
| `TELEGRAM_CHAT_ID`      | Your Telegram chat ID for alerts           |
| `PROJECT_MANAGER_EMAIL` | Email address for Telegram-triggered sends |


---

## Current Status (Week 14 — Final)


| Component           | Status    | Notes                              |
| ------------------- | --------- | ---------------------------------- |
| Reader              | ✅ Working | UNSEEN-only fetching               |
| Classifier          | ✅ Working | Expanded keyword list              |
| Drafter (Claude AI) | ✅ Working | claude-haiku-4-5                   |
| Sender              | ✅ Working | Silent mode for dashboard/Telegram |
| Shared State        | ✅ Working | Bridges all approval interfaces    |
| Telegram Bot        | ✅ Working | Alerts + /list /approve /skip      |
| Memory (SQLite)     | ✅ Working | Full audit log                     |
| Digest              | ✅ Working | Saved to logs/                     |
| Scheduler           | ✅ Working | 30-min checks + daily digest       |
| **Web Dashboard**   | ✅ Working | **NEW — Flask, localhost:5050**    |
| **run.py Launcher** | ✅ Working | **NEW — single command start**     |


---

## Future Improvements

- LLM-based classifier to handle novel email types beyond keyword matching
- PDF attachment parsing for RFIs and submittal documents

---

*CEM501 — Spring 2026 — Dr. Eyuphan Koc — Bogazici University*

