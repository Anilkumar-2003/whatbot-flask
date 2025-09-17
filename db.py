import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

users_col = db["users"]
questions_col = db["questions"]
answers_col = db["answers"]
sessions_col = db["sessions"]
