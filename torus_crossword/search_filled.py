import torus
from lib import Direction
from fast_search import get_word_locations, get_new_grids, count_letters
import time
import json
import tqdm
import torus
from lib import Direction, get_words_in_partial_grid, grid_filled

from config import C_WALL

FAI_JSON = "temp_fails.json"

INITIAL_TEMPLATE = [
    "@@@█@@@@█@@@@@@",
    "@@@█@@@@█@@@@@@",
    "@@@█@@@@█@@@@@@",
    "@@@@█@@@@@@@███",
    "@@@@@@@█@@@█@@@",
    "███@@@@T@@@█@@@",
    "@@@@@█@O@@██@@@",
    "HNUT█@@R@@█DOUG",
    "@@@██@@U@█@@@@@",
    "@@@█@@@S@@@@███",
    "@@@█@@@█@@@@@@@",
    "███@@@@@@@█@@@@",
    "@@@@@@█@@@@█@@@",
    "@@@@@@█@@@@█@@@",
    "@@@@@@█@@@@█@@@",
]

id = int(time.time())
BES_JSON = f"fast_search/bests_{id}.json"
SOL_JSON = f"solutions/solutions_{id}.json"

T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"


solutions = []


f_save_words_used = False

from config import WOR_JSON, WORDS_APPROVED_JSON, ACTIVE_WORDS_JSON, WORDS_OMITTED_JSON

v_best_score = 0
v_best_grids = []
solutions = []


def recursive_search(grid, level=0):
    global v_best_score
    global v_best_grids
    global solutions

    tqdm.tqdm.write(
        T_BLUE + f"{json.dumps(grid, indent=2, ensure_ascii=False)}" + T_NORMAL
    )
    if f_save_words_used:
        words_contained = get_words_in_partial_grid(grid)
        words_contained
        trashed_words = words_contained - set(torus.json.load_json(WOR_JSON))
        if trashed_words:
            tqdm.tqdm.write("\n")
            tqdm.tqdm.write(
                T_PINK + f"FOUND TRASHED WORD ... Skipping: {trashed_words}" + T_NORMAL
            )
            tqdm.tqdm.write(T_PINK + "\n".join(grid) + T_NORMAL)
            return

        # get all words in words approved, and add them to active words
        words_approved = torus.json.load_json(WORDS_APPROVED_JSON)
        words_active = torus.json.load_json(ACTIVE_WORDS_JSON)
        words_omitted = torus.json.load_json(WORDS_OMITTED_JSON)

        for w in words_contained:
            if w in words_active or w in words_approved or w in words_omitted:
                continue
            tqdm.tqdm.write(T_YELLOW + f"Adding {w} to active words" + T_NORMAL)
            torus.json.append_json(ACTIVE_WORDS_JSON, w)

    if grid_filled(grid):
        tqdm.tqdm.write(T_YELLOW + "Solution found")  # Green text indicating success
        tqdm.tqdm.write(json.dumps(grid, indent=2, ensure_ascii=False))
        tqdm.tqdm.write(T_NORMAL)
        solutions.append(grid)
        torus.json.write_json(SOL_JSON, solutions)

        return

    new_grids = get_new_grids(grid)

    if not new_grids:
        return

    with tqdm.tqdm(new_grids, desc=f"Level {level}", leave=False) as t:
        l = count_letters(grid)
        if l > v_best_score:
            v_best_score = l
            v_best_grids.append({"level": level, "score": l, "grid": grid})
            torus.json.write_json(BES_JSON, v_best_grids)

        for new_grid in t:
            recursive_search(new_grid.copy(), level + 1)

        t.close()


if __name__ == "__main__":
    grid = INITIAL_TEMPLATE.copy()

    fails = torus.json.load_json(FAI_JSON)

    words = get_word_locations(grid, Direction.ACROSS) + get_word_locations(
        grid, Direction.DOWN
    )
    print(T_YELLOW, "number of answers", len(words), T_NORMAL)
    print(T_YELLOW, "number of black squares", "".join(grid).count(C_WALL), T_NORMAL)

    if grid in fails:
        print("Already failed")
        exit()

    recursive_search(grid, 0)

    if not len(solutions):
        print("No solution found")

        fails.append(INITIAL_TEMPLATE)
        torus.json.write_json(FAI_JSON, fails)
    else:
        print(T_GREEN, f"Found {len(solutions)} solutions", T_NORMAL)
