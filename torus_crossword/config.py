# the wordlist contains all words in consideration for the search
# the format is a list of strings, about 100k total
WOR_JSON = "word_list.json"


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
STAR_FLIPPED_TEMPLATE = [
    "███@@@██████",
    "███@@@██████",
    "███@@@@@@@@@",
    "███@@@@@@@@@",
    "███@@@@@@@@@",
    "@@@@@@@@@███",
    "@@@@@@@@@███",
    "@@@@@@@@@███",
    "██████@@@███",
    "██████@@@███",
]

STAR_ROWS_OF_INTEREST = [2, 3, 4, 5, 6, 7]
STAR_COLS_OF_INTEREST = [3, 4, 5, 6, 7, 8]
