import os
import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

def draft_reply(email_data):
    category = email_data.get("category", "ARCHIVE")
    sender = email_data.get("sender", "")
    subject = email_data.get("subject", "")
    preview = email_data.get("preview", "")

    if category == "ARCHIVE":
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are Hilal Esila Yağcıoğlu, a Project Engineer on a construction project.
Write a professional email reply for the following incoming email.

Category: {category}
From: {sender}
Subject: {subject}
Message preview: {preview}

Rules:
- Be formal and professional
- Keep it concise (max 150 words)
- If URGENT: acknowledge urgency, promise response within 2 hours
- If ACTION: confirm receipt, promise response within 24 hours
- If FYI: thank them briefly, confirm you noted the information
- End with: Best regards, Hilal Esila Yağcıoğlu, Project Engineer
- Do NOT include Subject line in the body
"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Anthropic API error: {e}")
        return None


def print_draft(email_data, draft):
    print("\n" + "=" * 80)
    print(f"DRAFT REPLY — [{email_data['category']}]")
    print(f"Original From   : {email_data['sender']}")
    print(f"Original Subject: {email_data['subject']}")
    print("-" * 80)
    print(draft)
    print("=" * 80)