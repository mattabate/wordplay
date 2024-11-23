def get_prefix(word, len_pref=6):
    """Given a string, return the first len_pref characters."""
    return word[:len_pref]


def get_suffix(word, len_suff=6):
    """Given a string, return the last len_suff characters."""
    return word[(-len_suff):]
