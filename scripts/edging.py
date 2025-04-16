import json

GRAPH_FILE = "output/synonyms_graph.json"
LINKED_GRAPH_FILE = "output/synonyms_graph_linked.json"

def load_graph(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_graph(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def build_index(data):
    term_index = {}
    for lemma_id, lemma in data.items():
        term = lemma["term"].lower()
        if term not in term_index:
            term_index[term] = []
        term_index[term].append(lemma_id)
    return term_index

def link_synonyms(data, index):
    for lemma in data.values():
        linked_synonyms = []
        lemma_pos = lemma["part_of_speech"].lower()
        original_term = lemma["term"].lower()

        for synonym in lemma["synonyms"]:
            synonym_term = synonym.lower()
            if synonym_term in index:
                matching_lemmas = index[synonym_term]

                # Only one lemma? Easy pick
                if len(matching_lemmas) == 1:
                    linked_synonyms.append(matching_lemmas[0])
                    continue

                # Filter by part of speech
                pos_matched = [
                    lemma_id for lemma_id in matching_lemmas
                    if data[lemma_id]["part_of_speech"].lower() == lemma_pos
                ]

                # If POS narrows it to one, perfect
                if len(pos_matched) == 1:
                    linked_synonyms.append(pos_matched[0])
                    continue

                # Try reciprocal synonym check
                reciprocal_match = None
                for lemma_id in pos_matched:
                    candidate = data[lemma_id]
                    candidate_synonyms = [s.lower() for s in candidate["synonyms"]]
                    if original_term in candidate_synonyms:
                        reciprocal_match = lemma_id
                        break  # Found our match!

                if reciprocal_match:
                    linked_synonyms.append(reciprocal_match)
                elif pos_matched:
                    # Still ambiguous, no reciprocal match, just pick one for now
                    linked_synonyms.append(pos_matched[0])
                else:
                    # No part-of-speech match
                    linked_synonyms.append(synonym)
            else:
                linked_synonyms.append(synonym)

        lemma["synonyms"] = linked_synonyms

def main():
    data = load_graph(GRAPH_FILE)
    index = build_index(data)
    link_synonyms(data, index)
    save_graph(data, LINKED_GRAPH_FILE)
    print("✨ Synonyms linked and saved!")

if __name__ == "__main__":
    main()