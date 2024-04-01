import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np


class Letter:
    letter = ""
    center = (0, 0)
    border = []
    hole = []

    def __init__(self, letter):
        if letter not in "MTA":
            raise ValueError(f"Unknown letter: {letter}")
        self.letter = letter
        if letter == "M":
            self.border = [
                (-0.05, -0.20),
                (-0.17, -0.005),
                (-0.2, -0.32),
                (-0.4, -0.32),
                (-0.3, 0.31),
                (-0.1, 0.31),
                (0.0, 0.06),
                (0.1, 0.31),
                (0.3, 0.31),
                (0.4, -0.32),
                (0.2, -0.32),
                (0.17, -0.005),
                (0.05, -0.20),
            ]
        elif letter == "T":
            self.border = [
                (-0.1, -0.33),
                (-0.1, -0.05),  # extra point for plotting
                (-0.1, 0.2),
                (-0.25, 0.2),  # extra point for plotting
                (-0.4, 0.2),
                (-0.4, 0.25),  # extra point for plotting
                (-0.4, 0.32),
                (0, 0.32),  # extra point for plotting
                (0.4, 0.32),
                (0.4, 0.25),  # extra point for plotting
                (0.4, 0.2),
                (0.25, 0.2),  # extra point for plotting
                (0.1, 0.2),
                (0.1, 0.05),  # extra point for plotting
                (0.1, -0.33),
            ]
        elif letter == "A":
            self.border = [
                (0.2, 0.31),
                (0.35, -0.32),
                (0.25, -0.32),  # extra
                (0.15, -0.32),
                (0.1, -0.07),
                (0.0, -0.07),  # extra
                (-0.1, -0.07),
                (-0.15, -0.32),
                (-0.25, -0.32),  # extra
                (-0.35, -0.32),
                (-0.2, 0.31),
            ]
            self.hole = [
                (-0.1, 0.06),
                (-0.05, 0.06),  # extra
                (0, 0.06),  # extra
                (0.05, 0.06),  # extra
                (0.1, 0.06),
                (0.1, 0.19),
                (0.05, 0.19),  # extra
                (0.0, 0.19),  # extra
                (-0.05, 0.19),  # extra
                (-0.1, 0.19),
            ]
        else:
            raise ValueError(f"Unknown letter: {letter}")

    def shift(self, dx, dy):
        self.center = (self.center[0] + dx, self.center[1] + dy)

    def rotate(self, angle):
        self.border = [
            (
                x * np.cos(angle) - y * np.sin(angle) + self.center[0],
                x * np.sin(angle) + y * np.cos(angle) + self.center[1],
            )
            for x, y in self.border
        ]
        if self.hole:
            self.hole = [
                (
                    x * np.cos(angle) - y * np.sin(angle) + self.center[0],
                    x * np.sin(angle) + y * np.cos(angle) + self.center[1],
                )
                for x, y in self.hole
            ]

    def stretch(self, sx, sy):
        self.border = [
            (x * sx + self.center[0], y * sy + self.center[1]) for x, y in self.border
        ]
        if self.hole:
            self.hole = [
                (x * sx + self.center[0], y * sy + self.center[1]) for x, y in self.hole
            ]


if __name__ == "__main__":
    # plot the border and hole of the letter 'A'
    mask = Letter(letter="T")

    print(mask.border)
    print(mask.hole)

    fig, ax = plt.subplots()

    closed_border = mask.border + [mask.border[0]]
    shifted_border = [
        (x + mask.center[0], y + mask.center[1]) for x, y in closed_border
    ]
    border_path = Path(shifted_border)  # Close the loop
    border_patch = patches.PathPatch(
        border_path, facecolor="lightblue", lw=2, alpha=0.5
    )
    ax.add_patch(border_patch)

    # Plot the hole if it exists
    if mask.hole:
        closed_hole = mask.hole + [mask.hole[0]]
        shifted_hole = [
            (x + mask.center[0], y + mask.center[1]) for x, y in closed_hole
        ]
        hole_path = Path(shifted_hole)  # Close the loop
        hole_patch = patches.PathPatch(hole_path, facecolor="white", lw=2)
        ax.add_patch(hole_patch)

    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect("equal")
    plt.title("2D Preview of Letter 'A'")

    plt.show()
