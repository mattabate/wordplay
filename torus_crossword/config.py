# the wordlist contains all words in consideration for the search
# the format is a list of strings, about 100k total
WOR_JSON = "wordlist/word_list.json"
SCORED_WORDS_JSON = "wordlist/scored_words.json"
ACTIVE_WORDS_JSON = "wordlist/words_in_active_grids.json"
WORDS_OMITTED_JSON = "wordlist/words_omitted.json"


# initial conditions for the search are refered to as stars
# stars come in two flavors: normal and flipped
# files where the stars are stored are named star_sols.json and star_sols_flipped.json
STARS_FOUND_JSON = "star_sols.json"
STARS_FOUND_FLIPPED_JSON = "star_sols_flipped.json"

STARS_CHECKED_JSON = "stars_checked.json"
STARS_CHECKED_FLIPPED_JSON = "stars_checked_flipped.json"

# basic properties of the grid
ROWLEN = 15
COLLEN = 15
GRIDCELLS = ROWLEN * ROWLEN
C_WALL = "█"

# Config for maip.py 15x15 search
# Note editing may cause big problems
IC_TYPE = "AD"
MAX_WAL = 42
SEARCH_W_FLIPPED = False

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


GRID_TEMPLATE = [
    "______█_@@_█___",
    "______█_@@_█___",
    "______█_@@_█___",
    "███__@_________",
    "___________@___",
    "____________███",
    "@@@____________",
    "_______________",
    "____________@@@",
    "███____________",
    "___@___________",
    "_________@__███",
    "___█_@@_█______",
    "___█_@@_█______",
    "___█_@@_█______",
]

GRID_TEMPLATE_FLIPPED = [s[::-1] for s in GRID_TEMPLATE]
