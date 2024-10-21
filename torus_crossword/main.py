"""15x15 grids use _ █ and @, this script places the words"""

from datetime import datetime
import pytz
import json
import re
import tqdm
import random
import os
from collections import deque

from fast_search import get_new_grids as get_new_grids_main

from config import (
    WOR_JSON,
    ACTIVE_WORDS_JSON,
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    WORDS_APPROVED_JSON,
    WORDS_OMITTED_JSON,
    ROWLEN,
    GRIDCELLS,
    STAR_START,
    C_WALL,
    GRID_TEMPLATE,
    GRID_TEMPLATE_FLIPPED,
    get_failures_json,
    get_solutions_json,
    get_bad_solutions_json,
    IC_TYPE,
    MAX_WAL,
    SEARCH_W_FLIPPED,
    f_verbose,
    f_save_words_used,
    f_save_bounds,
)

import torus

from lib import (
    transpose,
    replace_char_in_string,
    string_to_star,
    T_BLUE,
    T_GREEN,
    T_NORMAL,
    T_PINK,
    T_YELLOW,
    add_theme_words,
    get_star_from_grid,
)


# grids i dont like

FAI_JSON = get_failures_json(IC_TYPE, MAX_WAL, flipped=SEARCH_W_FLIPPED)
SOL_JSON = get_solutions_json(IC_TYPE, MAX_WAL, flipped=SEARCH_W_FLIPPED)
BAD_SOL_JSON = get_bad_solutions_json(IC_TYPE, MAX_WAL, flipped=SEARCH_W_FLIPPED)
if not os.path.exists(FAI_JSON):
    torus.json.write_json(FAI_JSON, [])
if not os.path.exists(SOL_JSON):
    torus.json.write_json(SOL_JSON, [])
if not os.path.exists(BAD_SOL_JSON):
    torus.json.write_json(BAD_SOL_JSON, [])


if not SEARCH_W_FLIPPED:
    STA_JSON = STARS_FOUND_JSON
    INITIAL_TEMPLATE = GRID_TEMPLATE
else:
    STA_JSON = STARS_FOUND_FLIPPED_JSON
    INITIAL_TEMPLATE = GRID_TEMPLATE_FLIPPED


# bests

v_best_grids = []
v_best_score = 0

WORDLIST = torus.json.load_json(WOR_JSON)
if not f_save_words_used:
    WORDLIST_SET = set(WORDLIST)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = C_WALL + w + C_WALL
random.shuffle(WORDLIST)


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
        for candidate_word in WORDLIST:
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
    return any(c not in ["█", "_"] for c in line)


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
    return line.replace("█_█", "███").replace("█__█", "████")


def add_letter_placeholders_line(line: str) -> str:
    """Add placeholders for letters in the line."""

    double = line + line
    matches = re.finditer(r"█[A-Z@][A-Z@_][A-Z@_]", double)
    for match in matches:
        if line[(match.end() - 2) % ROWLEN] == "_":
            line = replace_char_in_string(line, "@", (match.end() - 2) % ROWLEN)
        if line[(match.end() - 1) % ROWLEN] == "_":
            line = replace_char_in_string(line, "@", (match.end() - 1) % ROWLEN)

    double = line + line
    matches = re.finditer(r"█_[A-Z@]_", double)
    for match in matches:
        line = replace_char_in_string(line, "@", (match.end() - 1) % ROWLEN)

    double = line + line
    matches = re.finditer(r"[A-Z@_][A-Z@_][A-Z@]█", double)
    for match in matches:
        if line[(match.start()) % ROWLEN] == "_":
            line = replace_char_in_string(line, "@", match.start() % ROWLEN)
        if line[(match.start() + 1) % ROWLEN] == "_":
            line = replace_char_in_string(line, "@", (match.start() + 1) % ROWLEN)

    double = line + line
    matches = re.finditer(r"_[A-Z@]_█", double)
    for match in matches:
        line = replace_char_in_string(line, "@", match.start() % ROWLEN)

    return line


def fill_in_small_holes(grid: list[str]) -> list[str]:
    """Return a grid with holes filled like █_█ -> "███" or "█@__" -> "█@@@"."""
    new_grid = [fill_small_holes_line(l) for l in grid]
    tr = transpose(new_grid)  # compute transpose matrix
    new_grid = [fill_small_holes_line(l) for l in tr]
    return transpose(new_grid)


def add_letter_placeholders(grid: list[str]) -> list[str]:
    """Add placeholders for letters in the grid. like █[A-Z@][A-Z@_][A-Z@_] -> █@@@."""
    new_grid = [add_letter_placeholders_line(l) for l in grid]
    tr = transpose(new_grid)  # compute transpose matrix
    new_grid = [add_letter_placeholders_line(l) for l in tr]
    return transpose(new_grid)


def enforce_symmetry(grid: list[str]) -> list[str]:
    long_string = "".join(grid)
    for j, c in enumerate(long_string):
        rvs_idx = GRIDCELLS - 1 - j
        rvs_c = long_string[rvs_idx]

        # ENFORCE SYMETRY
        if c == C_WALL:
            if rvs_c != C_WALL and rvs_c != "_":  # check symetry
                return False
            if rvs_c == "_":  # enforce symetry
                long_string = replace_char_in_string(long_string, C_WALL, rvs_idx)
        elif c != "_":
            if rvs_c == C_WALL:  # check symetry
                return False
            if rvs_c == "_":  # enforce symetry
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


def is_only_at_and_block(s):
    return all(char in {"@", "█"} for char in s)


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

        if is_only_at_and_block(w):
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


def check_center_row_sym(line: str) -> bool:
    "Return true if line symetric in terms of C_WALL ie █@@█@█@@█"
    return any(
        [
            ((line[k] == C_WALL) ^ (line[ROWLEN - 1 - k] == C_WALL))
            for k in range(ROWLEN)
        ]
    )


def num_walls(grid: list[str]) -> int:
    "return number of wall characters in grid"
    return "".join(grid).count(C_WALL)


def grid_contains_unwalled_rows(grid: list[str]) -> bool:
    for line in grid:
        if C_WALL not in line:
            return True
    for line in transpose(grid):
        if C_WALL not in line:
            return True
    return False


def get_best_row(grid: list[str]) -> tuple[int, int, list[list[str]]]:
    """Given a grid, find the best row to latch on to.

    Returns:
        int: The index of the best row
        int: The score of the best row
        list[list[str]]: The best grids
    """

    K_INDEX = -1
    K_MIN_SCORE = 1000000000000
    K_BEST_GRIDS = []
    score = 0

    FILL_INS_TEMPLATE = grid.copy()

    for row in range(ROWLEN):
        # for every row, compute the latch with the fewest fitting words

        # for each line
        line = grid[row]
        if is_line_filled(line) or not latches_in_line(line):
            continue

        # TODO: reduce time of get fixtures, but using one line to tell other
        fixtures = get_fixtures(line)

        if not fixtures:
            continue

        candidate_lines = get_new_lines(fixtures, line)

        if not candidate_lines:
            # no words fit template
            return row, 0, []

        # get the squares that have letters in all of the candidate lines
        for i in range(15):  # every letter location
            if FILL_INS_TEMPLATE[row][i] != "_":
                continue
            all_fills = set(line[i] for line in candidate_lines)
            if len(all_fills) == 1:
                FILL_INS_TEMPLATE[row] = replace_char_in_string(
                    FILL_INS_TEMPLATE[row], next(iter(all_fills)), i
                )
            elif C_WALL not in all_fills and "_" not in all_fills:
                FILL_INS_TEMPLATE[row] = replace_char_in_string(
                    FILL_INS_TEMPLATE[row], "@", i
                )

        # TODO: DO THIS WITHOUT COMPUTING GRIDS EXPLICITLY
        # now that you have the words that fit, do any lead to a trvially bad grid?
        working_grids: list[list[str]] = []
        num_new_grids_from_line = 0
        num_blanks = 0
        for l in candidate_lines:
            if row == 7 and not check_center_row_sym(l):
                continue
            candidate_grid = grid.copy()
            candidate_grid[row] = l  # make line word from options

            candidate_grid = enforce_symmetry(candidate_grid)
            if not candidate_grid:
                continue
            candidate_grid = fill_in_small_holes(candidate_grid)

            if num_walls(candidate_grid) > MAX_WAL:
                continue

            if grid_contains_englosed_spaces(candidate_grid):
                continue

            candidate_grid = add_letter_placeholders(candidate_grid)

            if num_walls(candidate_grid) == MAX_WAL:
                if grid_contains_unwalled_rows(candidate_grid):
                    continue
                for j in range(ROWLEN):
                    candidate_grid[j] = candidate_grid[j].replace("_", "@")

            if grid_contains_short_words(candidate_grid):
                continue

            working_grids.append(candidate_grid)
            num_blanks += "".join(candidate_grid).count(
                "_"
            )  # minimize number of total blanks

            # grid is approved!
            num_new_grids_from_line += 1

            # the idea us that i need -> 1000 grids with 0 blanks
            # less preferable then -> 10 grids with 100 blanks
            # 1000 grids with 0 blanks > 10 grids with 100 blanks
            # score = num_grids * (num_blanks + 1)

            # score = num_new_grids_from_line * (num_blanks + 1)
            # score = num_blanks
            # score = num_new_grids_from_line
            score = num_blanks + num_new_grids_from_line
            if score > K_MIN_SCORE:  # minimize score
                break
        else:
            if score >= K_MIN_SCORE:
                continue

            K_MIN_SCORE = score
            K_MIN_GRIDS = num_new_grids_from_line
            K_INDEX = row
            K_BEST_GRIDS = working_grids

    # check to make sure it is possible to make grid symetric from all row options
    # o = FILL_INS_TEMPLATE
    FILL_INS_TEMPLATE = enforce_symmetry(FILL_INS_TEMPLATE)
    if not FILL_INS_TEMPLATE:
        # tqdm.tqdm.write(T_YELLOW + "below not actually doable" + T_NORMAL)
        # print(T_YELLOW + json.dumps(o, indent=2, ensure_ascii=False) + T_NORMAL)
        return row, 0, []

    betterd_grids = []
    for g in K_BEST_GRIDS:
        for i in range(ROWLEN):
            for j in range(ROWLEN):
                if g[i][j] == "_" and FILL_INS_TEMPLATE[i][j] != "_":
                    g[i][j] == FILL_INS_TEMPLATE[i][j]
        betterd_grids.append(g)

    return K_INDEX, K_MIN_SCORE, K_BEST_GRIDS


def get_new_grids(grid: list[str]) -> tuple[str, int, list[list[str]]]:
    """Given a grid, find the best row or column to latch on to."""

    # find the best row to latch on
    row_idx, best_row_score, best_row_grids = get_best_row(grid)
    # transpose to find the best collum
    col_idx, best_col_score, best_col_grids = get_best_row(transpose(grid))

    # note you want to minimize scre
    if best_row_score < best_col_score:
        return "r", row_idx, best_row_grids
    else:
        # transform back all of the column grids
        transposed_col_grids = [transpose(g) for g in best_col_grids]
        return "c", col_idx, transposed_col_grids


def print_grid(grid: list[str], h: tuple[str, int, str]):

    grid_copy = grid.copy()

    h_color = h[2]
    if h[0] == "r":
        grid_copy[h[1]] = h_color + grid_copy[h[1]] + T_NORMAL
    else:
        for i in range(ROWLEN):
            grid_copy[i] = replace_char_in_string(
                grid_copy[i], h_color + grid_copy[i][h[1]] + T_NORMAL, h[1]
            )

    return "\n".join(grid_copy) + T_NORMAL


def get_words_in_partial_grid(grid: list[str]) -> set[str]:
    across_words = set()
    for l in grid:
        bits = (l + l).split(C_WALL)[1:-1]

        for b in bits:
            if b and ("@" not in b) and ("_" not in b):
                across_words.add(b)

    down_words = set()
    for l in transpose(grid):
        bits = (l + l).split(C_WALL)[1:-1]
        for b in bits:
            if b and "@" not in b and "_" not in b:
                down_words.add(b)

    return across_words | down_words


def recursive_search(grid, level=0):
    global v_best_score
    global v_best_grids

    if grid_filled(grid):
        tqdm.tqdm.write(T_GREEN + "Solution found")  # Green text indicating success
        tqdm.tqdm.write(json.dumps(grid, indent=2, ensure_ascii=False))
        tqdm.tqdm.write(T_NORMAL)

        current_solutions = torus.json.load_json(SOL_JSON)
        current_bad_solutions = torus.json.load_json(BAD_SOL_JSON)
        if grid in current_solutions or grid in current_bad_solutions:
            tqdm.tqdm.write(T_PINK + "Already in solutions" + T_NORMAL)
            return
        torus.json.append_json(SOL_JSON, grid)
        return

    if f_save_words_used:
        trashed_words = get_words_in_partial_grid(grid) - set(
            torus.json.load_json(WOR_JSON)
        )
    else:
        trashed_words = get_words_in_partial_grid(grid) - WORDLIST_SET

    if trashed_words:
        if f_verbose:
            tqdm.tqdm.write("\n")
            tqdm.tqdm.write(
                T_PINK + f"FOUND TRASHED WORD ... Skipping: {trashed_words}" + T_NORMAL
            )
            tqdm.tqdm.write(T_PINK + "\n".join(grid) + T_NORMAL)
        return

    grid_str = "".join(grid)
    if grid_str.count("_") == 0:
        for i, line in enumerate(grid):
            if C_WALL not in line:
                tqdm.tqdm.write("\n")
                tqdm.tqdm.write(f"Grid has max walls but ROW {i} has no black squares.")
                tqdm.tqdm.write(print_grid(grid, ("r", i, T_BLUE)))
                return

        for i, line in enumerate(transpose(grid)):
            if C_WALL not in line:
                tqdm.tqdm.write("\n")
                tqdm.tqdm.write(f"Grid has max walls but COL {i} has no black squares.")
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

        if not new_grids:
            if f_verbose:
                out1 = (
                    f"No possibilities ROW {start}"
                    if row_or_col == "r"
                    else f"\nNo possibilities COL {start}"
                )
                tqdm.tqdm.write("\n")
                tqdm.tqdm.write(out1)
                tqdm.tqdm.write(print_grid(grid, (row_or_col, start, T_PINK)))

            return

        # reorder longest first
        if False:
            if row_or_col == "r":
                lines = [g[start] for g in new_grids]
                # reorder longest first
            else:
                lines = [transpose(g)[start] for g in new_grids]

            ind_w_line_sorted = sorted(
                enumerate(lines),
                key=lambda x: count_letters_in_line(x[1]),
                reverse=True,
            )
            new_grids = [new_grids[i].copy() for i, _ in ind_w_line_sorted]

        if f_save_words_used and f_save_bounds[0] <= len(new_grids) <= f_save_bounds[1]:
            words_seen = set(torus.json.load_json(ACTIVE_WORDS_JSON))
            if row_or_col == "r":
                for pp in new_grids:
                    row = pp[start]
                    words_seen |= set(
                        [
                            l
                            for l in (row + row).split(C_WALL)[1:-1]
                            if l and "@" not in l and "_" not in l
                        ]
                    )
            else:
                for pp in new_grids:
                    row = transpose(pp)[start]
                    words_seen |= set(
                        [
                            l
                            for l in (row + row).split(C_WALL)[1:-1]
                            if l and "@" not in l and "_" not in l
                        ]
                    )

            # get all words in words approved, and add them to active words
            words_approved = torus.json.load_json(WORDS_APPROVED_JSON)
            words_active = torus.json.load_json(ACTIVE_WORDS_JSON)
            words_omitted = torus.json.load_json(WORDS_OMITTED_JSON)

            for w in words_seen:
                if w in words_active or w in words_approved or w in words_omitted:
                    continue
                tqdm.tqdm.write(T_YELLOW + f"Adding {w} to active words" + T_NORMAL)
                torus.json.append_json(ACTIVE_WORDS_JSON, w)

        with tqdm.tqdm(new_grids, desc=f"Level {level}", leave=False) as t:
            if f_verbose:
                len_new_grids = len(new_grids)
                out2 = (
                    f"Testing {len_new_grids} possibilities for ROW {start}"
                    if row_or_col == "r"
                    else f"Testing {len_new_grids} possibilities for COL {start}"
                )
                tqdm.tqdm.write("\n")
                tqdm.tqdm.write(out2)
                tqdm.tqdm.write(print_grid(grid, (row_or_col, start, T_GREEN)))

            for new_grid in t:
                recursive_search(new_grid, level + 1)


if __name__ == "__main__":
    stars_strings = torus.json.load_json(STA_JSON)
    fail_stars = torus.json.load_json(FAI_JSON)

    t0 = datetime.now()
    INITIAL_TEMPLATE = add_theme_words(INITIAL_TEMPLATE, IC_TYPE)
    grid = INITIAL_TEMPLATE.copy()

    ####
    # DETERMINE STARS TO SEARCH
    joined_grids_cache = {}

    fail_stars_set = set(fail_stars)
    id_stars_of_interest = []
    id_stars_of_interest = [
        (i, s) for i, s in enumerate(stars_strings) if s not in fail_stars_set
    ]

    #####

    random.shuffle(id_stars_of_interest)
    ls = len(stars_strings)
    lsoi = len(id_stars_of_interest)

    # Get the current UTC time, then convert it to US Eastern
    eastern = pytz.timezone("US/Eastern")
    eastern_now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(eastern)
    datetime_string_am_pm = eastern_now.strftime("%Y-%m-%d %I:%M:%S %p")

    print()
    print(T_YELLOW + "Saving Solutions to: " + T_GREEN + SOL_JSON + T_NORMAL)
    print(T_YELLOW + "Saving Failures to: " + T_GREEN + FAI_JSON + T_NORMAL)
    print(T_YELLOW + "Current time: " + T_GREEN + f"{datetime_string_am_pm}" + T_NORMAL)
    print()
    for t, s in enumerate(id_stars_of_interest):
        init_id, star_str = s
        tqdm.tqdm.write(T_YELLOW + f"Trial {t} / {lsoi}  ({ls} tot)" + T_NORMAL)
        tqdm.tqdm.write(T_YELLOW + f"Star id: " + T_NORMAL + f"{init_id}")
        grid = INITIAL_TEMPLATE.copy()

        grid = add_star(grid, string_to_star(star_str))
        fail_stars_str = torus.json.load_json(FAI_JSON)

        if star_str in fail_stars_str:
            tqdm.tqdm.write(T_BLUE + "Already Failed - Skipping" + T_NORMAL)
            continue

        recursive_search(grid, 0)

        all_solutions = torus.json.load_json(SOL_JSON)
        for s in all_solutions:
            star = get_star_from_grid(s, SEARCH_W_FLIPPED)
            if star == star_str:
                for _ in range(20):
                    print(T_YELLOW + "TOTALLY COMPLETED GOOD GRID" + T_NORMAL)

                print(T_PINK + star_str + T_NORMAL)
                exit()
                break
        else:
            print(T_PINK + "No solution found." + T_NORMAL)
            torus.json.append_json(FAI_JSON, star_str)
