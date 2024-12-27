from torus.strings import replace_char_in_string
from config import C_WALL
from torus.word import Word, Direction

T_NORMAL = "\033[0m"
ROWLEN = 15


def str_to_grid(grid_str: str) -> list[str]:
    """Convert a string of len 225 to a list[str] where each string is len 15."""
    return [grid_str[i : i + 15] for i in range(0, len(grid_str), 15)]


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


def transpose(grid: list[str]) -> list[str]:
    """transpose a 15x15 character grid, represented as a list of strings"""
    return ["".join(row) for row in zip(*grid)]


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


def get_grid_template_from_grid(grid):
    return ["".join("@" if c != C_WALL else C_WALL for c in s) for s in grid]


def get_grid_template_str_from_grid_str(grid_str: str):
    return "".join("@" if c != C_WALL else C_WALL for c in grid_str)


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


def get_words_in_filled_grid(grid: list[str]) -> list[str]:
    """returns a list of words in a filled grid"""
    words = get_word_locations(
        grid=grid, direction=Direction.ACROSS
    ) + get_word_locations(grid=grid, direction=Direction.DOWN)

    word_strings = []
    for w in words:
        string_word = ""
        for i in range(w.length):
            if w.direction == Direction.ACROSS:
                string_word += grid[w.start[0]][(w.start[1] + i) % ROWLEN]
            else:
                string_word += grid[(w.start[0] + i) % ROWLEN][w.start[1]]

        word_strings.append(string_word)

    return word_strings


def contains_bad_word_pairs(words):
    if (
        ("OPENDATES" in words and "TOURDATES" in words)
        or ("SKA" in words and "SKABANDS" in words)
        or ("NOTSMART" in words and "NOTATRACE" in words)
    ):
        return True
    return False
