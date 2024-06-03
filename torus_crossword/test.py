import json


def replace_char_at(string, char, index):
    # Check if index is within the bounds of the string
    if index < 0:
        index += len(string)
    if index >= len(string) or index < 0:
        return string  # Return the original string if index is out of bounds
    return string[:index] + char + string[index + 1 :]


with open("words_filtered.json") as f:
    data = json.load(f)


line = "NG.??CAT.????CI"
if len(line) != 15:
    print("len line", len(line))
    exit()

print("initial template:", line)
print()

rotations = []
# i want all rotations of sting
for i in range(len(line)):
    new_string = line[i:] + line[:i]
    if new_string[0] == "?" or new_string[-1] not in ["?"]:
        continue

    word = new_string.split("?")[0]

    rotations.append((i, word, new_string))


# how many word islands
# thing one, start at the begining, and

TEMPLATE_SET = []

for i, word, rotated_string in rotations:
    NEW_TEMPLATES = []

    if word[0] != "." and word[-1] == ".":
        suffix = word.split(".")[0] + "."
        print("suffix", suffix)
        for candidate_word in data:
            candidate_word = "." + candidate_word + "."
            if not candidate_word.endswith(suffix):
                continue

            new_line = rotated_string
            for yy in range(1, len(candidate_word) - len(suffix) + 1):
                candidate_letter = candidate_word[-len(suffix) - yy]
                template_letter = rotated_string[-yy]

                new_line = replace_char_at(new_line, candidate_letter, -yy)

                if template_letter == "?":
                    continue
                if template_letter == candidate_letter:
                    continue
                if template_letter == "@" and candidate_letter != ".":
                    continue
                break
            else:
                newline = rotated_string

                NEW_TEMPLATES.append(new_line[-i:] + new_line[:-i])

        TEMPLATE_SET.append(NEW_TEMPLATES)

    if word[0] == "." and word[-1] != ".":
        print(word)

print(json.dumps(TEMPLATE_SET, indent=2))
