import json
from lib import load_json, transpose

word = "CANDYCOAT"


for file in ["star_sols.json", "star_sols_flipped.json"]:

    star_sols = load_json(file)

    initial_num = len(star_sols)
    new_star_sols = []

    for star in star_sols:

        fails = False
        for line in star:
            if word in line:
                print("found " + word)
                break
        else:
            for line in transpose(star):
                if word in line:
                    print("found " + word)
                    break
            else:
                new_star_sols.append(star)

    final_num = len(new_star_sols)
    print("number removed ", initial_num - final_num)

    with open(file, "w") as f:
        json.dump(new_star_sols, f, indent=2, ensure_ascii=False)
