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

###############################################
# main.py config
# searches for completed 15x15 grid given initial conditions
###############################################

# Config for maip.py 15x15 search
# Note editing may cause big problems

IC_TYPE = "AD"
SEARCH_W_FLIPPED = False
# note - WE HAVE GOOD for AD, 42, not flipped [but no solutions for 40]

# IC_TYPE = "DA"  # da = flipped
# SEARCH_W_FLIPPED = True

# IC_TYPE = "A"  # A = flipped
# SEARCH_W_FLIPPED = True

MAX_WAL = 42
f_verbose = True
f_save_words_used = True
f_save_bounds = [1, 4]
SLEEP_DURATION = -1

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

GRID_TEMPLATE_FLIPPED = [
    "___█_@@@█______",
    "___█@@@@█______",
    "___█@@@@█______",
    "_________@__███",
    "@@@@________@@@",
    "███_________@@@",
    "@@@_________@@@",
    "@@@_________@@@",
    "@@@_________@@@",
    "@@@_________███",
    "@@@________@@@@",
    "███__@_________",
    "______█@@@@█___",
    "______█@@@@█___",
    "______█@@@_█___",
]


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
STAR_SEARCH_W_FLIPPED = True  # False on personal computer
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
