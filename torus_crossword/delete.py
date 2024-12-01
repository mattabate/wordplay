import torus
import tqdm
import json
from lib import string_to_star
from config import STAR_ROWS_OF_INTEREST, STAR_COLS_OF_INTEREST

flipped_stars = torus.json.load_json("ic_data/star_sols_flipped.json")
flipped_stars_bad = torus.json.load_json(
    "failures/15x15_stars_failures_DA_40_flipped.json"
)
corner_squares = torus.json.load_json("ic_data/corner_squares_flipped.json")


def get_star_inner_square(star_string):
    star = string_to_star(star_string)
    impt_rows = [star[i] for i in STAR_ROWS_OF_INTEREST]
    inner_square = []
    for row in impt_rows:
        inner_square.append("".join([row[i] for i in STAR_COLS_OF_INTEREST]))
    return inner_square


living_stars = set(flipped_stars) - set(flipped_stars_bad)
print("stars found:", len(flipped_stars))
print("bad stars found:", len(flipped_stars_bad))
print("number living stars:", len(living_stars))

all_square_strings = set()
for s in tqdm.tqdm(living_stars):
    # print(json.dumps(string_to_star(s), indent=4, ensure_ascii=False))
    # print(json.dumps(get_star_inner_square(s), indent=4, ensure_ascii=False))
    q = "".join(get_star_inner_square(s))
    all_square_strings.add(q)

# get
print("corner squares found:", len(corner_squares))
print("squares from living stars:", len(all_square_strings))

dead_squares = set(corner_squares) - all_square_strings
print("dead squares found:", len(dead_squares))

with open("failures/square_failures_DA_40_flipped.json", "w") as f:
    json.dump(list(dead_squares), f, indent=4)
