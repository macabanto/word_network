import json

def alphabetize_json_case_insensitive(input_file="synonyms.json", output_file="synonyms_sorted.json"):
    try:
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
        print(f"{total_words} total words processed")
    except Exception as e:
        print(f"Error: {e}")

# Run the function
if __name__ == "__main__":
    alphabetize_json_case_insensitive()