# determine if any living stars are in wins

import tqdm

import torus

from lib import get_star_from_grid, T_PINK, T_YELLOW, T_NORMAL
from config import (
    IC_TYPE,
    MAX_WAL,
    SEARCH_W_FLIPPED,
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    get_failures_json,
    get_bad_solutions_json,
)

if SEARCH_W_FLIPPED:
    stars_found = torus.json.load_json(STARS_FOUND_FLIPPED_JSON)
else:
    stars_found = torus.json.load_json(STARS_FOUND_JSON)

stars_failed = torus.json.load_json(
    get_failures_json(type=IC_TYPE, max_walls=MAX_WAL, flipped=SEARCH_W_FLIPPED)
)


JSON_FILLED_GRIDS_BAD = get_bad_solutions_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)
filled_grids_bad = torus.json.load_json(JSON_FILLED_GRIDS_BAD)


print("Sourcing from:", JSON_FILLED_GRIDS_BAD)
print("Number of bad solutions", len(filled_grids_bad))
stars_in_bad_solutions = []
# gets every bad solution
for b in tqdm.tqdm(filled_grids_bad):
    s = get_star_from_grid(b, SEARCH_W_FLIPPED)
    stars_in_bad_solutions.append(s) if s not in stars_in_bad_solutions else None


print("num stars in bad solutions:", len(stars_in_bad_solutions))


stars_to_check = []
print("num stars failed:", len(stars_failed))
for star in tqdm.tqdm(stars_in_bad_solutions):
    star_str = "".join(star)
    if star_str in stars_failed:
        print(T_PINK + "star is falied:", star_str + T_NORMAL)
    else:
        stars_to_check.append(star)
        print(T_YELLOW + "star is living:", star_str + T_NORMAL)


print("num stars to check:", len(stars_found))
print("num to check:", len(stars_to_check))
