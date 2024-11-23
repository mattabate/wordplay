from config import (
    ACTIVE_WORDS_JSON,
    WORDS_APPROVED_JSON,
    SCORES_DICT_JSON,
    WORDS_CONSIDERED_JSON,
)

import torus


# scored words
active_words = torus.json.load_json(ACTIVE_WORDS_JSON)
considered_words = torus.json.load_json(WORDS_CONSIDERED_JSON)
scored_dict = torus.json.load_json(SCORES_DICT_JSON)  # scored words

approved_words = torus.json.load_json(WORDS_APPROVED_JSON)

sorted_active_words = sorted(
    (word for word in active_words if word in scored_dict),
    key=lambda word: scored_dict[word],
    reverse=True,  # Set to False if you want ascending order
)

sorted_considered_words = sorted(
    (word for word in considered_words if word in scored_dict),
    key=lambda word: scored_dict[word],
    reverse=True,  # Set to False if you want ascending order
)

torus.json.write_json(ACTIVE_WORDS_JSON, list(set(sorted_active_words)))
torus.json.write_json(WORDS_CONSIDERED_JSON, list(set(sorted_considered_words)))
torus.json.write_json(WORDS_APPROVED_JSON, list(set(approved_words)))
