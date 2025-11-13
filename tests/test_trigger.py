import requests
import json

# Mock payload for testing n8n
payload = {
    "user_id": 1,  # Dummy user_id
    "tier": "premium",
    "profiles": [
        {
            "url": "https://www.instagram.com/parisfoodguide_/",
            "days_since": 14,
            "type": "instagram",
            "max_results": 50
        },
        {
            "url": "https://www.instagram.com/ellevousguide/",
            "days_since": 14,
            "type": "instagram",
            "max_results": 50
        },
        {
            "url": "https://www.instagram.com/_lavieparisienne__/",
            "days_since": 14,
            "type": "instagram",
            "max_results": 50
        }
    ]
}

# Send to n8n test webhook
n8n_url = "http://localhost:5678/webhook-test/scrape"
try:
    response = requests.post(n8n_url, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")