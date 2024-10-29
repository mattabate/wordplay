import json

with open("word_list.json") as f:
    words = json.load(f)


def every_other_letter_same(word):
    if set(word[::2]) == {word[0]}:
        return word[0], word
    elif set(word[1::2]) == {word[1]}:
        return word[1], word
    return "", ""


holder = {}
for word in words:
    a, b = every_other_letter_same(word)
    if a:
        if not holder.get(a):
            holder[a] = []
        holder[a].append(b)

for k, v in holder.items():
    large = [c for c in v if len(c) > 6]
    if len(large) > 0:
        print(json.dumps(large, indent=4))
