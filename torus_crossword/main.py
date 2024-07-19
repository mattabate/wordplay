import json
import tqdm
from schema import Direction, Sqaure, Word
import time
import itertools

# NOTE: instead we need to do somethign where "the letter a in this position implies the letter x in this position."


# clear that grid for me
INITIAL_TEMPLATE = [
    "@@@█@@@█@@@@@@@",
    "@@@█@@@█@@@@@@@",
    "@@@█@@@█@@@@@@@",
    "@@@@@@@█@@@████",
    "███@@@@@@@█@@@@",
    "@@@@@@█@@@█@@@@",
    "@@@@@█@@@@█@@@@",
    "@@@@█TORUS█@@@@",
    "@@@@█@@@@█@@@@@",
    "@@@@█@@@█@@@@@@",
    "@@@@█@@@@@@@███",
    "████@@@█@@@@@@@",
    "@@@@@@@█@@@█@@@",
    "@@@@@@@█@@@█@@@",
    "@@@@@@@█@@@█@@@",
]

# FLIP = [
#     "@@@@@@@█@@@█@@@",
#     "@@@@@@@█@@@█@@@",
#     "@@@@@@@█@@@█@@@",
#     "████@@@█@@@@@@@",
#     "@@@@█@@@@@@@███",
#     "@@@@█@@@█@@@@@@",
#     "@@@@█@@@@█@@@@@",
#     "@@@@█TORUS█@@@@",
#     "@@@@@█@@@@█@@@@",
#     "@@@@@@█@@@█@@@@",
#     "███@@@@@@@█@@@@",
#     "@@@@@@@█@@@████",
#     "@@@█@@@█@@@@@@@",
#     "@@@█@@@█@@@@@@@",
#     "@@@█@@@█@@@@@@@",
# ]

id = int(time.time())
BES_JSON = f"results/bests_{id}.json"
SOL_JSON = f"solutions/solutions_{id}.json"
FAI_JSON = "fails.json"

ROWLEN = 15
GRIDCELLS = ROWLEN * ROWLEN

C_WALL = "█"

T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"


iterator = itertools.combinations(range(ROWLEN), 2)

# bests
v_best_score = 0
v_best_grids = []
solutions = []


def transpose(grid):
    return ["".join(x) for x in zip(*grid)]


def get_word_locations(grid: list[list[str]], direction: Direction) -> list[Word]:
    """Get all the words in the grid in the given direction.

    Args:
        grid (list[list[str]]): The grid to search.
        direction (Direction): The direction to search in.

    Returns:
        list[Word]: The words found in the grid.

    Note:
        The words contain the starting point, the direction, and the length of the word.
        When a word is created, it is initialized with a set of all possible words of that length.
    """

    if direction == Direction.DOWN:
        grid_T = transpose(grid)

    output = []  # 1 "accross" or "down", (row, colum) of first word, length of word
    # across
    for r in range(ROWLEN):
        if direction == Direction.ACROSS:
            row = grid[r]
        else:
            row = grid_T[r]

        start = -1
        for j, c in enumerate(row):
            if c == C_WALL:
                continue
            if row[(j - 1) % ROWLEN] == C_WALL:
                start = j
            elif row[(j + 1) % ROWLEN] == C_WALL and start != -1:
                if direction == Direction.ACROSS:
                    point = (r, start)
                else:
                    point = (start, r)

                word = Word(point, direction, (j - start + 1) % ROWLEN)
                output.append(word)
                start = -1

        if start != -1:
            # NOTE: assumes 1 black square
            if direction == Direction.ACROSS:
                point = (r, start)
            else:
                point = (start, r)
            word = Word(point, direction, ROWLEN - start + row.find(C_WALL))
            output.append(word)
    return output


# NOTE: pass on the word for each square and possibilities to use as initial condidtions
def update_square_possibilities(
    square_to_word_map: dict[tuple[int, int], Sqaure], words: list[Word]
) -> dict[tuple[int, int], Sqaure]:
    for s in square_to_word_map.values():
        across: Word = s.across
        word = words[across[0]]
        spot = across[1]
        accross_pos = {p[spot] for p in word.possibilities}

        down = s.down
        word = words[down[0]]
        spot = down[1]
        down_pos = {p[spot] for p in word.possibilities}

        pos = accross_pos.intersection(down_pos)

        s.possible_chars = pos

    return square_to_word_map


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
                                (x_start, (y_start + i) % ROWLEN)
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
                                ((x_start + i) % ROWLEN, y_start)
                            ].possible_chars
                        ):
                            break
                    else:
                        new_possibilities += "," + p

        w.possibilities = new_possibilities.split(",")[1:]

    return words


def replace_char_at(grid: list[str], loc: tuple[int, int], c: str) -> list[str]:
    """Replace the character at the given location in the grid."""
    row = grid[loc[0]]
    grid[loc[0]] = f"{row[:loc[1]]}{c}{row[loc[1]+1:]}"
    return grid


def initalize(grid):
    # NOTE: initialize words
    words = get_word_locations(grid, Direction.ACROSS) + get_word_locations(
        grid, Direction.DOWN
    )
    # NOTE: initialize square_to_word_map
    square_to_word_map: dict[list[tuple[int, int]], Sqaure] = {}
    for i, j in itertools.product(range(ROWLEN), repeat=2):
        letter = grid[i][j]
        if letter == C_WALL:
            continue
        square_to_word_map[(i, j)] = Sqaure(None, None)
        if letter != "@":
            square_to_word_map[(i, j)].possible_chars = {letter}

    for wid, w in enumerate(words):
        x_start, y_start = w.start
        if w.direction == Direction.ACROSS:
            for i in range(w.length):
                square_to_word_map[(x_start, (y_start + i) % ROWLEN)].across = (wid, i)
        elif w.direction == Direction.DOWN:
            for i in range(w.length):
                square_to_word_map[((x_start + i) % ROWLEN, y_start)].down = (wid, i)

    return words, square_to_word_map


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
    min_possibilities = 26
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
        for l in solutions:
            if l["grid"] == grid:
                return

        tqdm.tqdm.write(T_YELLOW + "Solution found")  # Green text indicating success
        tqdm.tqdm.write(json.dumps(grid, indent=2, ensure_ascii=False))
        tqdm.tqdm.write(T_NORMAL)
        solutions.append({"level": level, "grid": grid})
        with open(SOL_JSON, "w") as f:
            json.dump(solutions, f, indent=2, ensure_ascii=False)

        if len(solutions) > 10:
            print(T_GREEN, "Found 10 solutions", T_NORMAL)
            exit()
        return

    new_grids = get_new_grids(grid)

    if not new_grids:
        tqdm.tqdm.write(
            T_PINK + "No solution found" + T_NORMAL
        )  # Red text indicating failure
        return

    with tqdm.tqdm(new_grids, desc=f"Level {level}") as t:
        l = count_letters(grid)
        if l > v_best_score:
            v_best_score = l
            v_best_grids.append({"level": level, "score": l, "grid": grid})

            with open(BES_JSON, "w") as f:
                json.dump(v_best_grids, f, indent=2, ensure_ascii=False)

        for new_grid in t:
            recursive_search(new_grid.copy(), level + 1)


if __name__ == "__main__":
    grid = INITIAL_TEMPLATE.copy()
    with open(FAI_JSON, "r") as f:
        fails = json.load(f)

    words = get_word_locations(grid, Direction.ACROSS) + get_word_locations(
        grid, Direction.DOWN
    )
    print(T_YELLOW, "number of answers", len(words), T_NORMAL)
    print(T_YELLOW, "number of black squares", "".join(grid).count(C_WALL), T_NORMAL)

    if grid in fails:
        print("Already failed")
        exit()

    recursive_search(grid, 0)

    if not len(solutions):
        print("No solution found")

        fails.append(INITIAL_TEMPLATE)
        with open(FAI_JSON, "w") as f:
            json.dump(fails, f, indent=2, ensure_ascii=False)
    else:
        print(T_GREEN, f"Found {len(solutions)} solutions", T_NORMAL)
