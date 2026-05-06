import argparse
import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from reader import fetch_recent_emails, print_summary
from drafter import draft_reply, print_draft
from sender import send_email
from memory import init_db, log_message
from digest import print_digest
from shared_state import save_drafts
from telegram import Bot

init_db()


async def send_telegram_alert(urgent_emails, draft_count):
    try:
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        message = f"🔴 {len(urgent_emails)} URGENT email(s) need attention:\n\n"
        for e in urgent_emails:
            message += f"• {e['subject'][:50]}\n"
        message += f"\n📋 {draft_count} draft(s) ready for approval.\n"
        message += "Use /list to see drafts, /approve_N to send, /skip_N to discard."
        await bot.send_message(chat_id=chat_id, text=message)
        print("Telegram alert sent.")
    except Exception as e:
        print(f"Telegram alert failed: {e}")


def run_agent(dry_run=False):
    print("\n" + "=" * 80)
    print("CEM501 COMMUNICATION AGENT")
    print("Hilal Esila Yağcıoğlu — Project Engineer")
    print("=" * 80)

    print("\n[1/3] Fetching emails...")
    emails = fetch_recent_emails()

    if not emails:
        print("No emails found.")
        return

    print_summary(emails)
    print_digest(emails)

    for email_data in emails:
        log_message(
            contact_email=email_data["sender"],
            direction="received",
            subject=email_data["subject"],
            body=email_data["preview"],
            category=email_data["category"],
            channel="email"
        )

    print("\n[2/3] Generating draft replies...")
    drafts = []

    for email_data in emails:
        if email_data["category"] in ["URGENT", "ACTION"]:
            draft = draft_reply(email_data)
            if draft:
                print_draft(email_data, draft)
                drafts.append({
                    "email": email_data,
                    "draft": draft
                })

    if not drafts:
        print("No URGENT or ACTION emails found. Nothing to draft.")
        return

    # Save drafts for Telegram approval
    save_drafts(drafts)

    # Send Telegram alert
    urgent_emails = [e for e in emails if e["category"] == "URGENT"]
    if urgent_emails:
        asyncio.run(send_telegram_alert(urgent_emails, len(drafts)))

    if dry_run:
        print("\n[3/3] DRY RUN MODE — Drafts saved for Telegram approval.")
        print(f"Saved {len(drafts)} draft(s). Use /list in Telegram bot to approve.")
        return

    print("\n[3/3] Review and send drafts...")
    sent = 0

    for item in drafts:
        email_data = item["email"]
        draft = item["draft"]

        sender = email_data["sender"]
        if "<" in sender and ">" in sender:
            to_address = sender.split("<")[1].split(">")[0]
        else:
            to_address = sender

        subject = "RE: " + email_data["subject"]
        result = send_email(to_address, subject, draft)

        if result:
            sent += 1
            log_message(
                contact_email=to_address,
                direction="sent",
                subject=subject,
                body=draft,
                category=email_data["category"],
                channel="email"
            )

    print(f"\nDone. {sent}/{len(drafts)} emails sent.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CEM501 Communication Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without sending emails"
    )
    args = parser.parse_args()
    run_agent(dry_run=args.dry_run)