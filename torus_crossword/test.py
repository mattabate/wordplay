import json
import time
import re

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


def get_new_templates_all(fixtures: list[tuple[str, int, str]], line: str):
    new_templates = {i:[] for t, i, c in fixtures}
    for w in WORDLIST:
        for _, i, cont in fixtures:
            pattern = cont.replace("@", "[^.]")
            matches = re.finditer(pattern, w)
            positions = [match.start() for match in matches]
            for p in positions:
                new_template = line
                for j, c in enumerate(w):
                    ooo = (i - p + j) % ROWLEN
                    if line[ooo] in [c, "?"] or (line[ooo] == "@" and c != "."):
                        new_template = new_template[:ooo] + c + new_template[ooo + 1 :]
                        continue
                    break
                else:
                    # clean to convert .?. and .??. to ... and ....
                    pattern = r"\.[A-Za-z]\."
                    if bool(re.search(pattern, new_template+new_template)):
                        continue
                    pattern = r"\.[A-Za-z]{2}\."
                    if bool(re.search(pattern, new_template+new_template)):
                        continue

                    new_template = new_template.replace('.?.', '...').replace('.??.', '....')
                    new_templates[i].append(new_template)

    return new_templates
                        

            
def get_new_templates(fixtures: list[tuple[str, int, str]], line: str) -> list[str]:
    new_tempalates = get_new_templates_all(fixtures, line)
    # return shortest item
    shortest_len = 100000000
    shortest = []
    for _, v in new_tempalates.items():
        if len(v) < shortest_len:
            shortest_len = len(v)
            shortest = v 

    return shortest

    


if __name__ == "__main__":
    INITIAL_TEMPLATE = [
        "???????I???????",
        "???????D???????",
        "???????A???????",
        "???????L???????",
        "???????.???????",
        "???????G???????",
        "?????.RING.????",
        "IDAL.TORUS.TORO",
        "CORE.HOLE.APPLE",
        "???????S???????",
        "???????.???????",
        "???????P???????",
        "???????O???????",
        "???????L???????",
        "???????O???????",
    ]

    t0 = time.time()

    best_row = (-1, [], 1000000000)
    for i in range(ROWLEN):
        # line should be the third column of initial template
        line = INITIAL_TEMPLATE[i]

        if not ("@" in line or "?" in line):
            continue 

        if bool(re.fullmatch(r"[.?]*", line)):
            continue

        sub_strings = word_islands_indexes(line)
        fixtures = word_fixtures(sub_strings)
        if not fixtures:
            continue
        new_tempalates = get_new_templates(fixtures, line)
        if not new_tempalates:
            print("no possibilities", f"row {i}")
            exit()
        if len(new_tempalates) < best_row[2]:
            best_row = (i, new_tempalates, len(new_tempalates))

    best_col = (-1, [], 1000000000)
    for i in range(ROWLEN):
        # line should be the third column of initial template
        line = "".join(row[i] for row in INITIAL_TEMPLATE)

        if not ("@" in line or "?" in line):
            continue 

        sub_strings = word_islands_indexes(line)
        fixtures = word_fixtures(sub_strings)
        if not fixtures:
            continue
        new_tempalates = get_new_templates(fixtures, line)
        if not new_tempalates:
            print("no possibilities", f"col {i}")
            exit()
        if len(new_tempalates) < best_col[2]:
            best_col = (i, new_tempalates, len(new_tempalates))

        
    print("processing time:", time.time() - t0)
    print("best column:", best_row[0])
    print("num possibilities:", best_row[2])
    print("best column:", best_col[0])
    print("num possibilities:", best_col[2])
