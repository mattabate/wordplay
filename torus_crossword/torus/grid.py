from torus.strings import replace_char_in_string

T_NORMAL = "\033[0m"
ROWLEN = 15


def str_to_grid(grid_str: str) -> list[str]:
    return [grid_str[i : i + 15] for i in range(0, len(grid_str), 15)]


def print_grid(grid: list[str], h: tuple[str, int, str]):

    grid_copy = grid.copy()

    h_color = h[2]
    if h[0] == "r":
        grid_copy[h[1]] = h_color + grid_copy[h[1]] + T_NORMAL
    else:
        for i in range(ROWLEN):
            grid_copy[i] = replace_char_in_string(
                grid_copy[i], h_color + grid_copy[i][h[1]] + T_NORMAL, h[1]
            )

    return "\n".join(grid_copy) + T_NORMAL
