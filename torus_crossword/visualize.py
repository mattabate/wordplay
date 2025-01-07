import sys
import json
from typing import List, Tuple, Dict
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
from PyQt5.QtCore import Qt, pyqtSignal
import torus

JSON_FILE = "solutions/15x15_grid_solutions_DA_42_flipped.json"

#############################
#   Common-cells detection
#############################


def find_common_cells(crosswords: List[List[str]]) -> List[List[str]]:
    """
    Given a list of 15×15 grids (each grid is a list of 15 strings),
    returns a 15×15 matrix 'common_chars' where:
      - common_chars[r][c] = None if that cell varies across the crosswords,
      - common_chars[r][c] = that single character if the cell is the same
        in ALL crosswords (e.g., always '█', or always 'A', etc.).
    """
    if not crosswords:
        # If no crosswords, return a matrix of Nones
        return [[None] * 15 for _ in range(15)]

    rows, cols = 15, 15
    common_chars = [[None for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            first_char = crosswords[0][r][c]
            if all(cw[r][c] == first_char for cw in crosswords):
                common_chars[r][c] = first_char
    return common_chars


#############################
#   Clickable Cell Label
#############################


class ClickableCell(QLabel):
    """
    A QLabel that emits a custom `rightClicked(row, col)` signal whenever
    the user right-clicks the cell.
    """

    rightClicked = pyqtSignal(int, int)

    def __init__(self, row: int, col: int, parent=None):
        super().__init__("", parent)
        self.row = row
        self.col = col
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 14))
        # Make labels expand both horizontally & vertically
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rightClicked.emit(self.row, self.col)
        else:
            super().mousePressEvent(event)


#############################
#     Main Viewer Class
#############################


class CrosswordViewer(QMainWindow):
    def __init__(self, scored_crosswords: List[Tuple[List[str], float]]):
        """
        :param scored_crosswords: List of (grid, score) tuples, sorted descending.
        """
        super().__init__()

        # Keep an original copy of all crosswords so we can re-filter
        self.original_scored_crosswords = scored_crosswords
        # The currently displayed set of crosswords (initially all)
        self.scored_crosswords = list(scored_crosswords)
        self.current_index = 0

        # Dictionary to store locked cells: (row, col) -> letter
        self.locked_cells: Dict[Tuple[int, int], str] = {}

        self.setWindowTitle("Crossword Viewer")

        # We'll compute "filtered_common_cells" on each filter,
        # showing which cells have exactly one possible letter in the *filtered* set.
        self.filtered_common_cells = find_common_cells(
            [cw for cw, _ in self.scored_crosswords]
        )

        # -- Main Widget and Layout --
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        # -- Top Info Area --
        self.info_layout = QHBoxLayout()
        self.info_label = QLabel("", self)
        self.info_label.setFont(QFont("Arial", 14))
        self.info_label.setFixedHeight(30)  # fixed height for top label
        self.info_layout.addWidget(self.info_label)
        self.main_layout.addLayout(self.info_layout)

        # -- Grid Layout for the 15×15 Crossword --
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(1)
        self.main_layout.addLayout(self.grid_layout, stretch=1)

        # Create the 15×15 grid of ClickableCell labels
        self.labels: List[List[ClickableCell]] = []
        for row in range(15):
            row_cells = []
            for col in range(15):
                lbl = ClickableCell(row, col, self)
                lbl.rightClicked.connect(self.handle_right_click)
                self.grid_layout.addWidget(lbl, row, col)
                row_cells.append(lbl)
            self.labels.append(row_cells)

        # Give each row/column a stretch factor
        for i in range(15):
            self.grid_layout.setRowStretch(i, 1)
            self.grid_layout.setColumnStretch(i, 1)

        # Render the first crossword
        self.update_grid(self.current_index)

    def update_info_label(self):
        """
        Update the info label in the top-left with rank, score, word count, etc.
        """
        total = len(self.scored_crosswords)
        if total == 0:
            # In case everything got filtered out.
            self.info_label.setText("No crosswords left after filtering.")
            return

        rank = self.current_index + 1
        score = self.scored_crosswords[self.current_index][1]
        grid = self.scored_crosswords[self.current_index][0]
        word_count = len(torus.grid.get_words_in_filled_grid(grid))
        self.info_label.setText(
            f"Rank {rank}/{total} — Score: {score:.2f} — Words: {word_count}"
        )

    def update_grid(self, index: int):
        """
        Renders the crossword at `self.scored_crosswords[index]` into the label grid.
        Also applies locked-cells coloring (green), and "common among filtered set" (blue).
        """
        if not self.scored_crosswords:
            # If there's nothing to show, clear the grid
            for r in range(15):
                for c in range(15):
                    self.labels[r][c].setText("")
                    palette = self.labels[r][c].palette()
                    palette.setColor(QPalette.Window, QColor(255, 255, 255))
                    self.labels[r][c].setAutoFillBackground(True)
                    self.labels[r][c].setPalette(palette)
            self.update_info_label()
            return

        crossword, _score = self.scored_crosswords[index]
        self.update_info_label()

        # For convenience, let's store the 15×15 matrix of letters that are
        # common across the *filtered* crosswords, so we can highlight them in blue.
        # We already computed self.filtered_common_cells in handle_right_click.
        for row in range(15):
            row_string = crossword[row]
            for col in range(15):
                char = row_string[col]
                lbl = self.labels[row][col]

                # Start with a default "white" background and black text
                palette = lbl.palette()
                palette.setColor(QPalette.Window, QColor(255, 255, 255))
                lbl.setAutoFillBackground(True)
                lbl.setPalette(palette)
                lbl.setStyleSheet("color: black;")

                if char == "█":
                    # It's a black square
                    lbl.setText("")  # Typically hide '█'
                    palette.setColor(
                        QPalette.Window, QColor(0, 0, 0)
                    )  # black background
                    lbl.setAutoFillBackground(True)
                    lbl.setPalette(palette)

                else:
                    # It's a letter
                    lbl.setText(char)

                    # 1) If this cell is locked, highlight green
                    if (row, col) in self.locked_cells:
                        palette.setColor(
                            QPalette.Window, QColor(144, 238, 144)
                        )  # light green
                        lbl.setPalette(palette)
                    else:
                        # 2) If it's not locked but is "common in the filtered set", highlight blue
                        filtered_char = self.filtered_common_cells[row][col]
                        if filtered_char == char:
                            # highlight in light-blue
                            palette.setColor(QPalette.Window, QColor(173, 216, 230))
                            lbl.setPalette(palette)

    def handle_right_click(self, row: int, col: int):
        """
        Toggle fix for (row, col):
          - If not fixed, fix it (store letter).
          - If fixed, un-fix it.
        Then filter crosswords accordingly, and attempt to remain on the same puzzle if possible.
        Also re-compute "filtered_common_cells" so we can highlight newly forced squares in blue.
        """
        if not self.scored_crosswords:
            return

        # Current crossword
        current_cw, current_score = self.scored_crosswords[self.current_index]
        letter = current_cw[row][col]

        # Don't lock black squares
        if letter == "█":
            return

        # Toggle lock
        if (row, col) in self.locked_cells:
            # Un-fix it
            del self.locked_cells[(row, col)]
        else:
            # Fix it (store its letter)
            self.locked_cells[(row, col)] = letter

        # Keep track of which grid we're on (so we can stay on it if it still exists)
        old_grid = current_cw

        # 1) Re-filter from the original list
        new_filtered = []
        for grid, score in self.original_scored_crosswords:
            match = True
            for (r, c), ch in self.locked_cells.items():
                if grid[r][c] != ch:
                    match = False
                    break
            if match:
                new_filtered.append((grid, score))

        # 2) (Optionally) re-sort by score
        # new_filtered.sort(key=lambda x: x[1], reverse=True)

        self.scored_crosswords = new_filtered

        # 3) Compute "common cells" across the newly filtered crosswords
        #    so that we can highlight them in blue in update_grid.
        filtered_grids = [cw for cw, _ in self.scored_crosswords]
        self.filtered_common_cells = find_common_cells(filtered_grids)

        # 4) Attempt to remain on the same crossword if it still exists
        new_index = 0
        for i, (g, s) in enumerate(self.scored_crosswords):
            if g == old_grid:
                new_index = i
                break
        self.current_index = new_index

        # Finally, re-render
        self.update_grid(self.current_index)

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

    # 1) Load the crosswords from the JSON file (LIMIT to first 300)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        crossword_strs = json.load(f)  # List of 15x15 grids
        crossword_strs = crossword_strs[:300]  # <--- Limit to first 300
        crosswords = [torus.grid.str_to_grid(grid_str) for grid_str in crossword_strs]

    # Example filter logic from your code:
    new_crosswords = []
    for cw in crosswords:
        sol_template = torus.grid.get_grid_template_str_from_grid_str("".join(cw))
        if sol_template in [
            "@@@██@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@@█@@@@@@███@@@@@@@█@@@█@@@███@@@@@@█@@@@@@@@█@@@@██@@@@@@@@@█@@@@@█@@@@@@@@@██@@@@█@@@@@@@@█@@@@@@███@@@█@@@█@@@@@@@███@@@@@@█@@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@██@@@",
            "@@@██@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@@█@@@@@@███@@@@@@██@@@█@@@███@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@███@@@█@@@██@@@@@@███@@@@@@█@@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@██@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@██@@@@@@███@@@@@@██@@@█@@@███@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@███@@@█@@@██@@@@@@███@@@@@@██@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@███@@@@@███@@@@@@@█@@@█@@@███@@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@@███@@@█@@@█@@@@@@@███@@@@@███@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
            "@@@██@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@@█@@@@@@███@@@@@@██@@@█@@@███@@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@@███@@@█@@@██@@@@@@███@@@@@@█@@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@██@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@█@@@@@@@███@@@@@███@@@█@@@███@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@███@@@█@@@███@@@@@███@@@@@@@█@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@██@@@@@@███@@@@@@██@@@█@@@███@@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@@███@@@█@@@██@@@@@@███@@@@@@██@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@█@@@@@@@███@@@@@███@@@█@@@███@@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@@███@@@█@@@███@@@@@███@@@@@@@█@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@██@@@@@@███@@@@@@██@@@█@@@███@@@@@@█@@@@@@@@█@@@@█@@@@@@@@@@█@@@@@█@@@@@@@@@@█@@@@█@@@@@@@@█@@@@@@███@@@█@@@██@@@@@@███@@@@@@██@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
            "@@@██@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@@██@@@@@███@@@@@@@█@@@█@@@███@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@███@@@█@@@█@@@@@@@███@@@@@██@@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@██@@@",
            "@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@███@@@@@███@@@@@@@█@@@█@@@███@@@@@@█@@@@@@@@█@@@@█@@@@@@@@@@█@@@@@█@@@@@@@@@@█@@@@█@@@@@@@@█@@@@@@███@@@█@@@█@@@@@@@███@@@@@███@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@",
            "@@@██@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@@@██@@@@@███@@@@@@@█@@@█@@@███@@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@█@@@@@@@@█@@@@@@█@@@@@@@@█@@@@@@███@@@█@@@█@@@@@@@███@@@@@██@@@@@@@@@@@█@@@@█@@@@@@@@@█@@@@█@@@@@@@@@█@@@██@@@",
        ]:
            continue
        words = torus.grid.get_words_in_filled_grid(cw)
        if (
            "LEONES" in words
            or "LEONID" in words
            or "ACIDTEST" in words
            or "PATOOT" in words
        ):
            continue
        new_crosswords.append(cw)

    crosswords = new_crosswords

    # 2) Compute scores for each crossword, then sort them descending
    scored_crosswords = torus.svm.grids_av_score(crosswords)
    scored_crosswords.sort(key=lambda x: x[1], reverse=True)

    # 3) Instantiate the viewer with the (grid, score) pairs
    viewer = CrosswordViewer(scored_crosswords)
    viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
