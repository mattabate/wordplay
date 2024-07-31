import json
import os
from schema import append_json, T_BLUE, T_GREEN, T_NORMAL, T_PINK, T_YELLOW

for TYPE in ["AA", "AD", "DA", "DD"]:
    print(f"{T_BLUE}Pruning Type: {TYPE}{T_NORMAL}")
    print(f"{T_YELLOW}Starting normal: {T_NORMAL}")

    # find all files in failures/ with names like 15x15_grid_failures_DA_42.json or 15x15_grid_failures_DA_40.json and give me the numbers
    files = os.listdir("failures/")
    numbers = []
    for file in files:
        if file.startswith(f"15x15_grid_failures_{TYPE}_") and not file.endswith(
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
        file1 = f"failures/15x15_grid_failures_{TYPE}_{highest_number}.json"
        with open(file1) as f:
            higher_data: list[list[str]] = json.load(f)

        for j in range(i + 1, len_numbers):
            lower_number = numbers[j]
            file2 = f"failures/15x15_grid_failures_{TYPE}_{lower_number}.json"
            with open(file2) as f:
                lower_data: list[list[str]] = json.load(f)

            for grid in higher_data:
                if grid not in lower_data:
                    lower_data.append(grid)
                    print(
                        "adding one possible grid from ",
                        T_GREEN + str(highest_number) + T_NORMAL,
                        "to",
                        T_GREEN + str(lower_number) + T_NORMAL,
                    )

        with open(file2, "w") as f:
            json.dump(lower_data, f, indent=4, ensure_ascii=False)

    print()
    print(f"{T_YELLOW}Starting flipped: {T_NORMAL}")

    files = os.listdir("failures/")
    numbers = []
    for file in files:
        if file.startswith(f"15x15_grid_failures_{TYPE}_") and file.endswith(
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
        file1 = f"failures/15x15_grid_failures_{TYPE}_{highest_number}_flipped.json"
        with open(file1) as f:
            higher_data: list[list[str]] = json.load(f)

        for j in range(i + 1, len_numbers):
            lower_number = numbers[j]
            file2 = f"failures/15x15_grid_failures_{TYPE}_{lower_number}_flipped.json"
            with open(file2) as f:
                lower_data: list[list[str]] = json.load(f)

            for grid in higher_data:
                if grid not in lower_data:
                    lower_data.append(grid)
                    print(
                        "adding one possible grid from ",
                        T_GREEN + str(highest_number) + T_NORMAL,
                        "to",
                        T_GREEN + str(lower_number) + T_NORMAL,
                    )

            with open(file2, "w") as f:
                json.dump(lower_data, f, indent=4, ensure_ascii=False)

    print()
