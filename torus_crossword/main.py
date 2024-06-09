import json
import time
import re
import tqdm 

ROWLEN = 15
SOLUTIONS = []
C_WALL = "█"
MAX_WALLS = 40



T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"

with open("words.json") as f:
    WORDLIST = json.load(f)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = C_WALL + w + C_WALL


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "_" in l or "@" in l:
            return False
    return True

def char_is_letter(c: str) -> bool:
    if len(c) != 1:
        raise ValueError("Input must be a single character")
    return c in "@ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def replace_char_at(string, char, index):
    """Replace a character at a specific index in a string.
    
    Args:
        string (str): The original string
        char (str): The character to replace with
        index (int): The index at which to replace the character
        
    Returns:
        str: The modified string
    """
    if index < 0:
        index += len(string)
    if index >= len(string) or index < 0:
        return string  # Return the original string if index is out of bounds
    return string[:index] + char + string[index + 1 :]


def check_line_for_short_words(line: str) -> bool:
    """Check if there are any one or two letter words in the line."""
    # Combine both patterns into one
    if bool(re.search(r"█[A-Za-z@]█|█[A-Za-z@]{2}█", 2 * line)):
        return True
    return False

def check_grid_for_short_words(grid: list[str]) -> bool:
    """Check if there are any one or two letter words in the line."""
    transpose = ["".join(row[i] for row in grid) for i in range(ROWLEN)]
    for g in [grid, transpose]:
        for l in g:
            if check_line_for_short_words(l):
                return True  
    return False

def check_grid(grid: list[str]) -> bool:
    # ensure not to many walls
    long_string = "".join(grid)
    if long_string.count(C_WALL) > MAX_WALLS:
        return False

    # ensure not one or two letter words
    if check_grid_for_short_words(grid):
        return False     
           

    return True


def word_islands_indexes(line: str) -> list[list[int]]:
    """with wrapping"""
    """
    Example: "a█bb___ab_c@█@█" -> [(7, 'ab'), (10, 'c@█@█a█bb')]
    """
    if "_" not in line:
        # HACK: must exit here since no _ means no starting index for word islands
        return []

    qm_positions = [index for index, char in enumerate(line) if char == "_"]
    qm_positions.append(ROWLEN)

    # looks like: [[5, 6], [8, 9, 10], [13, 14, 15, 16, 17]]
    word_islands: list[int] = []
    for i in range(len(qm_positions) - 1):
        in_between = list(range(qm_positions[i] + 1, qm_positions[i + 1]))
        if in_between:
            word_islands.append(in_between)

    wrap = line.find("_")
    if wrap:
        if not word_islands:
            word_islands = [[]]
        word_islands[-1].extend([ROWLEN + i for i in range(wrap)])

    sub_strings = []
    for li in word_islands:
        word = "".join(line[c % ROWLEN] for c in li)
        sub_strings.append(
            (
                li[0],
                word,
            )
        )

    return sub_strings


def word_fixtures(sub_strings: list[tuple[int, str]]) -> list[tuple[str, int, str]]:
    word_fixtures = []
    for i, s in sub_strings:  # starting index, word
        periods = s.split(C_WALL)

        if len(periods) == 1:
            # if no periods
            word_fixtures.append(("substring", i, s))
            continue

        if periods[0]:
            word_fixtures.append(("suffix", i, periods[0] + C_WALL))

        if periods[-1]:
            word_fixtures.append(
                ("prefix", i + len(s) - len(periods[-1]) - 1, C_WALL + periods[-1])
            )

        spots = [j for j, c in enumerate(s) if c == C_WALL]

        for j in range(1, len(periods) - 1):
            if "@" in periods[j]:
                word_fixtures.append(
                    ("infix", i + spots[j - 1], C_WALL + periods[j] + C_WALL)
                )

    return word_fixtures


def get_new_templates_all(fixtures: list[tuple[str, int, str]], line: str):
    new_templates = {i:[] for _, i, _ in fixtures}
    max_len = max([len(c) for c in (line+line).split(C_WALL)]) + 2

    for w in WORDLIST:
        if len(w) > max_len:
            continue
        for _, i, cont in fixtures:
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
                    if check_line_for_short_words(new_template):
                        continue
                    new_template = new_template.replace(f'{C_WALL}_{C_WALL}', 3*C_WALL).replace(f'{C_WALL}__{C_WALL}', 4*C_WALL)
                    new_templates[i].append(new_template)

    return new_templates
                        

            
def get_new_templates(fixtures: list[tuple[str, int, str]], line: str) -> list[str]:
    """Get all possible new lines templates for a line given the fixtures."""
    new_tempalates = get_new_templates_all(fixtures, line)
    # return shortest item
    shortest_len = 100000000
    shortest = []
    for _, v in new_tempalates.items():
        if len(v) < shortest_len:
            shortest_len = len(v)
            shortest = v 

    return shortest



def get_best_row(grid: list[str]) -> tuple[int, int, list[list[str]]]:
    K_INDEX = -1
    K_BEST_SCORE = 1000000000
    K_BEST_GRIDS = []
    
    for i in range(ROWLEN):
        # for each line
        line = grid[i]
        if not ("@" in line or "_" in line):
            # this line cant fit any more words
            continue 
        if not any(c not in ["█", "_"] for c in line):
            # this line only contains █ and _ so we cant latch anywhere
            continue

        sub_strings = word_islands_indexes(line)
        fixtures = word_fixtures(sub_strings)
        # TODO: look here
        if not fixtures:
            continue
        new_tempalates = get_new_templates(fixtures, line)
        if not new_tempalates:
            return i, 0, []
        
        # TODO: DO THIS WITHOUT COMPUTING GRIDS EXPLICITLY
        new_grids : list[list[str]]= []
        for l in new_tempalates:
            temp = grid.copy()
            temp[i] = l # make line word from options

            long_string = "".join(temp)
            for j, c in enumerate(long_string):
                if c == C_WALL:
                    long_string = replace_char_at(long_string, C_WALL, len(long_string) - 1 - j)
                elif char_is_letter(c) and long_string[len(long_string) - 1 - j] == "_" :
                    long_string = replace_char_at(long_string, "@", len(long_string) - 1 - j)

            temp = [long_string[j:j+ROWLEN] for j in range(0, len(long_string), ROWLEN)]

            if check_grid(temp):
                new_grids.append(temp)

        if len(new_grids) < K_BEST_SCORE:
            K_INDEX = i
            K_BEST_GRIDS = new_grids
            K_BEST_SCORE = len(new_grids)

    return K_INDEX, K_BEST_SCORE, K_BEST_GRIDS


def transpose(grid: list[str]) -> list[str]:
    return ["".join(row[i] for row in grid) for i in range(ROWLEN)]


def get_new_grids(grid: list[str])->tuple[int, list[list[str]]]:
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
                print_grid[i], 
                h_color + print_grid[i][h[1]] + BACKGROUND, h[1]
            )

    return "\n".join(print_grid) + T_NORMAL


def recursive_search(grid, level=0):
    if grid_filled(grid):
        tqdm.tqdm.write("\033[92mSolution found")  # Green text indicating success
        tqdm.tqdm.write(json.dumps(grid, indent=2, ensure_ascii=False))
        tqdm.tqdm.write("\033[0m")
        SOLUTIONS.append(grid)
        with open("solutions.json", "w", encoding='utf-8') as f:
            json.dump(SOLUTIONS, f, indent=2, ensure_ascii=False)
        return
    
    x, idx_str, new_grids = get_new_grids(grid)
    if not new_grids:
        out1 = f"\nNo possibilities ROW {idx_str}" if x == "r" else f"\nNo possibilities COL {idx_str}"
        tqdm.tqdm.write(out1)
        tqdm.tqdm.write(print_grid(grid, (x, idx_str, T_PINK)))
        return
    
    out2 = f"\nTesting {len(new_grids)} possibilities for ROW {idx_str}" if x == "r" else f"\nTesting {len(new_grids)} possibilities for COL {idx_str}"
    tqdm.tqdm.write(out2)
    tqdm.tqdm.write(print_grid(grid, (x, idx_str, T_GREEN)  ))
    
    with tqdm.tqdm(new_grids, desc=f"Level {level}") as t:
        for new_grid in t:
            recursive_search(new_grid, level + 1)


if __name__ == "__main__":
    INITIAL_TEMPLATE = [
        "_______I_______",
        "_______D_______",
        "_______A_______",
        "_______L_______",
        "_______█_______",
        "_______G_______",
        "ECORE█RING█APPL",
        "IDAL█TORUS█TORO",
        "TUBE█HOLE█INNER",
        "_______S_______",
        "_______█_______",
        "_______P_______",
        "_______O_______",
        "_______L_______",
        "_______O_______"
    ]

    with open("fails.json", "r") as f:
        data = json.load(f)
        if INITIAL_TEMPLATE in data:
            print("already failed")
            exit()

    t0 = time.time()

    grid = INITIAL_TEMPLATE.copy()


    recursive_search(grid, 0)
    