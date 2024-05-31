import json
import tqdm

with open("words_med.json") as f:
    words = json.load(f)

WINNING_SETS = []
SEARCH_DEPTH = 5
SAVE_ON = 1  # starts at 1


def process(w1, w2) -> tuple[str, str, list[str]]:
    if len(w1.replace(" ", "")) > len(w2.replace(" ", "")):
        short_word = w2
        long_word = w1
    else:
        short_word = w1
        long_word = w2

    c1 = short_word.replace(" ", "").lower()
    c2 = long_word.replace(" ", "").lower()

    if not c2.startswith(c1):
        return "", "", []

    words_to_consider = []
    missing_letters = c2[len(c1) :]

    for word in words:
        if word == missing_letters:
            WINNING_SETS.append((short_word + " " + word, long_word))
            continue

        if word.startswith(missing_letters):
            words_to_consider.append(word)
            continue

        if missing_letters.startswith(word):
            words_to_consider.append(word)
            continue

    return short_word, long_word, words_to_consider


def process_recursive(w1, w2, level=5):
    if level > SEARCH_DEPTH - SAVE_ON:
        with open("winning_sets.json", "w") as f:
            json.dump(WINNING_SETS, f, indent=2)

    if level <= 0:
        return
    a1, b1, words_to_consider1 = process(w1, w2)
    if not words_to_consider1:
        return

    for w in words_to_consider1:
        process_recursive(a1 + " " + w, b1, level - 1)


for j in tqdm.tqdm(range(len(words))):
    w1 = words[j]
    for w2 in words[j:]:
        if not w2.startswith(w1):
            continue

        if w1 == w2:
            continue
        if w1 == w2 + "s" or w2 == w1 + "s":
            continue
        if w1 == w2 + "es" or w2 == w1 + "es":
            continue
        if w1 == w2 + "d" or w2 == w1 + "d":
            continue
        if w1 == w2 + "ed" or w2 == w1 + "ed":
            continue
        if w1 == w2 + "ing" or w2 == w1 + "ing":
            continue

        if len(w1) > len(w2):
            short_word = w2
            long_word = w1
        else:
            short_word = w1
            long_word = w2

        process_recursive(short_word, long_word, SEARCH_DEPTH)
