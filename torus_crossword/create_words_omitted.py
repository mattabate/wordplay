import json
import tqdm
from lib import T_YELLOW, T_NORMAL, load_json, write_json

MASTER_WL_JSON = "crossword_words.json"
WORDS_CONSIDERED = "word_list.json"
SAV_FILE = "words_omitted.json"


### DO NOT EDIT BELOW THIS LINE ###
MIN_SOCRE = 30
###                             ###

scored_words = load_json(MASTER_WL_JSON)

print(T_YELLOW + "Len Wordlist:" + T_NORMAL, len(scored_words))

current_list = load_json(WORDS_CONSIDERED)

admissible = []
for word, score in scored_words:
    word = word.replace("-", "").replace("'", "")
    if 2 < len(word) < 15 and score >= MIN_SOCRE:
        admissible.append(word)

print(T_YELLOW + "Num Admittable:" + T_NORMAL, len(admissible))

words_omitted = [
    word for word in tqdm.tqdm(admissible, leave=False) if word not in current_list
]

print(T_YELLOW + "Number of Candidaes:" + T_NORMAL, len(current_list))
print(T_YELLOW + "Num Omitted:" + T_NORMAL, len(words_omitted))

write_json(SAV_FILE, words_omitted)
