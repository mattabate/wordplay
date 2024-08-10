import json


def transpose(grid: list[str]) -> list[str]:
    return ["".join(row) for row in zip(*grid)]


file = "star_sols.json"
file = "star_sols_flipped.json"
with open(file, "r") as f:
    star_sols = json.load(f)

word = "RYANONEAL"

print(len(star_sols))
new_star_sols = []

for star in star_sols:

    fails = False
    for line in star:
        if word in line:
            break
    else:
        for line in transpose(star):
            if word in line:
                break
        else:
            new_star_sols.append(star)


print(len(new_star_sols))

with open(file, "w") as f:
    json.dump(new_star_sols, f, indent=2, ensure_ascii=False)
