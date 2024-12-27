import json

with open("words_approved.json", "r") as file:
    word_list = json.load(file)

for word in word_list:
    if len(word) == 11:
        print(word)
