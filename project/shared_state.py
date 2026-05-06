import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "pending_drafts.json")


def save_drafts(drafts):
    """Save pending drafts to file."""
    data = []
    for i, item in enumerate(drafts):
        data.append({
            "id": i + 1,
            "sender": item["email"]["sender"],
            "subject": item["email"]["subject"],
            "category": item["email"]["category"],
            "draft": item["draft"]
        })
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} draft(s) to pending_drafts.json")


def load_drafts():
    """Load pending drafts from file."""
    if not os.path.exists(STATE_FILE):
        return []
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def remove_draft(draft_id):
    """Remove a draft after it's been sent or skipped."""
    drafts = load_drafts()
    drafts = [d for d in drafts if d["id"] != draft_id]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(drafts, f, ensure_ascii=False, indent=2)


def clear_drafts():
    """Clear all pending drafts."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)