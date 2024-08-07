import json
import tqdm
from lib import T_YELLOW, T_NORMAL

MASTER_WL_JSON = "crossword_words.json"
WORDS_CONSIDERED = "word_list.json"
SAV_FILE = "words_omitted.json"


### DO NOT EDIT BELOW THIS LINE ###
MIN_SOCRE = 30
###                             ###


with open(MASTER_WL_JSON, "r") as f:
    scored_words = json.load(f)

print(T_YELLOW + "Len Wordlist:" + T_NORMAL, len(scored_words))

with open(WORDS_CONSIDERED, "r") as f:
    current_list = json.load(f)

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

with open(SAV_FILE, "w") as f:
    json.dump(words_omitted, f, indent=2)
