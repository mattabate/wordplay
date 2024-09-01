"""optimizes script aimed just at the corners"""

import json
import time
import tqdm
from lib import (
    Direction,
    Sqaure,
    Word,
    WORDLIST_BY_LEN,
    load_json,
    append_json,
    transpose,
    replace_char_in_grid,
)


# NOTE: instead we need to do somethign where "the letter a in this position implies the letter x in this position."

f_flipped = False
f_verbose = False

if not f_flipped:
    SOL_JSON = f"star_sols.json"
    CHE_JSON = f"stars_checked.json"
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

else:
    SOL_JSON = f"star_sols_flipped.json"
    CHE_JSON = f"stars_checked_flipped.json"
    INITIAL_TEMPLATE = [
        "███@@@██████",
        "███@@@██████",
        "███@@@@@@@@@",
        "███@@@@@@@@@",
        "███@@@@@@@@@",
        "@@@@@@@@@███",
        "@@@@@@@@@███",
        "@@@@@@@@@███",
        "██████@@@███",
        "██████@@@███",
    ]

ROWS_OF_INTEREST = [2, 3, 4, 5, 6, 7]
COLS_OF_INTEREST = [3, 4, 5, 6, 7, 8]

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


v_best_score = 0
v_best_grids = []


def find_first_letter(input_string):
    l = len(input_string)
    non_c_wall_index = l - len(input_string.lstrip(C_WALL))
    return non_c_wall_index if non_c_wall_index != l else -1


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
        x_start, y_start = w.start
        new_possibilities = ""
        match w.direction:
            case Direction.ACROSS:
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
            filled_grid = replace_char_in_grid(
                filled_grid, s, list(v.possible_chars)[0]
            )
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
        replace_char_in_grid(filled_grid.copy(), min_square, p)
        for p in square_to_word_map[min_square].possible_chars
    ]
    return output


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "@" in l:
            return False
    return True


def recursive_search(grid, level=0):
    global v_best_score
    global v_best_grids

    if f_verbose:
        print(json.dumps(grid, indent=2, ensure_ascii=False))
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

        solutions = load_json(SOL_JSON)
        if grid not in solutions:
            append_json(SOL_JSON, grid)
        return

    new_grids = get_new_grids(grid)

    if not new_grids:
        return

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
        print(f"{i}/{len_wln}", "Seed word:", seed)
        already_checked = load_json(CHE_JSON)
        if seed in already_checked:
            print(T_GREEN + "Already checked" + T_NORMAL)
            continue
        grid = INITIAL_TEMPLATE.copy()
        if not f_flipped:
            grid[3] = seed + "███"
        else:
            grid[3] = "███" + seed

        for seed2 in tqdm.tqdm(words_9_letter):
            if not f_flipped:
                grid[4] = seed2 + "███"
            else:
                grid[4] = "███" + seed2

            recursive_search(grid, 0)

        append_json(CHE_JSON, seed)
