import os
import tqdm
import torus
from lib import T_YELLOW, T_NORMAL

files = os.listdir("bad_solutions")

for f in files:
    f = "bad_solutions/" + f
    bad_solutions = torus.json.load_json(f)
    # get all file names in the bad_solutions folder - dont use torus
    l = len(bad_solutions)
    print("Searching", f)
    print(
        f"found ",
        T_YELLOW,
        l,
        f" bad solutions. Lines ",
        T_YELLOW,
        f"{2+17*l}",
        T_NORMAL,
    )

    unique_bad_str = []
    for g in tqdm.tqdm(bad_solutions):
        g_str = "".join(g)
        if g_str not in unique_bad_str:
            unique_bad_str.append(g_str)

    torus.json.write_json(f, unique_bad_str)
    print(
        f"saved ",
        T_YELLOW,
        {len(unique_bad_str)},
        T_NORMAL,
        " unique bad solutions. lines {2+len(unique_bad_str)}",
    )
    print("\n\n")
# files = os.listdir("bad_solutions")

# print(len(bad_solutions))
# print(files)
