import enum
import fire
import json
import os
import tqdm
import matplotlib.gridspec as gridspec
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches


class ScoringMethod(enum.Enum):
    MAX_ENTROPY = "max_entropy"
    MIN_ENTROPY = "min_entropy"
    MAX_STD = "max_std"
    MIN_STD = "min_std"


def plot_card(ax, value, suit, x, y, width=1, height=1.4):
    """
    Plot a single card on the given axes.

    Parameters:
    - ax: Matplotlib axes to draw the card on.
    - value: The value of the card ('A', '2', ..., '10', 'J', 'Q', 'K').
    - suit: The suit of the card ('clubs', 'diamonds', 'hearts', 'spades').
    - x, y: Bottom left corner of the card.
    - width, height: Width and height of the card.
    """
    suits_symbols = {"clubs": "♣", "diamonds": "♦", "hearts": "♥", "spades": "♠"}
    color = "red" if suit in ["diamonds", "hearts"] else "black"

    # Draw card rectangle
    ax.add_patch(
        patches.Rectangle(
            (x, y),
            width,
            height,
            fill=True,
            edgecolor="black",
            facecolor="white",
            lw=1.5,
        )
    )

    # Add value and suit symbol
    symbol = suits_symbols[suit]
    ax.text(
        x + width / 2,
        y + height - 0.2,
        f"{value}\n{symbol}",
        fontsize=18,
        ha="center",
        va="top",
        color=color,
    )

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")


def plot_deck(ax, deck: list[int], cards_per_row=13):
    """
    Plots a deck of cards with adjustable figure size and aspect ratio.

    Parameters:
    - fig_width: Width of the figure.
    - fig_height: Height of the figure.
    - cards_per_row: Number of cards to display per row.
    """
    deck_tuples = []
    for c in deck:
        suit_index = (c - 1) // 13
        rank_index = (c - 1) % 13
        deck_tuples.append((suit_index, rank_index))

    # Calculate necessary parameters based on inputs
    values = ["A"] + [str(n) for n in range(2, 11)] + ["J", "Q", "K"]
    suits = [
        "spades",
        "hearts",
        "diamonds",
        "clubs",
    ]
    num_rows = len(suits)  # Number of suits determines the rows

    # Ensure the figure can display all cards without running off
    x_offset, y_offset = 1.2, 1.5  # Keep these fixed or adjust based on preferences
    total_width = x_offset * cards_per_row
    total_height = y_offset * num_rows

    # fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    for i, a in enumerate(deck_tuples):

        suit_index, rank_index = a
        suit = suits[suit_index]
        value = values[rank_index]

        row = i // cards_per_row
        col = i % cards_per_row
        x = col * x_offset
        y = total_height - (row * y_offset) - y_offset

        plot_card(ax, value, suit, x, y, width=1, height=1.4)

    ax.set_xlim(-0.5, total_width)
    ax.set_ylim(-0.5, total_height)
    ax.axis("off")


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


def get_decks_of_interest(starting_deck: list[int], shuffle_num=4):
    """Given a starting deck, return a list of decks with two cards switched."""
    decks = []
    for card in range(1, 53):
        loc = starting_deck.index(card)
        for j in range(1, 53):
            if letter_locations(card_name(card), "e") == letter_locations(
                card_name(j), "e"
            ):
                continue
            loc_new = starting_deck.index(j)
            if loc_new <= loc:
                continue
            deck_w_switch = starting_deck.copy()
            deck_w_switch[loc] = j
            deck_w_switch[loc_new] = card

            decks.append(deck_w_switch)

    for _ in range(1000):
        decks.append(shuffle(starting_deck, shuffle_num))

    for c in range(1, 53):
        loc = starting_deck.index(c)
        for j in range(53):
            if j == loc:
                continue
            new_deck: list[int] = starting_deck[:loc] + starting_deck[loc + 1 :]
            new_deck.insert(j, c)
            decks.append(new_deck)

    return decks


def calculate_entropy(locations, total_length):
    locations.insert(0, -1)
    locations.append(total_length)
    distances = [locations[i] - locations[i - 1] for i in range(1, len(locations))]
    return -float(np.std(distances))


def score_sentence(
    sentence, method: ScoringMethod = ScoringMethod.MAX_ENTROPY
) -> float:
    total_length = len(sentence)
    loc_es = letter_locations(sentence, "e")

    if method == ScoringMethod.MAX_ENTROPY:  # high predictability
        entropy = calculate_entropy(loc_es, total_length)
        return entropy
    elif method == ScoringMethod.MIN_ENTROPY:  # low predictability
        entropy = calculate_entropy(loc_es, total_length)
        return -entropy
    elif method == ScoringMethod.MAX_STD:
        return float(np.std(loc_es))
    elif method == ScoringMethod.MIN_STD:
        return -float(np.std(loc_es))


def score_deck(deck, method: ScoringMethod = ScoringMethod.MAX_ENTROPY) -> float:
    sentence = deck_2_sentence(deck)
    return score_sentence(sentence, method)


def find_better_deck(
    starting_deck: list[int],
    scoring_method: ScoringMethod = ScoringMethod.MAX_ENTROPY,
    shuffle_num=4,
) -> tuple[list[int], float]:
    """Return the best deck and its score from a starting deck."""
    decks = get_decks_of_interest(starting_deck, shuffle_num=shuffle_num)

    best_deck = starting_deck
    best_score: float = score_deck(starting_deck, scoring_method)
    for d in decks:
        d_score = score_deck(d, scoring_method)
        if d_score > best_score:
            best_deck = d
            best_score = d_score

    return best_deck, best_score


def brute_stats(starting_deck: list[int]):
    """compute and print stats on the deck strings."""

    sentence = deck_2_sentence(starting_deck)
    print("Deck string, unshuffles:", sentence, "\n")
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


def save_deck(save_file, deck, scoring_method, score):
    with open(save_file, "w") as f:
        json.dump(
            {
                "sentence": deck_2_sentence(deck),
                "deck": deck,
                "scoring_method": scoring_method.value,
                "score": score,
            },
            f,
            indent=1,
        )


def shuffle(deck, num_cards=4):
    """Shuffle the deck by selecting a random subset of cards and shuffling them."""
    new_deck = deck.copy()
    indexes = np.random.choice(52, num_cards, replace=False)
    indexes = np.random.choice(52, num_cards, replace=False)
    selected_cards = [new_deck[i] for i in indexes]
    np.random.shuffle(selected_cards)
    for i, j in enumerate(indexes):
        new_deck[j] = selected_cards[i]

    return new_deck


def run_search(
    initial_deck: list[int],
    k_scoring_method: ScoringMethod,
    k_num_runs: int,
    save_file: str,
    shuffle_num: int = 4,
) -> str:
    """Run the search for the best deck."""

    # find best shuffle
    high_score: float = -np.inf
    for _ in tqdm.tqdm(range(k_num_runs)):
        starting_deck = initial_deck.copy()

        run_best_score: float = -np.inf
        i = 0
        while True:
            i += 1
            better_deck, score = find_better_deck(
                starting_deck, scoring_method=k_scoring_method, shuffle_num=shuffle_num
            )
            if score > run_best_score:
                starting_deck = better_deck
                run_best_score = score
            else:
                break

        run_best_sentence = deck_2_sentence(starting_deck)

        if run_best_score > high_score:
            high_score = run_best_score
            best_sentence = run_best_sentence
            initial_deck = starting_deck.copy()

            # is best??
            if not os.path.exists(save_file):
                save_deck(save_file, starting_deck, k_scoring_method, high_score)
            else:
                with open(save_file, "r") as f:
                    dataset = json.load(f)

                saved_sentence = dataset["sentence"]
                saved_score = score_sentence(saved_sentence, k_scoring_method)
                if high_score > saved_score:
                    save_deck(save_file, starting_deck, k_scoring_method, high_score)
                    print("\033[93mSaved new best deck")
                    print(f"new score: {high_score}, old score: {saved_score}")
                    print("\033[0m")

    return best_sentence


def plot_histogram(ax, loc_es):
    # Adjust the first subplot (the left one)
    ax.hist(loc_es, bins=10)
    ax.hist(loc_es, bins=52)
    ax.set_title('"E" Locations Histogram', fontsize=24)
    ax.tick_params(axis="both", which="major", labelsize=14, width=3)


def main(
    num_runs: int = 20,
    metric="max_entropy",
    search: bool = True,
    verbose: bool = True,
    plot: bool = True,
    shuffle_num: int = 4,
):
    if metric == "max_entropy":
        scoring_method = ScoringMethod.MAX_ENTROPY
    elif metric == "min_entropy":
        scoring_method = ScoringMethod.MIN_ENTROPY
    elif metric == "max_std":
        scoring_method = ScoringMethod.MAX_STD
    elif metric == "min_std":
        scoring_method = ScoringMethod.MIN_STD
    else:
        raise ValueError("Invalid metric. Please choose a valid scoring method.")

    save_file = scoring_method.value + "_best_deck.json"

    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            dataset = json.load(f)

        starting_deck = dataset["deck"]
    else:
        starting_deck = list(range(1, 53))

    if verbose:
        brute_stats(starting_deck)

    if search:
        run_search(starting_deck, scoring_method, num_runs, save_file, shuffle_num)

    if plot:
        with open(save_file, "r") as f:
            dataset = json.load(f)

        loc_es = letter_locations(dataset["sentence"], "e")
        # Create a figure and a 1x2 grid of subplots
        fig = plt.figure(figsize=(13, 5))
        gs = gridspec.GridSpec(
            1, 2, width_ratios=[3, 1]
        )  # Adjust the width ratios as needed

        # Create subplots
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])

        plot_deck(ax1, dataset["deck"], cards_per_row=13)
        plot_histogram(ax2, loc_es)

        plt.show()


if __name__ == "__main__":
    fire.Fire(main)
