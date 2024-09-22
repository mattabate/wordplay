"""Given a bad word, remove it from all stars and the word_list"""

from config import (
    WOR_JSON,
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    WORDS_OMITTED_JSON,
    C_WALL,
)
from torus.json import load_json, write_json
from lib import transpose, string_to_star

words_ommitted = load_json(WORDS_OMITTED_JSON)

print("(1) Remove Duplicate Stars")
for file in [STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON]:
    star_sols = load_json(file)
    initial_num = len(star_sols)
    new_star_sols = list(set(star_sols))
    final_num = len(new_star_sols)
    print("number ics removed ", initial_num - final_num)
    write_json(file, new_star_sols)


exit()

for file in [STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON]:
    star_sols = load_json(file)
    initial_num = len(star_sols)
    new_star_sols = []

    for star_str in star_sols:
        star = string_to_star(star_str)

        fails = False
        for line in star:
            # HACK: assumes no line of star with two words
            if line.replace(C_WALL, "") in words_ommitted:
                break
        else:
            for line in transpose(star):
                if line.replace(C_WALL, "") in words_ommitted:
                    break
            else:
                new_star_sols.append(star_str)

    final_num = len(new_star_sols)
    print("number ics removed ", initial_num - final_num)
    write_json(file, new_star_sols)
