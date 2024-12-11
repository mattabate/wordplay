import enum
import yaml

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


class Source(enum.Enum):
    in_consideration = 0
    active_grids = 1
    ics = 2
    ranked = 3
    words_len_10 = 4
    solutions = 5


# Load the YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access the configuration values
forward_search = config["forward_search"]
backward_search = config["backward_search"]
sort_parameters = config["api_sort_parameters"]

# Use the values in your code
IC_TYPE = forward_search["mode"]
if IC_TYPE == "AD":
    mode = Mode.AD
elif IC_TYPE == "DA":
    mode = Mode.DA
elif IC_TYPE == "A":
    mode = Mode.A
elif IC_TYPE == "":
    mode = Mode.MIN

f_verbose = forward_search["f_verbose"]
f_save_words_used = forward_search["f_save_words_used"]
f_save_bounds = forward_search["f_save_bounds"]
SLEEP_DURATION = forward_search["sleep_duration"]
RESTART_AT_LEVEL = forward_search["restart_at_level"]
MAX_LEVEL_FOR_ACTIVE_ADD = forward_search["max_level_for_active_add"]
SEARCH_W_FLIPPED = forward_search["f_search_with_flipped"]
MAX_WAL = forward_search["max_walls"]


SLEEP_DURATION_GRID = backward_search["sleep_duration_grid"]
GRID_KILL_STEP = backward_search["grid_kill_step"]


# API Sort
if sort_parameters["word_source"] == "in_consideration":
    WORDS_SOURCE = Source.in_consideration
elif sort_parameters["word_source"] == "active_grids":
    WORDS_SOURCE = Source.active_grids
elif sort_parameters["word_source"] == "ics":
    WORDS_SOURCE = Source.ics
elif sort_parameters["word_source"] == "ranked":
    WORDS_SOURCE = Source.ranked
elif sort_parameters["word_source"] == "words_len_10":
    WORDS_SOURCE = Source.words_len_10
elif sort_parameters["word_source"] == "solutions":
    WORDS_SOURCE = Source.solutions
WITHOUT_CLUES_ONLY = sort_parameters["without_clues_only"]
DELETE_ACTIVE = sort_parameters["delete_active"]


GRID_TEMPLATE = [
    "___@@@█@@@_█___",
    "___@@@█@@@@█___",
    "___@@@█@@@@█___",
    "███__@______@@@",
    "@@@________@@@@",
    "@@@_________███",
    "@@@_________@@@",
    "@@@_________@@@",
    "@@@_________@@@",
    "███_________@@@",
    "@@@@________@@@",
    "@@@______@__███",
    "___█@@@@█@@@___",
    "___█@@@@█@@@___",
    "___█_@@@█@@@___",
]

GRID_TEMPLATE_FLIPPED = [s[::-1] for s in GRID_TEMPLATE]


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
STAR_HEIGHT = 6  # DO NOT CHANGE
STAR_WIDTH = 6  # DO NOT CHANGE
STAR_START = (12, 12)  # DO NOT CHANGE


STAR_TEMPLATE = [
    "@@@@@@",
    "@@@@@@",
    "@@@@@@",
    "@@@@@@",
    "@@@@@@",
    "@@@@@@",
]

STAR_FLIPPED_TEMPLATE = [s[::-1] for s in STAR_TEMPLATE]

STAR_ROWS_OF_INTEREST = [2, 3, 4, 5, 6, 7]
STAR_COLS_OF_INTEREST = [3, 4, 5, 6, 7, 8]


def get_failures_json(type: str, max_walls: int, flipped: bool = False) -> str:
    if flipped:
        return f"failures/square_failures_{type}_{max_walls}_flipped.json"
    return f"failures/square_failures_{type}_{max_walls}.json"


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
STARS_FOUND_JSON = "ic_data/corner_squares.json"
STARS_FOUND_FLIPPED_JSON = "ic_data/corner_squares_flipped.json"
STARS_CHECKED_JSON = "ic_data/stars_checked.json"
STARS_CHECKED_FLIPPED_JSON = "ic_data/stars_checked_flipped.json"

# basic properties of the grid
ROWLEN = 15
COLLEN = 15
GRIDCELLS = ROWLEN * ROWLEN
C_WALL = "█"


# embed_seperate.py
EMB_PREF = "ANSWER: "
EMB_MODL = "text-embedding-3-small"
PKL_MODL = "matts_preferences.pkl"
