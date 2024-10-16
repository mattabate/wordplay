import tqdm
import torus

from lib import Direction, T_YELLOW, T_NORMAL
from fast_search import get_word_locations, ROWLEN

from config import (
    WOR_JSON,
    IC_TYPE,
    MAX_WAL,
    SEARCH_W_FLIPPED,
    SCORES_DICT_JSON,
    WORDS_IN_SOLUTIONS_JSON,
    WORDS_APPROVED_JSON,
    get_solutions_json,
    get_bad_solutions_json,
)


f_reomve_duplicates = True
f_reomve_duplicates_bad = False

WORDLIST = torus.json.load_json(WOR_JSON)
SOLS_PATH = get_solutions_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)
BAD_SOLUTIONS = get_bad_solutions_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)


def get_words_in_filled_grid(grid: list[str]) -> list[str]:
    """returns a list of words in a filled grid"""
    words = get_word_locations(
        grid=grid, direction=Direction.ACROSS
    ) + get_word_locations(grid=grid, direction=Direction.DOWN)

    word_strings = []
    for w in words:
        string_word = ""
        for i in range(w.length):
            if w.direction == Direction.ACROSS:
                string_word += grid[w.start[0]][(w.start[1] + i) % ROWLEN]
            else:
                string_word += grid[(w.start[0] + i) % ROWLEN][w.start[1]]

        word_strings.append(string_word)

    return word_strings


if __name__ == "__main__":
    print(f"Filtering solutions: {T_YELLOW}{SOLS_PATH}{T_NORMAL}")

    ############################
    # Step 1: Remove duplicates
    ############################
    print(T_YELLOW, "Reducing Solutions to Unique", T_NORMAL)
    if f_reomve_duplicates:
        print("Number of solutions in json:", len(torus.json.load_json(SOLS_PATH)))
        torus.json.remove_duplicates(SOLS_PATH)
        solutions = torus.json.load_json(SOLS_PATH)
        print("Number of unique solutions:", len(solutions))
    else:
        solutions = torus.json.load_json(SOLS_PATH)

    if f_reomve_duplicates_bad:
        print(
            "Number of bad solutions in json:",
            len(torus.json.load_json(BAD_SOLUTIONS)),
        )
        torus.json.remove_duplicates(BAD_SOLUTIONS)
        passed = torus.json.load_json(BAD_SOLUTIONS)
        print("Number of unique bad solutions:", len(passed))
    else:
        passed = torus.json.load_json(BAD_SOLUTIONS)

    ############################
    # Step 2: ????
    ############################
    scored_words = torus.json.load_json(SCORES_DICT_JSON)

    print("number solutions ever:", len(solutions) + len(passed))
    print("number solutions considered:", len(solutions))
    allowed_grids = []
    scored_words_seen = {}
    bad_words_seens = set()
    for s in tqdm.tqdm(solutions):
        words = get_words_in_filled_grid(s)
        if len(words) != len(set(words)):
            passed.append(s)
            continue

        for w in words:
            if w not in WORDLIST:
                passed.append(s)
                bad_words_seens.add(w)
                break
        else:
            allowed_grids.append(s)
            for w in words:
                if w not in scored_words_seen:
                    scored_words_seen[w] = scored_words[w]

    print("number solutions allowed:", len(allowed_grids))
    torus.json.write_json(BAD_SOLUTIONS, passed)
    torus.json.write_json(SOLS_PATH, allowed_grids)

    print("number of scored words in valid solutiosn:", len(scored_words_seen))
    print("bad words seen:", list(bad_words_seens))

    # sort by value and save as list
    sorted_data = sorted(
        scored_words_seen.keys(), key=lambda x: scored_words_seen[x], reverse=True
    )

    words_approved = torus.json.load_json(WORDS_APPROVED_JSON)
    xx = []
    for s in sorted_data:
        if s not in words_approved:
            xx.append(s)
    sorted_data = xx

    torus.json.write_json(WORDS_IN_SOLUTIONS_JSON, sorted_data)

    print("number of words that still havent been checked:", len(sorted_data))
    print(
        f"JSON file {WORDS_IN_SOLUTIONS_JSON}' has been created with the data sorted by values."
    )
