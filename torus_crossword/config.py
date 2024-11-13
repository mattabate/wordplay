import enum

###############################################
# main.py config
# searches for completed 15x15 grid given initial conditions
###############################################

# Config for maip.py 15x15 search
# Note editing may cause big problems


class Mode(enum.Enum):
    AD = 0
    DA = 1
    A = 2
    MIN = 3


mode = Mode.DA  # da on personal
f_verbose = True
f_save_words_used = False
f_save_bounds = [0, 2]
SLEEP_DURATION = 120
SLEEP_DURATION_GRID = 180


if mode == Mode.AD:
    IC_TYPE = "AD"
    SEARCH_W_FLIPPED = False
    MAX_WAL = 42
    # note - WE HAVE GOOD for AD, 42, not flipped [but no solutions for 40]
elif mode == Mode.DA:
    IC_TYPE = "DA"  # da = flipped
    SEARCH_W_FLIPPED = True
    MAX_WAL = 40
elif mode == Mode.A:
    IC_TYPE = "A"  # A = flipped
    SEARCH_W_FLIPPED = True
    MAX_WAL = 42
elif mode == Mode.MIN:
    IC_TYPE = ""
    SEARCH_W_FLIPPED = True
    MAX_WAL = 42


GRID_TEMPLATE = [
    "______█@@@_█___",
    "______█@@@@█___",
    "______█@@@@█___",
    "███__@_________",
    "@@@________@@@@",
    "@@@_________███",
    "@@@_________@@@",
    "@@@_________@@@",
    "@@@_________@@@",
    "███_________@@@",
    "@@@@________@@@",
    "_________@__███",
    "___█@@@@█______",
    "___█@@@@█______",
    "___█_@@@█______",
]

GRID_TEMPLATE_FLIPPED = [s[::-1] for s in GRID_TEMPLATE]

import json

with open("liked_templates.json", "r") as f:
    liked_templates = json.load(f)

# GRID_TEMPLATE_FLIPPED = liked_templates[41]

# 0, 1, 3 has failed
# 2 got down to 1, no solutions found

# 4 got down to 1, no solutions found
# 5, 6, 7, 8, 9 no solutions
## fails = 11 - 41


# GRID_TEMPLATE_FLIPPED = [
#     "@@@█@@@@█@@@@@@",
#     "@@@█@@@@█@@@@@@",
#     "@@@█@@@@█@@@@@@",
#     "@@@@██@@@@@_███",
#     "@@@@@@@█@@@█@@@",
#     "███@@@@@@█@@@@@",
#     "@@@@@@█@@@█@@@@",
#     "@@@@█@@@@@█@@@@",
#     "@@@@█@@@█@@@@@@",
#     "@@@@@█@@@@@@███",
#     "@@@█@@@█@@@@@@@",
#     "███_@@@@@██@@@@",
#     "@@@@@@█@@@@█@@@",
#     "@@@@@@█@@@@█@@@",
#     "@@@@@@█@@@@█@@@",
# ]


# GRID_TEMPLATE_FLIPPED = [
#     "@@@██@@@█@@@@@@",
#     "@@@█@@@@█@@@@@@",
#     "@@@█@@@@█@@@@@@",
#     "@@@@@██@@@@@███",
#     "@@@@@@@█@@@█@@@",
#     "███@@@@T@█@@@@@",
#     "@@@█@@@O█@@@@@@",
#     "HNUT█@@R@@█DOUG",
#     "@@@@@@█U@@@█@@@",
#     "@@@@@█@S@@@@███",
#     "@@@█@@@█@@@@@@@",
#     "███@@@@@██@@@@@",
#     "@@@@@@█@@@@█@@@",
#     "@@@@@@█@@@@█@@@",
#     "@@@@@@█@@@██@@@",
# ]


GRID_TEMPLATE_FLIPPED_MIN = [
    "@@@█_@@@█@@@@@@",
    "@@@█@@@@█@@@@@@",
    "@@@█@@@@█@@@@@@",
    "@@@@@@@@@@@@███",
    "@@@@@█@@@@█@@@@",
    "███@@@@@@@@@@@@",
    "@@@@█@@@@█@@@@@",
    "@@@@@@@█@@@@@@@",
    "@@@@@█@@@@█@@@@",
    "@@@@@@@@@@@@███",
    "@@@@█@@@@█@@@@@",
    "███@@@@@@@@@@@@",
    "@@@@@@█@@@@█@@@",
    "@@@@@@█@@@@█@@@",
    "@@@@@@█@@@_█@@@",  # note - double here could come out
]

###############################################
# generate_initials.py config
# searches for completed 10x12 initial conditions
###############################################
STAR_SEARCH_W_FLIPPED = True  # True on personal computer
STAR_SEARCH_VERBOSE = False
BAD_STAR_JSON = "ic_data/bad_stars.json"
BAD_STAR_FLIPPED_JSON = "ic_data/bad_stars_flipped.json"

# location of start of the star
# note that stars wrap around the grid, touching all corners
STAR_HEIGHT = 10  # DO NOT CHANGE
STAR_WIDTH = 12  # DO NOT CHANGE
STAR_START = (10, 9)  # DO NOT CHANGE


STAR_TEMPLATE = [
    "██████@@@███",
    "██████@@@███",
    "@@@@@@@@@███",
    "@@@@@@@@@███",
    "@@@@@@@@@███",
    "███@@@@@@@@@",
    "███@@@@@@@@@",
    "███@@@@@@@@@",
    "███@@@██████",
    "███@@@██████",
]

STAR_FLIPPED_TEMPLATE = [s[::-1] for s in STAR_TEMPLATE]

STAR_ROWS_OF_INTEREST = [2, 3, 4, 5, 6, 7]
STAR_COLS_OF_INTEREST = [3, 4, 5, 6, 7, 8]


def get_failures_json(type: str, max_walls: int, flipped: bool = False) -> str:
    if flipped:
        return f"failures/15x15_stars_failures_{type}_{max_walls}_flipped.json"
    return f"failures/15x15_stars_failures_{type}_{max_walls}.json"


def get_solutions_json(type: str, max_walls: int, flipped: bool = False) -> str:
    if flipped:
        return f"solutions/15x15_grid_solutions_{type}_{max_walls}_flipped.json"
    return f"solutions/15x15_grid_solutions_{type}_{max_walls}.json"


def get_bad_solutions_json(type: str, max_walls: int, flipped: bool = False) -> str:
    if flipped:
        return f"bad_solutions/15x15_grid_solutions_{type}_{max_walls}_bad_flipped.json"
    return f"bad_solutions/15x15_grid_solutions_{type}_{max_walls}_bad.json"


# the wordlist contains all words in consideration for the search
# the format is a list of strings, about 100k total
WOR_JSON = "wordlist/word_list.json"
SCORES_DICT_JSON = "wordlist/scores_dict.json"
ACTIVE_WORDS_JSON = "filter_words/words_in_active_grids.json"
WORDS_OMITTED_JSON = "wordlist/words_omitted.json"
WORDS_APPROVED_JSON = "wordlist/words_approved.json"
WORDS_CONSIDERED_JSON = "filter_words/in_consideration.json"
WORDS_IN_SOLUTIONS_JSON = "filter_words/words_in_valid_solutions.json"

# initial conditions for the search are refered to as stars
# stars come in two flavors: normal and flipped
# files where the stars are stored are named star_sols.json and star_sols_flipped.json
STARS_FOUND_JSON = "ic_data/star_sols.json"
STARS_FOUND_FLIPPED_JSON = "ic_data/star_sols_flipped.json"
STARS_CHECKED_JSON = "ic_data/stars_checked.json"
STARS_CHECKED_FLIPPED_JSON = "ic_data/stars_checked_flipped.json"

# basic properties of the grid
ROWLEN = 15
COLLEN = 15
GRIDCELLS = ROWLEN * ROWLEN
C_WALL = "█"
