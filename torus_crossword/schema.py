from enum import Enum
import json
import random


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


class WalledWord(Word):
    def __init__(self, start: tuple[int, int], direction: Direction, length: int):
        super().__init__(start, direction, length)
        self.possibilities = WORDLIST_WALLED_BY_LEN[length]


class WalledSqaure(Sqaure):
    def __init__(self, across: WalledWord, down: WalledWord):
        super().__init__(across, down)
        self.possible_chars = set(l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + C_WALL)
