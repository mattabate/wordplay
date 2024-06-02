# Sater

The `sater` repository uses a novel search script for for creating crossword puzzles. `main.py`

## Features

- **Dynamic Word Insertion:** Dynamically inserts words into a crossword template based on specified constraints.
- **Template Transposition:** Capable of transposing rows and columns to fit words in various orientations.
- **Word List Flexibility:** Supports different word lists and can combine them for a richer vocabulary.
- **Verbose Processing:** Provides detailed output of the process, making it easier to track and understand the steps involved.

## Requirements

This project requires Python 3.8 or later. You must have the following Python packages installed:

- `json`: For loading and saving word lists.
- `tqdm`: For displaying progress during the generation process.
- `enum`: For managing different word list options.

To install the necessary packages, run:

```bash
pip install tqdm
```

## Usage

Before you can start generating crosswords, ensure that the word lists are properly set up under the `eowl/` and `crosswords/` directories, with JSON files named `eowl_words.json` and `crossword_words.json`, respectively.

To run the script, simply execute:

```bash
python main.py
```

You can adjust the script settings by modifying the `f_wordlist`, `f_test`, `f_verbose`, `k_place`, and `k_word_length` variables within the script to tailor the crossword generation to your preferences.

## Script Breakdown

- **Initialization:** Sets up the word dictionary based on the selected word list.
- **Template Generation:** Starts with a basic template and tries to insert words at strategic positions.
- **Word Validation:** Ensures all words fit the crossword rules and checks for any word duplications.
- **Win Condition:** Once a valid template is completely filled, it is saved.

## Output

The generated crosswords are saved in a JSON format in a file named `wins.json`, which can be found in the root directory of the project.
