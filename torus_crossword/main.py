"""15x15 grids use _ █ and @, this script places the words"""

from datetime import datetime
import json
import re
import tqdm
import time
import random
import os
from collections import deque

from fast_search import get_new_grids as get_new_grids_main

from config import (
    WOR_JSON,
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    ROWLEN,
    GRIDCELLS,
    STAR_START,
    C_WALL,
    GRID_TEMPLATE,
    GRID_TEMPLATE_FLIPPED,
    get_failures_json,
    get_solutions_json,
)

from torus.json import append_json, load_json, write_json

from lib import (
    transpose,
    replace_char_in_string,
    string_to_star,
    T_BLUE,
    T_GREEN,
    T_NORMAL,
    T_PINK,
    T_YELLOW,
)


f_flipped = False
TYPE = "AD"  # TORUS ACROSS
MAX_WALLS = 42

f_verbose = True

FAI_JSON = get_failures_json(TYPE, MAX_WALLS, flipped=f_flipped)
SOL_JSON = get_solutions_json(TYPE, MAX_WALLS, flipped=f_flipped)

if not f_flipped:
    STA_JSON = STARS_FOUND_JSON

    INITIAL_TEMPLATE = GRID_TEMPLATE
else:
    STA_JSON = STARS_FOUND_FLIPPED_JSON
    INITIAL_TEMPLATE = GRID_TEMPLATE_FLIPPED

if not os.path.exists(FAI_JSON):
    write_json(FAI_JSON, [])
if not os.path.exists(SOL_JSON):
    write_json(SOL_JSON, [])

if TYPE == "AA":
    INITIAL_TEMPLATE[7] = "HUNT█TORUS█DOUG"
elif TYPE == "AD":
    col7 = "HNUT█_____█DOUG"
    for i in range(ROWLEN):
        INITIAL_TEMPLATE[i] = replace_char_in_string(INITIAL_TEMPLATE[i], col7[i], 7)
    INITIAL_TEMPLATE[7] = "____█TORUS█____"
elif TYPE == "DA":
    INITIAL_TEMPLATE[7] = "HNUT█_____█DOUG"
    col7 = "____█TORUS█____"
    for i in range(ROWLEN):
        INITIAL_TEMPLATE[i] = replace_char_in_string(INITIAL_TEMPLATE[i], col7[i], 7)
elif TYPE == "DD":
    col7 = "HUNT█TORUS█DOUG"
    for i in range(ROWLEN):
        INITIAL_TEMPLATE[i] = replace_char_in_string(INITIAL_TEMPLATE[i], col7[i], 7)

# bests
new_solutions = []  # tracks initial conditions solutions
v_best_grids = []
v_best_score = 0

WORDLIST = load_json(WOR_JSON)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = C_WALL + w + C_WALL

SORTED_WORDLIST = sorted(WORDLIST, key=len)  # short words first
SORTED_WORDLIST_L = sorted(SORTED_WORDLIST, key=len, reverse=True)  # long words first

import random

random.shuffle(WORDLIST)
WORDS_TO_USE = WORDLIST


def add_star(grid, star):
    grid = [list(row) for row in grid]

    for i, line in enumerate(star):
        r = (STAR_START[0] + i) % ROWLEN
        for j, l in enumerate(line):
            if l != "█":
                c = (STAR_START[1] + j) % ROWLEN
                grid[r][c] = l

    return ["".join(row) for row in grid]


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "_" in l or "@" in l:
            return False
    return True


def count_letters_in_line(line: str) -> int:
    return len([c for c in line if c.isalpha()])


def count_letters(grid: list[str]) -> int:
    return GRIDCELLS - sum([l.count("_") + l.count("@") + l.count("█") for l in grid])


def check_line_for_short_words(line: str) -> bool:
    """Check if there are any one or two letter words in the line."""
    m = line.split(C_WALL)
    for word in m:
        if len(word) in [1, 2] and any(c.isalpha() or c == "@" for c in word):
            return True
    return False


def can_letter_go_there(suggestion: str, current_entry: str) -> bool:
    if current_entry in [suggestion, "_"] or (
        suggestion != C_WALL and current_entry == "@"
    ):
        return True
    return False


def can_word_go_there(word: str, line: str, pos) -> bool:
    for j, suggested_letter in enumerate(word):  # suggested letter
        p = (pos + j) % ROWLEN
        if not can_letter_go_there(suggestion=suggested_letter, current_entry=line[p]):
            return False
    return True


def replace_word_at(word: str, line: str, start_idx: int) -> str:
    new_template = line[:start_idx] + word
    t_len = len(new_template)
    if t_len < ROWLEN:
        new_template += line[t_len:]
    elif t_len > ROWLEN:
        y = t_len - ROWLEN
        new_template = new_template[:ROWLEN]
        new_template = word[-y:] + new_template[y:]

    return new_template


# TODO: Change this to break after each iteration surpasses the best score
def get_new_lines(fixtures: list[tuple[str, int, str]], line: str) -> list[str]:
    """Get all possible new lines templates for a line given the fixtures."""
    new_tempalates = {i: [] for i, _ in fixtures}
    max_len = max([len(c) for c in (line + line).split(C_WALL)]) + 2  # includes 2 walls

    # possible
    # return shortest item
    shortest_len = 100000000
    shortest_i = -1
    for i, cont in fixtures:

        stop_processing = False
        num_possible_words = 0
        lc = len(cont)
        pattern = cont.replace("@", f"[^{C_WALL}]")
        for candidate_word in WORDS_TO_USE:
            lw = len(candidate_word)
            if lw > max_len or lw < lc:
                continue

            matches = re.finditer(pattern, candidate_word)
            positions = [match.start() for match in matches]

            for p in positions:
                if can_word_go_there(candidate_word, line, i - p):
                    new_tempalates[i].append(
                        replace_word_at(candidate_word, line, i - p)
                    )
                    num_possible_words += 1
                    if num_possible_words > shortest_len:
                        stop_processing = True
                        break
            if stop_processing:
                break
        if stop_processing:
            continue

        v = new_tempalates[i]
        len_v = len(v)
        if len_v < shortest_len:
            shortest_len = len_v
            shortest_i = i

    candidate_lines = new_tempalates[shortest_i]
    return candidate_lines


def is_line_filled(line: str) -> bool:
    """Return true if "@" and "_" not in line"""
    return "@" not in line and "_" not in line


def latches_in_line(line: str) -> bool:
    """Return true if line contains latches"""
    return not any(c not in ["█", "_"] for c in line)


def fill_small_holes_line(line: str) -> str:
    # fastest approach it seems

    if line.startswith("_█"):
        line = "██" + line[2:]
    if line.endswith("█_"):
        line = line[:-2] + "██"
    if line.startswith("__█") or line.startswith("_██"):
        line = "███" + line[3:]
    if line.endswith("█__") or line.endswith("██_"):
        line = line[:-3] + "███"
    return (
        line.replace("█_█", "███")
        .replace("█__█", "████")
        .replace("█@__", "█@@@")
        .replace("█@@_", "█@@@")
        .replace("█@_@", "█@@@")
        .replace("__@█", "@@@█")
        .replace("@_@█", "@@@█")
        .replace("_@@█", "@@@█")
        .replace("█_@_█", "█@@@█")
    )


def fill_in_small_holes(grid: list[str]) -> list[str]:
    """Return a grid with holes filled like █_█ -> "███" or "█@__" -> "█@@@"."""
    new_grid = [fill_small_holes_line(l) for l in grid]
    tr = transpose(new_grid)  # compute transpose matrix
    new_grid = [fill_small_holes_line(l) for l in tr]
    return transpose(new_grid)


def enforce_symmetry(grid: list[str]) -> list[str]:
    long_string = "".join(grid)
    for j, c in enumerate(long_string):
        rvs_idx = GRIDCELLS - 1 - j
        if long_string[rvs_idx] != "_":
            continue

        if c == C_WALL:
            long_string = replace_char_in_string(long_string, C_WALL, rvs_idx)
        elif c != "_":
            long_string = replace_char_in_string(long_string, "@", rvs_idx)

    return [long_string[j : j + ROWLEN] for j in range(0, GRIDCELLS, ROWLEN)]


def grid_contains_short_words(grid: list[str]) -> bool:
    for line in grid:
        if check_line_for_short_words(line):
            return True

    for line in transpose(grid):
        if check_line_for_short_words(line):
            return True
    return False


def get_fixtures(line: str) -> list[tuple[int, str]]:
    indices: list[int] = [
        index for index, char in enumerate(line) if char not in ["█", "_"]
    ]
    if not indices:
        return []

    grouped = []
    current_group = [indices[0]]

    for current, next in zip(indices[:-1], indices[1:]):
        if next == current + 1:
            current_group.append(next)
        else:
            grouped.append(current_group)
            current_group = [next]

    grouped.append(current_group)

    if grouped[0][0] == 0 and grouped[-1][-1] == ROWLEN - 1:
        grouped[-1].extend([i + ROWLEN for i in grouped[0]])
        grouped.pop(0)

    fixtures: list[tuple[int, str]] = []
    for g in grouped:
        strt = g[0]
        w = "".join(line[i % ROWLEN] for i in g)
        if line[g[0] - 1 % ROWLEN] == "█":
            w = "█" + w
            strt -= 1
        if line[(g[-1] + 1) % ROWLEN] == "█":
            w = w + "█"

        if w.count(C_WALL) == 2 and "@" not in w:
            continue
        fixtures.append((strt, w))

    return fixtures


def grid_contains_englosed_spaces(grid):
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]

    # Directions for moving up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Find the starting point for a non-wall character
    start = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "█":
                start = (r, c)
                break
        if start:
            break

    if not start:
        return False  # No white squares

    # BFS to check connectivity
    queue = deque([start])
    visited[start[0]][start[1]] = True
    count = 1  # Number of visited white squares

    while queue:
        r, c = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and not visited[nr][nc]
                and grid[nr][nc] != "█"
            ):
                visited[nr][nc] = True
                queue.append((nr, nc))
                count += 1

    # Count all non-wall squares
    total_non_wall = sum(row.count("█") for row in grid)
    total_non_wall = rows * cols - total_non_wall  # Total non-wall characters

    return count != total_non_wall


def get_best_row(grid: list[str]) -> tuple[int, int, list[list[str]]]:
    K_INDEX = -1
    K_BEST_SCORE = 1000000000
    K_BEST_GRIDS = []

    for row in range(ROWLEN):
        # for every row, compute the latch with the fewest fitting words

        # for each line
        line = grid[row]
        if is_line_filled(line) or latches_in_line(line):
            continue

        # TODO: reduce time of get fixtures, but using one line to tell other
        fixtures = get_fixtures(line)

        if not fixtures:
            continue

        # TODO: get possible word lens from the grid:
        candidate_lines = get_new_lines(fixtures, line)

        if not candidate_lines:
            # no words fit template
            return row, 0, []

        # TODO: DO THIS WITHOUT COMPUTING GRIDS EXPLICITLY
        # now that you have the words that fit, do any lead to a trvially bad grid?
        working_grids: list[list[str]] = []
        m = 0
        for l in candidate_lines:
            candidate_grid = grid.copy()

            if row == 7:
                if any(
                    [
                        C_WALL in [l[k], l[14 - k]] and l[k] != l[14 - k]
                        for k in range(ROWLEN)
                    ]
                ):
                    continue

            candidate_grid[row] = l  # make line word from options

            candidate_grid = enforce_symmetry(candidate_grid)
            candidate_grid = fill_in_small_holes(candidate_grid)

            # NOTE: This ensures not to many walls
            num_walls = "".join(candidate_grid).count(C_WALL)
            if num_walls > MAX_WALLS:
                continue

            if grid_contains_englosed_spaces(candidate_grid):
                continue

            if num_walls == MAX_WALLS:
                for j in range(ROWLEN):
                    if C_WALL in candidate_grid[j]:
                        candidate_grid[j] = candidate_grid[j].replace("_", "@")

                passes = True
                for line in grid:
                    if C_WALL not in line:
                        passes = False
                        break

                for line in transpose(grid):
                    if C_WALL not in line:
                        passes = False
                        break

                if not passes:
                    continue

            if grid_contains_short_words(candidate_grid):
                continue

            working_grids.append(candidate_grid)

            m += 1
            if m > K_BEST_SCORE:
                break
        else:
            K_INDEX = row
            K_BEST_SCORE = m
            K_BEST_GRIDS = working_grids

    # candidate_grid = [long_string[j:j+ROWLEN] for j in range(0, len(long_string), ROWLEN)]
    return K_INDEX, K_BEST_SCORE, K_BEST_GRIDS


def get_new_grids(grid: list[str]) -> tuple[str, int, list[list[str]]]:
    """Given a grid, find the best row or column to latch on to."""

    # find the best row to latch on
    row_idx, best_row_score, best_row_grids = get_best_row(grid)
    # transpose to find the best collum
    col_idx, best_col_score, best_col_grids = get_best_row(transpose(grid))

    # TODO: SOMETHING WRONG HERE???
    if best_row_score <= best_col_score:
        return "r", row_idx, best_row_grids
    else:
        # transform back all of the column grids
        transposed_col_grids = [transpose(g) for g in best_col_grids]
        return "c", col_idx, transposed_col_grids


def print_grid(grid: list[str], h: tuple[str, int, str]):
    BACKGROUND = T_NORMAL

    print_grid = grid.copy()

    h_color = h[2]
    if h[0] == "r":
        print_grid[h[1]] = h_color + print_grid[h[1]] + BACKGROUND
    else:
        for i in range(ROWLEN):
            print_grid[i] = replace_char_in_string(
                print_grid[i], h_color + print_grid[i][h[1]] + BACKGROUND, h[1]
            )

    return "\n".join(print_grid) + T_NORMAL


def recursive_search(grid, level=0):
    global new_solutions
    global v_best_score
    global v_best_grids

    if grid_filled(grid):
        tqdm.tqdm.write(T_GREEN + "Solution found")  # Green text indicating success
        tqdm.tqdm.write(json.dumps(grid, indent=2, ensure_ascii=False))
        tqdm.tqdm.write(T_NORMAL)

        current_solutions = load_json(SOL_JSON)
        if grid in current_solutions:
            tqdm.tqdm.write(T_PINK + "Already in solutions" + T_NORMAL)
            return
        new_solutions.append(grid)
        append_json(SOL_JSON, grid)
        return

    grid_str = "".join(grid)
    if grid_str.count(C_WALL) >= MAX_WALLS and grid_str.count("_") == 0:
        for i, line in enumerate(grid):
            if C_WALL not in line:
                tqdm.tqdm.write(
                    f"\nGrid has max walls but ROW {i} has no black squares."
                )
                tqdm.tqdm.write(print_grid(grid, ("r", i, T_BLUE)))
                return

        for i, line in enumerate(transpose(grid)):
            if C_WALL not in line:
                tqdm.tqdm.write(
                    f"\nGrid has max walls but COL {i} has no black squares."
                )
                tqdm.tqdm.write(print_grid(grid, ("c", i, T_BLUE)))
                return

        new_grids = get_new_grids_main(grid)

        if not new_grids:
            if f_verbose:
                tqdm.tqdm.write(f"\nGrid disqualified by letter check")
                tqdm.tqdm.write(T_BLUE + "\n".join(grid) + T_NORMAL)
            return

        with tqdm.tqdm(new_grids, desc=f"Level {level}", leave=False) as t:
            if f_verbose:
                tqdm.tqdm.write(
                    T_GREEN
                    + f"\nTesting {len(new_grids)} possibilities for one square"
                    + T_NORMAL
                )
                tqdm.tqdm.write(T_GREEN + "\n".join(grid) + T_NORMAL)

            for new_grid in t:
                recursive_search(new_grid, level + 1)

    else:
        row_or_col, start, new_grids = get_new_grids(grid)
        # row_or_col, start, new_grids = get_new_grids_p(grid, level)

        if not new_grids:
            if f_verbose:
                out1 = (
                    f"\nNo possibilities ROW {start}"
                    if row_or_col == "r"
                    else f"\nNo possibilities COL {start}"
                )
                tqdm.tqdm.write(out1)
                tqdm.tqdm.write(print_grid(grid, (row_or_col, start, T_PINK)))

            return

        if row_or_col == "r":
            lines = [g[start] for g in new_grids]
            # reorder longest first
        else:
            lines = [transpose(g)[start] for g in new_grids]

        # reorder longest first
        ind_w_line_sorted = sorted(
            enumerate(lines),
            key=lambda x: count_letters_in_line(x[1]),
            reverse=True,
        )
        new_grids = [new_grids[i].copy() for i, _ in ind_w_line_sorted]

        with tqdm.tqdm(new_grids, desc=f"Level {level}", leave=False) as t:
            if f_verbose:
                len_new_grids = len(new_grids)
                out2 = (
                    f"\nTesting {len_new_grids} possibilities for ROW {start}"
                    if row_or_col == "r"
                    else f"\nTesting {len_new_grids} possibilities for COL {start}"
                )
                tqdm.tqdm.write(out2)
                tqdm.tqdm.write(print_grid(grid, (row_or_col, start, T_GREEN)))

                tqdm.tqdm.write("\n")
                if row_or_col == "r":
                    for pp in new_grids:
                        tqdm.tqdm.write(T_BLUE + pp[start] + T_NORMAL)
                else:
                    for pp in new_grids:
                        tqdm.tqdm.write(T_BLUE + transpose(pp)[start] + T_NORMAL)
                tqdm.tqdm.write("\n")

            for new_grid in t:
                recursive_search(new_grid, level + 1)


if __name__ == "__main__":

    stars_strings = load_json(STA_JSON)
    fail_stars = load_json(FAI_JSON)

    id_stars_of_interest = []
    t0 = datetime.now()
    grid = INITIAL_TEMPLATE.copy()

    ####
    # DETERMINE STARS TO SEARCH
    joined_grids_cache = {}

    fail_stars_set = set(fail_stars)
    id_stars_of_interest = [
        (i, s) for i, s in enumerate(stars_strings) if s not in fail_stars_set
    ]

    #####

    random.shuffle(id_stars_of_interest)
    ls = len(stars_strings)
    lsoi = len(id_stars_of_interest)
    print()
    print(T_YELLOW + f"Starting Again: " + T_GREEN + f"{time.asctime()}" + T_NORMAL)
    print(T_YELLOW + "Saving Solutions to: " + T_GREEN + SOL_JSON + T_NORMAL)
    print(T_YELLOW + "Saving Failures to: " + T_GREEN + FAI_JSON + T_NORMAL)
    print()
    for t, s in enumerate(id_stars_of_interest):
        init_id, star_str = s
        tqdm.tqdm.write(T_YELLOW + f"Trial {t} / {lsoi}  ({ls} tot)" + T_NORMAL)
        tqdm.tqdm.write(T_YELLOW + f"Star id: " + T_NORMAL + f"{init_id}")
        grid = INITIAL_TEMPLATE.copy()

        grid = add_star(grid, string_to_star(star_str))
        fail_stars_str = load_json(FAI_JSON)

        if star_str in fail_stars_str:
            tqdm.tqdm.write(T_BLUE + "Already Failed - Skipping" + T_NORMAL)
            continue

        new_solutions = []
        recursive_search(grid, 0)

        if not new_solutions:
            print(T_PINK + "No solution found." + T_NORMAL)
            append_json(FAI_JSON, star_str)
        else:
            print(T_YELLOW + "TOTALLY COMPLETED GOOD GRID" + T_NORMAL)
            print(T_PINK + star_str + T_NORMAL)
