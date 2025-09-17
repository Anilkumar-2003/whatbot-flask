from db import get_db_connection

def add_user(name, email, clas, school, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, class, school, role) VALUES (%s, %s, %s, %s, %s)",
        (name, email, clas, school, role)
    )
    conn.commit()
    conn.close()

def get_questions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    conn.close()
    return questions

def save_answer(user_id, question_id, selected, is_correct):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO answers (user_id, question_id, selected_option, is_correct) VALUES (%s, %s, %s, %s)",
        (user_id, question_id, selected, is_correct)
    )
    conn.commit()
    conn.close()

def update_score(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM answers WHERE user_id=%s AND is_correct=1", (user_id,))
    score = cursor.fetchone()[0]
    cursor.execute("UPDATE users SET score=%s WHERE id=%s", (score, user_id))
    conn.commit()
    conn.close()
