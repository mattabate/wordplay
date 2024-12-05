"""15x15 grids use █ and @, this script places the letters, and is typically used to solve crosswords."""

import itertools

from lib import Direction, Sqaure, Word, replace_char_in_grid, transpose

from config import C_WALL, ROWLEN


def get_word_locations(grid: list[str], direction: Direction) -> list[Word]:
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
        x_start, y_start = w.start
        new_possibilities = ""
        match w.direction:
            case Direction.ACROSS:
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

        # # NOTE: find the square with the fewest possibilities otherwise
        num_pos = len(v.possible_chars)
        if num_pos < min_possibilities:
            min_possibilities = num_pos
            min_square = s

    if "@" not in "".join(filled_grid):
        return [filled_grid]

    # TODO: make min square to influence
    output = [
        replace_char_in_grid(filled_grid.copy(), min_square, p)
        for p in square_to_word_map[min_square].possible_chars
    ]
    return output
