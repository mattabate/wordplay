from lib import (
    WORDLIST,
    WORDLIST_BY_LEN,
)


# # testing these here for now
# words_for_across = WORDLIST_BY_LEN[14]

# words = set()
# for w in tqdm.tqdm(words_for_across):
#     w1 = w[::4]
#     w2 = w[1::4]
#     w3 = w[2::4]
#     w4 = w[3::4]
#     if (
#         w1 in WORDLIST_BY_LEN[len(w1)]
#         and w2 in WORDLIST_BY_LEN[len(w2)]
#         and w3 in WORDLIST_BY_LEN[len(w3)]
#         and w4 in WORDLIST_BY_LEN[len(w4)]
#     ):
#         print(w, w1, w2, w3, w4)

for w in WORDLIST:
    w1 = w[::2]
    w2 = w[1::2]
    if w == w1 + w2 or w == w2 + w1:
        print(w, w1, w2)
