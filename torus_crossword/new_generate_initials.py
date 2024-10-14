"""optimizes script aimed just at the corners"""

import json
import time
import tqdm
from config import C_WALL
from torus.json import append_json, load_json
from config import (
    STAR_HEIGHT,
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    STARS_CHECKED_JSON,
    STARS_CHECKED_FLIPPED_JSON,
    STAR_TEMPLATE,
    STAR_FLIPPED_TEMPLATE,
    STAR_ROWS_OF_INTEREST,
    STAR_COLS_OF_INTEREST,
    STAR_SEARCH_W_FLIPPED,
    STAR_SEARCH_VERBOSE,
)
from lib import (
    Direction,
    Sqaure,
    Word,
    WORDLIST_BY_LEN,
    transpose,
    replace_char_in_grid,
    T_NORMAL,
    T_GREEN,
    T_PINK,
)
from torus.strings import get_prefix, get_suffix

f_flipped = STAR_SEARCH_W_FLIPPED
f_verbose = STAR_SEARCH_VERBOSE

if not f_flipped:
    SOL_JSON = STARS_FOUND_JSON
    CHE_JSON = STARS_CHECKED_JSON
    TEMPLATE = STAR_TEMPLATE
else:
    SOL_JSON = STARS_FOUND_FLIPPED_JSON
    CHE_JSON = STARS_CHECKED_FLIPPED_JSON
    TEMPLATE = STAR_FLIPPED_TEMPLATE

letter_locs = [
    (r, c)
    for r in range(len(TEMPLATE))
    for c in range(len(TEMPLATE[0]))
    if TEMPLATE[r][c] != C_WALL
]


v_best_score = 0
v_best_grids = []

# testing these here for now
words_for_across = WORDLIST_BY_LEN[9]
words_for_down = WORDLIST_BY_LEN[8]

across_pref_set = list(set(get_prefix(word=w, len_pref=6) for w in words_for_across))
across_suff_set = list(set(get_suffix(word=w, len_suff=6) for w in words_for_across))

down_pref_set = list(set(get_prefix(word=w, len_pref=6) for w in words_for_down))
down_suff_set = list(set(get_suffix(word=w, len_suff=6) for w in words_for_down))

new_inital_grid = ["@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@"]


def find_first_letter(input_string):
    l = len(input_string)
    non_c_wall_index = l - len(input_string.lstrip(C_WALL))
    return non_c_wall_index if non_c_wall_index != l else -1


def get_word_locations(grid: list[list[str]], direction: Direction) -> list[Word]:
    words = []
    if direction == Direction.ACROSS:
        for r in STAR_ROWS_OF_INTEREST:
            if not "@" in grid[r]:
                continue

            word_holder = Word(
                direction=Direction.ACROSS,
                start=(r, find_first_letter(grid[r])),
                length=6,
            )
            if r in [2, 3, 4]:
                word_holder.possibilities = across_suff_set
            elif r in [5, 6, 7]:
                word_holder.possibilities = across_pref_set
            words.append(word_holder)
    else:
        it_t = transpose(grid)
        for c in STAR_COLS_OF_INTEREST:
            if "@" in it_t[c]:
                if not "@" in it_t[c]:
                    continue

                word_holder = Word(
                    direction=Direction.DOWN,
                    start=(find_first_letter(it_t[c]), c),
                    length=6,
                )
                if c in [3, 4, 5]:
                    word_holder.possibilities = down_pref_set
                elif c in [6, 7, 8]:
                    word_holder.possibilities = down_suff_set

                words.append(word_holder)
    return words


def initalize(grid):
    # NOTE: initialize words
    unfilled_accross_words = get_word_locations(grid, Direction.ACROSS)
    unfilled_down_words = get_word_locations(grid, Direction.DOWN)
    words = unfilled_accross_words + unfilled_down_words

    # NOTE: initialize square_to_word_map
    square_to_word_map: dict[list[tuple[int, int]], Sqaure] = {}
    for i, j in letter_locs:
        letter = grid[i][j]
        square_to_word_map[(i, j)] = Sqaure(None, None)
        # initialize square as empty (ABCDEFGHIJKLMNOPQRSTUVWXYZ possible)
        if letter != "@":
            square_to_word_map[(i, j)].possible_chars = {letter}

    for wid, w in enumerate(words):
        x_start, y_start = w.start
        if w.direction == Direction.ACROSS:
            for i in range(w.length):
                square_to_word_map[(x_start, (y_start + i))].across = (wid, i)
        elif w.direction == Direction.DOWN:
            for i in range(w.length):
                square_to_word_map[((x_start + i), y_start)].down = (wid, i)

    return words, square_to_word_map


# NOTE: pass on the word for each square and possibilities to use as initial condidtions
# DONE
def update_square_possibilities(
    square_to_word_map: dict[tuple[int, int], Sqaure], words: list[Word]
) -> dict[tuple[int, int], Sqaure]:
    for s in square_to_word_map.values():
        if s.across:
            across: Word = s.across
            word = words[across[0]]
            spot = across[1]
            accross_pos = {p[spot] for p in word.possibilities}
        else:
            accross_pos = set(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        if not s.down:
            s.possible_chars = accross_pos
            continue

        down = s.down
        word = words[down[0]]
        spot = down[1]
        down_pos = {p[spot] for p in word.possibilities}

        pos = accross_pos.intersection(down_pos)

        s.possible_chars = pos

    return square_to_word_map


# DONE
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
                                (x_start, (y_start + i))
                            ].possible_chars
                        ):
                            break
                    else:
                        new_possibilities += "," + p
            case Direction.DOWN:
                for p in w.possibilities:  # for every possible word
                    for i, c in enumerate(p):  # for every character in the word
                        if (
                            c
                            not in square_to_word_map[
                                ((x_start + i), y_start)
                            ].possible_chars
                        ):  # if the character is not in the possible characters for the square
                            break
                    else:
                        new_possibilities += (
                            "," + p
                        )  # if every characters in the word wordks, add the word!

        w.possibilities = new_possibilities.split(",")[1:]

    return words


# DONE
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

        # NOTE: find the square with the fewest possibilities otherwise
        num_pos = len(v.possible_chars)
        if num_pos < min_possibilities:
            min_possibilities = num_pos
            min_square = s

    if not min_square:
        return [filled_grid]

    output = [
        replace_char_in_grid(filled_grid.copy(), min_square, p)
        for p in square_to_word_map[min_square].possible_chars
    ]
    return output


def grid_filled(grid: list[str]) -> bool:
    for l in grid:
        if "@" in l:
            return False
    return True


def isolate_word(s) -> str:
    return s.replace("█", "")


def something_1(grid):
    for r in STAR_ROWS_OF_INTEREST:
        candidate = isolate_word(grid[r])
        if candidate not in WORDLIST_BY_LEN[len(candidate)]:
            return False
    return True


def something_2(grid):
    for c in STAR_COLS_OF_INTEREST:
        candidate = isolate_word("".join([grid[r][c] for r in range(STAR_HEIGHT)]))
        if candidate not in WORDLIST_BY_LEN[len(candidate)]:
            return False
    return True


def recursive_search(grid, level=0):
    global v_best_score
    global v_best_grids

    if f_verbose:
        print(json.dumps(grid, indent=2, ensure_ascii=False))

    if grid_filled(grid):
        # check to make sure rows of interest are valie words
        if (not something_1(grid)) or (not something_2(grid)):
            return

        print("Solution found")  # Green text indicating success

        solutions = load_json(SOL_JSON)
        if grid not in solutions:
            1
            print("New solution found??")
            print(json.dumps(grid, indent=2, ensure_ascii=False))
            # append_json(SOL_JSON, "".join(grid))
        return

    new_grids = get_new_grids(grid)

    if not new_grids:
        return

    for new_grid in new_grids:
        recursive_search(new_grid.copy(), level + 1)


# STAR_TEMPLATE = [
#     "██████@@@███",
#     "██████@@@███",
#     "@@@@@@@@@███",
#     "@@@@@@@@@███",
#     "@@@@@@@@@███",
#     "███@@@@@@@@@",
#     "███@@@@@@@@@",
#     "███@@@@@@@@@",
#     "███@@@██████",
#     "███@@@██████",
# ]
# across words length 9
# down words length 8


# FIX
if __name__ == "__main__":
    t0 = time.time()

    for i, seed in enumerate(across_suff_set):
        number_seen_so_far = len(list(set(load_json(CHE_JSON))))
        print(
            "-----------\n"
            + f"direction: {T_GREEN}{"flipped" if f_flipped else "NOT flipped"}{T_NORMAL}\n"
            + f"TOTAL PROGRESS: {T_GREEN}{number_seen_so_far} / {len_wln}{T_NORMAL}\n"
            + f"LOCAL ITERATION {T_GREEN}{i}{T_NORMAL}\n"
            + f"Seed word: {T_GREEN}{seed}{T_NORMAL}"
        )
        already_checked = load_json(CHE_JSON)
        if seed in already_checked:
            print(T_PINK + "Already checked" + T_NORMAL)
            continue
        grid = TEMPLATE.copy()

        grid[3] = seed
        for seed2 in tqdm.tqdm(across_suff_set):
            grid[4] = seed2
            recursive_search(grid, 0)

        # append_json(CHE_JSON, seed)
