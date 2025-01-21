import requests
from bs4 import BeautifulSoup
import json
import time
import sys

sys.setrecursionlimit(1500)

# URL Template
BASE_URL = "https://www.thesaurus.com/browse/"

# Load existing data or initialize new storage
def load_synonyms(filename="synonyms.json"):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save data to JSON file
def save_synonyms(data, filename="synonyms.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Fetch synonyms from thesaurus.com
def fetch_synonyms(word):
    try:
        response = requests.get(BASE_URL + word)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract synonyms by class identifier
        synonym_elements = soup.find_all(class_="Bf5RRqL5MiAp4gB8wAZa")
        synonyms = {elem.text.strip() for elem in synonym_elements}
        return synonyms
    except Exception as e:
        print(f"Error fetching synonyms for '{word}': {e}")
        return set()

# Recursive function to build the synonym network
def build_synonym_network(word, data):
    if word in data:
        print(f"'{word}' already processed.")
        return
    
    print(f"Processing '{word}'...")
    synonyms = fetch_synonyms(word)
    data[word] = list(synonyms)  # Convert set to list for JSON compatibility

    # Process each synonym recursively
    for synonym in synonyms:
        if synonym not in data:  # Avoid reprocessing
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

    print("Synonym network built and saved to synonyms.json!")