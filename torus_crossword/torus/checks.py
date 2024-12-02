from collections import deque

from torus.strings import replace_char_in_string
from config import C_WALL, GRIDCELLS, ROWLEN


def enforce_symmetry(grid: list[str]) -> list[str]:
    long_string = "".join(grid)
    for j, c in enumerate(long_string):
        rvs_idx = GRIDCELLS - 1 - j
        rvs_c = long_string[rvs_idx]

        # ENFORCE SYMETRY
        if c == C_WALL:
            if rvs_c != C_WALL and rvs_c != "_":  # check symetry
                return False
            if rvs_c == "_":  # enforce symetry
                long_string = replace_char_in_string(long_string, C_WALL, rvs_idx)
        elif c != "_":
            if rvs_c == C_WALL:  # check symetry
                return False
            if rvs_c == "_":  # enforce symetry
                long_string = replace_char_in_string(long_string, "@", rvs_idx)

    return [long_string[j : j + ROWLEN] for j in range(0, GRIDCELLS, ROWLEN)]


def grid_contains_englosed_spaces(grid):
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]

    # Directions for moving up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Find the starting point for a non-wall character
    start = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "█":
                start = (r, c)
                break
        if start:
            break

    if not start:
        return False  # No white squares

    # BFS to check connectivity
    queue = deque([start])
    visited[start[0]][start[1]] = True
    count = 1  # Number of visited white squares

    while queue:
        r, c = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and not visited[nr][nc]
                and grid[nr][nc] != "█"
            ):
                visited[nr][nc] = True
                queue.append((nr, nc))
                count += 1

    # Count all non-wall squares
    total_non_wall = sum(row.count("█") for row in grid)
    total_non_wall = rows * cols - total_non_wall  # Total non-wall characters

    return count != total_non_wall
