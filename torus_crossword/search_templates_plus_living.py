"""
idea:
- run this (builds up failed templates)
- then run main
- keep the failed ics, but the restore the failed templates (bad)
"""

import torus
from lib import Direction
from fast_search import get_word_locations, get_new_grids
import time
import json
import tqdm
import torus

from main import add_star
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
    WOR_JSON,
    GRID_KILL_STEP,
    f_save_words_used,
    MAX_WAL,
    f_verbose,
    WOR_JSON,
    WORDS_APPROVED_JSON,
    STARS_FOUND_FLIPPED_JSON,
    ACTIVE_WORDS_JSON,
    WORDS_OMITTED_JSON,
    SEARCH_W_FLIPPED,
    get_failures_json,
)

WORDLIST = torus.json.load_json(WOR_JSON)
if not f_save_words_used:
    WORDLIST_SET = set(WORDLIST)

id = int(time.time())
SOL_JSON = f"solutions/solutions_{id}.json"


v_best_score = 0
solutions = []


def recursive_search(grid, level=0):
    global v_best_score
    global solutions

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

    ic_all = torus.json.load_json(STARS_FOUND_FLIPPED_JSON)
    ic_failures = torus.json.load_json(
        get_failures_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)
    )
    ics_of_interest = [ic for ic in ic_all if ic not in ic_failures]

    print("total templates to check:", len(templates_of_interest))
    print("total ic to check:", len(ics_of_interest))

    # templats of interest are those not in the chat

    lsoi = len(templates_of_interest)
    random.shuffle(templates_of_interest)

    for i, t in enumerate(templates_of_interest):
        words = get_word_locations(t, Direction.ACROSS) + get_word_locations(
            t, Direction.DOWN
        )
        tqdm.tqdm.write(T_YELLOW + f"> max wall {MAX_WAL}" + T_NORMAL)
        tqdm.tqdm.write(T_YELLOW + f"> number of answers {len(words)}" + T_NORMAL)
        tqdm.tqdm.write(
            T_YELLOW
            + f"> number of black squares {"".join(t).count(C_WALL)}"
            + T_NORMAL
        )

        failed_templates = torus.json.load_json("bad_templates.json")
        if "".join(t) in failed_templates[str(MAX_WAL)]:
            print(T_BLUE + "> already failed, skipping" + T_NORMAL)
            continue

        tqdm.tqdm.write(T_YELLOW + f"Trial {i} / {lsoi}" + T_NORMAL)
        for ic in tqdm.tqdm(ics_of_interest):
            t_i_care_about = add_star(t, [ic[v : v + 6] for v in range(0, 36, 6)])

            grid = add_theme_words(t_i_care_about, IC_TYPE)

            recursive_search(grid, 0)

        if not len(solutions):
            print("No solution found")
            failed_templates = torus.json.load_json("bad_templates.json")
            t_str = "".join(t)
            n_w = t_str.count(C_WALL)
            if t_str not in failed_templates[str(n_w)]:
                failed_templates[str(n_w)].append("".join(t))
                torus.json.write_json("bad_templates.json", failed_templates)

        if len(solutions):
            print(T_GREEN, f"Found {len(solutions)} solutions", T_NORMAL)
            exit()
        solutions = []
