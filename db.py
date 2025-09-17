# db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "quizdb")

if not MONGODB_URI:
    raise RuntimeError("Set MONGODB_URI in environment")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# collections
users_col = db["users"]
questions_col = db["questions"]
answers_col = db["answers"]
sessions_col = db["sessions"]
