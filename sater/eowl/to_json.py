import os
import json

if __name__ == "__main__":
    # get txt file paths in by_letter folder

    path = "by_letter/"
    files = os.listdir(path)

    all_txt_files = []
    for file in files:
        if file.endswith(".txt"):
            all_txt_files.append(file)

    all_words = []
    for file in all_txt_files:
        with open(path + file, "r") as f:
            words = f.readlines()
            words = [word.strip() for word in words]
            all_words.extend(words)

    with open("eowl_words.json", "w") as f:
        json.dump(all_words, f, indent=4)
