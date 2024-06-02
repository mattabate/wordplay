import json
import math
from typing import List, Tuple
import tqdm

with open("solutions.json") as f:
    solutions = json.load(f)


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def square_area(points: List[Tuple[float, float]]) -> bool:
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
    if (dists[0] == dists[1] == dists[2] == dists[3]) and (dists[4] == dists[5]):
        return dists[0] ** 2


num = 0
for i, solution in enumerate(solutions):
    area = square_area(solution)
    if (area - 29.0) ** 2 <= 0.1:
        num += 1
        print(f"Solution {i + 1}: {solution}")

print(num)
