import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import os

sys.setrecursionlimit(2000)

# URL Template
BASE_URL = "https://www.thesaurus.com/browse/"

# Get the absolute path to the project root (one level up from "scripts")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Construct paths to input and output files relative to project root
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
INPUT_FILE = os.path.join(OUTPUT_DIR, "synonyms.json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "synonyms.json")  # Using same file for updates

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load existing data or initialize new storage
def load_synonyms(filename=INPUT_FILE):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save data to JSON file
def save_synonyms(data, filename=OUTPUT_FILE):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Fetch synonyms from thesaurus.com
def fetch_synonyms(word):
    try:
        response = requests.get(BASE_URL + word)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract synonyms by multiple class identifiers
        synonym_elements = soup.select('.Bf5RRqL5MiAp4gB8wAZa, .CPTwwN0qNO__USQgCKp8')
        synonyms = {elem.text.strip() for elem in synonym_elements}
        return synonyms
    except Exception as e:
        print(f"Error fetching synonyms for '{word}': {e}")
        return set()

# Recursive function to build the synonym network
def build_synonym_network(word, data):
    # Check if word exists AND if it has synonyms (non-empty list)
    if word in data and data[word]:
        print(f"'{word}' already processed with synonyms, skipping...")
        return
    
    print(f"Processing '{word}'...")
    synonyms = fetch_synonyms(word)

    if synonyms:
        data[word] = list(synonyms)  # Convert set to list for JSON compatibility
        print(f"Found {len(synonyms)} synonyms for '{word}'")
    else:
        data[word] = []  # Store an empty list to avoid reprocessing later
        print(f"No synonyms found for '{word}', storing as empty.")

    # Process each synonym recursively
    for synonym in synonyms:
        if synonym not in data or not data[synonym]:  # Only process if new or empty
            build_synonym_network(synonym, data)
    
    # Save after processing each word
    save_synonyms(data)

# Main function
if __name__ == "__main__":
    # Load existing synonym data
    synonym_data = load_synonyms()

    # Starting word
    starting_word = input("Enter a starting word: ").strip().lower()
    build_synonym_network(starting_word, synonym_data)

    print(f"Synonym network built and saved to {OUTPUT_FILE}!")