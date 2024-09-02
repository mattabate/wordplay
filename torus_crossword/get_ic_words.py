"""
    this script is going to find every star that is in sols
    but not in fails and then it is going to take hose and get the number of wor
"""

import json
import os
import tqdm
from lib import C_WALL, load_json, transpose, string_to_star

TYPE = "AD"  # TORUS ACROSS
MAX_WALLS = 42
STA_JSON = "star_sols.json"
FAI_JSON = f"failures/15x15_stars_failures_{TYPE}_{MAX_WALLS}.json"

sol_strs = load_json(STA_JSON)
fail_strs = load_json(FAI_JSON)
fails_set = set(fail_strs)

good_star_strs = [s for s in sol_strs if s not in fails_set]

all_words = set()
for s in good_star_strs:
    star = string_to_star(s)
    ROWS_OF_INTEREST = [2, 3, 4, 5, 6, 7]

    COLS_OF_INTEREST = [3, 4, 5, 6, 7, 8]
    for r in ROWS_OF_INTEREST:
        word = star[r].replace(C_WALL, "")
        all_words.add(word)

print(len(all_words))
with open("delete.json", "w") as file:
    json.dump(list(all_words), file, indent=4, ensure_ascii=False)
