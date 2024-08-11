import json
from lib import Direction
from fast_search import get_word_locations, ROWLEN
from main import load_json, T_PINK, T_NORMAL, T_YELLOW
import tqdm

SOLS_PATH = "solutions/15x15_grid_solutions_DA_42_flipped.json"
WORDALLOWED = "word_list.json"

with open(WORDALLOWED) as f:
    WORDLIST = json.load(f)


def score_words(grid: list[str]):
    words = get_word_locations(
        grid=grid, direction=Direction.ACROSS
    ) + get_word_locations(grid=grid, direction=Direction.DOWN)
    # if contains duplicates, remove them
    if len(words) != len(set(words)):
        sols = load_json(SOLS_PATH)
        sols.remove(grid)
        with open(SOLS_PATH, "w") as f:
            json.dump(sols, f, indent=2, ensure_ascii=False)
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


with open(SOLS_PATH) as f:
    solutions = json.load(f)

print("number solutions ever:", len(solutions))
allowed_grids = []
for s in tqdm.tqdm(solutions):
    words = score_words(s)
    for w in words:
        if w not in WORDLIST:
            break
    else:
        allowed_grids.append(s)

print("number solutions allowed:", len(allowed_grids))
# print first 10
for i in range(10):
    print(json.dumps(allowed_grids[i], indent=2, ensure_ascii=False))
