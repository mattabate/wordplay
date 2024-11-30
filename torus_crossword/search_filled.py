import migrations.schema
import torus
from lib import Direction
from fast_search import get_word_locations, get_new_grids
import time
import json
import tqdm
import torus

from lib import (
    Direction,
    get_words_in_partial_grid,
    grid_filled,
    add_theme_words,
    T_BLUE,
    T_YELLOW,
    T_GREEN,
    T_PINK,
    T_NORMAL,
)
from config import (
    C_WALL,
    IC_TYPE,
    GRID_KILL_STEP,
    f_save_words_used,
    MAX_WAL,
    f_verbose,
    ACTIVE_WORDS_JSON,
)
import migrations.database

WORDLIST = migrations.database.get_non_rejected_words()
if not f_save_words_used:
    WORDLIST_SET = set(WORDLIST)

id = int(time.time())
SOL_JSON = f"solutions/solutions_{id}.json"


v_best_score = 0
solutions = []


def recursive_search(grid, level=0):
    global v_best_score
    global solutions

    if level >= GRID_KILL_STEP + 1:
        exit()

    if f_verbose:
        tqdm.tqdm.write(
            T_BLUE + f"{json.dumps(grid, indent=2, ensure_ascii=False)}" + T_NORMAL
        )

    if f_save_words_used:
        words_contained = get_words_in_partial_grid(grid)
        trashed_words = words_contained - set(
            migrations.database.get_non_rejected_words()
        )
    else:
        trashed_words = get_words_in_partial_grid(grid) - WORDLIST_SET

    if trashed_words:
        tqdm.tqdm.write("\n")
        tqdm.tqdm.write(
            T_PINK + f"FOUND TRASHED WORD ... Skipping: {trashed_words}" + T_NORMAL
        )
        tqdm.tqdm.write(T_PINK + "\n".join(grid) + T_NORMAL)
        return
    elif f_save_words_used:
        words_active = torus.json.load_json(ACTIVE_WORDS_JSON)
        words_reviewed = migrations.database.get_words_reviewed()
        for w in words_contained:
            if w in words_active or w in words_reviewed:
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
        for new_grid in t:
            recursive_search(new_grid.copy(), level + 1)

        t.close()


if __name__ == "__main__":
    tamplates = torus.json.load_json("liked_templates.json")
    failed_templates = torus.json.load_json("bad_templates.json")

    templates_of_interest = [
        [t[i : i + 15] for i in range(0, 225, 15)]
        for t in tamplates[str(MAX_WAL)]
        if t not in failed_templates[str(MAX_WAL)]
    ]

    import random

    # templats of interest are those not in the chat

    ls = len(tamplates[str(MAX_WAL)])
    lsoi = len(templates_of_interest)
    random.shuffle(templates_of_interest)

    for i, t in enumerate(templates_of_interest):
        tqdm.tqdm.write(T_YELLOW + f"Trial {i} / {lsoi}  ({ls} tot)" + T_NORMAL)

        grid = add_theme_words(t, IC_TYPE)

        words = get_word_locations(grid, Direction.ACROSS) + get_word_locations(
            grid, Direction.DOWN
        )
        tqdm.tqdm.write(T_YELLOW + f"> max wall {MAX_WAL}" + T_NORMAL)
        tqdm.tqdm.write(T_YELLOW + f"> number of answers {len(words)}" + T_NORMAL)
        tqdm.tqdm.write(
            T_YELLOW
            + f"> number of black squares {"".join(grid).count(C_WALL)}"
            + T_NORMAL
        )

        recursive_search(grid, 0)

        if not len(solutions):
            print("No solution found")
            failed_templates = torus.json.load_json("bad_templates.json")
            t_str = "".join(t)
            n_w = t_str.count(C_WALL)
            if t_str not in failed_templates[str(n_w)]:
                failed_templates[str(n_w)].append("".join(t))
                torus.json.write_json("bad_templates.json", failed_templates)
        else:
            print(T_GREEN, f"Found {len(solutions)} solutions", T_NORMAL)
        solutions = []
