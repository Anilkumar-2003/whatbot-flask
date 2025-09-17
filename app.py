from flask import Flask, request, jsonify
import requests
import config
from quiz_logic import start_quiz, next_question
from models import add_user

app = Flask(__name__)

GRAPH_URL = f"https://graph.facebook.com/v20.0/{config.PHONE_NUMBER_ID}/messages"

def send_message(to, text):
    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(GRAPH_URL, headers=headers, json=data)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == config.VERIFY_TOKEN:
            return challenge
        return "Invalid verify token", 403

    data = request.get_json()
    if "messages" in data.get("entry", [])[0].get("changes", [])[0].get("value", {}):
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"].strip().lower()

        if text == "hi":
            send_message(from_number, "Welcome! Please enter your details: Name, Email, Class, School, Role(student/teacher)")
        elif "," in text:
            try:
                name, email, clas, school, role = [x.strip() for x in text.split(",")]
                add_user(name, email, clas, school, role)
                send_message(from_number, "Details saved. Do you want to start the quiz? (yes/no)")
            except:
                send_message(from_number, "Invalid format. Please enter details again: Name, Email, Class, School, Role")
        elif text == "yes":
            q = start_quiz(1)  # For demo using user_id=1 (later map real user)
            send_message(from_number, f"Q1: {q['question']}\nA. {q['option_a']}\nB. {q['option_b']}\nC. {q['option_c']}\nD. {q['option_d']}")
        elif text in ["a", "b", "c", "d"]:
            q, done = next_question(1, text)
            if q:
                send_message(from_number, f"{q['question']}\nA. {q['option_a']}\nB. {q['option_b']}\nC. {q['option_c']}\nD. {q['option_d']}")
            else:
                send_message(from_number, done)
        else:
            send_message(from_number, "Say 'hi' to start.")
    return "ok", 200

@app.route("/")
def home():
    return "Quiz App Running!"
