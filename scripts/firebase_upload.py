import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Dynamically determine base directory (one level up from 'scripts/')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Dynamically determine base directory (two levels up from 'scripts/')
KEYS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Paths to important files
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

SERVICE_ACCOUNT_FILE = os.path.join(KEYS_DIR, "keys", "wordnet-d2044-firebase-adminsdk-fbsvc-fa897dbf32.json")  # Assuming you have a 'firebase' folder
JSON_FILE = os.path.join(OUTPUT_DIR, "synonyms_sorted.json")

# Initialize Firebase with service account credentials
def initialize_firebase(cred_file=SERVICE_ACCOUNT_FILE):
    try:
        cred = credentials.Certificate(cred_file)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully!")
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise

# Sanitize strings for Firestore document IDs and fields
def sanitize_string(text):
    return text.replace("/", "|")  # Replace slashes with pipes for safety

# Upload JSON data to Firestore
def upload_json_to_firestore(json_file=JSON_FILE, collection_name="wordnet", db=None):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

        for word, synonyms in data.items():
            safe_word = sanitize_string(word)
            sanitized_synonyms = [sanitize_string(syn) for syn in synonyms]

            # Upload to Firestore
            doc_ref = db.collection(collection_name).document(safe_word)
            doc_ref.set({"synonyms": sanitized_synonyms})

            print(f"Uploaded '{word}' as '{safe_word}' with sanitized synonyms: {sanitized_synonyms}")

        print("Upload complete!")

    except FileNotFoundError:
        print(f"JSON file '{json_file}' not found.")
    except Exception as e:
        print(f"Error uploading data: {e}")

# Main execution
if __name__ == "__main__":
    db = initialize_firebase()
    upload_json_to_firestore(db=db)