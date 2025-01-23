import json
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials
def initialize_firebase(cred_file):
    cred = credentials.Certificate(cred_file)
    firebase_admin.initialize_app(cred)
    return firestore.client()

# Function to sanitize strings for Firestore document names and fields
def sanitize_string(text):
    return text.replace("/", "|")  # Replace slashes with underscores

# Upload JSON data to Firestore
def upload_json_to_firestore(json_file, collection_name, db):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

        for word, synonyms in data.items():
            # Sanitize word for document ID
            safe_word = sanitize_string(word)

            # Sanitize synonyms (replace slashes in each word)
            sanitized_synonyms = [sanitize_string(syn) for syn in synonyms]

            # Upload to Firestore
            doc_ref = db.collection(collection_name).document(safe_word)
            doc_ref.set({"synonyms": sanitized_synonyms})

            print(f"Uploaded '{word}' as '{safe_word}' with sanitized synonyms: {sanitized_synonyms}")

        print("Upload complete!")

    except Exception as e:
        print(f"Error uploading data: {e}")

# Main execution
if __name__ == "__main__":
    service_account_file = "private-key-here"  # Your Firebase private key file
    json_file = "synonyms_sorted.json"  # Your synonyms JSON file
    collection_name = "wordnet"  # Firestore collection name

    db = initialize_firebase(service_account_file)
    upload_json_to_firestore(json_file, collection_name, db)