"""
What do i want this to do in the future?
- for every star in every failure file, if that star is not in the solutions file, delete
- if fails high number (42), delete all lower numbers (40, 38, ...)


---
really it should be
- (possibly run with nw word to take out)
- generate words omitted
- remove all stars that contain words omitted
- remove all those stars from the failures files
- propegate the stars to the lower files
"""

import os
import tqdm

import torus

from lib import T_BLUE, T_GREEN, T_NORMAL, T_YELLOW
from config import get_failures_json, STARS_FOUND_JSON, STARS_FOUND_FLIPPED_JSON


def remove_unfound_fails():
    """
    if a star is in the failures file (it has been disqualified),
    but not in the solutions file (it is not considered),
    delete it"""
    star_sols = torus.json.load_json(STARS_FOUND_JSON)
    star_sols_flipped = torus.json.load_json(STARS_FOUND_FLIPPED_JSON)

    # get all files in failures/
    files = os.listdir("failures/")
    for file in files:
        file = "failures/" + file
        if file.endswith("_flipped.json"):
            doots = star_sols_flipped.copy()
        else:
            doots = star_sols.copy()

        stars_failed = torus.json.load_json(file)
        new_stars_failed = []
        for star in tqdm.tqdm(stars_failed):
            if star in doots:
                new_stars_failed.append(star)

        print(file)
        print("oringal", len(stars_failed))
        print("new", len(new_stars_failed))
        print()
        torus.json.write_json(file, new_stars_failed)


def propegate_fails_to_lower_files():
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
            file1 = get_failures_json(
                type=TYPE, max_walls=highest_number, flipped=False
            )
            higher_data: list[list[str]] = torus.json.load_json(file1)

            for j in range(i + 1, len_numbers):
                lower_number = numbers[j]
                file2 = get_failures_json(
                    type=TYPE, max_walls=lower_number, flipped=False
                )
                lower_data: list[list[str]] = torus.json.load_json(file2)

                for grid in higher_data:
                    if grid not in lower_data:
                        lower_data.append(grid)
                        print(
                            "adding one possible grid from ",
                            T_GREEN + str(highest_number) + T_NORMAL,
                            "to",
                            T_GREEN + str(lower_number) + T_NORMAL,
                        )

                torus.json.write_json(file2, lower_data)

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
            higher_data = torus.json.load_json(file1)

            for j in range(i + 1, len_numbers):
                lower_number = numbers[j]
                file2 = get_failures_json(
                    type=TYPE, max_walls=lower_number, flipped=True
                )
                lower_data: list[list[str]] = torus.json.load_json(file2)

                for grid in higher_data:
                    if grid not in lower_data:
                        lower_data.append(grid)
                        print(
                            "adding one possible grid from ",
                            T_GREEN + str(highest_number) + T_NORMAL,
                            "to",
                            T_GREEN + str(lower_number) + T_NORMAL,
                        )

                torus.json.write_json(file2, lower_data)

        print()


if __name__ == "__main__":
    remove_unfound_fails()
    propegate_fails_to_lower_files()
