import tqdm
from torus.json import append_json, load_json
import json
from lib import (
    WORDLIST_BY_LEN,
)
from torus.strings import get_prefix, get_suffix


# testing these here for now
words_for_across = WORDLIST_BY_LEN[14]

words = set()
for w in tqdm.tqdm(words_for_across):
    w1 = w[::4]
    w2 = w[1::4]
    w3 = w[2::4]
    w4 = w[3::4]
    if (
        w1 in WORDLIST_BY_LEN[len(w1)]
        and w2 in WORDLIST_BY_LEN[len(w2)]
        and w3 in WORDLIST_BY_LEN[len(w3)]
        and w4 in WORDLIST_BY_LEN[len(w4)]
    ):
        print(w, w1, w2, w3, w4)
