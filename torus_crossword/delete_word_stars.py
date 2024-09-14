"""Given a bad word, remove it from all stars and the word_list"""

from config import WOR_JSON, STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON
from torus.json import load_json, write_json
from lib import transpose, string_to_star

word = "TEDDYBOYS"

words = load_json(WOR_JSON)


for file in [STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON]:
    star_sols = load_json(file)
    initial_num = len(star_sols)
    new_star_sols = []

    for star_str in star_sols:
        star = string_to_star(star_str)

        fails = False
        for line in star:
            # HACK: note that this can remove a word that is part of another word - terrible
            if word in line:
                break
        else:
            for line in transpose(star):
                if word in line:
                    break
            else:
                new_star_sols.append(star_str)

    final_num = len(new_star_sols)
    print("number ics removed ", initial_num - final_num)
    write_json(file, new_star_sols)

# remove the word from the word list
words = set(words)
if word in words:
    print("removing " + word + " from word list")
    words.remove(word)
    write_json(WOR_JSON, list(words))
