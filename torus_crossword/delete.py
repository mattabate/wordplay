import json
from tqdm import tqdm


def load_json(file_path):
    """Load data from a JSON file."""
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def save_json(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_unique_entries(entries):
    """Return a list of unique entries, where entries are lists of strings."""
    unique_entries_set = set()
    for entry in tqdm(entries, desc="Processing entries"):
        # Convert each list of strings to a tuple for hashing
        tuple_entry = tuple(entry)
        unique_entries_set.add(tuple_entry)
    # Convert tuples back to lists
    unique_entries = [list(t) for t in unique_entries_set]
    return unique_entries


def main():
    # Load entries from the original JSON file
    entries = load_json("star_sols.json")

    # Get unique entries
    unique_entries = get_unique_entries(entries)

    # Save the unique entries to a new JSON file
    save_json(unique_entries, "unique_star_sols.json")

    print("Unique entries have been saved to unique_star_sols.json.")


if __name__ == "__main__":
    main()
