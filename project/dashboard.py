"""
CEM501 Communication Agent — Web Dashboard
Flask backend: reads memory.db and pending_drafts.json
Run with: python dashboard.py
"""

from flask import Flask, jsonify, render_template_string, request
import sqlite3
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(override=True)

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")
DRAFTS_PATH = os.path.join(os.path.dirname(__file__), "pending_drafts.json")

# ─── HTML TEMPLATE ──────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CEM501 Communication Agent</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

  :root {
    --bg: #f4f6f9;
    --surface: #ffffff;
    --surface2: #f0f2f5;
    --border: #e2e6ed;
    --text: #1a202c;
    --muted: #7a8599;
    --urgent: #dc2626;
    --urgent-bg: #fff0f0;
    --action: #d97706;
    --action-bg: #fffbeb;
    --fyi: #2563eb;
    --fyi-bg: #eff6ff;
    --archive: #6b7280;
    --archive-bg: #f9fafb;
    --green: #059669;
    --accent: #4f46e5;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
    min-height: 100vh;
  }

  /* ── Header ── */
  header {
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    position: sticky;
    top: 0;
    background: var(--surface);
    z-index: 100;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: var(--text);
  }

  .logo-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.8rem;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
  }

  #last-updated { color: var(--muted); }

  .refresh-btn {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 0.35rem 0.9rem;
    border-radius: 6px;
    font-size: 0.78rem;
    font-family: 'IBM Plex Mono', monospace;
    cursor: pointer;
    transition: all 0.15s;
  }
  .refresh-btn:hover { background: var(--accent); border-color: var(--accent); color: #fff; }

  .run-btn {
    background: var(--accent);
    border: 1px solid var(--accent);
    color: #fff;
    padding: 0.35rem 1.1rem;
    border-radius: 6px;
    font-size: 0.78rem;
    font-family: 'IBM Plex Mono', monospace;
    cursor: pointer;
    transition: all 0.15s;
    font-weight: 600;
  }
  .run-btn:hover { background: #3730a3; border-color: #3730a3; }
  .run-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  /* ── Agent status bar ── */
  #agent-status {
    margin-bottom: 1.5rem;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    font-size: 0.8rem;
    font-family: 'IBM Plex Mono', monospace;
    display: none;
    align-items: center;
    gap: 0.6rem;
  }
  #agent-status.running {
    display: flex;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
  }
  #agent-status.success {
    display: flex;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #15803d;
  }
  #agent-status.error {
    display: flex;
    background: #fff0f0;
    border: 1px solid #fecaca;
    color: #dc2626;
  }

  .spinner {
    width: 14px; height: 14px;
    border: 2px solid #bfdbfe;
    border-top-color: #1d4ed8;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Layout ── */
  main {
    max-width: 1300px;
    margin: 0 auto;
    padding: 2rem;
  }

  /* ── Stats Row ── */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.15s;
  }
  .stat-card:hover { transform: translateY(-2px); }

  .stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
  }
  .stat-card.urgent::before { background: var(--urgent); }
  .stat-card.action::before { background: var(--action); }
  .stat-card.fyi::before    { background: var(--fyi); }
  .stat-card.total::before  { background: var(--accent); }

  .stat-label {
    font-size: 0.7rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
  }

  .stat-value {
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
    font-family: 'IBM Plex Mono', monospace;
  }
  .stat-card.urgent .stat-value { color: var(--urgent); }
  .stat-card.action .stat-value { color: var(--action); }
  .stat-card.fyi    .stat-value { color: var(--fyi); }
  .stat-card.total  .stat-value { color: var(--accent); }

  .stat-sub { font-size: 0.75rem; color: var(--muted); }

  /* ── Two columns ── */
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  /* ── Section ── */
  .section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
  }

  .section-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .section-title {
    font-size: 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .badge {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.15rem 0.6rem;
    font-size: 0.7rem;
    font-family: 'IBM Plex Mono', monospace;
    color: var(--text);
  }

  .section-body { padding: 0; }

  /* ── Draft cards ── */
  .draft-card {
    padding: 1.2rem 1.5rem;
    border-bottom: 1px solid var(--border);
    transition: background 0.15s;
  }
  .draft-card:last-child { border-bottom: none; }
  .draft-card:hover { background: var(--surface2); }

  .draft-meta {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
  }

  .cat-badge {
    font-size: 0.65rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.08em;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-weight: 600;
  }
  .cat-URGENT { background: var(--urgent-bg); color: var(--urgent); border: 1px solid var(--urgent); }
  .cat-ACTION { background: var(--action-bg); color: var(--action); border: 1px solid var(--action); }
  .cat-FYI    { background: var(--fyi-bg);    color: var(--fyi);    border: 1px solid var(--fyi); }
  .cat-ARCHIVE{ background: var(--archive-bg);color: var(--archive);border: 1px solid var(--archive); }

  .draft-subject {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .draft-sender {
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 0.6rem;
    font-family: 'IBM Plex Mono', monospace;
  }

  .draft-preview {
    font-size: 0.8rem;
    color: #475569;
    line-height: 1.5;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.8rem;
    max-height: 80px;
    overflow: hidden;
    white-space: pre-wrap;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
  }

  .draft-actions { display: flex; gap: 0.5rem; }

  .btn {
    padding: 0.4rem 1rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s;
    letter-spacing: 0.03em;
  }

  .btn-approve {
    background: #ecfdf5;
    color: var(--green);
    border-color: var(--green);
  }
  .btn-approve:hover { background: var(--green); color: #fff; }

  .btn-skip {
    background: var(--surface2);
    color: var(--muted);
    border-color: var(--border);
  }
  .btn-skip:hover { background: #1f0a0a; color: var(--urgent); border-color: var(--urgent); }

  .btn-sending {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* ── History list ── */
  .history-item {
    padding: 0.9rem 1.5rem;
    border-bottom: 1px solid var(--border);
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.75rem;
    align-items: center;
    transition: background 0.15s;
  }
  .history-item:last-child { border-bottom: none; }
  .history-item:hover { background: var(--surface2); }

  .direction-icon {
    font-size: 0.9rem;
    width: 24px;
    text-align: center;
  }

  .history-subject {
    font-size: 0.82rem;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .history-sub {
    font-size: 0.7rem;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 0.15rem;
  }

  .history-time {
    font-size: 0.68rem;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
    white-space: nowrap;
  }

  /* ── Empty state ── */
  .empty {
    padding: 3rem;
    text-align: center;
    color: var(--muted);
    font-size: 0.82rem;
    font-family: 'IBM Plex Mono', monospace;
  }

  /* ── Toast ── */
  #toast {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: var(--surface);
    border: 1px solid var(--border);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-size: 0.82rem;
    font-family: 'IBM Plex Mono', monospace;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s;
    z-index: 999;
  }
  #toast.show { opacity: 1; transform: translateY(0); }
  #toast.success { border-color: var(--green); color: var(--green); }
  #toast.error   { border-color: var(--urgent); color: var(--urgent); }

  /* ── Full-width history ── */
  .full-width { grid-column: 1 / -1; }
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-dot"></div>
    CEM501 // COMMUNICATION AGENT
  </div>
  <div class="header-right">
    <span id="last-updated">—</span>
    <button class="refresh-btn" onclick="loadAll()">↻ refresh</button>
    <button class="run-btn" id="run-btn" onclick="runAgent()">▶ Run Agent</button>
  </div>
</header>

<main>
  <!-- Agent status bar -->
  <div id="agent-status"><div class="spinner" id="spinner"></div><span id="agent-status-text"></span></div>

  <!-- Stats -->
  <div class="stats-row" id="stats-row">
    <div class="stat-card urgent">
      <div class="stat-label">Urgent</div>
      <div class="stat-value" id="stat-urgent">—</div>
      <div class="stat-sub">emails</div>
    </div>
    <div class="stat-card action">
      <div class="stat-label">Action</div>
      <div class="stat-value" id="stat-action">—</div>
      <div class="stat-sub">emails</div>
    </div>
    <div class="stat-card fyi">
      <div class="stat-label">Pending Drafts</div>
      <div class="stat-value" id="stat-drafts">—</div>
      <div class="stat-sub">awaiting approval</div>
    </div>
    <div class="stat-card total">
      <div class="stat-label">Total Logged</div>
      <div class="stat-value" id="stat-total">—</div>
      <div class="stat-sub">messages</div>
    </div>
  </div>

  <!-- Drafts + History -->
  <div class="columns">

    <!-- Pending Drafts -->
    <div class="section">
      <div class="section-header">
        <div class="section-title">
          📋 Pending Drafts
          <span class="badge" id="drafts-count">0</span>
        </div>
      </div>
      <div class="section-body" id="drafts-list">
        <div class="empty">No pending drafts</div>
      </div>
    </div>

    <!-- Message History -->
    <div class="section">
      <div class="section-header">
        <div class="section-title">
          📨 Message History
          <span class="badge" id="history-count">0</span>
        </div>
      </div>
      <div class="section-body" id="history-list">
        <div class="empty">No messages yet</div>
      </div>
    </div>

  </div>
</main>

<div id="toast"></div>

<script>
async function runAgent() {
  const btn = document.getElementById('run-btn');
  const bar = document.getElementById('agent-status');
  const txt = document.getElementById('agent-status-text');
  const spinner = document.getElementById('spinner');

  btn.disabled = true;
  btn.textContent = '⏳ Running…';
  bar.className = 'running';
  spinner.style.display = 'block';
  txt.textContent = 'Agent running — fetching and classifying emails…';

  try {
    const r = await fetch('/api/run', { method: 'POST' });
    const d = await r.json();

    if (d.success) {
      bar.className = 'success';
      spinner.style.display = 'none';
      txt.textContent = `✓ Done — ${d.emails_found} emails found, ${d.drafts_created} drafts created.`;
      await loadAll();
    } else {
      bar.className = 'error';
      spinner.style.display = 'none';
      txt.textContent = '✕ Error: ' + (d.error || 'Agent failed');
    }
  } catch(e) {
    bar.className = 'error';
    spinner.style.display = 'none';
    txt.textContent = '✕ Could not reach agent: ' + e.message;
  }

  btn.disabled = false;
  btn.textContent = '▶ Run Agent';
  setTimeout(() => { bar.className = ''; }, 8000);
}

async function loadAll() {
  await Promise.all([loadStats(), loadDrafts(), loadHistory()]);
  document.getElementById('last-updated').textContent =
    'updated ' + new Date().toLocaleTimeString();
}

async function loadStats() {
  const r = await fetch('/api/stats');
  const d = await r.json();
  document.getElementById('stat-urgent').textContent = d.urgent;
  document.getElementById('stat-action').textContent  = d.action;
  document.getElementById('stat-drafts').textContent  = d.pending_drafts;
  document.getElementById('stat-total').textContent   = d.total;
}

async function loadDrafts() {
  const r = await fetch('/api/drafts');
  const drafts = await r.json();
  const el = document.getElementById('drafts-list');
  document.getElementById('drafts-count').textContent = drafts.length;

  if (!drafts.length) {
    el.innerHTML = '<div class="empty">No pending drafts ✓</div>';
    return;
  }

  el.innerHTML = drafts.map(d => `
    <div class="draft-card" id="draft-${d.id}">
      <div class="draft-meta">
        <span class="cat-badge cat-${d.category}">${d.category}</span>
        <span class="draft-subject" title="${d.subject}">${d.subject}</span>
      </div>
      <div class="draft-sender">From: ${d.sender}</div>
      <div class="draft-preview">${d.draft}</div>
      <div class="draft-actions">
        <button class="btn btn-approve" onclick="approveDraft(${d.id}, this)">
          ✓ Approve &amp; Send
        </button>
        <button class="btn btn-skip" onclick="skipDraft(${d.id}, this)">
          ✕ Skip
        </button>
      </div>
    </div>
  `).join('');
}

async function loadHistory() {
  const r = await fetch('/api/history');
  const history = await r.json();
  const el = document.getElementById('history-list');
  document.getElementById('history-count').textContent = history.length;

  if (!history.length) {
    el.innerHTML = '<div class="empty">No messages logged yet</div>';
    return;
  }

  el.innerHTML = history.map(h => `
    <div class="history-item">
      <div class="direction-icon">${h.direction === 'sent' ? '↑' : '↓'}</div>
      <div>
        <div class="history-subject">${h.subject}</div>
        <div class="history-sub">${h.contact_email} · <span class="cat-badge cat-${h.category}" style="font-size:0.62rem;padding:0.1rem 0.4rem">${h.category}</span></div>
      </div>
      <div class="history-time">${formatTime(h.sent_at)}</div>
    </div>
  `).join('');
}

async function approveDraft(id, btn) {
  btn.textContent = 'Sending…';
  btn.classList.add('btn-sending');
  btn.disabled = true;

  const r = await fetch(`/api/drafts/${id}/approve`, { method: 'POST' });
  const d = await r.json();

  if (d.success) {
    document.getElementById(`draft-${id}`).remove();
    showToast('✓ Email sent successfully', 'success');
    loadStats();
    loadHistory();
  } else {
    btn.textContent = '✓ Approve & Send';
    btn.classList.remove('btn-sending');
    btn.disabled = false;
    showToast('✕ ' + (d.error || 'Send failed'), 'error');
  }
}

async function skipDraft(id, btn) {
  btn.textContent = 'Skipping…';
  btn.disabled = true;

  const r = await fetch(`/api/drafts/${id}/skip`, { method: 'POST' });
  const d = await r.json();

  if (d.success) {
    document.getElementById(`draft-${id}`).remove();
    showToast('Draft skipped', 'success');
    loadStats();
  }
}

function formatTime(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleDateString('en-GB', { day:'2-digit', month:'short' }) +
    ' ' + d.toLocaleTimeString('en-GB', { hour:'2-digit', minute:'2-digit' });
}

function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'show ' + (type || '');
  setTimeout(() => t.className = '', 3000);
}

// Auto-refresh every 30 seconds
loadAll();
setInterval(loadAll, 30000);
</script>
</body>
</html>"""


# ─── API ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/api/stats')
def api_stats():
    stats = {"urgent": 0, "action": 0, "fyi": 0, "archive": 0, "total": 0, "pending_drafts": 0}

    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT category, COUNT(*) FROM message_history WHERE direction='received' GROUP BY category")
        for row in c.fetchall():
            cat = (row[0] or '').upper()
            if cat in stats:
                stats[cat.lower()] = row[1]
        c.execute("SELECT COUNT(*) FROM message_history")
        stats["total"] = c.fetchone()[0]
        conn.close()

    if os.path.exists(DRAFTS_PATH):
        with open(DRAFTS_PATH, encoding='utf-8') as f:
            drafts = json.load(f)
        stats["pending_drafts"] = len(drafts)

    return jsonify(stats)


@app.route('/api/drafts')
def api_drafts():
    if not os.path.exists(DRAFTS_PATH):
        return jsonify([])
    with open(DRAFTS_PATH, encoding='utf-8') as f:
        return jsonify(json.load(f))


@app.route('/api/drafts/<int:draft_id>/approve', methods=['POST'])
def approve_draft(draft_id):
    if not os.path.exists(DRAFTS_PATH):
        return jsonify({"success": False, "error": "No drafts file"})

    with open(DRAFTS_PATH, encoding='utf-8') as f:
        drafts = json.load(f)

    draft = next((d for d in drafts if d['id'] == draft_id), None)
    if not draft:
        return jsonify({"success": False, "error": "Draft not found"})

    # Parse recipient email
    sender = draft['sender']
    if '<' in sender and '>' in sender:
        to_address = sender.split('<')[1].split('>')[0]
    else:
        to_address = sender

    subject = "RE: " + draft['subject']
    body = draft['draft']

    # Send via SMTP
    try:
        EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
        EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_address, msg.as_string())

        # Log to DB
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO message_history (contact_email, direction, subject, body, category, channel) VALUES (?,?,?,?,?,?)",
                (to_address, "sent", subject, body, draft['category'], "email")
            )
            conn.commit()
            conn.close()

        # Remove from drafts
        drafts = [d for d in drafts if d['id'] != draft_id]
        with open(DRAFTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(drafts, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/drafts/<int:draft_id>/skip', methods=['POST'])
def skip_draft(draft_id):
    if not os.path.exists(DRAFTS_PATH):
        return jsonify({"success": False})

    with open(DRAFTS_PATH, encoding='utf-8') as f:
        drafts = json.load(f)

    drafts = [d for d in drafts if d['id'] != draft_id]

    with open(DRAFTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(drafts, f, ensure_ascii=False, indent=2)

    return jsonify({"success": True})


@app.route('/api/run', methods=['POST'])
def api_run():
    """Run agent.py --dry-run in background and return results."""
    import subprocess, sys
    agent_path = os.path.join(os.path.dirname(__file__), "agent.py")

    if not os.path.exists(agent_path):
        return jsonify({"success": False, "error": "agent.py not found in same folder"})

    try:
        # Count drafts before
        drafts_before = 0
        if os.path.exists(DRAFTS_PATH):
            with open(DRAFTS_PATH, encoding='utf-8') as f:
                drafts_before = len(json.load(f))

        result = subprocess.run(
            [sys.executable, agent_path, "--dry-run"],
            capture_output=True, text=True, timeout=120,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        # Count emails found from output — matches "Found X unseen email(s)."
        import re as _re
        emails_found = 0
        for line in result.stdout.splitlines():
            m = _re.search(r'found (\d+) unseen', line.lower())
            if m:
                emails_found = int(m.group(1))
                break
            if "no new" in line.lower() or "no emails" in line.lower():
                emails_found = 0
                break

        # Count new drafts created
        drafts_after = 0
        if os.path.exists(DRAFTS_PATH):
            with open(DRAFTS_PATH, encoding='utf-8') as f:
                drafts_after = len(json.load(f))

        drafts_created = max(0, drafts_after - drafts_before)

        if result.returncode != 0 and "no emails" not in result.stdout.lower():
            return jsonify({
                "success": False,
                "error": result.stderr[:300] if result.stderr else "Agent exited with error"
            })

        return jsonify({
            "success": True,
            "emails_found": emails_found,
            "drafts_created": drafts_created,
            "output": result.stdout[-500:] if result.stdout else ""
        })

    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Agent timed out after 120 seconds"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/history')
def api_history():
    if not os.path.exists(DB_PATH):
        return jsonify([])

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT contact_email, direction, subject, category, channel, sent_at
        FROM message_history
        ORDER BY sent_at DESC
        LIMIT 30
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)


if __name__ == '__main__':
    import threading

    # Start Telegram bot in background thread if telegram_channel.py exists
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telegram_channel.py")

    if os.path.exists(bot_path):
        import subprocess, sys
        def run_telegram():
            subprocess.run(
                [sys.executable, bot_path],
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
        t = threading.Thread(target=run_telegram, daemon=True)
        t.start()
        print("=" * 60)
        print("  CEM501 DASHBOARD + TELEGRAM BOT")
        print("  Dashboard : http://localhost:5050")
        print("  Telegram  : bot is running")
        print("  Ctrl+C to stop both")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  CEM501 DASHBOARD")
        print("  http://localhost:5050")
        print("  (telegram_channel.py not found — bot not started)")
        print("  Ctrl+C to stop")
        print("=" * 60)

    app.run(debug=False, port=5050)