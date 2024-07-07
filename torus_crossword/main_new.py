import json
import os
import time
import tqdm
from enum import Enum


INITIAL_TEMPLATE = [
    "@@@█@E@@█A@@@@@",
    "@@@█@R@@█KL@@@@",
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

ROWLEN = 15
WOR_JSON = "words.json"
C_WALL = "█"


with open(WOR_JSON) as f:
    WORDLIST = json.load(f)

WORDLIST_BY_LEN = {}
for w in WORDLIST:
    l = len(w)
    if l not in WORDLIST_BY_LEN:
        WORDLIST_BY_LEN[l] = []
    WORDLIST_BY_LEN[l].append(w)


def transpose(grid):
    return ["".join(x) for x in zip(*grid)]


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
            if INITIAL_TEMPLATE[i][j] != C_WALL:
                square_to_word_map[(i, j)] = Sqaure(None, None)
                if INITIAL_TEMPLATE[i][j] != "@":
                    square_to_word_map[(i, j)].possible_chars = {INITIAL_TEMPLATE[i][j]}

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
            print("no change", zz)
            # sort vector and print
            print(sorted(new_vector))
            print(sorted([len(s.possible_chars) for s in square_to_word_map.values()]))

            # take grid and add all letters for which there is one possibility

            break
        old_vector = new_vector

        square_to_word_map = update_square_possibilities(square_to_word_map, words)

        for s in square_to_word_map.keys():
            if len(square_to_word_map[s].possible_chars) == 0:
                print("reached a dead end", s)
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


new_grids = get_new_grids(INITIAL_TEMPLATE)

for g in new_grids:
    print(json.dumps(g, indent=2, ensure_ascii=False))
