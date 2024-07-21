import json
from schema import Direction, Sqaure, Word, WORDLIST_BY_LEN
import time

# NOTE: instead we need to do somethign where "the letter a in this position implies the letter x in this position."
id = int(time.time())
BES_JSON = f"results/bests_{id}.json"
SOL_JSON = f"solutions/solutions_{id}.json"
FAI_JSON = "fails.json"

INITIAL_TEMPLATE = [
    "██████@@@███",
    "██████@@@███",
    "@@@@@@@@@███",
    "@@@@@@@@@███",
    "@@@@@@@@@███",
    "███@@@@@@@@@",
    "███@@@@@@@@@",
    "███@@@@@@@@@",
    "███@@@██████",
    "███@@@██████",
]


# INITIAL_TEMPLATE = [
#     "███@@@██████",
#     "███@@@██████",
#     "███@@@@@@@@@",
#     "███@@@@@@@@@",
#     "███@@@@@@@@@",
#     "@@@@@@@@@███",
#     "@@@@@@@@@███",
#     "@@@@@@@@@███",
#     "██████@@@███",
#     "██████@@@███",
# ]

ROWLEN = len(INITIAL_TEMPLATE[0])
COLLEN = len(INITIAL_TEMPLATE)
GRIDCELLS = ROWLEN * COLLEN

C_WALL = "█"

letter_locs = [
    (r, c)
    for r in range(len(INITIAL_TEMPLATE))
    for c in range(len(INITIAL_TEMPLATE[0]))
    if INITIAL_TEMPLATE[r][c] != C_WALL
]


T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"

ROWS_OF_INTEREST = [2, 3, 4, 5, 6, 7]
COLS_OF_INTEREST = [3, 4, 5, 6, 7, 8]


v_best_score = 0
v_best_grids = []
solutions = []


def transpose(grid):
    return ["".join(x) for x in zip(*grid)]


def find_first_letter(input_string):
    for i, char in enumerate(input_string):
        if char != C_WALL:
            return i
    return -1


def find_last_letter(input_string):
    for i, char in enumerate(input_string[::-1]):
        if char != C_WALL:
            return len(input_string) - i - 1
    return


def get_word_locations(grid: list[list[str]], direction: Direction) -> list[Word]:
    words = []
    if direction == Direction.ACROSS:
        for r in ROWS_OF_INTEREST:
            if not "@" in grid[r]:
                continue
            words.append(
                Word(
                    direction=Direction.ACROSS,
                    start=(r, find_first_letter(grid[r])),
                    length=len([s for s in grid[r] if s != C_WALL]),
                )
            )
    else:
        it_t = transpose(grid)
        for c in COLS_OF_INTEREST:
            if "@" in it_t[c]:
                if not "@" in it_t[c]:
                    continue

                words.append(
                    Word(
                        direction=Direction.DOWN,
                        start=(find_first_letter(it_t[c]), c),
                        length=len([s for s in it_t[c] if s != C_WALL]),
                    )
                )
    return words


def initalize(grid):
    # NOTE: initialize words
    words = get_word_locations(grid, Direction.ACROSS) + get_word_locations(
        grid, Direction.DOWN
    )

    # NOTE: initialize square_to_word_map
    square_to_word_map: dict[list[tuple[int, int]], Sqaure] = {}
    for i, j in letter_locs:
        letter = grid[i][j]
        square_to_word_map[(i, j)] = Sqaure(None, None)
        if letter != "@":
            square_to_word_map[(i, j)].possible_chars = {letter}

    for wid, w in enumerate(words):
        x_start, y_start = w.start
        if w.direction == Direction.ACROSS:
            for i in range(w.length):
                square_to_word_map[(x_start, (y_start + i))].across = (wid, i)
        elif w.direction == Direction.DOWN:
            for i in range(w.length):
                square_to_word_map[((x_start + i), y_start)].down = (wid, i)

    return words, square_to_word_map


# NOTE: pass on the word for each square and possibilities to use as initial condidtions
# DONE
def update_square_possibilities(
    square_to_word_map: dict[tuple[int, int], Sqaure], words: list[Word]
) -> dict[tuple[int, int], Sqaure]:
    for s in square_to_word_map.values():
        if s.across:
            across: Word = s.across
            word = words[across[0]]
            spot = across[1]
            accross_pos = {p[spot] for p in word.possibilities}
        else:
            accross_pos = set(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        if not s.down:
            s.possible_chars = accross_pos
            continue

        down = s.down
        word = words[down[0]]
        spot = down[1]
        down_pos = {p[spot] for p in word.possibilities}

        pos = accross_pos.intersection(down_pos)

        s.possible_chars = pos

    return square_to_word_map


# DONE
def update_word_possibilities(
    words: list[Word], square_to_word_map: dict[tuple[int, int], Sqaure]
) -> list[Word]:
    for w in words:
        new_possibilities = []
        x_start, y_start = w.start
        match w.direction:
            case Direction.ACROSS:
                new_possibilities = ""
                for p in w.possibilities:
                    for i, c in enumerate(p):
                        if (
                            c
                            not in square_to_word_map[
                                (x_start, (y_start + i))
                            ].possible_chars
                        ):
                            break
                    else:
                        new_possibilities += "," + p
            case Direction.DOWN:
                new_possibilities = ""
                for p in w.possibilities:
                    for i, c in enumerate(p):
                        if (
                            c
                            not in square_to_word_map[
                                ((x_start + i), y_start)
                            ].possible_chars
                        ):
                            break
                    else:
                        new_possibilities += "," + p

        w.possibilities = new_possibilities.split(",")[1:]

    return words


# DONE
def get_new_grids(
    grid: list[str],
) -> list[list[str]]:

    words, square_to_word_map = initalize(grid)

    old_vector = [len(w.possibilities) for w in words]

    while True:

        words = update_word_possibilities(words, square_to_word_map)
        new_vector = [len(w.possibilities) for w in words]
        if old_vector == new_vector:
            # when the number of possibilities can no longer be reduced
            break
        old_vector = new_vector
        # BUG: square_to_word_map have both across and down : (29, 5) (50, 2)
        square_to_word_map = update_square_possibilities(square_to_word_map, words)

        # if the square has no possibilities, return no grids
        dead_ends = [
            True for square in square_to_word_map.values() if square.possible_chars
        ]
        if not dead_ends:
            return []

    # get square with min possibilities, not including 1
    min_possibilities = 27
    min_square = None
    filled_grid = grid.copy()
    for s, v in square_to_word_map.items():
        if len(v.possible_chars) == 1:
            # NOTE: fill in all squares with only one possibility
            filled_grid = replace_char_at(filled_grid, s, list(v.possible_chars)[0])
            continue

        # NOTE: find the square with the fewest possibilities otherwise
        num_pos = len(v.possible_chars)
        if num_pos < min_possibilities:
            min_possibilities = num_pos
            min_square = s

    if not min_square:
        return [filled_grid]

    # TODO: make min square to influence
    output = [
        replace_char_at(filled_grid.copy(), min_square, p)
        for p in square_to_word_map[min_square].possible_chars
    ]
    return output


# DONE
def replace_char_at(grid: list[str], loc: tuple[int, int], c: str) -> list[str]:
    """Replace the character at the given location in the grid."""
    row = grid[loc[0]]
    grid[loc[0]] = f"{row[:loc[1]]}{c}{row[loc[1]+1:]}"
    return grid


def count_letters(grid: list[str]) -> int:
    return GRIDCELLS - sum(line.count("@") + line.count("█") for line in grid)


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "@" in l:
            return False
    return True


def recursive_search(grid, level=0):
    global v_best_score
    global v_best_grids
    global solutions

    if grid_filled(grid):
        # check to make sure rows of interest are valie words
        for r in ROWS_OF_INTEREST:
            candidate = grid[r].replace("█", "")
            if candidate not in WORDLIST_BY_LEN[len(candidate)]:
                return

        for c in COLS_OF_INTEREST:
            candidate = "".join([grid[r][c] for r in range(COLLEN)]).replace("█", "")
            if candidate not in WORDLIST_BY_LEN[len(candidate)]:
                return

        print("Solution found")  # Green text indicating success
        solutions.append({"level": level, "grid": grid})
        with open(SOL_JSON, "w") as f:
            json.dump(solutions, f, indent=2, ensure_ascii=False)

        return

    new_grids = get_new_grids(grid)

    if not new_grids:
        return

    l = count_letters(grid)
    if l > v_best_score:
        v_best_score = l
        v_best_grids.append({"level": level, "score": l, "grid": grid})

        with open(BES_JSON, "w") as f:
            json.dump(v_best_grids, f, indent=2, ensure_ascii=False)

    for new_grid in new_grids:
        recursive_search(new_grid.copy(), level + 1)


if __name__ == "__main__":
    words = get_word_locations(INITIAL_TEMPLATE, Direction.ACROSS) + get_word_locations(
        INITIAL_TEMPLATE, Direction.DOWN
    )

    print("number of answers", len(words))
    print(
        "number of black squares",
        "".join(INITIAL_TEMPLATE).count(C_WALL),
        T_NORMAL,
    )

    words_9_letter = WORDLIST_BY_LEN[9]
    len_wln = len(words_9_letter)
    t0 = time.time()
    for i, seed in enumerate(words_9_letter):
        current_time = round(time.time() - t0)
        time_remaining = round(current_time / (i + 1) * (len_wln - i))
        current_time = time.strftime("%H:%M:%S", time.gmtime(current_time))
        time_remaining = time.strftime("%H:%M:%S", time.gmtime(time_remaining))
        print(
            f"{i}/{len_wln}",
            "Seed word:",
            seed,
            "current time:",
            current_time,
            "time remaining:",
            time_remaining,
        )
        grid = INITIAL_TEMPLATE.copy()
        grid[2] = seed + "███"

        recursive_search(grid, 0)