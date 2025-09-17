import os
from pymongo import MongoClient

# Get MongoDB URI from Render environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "quizdb")  # fallback to quizdb if not set

client = MongoClient(MONGO_URI)
db = client[DB_NAME]  # explicitly select database

# Collections
users_col = db["users"]
questions_col = db["questions"]
answers_col = db["answers"]
sessions_col = db["sessions"]
