from typing import List, Tuple
import math
import tqdm  # type: ignore
import json

board_size = 13
num_dots = board_size**2


# takes in int returns 2d coordinate on go board
def int_to_go_coordinate(n: int) -> tuple[float, float]:
    """Return 2d coordinate on go board from int 0-361."""
    if n < 0 or n >= num_dots:
        raise ValueError(f"n must be in range 0-{num_dots}")
    return float(n % board_size), float(n // board_size)


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def is_square(points: List[Tuple[float, float]]) -> bool:
    if len(points) != 4.0:
        return False  # There must be exactly four points

    # Calculate distances between all pairs of points
    dists = []
    for i in range(4):
        for j in range(i + 1, 4):
            dists.append(distance(points[i], points[j]))

    # Sort distances to easily check for equal side lengths and diagonals
    dists.sort()

    # Check if the first 4 distances (sides) are equal and the last 2 (diagonals) are equal
    return (dists[0] == dists[1] == dists[2] == dists[3]) and (dists[4] == dists[5])


solutions = []
for i in tqdm.tqdm(range(num_dots - 3)):
    for j in range(i + 1, num_dots - 2):
        for k in range(j + 1, num_dots - 1):
            for l in range(k + 1, num_dots):
                points = [int_to_go_coordinate(x) for x in [i, j, k, l]]
                if is_square(points):
                    solutions.append(points)

with open("solutions.json", "w") as f:
    json.dump(solutions, f, indent=2)

print(f"Found {len(solutions)} solutions")
