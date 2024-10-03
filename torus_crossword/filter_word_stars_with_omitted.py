"""Given a bad word, remove it from all stars and the word_list"""

from config import (
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    WORDS_OMITTED_JSON,
    WORDS_APPROVED_JSON,
    C_WALL,
    STAR_ROWS_OF_INTEREST,
    STAR_COLS_OF_INTEREST,
    BAD_STAR_JSON,
    BAD_STAR_FLIPPED_JSON,
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
    if initial_num != final_num:
        write_json(file, new_star_sols)


print("(2) Check for omitted words in stars")
words_found = set()
for is_flipped in [False, True]:
    if is_flipped:
        file = STARS_FOUND_FLIPPED_JSON
        bad_stars_json = BAD_STAR_FLIPPED_JSON
    else:
        file = STARS_FOUND_JSON
        bad_stars_json = BAD_STAR_JSON
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
    if words_found:
        old_bad_stars = load_json(bad_stars_json)
        for x in set(star_sols) - set(new_star_sols):
            old_bad_stars.append(x)
        write_json(bad_stars_json, old_bad_stars)

        # save the remaining stars
        write_json(file, new_star_sols)


print("(3) collect all down words in stars")
already_seen = load_json(WORDS_APPROVED_JSON)
across_words = dict()
for file in [STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON]:
    star_sols = load_json(file)
    for star_str in tqdm.tqdm(star_sols):
        star = string_to_star(star_str)
        for r in STAR_ROWS_OF_INTEREST:
            line = star[r]
            word_considered = line.replace(C_WALL, "")
            if word_considered in already_seen:
                continue
            entry = across_words.get(word_considered, 0)
            across_words[word_considered] = entry + 1

write_json("filter_words/all_words_in_ics.json", across_words)
# sort the keys by value (largest to smallest) and then save as list of strings (just key, forget value)
sorted_words = sorted(across_words, key=across_words.get, reverse=True)
write_json("filter_words/sorted_words_in_ics.json", sorted_words)
