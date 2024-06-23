import json
import time
import re
import tqdm
import os

ROWLEN = 15
GRIDCELLS = ROWLEN * ROWLEN
MAX_WALLS = 46

C_WALL = "█"


T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"

SOL_JSON = "solutions_rec.json"
BES_JSON = "bests_rec.json"

if os.path.exists(SOL_JSON):
    with open(SOL_JSON) as f:
        SOLUTIONS = json.load(f)
else:
    SOLUTIONS = []

# bests
v_best_score = 0
v_best_grids = []

f_allow_edge_small_words = False


with open("words.json") as f:
    WORDLIST = json.load(f)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = C_WALL + w + C_WALL

# sort short words first
SORTED_WORDLIST = sorted(WORDLIST, key=len)
# sort long words first
SORTED_WORDLIST_L = sorted(SORTED_WORDLIST, key=len, reverse=True)


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "_" in l or "@" in l:
            return False
    return True


def count_letters(grid: list[str]) -> int:
    return GRIDCELLS - sum([l.count("_") + l.count("@") + l.count("█") for l in grid])


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


def get_new_templates_all(fixtures: list[tuple[int, str]], line: str):
    new_templates = {i: [] for i, _ in fixtures}
    max_len = max([len(c) for c in (line + line).split(C_WALL)]) + 2

    # possible
    for w in SORTED_WORDLIST_L:
        lw = len(w)
        if lw > max_len:
            continue
        for i, cont in fixtures:
            mil_len = len(cont)
            if mil_len > lw:
                continue
            pattern = cont.replace("@", f"[^{C_WALL}]")
            matches = re.finditer(pattern, w)
            positions = [match.start() for match in matches]
            for p in positions:
                new_template = line
                for j, c in enumerate(w):
                    ooo = (i - p + j) % ROWLEN
                    if line[ooo] in [c, "_"] or (line[ooo] == "@" and c != C_WALL):
                        new_template = replace_char_at(new_template, c, ooo)
                        continue
                    break
                else:
                    new_templates[i].append(new_template)

    return new_templates


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
        elif c in "@ABCDEFGHIJKLMNOPQRSTUVWXYZ":
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


def filter_lines_by_size(i, lines: list[str], grid: str) -> list[str]:
    """i is row"""
    # TODO: probably way to do this involves computing words that can fit on both lines

    if i in [1, 2]:
        zz = []
        for j, q in enumerate(zip(grid[0], grid[1])):
            c1, c2 = q
            if c1 not in "█_" or c2 not in "█_":
                zz.append(j)

        filtered = []
        for l in lines:
            for z in zz:
                if l[z] == "█":
                    break
            else:
                filtered.append(l)
        lines = filtered

    if i in [ROWLEN - 2, ROWLEN - 3]:
        zz = []
        for j, q in enumerate(zip(grid[ROWLEN - 1], grid[ROWLEN - 2])):
            c1, c2 = q
            if c1 not in "█_" or c2 not in "█_":
                zz.append(j)

        filtered = []
        for l in lines:
            for z in zz:
                if l[z] == "█":
                    break
            else:
                filtered.append(l)
        lines = filtered

    filtered = []
    for l in lines:
        if (l[1] == "█" or l[2] == "█") and not (l[0] in "_█" and l[1] in "_█"):
            continue
        if (l[-2] == "█" or l[-3] == "█") and not (l[-1] in "_█" and l[-2] in "_█"):
            continue
        filtered.append(l)
    lines = filtered

    return lines


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
        candidate_lines = filter_lines_by_size(i, candidate_lines, grid)

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

            tr = transpose(candidate_grid)
            if any(check_line_for_short_words(l) for l in candidate_grid):
                continue
            if any(check_line_for_short_words(l) for l in tr):
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

        for new_grid in t:
            l = count_letters(new_grid)
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

    initial_template = [
        "@@@___█_@@_█@@@",
        "@@@@@@█_@@_█@@@",
        "@@@@@@█_@@_@@@@",
        "███_________███",
        "_______________",
        "_______________",
        "_______________",
        "____█_____█____",
        "_______________",
        "_______________",
        "_______________",
        "███_________███",
        "@@@@_@@__@@@@@@",
        "@@@█_@@_█@@@@@@",
        "@@@█_@@_█___@@@",
    ]

    # thing = ["█INNERTUBE█", "█SCRUNCHIE█", "█BUNDTCAKE█", "█ONIONRING█"]
    # thing = ["█SCRUNCHIE█", "█INNERTUBE█", "█BUNDTCAKE█", "█ONIONRING█"]
    # thing = ["█BUNDTCAKE█", "█INNERTUBE█", "█SCRUNCHIE█", "█ONIONRING█"]
    # thing = ["█INNERTUBE█", "█BUNDTCAKE█", "█SCRUNCHIE█", "█ONIONRING█"]
    thing = ["█SCRUNCHIE█", "█ONIONRING█", "█BUNDTCAKE█", "█INNERTUBE█"]

    import itertools

    # combinations = list(itertools.permutations(thing))
    # combinations of len 2
    combinations = list(itertools.combinations(thing, 2))

    for j, t in enumerate(combinations):
        words = [
            (t[0], "r", 0, 11),
            (t[1], "r", 14, 8),
            # (t[1], "r", 4, 8),
            # (t[2], "r", 10, 11)
        ]

        # words = [
        #     (t[0], "r", 3, 10),  # row, start
        #     (t[1], "c", 8, 5),  # col, start
        #     (t[2], "r", 11, 9),
        #     (t[3], "c", 11, 9),
        # ]

        for w, d, rw, cl in words:
            if d == "r":
                for i, c in enumerate(w):
                    initial_template[rw] = replace_char_at(
                        initial_template[rw], c, (cl + i) % ROWLEN
                    )
            if d == "c":
                for i, c in enumerate(w):
                    initial_template[(rw + i) % ROWLEN] = replace_char_at(
                        initial_template[(rw + i) % ROWLEN], c, cl
                    )

        INITIAL_TEMPLATE = initial_template

        with open("fails.json") as f:
            fails = json.load(f)
        if INITIAL_TEMPLATE in fails:
            print(
                f"{j}/{len(combinations)} This grid has already been proven to have no solution."
            )
            continue

        grid = INITIAL_TEMPLATE.copy()

        solution_found = False
        recursive_search(grid, 0)

        if not solution_found:
            print("No solution found")
            with open("fails.json", "w") as f:
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