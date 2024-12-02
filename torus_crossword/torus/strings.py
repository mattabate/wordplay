def get_prefix(word, len_pref=6):
    """Given a string, return the first len_pref characters."""
    return word[:len_pref]


def get_suffix(word, len_suff=6):
    """Given a string, return the last len_suff characters."""
    return word[(-len_suff):]


def replace_char_in_string(string, char, index):
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
