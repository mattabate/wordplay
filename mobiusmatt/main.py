import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches


class Mask:
    border = []
    hole = []

    def __init__(self, border, hole=[]):
        self.border = border
        self.hole = hole

    def shift(self, dx, dy):
        return Mask(
            border=[(x + dx, y + dy) for x, y in self.border],
            hole=[(x + dx, y + dy) for x, y in self.hole],
        )


m_mask = Mask(
    [
        (0.1, 0.4),
        (0.6, 0.3),
        (0.6, 0.1),
        (0.4, 0.0),
        (0.6, -0.1),
        (0.6, -0.3),
        (0.1, -0.4),
        (0.1, -0.2),
        (0.35, -0.17),
        (0.2, -0.05),
        (0.2, 0.05),
        (0.35, 0.17),
        (0.1, 0.2),
    ],
    [],
)
t_mask = Mask(
    [
        (0.1, 0.1),
        (0.5, 0.1),
        (0.5, 0.4),
        (0.6, 0.4),
        (0.6, -0.4),
        (0.5, -0.4),
        (0.5, -0.1),
        (0.1, -0.1),
        (0.1, 0.1),
    ],
    [],
)
a_mask = Mask(
    border=[
        (0.1, 0.35),
        (0.6, 0.2),
        (0.6, -0.2),
        (0.1, -0.35),
        (0.1, -0.15),
        (0.3, -0.1),
        (0.3, 0.1),
        (0.1, 0.15),
    ],
    hole=[
        (0.4, 0.1),
        (0.4, -0.1),
        (0.5, -0.1),
        (0.5, 0.1),  # Close the loop
    ],
)


# Define the parameterization of the Möbius strip
def mobius_strip(u, v):
    x = (1 + v / 2 * np.cos(u / 2)) * np.cos(u)
    y = (1 + v / 2 * np.cos(u / 2)) * np.sin(u)
    z = v / 5 * np.sin(u / 2)
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


def plot_2d_test_layout(masks: list[Mask]):
    fig, ax = plt.subplots()
    strip_rectangle = patches.Rectangle(
        (0, -0.5), 2 * np.pi, 1, linewidth=1, edgecolor="r", facecolor="none"
    )
    ax.add_patch(strip_rectangle)

    for mask in masks:
        # Plot the border
        border_path = Path(mask.border + [mask.border[0]])  # Close the loop
        border_patch = patches.PathPatch(
            border_path, facecolor="lightblue", lw=2, alpha=0.5
        )
        ax.add_patch(border_patch)

        # Plot the hole if it exists
        if mask.hole:
            hole_path = Path(mask.hole + [mask.hole[0]])  # Close the loop
            hole_patch = patches.PathPatch(hole_path, facecolor="white", lw=2)
            ax.add_patch(hole_patch)

    # Add colored dots to specified corners
    ax.plot(2 * np.pi, 0.5, "ro", markersize=20)  # Red dot in the upper right corner
    ax.plot(0, -0.5, "ro", markersize=20)  # Red dot in the lower left corner
    ax.plot(2 * np.pi, -0.5, "bo", markersize=20)  # Blue dot in the lower right corner
    ax.plot(0, 0.5, "bo", markersize=20)  # Blue dot in the upper left corner

    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect("equal")
    plt.title("2D Preview of Möbius Strip Layout")
    plt.show()


if __name__ == "__main__":

    nonconvex_polygons = [
        t_mask.shift(0.001, 0),
        t_mask.shift(np.pi / 4 + 0.001, 0),
        a_mask.shift(np.pi / 2, 0),
        m_mask.shift(3 * np.pi / 4, 0),
        t_mask.shift(np.pi + 0.001, 0),
        t_mask.shift(5 * np.pi / 4 + 0.001, 0),
        a_mask.shift(3 * np.pi / 2, 0),
        m_mask.shift(7 * np.pi / 4, 0),
    ]

    test_flag = False  # Set to True to see the 2D preview

    plot_2d_test_layout(nonconvex_polygons)

    if not test_flag:
        # Generate a dense meshgrid for finer detail
        u = np.linspace(0, 2 * np.pi, 2000)
        v = np.linspace(-0.5, 0.5, 100)
        u, v = np.meshgrid(u, v)

        x, y, z = mobius_strip(u, v)
        for polygon_points in nonconvex_polygons:
            # Example of applying the new function to the 'A' mask
            inside_mask = is_inside_complex_polygon(
                polygon_points.border, polygon_points.hole, u, v
            )
            x[inside_mask], y[inside_mask], z[inside_mask] = (
                np.nan,
                np.nan,
                np.nan,
            )

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        # ax.plot_surface(x, y, z, color="cyan", edgecolor="none", alpha=0.6)
        colors = plt.cm.hsv(u / (2 * np.pi))

        # Plot the surface with the facecolors set to the colormap
        ax.plot_surface(x, y, z, facecolors=colors, edgecolor="none", alpha=0.6)

        # Set the title and axis limits
        ax.set_title("Möbius Matt", fontsize=40)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)

        # Hide the axes for a cleaner look
        ax.set_axis_off()

        # Set initial view
        ax.view_init(elev=30, azim=30)

        # Oscillation parameters
        elev_start = -40
        elev_end = 75
        frames_per_oscillation = 80
        total_cycles = 5
        azim_change_per_frame = 360 / (frames_per_oscillation * total_cycles)
        azim_current = 30

        try:
            # Total frames for both upward and downward oscillation
            for frame in range(frames_per_oscillation * total_cycles * 2):
                if frame % (frames_per_oscillation * 2) < frames_per_oscillation:
                    # Upward oscillation in z
                    elev = np.linspace(elev_start, elev_end, frames_per_oscillation)[
                        frame % frames_per_oscillation
                    ]
                else:
                    # Downward oscillation in z
                    elev = np.linspace(elev_end, elev_start, frames_per_oscillation)[
                        frame % frames_per_oscillation
                    ]

                # Counter-clockwise rotation by decreasing the azimuth angle
                azim_current -= azim_change_per_frame
                ax.view_init(elev=elev, azim=azim_current)
                plt.draw()
                plt.pause(0.1)  # Adjust as needed for your screen recording

        except KeyboardInterrupt:
            pass
