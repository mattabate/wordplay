from lib import Direction
from fast_search import get_word_locations, ROWLEN
import tqdm
from config import (
    WOR_JSON,
    IC_TYPE,
    MAX_WAL,
    C_WALL,
    get_solutions_json,
    get_bad_solutions_json,
)
from torus.json import load_json, write_json

WORDLIST = load_json(WOR_JSON)
SOLS_PATH = get_solutions_json(IC_TYPE, MAX_WAL)
PASS_PATH = get_bad_solutions_json(IC_TYPE, MAX_WAL)


def score_words(grid: list[str]):
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
    passed = load_json(PASS_PATH)

    print("number solutions ever:", len(solutions) + len(passed))
    print("number solutions considered:", len(solutions))
    allowed_grids = []

    for s in tqdm.tqdm(solutions):
        words = score_words(s)
        for w in words:
            if w not in WORDLIST:
                passed.append(s)
                break
        else:
            allowed_grids.append(s)

    print("number solutions allowed:", len(allowed_grids))

    write_json(PASS_PATH, passed)
    write_json(SOLS_PATH, allowed_grids)
