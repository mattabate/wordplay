import random
import requests
import time

from bs4 import BeautifulSoup

import torus
from lib import T_YELLOW, T_PINK, T_NORMAL, T_GREEN, T_BLUE
from config import (
    WORDS_CONSIDERED_JSON,
    WORDS_APPROVED_JSON,
    WOR_JSON,
    WORDS_OMITTED_JSON,
    ACTIVE_WORDS_JSON,
)

import enum


class Source(enum.Enum):
    in_consideration: int = 0
    active_grids: int = 1
    bad_words: int = 2
    good_words: int = 3


source = Source.bad_words

without_clues_only = False
f_delete_active = False

words_omitted = torus.json.load_json(WORDS_OMITTED_JSON)
words_appoved = torus.json.load_json(WORDS_APPROVED_JSON)
words_seen = set(words_omitted + words_appoved)


if source == Source.active_grids:
    torus.json.write_json(
        WORDS_CONSIDERED_JSON, torus.json.load_json(ACTIVE_WORDS_JSON)
    )
    if f_delete_active:
        torus.json.write_json(ACTIVE_WORDS_JSON, [])
if source == Source.bad_words:
    torus.json.write_json(
        WORDS_CONSIDERED_JSON, torus.json.load_json("filter_words/assumed_bad.json")
    )
    if f_delete_active:
        torus.json.write_json(ACTIVE_WORDS_JSON, [])
if source == Source.good_words:
    torus.json.write_json(
        WORDS_CONSIDERED_JSON, torus.json.load_json("filter_words/assumed_good.json")
    )
    if f_delete_active:
        torus.json.write_json(ACTIVE_WORDS_JSON, [])

words_condered = torus.json.load_json(WORDS_CONSIDERED_JSON)


num_printed = 6
params = {"search_redirect": "True"}

# Define headers for the request
headers = {
    # Headers as defined previously
}


for word in words_condered:
    url = f"https://crosswordtracker.com/answer/{word.lower()}/"
    print(f"Word:", T_GREEN + f"{" ".join(word.upper())}" + T_NORMAL)
    if word in words_seen:
        print(T_PINK + "> Already seen" + T_NORMAL + "\n")
        torus.json.remove_from_json_list(WORDS_CONSIDERED_JSON, word)
        continue

    try:
        response = requests.get(url, headers=headers, params=params)
        code = response.status_code
        print(f"Response Code: {code}")
    except:
        code = 1

    if code != 200:
        print(T_PINK + f"No Clues Found for '{word}'" + T_NORMAL)
    else:
        print(T_BLUE + f"Clues Found for '{word}'" + T_NORMAL + "... Skipping \n")
        time.sleep(random.random() * 2)
        if without_clues_only:
            continue
        soup = BeautifulSoup(response.text, "lxml")
        clue_container = soup.find(
            "h3", string="Referring crossword puzzle clues"
        ).find_next_sibling("div")
        clues = clue_container.find_all("li")

        for clue in clues[:num_printed]:
            print("-", clue.get_text())

    resp = input(
        "\n"
        + T_YELLOW
        + "P"
        + T_NORMAL
        + ": to save"
        + " | "
        + T_YELLOW
        + "O"
        + T_NORMAL
        + ": to rejct"
        + "\nresponse: "
        + T_YELLOW
    )
    print(T_NORMAL)

    if resp.lower() in ["p", "d"]:
        print("Saving as approved")
        torus.json.append_json(WORDS_APPROVED_JSON, word)
        torus.json.remove_from_json_list(WORDS_CONSIDERED_JSON, word)

    elif resp.lower() in ["o", "s"]:
        print("Saving as Rejected")
        torus.json.append_json(WORDS_OMITTED_JSON, word)
        torus.json.remove_from_json_list(WOR_JSON, word)
        torus.json.remove_from_json_list(WORDS_CONSIDERED_JSON, word)
    else:
        print("Invalid Response")

    print("\n" + "-" * 50 + "\n")
