"""
    this script is going to find every star that is in star_sols but not in fails
    then it finds all the contained words
"""

import torus

from lib import string_to_star
from config import (
    C_WALL,
    STAR_ROWS_OF_INTEREST,
    STAR_COLS_OF_INTEREST,
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    get_failures_json,
    IC_TYPE,
    MAX_WAL,
    SEARCH_W_FLIPPED,
)
import migrations.database
from migrations.schema import ReviewStatus


def get_words_in_star(star):
    all_words = set()
    for r in STAR_ROWS_OF_INTEREST:
        word = star[r].replace(C_WALL, "")
        all_words.add(word)

    for c in STAR_COLS_OF_INTEREST:
        word = "".join([star[r][c] for r in range(10)]).replace(C_WALL, "")
        all_words.add(word)

    return all_words


if __name__ == "__main__":
    FAI_JSON = get_failures_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)

    if SEARCH_W_FLIPPED:
        sol_strs = torus.json.load_json(STARS_FOUND_FLIPPED_JSON)
    else:
        sol_strs = torus.json.load_json(STARS_FOUND_JSON)

    fails_set = set(torus.json.load_json(FAI_JSON))

    good_star_strs = [s for s in sol_strs if s not in fails_set]

    words_approved = migrations.database.get_words_by_status(ReviewStatus.APPROVED)

    print("number words in all ics", len(good_star_strs))
    all_words = set()
    for s in good_star_strs:
        star = string_to_star(s)
        all_words |= get_words_in_star(star)

    all_words = all_words - set(words_approved)

    # Filter words to include only those in all_words, sort by score
    # highest to lowest
    sorted_words = sorted(
        (
            [word, float(migrations.database.get_word_world_score(word))]
            for word in all_words
        ),
        key=lambda w: w[1],
        reverse=True,
    )

    torus.json.write_json(
        "filter_words/sorted_words_in_ics.json", [w for w, _ in sorted_words]
    )
