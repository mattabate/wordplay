import requests
from bs4 import BeautifulSoup
from lib import T_YELLOW, T_PINK, T_NORMAL
from config import (
    WORDS_CONSIDERED_JSON,
    WORDS_APPROVED_JSON,
    WOR_JSON,
    WORDS_OMITTED_JSON,
)
from torus.json import load_json, write_json


words_condered = load_json(WORDS_CONSIDERED_JSON)

num_printed = 6
params = {"search_redirect": "True"}

# Define headers for the request
headers = {
    # Headers as defined previously
}

for word in words_condered:
    url = f"https://crosswordtracker.com/answer/{word.lower()}/"
    print(f"Word:", T_YELLOW + f"{" ".join(word.upper())}" + T_NORMAL)

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(T_PINK + f"No Clues Found for '{word}'" + T_NORMAL)
    else:
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

    if resp.lower() == "p":
        print("Saving as approved")
        words_allowed = load_json(WORDS_APPROVED_JSON)
        words_allowed.append(word)
        write_json(WORDS_APPROVED_JSON, words_allowed)

        words_condered_new = load_json(WORDS_CONSIDERED_JSON)
        new = []
        for ww in words_condered_new:
            if ww != word:
                new.append(ww)
        write_json(WORDS_CONSIDERED_JSON, new)

    elif resp.lower() == "o":
        print("Saving as Rejected")
        word_list = load_json(WOR_JSON)
        new = []
        for ww in word_list:
            if ww != word:
                new.append(ww)
        write_json(WOR_JSON, new)

        words_condered_new = load_json(WORDS_CONSIDERED_JSON)
        new = []
        for ww in words_condered_new:
            if ww != word:
                new.append(ww)
        write_json(WORDS_CONSIDERED_JSON, new)
    else:
        print("Invalid Response")

    print("\n" + "-" * 50 + "\n")
