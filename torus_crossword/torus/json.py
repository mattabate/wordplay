import json
import fcntl
import tqdm


def load_json(json_name):
    with open(json_name, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            out = json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return out


def write_json(json_name, data):
    with open(json_name, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=4, ensure_ascii=False)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def append_json(json_name, grid):
    with open(json_name, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            data = json.load(f)
            data.append(grid)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def remove_duplicates(json_name):
    "preserves ordering"
    initial = load_json(json_name)
    unique = []
    for s in tqdm.tqdm(initial):
        if s not in unique:
            unique.append(s)
    write_json(json_name, unique)


def remove_from_json_list(json_file: str, entry):
    current_list = load_json(json_file)
    reduced_json = [e for e in current_list if e != entry]
    write_json(json_file, reduced_json)
