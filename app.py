import os, json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from db import users_col, questions_col, answers_col, sessions_col
from whatsapp import send_text

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_verify_token")
RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")

# 🔹 Send "Hi" message automatically when server starts
@app.before_first_request
def send_initial_hi():
    send_text(RECIPIENT_NUMBER, "Hi 👋 Welcome to the WhatsApp Quiz App!")

# ---- Helper functions ----
def get_session(phone):
    return sessions_col.find_one({"phone": phone})

def create_or_update_session(phone, state, temp_data=None, current_q_index=0, user_id=None):
    sessions_col.update_one(
        {"phone": phone},
        {"$set": {
            "state": state,
            "temp_data": temp_data or {},
            "current_q_index": current_q_index,
            "user_id": user_id
        }},
        upsert=True
    )

def clear_session(phone):
    sessions_col.delete_one({"phone": phone})

def find_user_by_phone(phone):
    return users_col.find_one({"phone": phone})

def upsert_user_by_phone(phone, data):
    users_col.update_one(
        {"phone": phone},
        {"$set": {
            "name": data.get("name"),
            "email": data.get("email"),
            "class": data.get("class"),
            "school": data.get("school"),
            "role": data.get("role"),
            "phone": phone
        }},
        upsert=True
    )
    return users_col.find_one({"phone": phone})

def total_questions():
    return questions_col.count_documents({})

def get_question_by_index(idx):
    q = questions_col.find().skip(idx).limit(1)
    l = list(q)
    return l[0] if l else None

def record_answer(user_id, question_id, selected_option):
    q = questions_col.find_one({"_id": question_id})
    correct = (selected_option.upper() == q["correct_option"].upper())
    answers_col.insert_one({
        "user_id": user_id,
        "question_id": question_id,
        "selected_option": selected_option.upper(),
        "is_correct": correct
    })
    correct_count = answers_col.count_documents({"user_id": user_id, "is_correct": True})
    users_col.update_one({"_id": user_id}, {"$set": {"score": correct_count}})
    return correct

def teacher_summary_text():
    tq = total_questions()
    pipeline = [
        {"$match": {"role": "student"}},
        {"$lookup": {
            "from": "answers",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "answers"
        }},
        {"$project": {"name": 1, "score": 1, "answers_count": {"$size": "$answers"}}},
        {"$match": {"answers_count": {"$gte": tq}}},
        {"$sort": {"score": -1}}
    ]
    rows = list(users_col.aggregate(pipeline))
    if not rows:
        return "No student has completed the quiz yet."
    lines = [f"Total completed: {len(rows)}"]
    for r in rows:
        lines.append(f"{r.get('name','-')} — Score: {r.get('score',0)}")
    return "\n".join(lines)

def format_question(q, idx):
    return f"Q{idx}: {q['question']}\nA) {q['option_a']}\nB) {q['option_b']}\nC) {q['option_c']}\nD) {q['option_d']}\n\nReply with A/B/C/D"

# ---- Webhook verification ----
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# ---- Webhook receiver ----
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("incoming:", json.dumps(data))
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages")
        if not messages:
            return jsonify({}), 200
        msg = messages[0]
        phone = msg.get("from")
        text = msg.get("text", {}).get("body", "").strip()
        if not text:
            send_text(phone, "Sorry, only text is supported.")
            return jsonify({}), 200

        text_l = text.lower()
        session = get_session(phone)

        # start registration
        if text_l in ["hi","hello","hey"]:
            create_or_update_session(phone, "awaiting_name", temp_data={})
            send_text(phone, "Welcome! Please send your Full Name:")
            return jsonify({}), 200

        if not session:
            send_text(phone, "Please send 'Hi' to start registration.")
            return jsonify({}), 200

        state = session.get("state")

        if state == "awaiting_name":
            temp = session["temp_data"]; temp["name"] = text
            create_or_update_session(phone, "awaiting_email", temp_data=temp)
            send_text(phone, "Enter your email:")
            return jsonify({}), 200

        if state == "awaiting_email":
            temp = session["temp_data"]; temp["email"] = text
            create_or_update_session(phone, "awaiting_class", temp_data=temp)
            send_text(phone, "Enter your class (e.g., 10th):")
            return jsonify({}), 200

        if state == "awaiting_class":
            temp = session["temp_data"]; temp["class"] = text
            create_or_update_session(phone, "awaiting_school", temp_data=temp)
            send_text(phone, "Enter your school name:")
            return jsonify({}), 200

        if state == "awaiting_school":
            temp = session["temp_data"]; temp["school"] = text
            create_or_update_session(phone, "awaiting_role", temp_data=temp)
            send_text(phone, "Are you a 'student' or 'teacher'?")
            return jsonify({}), 200

        if state == "awaiting_role":
            if text_l not in ["student","teacher"]:
                send_text(phone, "Please type 'student' or 'teacher'.")
                return jsonify({}), 200
            temp = session["temp_data"]; temp["role"] = text_l
            user_doc = upsert_user_by_phone(phone, temp)
            create_or_update_session(phone, "awaiting_start_confirmation", temp_data=temp, user_id=user_doc["_id"])
            send_text(phone, "Saved. Type YES to start quiz (student) or view results (teacher).")
            return jsonify({}), 200

        if state == "awaiting_start_confirmation":
            if text_l in ["yes","y"]:
                temp = session["temp_data"]; role = temp["role"]
                user = find_user_by_phone(phone); user_id = user["_id"]
                if role == "teacher":
                    send_text(phone, teacher_summary_text())
                    clear_session(phone)
                else:
                    answers_col.delete_many({"user_id": user_id})
                    users_col.update_one({"_id": user_id}, {"$set": {"score": 0}})
                    create_or_update_session(phone, "in_quiz", temp_data=temp, current_q_index=0, user_id=user_id)
                    q = get_question_by_index(0)
                    if not q:
                        send_text(phone, "No questions found.")
                        clear_session(phone)
                    else:
                        send_text(phone, format_question(q, 1))
            elif text_l in ["no","n"]:
                send_text(phone, "Cancelled. Send 'Hi' to restart.")
                clear_session(phone)
            else:
                send_text(phone, "Reply YES or NO.")
            return jsonify({}), 200

        if state == "in_quiz":
            if text_l.upper() not in ["A","B","C","D"]:
                send_text(phone, "Reply with A, B, C or D.")
                return jsonify({}), 200
            user = find_user_by_phone(phone); user_id = user["_id"]
            q_index = session.get("current_q_index", 0)
            q = get_question_by_index(q_index)
            is_correct = record_answer(user_id, q["_id"], text_l.upper())
            send_text(phone, "Correct ✅" if is_correct else f"Wrong ❌, correct: {q['correct_option']}")
            send_text(phone, f"Explanation: {q['explanation']}")
            next_idx = q_index + 1; total = total_questions()
            if next_idx >= total:
                score = users_col.find_one({"_id": user_id}).get("score", 0)
                send_text(phone, f"Quiz complete! Your score: {score}/{total}")
                clear_session(phone)
            else:
                create_or_update_session(phone, "in_quiz", temp_data=session["temp_data"], current_q_index=next_idx, user_id=user_id)
                send_text(phone, format_question(get_question_by_index(next_idx), next_idx+1))
            return jsonify({}), 200

        send_text(phone, "Unknown state. Send 'Hi' to restart.")
        return jsonify({}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Quiz App is running", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
