"""
    this script is going to find every star that is in star_sols but not in fails
    then it finds all the contained words
"""

from config import C_WALL
from torus.json import load_json, write_json
from lib import string_to_star
from config import (
    STAR_ROWS_OF_INTEREST,
    STAR_COLS_OF_INTEREST,
    STARS_FOUND_JSON,
    STARS_FOUND_FLIPPED_JSON,
    get_failures_json,
    SCORED_WORDS_JSON,
    IC_TYPE,
    MAX_WAL,
)


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
    FAI_JSON = get_failures_json(IC_TYPE, MAX_WAL)

    sol_strs = load_json(STARS_FOUND_JSON) + load_json(STARS_FOUND_FLIPPED_JSON)

    fails_set = set(load_json(FAI_JSON))

    good_star_strs = [s for s in sol_strs if s not in fails_set]

    print("number words in all ics", len(good_star_strs))
    all_words = set()
    for s in good_star_strs:
        star = string_to_star(s)
        all_words |= get_words_in_star(star)

    scored_words = load_json(SCORED_WORDS_JSON)
    # scored like [ ["word", "score"], ... ]
    # turn all words into list and sort using scores
    word_scores = {word: float(score) for word, score in scored_words}

    # Filter words to include only those in all_words, sort by score
    # highest to lowest
    sorted_words = sorted(
        ([word, word_scores[word]] for word in all_words if word in word_scores),
        key=lambda w: word_scores[w[0]],
        reverse=True,
    )

    write_json("delete.json", sorted_words)
