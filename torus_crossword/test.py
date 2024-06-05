import json
import numpy as np


ROWLEN = 15


def replace_char_at(string, char, index):
    # Check if index is within the bounds of the string
    if index < 0:
        index += len(string)
    if index >= len(string) or index < 0:
        return string  # Return the original string if index is out of bounds
    return string[:index] + char + string[index + 1 :]


with open("words.json") as f:
    word_list = json.load(f)

for i, w in enumerate(word_list):
    word_list[i] = "." + w + "."

line = "a.bb???ab.cb.I."
print()
print(line)
print()

if len(line) != ROWLEN:
    print("Invalid row length", len(line))
    exit()


def word_islands_indexes(line: str) -> list[list[int]]:
    """with wrapping"""
    """
    Example: "NB@??.C?T.D??RI" -> [[5, 6], [8, 9, 10], [13, 14, 15, 16, 17]]
    """
    if "?" not in line:
        # TODO: make sure we exit here - if row full, cant do any of the stuff below
        return []

    qm_positions = [index for index, char in enumerate(line) if char == "?"]
    qm_positions.append(ROWLEN)
    result: list[int] = []

    for i in range(len(qm_positions) - 1):
        in_between = list(range(qm_positions[i] + 1, qm_positions[i + 1]))
        if in_between:
            result.append(in_between)

    wrap = line.find("?")
    if wrap:
        result[-1].extend([ROWLEN + i for i in range(wrap)])

    return result


word_islands = word_islands_indexes(line)

sub_strings = []
for li in word_islands:
    word = "".join(line[c % ROWLEN] for c in li)
    sub_strings.append(
        (
            li[0],
            word,
        )
    )


print("sub_strings", sub_strings)
print()

FINAL = []
for i, s in sub_strings:  # starting index, word
    periods = s.split(".")

    if len(periods) == 1:
        FINAL.append(("substring", i, s))
        continue

    if periods[0]:
        # this actually works
        FINAL.append(("suffix", i, periods[0] + "."))

    if periods[-1]:
        FINAL.append(("prefix", i + len(s) - len(periods[-1]) - 1, "." + periods[-1]))

    spots = [j for j, c in enumerate(s) if c == "."]

    for j in range(1, len(periods) - 1):
        FINAL.append(("infix", i + spots[j - 1], "." + periods[j] + "."))


print(json.dumps(FINAL, indent=4))
exit()

print(FINAL)
exit()
line = "NG??.CAT.D??RI"
chunks = line.split("?")
print(chunks)
print(len(chunks) + sum(len(c) for c in chunks))


# DO NOT RECOMPUTE POSSIBILITIES FOR HALF AREAS
