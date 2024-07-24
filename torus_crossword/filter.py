import json

with open("star_fails.json") as f:
    star_fails = json.load(f)


def replace_char_at(string, char, index):
    """Replace a character at a specific index in a string.

    Args:
        string (str): The original string
        char (str): The character to replace with
        index (int): The index at which to replace the character

    Returns:
        str: The modified string
    """
    l = len(string)
    if index < 0:
        index += l
    if index >= l or index < 0:
        return string  # Return the original string if index is out of bounds

    return string[:index] + char + string[index + 1 :]


for star in star_fails:
    if star[5][14] == "█" and star[5][13] == "█" and star[5][12] == "_":
        star[5] = replace_char_at(star[5], "█", 12)

with open("star_fails.json", "w") as f:
    json.dump(star_fails, f, indent=4, ensure_ascii=False)
