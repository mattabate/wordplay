# determine if any living stars are in wins

import tqdm

import torus
from lib import get_star_from_grid
from config import (
    IC_TYPE,
    MAX_WAL,
    SEARCH_W_FLIPPED,
    STARS_FOUND_FLIPPED_JSON,
    get_failures_json,
    get_bad_solutions_json,
)


stars_found = torus.json.load_json(STARS_FOUND_FLIPPED_JSON)

stars_failed = torus.json.load_json(
    get_failures_json(type=IC_TYPE, max_walls=MAX_WAL, flipped=SEARCH_W_FLIPPED)
)


bad_solutions_json = get_bad_solutions_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)
bad_solutions = torus.json.load_json(bad_solutions_json)

import json

print("json containing bad solutions:", bad_solutions_json)
print("number of bad solutions", len(bad_solutions))
stars_in_bad_solutions = []
for b in tqdm.tqdm(bad_solutions):
    s = get_star_from_grid(b, SEARCH_W_FLIPPED)
    if s not in stars_in_bad_solutions:
        stars_in_bad_solutions.append(s)

print("num stars in bad solutions:", len(stars_in_bad_solutions))

from lib import T_YELLOW, T_NORMAL

stars_to_check = []
print("num stars failed:", len(stars_failed))
for star in tqdm.tqdm(stars_in_bad_solutions):
    star_str = "".join(star)
    if star_str not in stars_failed:
        stars_to_check.append(star)
        print("star not in failed:", "".join(star))
    else:
        print(T_YELLOW + star_str + T_NORMAL)


print("num to check:", len(stars_to_check))
