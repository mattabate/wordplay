import json
import numpy as np
import time

ROWLEN = 15

with open("words.json") as f:
    WORDLIST = json.load(f)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = "." + w + "."


def replace_char_at(string, char, index):
    # Check if index is within the bounds of the string
    if index < 0:
        index += len(string)
    if index >= len(string) or index < 0:
        return string  # Return the original string if index is out of bounds
    return string[:index] + char + string[index + 1 :]


def word_islands_indexes(line: str) -> list[list[int]]:
    """with wrapping"""
    """
    Example: "a.bb???ab?c@.@." -> [(7, 'ab'), (10, 'c@.@.a.bb')]
    """
    if "?" not in line:
        # TODO: make sure we exit here - if row full, cant do any of the stuff below
        return []

    qm_positions = [index for index, char in enumerate(line) if char == "?"]
    qm_positions.append(ROWLEN)

    # looks like: [[5, 6], [8, 9, 10], [13, 14, 15, 16, 17]]
    word_islands: list[int] = []
    for i in range(len(qm_positions) - 1):
        in_between = list(range(qm_positions[i] + 1, qm_positions[i + 1]))
        if in_between:
            word_islands.append(in_between)

    wrap = line.find("?")
    if wrap:
        word_islands[-1].extend([ROWLEN + i for i in range(wrap)])

    sub_strings = []
    for li in word_islands:
        word = "".join(line[c % ROWLEN] for c in li)
        sub_strings.append(
            (
                li[0],
                word,
            )
        )

    return sub_strings


def word_fixtures(sub_strings: list[tuple[int, str]]) -> list[tuple[str, int, str]]:
    word_fixtures = []
    for i, s in sub_strings:  # starting index, word
        periods = s.split(".")

        if len(periods) == 1:
            word_fixtures.append(("substring", i, s))
            continue

        if periods[0]:
            # this actually works
            word_fixtures.append(("suffix", i, periods[0] + "."))

        if periods[-1]:
            word_fixtures.append(
                ("prefix", i + len(s) - len(periods[-1]) - 1, "." + periods[-1])
            )

        spots = [j for j, c in enumerate(s) if c == "."]

        for j in range(1, len(periods) - 1):
            if "@" in periods[j]:
                word_fixtures.append(
                    ("infix", i + spots[j - 1], "." + periods[j] + ".")
                )

    return word_fixtures


if __name__ == "__main__":
    line = "A.BB???AB?C@..."
    # line = "???????????????"
    # line = "ABCDEDF..AA.AAA"
    print()
    print("line:", line)
    print()

    if len(line) != ROWLEN:
        print("Invalid row length", len(line))
        exit()

    t0 = time.time()

    sub_strings = word_islands_indexes(line)
    fixtures = word_fixtures(sub_strings)

    print("processing time", time.time() - t0)
    print("sub_strings", sub_strings)
    print()
    print(json.dumps(fixtures, indent=4))

    for type, i, cont in fixtures:
        if type == "suffix":
            1
