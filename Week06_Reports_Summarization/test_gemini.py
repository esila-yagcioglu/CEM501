from google import genai
import os
import time

api_key = os.getenv("GEMINI_API_KEY")
print("API key exists:", bool(api_key))
print("API key starts with:", api_key[:8] if api_key else "NONE")

client = genai.Client(api_key=api_key)

for i in range(5):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Explain how AI works in one sentence."
        )
        print("SUCCESS:")
        print(response.text)
        break
    except Exception as e:
        print(f"Try {i+1} failed:", e)
        if i < 4:
            time.sleep(10)
        else:
            raise