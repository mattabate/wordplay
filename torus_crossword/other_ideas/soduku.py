from lib import (
    WORDLIST,
    WORDLIST_BY_LEN,
)
import random

# # testing these here for now
words_for_across = WORDLIST_BY_LEN[6]
# shuffle
random.shuffle(words_for_across)
combs_seen = {}
for w in words_for_across:
    # alphabatize
    key = "".join(sorted(w))
    if key in combs_seen:
        combs_seen[key].append(w)
    else:
        combs_seen[key] = [w]

# get the words that have the most anagrams
max_len = 0
max_words = []
for k, v in combs_seen.items():
    if len(v) > max_len:
        max_len = len(v)
        max_words = [v]
    elif len(v) == max_len:
        max_words.append(v)


print(max_len, max_words)
