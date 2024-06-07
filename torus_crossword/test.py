import json
import time
import re

ROWLEN = 15

with open("words.json") as f:
    WORDLIST = json.load(f)

for i, w in enumerate(WORDLIST):
    WORDLIST[i] = "█" + w + "█"


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
    Example: "a█bb___ab_c@█@█" -> [(7, 'ab'), (10, 'c@█@█a█bb')]
    """
    if "_" not in line:
        # TODO: make sure we exit here - if row full, cant do any of the stuff below
        return []

    qm_positions = [index for index, char in enumerate(line) if char == "_"]
    qm_positions.append(ROWLEN)

    # looks like: [[5, 6], [8, 9, 10], [13, 14, 15, 16, 17]]
    word_islands: list[int] = []
    for i in range(len(qm_positions) - 1):
        in_between = list(range(qm_positions[i] + 1, qm_positions[i + 1]))
        if in_between:
            word_islands.append(in_between)

    wrap = line.find("_")
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
        periods = s.split("█")

        if len(periods) == 1:
            word_fixtures.append(("substring", i, s))
            continue

        if periods[0]:
            # this actually works
            word_fixtures.append(("suffix", i, periods[0] + "█"))

        if periods[-1]:
            word_fixtures.append(
                ("prefix", i + len(s) - len(periods[-1]) - 1, "█" + periods[-1])
            )

        spots = [j for j, c in enumerate(s) if c == "█"]

        for j in range(1, len(periods) - 1):
            if "@" in periods[j]:
                word_fixtures.append(
                    ("infix", i + spots[j - 1], "█" + periods[j] + "█")
                )

    return word_fixtures


def get_new_templates_all(fixtures: list[tuple[str, int, str]], line: str):
    new_templates = {i:[] for t, i, c in fixtures}
    for w in WORDLIST:
        for _, i, cont in fixtures:
            pattern = cont.replace("@", "[^█]")
            matches = re.finditer(pattern, w)
            positions = [match.start() for match in matches]
            for p in positions:
                new_template = line
                for j, c in enumerate(w):
                    ooo = (i - p + j) % ROWLEN
                    if line[ooo] in [c, "_"] or (line[ooo] == "@" and c != "█"):
                        new_template = new_template[:ooo] + c + new_template[ooo + 1 :]
                        continue
                    break
                else:
                    # clean to convert ._. and .__. to ... and ....
                    if bool(re.search(r"\.[A-Za-z]\.", new_template+new_template)):
                        continue
                    if bool(re.search(r"\.[A-Za-z]{2}\.", new_template+new_template)):
                        continue
                    new_template = new_template.replace('█_█', '███').replace('█__█', '████')
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

    
def get_new_grids(grid: list[str])->list[list[str]]:
    best_row = (-1, [], 1000000000)
    for i in range(ROWLEN):
        # line should be the third column of initial template
        line = grid[i]

        if not ("@" in line or "_" in line):
            continue 

        if bool(re.fullmatch(r"[█_]*", line)):
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

    if best_row[2] == 0:
        return []

    best_col = (-1, [], 1000000000)
    for i in range(ROWLEN):
        # line should be the third column of initial template
        line = "".join(row[i] for row in grid)

        if not ("@" in line or "_" in line):
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

    if best_col[2] == 0:
        return []
    
    new_grids = []
    if best_row[2] < best_col[2]:
        for l in best_row[1]:
            temp = grid.copy()
            temp[best_row[0]] = l
            new_grids.append(temp)
        return best_row[2], new_grids
    else:
        for l in best_col[1]:
            temp = grid.copy()
            for i, c in enumerate(l):
                temp[i] = replace_char_at(temp[i], c, best_col[0])

                # if eg (1, 2) = "." -> replace with (13, 11) = "."
                if c == "█":
                    temp[ROWLEN - 1 -i] = replace_char_at(temp[ROWLEN - 1 -i], "█", ROWLEN - 1 - best_col[0])

                if c in "@ABCDEFGHIJKLMNOPQRSTUVWXYZ" and temp[ROWLEN - 1 - i][ROWLEN - 1 - best_col[0]] == "_" :
                    temp[ROWLEN - 1 - i] = replace_char_at(temp[ROWLEN - 1 -i], "@", ROWLEN - 1 - best_col[0])

            new_grids.append(temp)


        return best_col[2], new_grids


if __name__ == "__main__":
    INITIAL_TEMPLATE = [
        "_______I_______",
        "_______D_______",
        "_______A_______",
        "_______L_______",
        "_______█_______",
        "_______G_______",
        "_____█RING█____",
        "IDAL█TORUS█TORO",
        "CORE█HOLE█APPLE",
        "_______S_______",
        "_______█_______",
        "_______P_______",
        "_______O_______",
        "_______L_______",
        "_______O_______",
    ]

    t0 = time.time()

    grids = INITIAL_TEMPLATE.copy()
    pos, new_grids = get_new_grids(grids)

    with open("output.json", "w", encoding='utf-8') as f:
        json.dump(new_grids, f, indent=2, ensure_ascii=False)

    print("num possibilities:", pos)
    print("processing time:", time.time() - t0)
   
