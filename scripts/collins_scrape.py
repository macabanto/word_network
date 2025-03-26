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

# Constants
BASE_URL = "https://www.collinsdictionary.com/dictionary/english-thesaurus/"
OUTPUT_FILE = "output/synonyms_graph.json"

# Load existing JSON or create new storage
def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Set up Selenium (Headless Chrome)
def setup_selenium():
    chrome_options = Options()
    # try without chrome_options.add_argument("--headless")  # Run in the background without UI
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection

    # Provide path to your chromedriver
    service = Service("~/Applications/chromedriver-mac-arm64")  # Replace with actual ChromeDriver path
    driver = webdriver.Chrome()
    
    return driver

# Fetch HTML content using Selenium
def fetch_html(word):
    url = BASE_URL + word
    driver = setup_selenium()
    
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JavaScript to load

        # Print the first 500 characters of the page source for debugging
        page_source = driver.page_source
        #print(page_source[:500])  # Check if content is loading

        soup = BeautifulSoup(page_source, "html.parser")
        
        return soup

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    finally:
        driver.quit()

# Generate a unique ID for a word-definition pair
def generate_lemma_id(word, definition):
    return uuid.uuid5(uuid.NAMESPACE_DNS, word + definition).hex[:10]

# Lemma generation
# given the soup object, we want to extract every single lemma found on the page for a given word
# Parse HTML and extract LEMMAs
# given word, soup object
# output list of lemmas found on page following the lemma schema
def parse_lemma(word, soup):
    lemma_list = []
    # Isolate the british lemmas
    british_div = soup.select_one('div.blockThes-british') # div pertaining to british definitions ( avoid extracting american def / duplication )
    # Find all "sense" divs
    sense_divs = british_div.select('div.sense.opened.moreAnt.moreSyn')
    if not sense_divs:  
        print(f"No .sense elements found for {word}!")  
        print(soup.prettify()[:20])  
        return []
    # testing - why more senses than thought: discovered - both british and american definitions were being parsed; print(len(sense_divs))
    for sense in sense_divs:
        # Extract part of speech
        part_of_speech = sense.select_one("span.headerSensePos")
        part_of_speech = part_of_speech.text.strip() if part_of_speech else "Unknown"

        # Extract definition
        definition = sense.select_one(".def")
        definition = definition.text.strip() if definition else "No definition available"

        id = generate_lemma_id(word, definition)

        synonym_block = sense.select_one('div.blockSyn')
        synonym_elements = synonym_block.select('span.orth')
        synonyms = [syn.text.strip() for syn in synonym_elements if syn and syn.text.strip()]

        # Create lemma object
        lemma_obj = {
            "id": id,
            "term": word,
            "part_of_speech": part_of_speech,
            "definition": definition,
            "synonyms": synonyms  # Store raw words
        }
        lemma_list.append(lemma_obj)
        #way too much, print(lemma_obj)
        #i think its returning before going through the whole lemma list, not sure why
    return lemma_list

# Main function to build the graph
def build_synonym_graph(start_word):
    data = load_json(OUTPUT_FILE)
    queue = deque([start_word])  # BFS approach
    
    while queue:
        print(queue)
        word = queue.popleft()
        
        if any(lemma.startswith(word) for lemma in data.keys()):  # Skip if processed
            continue
        
        print(f"Processing: {word}")
        soup = fetch_html(word)
        if not soup:
            continue
        
        lemma_list = parse_lemma(word, soup)
        
        for lemma in lemma_list:
            key = f"{lemma['id']}".lower()  # Unique key per lemma
            data[key] = lemma  # Store as a flat entry
        
            for synonym in lemma["synonyms"]:
                if synonym not in queue and synonym not in data:
                    queue.append(synonym)  # Add to queue for processing
        
        save_json(data, OUTPUT_FILE)
        time.sleep(0.2)  # Avoid request overload
    
    print("Processing complete! Data saved.")

# Run the script
if __name__ == "__main__":
    start_word = input("Enter a starting word: ").strip().lower()
    build_synonym_graph(start_word)