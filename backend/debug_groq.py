import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/chat/completions"

print(f"Testing with key: {key[:10]}...")

payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "user", "content": "Hello, respond with a JSON object: {'greeting': 'hi'}"}
    ],
    "temperature": 0.5
}

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
