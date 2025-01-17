import sys
import json
from typing import List, Tuple, Dict, Set
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QSizePolicy,
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import torus

JSON_FILE = "solutions/15x15_grid_solutions_DA_42_flipped.json"


#############################
#   Utility / Common
#############################


def find_common_cells(crosswords: List[List[str]]) -> List[List[str]]:
    """
    Returns a 15×15 matrix 'common_chars' where:
      - None if that cell varies across crosswords,
      - a single character if the cell is the same in ALL crosswords.
    """
    if not crosswords:
        return [[None] * 15 for _ in range(15)]

    rows, cols = 15, 15
    common_chars = [[None for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            first_char = crosswords[0][r][c]
            if all(cw[r][c] == first_char for cw in crosswords):
                common_chars[r][c] = first_char
    return common_chars


def get_possible_letters_for_cell(
    crosswords: List[List[str]], row: int, col: int
) -> Set[str]:
    """
    Among the given crosswords, return all distinct letters that appear
    at (row, col), *excluding* black squares ('█').
    """
    letters = set()
    for grid in crosswords:
        ch = grid[row][col]
        if ch != "█":
            letters.add(ch)
    return letters


def get_across_word_indices(grid: List[str], row: int, col: int) -> Tuple[int, int]:
    """
    Finds the start_col and end_col of the 'across word' containing (row, col),
    bounded by black squares ('█') or edges of the grid.
    """
    start_c = col
    while start_c > 0 and grid[row][start_c - 1] != "█":
        start_c -= 1

    end_c = col
    while end_c < 14 and grid[row][end_c + 1] != "█":
        end_c += 1

    return (start_c, end_c)


def get_down_word_indices(grid: List[str], row: int, col: int) -> Tuple[int, int]:
    """
    Same idea but for vertical (down).
    """
    start_r = row
    while start_r > 0 and grid[start_r - 1][col] != "█":
        start_r -= 1

    end_r = row
    while end_r < 14 and grid[end_r + 1][col] != "█":
        end_r += 1

    return (start_r, end_r)


def extract_word_from_grid(
    grid: List[str], row1: int, col1: int, row2: int, col2: int, direction: str
) -> str:
    """
    Extract the substring from the grid in 'across' or 'down' direction.
    """
    if direction == "across":
        r = row1
        return "".join(grid[r][c] for c in range(col1, col2 + 1))
    else:  # 'down'
        c = col1
        return "".join(grid[r][c] for r in range(row1, row2 + 1))


#############################
#   Clickable Cell
#############################


class ClickableCell(QLabel):
    # We'll use left-click for selection
    leftClicked = pyqtSignal(int, int)

    def __init__(self, row: int, col: int, parent=None):
        super().__init__("", parent)
        self.row = row
        self.col = col
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 14))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Emit signal for "cell selected"
            self.leftClicked.emit(self.row, self.col)
        else:
            super().mousePressEvent(event)


#############################
#     Main Viewer Class
#############################


class CrosswordViewer(QMainWindow):
    def __init__(self, scored_crosswords: List[Tuple[List[str], float]]):
        super().__init__()

        self.original_scored_crosswords = scored_crosswords
        self.scored_crosswords = list(scored_crosswords)
        self.current_index = 0

        # Dictionary for locked cells: (r, c) -> letter
        self.locked_cells: Dict[Tuple[int, int], str] = {}

        # Currently selected cell
        self.selected_cell = None  # (row, col) or None

        # Precompute "common" letters across the *current* filtered set
        self.filtered_common_cells = find_common_cells(
            [cw for cw, _ in self.scored_crosswords]
        )

        self.setWindowTitle("Crossword Viewer")

        # ========== Main Layout ==========
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # -- LEFT: Crossword Grid --
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(5)
        main_layout.addWidget(self.left_widget, stretch=3)

        # Top info area (left side)
        self.info_label = QLabel("", self)
        self.info_label.setFont(QFont("Arial", 14))
        self.info_label.setFixedHeight(30)
        self.left_layout.addWidget(self.info_label)

        # Grid layout for the crossword
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)
        self.left_layout.addLayout(self.grid_layout, stretch=1)

        self.labels: List[List[ClickableCell]] = []
        for r in range(15):
            row_cells = []
            for c in range(15):
                lbl = ClickableCell(r, c, self)
                lbl.leftClicked.connect(self.on_cell_selected)
                self.grid_layout.addWidget(lbl, r, c)
                row_cells.append(lbl)
            self.labels.append(row_cells)

        for i in range(15):
            self.grid_layout.setRowStretch(i, 1)
            self.grid_layout.setColumnStretch(i, 1)

        # -- RIGHT: Side Panel with 3 sections --
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(5, 5, 5, 5)
        self.right_layout.setSpacing(10)
        main_layout.addWidget(self.right_widget, stretch=2)

        # (1) Possible letters
        self.letters_box = QGroupBox("Possible Letters")
        # We'll use a 3-column grid layout for these buttons
        self.letters_grid = QGridLayout()
        self.letters_box.setLayout(self.letters_grid)
        self.right_layout.addWidget(self.letters_box)

        # (2) Across word possibilities
        self.across_box = QGroupBox("Across Word Possibilities")
        self.across_grid = QGridLayout()
        self.across_box.setLayout(self.across_grid)
        self.right_layout.addWidget(self.across_box)

        # (3) Down word possibilities
        self.down_box = QGroupBox("Down Word Possibilities")
        self.down_grid = QGridLayout()
        self.down_box.setLayout(self.down_grid)
        self.right_layout.addWidget(self.down_box)

        # Add "stretch" at bottom to push content up
        self.right_layout.addStretch()

        # Render the first crossword
        self.update_grid(self.current_index)
        self.update_side_panel(None)  # no cell selected initially

    ########################
    #   Grid Rendering
    ########################

    def update_info_label(self):
        if not self.scored_crosswords:
            self.info_label.setText("No crosswords left after filtering.")
            return

        rank = self.current_index + 1
        total = len(self.scored_crosswords)
        cw, sc = self.scored_crosswords[self.current_index]
        word_count = len(torus.grid.get_words_in_filled_grid(cw))

        self.info_label.setText(
            f"Rank {rank}/{total} — Score: {sc:.2f} — Words: {word_count}"
        )

    def update_grid(self, index: int):
        """
        Renders the crossword at scored_crosswords[index].
        Applies coloring for locked cells (green) and forced cells (blue).
        """
        if not self.scored_crosswords:
            # Nothing to show, clear
            for r in range(15):
                for c in range(15):
                    lbl = self.labels[r][c]
                    lbl.setText("")
                    p = lbl.palette()
                    p.setColor(QPalette.Window, QColor(255, 255, 255))
                    lbl.setPalette(p)
            self.update_info_label()
            return

        cw, _ = self.scored_crosswords[index]
        self.update_info_label()

        for r in range(15):
            row_str = cw[r]
            for c in range(15):
                ch = row_str[c]
                lbl = self.labels[r][c]

                # Default white background
                p = lbl.palette()
                p.setColor(QPalette.Window, QColor(255, 255, 255))
                lbl.setAutoFillBackground(True)
                lbl.setPalette(p)
                lbl.setStyleSheet("color: black;")

                if ch == "█":
                    lbl.setText("")
                    p.setColor(QPalette.Window, QColor(0, 0, 0))
                    lbl.setPalette(p)
                else:
                    lbl.setText(ch)
                    # If locked
                    if (r, c) in self.locked_cells:
                        p.setColor(QPalette.Window, QColor(144, 238, 144))  # green
                        lbl.setPalette(p)
                    else:
                        # If forced (common across filtered set) => blue
                        forced_ch = self.filtered_common_cells[r][c]
                        if forced_ch == ch:
                            p.setColor(QPalette.Window, QColor(173, 216, 230))  # blue
                            lbl.setPalette(p)

    ########################
    #   Side Panel
    ########################

    def update_side_panel(self, selected_cell):
        """
        Updates the side panel for the selected cell:
         (1) Possible letters (3-column grid)
         (2) Possible across words (3-column grid)
         (3) Possible down words (3-column grid)

        AFTER 26 items, we show a '...' button to indicate more remain.
        """
        self._clear_grid_layout(self.letters_grid)
        self._clear_grid_layout(self.across_grid)
        self._clear_grid_layout(self.down_grid)

        if not self.scored_crosswords or selected_cell is None:
            return

        r, c = selected_cell
        current_cw, _ = self.scored_crosswords[self.current_index]
        if current_cw[r][c] == "█":
            # No side panel updates if it's a black cell
            return

        all_filtered_grids = [grid for (grid, _) in self.scored_crosswords]

        # 1) Possible letters
        possible_letters = sorted(
            get_possible_letters_for_cell(all_filtered_grids, r, c)
        )
        # Truncate after 26
        truncated_letters = possible_letters[:26]
        truncated = len(possible_letters) > 26

        row_i, col_i = 0, 0
        for letter in truncated_letters:
            btn = QPushButton(letter)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.clicked.connect(lambda _, let=letter: self.toggle_cell_fix(r, c, let))

            self.letters_grid.addWidget(btn, row_i, col_i)
            col_i += 1
            if col_i >= 3:
                col_i = 0
                row_i += 1

        if truncated:
            # Add a "..." button
            more_btn = QPushButton("...")
            more_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            # No real action; purely visual
            self.letters_grid.addWidget(more_btn, row_i, col_i)

        # 2) Across possibilities
        start_c, end_c = get_across_word_indices(current_cw, r, c)
        across_len = end_c - start_c + 1
        if across_len > 1:
            across_set = set()
            for grid in all_filtered_grids:
                word = extract_word_from_grid(grid, r, start_c, r, end_c, "across")
                across_set.add(word)

            all_across_words = sorted(across_set)
            truncated_across = all_across_words[:26]
            truncated_flag = len(all_across_words) > 26

            row_i, col_i = 0, 0
            for w in truncated_across:
                btn = QPushButton(w)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                btn.clicked.connect(
                    lambda _, word=w: self.toggle_across_fix(r, start_c, r, end_c, word)
                )
                self.across_grid.addWidget(btn, row_i, col_i)
                col_i += 1
                if col_i >= 3:
                    col_i = 0
                    row_i += 1

            if truncated_flag:
                more_btn = QPushButton("...")
                more_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                self.across_grid.addWidget(more_btn, row_i, col_i)

        # 3) Down possibilities
        start_r, end_r = get_down_word_indices(current_cw, r, c)
        down_len = end_r - start_r + 1
        if down_len > 1:
            down_set = set()
            for grid in all_filtered_grids:
                word = extract_word_from_grid(grid, start_r, c, end_r, c, "down")
                down_set.add(word)

            all_down_words = sorted(down_set)
            truncated_down = all_down_words[:26]
            truncated_flag = len(all_down_words) > 26

            row_i, col_i = 0, 0
            for w in truncated_down:
                btn = QPushButton(w)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                btn.clicked.connect(
                    lambda _, word=w: self.toggle_down_fix(start_r, c, end_r, c, word)
                )
                self.down_grid.addWidget(btn, row_i, col_i)
                col_i += 1
                if col_i >= 3:
                    col_i = 0
                    row_i += 1

            if truncated_flag:
                more_btn = QPushButton("...")
                more_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                self.down_grid.addWidget(more_btn, row_i, col_i)

    def _clear_grid_layout(self, layout: QGridLayout):
        """
        Remove all child widgets from the given QGridLayout.
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    ########################
    #   Selection & Fixing
    ########################

    def on_cell_selected(self, row: int, col: int):
        """
        Left-click on the grid => we select (row, col).
        Refresh the side panel.
        """
        self.selected_cell = (row, col)
        self.update_side_panel(self.selected_cell)

    def toggle_cell_fix(self, row: int, col: int, letter: str):
        """
        Clicking a letter in the "Possible Letters" area => toggle fix for (row,col) = letter.
        If locked to `letter` already, unlock it. Otherwise lock it.
        Then re-filter & re-render.
        """
        currently_locked = (row, col) in self.locked_cells and self.locked_cells[
            (row, col)
        ] == letter

        if currently_locked:
            del self.locked_cells[(row, col)]
        else:
            # If locked to a different letter, remove that first
            if (row, col) in self.locked_cells:
                del self.locked_cells[(row, col)]
            self.locked_cells[(row, col)] = letter

        self._refilter_and_update()

    def toggle_across_fix(self, r1: int, c1: int, r2: int, c2: int, word: str):
        """
        Toggle fix for each cell in the across word [r1,c1..c2].
        """
        fully_locked = True
        length = c2 - c1 + 1
        for i in range(length):
            rr, cc = r1, c1 + i
            desired_char = word[i]
            if (rr, cc) not in self.locked_cells or self.locked_cells[
                (rr, cc)
            ] != desired_char:
                fully_locked = False
                break

        if fully_locked:
            # Unlock them all
            for i in range(length):
                rr, cc = r1, c1 + i
                if (rr, cc) in self.locked_cells:
                    del self.locked_cells[(rr, cc)]
        else:
            # Lock them all (override any existing lock on those cells)
            for i in range(length):
                rr, cc = r1, c1 + i
                self.locked_cells[(rr, cc)] = word[i]

        self._refilter_and_update()

    def toggle_down_fix(self, r1: int, c1: int, r2: int, c2: int, word: str):
        """
        Toggle fix for each cell in the down word [r1..r2, c1].
        """
        fully_locked = True
        length = r2 - r1 + 1
        for i in range(length):
            rr, cc = r1 + i, c1
            desired_char = word[i]
            if (rr, cc) not in self.locked_cells or self.locked_cells[
                (rr, cc)
            ] != desired_char:
                fully_locked = False
                break

        if fully_locked:
            # Unlock them
            for i in range(length):
                rr, cc = r1 + i, c1
                if (rr, cc) in self.locked_cells:
                    del self.locked_cells[(rr, cc)]
        else:
            # Lock them
            for i in range(length):
                rr, cc = r1 + i, c1
                self.locked_cells[(rr, cc)] = word[i]

        self._refilter_and_update()

    def _refilter_and_update(self):
        """
        Applies the 'locked_cells' constraints to the original crossword set,
        tries to remain on the same puzzle if possible,
        then re-renders the grid + side panel.
        """
        old_cw = None
        if self.scored_crosswords:
            old_cw, old_score = self.scored_crosswords[self.current_index]

        new_filtered = []
        for grid, score in self.original_scored_crosswords:
            match = True
            for (r, c), ch in self.locked_cells.items():
                if grid[r][c] != ch:
                    match = False
                    break
            if match:
                new_filtered.append((grid, score))

        # optional re-sort by score
        # new_filtered.sort(key=lambda x: x[1], reverse=True)

        self.scored_crosswords = new_filtered

        # Recompute filtered_common_cells
        filtered_grids = [cw for (cw, _) in self.scored_crosswords]
        self.filtered_common_cells = find_common_cells(filtered_grids)

        # Attempt to remain on old puzzle if it still exists
        new_index = 0
        for i, (g, s) in enumerate(self.scored_crosswords):
            if old_cw is not None and g == old_cw:
                new_index = i
                break

        self.current_index = new_index
        self.update_grid(self.current_index)

        # Rebuild the side panel for the currently selected cell (if any)
        if self.selected_cell:
            self.update_side_panel(self.selected_cell)

    ########################
    #   Key Navigation
    ########################

    def keyPressEvent(self, event):
        """
        Left/Right arrow to flip through puzzles.
        """
        if event.key() == Qt.Key_Right:
            if self.current_index < len(self.scored_crosswords) - 1:
                self.current_index += 1
                self.update_grid(self.current_index)
                if self.selected_cell:
                    self.update_side_panel(self.selected_cell)
        elif event.key() == Qt.Key_Left:
            if self.current_index > 0:
                self.current_index -= 1
                self.update_grid(self.current_index)
                if self.selected_cell:
                    self.update_side_panel(self.selected_cell)
        else:
            super().keyPressEvent(event)


#############################
#           main()
#############################


def main():
    app = QApplication(sys.argv)

    # Limit to first 300 crosswords
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        crossword_strs = json.load(f)
        # crossword_strs = crossword_strs[:300]
        crosswords = [torus.grid.str_to_grid(grid_str) for grid_str in crossword_strs]

    new_crosswords = []
    for cw in crosswords:
        # sol_template = torus.grid.get_grid_template_str_from_grid_str("".join(cw))
        # # Example template filtering ...
        # if sol_template in [
        #     "@@@██@@@█@@@@@@@@@...",  # etc
        # ]:
        #     continue
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

    scored_crosswords = torus.svm.grids_av_score(crosswords)
    scored_crosswords.sort(key=lambda x: x[1], reverse=True)

    scored_crosswords[:1000]
    viewer = CrosswordViewer(scored_crosswords)
    viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
