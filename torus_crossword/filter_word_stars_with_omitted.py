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
import tqdm

words_ommitted = load_json(WORDS_OMITTED_JSON)

print("(1) Remove Duplicate Stars")
for file in [STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON]:
    star_sols = load_json(file)
    initial_num = len(star_sols)
    new_star_sols = list(set(star_sols))
    final_num = len(new_star_sols)
    print(f"number ics removed  from {file}:", initial_num - final_num)
    write_json(file, new_star_sols)


print("(2) Check for omitted words in stars")
words_found = set()
for file in [STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON]:
    star_sols = load_json(file)
    initial_num = len(star_sols)
    new_star_sols = []

    for star_str in tqdm.tqdm(star_sols):
        star = string_to_star(star_str)

        fails = False
        for line in star:
            # HACK: assumes no line of star with two words
            word_considered = line.replace(C_WALL, "")
            if len(word_considered) > 4 and word_considered in words_ommitted:
                words_found.add(word_considered)
                break
        else:
            for line in transpose(star):
                word_considered = line.replace(C_WALL, "")
                if len(word_considered) > 4 and word_considered in words_ommitted:
                    words_found.add(word_considered)
                    break
            else:
                new_star_sols.append(star_str)

    final_num = len(new_star_sols)
    print(f"number ics removed from {file}:", initial_num - final_num)
    print(f"words found in {file}:", words_found)
    write_json(file, new_star_sols)
