from enum import Enum
import random

import torus
from config import (
    C_WALL,
    WOR_JSON,
    STAR_HEIGHT,
    STAR_WIDTH,
    ROWLEN,
    STAR_FLIPPED_TEMPLATE,
    STAR_TEMPLATE,
    STAR_START,
    STAR_HEIGHT,
    STAR_WIDTH,
)

T_NORMAL = "\033[0m"
T_BLUE = "\033[94m"
T_YELLOW = "\033[93m"
T_GREEN = "\033[92m"
T_PINK = "\033[95m"


WORDLIST = torus.json.load_json(WOR_JSON)

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

    def copy(self):
        return Word(self.start, self.direction, self.length)


import random


class Sqaure:
    across: Word
    down: Word
    possible_chars: set[str]

    def __init__(self, across: Word, down: Word):
        self.across = across
        self.down = down
        letter_set = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        random.shuffle(letter_set)
        self.possible_chars = set(letter_set)


def transpose(grid: list[str]) -> list[str]:
    """transpose a 15x15 character grid, represented as a list of strings"""
    return ["".join(row) for row in zip(*grid)]


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
    template = template.copy()
    t_holder = "____█TORUS█____"
    d_holder = "HNUT█_____█DOUG"
    if type == "A":
        for i in range(ROWLEN):
            if t_holder[i] != "_":
                template[7] = torus.strings.replace_char_in_string(
                    template[7], t_holder[i], i
                )
    elif type == "AA":
        template[7] = "HNUT█TORUS█DOUG"
    elif type == "AD":
        for i in range(ROWLEN):
            if d_holder[i] != "_":
                template[i] = torus.strings.replace_char_in_string(
                    template[i], d_holder[i], 7
                )

        for i in range(ROWLEN):
            if t_holder[i] != "_":
                template[7] = torus.strings.replace_char_in_string(
                    template[7], t_holder[i], i
                )
    elif type == "DA":
        for i in range(ROWLEN):
            if d_holder[i] != "_":
                template[7] = torus.strings.replace_char_in_string(
                    template[7], d_holder[i], i
                )
        for i in range(ROWLEN):
            if t_holder[i] != "_":
                template[i] = torus.strings.replace_char_in_string(
                    template[i], t_holder[i], 7
                )
    elif type == "DD":
        col7 = "HNUT█TORUS█DOUG"
        for i in range(ROWLEN):
            if col7[i] != "_":
                template[i] = torus.strings.replace_char_in_string(
                    template[i], col7[i], 7
                )
    elif type == "":
        pass
    else:
        raise ValueError(f"Invalid IC_TYPE: {type}")
    return template


import json


def get_star_from_grid(grid, f_flipped) -> list[list[str]]:
    if f_flipped:
        template = STAR_FLIPPED_TEMPLATE.copy()
    else:
        template = STAR_TEMPLATE.copy()

    for i in range(STAR_HEIGHT):
        for j in range(STAR_WIDTH):
            if template[i][j] != "@":
                continue

            template = replace_char_in_grid(
                template,
                (i, j),
                grid[(STAR_START[0] + i) % ROWLEN][(STAR_START[1] + j) % ROWLEN],
            )

    return template


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


def grid_template_filled(grid: list[str]) -> bool:
    """
    Return True if the grid template is filled with letters and letter placeholders.
    True if all letter locations are known, False otherwise.
    """
    for l in grid:
        if "_" in l:
            return False
    return True


def grid_filled(grid: list[str]) -> bool:
    """
    Return True if the grid is filled with letters
    and there are no remaining placeholders, False otherwise.
    """
    for l in grid:
        if "@" in l or "_" in l:
            return False
    return True


def count_letters(grid: list[str]) -> int:
    """
    Count the number of letters in the grid.
    """
    return len([c for c in "".join(grid) if c.isalpha()])
