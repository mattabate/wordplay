import json
import numpy as np
import os
import pickle
import time
import tqdm
from config import ACTIVE_WORDS_JSON, PKL_MODL, EMB_PREF, EMB_MODL, Source

from keys import OPENAI_API_KEY
from openai import OpenAI
from sklearn import svm, metrics

import migrations.database
from migrations.schema import ReviewStatus

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

client = OpenAI()

source = Source.active_grids

if source == Source.ics:
    input_file = "filter_words/sorted_words_in_ics.json"
elif source == Source.active_grids:
    input_file = ACTIVE_WORDS_JSON
else:
    print("Invalid source")
    exit()


good_words = migrations.database.get_words_by_status(ReviewStatus.APPROVED)
bad_words = migrations.database.get_words_by_status(ReviewStatus.REJECTED)

good_words = [EMB_PREF + g for g in good_words]
bad_words = [EMB_PREF + b for b in bad_words]

# Get embeddings
step = 1000
good_vectors = []
for i in tqdm.tqdm(range(0, len(good_words), step)):
    good_vectors += client.embeddings.create(
        input=good_words[i : i + step], model=EMB_MODL
    ).data
    time.sleep(1)
bad_vectors = []
for i in tqdm.tqdm(range(0, len(bad_words), step)):
    bad_vectors += client.embeddings.create(
        input=bad_words[i : i + step], model=EMB_MODL
    ).data
    time.sleep(1)

# Combine embeddings into a single dataset
X = np.array([item.embedding for item in good_vectors + bad_vectors])

# Create labels: 1 for good, 0 for bad
y = np.array([1] * len(good_vectors) + [0] * len(bad_vectors))

# Train the SVM
clf = svm.SVC(kernel="rbf", C=1.0)
clf.fit(X, y)

y_pred = clf.predict(X)

# Calculate accuracy
accuracy = metrics.accuracy_score(y, y_pred)
print("Accuracy:", accuracy)

with open(PKL_MODL, "wb") as file:
    pickle.dump(clf, file)
