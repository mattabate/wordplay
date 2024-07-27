"""15x15 grids use _ █ and @, this script places the words"""

import json
import re
import tqdm
import os
import time
import random
import fcntl

from main import get_new_grids as get_new_grids_main

INITIAL_TEMPLATE = [
    "______█H___█___",
    "______█N___█___",
    "______█U___█___",
    "███____T_______",
    "_______█_______",
    "____________███",
    "_______________",
    "____█TORUS█____",
    "_______________",
    "███____________",
    "_______█_______",
    "_______D____███",
    "___█___O█______",
    "___█___U█______",
    "___█___G█______",
]

f_verbose = True
f_save_best = True

ROWLEN = 15
GRIDCELLS = ROWLEN * ROWLEN
MAX_WALLS = 42

id = int(time.time())

WOR_JSON = "word_list.json"
FAI_JSON = "15x15_grid_failures_2.json"
SOL_JSON = f"15x15_grid_solutions.json"
TOP_JSON = f"results/top_solutions_{id}.json"


C_WALL = "█"

T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"

# bests
new_solutions = []  # tracks initial conditions solutions
v_best_grids = []
v_best_score = 0

with open(WOR_JSON) as f:
    WORDLIST = json.load(f)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = C_WALL + w + C_WALL

SORTED_WORDLIST = sorted(WORDLIST, key=len)  # short words first
SORTED_WORDLIST_L = sorted(SORTED_WORDLIST, key=len, reverse=True)  # long words first

import random

random.shuffle(WORDLIST)
WORDS_TO_USE = SORTED_WORDLIST_L

WORDLIST_BY_LEN = {}
for w in SORTED_WORDLIST_L:
    l = len(w)
    if l not in WORDLIST_BY_LEN:
        WORDLIST_BY_LEN[l] = []
    WORDLIST_BY_LEN[l].append(w)


def load_json(json_name):
    with open(json_name, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            out = json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return out


def append_json(json_name, grid):
    with open(json_name, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            data = json.load(f)
            data.append(grid)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def replace_char_at(string, char, index):
    """Replace a character at a specific index in a string.

    Args:
        string (str): The original string
        char (str): The character to replace with
        index (int): The index at which to replace the character

    Returns:
        str: The modified string
    """
    l = len(string)
    if index < 0:
        index += l
    if index >= l or index < 0:
        return string  # Return the original string if index is out of bounds

    return string[:index] + char + string[index + 1 :]


def add_star(grid, star):
    START = (10, 9)
    for i, line in enumerate(star):
        for j, l in enumerate(line):
            if l == "█":
                continue
            r = (START[0] + i) % ROWLEN
            c = (START[1] + j) % ROWLEN
            grid[r] = replace_char_at(grid[r], l, c)

    return grid


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "_" in l or "@" in l:
            return False
    return True


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
        # if entries the same
        # if that location is _ in the line, or if line entry is "@"
        # and the suggested letter is not letter
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


def get_new_templates_all(fixtures: list[tuple[int, str]], line: str):
    output = {i: [] for i, _ in fixtures}
    max_len = max([len(c) for c in (line + line).split(C_WALL)]) + 2  # includes 2 walls

    # possible
    for i, cont in fixtures:
        lc = len(cont)
        for (
            candidate_word
        ) in SORTED_WORDLIST_L:  # WORDLIST_BY_LEN[lc]:  # HACK: REQUIRES NO _
            lw = len(candidate_word)
            if lw > max_len or lw < lc:
                continue

            pattern = cont.replace("@", f"[^{C_WALL}]")
            matches = re.finditer(pattern, candidate_word)
            positions = [match.start() for match in matches]

            for p in positions:
                if can_word_go_there(candidate_word, line, i - p):
                    output[i].append(replace_word_at(candidate_word, line, i - p))

    return output


def get_new_templates(fixtures: list[tuple[str, int, str]], line: str) -> list[str]:
    """Get all possible new lines templates for a line given the fixtures."""
    new_tempalates = get_new_templates_all(fixtures, line)

    # return shortest item
    shortest_len = 100000000
    shortest_i = -1
    for i, v in new_tempalates.items():
        len_v = len(v)
        if len_v < shortest_len:
            shortest_len = len_v
            shortest_i = i

    return new_tempalates[shortest_i]


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
            long_string = replace_char_at(long_string, C_WALL, rvs_idx)
        elif c != "_":
            long_string = replace_char_at(long_string, "@", rvs_idx)

    return [long_string[j : j + ROWLEN] for j in range(0, GRIDCELLS, ROWLEN)]


def grid_contains_short_words(grid: list[str]) -> bool:
    for line in grid:
        if check_line_for_short_words(line):
            return True

    for line in transpose(grid):
        if check_line_for_short_words(line):
            return True
    return False


def get_fixtures(line: str):
    indices = [index for index, char in enumerate(line) if char not in ["█", "_"]]
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

    fixtures = []
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


def grid_contains_englosed_spaces(grid: list[str]) -> bool:
    # [
    #     "______█____█___",
    #     "______█____█___",
    #     "______█____█___",
    #     "███____________",
    #     "_______________",
    #     "____________███",
    #     "_______________",
    #     "HNUT█TORUS█DOUG",
    #     "_______________",
    #     "███____________",
    #     "_______________",
    #     "____________███",
    #     "___█____█______",
    #     "___█____█______",
    #     "___█____█______",
    # ]

    if C_WALL == grid[3][11] == grid[4][11]:
        return True
    if C_WALL == grid[10][3] == grid[11][3]:
        return True

    if C_WALL == grid[3][3] == grid[3][4] == grid[3][5]:
        return True
    if C_WALL == grid[11][9] == grid[11][10] == grid[11][11]:
        return True

    if C_WALL == grid[0][7] == grid[0][8] == grid[0][9] == grid[0][10]:
        return True
    if C_WALL == grid[3][7] == grid[3][8] == grid[3][9] == grid[3][10]:
        return True
    if C_WALL == grid[11][4] == grid[11][5] == grid[11][6] == grid[11][7]:
        return True
    if C_WALL == grid[14][4] == grid[14][5] == grid[14][6] == grid[14][7]:
        return True

    if C_WALL == grid[4][3] == grid[5][4] == grid[6][4] == grid[8][3]:
        return True

    if C_WALL == grid[4][2]:
        return True
    if C_WALL == grid[8][2]:
        return True

    return False


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
        candidate_lines = get_new_templates(fixtures, line)

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

            if grid_contains_short_words(candidate_grid):
                continue

            if grid_contains_englosed_spaces(candidate_grid):
                continue

            if num_walls >= MAX_WALLS:
                for j in range(ROWLEN):
                    if C_WALL in candidate_grid[j]:
                        candidate_grid[j] = candidate_grid[j].replace("_", "@")

                passes = True
                for i, line in enumerate(grid):
                    if C_WALL not in line:
                        # tqdm.tqdm.write(
                        #     f"\nGrid has max walls but ROW {i} has no black squares."
                        # )
                        # tqdm.tqdm.write(print_grid(candidate_grid, ("r", i, T_BLUE)))
                        passes = False
                        break

                for i, line in enumerate(transpose(grid)):
                    if C_WALL not in line:
                        # tqdm.tqdm.write(
                        #     f"\nGrid has max walls but COL {i} has no black squares."
                        # )
                        # tqdm.tqdm.write(print_grid(candidate_grid, ("c", i, T_BLUE)))
                        passes = False
                        break

                if not passes:
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


def transpose(grid: list[str]) -> list[str]:
    return ["".join(row) for row in zip(*grid)]


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
            print_grid[i] = replace_char_at(
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

        new_solutions.append(grid)
        append_json(SOL_JSON, grid)
        exit()
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

            if f_save_best:
                l = count_letters(grid)
                if l > v_best_score:
                    v_best_score = l
                    v_best_grids.append({"level": level, "score": l, "grid": grid})

                    with open(TOP_JSON, "w") as f:
                        json.dump(v_best_grids, f, indent=2, ensure_ascii=False)
            for new_grid in t:
                recursive_search(new_grid, level + 1)

    else:
        row_or_col, start, new_grids = get_new_grids(grid)

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

            if f_save_best:
                l = count_letters(grid)
                if l > v_best_score:
                    v_best_score = l
                    v_best_grids.append({"level": level, "score": l, "grid": grid})

                    with open(TOP_JSON, "w") as f:
                        json.dump(v_best_grids, f, indent=2, ensure_ascii=False)
            for new_grid in t:
                recursive_search(new_grid, level + 1)


if __name__ == "__main__":
    stars = load_json("star_sols.json")
    fails = load_json(FAI_JSON)

    stars_of_interest = []
    for i, star in enumerate(stars):
        grid = INITIAL_TEMPLATE.copy()
        grid = add_star(grid, star)
        if grid in fails:
            continue
        stars_of_interest.append(star)

    random.shuffle(stars_of_interest)
    ls = len(stars)
    lsoi = len(stars_of_interest)
    print()
    print(T_YELLOW + f"Starting Again: " + T_GREEN + f"{time.asctime()}" + T_NORMAL)
    print("Saving to: ", TOP_JSON)
    print()
    for i, star in enumerate(stars_of_interest):
        tqdm.tqdm.write(T_YELLOW + f"Trial {i} / {lsoi}  ({ls} tot)." + T_NORMAL)
        grid = INITIAL_TEMPLATE.copy()
        grid = add_star(grid, star)
        fails = load_json(FAI_JSON)

        if grid in fails:
            print(T_BLUE + "Already Failed - Skipping" + T_NORMAL)
            continue

        new_solutions = []
        recursive_search(grid, 0)

        if not new_solutions:
            print(T_PINK + "No solution found" + T_NORMAL)
            append_json(FAI_JSON, grid)
