import os
import requests
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

if not webhook_url:
    print("DISCORD_WEBHOOK_URL not found in .env")
    exit()

payload = {
    "content": "działa"
}

response = requests.post(webhook_url, json=payload)

print("Response: ", response.status_code)
if response.status_code in [200, 204]:
    print("udalo sie")
else:
    print("error ", response.text)