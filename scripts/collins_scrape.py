import requests
from bs4 import BeautifulSoup
import json
import uuid
import time
from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os

# Constants
BASE_URL = "https://www.collinsdictionary.com/dictionary/english-thesaurus/"
OUTPUT_FILE = "output/synonyms_graph.json"
QUEUE_FILE = "output/queue.json"

# Load existing JSON or create new storage
def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
METRICS_FILE = "output/metrics.json"

# Load or initialize metrics file
def load_metrics():
    try:
        with open(METRICS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"total_words_processed": 0, "total_synonyms": 0, "graph_file_size": 0, "queue_length": 0}

def save_metrics(metrics):
    with open(METRICS_FILE, 'w', encoding='utf-8') as file:
        json.dump(metrics, file, indent=4)

def update_metrics(data, queue):
    metrics = load_metrics()
    
    # Update metrics
    metrics["total_words_processed"] = len(set(lemma["term"] for lemma in data.values()))  # Unique words processed
    metrics["total_lemmas"] = len(data)  # Each lemma is uniquely stored by its ID
    metrics["total_synonyms"] = sum(len(lemma["synonyms"]) for lemma in data.values())  # Total synonyms stored
    metrics["graph_file_size"] = os.path.getsize(OUTPUT_FILE) if os.path.exists(OUTPUT_FILE) else 0  # File size in bytes
    metrics["queue_length"] = len(queue)  # Remaining words in queue
    
    save_metrics(metrics)

# Load the queue from file
def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as file:
            try:
                return deque(json.load(file))  # Convert list back to deque
            except json.JSONDecodeError:
                return deque()
    return deque()

# Save the queue to file
def save_queue(queue):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as file:
        json.dump(list(queue), file, indent=4, ensure_ascii=False)  # <--- ensure_ascii=False

# Set up Selenium (Headless Chrome)
def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in the background without UI
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection

    driver = webdriver.Chrome()
    return driver

# Fetch HTML content using Selenium
def fetch_html(word):
    url = BASE_URL + word
    driver = setup_selenium()
    
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JavaScript to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return soup
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    finally:
        driver.quit()

# Generate a unique ID for a word-definition pair
def generate_lemma_id(word, definition):
    return uuid.uuid5(uuid.NAMESPACE_DNS, word + definition).hex[:10]

# Parse HTML and extract lemmas
def parse_lemma(word, soup):
    lemma_list = []
    british_div = soup.select_one('div.blockThes-british')
    if not british_div:
        print(f"No British definitions found for {word}!")
        return []

    sense_divs = british_div.select('div.sense.opened.moreAnt.moreSyn')
    if not sense_divs:
        print(f"No .sense elements found for {word}!")  
        return []

    for sense in sense_divs:
        part_of_speech = sense.select_one("span.headerSensePos")
        part_of_speech = part_of_speech.text.strip() if part_of_speech else "unknown"
        part_of_speech = part_of_speech.replace("(","") # remove the parentheses
        part_of_speech = part_of_speech.replace(")","")

        definition = sense.select_one(".def")
        definition = definition.text.strip() if definition else "no definition available"

        id = generate_lemma_id(word, definition)

        synonym_elements = sense.select('div.blockSyn a span.orth')  # Only extract synonyms that link to a page
        synonyms = [syn.text.strip().replace(" ", "-") for syn in synonym_elements if syn and syn.text.strip()]
        lemma_obj = {
            "id": id,
            "term": word,
            "part_of_speech": part_of_speech,
            "definition": definition,
            "synonyms": synonyms  # Store raw words
        }
        lemma_list.append(lemma_obj)

    return lemma_list

# Main function to build the graph
def build_synonym_graph():
    data = load_json(OUTPUT_FILE)
    queue = load_queue()

    # If queue is empty, prompt for a starting word
    if not queue:
        start_word = input("Enter a starting word: ").strip().lower()
        queue.append(start_word)

    while queue:
        word = queue.popleft()

        # Skip if we've already processed this word (by checking lemma term)
        if any(entry["term"] == word for entry in data.values()):
            continue

        print(f"Processing: {word}")
        soup = fetch_html(word)
        if not soup:
            continue

        # Safely collect lemmas *first*
        lemma_list = parse_lemma(word, soup)
        if not lemma_list:
            continue  # Skip storing if parse failed

        for lemma in lemma_list:
            key = lemma["id"].lower()
            data[key] = lemma  # Store lemma only after full parse

            # Queue up new synonyms for processing
            for synonym in lemma["synonyms"]:
                if synonym not in queue and all(entry["term"] != synonym for entry in data.values()):
                    queue.append(synonym)

        # Save updated graph, queue, and metrics
        save_json(data, OUTPUT_FILE)
        save_queue(queue)
        update_metrics(data, queue)
        time.sleep(0.2)  # Be gentle with the server, darling 🥺

    print("Processing complete! Data saved.")

# Run the script
if __name__ == "__main__":
    build_synonym_graph()