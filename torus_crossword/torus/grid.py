def str_to_grid(grid_str: str) -> list[str]:
    return [grid_str[i : i + 15] for i in range(0, len(grid_str), 15)]
