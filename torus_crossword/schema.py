from enum import Enum
import json
import random
import fcntl

WOR_JSON = "word_list.json"
C_WALL = "█"

with open(WOR_JSON) as f:
    WORDLIST = json.load(f)

WORDLIST_WALLED = [C_WALL + w + C_WALL for w in WORDLIST]

random.shuffle(WORDLIST)
random.shuffle(WORDLIST_WALLED)

WORDLIST_BY_LEN = {}
for w in WORDLIST:
    l = len(w)
    if l not in WORDLIST_BY_LEN:
        WORDLIST_BY_LEN[l] = []
    WORDLIST_BY_LEN[l].append(w)

WORDLIST_WALLED_BY_LEN = {}
for w in WORDLIST_WALLED:
    l = len(w)
    if l not in WORDLIST_WALLED_BY_LEN:
        WORDLIST_WALLED_BY_LEN[l] = []
    WORDLIST_WALLED_BY_LEN[l].append(w)


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


# this is so stupid - it should have a touple position with a position in both words
class Sqaure:
    across: Word
    down: Word
    possible_chars: set[str]

    def __init__(self, across: Word, down: Word):
        self.across = across
        self.down = down
        self.possible_chars = set(l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")


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


def load_json(json_name):
    with open(json_name, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            out = json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return out


def append_json(json_name, grid):
    with open(json_name, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            data = json.load(f)
            data.append(grid)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
