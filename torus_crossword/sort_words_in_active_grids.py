from config import ACTIVE_WORDS_JSON, SCORED_WORDS_JSON
import json
from torus.json import load_json, write_json


active_words = load_json(ACTIVE_WORDS_JSON)
scored_words = load_json(SCORED_WORDS_JSON)
# here is the format of scored_words.
# scored_words = [
#   [
#     "ABRIGHTFUTURE",
#     50
#   ],
#   [ ..
# note that active_words is a list of strings, not a list of lists

scored_dict = {word_score[0]: word_score[1] for word_score in scored_words}

sorted_active_words = sorted(
    (word for word in active_words if word in scored_dict),
    key=lambda word: scored_dict[word],
    reverse=True,  # Set to False if you want ascending order
)

print(sorted_active_words)


exit()
print(json.dumps(active_words, indent=2))
# sort active_words by score from scored_words
active_words = sorted(
    active_words, key=lambda x: scored_words.index([x, 0]), reverse=True
)
print("====")
print(json.dumps(active_words, indent=2))

# save_json(ACTIVE_WORDS_JSON, active_words)
