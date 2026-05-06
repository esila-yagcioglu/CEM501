import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(override=True)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

sent_count = 0
sent_window_start = time.time()


def send_email(to, subject, body):
    global sent_count, sent_window_start

    current_time = time.time()
    if current_time - sent_window_start > 600:
        sent_count = 0
        sent_window_start = current_time

    if sent_count >= 10:
        print("Rate limit reached.")
        return False

    if not subject:
        print("WARNING: Subject is empty.")
        return False

    if not body or len(body) < 20:
        print("WARNING: Body too short.")
        return False

    if "[INSERT]" in body or "[TODO]" in body or "[PLACEHOLDER]" in body:
        print("WARNING: Placeholder text found.")
        return False

    print("\n" + "=" * 80)
    print("READY TO SEND — Please review:")
    print(f"To     : {to}")
    print(f"Subject: {subject}")
    print("-" * 80)
    print(body)
    print("=" * 80)

    confirm = input("\nSend this email? [y = yes / n = skip / e = edit]: ").strip().lower()

    if confirm == "y":
        try:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, to, msg.as_string())

            sent_count += 1

            with open("sent_log.txt", "a") as log:
                log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | TO: {to} | SUBJECT: {subject}\n")

            print("Email sent successfully!")
            return True

        except Exception as e:
            print(f"ERROR sending email: {e}")
            return False

    elif confirm == "e":
        print("Open the draft in your editor, edit it, and run again.")
        return False
    else:
        print("Email skipped.")
        return False


def send_email_silent(to, subject, body):
    """Send email without confirmation prompt - for Telegram bot use."""
    if not subject or not body or len(body) < 20:
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to, msg.as_string())

        with open("sent_log.txt", "a") as log:
            log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | TO: {to} | SUBJECT: {subject}\n")

        print(f"Email sent silently to {to}")
        return True

    except Exception as e:
        print(f"ERROR sending email: {e}")
        return False