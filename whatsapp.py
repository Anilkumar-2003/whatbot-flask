# whatsapp.py
import os, requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

GRAPH_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def send_text(to_number, text):
    """
    to_number: E.164 without + (e.g. "919166082886")
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": text
        }
    }
    resp = requests.post(GRAPH_URL, headers=HEADERS, json=payload)
    # return status for logging
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text
