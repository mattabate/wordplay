import json

with open("word_list.json", "r") as f:
    words = json.load(f)


print(len(words))

words = list(set(words))
print(len(words))

with open("word_list.json", "w") as f:
    json.dump(words, f, indent=2, ensure_ascii=False)
