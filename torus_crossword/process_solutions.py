import numpy as np
import tqdm
from lib import Direction, transpose
from fast_search import get_word_locations, ROWLEN

import matplotlib.pyplot as plt

import torus

from config import (
    get_solutions_json,
    SCORES_DICT_JSON,
    SEARCH_W_FLIPPED,
    IC_TYPE,
    MAX_WAL,
)
from main import T_PINK, T_NORMAL, T_YELLOW


SOLS_PATH = get_solutions_json(IC_TYPE, MAX_WAL, SEARCH_W_FLIPPED)
scored_words_dict = torus.json.load_json(SCORES_DICT_JSON)


def reduce_to_unique_solutions():
    solutions = torus.json.load_json(SOLS_PATH)

    unique_solutions = []
    for s in solutions:
        if s not in unique_solutions:
            unique_solutions.append(s)

    if len(unique_solutions) != len(solutions):
        print(
            T_PINK
            + SOLS_PATH
            + f"contains {len(solutions)} grids but some are suplicates"
            + T_PINK
        )
        print(
            T_PINK + f"Removing {len(solutions) - len(unique_solutions)} grids" + T_PINK
        )
        print()
        torus.json.write_json(SOLS_PATH, unique_solutions)

    return unique_solutions


def score_words(grid: list[str]):
    words = get_word_locations(
        grid=grid, direction=Direction.ACROSS
    ) + get_word_locations(grid=grid, direction=Direction.DOWN)
    # if contains duplicates, remove them
    if len(words) != len(set(words)):
        sols = torus.json.load_json(SOLS_PATH)
        sols.remove(grid)
        torus.json.write_json(SOLS_PATH, sols)
        return

    word_strings = []
    scores = []
    for w in words:
        string_word = ""
        for i in range(w.length):
            if w.direction == Direction.ACROSS:
                string_word += grid[w.start[0]][(w.start[1] + i) % ROWLEN]
            else:
                string_word += grid[(w.start[0] + i) % ROWLEN][w.start[1]]

        word_strings.append(string_word)
        for wr, sc in scored_words_dict.items():
            if wr == string_word:
                scores.append(sc)
                break

    return word_strings, scores


print(T_YELLOW + "REMOVE DUPLICATES" + T_NORMAL)
solutions = reduce_to_unique_solutions()


print(T_YELLOW + "SCORING GRIDS" + T_NORMAL)

highest_average_words_score = 0
fewest_words = 10000
lowest_variance = 10000
mean_lowest_variance = 10000
best_s = []
best_w = []

av_scores = []
for s in tqdm.tqdm(solutions):
    word_strings, scores = score_words(s)

    num_words = len(word_strings)
    average_score = sum(scores) / num_words
    av_scores.append(average_score)

    if average_score > highest_average_words_score:
        highest_average_words_score = average_score
        best_s = [s]
    elif average_score == highest_average_words_score:
        best_s.append(s)
    if num_words < fewest_words:
        fewest_words = num_words
        best_w = [s]
    elif num_words == fewest_words:
        best_w.append(s)

    variance = round(np.var(scores) ** (1 / 2), 2)
    if variance < lowest_variance:
        lowest_variance = variance
        best_v = [s]
        mean_lowest_variance = average_score
    elif variance == lowest_variance:
        best_v.append(s)


print(T_YELLOW + "TOTAL SOLUTIONS:" + T_NORMAL, len(solutions))
print(T_YELLOW + "BEST WORD SCORE:" + T_NORMAL, highest_average_words_score)
num_best = len(best_s)
print("NUMBER OF BEST WORD SCORES:", num_best)
print()
for i, s in enumerate(best_s):

    if SEARCH_W_FLIPPED:
        print("\n".join([" ".join(l) for l in s]))
    else:
        print("\n".join([" ".join(l) for l in transpose(s)]))
    word_strings, scores = score_words(s)
    print()

std = np.std(av_scores)
print(
    T_YELLOW + "MIN STDEV:" + T_NORMAL,
    lowest_variance,
    T_YELLOW + "MEAN:" + T_NORMAL,
    mean_lowest_variance,
)
print(T_YELLOW + "FEWEST WORDS:" + T_NORMAL, fewest_words)
print(T_YELLOW + "NUMBER OF FEWEST WORDS:" + T_NORMAL, len(best_w))
print()


# indexes min 5 scores in scores
snoot = zip(word_strings, scores)
snoot = sorted(snoot, key=lambda x: x[1])

print(
    T_YELLOW + "Worst Words in Best Grids:" + T_NORMAL,
    snoot[:40],
)

# min minus 1 to max plus 1 rounded to 0.1
bins = np.arange(round(min(av_scores) - 1, 1), round(max(av_scores) + 1, 1), 0.1)
# Create the histogram
plt.hist(av_scores, bins=bins, edgecolor="black")

# Add titles and labels
plt.title("Scoring Filled Grids Based on Commonness of Word")
plt.xlabel("Average Word Score")
plt.ylabel("Number of Grids With that Score")
plt.show()


# min minus 1 to max plus 1 rounded to 0.1
bins = np.arange(round(min(scores) - 1, 1), round(max(scores) + 1, 1), 1)
# Create the histogram
plt.hist(scores, bins=bins, edgecolor="black")
# Add titles and labels
plt.title("Sample Best Grid Word Commonness Distribution")
plt.xlabel("Word Score")
plt.ylabel("Number of Words With that Score")
plt.show()
