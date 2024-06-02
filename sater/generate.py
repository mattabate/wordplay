import json
import tqdm
import enum
import time

DICTIONARY: list[str] = []
ALL_WINS = []


def possibilities(template: str):
    """return all words that fit "?q??t"""
    constraints = []
    for i, letter in enumerate(template):
        if letter != "?":
            constraints.append((i, letter))

    valid_words = []
    for word in DICTIONARY:
        for i, letter in constraints:
            if word[i] != letter:
                break
        else:
            valid_words.append(word)

    return valid_words


def transpose(strings):
    return ["".join(row) for row in zip(*strings)]


def get_new_templates(template):
    # get all possible words in every direction
    # for every row, get all possible words
    min_len_row = 10000000
    best_row_set = []
    best_row_index = None
    for i, row in enumerate(template):
        if "?" not in row:
            continue

        p = possibilities(row)
        if len(p) < min_len_row:
            min_len_row = len(p)
            best_row_set = p
            best_row_index = i

    min_len_col = 10000000
    best_col_set = []
    best_col_index = None
    for i, _ in enumerate(template):
        col = "".join(row[i] for row in template)
        if "?" not in col:
            continue

        p = possibilities(col)
        if len(p) < min_len_col:
            min_len_col = len(p)
            best_col_set = p
            best_col_index = i

    templates = []
    if min_len_row <= min_len_col:
        for word in best_row_set:
            new_template = template.copy()
            new_template[best_row_index] = word
            templates.append(new_template)

    else:
        for word in best_col_set:
            new_template = template.copy()
            for i in range(len(template)):
                new_template[i] = (
                    new_template[i][:best_col_index]
                    + word[i]
                    + new_template[i][best_col_index + 1 :]
                )
            templates.append(new_template)

    return templates


def get_words_in_template(template):
    out = []
    for row in template:
        if "?" not in row:
            out.append(row)

    for i, _ in enumerate(template):
        col = "".join(row[i] for row in template)
        if "?" not in col:
            out.append(col)
    return out


def get_inital_templates(words: list[str], place: int = -1):
    "Given a word, return all possible templates for the word."
    templates = []

    l = len(words[0])
    init_template = ["?" * l for _ in range(l)]

    for word in words:
        template = init_template.copy()
        template[place - 1] = word
        if template not in templates:
            templates.append(template)

    return templates


def check_win(template):
    if all(["?" not in t for t in template]):
        ALL_WINS.append(template)
        with open("wins.json", "w") as f:
            json.dump(ALL_WINS, f, indent=4)


def process_template(template, level, f_verbose=True):
    """return all words that fit "?q??t"""

    template_set = get_new_templates(template)

    if f_verbose and level in [1, 2]:
        template_set = tqdm.tqdm(template_set)

    for template in template_set:
        if f_verbose and level == 1:
            print("\n\n")
            for s in template:
                print(s)

        gw = get_words_in_template(template)
        if not all([s in DICTIONARY for s in gw]):
            return False

        if len((set(gw))) != len(gw):
            return False

        check_win(template)
        process_template(template, level=level + 1, f_verbose=f_verbose)

    return True


class Wordlist(enum.Enum):
    EOWL = "eowl"
    CROSSWORDS = "crosswords"
    ALL = "all"


if __name__ == "__main__":
    print("starting")
    print("\n\n")
    f_wordlist = Wordlist.ALL
    f_test = True
    f_verbose = True
    k_place = 2
    k_word_length = 4

    all_words = []
    match f_wordlist:
        case Wordlist.EOWL:
            with open("eowl/eowl_words.json", "r") as f:
                all_words_lower = json.load(f)
                all_words = [w.upper() for w in all_words_lower]
        case Wordlist.CROSSWORDS:
            with open("crosswords/crossword_words.json", "r") as f:
                all_words_json = json.load(f)
                all_words = [w[0] for w in all_words_json]
        case Wordlist.ALL:
            with open("eowl/eowl_words.json", "r") as f:
                all_words_lower = json.load(f)
                all_words = [w.upper() for w in all_words_lower]
            with open("crosswords/crossword_words.json", "r") as f:
                all_words_json = json.load(f)
                all_words += [w[0] for w in all_words_json]

    DICTIONARY = [w for w in all_words if len(w) == k_word_length]
    DICTIONARY = list(set(DICTIONARY))

    print(f"number of words in dictionary: {len(all_words)}")
    print(f"dataset: {f_wordlist}")
    print(f"number {k_word_length}-letter words: {len(DICTIONARY)}")
    print()

    if f_test:
        if k_word_length == 4:
            TEST_WORD = "CATS"
        elif k_word_length == 5:
            TEST_WORD = "ABATE"
        elif k_word_length == 6:
            TEST_WORD = "CARROT"
        elif k_word_length == 15:
            TEST_WORD = "STARSANDSTRIPES"

        templates = get_inital_templates([TEST_WORD], place=k_place)
    else:
        templates = get_inital_templates(DICTIONARY, place=k_place)

    t0 = time.time()
    for template in tqdm.tqdm(templates):
        print("\033[33m")
        process_template(template, 1, f_verbose=f_verbose)
        print("\033[32m")
    t1 = time.time()
    print(f"Time: {t1-t0}")
