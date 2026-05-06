import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
pending_drafts = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to CEM501 Communication Agent!\n\n"
        "Commands:\n"
        "/list — see pending email drafts from agent\n"
        "/approve_N — approve and send draft N\n"
        "/skip_N — discard draft N\n\n"
        "Or send a field report and I will draft an email:\n"
        "'Pump failed at DW-03, water level rising fast'\n"
        "'Stop work - found unmarked gas line at Grid C-7'"
    )


async def list_drafts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from shared_state import load_drafts
    drafts = load_drafts()

    if not drafts:
        await update.message.reply_text("No pending drafts. Run agent.py first.")
        return

    message = f"📋 {len(drafts)} pending draft(s):\n\n"
    for d in drafts:
        message += f"[{d['id']}] [{d['category']}] {d['subject'][:50]}\n"
        message += f"To: {d['sender'][:30]}\n"
        message += f"Use /approve_{d['id']} or /skip_{d['id']}\n\n"

    await update.message.reply_text(message)


async def handle_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from shared_state import load_drafts, remove_draft
    from sender import send_email_silent as send_email

    text = update.message.text
    try:
        draft_id = int(text.split("_")[1])
    except:
        await update.message.reply_text("Usage: /approve_1, /approve_2, etc.")
        return

    drafts = load_drafts()
    draft = next((d for d in drafts if d["id"] == draft_id), None)

    if not draft:
        await update.message.reply_text(f"Draft {draft_id} not found.")
        return

    sender = draft["sender"]
    if "<" in sender and ">" in sender:
        to_address = sender.split("<")[1].split(">")[0]
    else:
        to_address = sender

    subject = "RE: " + draft["subject"]
    result = send_email(to_address, subject, draft["draft"])

    if result:
        remove_draft(draft_id)
        await update.message.reply_text(
            f"✅ Draft {draft_id} sent!\n"
            f"To: {to_address}\n"
            f"Category: {draft['category']}"
        )
    else:
        await update.message.reply_text(f"❌ Failed to send draft {draft_id}.")


async def handle_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from shared_state import remove_draft

    text = update.message.text
    try:
        draft_id = int(text.split("_")[1])
    except:
        await update.message.reply_text("Usage: /skip_1, /skip_2, etc.")
        return

    remove_draft(draft_id)
    await update.message.reply_text(f"Draft {draft_id} discarded.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    incoming_text = update.message.text
    sender = update.message.from_user.first_name
    chat_id = update.message.chat_id

    from drafter import draft_reply
    from reader import assign_triage_category

    await update.message.reply_text("Processing your field report...")

    category = assign_triage_category(incoming_text[:50], incoming_text)

    email_data = {
        "category": category,
        "sender": sender,
        "subject": incoming_text[:50],
        "preview": incoming_text
    }

    if category == "ARCHIVE":
        await update.message.reply_text(
            "This message doesn't seem urgent. No email draft needed.\n"
            "If this is important, please add more details."
        )
        return

    draft = draft_reply(email_data)

    if draft:
        pending_drafts[chat_id] = {
            "draft": draft,
            "category": category,
            "original": incoming_text
        }
        await update.message.reply_text(
            f"📋 [{category}] Draft email ready:\n\n"
            f"{draft}\n\n"
            f"Reply /send to send this email or /cancel to discard."
        )
    else:
        await update.message.reply_text("Could not generate draft. Please try again.")


async def send_draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id not in pending_drafts:
        await update.message.reply_text("No pending draft. Send a field report first.")
        return

    draft_data = pending_drafts[chat_id]

    from sender import send_email_silent as send_email

    to_address = os.getenv("PROJECT_MANAGER_EMAIL")
    subject = f"[{draft_data['category']}] Field Report: {draft_data['original'][:50]}"

    result = send_email(to_address, subject, draft_data['draft'])

    if result:
        await update.message.reply_text(
            f"✅ Email sent successfully!\n"
            f"To: {to_address}\n"
            f"Category: {draft_data['category']}"
        )
    else:
        await update.message.reply_text(
            "❌ Email could not be sent. Please check your connection."
        )

    del pending_drafts[chat_id]


async def cancel_draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id in pending_drafts:
        del pending_drafts[chat_id]
        await update.message.reply_text("Draft discarded.")
    else:
        await update.message.reply_text("No pending draft to cancel.")


def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env file.")
        return

    print("Starting CEM501 Telegram bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_drafts))
    app.add_handler(CommandHandler("send", send_draft))
    app.add_handler(CommandHandler("cancel", cancel_draft))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Regex(r'^/approve_\d+$'), handle_approve))
    app.add_handler(MessageHandler(filters.Regex(r'^/skip_\d+$'), handle_skip))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    run_bot()