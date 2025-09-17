from models import get_questions, save_answer, update_score

user_sessions = {}  # temporary quiz state per user

def start_quiz(user_id):
    questions = get_questions()
    user_sessions[user_id] = {"questions": questions, "current": 0, "score": 0}
    return questions[0]

def next_question(user_id, selected):
    session = user_sessions.get(user_id)
    if not session:
        return None, "Session not found."

    current_q = session["questions"][session["current"]]
    correct = (selected.upper() == current_q["correct_option"].upper())
    save_answer(user_id, current_q["id"], selected, correct)
    if correct:
        session["score"] += 1

    session["current"] += 1
    if session["current"] < len(session["questions"]):
        return session["questions"][session["current"]], None
    else:
        update_score(user_id)
        return None, f"Quiz completed! Your score: {session['score']}/{len(session['questions'])}"
