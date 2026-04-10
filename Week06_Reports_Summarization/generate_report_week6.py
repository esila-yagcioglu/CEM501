from pathlib import Path
from google import genai
import os
import time

FIELD_NOTES_DIR = Path("field_notes")
OUTPUT_FILE = Path("llm_draft_report.md")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def call_llm(prompt):
    for i in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Try {i+1} failed: {e}")
            if i < 4:
                time.sleep(5)
            else:
                return "ERROR"

def summarize_file(file_path):
    content = file_path.read_text(encoding="utf-8", errors="ignore")

    prompt = f"""
Summarize this construction field note professionally.
Do not invent anything.

Note:
{content}
"""

    return call_llm(prompt)

def main():
    summaries = []

    for file_path in sorted(FIELD_NOTES_DIR.glob("*.txt")):
        print(f"Processing {file_path.name}...")
        summary = summarize_file(file_path)
        summaries.append(f"{file_path.name}:\n{summary}")

    combined = "\n\n".join(summaries)

    final_prompt = f"""
You are a construction project engineer.

Using the summaries below, write a PROFESSIONAL DAILY REPORT.

Structure:
1. Daily Overview
2. Work Completed
3. Labor / Subcontractors
4. Equipment / Deliveries
5. Safety Issues
6. Traffic / Access
7. Municipality
8. Delays / Risks
9. Next Steps

Summaries:
{combined}
"""

    final_report = call_llm(final_prompt)

    OUTPUT_FILE.write_text(final_report, encoding="utf-8")

    print("✅ Draft report created!")

if __name__ == "__main__":
    main()