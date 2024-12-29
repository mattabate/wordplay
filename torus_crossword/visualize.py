import sys
import json
from typing import List
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import torus

JSON_FILE = "solutions/15x15_grid_solutions_DA_42_flipped.json"

#############################
#   Common-cells detection
#############################


def find_common_cells(crosswords: List[List[str]]) -> List[List[str]]:
    """
    Return a 15x15 matrix 'common_chars' where:
    - common_chars[r][c] = None if that cell varies across the crosswords,
    - common_chars[r][c] = that single character if the cell is the same
      in ALL crosswords (e.g., always '█', or always 'A', etc.).
    """
    rows, cols = 15, 15
    common_chars = [[None for _ in range(cols)] for _ in range(rows)]

    # For each cell, check if it's identical across all crosswords
    for r in range(rows):
        for c in range(cols):
            first_char = crosswords[0][r][c]
            if all(cw[r][c] == first_char for cw in crosswords):
                common_chars[r][c] = first_char

    return common_chars


#############################
#     Main Viewer Class
#############################


class CrosswordViewer(QMainWindow):
    def __init__(self, scored_crosswords):
        """
        :param scored_crosswords: List of tuples (grid, score),
                                  sorted by descending score.
        """
        super().__init__()

        # This is our (grid, score) list, sorted highest -> lowest
        self.scored_crosswords = scored_crosswords
        self.current_index = 0

        self.setWindowTitle("Crossword Viewer")

        # Extract just the grids for determining common cells
        all_grids = [item[0] for item in scored_crosswords]
        self.common_cells = find_common_cells(all_grids)

        # -- Main Widget and Layout --
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        # Remove or adjust margins if desired
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        # -- Top Info Area --
        # We'll stick the rank & score label in a small fixed-height area
        self.info_layout = QHBoxLayout()
        self.info_label = QLabel("", self)
        self.info_label.setFont(QFont("Arial", 14))
        self.info_label.setFixedHeight(30)  # <--- Make the text area fixed in height
        self.info_layout.addWidget(self.info_label)
        self.main_layout.addLayout(self.info_layout)

        # -- Grid Layout for the 15×15 Crossword --
        self.grid_layout = QGridLayout()
        # We want the grid to expand fully in the remaining space
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(1)
        self.main_layout.addLayout(self.grid_layout, stretch=1)

        # Create the 15×15 grid of QLabels
        self.labels = []
        for row in range(15):
            row_labels = []
            for col in range(15):
                lbl = QLabel("", self)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Arial", 14))

                # 1) Make labels expand both horizontally & vertically
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                self.grid_layout.addWidget(lbl, row, col)
                row_labels.append(lbl)
            self.labels.append(row_labels)

        # 2) Give each row/column a stretch factor
        for i in range(15):
            self.grid_layout.setRowStretch(i, 1)
            self.grid_layout.setColumnStretch(i, 1)

        # Render the first crossword
        self.update_grid(self.current_index)

    def update_info_label(self):
        """
        Update the info label in the top-left with rank and score.
        """
        rank = self.current_index + 1
        total = len(self.scored_crosswords)
        score = self.scored_crosswords[self.current_index][1]
        self.info_label.setText(
            f"Rank {rank}/{total} — Score: {score:.2f} -- Words: {len(torus.grid.get_words_in_filled_grid(self.scored_crosswords[self.current_index][0]))}"
        )

    def update_grid(self, index):
        """
        Update the 15×15 QLabels to display the crossword at scored_crosswords[index],
        highlighting cells that never change across all crosswords.
        """
        crossword, score = self.scored_crosswords[index]

        # Update the rank/score label
        self.update_info_label()

        for row in range(15):
            row_string = crossword[row]
            for col in range(15):
                char = row_string[col]
                lbl = self.labels[row][col]
                common_char = self.common_cells[row][col]

                if char == "█":
                    # It's a wall
                    lbl.setText("")  # Usually hide the '█'
                    palette = lbl.palette()
                    palette.setColor(
                        QPalette.Window, QColor(0, 0, 0)
                    )  # black background
                    lbl.setAutoFillBackground(True)
                    lbl.setPalette(palette)

                    # If it's *always* a wall, show '█' in blue
                    if common_char == "█":
                        lbl.setText("█")
                        lbl.setStyleSheet("color: blue;")
                    else:
                        lbl.setStyleSheet("color: black;")

                else:
                    # It's a letter
                    lbl.setText(char)
                    palette = lbl.palette()
                    palette.setColor(
                        QPalette.Window, QColor(255, 255, 255)
                    )  # white background
                    lbl.setAutoFillBackground(True)
                    lbl.setPalette(palette)

                    # If it's always the same letter, highlight background
                    if common_char and common_char != "█":
                        palette.setColor(
                            QPalette.Window, QColor(173, 216, 230)
                        )  # light blue
                        lbl.setPalette(palette)

    def keyPressEvent(self, event):
        """
        Handle left/right arrow keys to flip through crosswords.
        """
        if event.key() == Qt.Key_Right:
            # Move to next crossword if possible
            if self.current_index < len(self.scored_crosswords) - 1:
                self.current_index += 1
                self.update_grid(self.current_index)

        elif event.key() == Qt.Key_Left:
            # Move to previous crossword if possible
            if self.current_index > 0:
                self.current_index -= 1
                self.update_grid(self.current_index)

        else:
            super().keyPressEvent(event)


#############################
#           main()
#############################


def main():
    app = QApplication(sys.argv)

    # 1) Load the crosswords from the JSON file
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        crosswords = json.load(f)  # List of 15x15 grids

    new_crosswords = []
    for cw in crosswords:
        sol_template = torus.grid.get_grid_template_str_from_grid_str("".join(cw))
        if sol_template in [
            "@@@██@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@@█@@@@@@███@@@@@@@█@@@█@@@███@@@@@@█@@@@@@@@██@@@█@@@@@@@@@@█@@@@@█@@@@@@@@@@█@@@██@@@@@@@@█@@@@@@███@@@█@@@█@@@@@@@███@@@@@@█@@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@██@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@█@@@@@@@███@@@@@███@@@█@@@███@@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@@███@@@█@@@███@@@@@███@@@@@@@█@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
        ]:
            continue
        # words = torus.grid.get_words_in_filled_grid(cw)
        # if "ABATEMENT" not in words:
        #     continue
        new_crosswords.append(cw)

    crosswords = new_crosswords
    # 2) Compute scores for each crossword, then sort them descending
    scored_crosswords = []
    scored_crosswords = torus.svm.grids_av_score(crosswords)

    scored_crosswords.sort(key=lambda x: x[1], reverse=True)

    # 3) Instantiate the viewer with the (grid, score) pairs
    viewer = CrosswordViewer(scored_crosswords)
    viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
