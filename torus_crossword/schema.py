from enum import Enum
import json

WOR_JSON = "words.json"

with open(WOR_JSON) as f:
    WORDLIST = json.load(f)

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
