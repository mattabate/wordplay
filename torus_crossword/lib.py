from enum import Enum
import random
from config import WOR_JSON, STAR_HEIGHT, STAR_WIDTH, ROWLEN
from torus.json import load_json

T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"


WORDLIST = load_json(WOR_JSON)

random.shuffle(WORDLIST)

WORDLIST_BY_LEN = {}
for w in WORDLIST:
    l = len(w)
    if l not in WORDLIST_BY_LEN:
        WORDLIST_BY_LEN[l] = []
    WORDLIST_BY_LEN[l].append(w)


class Direction(Enum):
    ACROSS = 1
    DOWN = 2


class Word:
    start: tuple[int, int]
    direction: Direction
    length: int
    possibilities: list[str]

    def __init__(self, start: tuple[int, int], direction: Direction, length: int):
        self.start = start
        self.direction = direction
        self.length = length
        self.possibilities = WORDLIST_BY_LEN[length]


class Sqaure:
    across: Word
    down: Word
    possible_chars: set[str]

    def __init__(self, across: Word, down: Word):
        self.across = across
        self.down = down
        self.possible_chars = set(l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def transpose(grid: list[str]) -> list[str]:
    """transpose a 15x15 character grid, represented as a list of strings"""
    return ["".join(row) for row in zip(*grid)]


def replace_char_in_string(string, char, index):
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


def replace_char_in_grid(grid: list[str], loc: tuple[int, int], c: str) -> list[str]:
    """Replace the character at the given location in the grid."""
    row = grid[loc[0]]
    grid[loc[0]] = f"{row[:loc[1]]}{c}{row[loc[1]+1:]}"
    return grid


def string_to_star(s: str) -> list[str]:
    """
    Reshape a string (of len 120) into a list of strings (of len 12).

    Args:
        s (str): The string to reshape (string version of star)

    Returns:
        list[str]: The reshaped string (grid version of star)
    """
    return [s[i * STAR_WIDTH : (i + 1) * STAR_WIDTH] for i in range(STAR_HEIGHT)]


def add_theme_words(template: list[str], type: str):
    """
    Add theme words to the initial 15x15 grid.
    """
    if type == "AA":
        template[7] = "HUNT█TORUS█DOUG"
    elif type == "AD":
        col7 = "HNUT█_____█DOUG"
        for i in range(ROWLEN):
            template[i] = replace_char_in_string(template[i], col7[i], 7)
        template[7] = "____█TORUS█____"
    elif type == "DA":
        template[7] = "HNUT█_____█DOUG"
        col7 = "____█TORUS█____"
        for i in range(ROWLEN):
            template[i] = replace_char_in_string(template[i], col7[i], 7)
    elif type == "DD":
        col7 = "HUNT█TORUS█DOUG"
        for i in range(ROWLEN):
            template[i] = replace_char_in_string(template[i], col7[i], 7)
    else:
        raise ValueError(f"Invalid IC_TYPE: {type}")
    return template
