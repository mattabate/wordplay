import curses


INITIAL_TEMPLATE = [
    "TIN████@@@██SIW",
    "ERTUBE█@@@██INN",
    "RESTED█@@@█INTE",
    "███EASYTHERE███",
    "___N@H@__█@D@__",
    "@@@S@E@█@M@█@@@",
    "@@@I@E█__I█R@@@",
    "___L@R___SKI___",
    "EADS█A__█SIGHTR",
    "LLS█@N@█STRAWPO",
    "__@A@█__@OST___",
    "███INORDERTO███",
    "ROAD█@@@█SENTAB",
    "ING██@@@█ONIONR",
    "THE██@@@████SOO",
]

INITIAL_TEMPLATE = [
    "█SELAH█@@@@█KSU",
    "DTCAKE█@@@@█BUN",
    "RATION█@@@@█OPE",
    "JRS█________X██",
    "███_________███",
    "@@@____________",
    "@@@____________",
    "@@@_█_____█_@@@",
    "____________@@@",
    "____________@@@",
    "███_________███",
    "██R________█CPO",
    "INE█@@@@█CATHER",
    "UBE█@@@@█INNERT",
    "MAL█@@@@█@@ACK█",
]

INITIAL_TEMPLATE = [
    "█TI@@@█@@@@█DRE",
    "DTCAKE█@@@@█BUN",
    "PLAYER█@@@@█ONE",
    "IEN█________AN█",
    "███______█@@TE█",
    "@@@______█USSR█",
    "@@@_________███",
    "HNUT█TORUS█DOUG",
    "███_________@@@",
    "█DNAS█______@@@",
    "█OEIL█______███",
    "█EW________█SFO",
    "ISM█@@@@█DESPOT",
    "UBE█@@@@█INNERT",
    "DAX█@@@@█COOEE█",
]


def print_grid(stdscr, grid):
    stdscr.clear()
    for i, line in enumerate(grid):
        # Replace '?' with '_' and '.' with '█'
        line = line.replace("?", "_").replace(".", "█")
        stdscr.addstr(i, 0, line)
    stdscr.refresh()


def rotate_right(grid):
    return [row[-1] + row[:-1] for row in grid]


def rotate_left(grid):
    return [row[1:] + row[0] for row in grid]


def rotate_up(grid):
    return grid[1:] + [grid[0]]


def rotate_down(grid):
    return [grid[-1]] + grid[:-1]


def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    grid = INITIAL_TEMPLATE.copy()
    print_grid(stdscr, grid)

    while True:
        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            grid = rotate_right(grid)
        elif key == curses.KEY_LEFT:
            grid = rotate_left(grid)
        elif key == curses.KEY_UP:
            grid = rotate_up(grid)
        elif key == curses.KEY_DOWN:
            grid = rotate_down(grid)
        print_grid(stdscr, grid)


# Run the program
curses.wrapper(main)
