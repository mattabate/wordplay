import json
import time
import tqdm
from config import C_WALL
from torus.json import append_json, load_json
from config import (
    NEW_STARS_FOUND_JSON,
    NEW_STARS_FOUND_FLIPPED_JSON,
    NEW_STARS_CHECKED_JSON,
    NEW_STARS_CHECKED_FLIPPED_JSON,
    STARS_CHECKED_FLIPPED_JSON,
    STAR_SEARCH_W_FLIPPED,
    STAR_SEARCH_VERBOSE,
    STARS_CHECKED_JSON,
    STAR_TEMPLATE,
    STAR_FLIPPED_TEMPLATE,
)
from lib import (
    Direction,
    Sqaure,
    Word,
    WORDLIST_BY_LEN,
    transpose,
    replace_char_in_grid,
    T_NORMAL,
    T_GREEN,
    T_PINK,
)
from torus.strings import get_prefix, get_suffix

f_verbose = STAR_SEARCH_VERBOSE

# across words length 9
# down words length 8
TEMPLATE = ["@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@", "@@@@@@"]
if not STAR_SEARCH_W_FLIPPED:
    SOL_JSON = NEW_STARS_FOUND_JSON
    CHE_JSON = NEW_STARS_CHECKED_JSON
else:
    SOL_JSON = NEW_STARS_FOUND_FLIPPED_JSON
    CHE_JSON = NEW_STARS_CHECKED_FLIPPED_JSON

# testing these here for now
words_for_across = WORDLIST_BY_LEN[9]

across_pref_set = list(set(get_prefix(word=w, len_pref=6) for w in words_for_across))
across_suff_set = list(set(get_suffix(word=w, len_suff=6) for w in words_for_across))


seen_previously = load_json(STARS_CHECKED_FLIPPED_JSON)

prefixes_seen = list(set(get_prefix(word=w, len_pref=6) for w in seen_previously))

word_to_add = []
for s in tqdm.tqdm(prefixes_seen):
    words_with_suffix = [
        w for w in words_for_across if w.startswith(s)
    ]  # all possible words in wordlist with that suffix

    for x in words_with_suffix:
        if x not in seen_previously:
            break
    else:
        word_to_add.append(s)

with open("ic_data/new_stars_checked_flipped.json", "w") as f:
    json.dump(word_to_add, f, indent=4)
