import random
from torus.json import load_json
from config import WOR_JSON
from enum import Enum

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

    def copy(self):
        return Word(self.start, self.direction, self.length)
