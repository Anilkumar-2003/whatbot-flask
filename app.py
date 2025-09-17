from flask import Flask, request
from db import users_col, questions_col, answers_col, sessions_col
from whatsapp import send_text
import os

app = Flask(__name__)

RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")  # your test number (e.g. 919247740141)

@app.route("/")
def home():
    return "✅ WhatsApp Quiz Bot is running!", 200


# Test endpoint: sends "Hi" when app runs
@app.route("/start-test", methods=["GET"])
def start_test():
    send_text(RECIPIENT_NUMBER, "Hi 👋 Welcome to the Quiz Bot! Please enter your full name:")
    return "Test message sent!", 200


# Webhook (Meta will POST messages here)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = message["from"]
        text = message["text"]["body"].strip().lower()

        # Example flow
        if text == "hi":
            send_text(phone, "Welcome! Please send your Full Name:")
        elif text == "yes":
            send_text(phone, "Great! Let's start the quiz 🎯")
        else:
            send_text(phone, f"You said: {text}")

    except Exception as e:
        print("Error:", e)

    return "ok", 200
