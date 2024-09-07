import tqdm
from config import WOR_JSON, WORDS_OMITTED_JSON
from torus.json import load_json, write_json
from lib import T_YELLOW, T_NORMAL

MASTER_WL_JSON = "wordlist/scored_words.json"


### DO NOT EDIT BELOW THIS LINE ###
MIN_SOCRE = 30
###                             ###

scored_words = load_json(MASTER_WL_JSON)

print(T_YELLOW + "Len Wordlist:" + T_NORMAL, len(scored_words))

current_list = load_json(WOR_JSON)

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

write_json(WORDS_OMITTED_JSON, words_omitted)
