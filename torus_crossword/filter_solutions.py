from lib import Direction
from fast_search import get_word_locations, ROWLEN
import tqdm
from config import (
    WOR_JSON,
    IC_TYPE,
    MAX_WAL,
    SEARCH_W_FLIPPED,
    SCORED_WORDS_JSON,
    WORDS_IN_SOLUTIONS_JSON,
    WORDS_APPROVED_JSON,
    get_solutions_json,
    get_bad_solutions_json,
)
from torus.json import load_json, write_json

WORDLIST = load_json(WOR_JSON)
SOLS_PATH = get_solutions_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)
BAD_SOLUTIONS = get_bad_solutions_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)


def score_words(grid: list[str]) -> list[str]:
    words = get_word_locations(
        grid=grid, direction=Direction.ACROSS
    ) + get_word_locations(grid=grid, direction=Direction.DOWN)
    # if contains duplicates, remove them
    if len(words) != len(set(words)):
        sols = load_json(SOLS_PATH)
        sols.remove(grid)
        write_json(SOLS_PATH, sols)
        return

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
    solutions = load_json(SOLS_PATH)
    passed = load_json(BAD_SOLUTIONS)
    scored_words = load_json(SCORED_WORDS_JSON)
    scored_dict = {word_score[0]: word_score[1] for word_score in scored_words}

    print("number solutions ever:", len(solutions) + len(passed))
    print("number solutions considered:", len(solutions))
    allowed_grids = []
    scored_words_seen = {}
    for s in tqdm.tqdm(solutions):
        words = score_words(s)
        for w in words:
            if w not in WORDLIST:
                passed.append(s)
                break
        else:
            allowed_grids.append(s)
            for w in words:
                if w not in scored_words_seen:
                    scored_words_seen[w] = scored_dict[w]

    print("number solutions allowed:", len(allowed_grids))
    write_json(BAD_SOLUTIONS, passed)
    write_json(SOLS_PATH, allowed_grids)

    print("number of scored words in valid solutiosn:", len(scored_words_seen))

    # sort by value and save as list
    sorted_data = sorted(
        scored_words_seen.keys(), key=lambda x: scored_words_seen[x], reverse=True
    )

    words_approved = load_json(WORDS_APPROVED_JSON)
    sorted_data = [x for x in sorted_data if x not in words_approved]
    write_json(WORDS_IN_SOLUTIONS_JSON, sorted_data)

    print("number of words that still havent been checked:", len(sorted_data))
    print(
        f"JSON file {WORDS_IN_SOLUTIONS_JSON}' has been created with the data sorted by values."
    )
