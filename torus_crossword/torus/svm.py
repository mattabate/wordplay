import os
import pickle
import time
import tqdm
from config import EMB_PREF, EMB_MODL, PKL_MODL
from openai import OpenAI
from torus.keys import OPENAI_API_KEY
from torus.grid import get_words_in_filled_grid

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


client = OpenAI()

with open(PKL_MODL, "rb") as file:
    clf = pickle.load(file)


def infer(words: list[str]) -> list[str]:
    words_considered = [EMB_PREF + w for w in words]
    step = 1000
    good_vectors = []
    for i in tqdm.tqdm(range(0, len(words_considered), step)):
        good_vectors += client.embeddings.create(
            input=words_considered[i : i + step], model=EMB_MODL
        ).data
        time.sleep(1)

    out = [x.embedding for x in good_vectors]
    # predictions = clf.predict(out)
    # print("Predictions:", predictions)

    # Compute decision function scores
    scores = clf.decision_function(out)
    word_scores = list(zip(words, scores))

    # Sort words from most assumed bad to most assumed good
    word_scores_sorted = sorted(word_scores, key=lambda x: x[1])
    sorted_words = [word for word, _ in word_scores_sorted]

    return sorted_words


def infer_scores(words: list[str]) -> list[tuple[str, float]]:
    """Return a sorted list of tuples of words and their corresponding scores, fro most assumed good to most assumed bad."""

    words_considered = [EMB_PREF + w for w in words]
    step = 1000
    good_vectors = []
    for i in tqdm.tqdm(range(0, len(words_considered), step)):
        good_vectors += client.embeddings.create(
            input=words_considered[i : i + step], model=EMB_MODL
        ).data
        time.sleep(1)

    out = [x.embedding for x in good_vectors]
    # predictions = clf.predict(out)
    # print("Predictions:", predictions)

    # Compute decision function scores
    scores = clf.decision_function(out)

    return scores


def grid_av_score(grid: list[str]) -> float:
    """Return a score for the grid by taking the average of its word scores."""
    words = get_words_in_filled_grid(grid)
    scores = infer_scores(words)
    print("Scores:", sum(scores))
    return sum(scores) / len(scores)


def grids_av_score(grids: list[list[str]]) -> list[tuple[list[str], float]]:
    """Return a score for the grids by taking the average of their word scores."""
    all_words = set()
    for grid in grids:
        all_words.update(get_words_in_filled_grid(grid))
    all_words = list(all_words)
    scores = infer_scores(all_words)

    output = []
    for g in grids:
        words = get_words_in_filled_grid(g)
        grid_score = sum(scores[all_words.index(w)] for w in words)
        output.append((g, grid_score / len(words)))
    return output
