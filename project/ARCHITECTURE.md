# System Architecture

**CEM501 Communication Skills for CEM -- Spring 2026**  
Hilal Esila Yağcıoğlu 

---

## System Overview

The CEM501 Communication Agent is an AI-powered email management system designed for construction project managers. It automatically reads incoming project emails, classifies them by urgency (URGENT/ACTION/FYI/ARCHIVE), generates professional draft replies using Claude AI, and enables approval via Telegram before sending. The system is built on modular design principles — each component has a single responsibility and can be tested independently.

### Architecture Diagram

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
          v
┌───────────────────────────────────────┐
│         telegram_channel.py           │
│  /list → /approve_N → sender.py       │
└─────────────────┬─────────────────────┘
                  │
                  v
┌───────────────────────────────────────┐
│              sender.py                │
│           (SMTP → email sent)         │
└─────────────────┬─────────────────────┘
                  │
                  v
┌───────────────────────────────────────┐
│              memory.py                │
│          (SQLite — audit log)         │
└───────────────────────────────────────┘
```



---

## ---

## Components

### Reader

- **File:** `reader.py`

- **Responsibility:** Connects to Gmail via IMAP, fetches the 20 most recent emails from the CEM501 folder, parses sender, subject, date, and body preview.

- **Key dependencies:** `imaplib`, `email`, `python-dotenv`

### Classifier

- **File:** `reader.py` (assign_triage_category function)

- **Responsibility:** Classifies each email into URGENT, ACTION, FYI, or ARCHIVE using keyword-based rules. URGENT keywords include "stop work", "urgent", "failed", "pump". ACTION keywords include "RFI", "approval", "review".

- **Key dependencies:** Built-in Python string matching

### Drafter

- **File:** `drafter.py`

- **Responsibility:** Generates professional draft email replies using Claude AI (claude-haiku-4-5). Takes email category, sender, subject, and preview as input and returns a context-appropriate reply.

- **Key dependencies:** `anthropic`, `python-dotenv`

### Sender

- **File:** `sender.py`

- **Responsibility:** Sends approved drafts via SMTP. Two modes: interactive (y/n confirmation in terminal) and silent (for Telegram bot use). Includes rate limiting and sent_log.txt logging.

- **Key dependencies:** `smtplib`, `python-dotenv`

### Shared State

- **File:** `shared_state.py`

- **Responsibility:** Saves and loads pending drafts as a JSON file. Bridges [agent.py](http://agent.py) and telegram_[channel.py](http://channel.py) so drafts produced by the agent can be approved via Telegram.

- **Key dependencies:** `json`

### Telegram Bot

- **File:** `channels/telegram_channel.py`

- **Responsibility:** Two functions: (1) Field reports — receives messages from field workers, classifies and drafts email replies, sends on approval. (2) Draft approval — lists pending drafts from agent via /list, approves via /approve_N, discards via /skip_N.

- **Key dependencies:** `python-telegram-bot`, `python-dotenv`

### Memory

- **File:** `memory.py`

- **Responsibility:** SQLite database tracking all sent and received messages. Three tables: contacts, message_history, scheduled_tasks. Provides audit trail for all communications.

- **Key dependencies:** `sqlite3`

### Digest

- **File:** `digest.py`

- **Responsibility:** Generates a formatted morning summary of all emails by category. Saves to logs/ folder with timestamp.

- **Key dependencies:** `datetime`

### Scheduler

- **File:** `scheduler.py`

- **Responsibility:** Runs the agent pipeline automatically — daily digest at 08:00 and email check every 30 minutes. No manual intervention needed.

- **Key dependencies:** `schedule`

### Agent (Main Pipeline)

- **File:** `agent.py`

- **Responsibility:** Orchestrates the full pipeline — fetch → classify → digest → log → draft → save to shared state → Telegram alert. Supports --dry-run mode.

- **Key dependencies:** All modules above

---

## Data Flow

1. **Scheduler** triggers [agent.py](http://agent.py) every 30 minutes

2. **Reader** connects to Gmail CEM501 folder via IMAP, fetches emails

3. **Classifier** categorizes each email (URGENT/ACTION/FYI/ARCHIVE)

4. **Digest** generates morning summary, saves to logs/

5. **Memory** logs all received emails to SQLite

6. **Drafter** generates AI reply for URGENT and ACTION emails

7. **Shared State** saves drafts to pending_drafts.json

8. **Telegram Bot** receives alert, user runs /list to see drafts

9. User runs /approve_N → **Sender** dispatches email via SMTP

10. **Memory** logs sent email

---

## Design Decisions

**Decision:** Keyword-based classification instead of LLM-based.

**Context:** Keyword matching is faster, cheaper, and more predictable for construction-specific terminology. LLM classification adds latency and cost for every email.

**Consequences:** Less flexible for novel email types, but reliable and free for standard CEM categories.

---

**Decision:** Human confirmation required before every send (via Telegram or terminal).

**Context:** AI-generated emails can contain errors. In construction, a misdirected email can have legal and contractual consequences worth millions.

**Consequences:** No emails sent without explicit user approval. Slower but safer.

---

**Decision:** Shared state via JSON file instead of database.

**Context:** A simple JSON file allows [agent.py](http://agent.py) and telegram_[channel.py](http://channel.py) to share data without running in the same process. Easy to inspect and debug.

**Consequences:** Not suitable for concurrent access by multiple users, but sufficient for a single-user agent.

---

## API Keys & Configuration

| Variable | Purpose |

| ANTHROPIC_API_KEY | Claude AI for draft generation |

| EMAIL_ADDRESS | Gmail account for IMAP/SMTP |

| EMAIL_PASSWORD | App-specific password |

| IMAP_SERVER | [imap.gmail.com](http://imap.gmail.com) |

| SMTP_SERVER | [smtp.gmail.com](http://smtp.gmail.com) |

| SMTP_PORT | 587 |

| TELEGRAM_BOT_TOKEN | Telegram bot authentication |

| TELEGRAM_CHAT_ID | Your Telegram chat ID for alerts |

| PROJECT_MANAGER_EMAIL | Email address for Telegram-triggered sends |

---

 Current Status (Week 13)

| Component | Status |

| Reader | ✅ Working |

| Classifier | ✅ Working |

| Drafter (Claude AI) | ✅ Working |

| Sender | ✅ Working |

| Shared State | ✅ Working |

| Telegram Bot | ✅ Working |

| Memory (SQLite) | ✅ Working |

| Digest | ✅ Working |

| Scheduler | ✅ Working |

---

 Future Improvements (Week 14)

- Improve classifier with LLM-based intent detection (not just keywords)

- Add WhatsApp channel via Twilio

- Add web dashboard for reviewing drafts

- Fine-tune prompts with project-specific contract language

- Add attachment parsing (PDF RFIs, submittal documents)

