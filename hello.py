import json
from nltk.corpus import wordnet as wn

# Function to fetch synonyms
def get_synonyms(word):
    synonyms = set()  # Use a set to avoid duplicates
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            if lemma.name().lower() != word.lower():  # Avoid the word itself
                synonyms.add(lemma.name().replace('_', ' '))
    return list(synonyms)

# Function to load words from a file
def load_words_from_file(filename):
    with open(filename, 'r') as file:
        words = [line.strip() for line in file if line.strip()]  # Remove empty lines
    return words

# Function to generate synonyms
def generate_synonyms(word_list):
    synonym_dict = {}
    for word in word_list:
        synonym_dict[word] = get_synonyms(word)[:7]  # Limit to 7 synonyms
    return synonym_dict

# Main logic
if __name__ == "__main__":
    # Load words from your file
    input_file = 'google-10000-english.txt'  # Replace with your file's path
    words = load_words_from_file(input_file)
    
    # Generate synonyms
    synonyms = generate_synonyms(words)

    # Save to a JSON file
    with open('synonyms.json', 'w') as file:
        json.dump(synonyms, file, indent=4)

    print(f"Synonyms for {len(words)} words saved to synonyms.json!")