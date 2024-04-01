import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matt_font import Letter
import fire


def map_to_torus(u, v, R=1, r=0.3):
    """
    Maps a grid of points (u, v) to a torus.

    Parameters:
    - u, v: 2D arrays of points representing the parameterized surface of the torus.
    - R: The distance from the center of the tube to the center of the torus.
    - r: The radius of the tube.

    Returns:
    - x, y, z: Coordinates of the torus surface.
    """
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return x, y, z


def is_inside_complex_polygon(border_points, hole_points, u, v):
    """
    Check if the points (u, v) are inside a complex polygon defined by 'border_points'
    and not inside 'hole_points'.
    """
    border_path = Path(border_points)
    hole_path = Path(hole_points) if hole_points else None

    # Initially check if points are inside the border
    inside_border = border_path.contains_points(
        np.vstack((u.flatten(), v.flatten())).T
    ).reshape(u.shape)

    # Then, if there's a hole, check if points are inside it and exclude those
    if hole_path:
        inside_hole = hole_path.contains_points(
            np.vstack((u.flatten(), v.flatten())).T
        ).reshape(u.shape)
        return np.logical_and(inside_border, ~inside_hole)
    else:
        return inside_border


def plot_2d_test_layout(masks: list[Letter]):
    fig, ax = plt.subplots()

    for mask in masks:
        closed_border = mask.border + [mask.border[0]]
        centerd_border = [
            (x + mask.center[0], y + mask.center[1]) for x, y in closed_border
        ]
        border_path = Path(centerd_border)  # Close the loop
        border_patch = patches.PathPatch(
            border_path, facecolor="lightblue", lw=2, alpha=0.5
        )
        ax.add_patch(border_patch)

        # Plot the hole if it exists
        if mask.hole:
            closed_hole = mask.hole + [mask.hole[0]]
            centerd_hole = [
                (x + mask.center[0], y + mask.center[1]) for x, y in closed_hole
            ]
            hole_path = Path(centerd_hole)  # Close the loop
            hole_patch = patches.PathPatch(hole_path, facecolor="white", lw=2)
            ax.add_patch(hole_patch)

    # Add colored dots to specified corners
    ax.plot(0, 0, "ro", markersize=20)  # Red dot in the upper right corner
    ax.plot(0, -2 * np.pi, "ro", markersize=20)  # Red dot in the lower left corner
    ax.plot(2 * np.pi, 0, "bo", markersize=20)  # Blue dot in the lower right corner
    ax.plot(
        2 * np.pi, -2 * np.pi, "bo", markersize=20
    )  # Blue dot in the upper left corner

    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(-2 * np.pi, 0)
    ax.set_aspect("equal")
    plt.title("2D Preview of Möbius Strip Layout")
    plt.show()


def main(word="MATT", test: bool = False, num_x=1, num_y=1):
    text_on_strip = word * num_x
    text_on_torus = []

    radius = 2
    inner_radius = 1.2

    for i in range(num_y * len(word)):
        text_on_torus.append(text_on_strip[i:] + text_on_strip[:i])

    nonconvex_polygons = []
    for j, line in enumerate(text_on_torus):
        for i, letter in enumerate(line):
            mask = Letter(letter=letter)

            width_x = num_x * len(word)
            width_y = num_y * len(word)

            delta_x = 2 * np.pi / width_x
            delta_y = 2 * np.pi / width_y

            mask.stretch(delta_x, delta_y)
            x_shift = delta_x * (i + 1 / 2) + 0.01
            y_shift = -delta_y * (j + 1 / 2) + 0.01
            mask.shift(
                x_shift,
                y_shift,
            )
            nonconvex_polygons.append(mask)

    if test:
        plot_2d_test_layout(nonconvex_polygons)

    if not test:
        # Generate a dense meshgrid for finer detail
        u = np.linspace(0, 2 * np.pi, 800)
        v = np.linspace(-2 * np.pi, 0, 200)
        u, v = np.meshgrid(u, v)

        fig = plt.figure()

        ax = fig.add_subplot(111, projection="3d")

        for polygon_points in nonconvex_polygons:
            x, y, z = map_to_torus(u, v, R=radius, r=inner_radius)

            shifed_border = [
                (x + polygon_points.center[0], y + polygon_points.center[1])
                for x, y in polygon_points.border
            ]
            shifed_hole = [
                (x + polygon_points.center[0], y + polygon_points.center[1])
                for x, y in polygon_points.hole
            ]

            inside_mask = is_inside_complex_polygon(shifed_border, shifed_hole, u, v)
            inside_mask = ~inside_mask
            x[inside_mask], y[inside_mask], z[inside_mask] = (
                np.nan,
                np.nan,
                np.nan,
            )

            colors = plt.cm.hsv(u / (2 * np.pi))
            # colors = np.zeros((*u.shape, 3), dtype=int)

            # Plot the surface with the facecolors set to the colormap
            ax.plot_surface(x, y, z, facecolors=colors, edgecolor="none", alpha=1)

        # Set the title and axis limits
        ax.set_title("Möbius Matt", fontsize=40)

        ax.set_xlim(-radius * 1.2, radius * 1.2)
        ax.set_ylim(-radius * 1.2, radius * 1.2)
        ax.set_zlim(-radius, radius)

        # Hide the axes for a cleaner look
        ax.set_axis_off()

        # Set initial view
        ax.view_init(elev=90, azim=30)

        plt.show()


if __name__ == "__main__":
    fire.Fire(main)
