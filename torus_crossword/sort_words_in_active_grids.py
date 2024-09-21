from config import (
    ACTIVE_WORDS_JSON,
    WORDS_APPROVED_JSON,
    SCORED_WORDS_JSON,
    WORDS_CONSIDERED_JSON,
)
import json
from torus.json import load_json, write_json


# scored words
active_words = load_json(ACTIVE_WORDS_JSON)
considered_words = load_json(WORDS_CONSIDERED_JSON)
scored_words = load_json(SCORED_WORDS_JSON)

scored_dict = {word_score[0]: word_score[1] for word_score in scored_words}


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

write_json(ACTIVE_WORDS_JSON, sorted_active_words)
write_json(WORDS_CONSIDERED_JSON, sorted_considered_words)
