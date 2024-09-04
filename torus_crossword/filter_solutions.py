import json
from lib import Direction
from fast_search import get_word_locations, ROWLEN
import tqdm
from config import WOR_JSON
from torus.json import load_json, write_json

TYPE = "AD"
NUM = 42
SOLS_PATH = f"solutions/15x15_grid_solutions_{TYPE}_{NUM}.json"
PASS_PATH = f"bad_solutions/15x15_grid_solutions_{TYPE}_{NUM}_bad.json"

WORDLIST = load_json(WOR_JSON)


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
