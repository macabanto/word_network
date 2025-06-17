import json
import certifi
from pymongo import MongoClient

MongoClient("your_uri", tlsCAFile=certifi.where())
# Connect to MongoDB (local or change URI for Atlas)
client = MongoClient(
    "mongodb+srv://antmacapple:5JCBbfFDyQ2SsKk@synonymgraph.rijgeic.mongodb.net/?retryWrites=true&w=majority&appName=SynonymGraph",
    tlsCAFile=certifi.where()
)
# Select your database and collection
db = client["SynonymGraph"]
collection = db["synonyms"]

# Load and prepare the JSON data
with open("output/synonyms_graph.json", "r") as file:
    data = json.load(file)

# Insert each document individually
for key, entry in data.items():
    document = {
        "term": entry["term"],
        "part_of_speech": entry["part_of_speech"],
        "definition": entry["definition"],
        "synonyms": entry["synonyms"]
    }
    try:
        collection.insert_one(document)
    except Exception as e:
        print(f"Error inserting document {entry['term']}: {e}")

print("Done inserting documents.")