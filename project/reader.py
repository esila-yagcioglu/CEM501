import imaplib
import email

EMAIL = "esila.cem501@gmail.com"
PASSWORD = "xeekltslxybyxmkb"

def connect_and_list_subjects():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()

        print("Connected successfully!")
        print(f"Total emails: {len(mail_ids)}")

        for mail_id in mail_ids[-5:]:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    print("Subject:", msg["subject"])

        mail.logout()

    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    connect_and_list_subjects()
    