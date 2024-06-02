import json
import tqdm

with open("words_med.json") as f:
    WORD_LIST = json.load(f)

WINNING_SETS = []
SEARCH_DEPTH = 5
SAVE_ON = 1  # starts at 1


BRAKE_SET = {
    "a": [
        "the",
        "there",
        "these",
        "they",
        "this",
        "that",
        "it",
        "has",
        "was",
        "to",
        "but",
        "get",
    ],
    "ah": ["or"],
    "abandon": ["eye", "ear"],
    "abuse": ["area"],
    "age": ["a", "area", "art", "net", "tap"],
    "an": ["a", "i", "an", "the"],
    "be": ["terror", "era"],
    "bet": ["he"],
    "ban": ["do"],
    "bus": ["ear", "eat", "earth", "emotional", "era", "eye"],
    "era": ["way", "get"],
    "east": ["ear"],
    "easy": ["ear"],
    "fee": ["lab"],
    "gain": ["stare"],
    "go": ["odd"],
    "net": ["small"],
    "these": ["they", "this"],
    "you": ["thin"],
}

all_vals = []
for k, v in BRAKE_SET.items():
    all_vals.extend(v)
all_vals = list(set(all_vals))

BREAK_SET_BACK = {a: [] for a in all_vals}

for a in all_vals:
    for k, v in BRAKE_SET.items():
        if a in v:
            BREAK_SET_BACK[a].append(k)


def process(w1, w2) -> tuple[str, str, list[str]]:
    """Returns the short word, long word, and the words to consider."""
    if len(w1.replace(" ", "")) > len(w2.replace(" ", "")):
        short_sen = w2
        long_sen = w1
    else:
        short_sen = w1
        long_sen = w2

    c1 = short_sen.replace(" ", "").lower()
    c2 = long_sen.replace(" ", "").lower()

    if not c2.startswith(c1):
        return "", "", []

    words_to_consider = []
    missing_letters = c2[len(c1) :]

    for word in WORD_LIST:
        # if last thre letters are " an" only add words that start with a consonant
        if short_sen == "an" or short_sen[-3:] == " an":
            if word[0] not in "aeiou":
                continue
            if word in ["a", "i", "either"]:
                continue

        if short_sen == "a" or short_sen[-2:] == " a":
            if word[0] in "aeiou":
                continue

        if word in BREAK_SET_BACK.keys():
            failed = False
            for k in BREAK_SET_BACK[word]:
                if short_sen == k or short_sen[(-len(k) - 1) :] == " " + k:
                    failed = True
                    break

            if failed:
                continue

        if word == missing_letters:
            a = short_sen + " " + word
            b = long_sen
            indx_a = a.find(" ")
            indx_b = b.find(" ")

            ok = True
            for l in [a, b]:
                last_word = l.split()[-1]
                if last_word in ["a", "an", "the"]:
                    ok = False
                    break
            if not ok:
                continue

            # find locations of spaces
            a_space = a.find(" ")
            b_space = b.find(" ")

            # if none continue
            if a_space == -1 or b_space == -1:
                continue

            dist_last = abs(len(a) - len(b))
            if dist_last < 2:
                continue

            if indx_a < indx_b:
                WINNING_SETS.append((a, b))
            else:
                WINNING_SETS.append((b, a))
            continue

        if word.startswith(missing_letters):
            """If the word starts with the missing letters, then it is a possible word."""
            words_to_consider.append(word)
            continue

        if missing_letters.startswith(word):
            """If the missing letters start with the word, then it is a possible word."""
            words_to_consider.append(word)
            continue

    return short_sen, long_sen, words_to_consider


def process_recursive(w1, w2, level=5):
    """Recursively finds the words that can be added to the short sentence to fit into long sentence"""
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


if __name__ == "__main__":
    for j in tqdm.tqdm(range(len(WORD_LIST))):
        w1 = WORD_LIST[j]
        for w2 in WORD_LIST[j:]:
            if not w2.startswith(w1):
                continue
            if abs(len(w1) - len(w2)) < 2:
                continue

            short_word, long_word = (w1, w2) if len(w1) < len(w2) else (w2, w1)

            if w1 == w2:
                continue
            if long_word == short_word + "s":
                continue
            if long_word == short_word + "es":
                continue
            if long_word == short_word + "d":
                continue
            if long_word == short_word + "ed":
                continue
            if long_word == short_word + "ing":
                continue
            if long_word == short_word + "ment":
                continue

            process_recursive(short_word, long_word, SEARCH_DEPTH)
