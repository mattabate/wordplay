import os

from torus.json import load_json, write_json
from lib import T_BLUE, T_GREEN, T_NORMAL, T_YELLOW
from config import get_failures_json

for TYPE in ["AA", "AD", "DA", "DD"]:
    print(f"{T_BLUE}Pruning Type: {TYPE}{T_NORMAL}")
    print(f"{T_YELLOW}Starting normal: {T_NORMAL}")

    # find all files in failures/ with names like 15x15_grid_failures_DA_42.json or 15x15_grid_failures_DA_40.json and give me the numbers
    files = os.listdir("failures/")
    numbers = []
    for file in files:
        if file.startswith(f"15x15_stars_failures_{TYPE}_") and not file.endswith(
            "_flipped.json"
        ):
            numbers.append(int(file.split("_")[-1].split(".")[0]))

    # find the highest number
    highest_number = max(numbers)
    remove_number = highest_number - 2

    # sorted highest first
    numbers.sort(reverse=True)
    highest_number = numbers[0]
    lower_numbers = numbers[1:]

    len_numbers = len(numbers)
    for i in range(len_numbers - 1):
        highest_number = numbers[i]
        file1 = get_failures_json(type=TYPE, max_walls=highest_number, flipped=False)
        higher_data: list[list[str]] = load_json(file1)

        for j in range(i + 1, len_numbers):
            lower_number = numbers[j]
            file2 = get_failures_json(type=TYPE, max_walls=lower_number, flipped=False)
            lower_data: list[list[str]] = load_json(file2)

            for grid in higher_data:
                if grid not in lower_data:
                    lower_data.append(grid)
                    print(
                        "adding one possible grid from ",
                        T_GREEN + str(highest_number) + T_NORMAL,
                        "to",
                        T_GREEN + str(lower_number) + T_NORMAL,
                    )

            write_json(file2, lower_data)

    print()
    print(f"{T_YELLOW}Starting flipped: {T_NORMAL}")

    files = os.listdir("failures/")
    numbers = []
    for file in files:
        if file.startswith(f"15x15_stars_failures_{TYPE}_") and file.endswith(
            "_flipped.json"
        ):
            file.replace("_flipped.json", ".json")
            numbers.append(int(file.split("_")[-2].split(".")[0]))

    # find the highest number
    highest_number = max(numbers)
    remove_number = highest_number - 2

    # sorted highest first
    numbers.sort(reverse=True)
    highest_number = numbers[0]
    lower_numbers = numbers[1:]

    len_numbers = len(numbers)
    for i in range(len_numbers - 1):
        highest_number = numbers[i]
        file1 = get_failures_json(type=TYPE, max_walls=highest_number, flipped=True)
        higher_data = load_json(file1)

        for j in range(i + 1, len_numbers):
            lower_number = numbers[j]
            file2 = get_failures_json(type=TYPE, max_walls=lower_number, flipped=True)
            lower_data: list[list[str]] = load_json(file2)

            for grid in higher_data:
                if grid not in lower_data:
                    lower_data.append(grid)
                    print(
                        "adding one possible grid from ",
                        T_GREEN + str(highest_number) + T_NORMAL,
                        "to",
                        T_GREEN + str(lower_number) + T_NORMAL,
                    )

            write_json(file2, lower_data)

    print()
