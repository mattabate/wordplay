import json
import tqdm
from schema import Direction, Sqaure, Word
import time

INITIAL_TEMPLATE = [
    "@@@█@E@@█A@@@@@",
    "@@@█@R@@█K@@@@@",
    "@@@█@T@@█E@@@@@",
    "@@@@█U@@@█@@@@@",
    "███@@B@█@@@@███",
    "@@@@@E█@@@@@@@@",
    "@@@@@█@@@@█@@@@",
    "HNUT█TORUS█DOUG",
    "@@@@█@@@@█@@@@@",
    "@@@@@@@@█B@@@@@",
    "███@@@@█@U@@███",
    "@@@@@█@@@N█@@@@",
    "@@@@@I█@@D@█@@@",
    "@@@@@N█@@T@█@@@",
    "@@@@@N█@@C@█@@@",
]

BES_JSON = f"results/bests_{int(time.time())}.json"
FAI_JSON = "fails.json"

ROWLEN = 15
GRIDCELLS = ROWLEN * ROWLEN

C_WALL = "█"

T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"

# bests
v_best_score = 0
v_best_grids = []
solution_found = False


def transpose(grid):
    return ["".join(x) for x in zip(*grid)]


def get_word_locations(
    initial_grid: list[list[str]],
) -> list[Word]:
    output = []  # 1 "accross" or "down", (row, colum) of first word, length of word
    # across
    for r in range(ROWLEN):
        row = initial_grid[r]
        start = -1
        for j, c in enumerate(row):
            if c != C_WALL and row[(j - 1) % ROWLEN] == C_WALL:
                start = j
            if c != C_WALL and row[(j + 1) % ROWLEN] == C_WALL and start != -1:
                word = Word((r, start), Direction.ACROSS, (j - start + 1) % ROWLEN)
                output.append(word)
                start = -1

        if start != -1:
            word = Word((r, start), Direction.ACROSS, ROWLEN - start + row.find(C_WALL))
            output.append(word)

    new_grid = transpose(initial_grid)
    # down
    for r in range(ROWLEN):
        row = new_grid[r]
        start = -1
        for j, c in enumerate(row):
            if c != C_WALL and row[(j - 1) % ROWLEN] == C_WALL:
                start = j
            if c != C_WALL and row[(j + 1) % ROWLEN] == C_WALL and start != -1:
                word = Word((start, r), Direction.DOWN, (j - start + 1) % ROWLEN)
                output.append(word)
                start = -1

        if start != -1:
            word = Word((start, r), Direction.DOWN, ROWLEN - start + row.find(C_WALL))
            output.append(word)

    return output


def update_square_possibilities(
    square_to_word_map: dict[tuple[int, int], Sqaure], words: list[Word]
) -> dict[tuple[int, int], Sqaure]:
    for s in square_to_word_map.keys():
        across = square_to_word_map[s].across
        word = words[across[0]]
        spot = across[1]
        accross_pos = set()
        for p in word.possibilities:
            accross_pos.add(p[spot])

        down = square_to_word_map[s].down
        word = words[down[0]]
        spot = down[1]
        down_pos = set()
        for p in word.possibilities:
            down_pos.add(p[spot])

        pos = accross_pos.intersection(down_pos)
        square_to_word_map[s].possible_chars = pos

    return square_to_word_map


def update_word_possibilities(
    words: list[Word], square_to_word_map: dict[tuple[int, int], Sqaure]
) -> list[Word]:
    for w in words:
        new_possibilities = []
        for p in w.possibilities:
            if w.direction == Direction.ACROSS:
                for i, c in enumerate(p):
                    if (
                        c
                        not in square_to_word_map[
                            (w.start[0], (w.start[1] + i) % ROWLEN)
                        ].possible_chars
                    ):
                        break
                else:
                    new_possibilities.append(p)
            elif w.direction == Direction.DOWN:
                for i, c in enumerate(p):
                    if (
                        c
                        not in square_to_word_map[
                            ((w.start[0] + i) % ROWLEN, w.start[1])
                        ].possible_chars
                    ):
                        break
                else:
                    new_possibilities.append(p)

        w.possibilities = new_possibilities

    return words


def replace_char_at(gird: list[str], loc: tuple[int, int], c: str) -> list[str]:
    row = gird[loc[0]]
    row = row[: loc[1]] + c + row[loc[1] + 1 :]
    gird[loc[0]] = row
    return gird


def get_new_grids(grid: list[str]) -> list[list[str]]:
    # NOTE: initialize words
    words = get_word_locations(grid)

    # NOTE: initialize square_to_word_map
    square_to_word_map: dict[tuple[int, int], Sqaure] = {}
    for i in range(ROWLEN):
        for j in range(ROWLEN):
            if grid[i][j] != C_WALL:
                square_to_word_map[(i, j)] = Sqaure(None, None)
                if grid[i][j] != "@":
                    square_to_word_map[(i, j)].possible_chars = {grid[i][j]}

    for wid, w in enumerate(words):
        if w.direction == Direction.ACROSS:
            for i in range(w.length):
                row, col = w.start[0], (w.start[1] + i) % ROWLEN
                square_to_word_map[(row, col)].across = (wid, i)

        if w.direction == Direction.DOWN:
            for i in range(w.length):
                row, col = (w.start[0] + i) % ROWLEN, w.start[1]
                square_to_word_map[(row, col)].down = (wid, i)

    old_vector = [len(w.possibilities) for w in words]
    for zz in range(10):
        words = update_word_possibilities(words, square_to_word_map)
        new_vector = [len(w.possibilities) for w in words]
        if old_vector == new_vector:

            break
        old_vector = new_vector

        square_to_word_map = update_square_possibilities(square_to_word_map, words)

        for s in square_to_word_map.keys():
            if len(square_to_word_map[s].possible_chars) == 0:
                return []

    output = []
    new_grid = grid.copy()
    for s in square_to_word_map.keys():
        if len(square_to_word_map[s].possible_chars) == 1:
            new_grid = replace_char_at(
                new_grid, s, list(square_to_word_map[s].possible_chars)[0]
            )

    # get square with min possibilities, not including 1
    min_possibilities = 26
    min_square = None
    for s in square_to_word_map.keys():
        num_pos = len(square_to_word_map[s].possible_chars)
        if num_pos == 1:
            continue
        if num_pos < min_possibilities:
            min_possibilities = num_pos
            min_square = s

    for p in square_to_word_map[min_square].possible_chars:
        g = new_grid.copy()
        g = replace_char_at(g, min_square, p)
        output.append(g)
    return output


def count_letters(grid: list[str], only_corners=False) -> int:
    if only_corners:
        _sum = 0
        for i in [0, 1, 2, 12, 13, 14]:
            bits = grid[i].split(C_WALL)
            _sum += bits[0].count("_") + bits[0].count("@") + bits[0].count("█")
            _sum += bits[-1].count("_") + bits[-1].count("@") + bits[-1].count("█")
        return 120 - _sum
    else:
        return GRIDCELLS - sum(
            [l.count("_") + l.count("@") + l.count("█") for l in grid]
        )


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "@" in l:
            return False
    return True


def recursive_search(grid, level=0):
    global v_best_score
    global v_best_grids
    global solution_found

    if grid_filled(grid):
        tqdm.tqdm.write(T_YELLOW + "Solution found")  # Green text indicating success
        tqdm.tqdm.write(json.dumps(grid, indent=2, ensure_ascii=False))
        tqdm.tqdm.write(T_NORMAL)
        tqdm.tqdm.write(
            json.dumps(
                T_YELLOW + INITIAL_TEMPLATE + T_NORMAL, indent=2, ensure_ascii=False
            )
        )
        solution_found = True
        return

    new_grids = get_new_grids(grid)

    if not new_grids:
        tqdm.tqdm.write(
            T_PINK + "No solution found" + T_NORMAL
        )  # Red text indicating failure
        return

    with tqdm.tqdm(new_grids, desc=f"Level {level}") as t:
        l = count_letters(grid)
        l = count_letters(grid)
        if l > v_best_score:
            v_best_score = l
            v_best_grids.append({"level": level, "score": l, "grid": grid})
            with open(BES_JSON, "w") as f:
                json.dump(v_best_grids, f, indent=2, ensure_ascii=False)

        for new_grid in t:
            recursive_search(new_grid, level + 1)


if __name__ == "__main__":
    grid = INITIAL_TEMPLATE.copy()
    with open(FAI_JSON, "r") as f:
        fails = json.load(f)

    if grid in fails:
        print("Already failed")
        exit()

    solution_found = False
    recursive_search(grid, 0)

    if not solution_found:
        print("No solution found")

        fails.append(INITIAL_TEMPLATE)
        with open(FAI_JSON, "w") as f:
            json.dump(fails, f, indent=2, ensure_ascii=False)
