import imaplib
import email
import os
import re
from email.header import decode_header
from dotenv import load_dotenv


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_FETCH_COUNT = 20


def decode_mime_words(text):
    if not text:
        return ""
    decoded_parts = decode_header(text)
    result = []

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or "utf-8", errors="ignore"))
        else:
            result.append(part)

    return "".join(result)


def strip_html(html_text):
    if not html_text:
        return ""

    html_text = re.sub(r"<script.*?>.*?</script>", "", html_text, flags=re.DOTALL | re.IGNORECASE)
    html_text = re.sub(r"<style.*?>.*?</style>", "", html_text, flags=re.DOTALL | re.IGNORECASE)
    html_text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.IGNORECASE)
    html_text = re.sub(r"</p>", "\n", html_text, flags=re.IGNORECASE)
    html_text = re.sub(r"<[^>]+>", "", html_text)
    html_text = re.sub(r"&nbsp;", " ", html_text)
    html_text = re.sub(r"&amp;", "&", html_text)
    html_text = re.sub(r"\s+", " ", html_text).strip()

    return html_text


def get_body_preview(message, max_length=200):
    body_text = ""

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition.lower():
                continue

            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue

                charset = part.get_content_charset() or "utf-8"
                decoded_text = payload.decode(charset, errors="ignore")

                if content_type == "text/plain":
                    body_text = decoded_text
                    break
                elif content_type == "text/html" and not body_text:
                    body_text = strip_html(decoded_text)
            except Exception:
                continue
    else:
        try:
            payload = message.get_payload(decode=True)
            if payload:
                charset = message.get_content_charset() or "utf-8"
                decoded_text = payload.decode(charset, errors="ignore")

                if message.get_content_type() == "text/html":
                    body_text = strip_html(decoded_text)
                else:
                    body_text = decoded_text
        except Exception:
            body_text = ""

    body_text = re.sub(r"\s+", " ", body_text).strip()
    return body_text[:max_length]


def assign_triage_category(subject, preview):
    text = f"{subject} {preview}".lower()

    urgent_keywords = [
    "urgent", "asap", "immediately", "critical", "delay", "blocked",
    "overdue", "deadline today", "issue", "problem", "risk", "accident",
    "non-compliance", "stop work", "shutdown", "failed", "failure",
    "pump", "water rising", "flood", "collapse", "injury", "fire",
    "gas leak", "crack", "broke", "broken", "emergency", "danger",
    "falling", "leak", "explosion", "stuck", "trapped"
]

    action_keywords = [
    "action required",
    "please review",
    "please approve",
    "approval",
    "confirm",
    "submit",
    "send",
    "respond",
    "reply",
    "update required",
    "need your input",
    "sign off",
    "review",
    "approve",
    "rfi",
    "request for information",
    "decision required",
    "clarification",
    "discrepancy"
]

    fyi_keywords = [
        "fyi", "for your information", "update", "attached", "meeting notes",
        "minutes", "schedule", "progress report", "weekly report", "status update",
        "notice", "information"
    ]

    archive_keywords = [
        "newsletter", "promotion", "marketing", "receipt", "invoice copy",
        "automated", "no-reply", "reminder only", "subscription"
    ]

    for keyword in urgent_keywords:
        if keyword in text:
            return "URGENT"

    for keyword in action_keywords:
        if keyword in text:
            return "ACTION"

    for keyword in fyi_keywords:
        if keyword in text:
            return "FYI"

    for keyword in archive_keywords:
        if keyword in text:
            return "ARCHIVE"

    return "ARCHIVE"


def triage_priority(category):
    order = {
        "URGENT": 0,
        "ACTION": 1,
        "FYI": 2,
        "ARCHIVE": 3
    }
    return order.get(category, 4)


def fetch_recent_emails():
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in the .env file.")

    mail = None
    email_summaries = []

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("Connected successfully.")

        mail.select("CEM501")

        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("Could not fetch emails.")
        
            return []

        email_ids = messages[0].split()
        recent_ids = email_ids[-EMAIL_FETCH_COUNT:]

        for email_id in reversed(recent_ids):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if not isinstance(response_part, tuple):
                    continue

                msg = email.message_from_bytes(response_part[1])

                sender = decode_mime_words(msg.get("From", ""))
                subject = decode_mime_words(msg.get("Subject", ""))
                date = decode_mime_words(msg.get("Date", ""))
                preview = get_body_preview(msg, max_length=200)
                category = assign_triage_category(subject, preview)

                email_summaries.append({
                    "category": category,
                    "sender": sender,
                    "subject": subject,
                    "date": date,
                    "preview": preview
                })

        return sorted(email_summaries, key=lambda x: triage_priority(x["category"]))

    finally:
        if mail is not None:
            try:
                mail.close()
            except Exception:
                pass
            try:
                mail.logout()
            except Exception:
                pass


def print_summary(email_summaries):
    print("\n" + "=" * 80)
    print("EMAIL TRIAGE SUMMARY")
    print("=" * 80)

    for index, item in enumerate(email_summaries, start=1):
        print(f"\n{index}. [{item['category']}]")
        print(f"From   : {item['sender']}")
        print(f"Subject: {item['subject']}")
        print(f"Date   : {item['date']}")
        print(f"Preview: {item['preview']}")
        print("-" * 80)


if __name__ == "__main__":
    summaries = fetch_recent_emails()
    print_summary(summaries)

    