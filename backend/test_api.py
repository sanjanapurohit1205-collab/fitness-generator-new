import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"API Key found: {bool(api_key)}")
if api_key:
    print(f"Key snippet: {api_key[:5]}...{api_key[-5:]}")
else:
    print("ERROR: No API Key found in environment variables.")
    exit(1)

print("\nTesting OpenRouter API...")
try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "FitForge Test"
        },
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "user", "content": "Say hello in one word."}
            ],
            "max_tokens": 10
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed with exception: {e}")