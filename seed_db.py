# seed_db.py
from db import questions_col
from pymongo import InsertOne

sample_questions = [
    {"question":"What is the capital of France?",
     "option_a":"Berlin","option_b":"Madrid","option_c":"Paris","option_d":"Rome",
     "correct_option":"C","explanation":"Paris is the capital of France."},
    {"question":"Which planet is known as the Red Planet?",
     "option_a":"Earth","option_b":"Mars","option_c":"Jupiter","option_d":"Saturn",
     "correct_option":"B","explanation":"Mars has a reddish appearance."},
    {"question":"Who wrote 'Hamlet'?",
     "option_a":"Charles Dickens","option_b":"William Shakespeare","option_c":"Mark Twain","option_d":"Leo Tolstoy",
     "correct_option":"B","explanation":"William Shakespeare wrote Hamlet."},
    {"question":"What is the largest mammal?",
     "option_a":"Elephant","option_b":"Blue Whale","option_c":"Giraffe","option_d":"Hippopotamus",
     "correct_option":"B","explanation":"Blue Whale is the largest mammal."},
    {"question":"How many continents are there?",
     "option_a":"5","option_b":"6","option_c":"7","option_d":"8",
     "correct_option":"C","explanation":"There are 7 continents."},
    {"question":"What is the boiling point of water at sea level?",
     "option_a":"90°C","option_b":"100°C","option_c":"120°C","option_d":"80°C",
     "correct_option":"B","explanation":"Water boils at 100°C at sea level."},
    {"question":"Which gas do plants absorb?",
     "option_a":"Oxygen","option_b":"Carbon Dioxide","option_c":"Nitrogen","option_d":"Hydrogen",
     "correct_option":"B","explanation":"Plants absorb carbon dioxide during photosynthesis."},
    {"question":"Who painted the Mona Lisa?",
     "option_a":"Vincent van Gogh","option_b":"Pablo Picasso","option_c":"Leonardo da Vinci","option_d":"Michelangelo",
     "correct_option":"C","explanation":"Leonardo da Vinci painted the Mona Lisa."},
    {"question":"What is the currency of Japan?",
     "option_a":"Dollar","option_b":"Yuan","option_c":"Yen","option_d":"Won",
     "correct_option":"C","explanation":"Japanese currency is the Yen."},
    {"question":"Which is the smallest prime number?",
     "option_a":"0","option_b":"1","option_c":"2","option_d":"3",
     "correct_option":"C","explanation":"2 is the smallest prime number."}
]

def seed():
    # clean existing (optional)
    # questions_col.delete_many({})
    ops = [InsertOne(q) for q in sample_questions]
    result = questions_col.bulk_write(ops)
    print("Inserted:", result.inserted_count if hasattr(result, 'inserted_count') else "done")

if __name__ == "__main__":
    seed()
