"""optimizes script aimed just at the corners"""

import json
import time
import tqdm
from config import C_WALL
from torus.json import append_json, load_json
from config import (
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    STARS_CHECKED_JSON,
    STARS_CHECKED_FLIPPED_JSON,
    STAR_SEARCH_W_FLIPPED,
    STAR_SEARCH_VERBOSE,
    STAR_TEMPLATE,
    STAR_FLIPPED_TEMPLATE,
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

f_verbose = STAR_SEARCH_VERBOSE

# across words length 9
# down words length 8
TEMPLATE = ["@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@"]
if not STAR_SEARCH_W_FLIPPED:
    SOL_JSON = STARS_FOUND_JSON
    CHE_JSON = STARS_CHECKED_JSON
else:
    SOL_JSON = STARS_FOUND_FLIPPED_JSON
    CHE_JSON = STARS_CHECKED_FLIPPED_JSON

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


def find_first_letter(input_string):
    l = len(input_string)
    non_c_wall_index = l - len(input_string.lstrip(C_WALL))
    return non_c_wall_index if non_c_wall_index != l else -1


def get_word_locations(grid: list[list[str]], direction: Direction) -> list[Word]:
    words = []
    if direction == Direction.ACROSS:
        for r in range(6):
            if not "@" in grid[r]:
                continue

            word_holder = Word(
                direction=Direction.ACROSS,
                start=(r, find_first_letter(grid[r])),
                length=6,
            )
            if r in [0, 1, 2]:
                if STAR_SEARCH_W_FLIPPED:
                    word_holder.possibilities = across_pref_set
                else:
                    word_holder.possibilities = across_suff_set
            elif r in [3, 4, 5]:
                if STAR_SEARCH_W_FLIPPED:
                    word_holder.possibilities = across_suff_set
                else:
                    word_holder.possibilities = across_pref_set
            words.append(word_holder)
    else:
        it_t = transpose(grid)
        for c in range(6):
            if "@" in it_t[c]:
                if not "@" in it_t[c]:
                    continue

                word_holder = Word(
                    direction=Direction.DOWN,
                    start=(find_first_letter(it_t[c]), c),
                    length=6,
                )
                if c in [0, 1, 2]:
                    if STAR_SEARCH_W_FLIPPED:
                        word_holder.possibilities = down_suff_set
                    else:
                        word_holder.possibilities = down_pref_set
                elif c in [3, 4, 5]:
                    if STAR_SEARCH_W_FLIPPED:
                        word_holder.possibilities = down_pref_set
                    else:
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


def get_stars_from_seed_grids(grid: list[str]) -> list[list[str]]:
    if STAR_SEARCH_W_FLIPPED:
        new_temp = STAR_FLIPPED_TEMPLATE.copy()
    else:
        new_temp = STAR_TEMPLATE.copy()
    for r in range(6):
        new_temp[r + 2] = new_temp[r + 2][:3] + grid[r] + new_temp[r + 2][9:]
    actual_ics = [new_temp]

    if STAR_SEARCH_W_FLIPPED:
        for r in [0, 1, 2]:
            words = [w for w in WORDLIST_BY_LEN[9] if w.startswith(grid[r])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new[2 + r] = C_WALL * 3 + w
                    new_actual_ics.append(new)
            actual_ics = new_actual_ics

        for r in [3, 4, 5]:
            words = [w for w in WORDLIST_BY_LEN[9] if w.endswith(grid[r])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new[2 + r] = w + C_WALL * 3
                    new_actual_ics.append(new)
            actual_ics = new_actual_ics

        grid_t = transpose(grid)
        for c in [0, 1, 2]:
            words = [w for w in WORDLIST_BY_LEN[8] if w.endswith(grid_t[c])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new_t = transpose(new)
                    new_t[c + 3] = w + C_WALL * 2
                    new_actual_ics.append(transpose(new_t))
            actual_ics = new_actual_ics

        for c in [3, 4, 5]:
            words = [w for w in WORDLIST_BY_LEN[8] if w.startswith(grid_t[c])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new_t = transpose(new)
                    new_t[c + 3] = C_WALL * 2 + w
                    new_actual_ics.append(transpose(new_t))
            actual_ics = new_actual_ics
    else:
        for r in [0, 1, 2]:
            words = [w for w in WORDLIST_BY_LEN[9] if w.endswith(grid[r])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new[2 + r] = w + C_WALL * 3
                    new_actual_ics.append(new)
            actual_ics = new_actual_ics

        for r in [3, 4, 5]:
            words = [w for w in WORDLIST_BY_LEN[9] if w.startswith(grid[r])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new[2 + r] = C_WALL * 3 + w
                    new_actual_ics.append(new)
            actual_ics = new_actual_ics

        grid_t = transpose(grid)
        for c in [0, 1, 2]:
            words = [w for w in WORDLIST_BY_LEN[8] if w.startswith(grid_t[c])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new_t = transpose(new)
                    new_t[c + 3] = C_WALL * 2 + w
                    new_actual_ics.append(transpose(new_t))
            actual_ics = new_actual_ics

        for c in [3, 4, 5]:
            words = [w for w in WORDLIST_BY_LEN[8] if w.endswith(grid_t[c])]

            new_actual_ics = []
            for w in words:
                for g in actual_ics:
                    new = g.copy()
                    new_t = transpose(new)
                    new_t[c + 3] = w + C_WALL * 2
                    new_actual_ics.append(transpose(new_t))
            actual_ics = new_actual_ics

    return ["".join(s) for s in actual_ics]


def recursive_search(grid, level=0):
    global v_best_score
    global v_best_grids

    if f_verbose:
        print(json.dumps(grid, indent=2, ensure_ascii=False))

    if grid_filled(grid):
        # potential solution found

        # check to make sure rows of interest are valid words
        if not STAR_SEARCH_W_FLIPPED:
            for r in range(6):
                if r in [0, 1, 2]:
                    if grid[r] not in across_suff_set:
                        return
                elif r in [3, 4, 5]:
                    if grid[r] not in across_pref_set:
                        return
            grid_t = transpose(grid)
            for c in range(6):
                if c in [0, 1, 2]:
                    if grid_t[c] not in down_pref_set:
                        return
                elif c in [3, 4, 5]:
                    if grid_t[c] not in down_suff_set:
                        return
        else:
            for r in range(6):
                if r in [0, 1, 2]:
                    if grid[r] not in across_pref_set:
                        return
                elif r in [3, 4, 5]:
                    if grid[r] not in across_suff_set:
                        return
            grid_t = transpose(grid)
            for c in range(6):
                if c in [0, 1, 2]:
                    if grid_t[c] not in down_suff_set:
                        return
                elif c in [3, 4, 5]:
                    if grid_t[c] not in down_pref_set:
                        return

        # ok - so now what i have to do is generate the grids from the inital grid

        stars_from_grid = get_stars_from_seed_grids(grid)

        print(
            f"Found {T_PINK}{len(stars_from_grid)}{T_NORMAL} Solutions"
        )  # Green text indicating success
        solutions = load_json(SOL_JSON)
        for s in stars_from_grid:
            if s not in solutions:
                append_json(SOL_JSON, s)
        return

    new_grids = get_new_grids(grid)

    if not new_grids:
        return

    for new_grid in new_grids:
        recursive_search(new_grid.copy(), level + 1)


if __name__ == "__main__":
    t0 = time.time()

    if STAR_SEARCH_W_FLIPPED:
        words_now = across_pref_set
    else:
        words_now = across_suff_set

    len_wln = len(across_suff_set)
    for i, seed in enumerate(words_now):
        number_seen_so_far = len(list(set(load_json(CHE_JSON))))
        print(
            "-----------\n"
            + f"direction: {T_GREEN}{"flipped" if STAR_SEARCH_W_FLIPPED else "NOT flipped"}{T_NORMAL}\n"
            + f"TOTAL PROGRESS: {T_GREEN}{number_seen_so_far} / {len_wln}{T_NORMAL}\n"
            + f"LOCAL ITERATION {T_GREEN}{i}{T_NORMAL}\n"
            + f"Seed word: {T_GREEN}{seed}{T_NORMAL}"
        )
        already_checked = load_json(CHE_JSON)
        if seed in already_checked:
            print(T_PINK + "> Already checked" + T_NORMAL)
            continue
        grid = TEMPLATE.copy()

        # PERPLEXES███SPIRITUAL
        grid[0] = seed
        for seed2 in tqdm.tqdm(words_now):
            grid[1] = seed2
            recursive_search(grid, 0)

        append_json(CHE_JSON, seed)
