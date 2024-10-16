import tqdm
from config import WOR_JSON, WORDS_OMITTED_JSON, SCORES_DICT_JSON
import torus
from lib import T_YELLOW, T_NORMAL


### DO NOT EDIT BELOW THIS LINE ###
MIN_SOCRE = 30
###                             ###

scored_words = torus.json.load_json(SCORES_DICT_JSON)

print(T_YELLOW + "Len Wordlist:" + T_NORMAL, len(scored_words.keys()))

current_list = torus.json.load_json(WOR_JSON)

admissible = []
for word, score in scored_words.items():
    word = word.replace("-", "").replace("'", "")
    if 2 < len(word) < 15 and score >= MIN_SOCRE:
        admissible.append(word)

print(T_YELLOW + "Num Admittable:" + T_NORMAL, len(admissible))

words_omitted = [
    word for word in tqdm.tqdm(admissible, leave=False) if word not in current_list
]

print(T_YELLOW + "Number of Candidaes:" + T_NORMAL, len(current_list))
num_omitted = len(words_omitted)
old = len(torus.json.load_json(WORDS_OMITTED_JSON))
print(T_YELLOW + "Num Omitted:" + T_NORMAL, num_omitted - old)
print(T_YELLOW + "Total Omitted:" + T_NORMAL, num_omitted)

torus.json.write_json(WORDS_OMITTED_JSON, words_omitted)
