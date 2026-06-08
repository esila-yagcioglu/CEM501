import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)


def generate_digest(email_summaries):
    """Generate a morning digest from email summaries."""

    urgent = [e for e in email_summaries if e["category"] == "URGENT"]
    action = [e for e in email_summaries if e["category"] == "ACTION"]
    fyi = [e for e in email_summaries if e["category"] == "FYI"]
    archive = [e for e in email_summaries if e["category"] == "ARCHIVE"]

    now = datetime.now().strftime("%B %d, %Y — %H:%M")

    lines = []
    lines.append("=" * 60)
    lines.append(f"  MORNING DIGEST — {now}")
    lines.append(f"  CEM501 Communication Agent")
    lines.append("=" * 60)

    if urgent:
        lines.append(f"\n🔴 URGENT ({len(urgent)}):")
        for e in urgent:
            lines.append(f"  • {e['subject'][:55]}")
            lines.append(f"    From: {e['sender'].split('<')[0].strip()}")

    if action:
        lines.append(f"\n🟡 ACTION REQUIRED ({len(action)}):")
        for e in action:
            lines.append(f"  • {e['subject'][:55]}")
            lines.append(f"    From: {e['sender'].split('<')[0].strip()}")

    if fyi:
        lines.append(f"\n🔵 FYI ({len(fyi)}):")
        for e in fyi:
            lines.append(f"  • {e['subject'][:55]}")

    if archive:
        lines.append(f"\n⚪ ARCHIVE ({len(archive)} emails skipped)")

    lines.append("\n" + "=" * 60)
    lines.append("  Reminder: AI drafts are suggestions — always verify before sending.")
    lines.append("=" * 60)

    return "\n".join(lines)


def save_digest(digest_text):
    """Save digest to logs folder."""
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    filename = os.path.join(logs_dir, f"digest_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(digest_text)
    print(f"Digest saved to {filename}")
    return filename


def print_digest(email_summaries):
    """Generate, print and save the digest."""
    digest = generate_digest(email_summaries)
    print(digest)
    save_digest(digest)
    return digest


if __name__ == "__main__":
    from reader import fetch_recent_emails
    emails = fetch_recent_emails()
    print_digest(emails)