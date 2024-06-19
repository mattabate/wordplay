import json
import time
import re
import tqdm
import os


INITIAL_TEMPLATE = [
    "█@@@@_█@@@@█@@@",
    "DTCAKE█@@@@█BUN",
    "@@@@@@_@@@@_@@@",
    "@@@____________",
    "███____________",
    "@@@____________",
    "@@@____________",
    "HNUT█TORUS█DOUG",
    "____________@@@",
    "____________@@@",
    "____________███",
    "____________@@@",
    "@@@_@@@@_@@@@@@",
    "UBE█@@@@█INNERT",
    "@@@█@@@@█_@@@@█",
]

f_allow_edge_small_words = False
only_corners = False

ROWLEN = 15
GRIDCELLS = ROWLEN * ROWLEN
MAX_WALLS = 42

SOL_JSON = "solutions1.json"
BES_JSON = "bests1.json"
WOR_JSON = "words.json"
FAI_JSON = "fails.json"

C_WALL = "█"

T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"

if os.path.exists(SOL_JSON):
    with open(SOL_JSON) as f:
        SOLUTIONS = json.load(f)
else:
    SOLUTIONS = []

# bests
v_best_score = 0
v_best_grids = []

with open(WOR_JSON) as f:
    WORDLIST = json.load(f)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = C_WALL + w + C_WALL

SORTED_WORDLIST = sorted(WORDLIST, key=len)  # short words first
SORTED_WORDLIST_L = sorted(SORTED_WORDLIST, key=len, reverse=True)  # long words first

import random

random.shuffle(WORDLIST)
WORDS_TO_USE = WORDLIST


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "_" in l or "@" in l:
            return False
    return True


def count_letters(grid: list[str], only_corners=False) -> int:
    if only_corners:
        _sum = 0
        for i in [0, 1, 2, 3, 11, 12, 13, 14]:
            _sum += grid[i].count("_") + grid[i].count("@") + grid[i].count("█")
        return 120 - _sum
    else:
        return GRIDCELLS - sum(
            [l.count("_") + l.count("@") + l.count("█") for l in grid]
        )


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


def check_line_for_short_words(line: str) -> bool:
    """Check if there are any one or two letter words in the line."""
    m = line.split(C_WALL)
    for word in m:
        if len(word) in [1, 2] and any(c.isalpha() or c == "@" for c in word):
            return True
    return False


def can_letter_go_there(letter: str, line: str, pos) -> bool:
    line_entry = line[pos]
    if line_entry in [letter, "_"]:
        # if entries the same
        return True
    if line_entry == "@" and letter != C_WALL:
        # if that location is _ in the line, or if line entry is "@"
        # and the suggested letter is not letter
        return True
    return False


def can_word_go_there(word: str, line: str, pos) -> bool:
    for j, suggested_letter in enumerate(word):  # suggested letter
        if not can_letter_go_there(suggested_letter, line, pos=(pos + j) % ROWLEN):
            return False
    return True


def replace_word_at(word: str, line: str, start_idx: int) -> str:
    new_template = line
    for j, suggested_letter in enumerate(word):
        new_template = replace_char_at(
            new_template, suggested_letter, (start_idx + j) % ROWLEN
        )
    return new_template


def get_new_templates_all(fixtures: list[tuple[int, str]], line: str):
    output = {i: [] for i, _ in fixtures}
    max_len = max([len(c) for c in (line + line).split(C_WALL)]) + 2

    # possible
    for w in WORDS_TO_USE:
        lw = len(w)
        if lw > max_len:
            continue
        for i, cont in fixtures:
            if len(cont) > lw:
                continue
            pattern = cont.replace("@", f"[^{C_WALL}]")
            matches = re.finditer(pattern, w)
            positions = [match.start() for match in matches]
            for p in positions:
                if can_word_go_there(w, line, i - p):
                    output[i].append(replace_word_at(w, line, i - p))

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
    if not f_allow_edge_small_words:
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
    tr = transpose(grid)
    # NOTE: This ensures no short words

    if f_allow_edge_small_words:
        g_val = "@@@".join(
            l + l for l in grid
        )  # double the lines, and then join and create long string
        t_val = "@@@".join(l + l for l in tr)
        search_string = g_val + "@@@" + t_val
        bites = search_string.split(C_WALL)

        for word in bites[1:-1]:
            if len(word) in [1, 2] and any(c.isalpha() or c == "@" for c in word):
                return True
    else:
        rows_split = [l.split(C_WALL) for l in grid]
        cols_split = [l.split(C_WALL) for l in tr]

        for word in rows_split:
            if len(word) in [1, 2] and any(c.isalpha() or c == "@" for c in word):
                return True
        for word in cols_split:
            if len(word) in [1, 2] and any(c.isalpha() or c == "@" for c in word):
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


def get_best_row(grid: list[str]) -> tuple[int, int, list[list[str]]]:
    K_INDEX = -1
    K_BEST_SCORE = 1000000000
    K_BEST_GRIDS = []

    for i in range(ROWLEN):
        # for every row, compute the latch with the fewest fitting words

        # for each line
        line = grid[i]
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
            return i, 0, []

        # TODO: DO THIS WITHOUT COMPUTING GRIDS EXPLICITLY
        # now that you have the words that fit, do any lead to a trvially bad grid?
        working_grids: list[list[str]] = []
        m = 0
        for l in candidate_lines:
            candidate_grid = grid.copy()
            candidate_grid[i] = l  # make line word from options

            if any(check_line_for_short_words(l) for l in candidate_grid):
                continue
            if any(check_line_for_short_words(l) for l in transpose(candidate_grid)):
                continue

            candidate_grid = enforce_symmetry(candidate_grid)
            candidate_grid = fill_in_small_holes(candidate_grid)

            # NOTE: This ensures not to many walls
            if "".join(candidate_grid).count(C_WALL) > MAX_WALLS:
                continue

            if grid_contains_short_words(candidate_grid):
                continue

            working_grids.append(candidate_grid)
            m += 1
            if m > K_BEST_SCORE:
                break
        else:
            K_INDEX = i
            K_BEST_GRIDS = working_grids
            K_BEST_SCORE = m

    # candidate_grid = [long_string[j:j+ROWLEN] for j in range(0, len(long_string), ROWLEN)]
    return K_INDEX, K_BEST_SCORE, K_BEST_GRIDS


def transpose(grid: list[str]) -> list[str]:
    return ["".join(row) for row in zip(*grid)]


def get_new_grids(grid: list[str]) -> tuple[int, list[list[str]]]:
    """Given a grid, find the best row or column to latch on to."""
    # find the best row to latch on
    row_idx, best_row_score, best_row_grids = get_best_row(grid)
    # transpose to find the best collum
    grid_transposed = transpose(grid)
    col_idx, best_col_score, best_col_grids = get_best_row(grid_transposed)

    # TODO: SOMETHING WRONG HERE???
    if best_row_score < best_col_score:
        return "r", row_idx, best_row_grids
    else:
        # transform back all of the column grids
        transposed_col_grids = []
        for g in best_col_grids:
            transposed_col_grids.append(transpose(g))
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
    global v_best_score
    global v_best_grids

    if grid_filled(grid):
        tqdm.tqdm.write(T_YELLOW + "Solution found")  # Green text indicating success
        tqdm.tqdm.write(json.dumps(grid, indent=2, ensure_ascii=False))
        tqdm.tqdm.write(T_NORMAL)
        tqdm.tqdm.write(
            json.dumps(
                T_YELLOW + INITIAL_TEMPLATE + T_NORMAL, indent=2, ensure_ascii=False
            )
        )

        SOLUTIONS.append(grid)
        with open(SOL_JSON, "w", encoding="utf-8") as f:
            json.dump(SOLUTIONS, f, indent=2, ensure_ascii=False)
        return

    x, idx_str, new_grids = get_new_grids(grid)
    len_new_grids = len(new_grids)
    if not new_grids:
        out1 = (
            f"\nNo possibilities ROW {idx_str}"
            if x == "r"
            else f"\nNo possibilities COL {idx_str}"
        )
        tqdm.tqdm.write(out1)
        tqdm.tqdm.write(print_grid(grid, (x, idx_str, T_PINK)))

        return

    with tqdm.tqdm(new_grids, desc=f"Level {level}") as t:
        out2 = (
            f"\nTesting {len_new_grids} possibilities for ROW {idx_str}"
            if x == "r"
            else f"\nTesting {len_new_grids} possibilities for COL {idx_str}"
        )
        tqdm.tqdm.write(out2)
        tqdm.tqdm.write(print_grid(grid, (x, idx_str, T_GREEN)))

        # words = []
        # for i, new_grid in enumerate(t):
        #     if x == "r":
        #         words.append(new_grid[idx_str])
        #     else:
        #         words.append("".join([l[idx_str] for l in new_grid]))

        # tqdm.tqdm.write("\n".join(words))
        for new_grid in t:
            l = count_letters(new_grid, only_corners=only_corners)
            if l > v_best_score:
                v_best_score = l
                v_best_grids.append(
                    {
                        "level": level,
                        "score": l,
                        "grid": new_grid,
                        "parrent": grid,
                    }
                )
                with open(BES_JSON, "w") as f:
                    json.dump(v_best_grids, f, indent=2, ensure_ascii=False)

            recursive_search(new_grid, level + 1)


if __name__ == "__main__":
    global solution_found

    with open(FAI_JSON) as f:
        fails = json.load(f)
    if INITIAL_TEMPLATE in fails:
        print(f"This grid has already been proven to have no solution.")
        exit()

    grid = INITIAL_TEMPLATE.copy()

    solution_found = False
    recursive_search(grid, 0)

    if not solution_found:
        print("No solution found")
        with open(FAI_JSON, "w") as f:
            fails.append(INITIAL_TEMPLATE)
            json.dump(fails, f, indent=2, ensure_ascii=False)

        print(
            T_PINK
            + json.dumps(INITIAL_TEMPLATE, indent=2, ensure_ascii=False)
            + T_NORMAL
        )


# 15
# @@@___█_@@_█POC
# ONRING█_@@_█ONI
# @@@@@@__@@__SIA
# ███________@ES█
# AKE█____█BUNDTC
# ROSS█______███H
# MASS█____@@A██A
# HNUT█TORUS█DOUG
# O██S@@____█ANDR
# L███______█REOI
# ERTUBE█____█INN
# █@@@________███
# @@@__@@__@@@SUA
# HIE█_@@_█SCRUNC
# @@@█_@@_█___PIA

# Almost best
# [
#     "T I N████@@@██SIW",
#     "E R TUBE█@@@██INN",
#     "R E STED█@@@█INTE",
#     "███ E A S Y T H E R E █ █ █ ",
#     "___N@H@__█@D@__",
#     "@@@S@E@█@M@█@@@",
#     "@@@I@E█__I█R@@@",
#     "___L@R___SKI___",
#     "EADS█A__█SIGHTR",
#     "LLS█@N@█STRAWPO",
#     "__@A@█__@OST___",
#     "███ INORDERTO███",
#     "R O AD█@@@█SENTAB",
#     "I N G██@@@█ONIONR",
#     "T H E██@@@████SOO",
# ]
