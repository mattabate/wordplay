import json
from lib import Direction
from fast_search import get_word_locations, ROWLEN
from main import load_json
import tqdm

TYPE = "AD"
NUM = 42
SOLS_PATH = f"solutions/15x15_grid_solutions_{TYPE}_{NUM}.json"
PASS_PATH = f"bad_solutions/15x15_grid_solutions_{TYPE}_{NUM}_bad.json"
WDLS_PATH = "word_list.json"

with open(WDLS_PATH) as f:
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

with open(PASS_PATH) as f:
    passed = json.load(f)

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

with open(PASS_PATH, "w") as f:
    json.dump(passed, f, indent=2, ensure_ascii=False)
with open(SOLS_PATH, "w") as f:
    json.dump(allowed_grids, f, indent=2, ensure_ascii=False)
# print first 10
# for i in range(10):
#     print(json.dumps(allowed_grids[i], indent=2, ensure_ascii=False))
