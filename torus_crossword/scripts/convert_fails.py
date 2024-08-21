import json
import os
import tqdm
from lib import T_BLUE, T_NORMAL, T_YELLOW, load_json


for TYPE in ["AA", "AD", "DA", "DD"]:
    print(f"{T_BLUE}Converting: {TYPE}{T_NORMAL}")

    # find all files in failures/ with names like 15x15_grid_failures_DA_42.json or 15x15_grid_failures_DA_40.json and give me the numbers
    files = os.listdir("failures/")
    paths = ["failures/" + file for file in files]

    for path in paths:
        data = load_json(path)

        new_data = ["".join(d) for d in tqdm.tqdm(data, desc=path, leave=False)]

        with open(path, "w") as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)

    # numbers = []
    # for file in files:
    #     if file.startswith(f"15x15_grid_failures_{TYPE}_") and not file.endswith(
    #         "_flipped.json"
    #     ):
    #         numbers.append(int(file.split("_")[-1].split(".")[0]))

    # # find the highest number
    # highest_number = max(numbers)
    # remove_number = highest_number - 2

    # # sorted highest first
    # numbers.sort(reverse=True)
    # highest_number = numbers[0]
    # lower_numbers = numbers[1:]

    # len_numbers = len(numbers)
    # for i in range(len_numbers - 1):
    #     highest_number = numbers[i]
    #     file1 = f"failures/15x15_grid_failures_{TYPE}_{highest_number}.json"
    #     with open(file1) as f:
    #         higher_data: list[list[str]] = json.load(f)
