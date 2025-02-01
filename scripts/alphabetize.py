import json
import os

# Get the absolute path to the project root (one level up from "scripts")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Construct paths to input and output files relative to project root
INPUT_FILE = os.path.join(BASE_DIR, "output", "synonyms.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "output", "synonyms_sorted.json")

def alphabetize_json_case_insensitive(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Load the existing JSON data
        with open(input_file, 'r') as file:
            data = json.load(file)
        
        # Count the total number of words (keys) in the dictionary
        total_words = len(data)

        # Sort dictionary keys ignoring case, preserving original casing
        sorted_data = {key: sorted(data[key], key=str.lower) for key in sorted(data, key=str.lower)}

        # Save the sorted dictionary back to a new file
        with open(output_file, 'w') as file:
            json.dump(sorted_data, file, indent=4)

        print(f"Case-insensitive alphabetized synonyms saved to '{output_file}' successfully!")
        print(f"Total number of words processed: {total_words}")

    except Exception as e:
        print(f"Error: {e}")

# Run the function
if __name__ == "__main__":
    alphabetize_json_case_insensitive()