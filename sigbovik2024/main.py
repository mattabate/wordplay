import numpy as np
import tqdm
import matplotlib.pyplot as plt
import enum


class ScoringMethod(enum.Enum):
    MAX_ENTROPY = 0
    MIN_ENTROPY = 1
    MAX_STD = 2
    MIN_STD = 3


def card_name(card_number) -> str:
    """Return the name of a card given its number."""
    # Ensure the card number is in the correct range
    if card_number < 1 or card_number > 52:
        raise ValueError(
            "Invalid card number. Please choose a number between 1 and 52."
        )

    suits = ["SPADES", "HEARTS", "DIAMONDS", "CLUBS"]
    ranks = [
        "ACE",
        "TWO",
        "THREE",
        "FOUR",
        "FIVE",
        "SIX",
        "SEVEN",
        "EIGHT",
        "NINE",
        "TEN",
        "JACK",
        "QUEEN",
        "KING",
    ]

    # Calculate the suit and rank of the card
    suit_index = (card_number - 1) // 13
    rank_index = (card_number - 1) % 13

    # Construct the name of the card
    return f"{ranks[rank_index]} OF {suits[suit_index]}"


def deck_2_sentence(list_of_cards: list[int]) -> str:
    """Return a sentence of card names from a list of card numbers."""
    if not isinstance(list_of_cards, list):
        raise ValueError("Invalid input. Please provide a list of integers.")
    if len(list_of_cards) != 52:
        raise ValueError(
            f"Invalid input. Please provide a list of 52 card numbers. count: {len(list_of_cards)}"
        )

    sentence = ""
    for card_number in list_of_cards:
        sentence += card_name(card_number) + ", "
    return sentence[:-2]


def letter_locations(sentence: str, letter: str):
    """Return the locations of a given letter in a sentence."""
    return [i for i, s in enumerate(sentence) if s == letter.upper()]


def get_decks_of_interest(starting_deck: list[int]):
    """Given a starting deck, return a list of decks with two cards switched."""
    decks = []
    for card in range(1, 52):
        loc = starting_deck.index(card)
        for j in range(card + 1, 53):
            loc_new = starting_deck.index(j)
            deck_w_switch = starting_deck.copy()
            deck_w_switch[loc] = j
            deck_w_switch[loc_new] = card

            decks.append(deck_w_switch)
    return decks


def calculate_entropy(locations, total_length):
    if not locations:
        return 0
    # Calculate probabilities
    probabilities = [loc / total_length for loc in locations]
    # Calculate entropy
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
    return entropy


def score_deck(deck, method: ScoringMethod = ScoringMethod.MAX_ENTROPY):

    sentence = deck_2_sentence(deck)
    total_length = len(sentence)
    loc_es = letter_locations(sentence, "e")

    if method == ScoringMethod.MAX_ENTROPY:  # high predictability
        entropy = calculate_entropy(loc_es, total_length)
        return entropy
    elif method == ScoringMethod.MIN_ENTROPY:  # low predictability
        entropy = calculate_entropy(loc_es, total_length)
        return -entropy
    elif method == ScoringMethod.MAX_STD:
        return np.std(loc_es)
    elif method == ScoringMethod.MIN_STD:
        return -np.std(loc_es)


def find_better_deck(
    starting_deck: list[int], scoring_method: ScoringMethod = ScoringMethod.MAX_ENTROPY
):
    """Return the best deck and its score from a starting deck."""
    decks = get_decks_of_interest(starting_deck)
    best_deck = starting_deck
    score = -np.inf
    for d in decks:
        std = score_deck(d, scoring_method)
        if std > score:
            best_deck = d
            score = std

    return best_deck, score


def brute_stats(starting_deck: list[int]):
    """compute and print stats on the deck strings."""

    sentence = deck_2_sentence(starting_deck)
    print("Deck string, unshuffles:", sentence)
    print()
    print("Legnth of deck string:", len(sentence))

    letters = {}
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        locs = letter_locations(sentence, letter)
        letters[letter] = len(locs)

    print(
        "Most common letters in Deck String:",
        sorted(letters.items(), key=lambda x: x[1], reverse=True)[:5],
    )

    letters = {}
    for card in range(1, 53):
        name = card_name(card)
        for letter in set(s for s in name if s not in [" ", ","]):
            if letter in letters.keys():
                letters[letter] += 1
            else:
                letters[letter] = 1
    print(
        "Most common letters in Card Names:",
        sorted(letters.items(), key=lambda x: x[1], reverse=True)[:5],
    )


def run_search(
    starting_deck: list[int], k_scoring_method: ScoringMethod, k_num_runs: int
) -> str:
    """Run the search for the best deck."""
    # find best shuffle
    high_score = -np.inf
    for _ in tqdm.tqdm(range(k_num_runs)):
        np.random.shuffle(starting_deck)
        run_best_score = -np.inf
        while True:
            best_deck, score = find_better_deck(
                starting_deck, scoring_method=k_scoring_method
            )
            if score > run_best_score:
                starting_deck = best_deck
                run_best_score = score
            else:
                break

        run_best_sentence = deck_2_sentence(starting_deck)
        print("Highest score:", run_best_score)
        print(run_best_sentence)

        if run_best_score > high_score:
            high_score = run_best_score
            best_sentence = run_best_sentence

    return best_sentence


if __name__ == "__main__":

    k_num_runs = 5
    k_scoring_method = ScoringMethod.MIN_ENTROPY
    k_verbose = True
    starting_deck = list(range(1, 53))

    if k_verbose:
        brute_stats(starting_deck)

    best_sentence = run_search(starting_deck, k_scoring_method, k_num_runs)

    with open("best_deck.txt", "w") as f:
        f.write(best_sentence)

    loc_es = letter_locations(best_sentence, "e")

    plt.hist(loc_es, bins=10)
    plt.hist(loc_es, bins=52)
    plt.show()
