import tqdm

from torus.json import load_json, append_json, write_json
from torus.grid import get_words_in_partial_grid
from torus.constants import T_YELLOW, T_NORMAL, T_GREEN, T_PINK
from config import (
    C_WALL,
    ACTIVE_WORDS_JSON,
    get_solutions_json,
    get_bad_solutions_json,
    IC_TYPE,
    MAX_WAL,
    WORDS_APPROVED_JSON,
    SEARCH_W_FLIPPED,
    WORDS_OMITTED_JSON,
)

SOL_JSON = get_solutions_json(IC_TYPE, MAX_WAL, flipped=SEARCH_W_FLIPPED)


def save_words_to_active(new_grids: list[list[str]]):
    words_seen = set()
    for l in new_grids:
        words_seen |= set(get_words_in_partial_grid(l))

    words_active = set(load_json(ACTIVE_WORDS_JSON))
    # get all words in words approved, and add them to active words
    words_approved = load_json(WORDS_APPROVED_JSON)
    words_omitted = load_json(WORDS_OMITTED_JSON)
    for w in words_seen:
        if w in words_active or w in words_approved or w in words_omitted:
            continue
        tqdm.tqdm.write(T_YELLOW + f"Adding {w} to active words" + T_NORMAL)
        append_json(ACTIVE_WORDS_JSON, w)


def add_to_grid_templates_if_not_seen(gt_str):
    seen_temps = load_json("liked_templates.json")
    num_walls = "".join(gt_str).count(C_WALL)
    if gt_str not in seen_temps[str(num_walls)]:
        seen_temps[str(num_walls)].append(gt_str)
        write_json("liked_templates.json", seen_temps)


def add_solution_to_json(solution: list[str], verbose=True):
    if verbose:
        tqdm.tqdm.write(
            T_GREEN + "Solution found" + "\n" + "\n".join(solution) + T_NORMAL
        )  # Green text indicating success

    sol_str = "".join(solution)
    if sol_str in load_json(SOL_JSON) or sol_str in get_bad_solutions_json(
        IC_TYPE, MAX_WAL, flipped=SEARCH_W_FLIPPED
    ):
        tqdm.tqdm.write(T_PINK + "Already in solutions" + T_NORMAL)
        return
    append_json(SOL_JSON, sol_str)
