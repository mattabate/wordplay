"""
    right now failuse are stored as grids
    trnaform the approach to save the stars that failed
"""

import json
import os
import tqdm
from lib import load_json, replace_char_in_string, STAR_START

files = os.listdir("failures/")  # contains jsons

for file in tqdm.tqdm(files):
    if not "grid" in file:
        continue

    tqdm.tqdm.write(f"Processing {file}")
    if file.endswith("_flipped.json"):
        f_flipped = True
        template = [
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
    else:
        f_flipped = False
        template = [
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

    data = load_json(f"failures/{file}")

    stars_from_file = []
    for grid_str in data:
        grid = [grid_str[i : i + 15] for i in range(0, 225, 15)]

        ROW_LEN = 15
        filled_template = template.copy()
        for i, l in enumerate(template):
            for j, c in enumerate(l):
                if template[i][j] == "█":
                    continue
                else:
                    thing = grid[(STAR_START[0] + i) % ROW_LEN][
                        (STAR_START[1] + j) % ROW_LEN
                    ]
                    filled_template[i] = replace_char_in_string(
                        filled_template[i], thing, j
                    )

        star = filled_template
        stars_from_file.append("".join(star))

    stars_from_file = list(set(stars_from_file))
    with open(f"failures/{file.replace('grid', 'stars')}", "w") as f:
        json.dump(stars_from_file, f, indent=4, ensure_ascii=False)
