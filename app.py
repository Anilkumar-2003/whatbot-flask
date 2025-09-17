import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Environment variables (set them in Render Dashboard)
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")  # from Meta Dashboard
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")  # from Meta Dashboard
RECIPIENT_NUMBER = os.environ.get("RECIPIENT_NUMBER")  # e.g., +9198xxxxxxx

@app.route('/')
def home():
    return "🚀 Flask WhatsApp API is running on Render!", 200

# Webhook verification endpoint
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Meta requires a VERIFY_TOKEN you choose yourself
    verify_token = os.environ.get("VERIFY_TOKEN", "my_verify_token")  
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == verify_token:
        return challenge, 200
    else:
        return "Verification failed", 403

# Webhook receiver endpoint
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    print("📩 Incoming webhook:", data)
    return "EVENT_RECEIVED", 200

# Send a test WhatsApp message
@app.route('/send-message', methods=['POST'])
def send_message():
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_NUMBER,
        "type": "text",
        "text": {"body": "Hello from Flask + Render deployment 🚀"}
    }
    response = requests.post(url, headers=headers, json=body)
    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    # Render requires binding to 0.0.0.0 and PORT from environment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
