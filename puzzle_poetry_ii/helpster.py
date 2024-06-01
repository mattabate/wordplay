import json

with open("winning_sets.json") as f:
    WINNING_SETS = json.load(f)

unique_words = set()
for a, b in WINNING_SETS:
    for word in a.split():
        unique_words.add(word)
    for word in b.split():
        unique_words.add(word)

with open("words_med_reduced.json", "w") as f:
    json.dump(list(unique_words), f, indent=2)
