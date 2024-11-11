import sys
import random
import requests
import time

from bs4 import BeautifulSoup
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox,
)

import torus
from config import (
    WORDS_CONSIDERED_JSON,
    WORDS_APPROVED_JSON,
    WOR_JSON,
    WORDS_OMITTED_JSON,
    ACTIVE_WORDS_JSON,
)

import enum


class Source(enum.Enum):
    in_consideration = 0
    active_grids = 1
    bad_words = 2
    good_words = 3


WORDS_SOURCE = Source.active_grids
WITHOUT_CLUES_ONLY = False
DELETE_ACTIVE = True


class WordSortingApp(QWidget):
    def __init__(self):
        super().__init__()

        self.source = WORDS_SOURCE
        self.without_clues_only = WITHOUT_CLUES_ONLY
        self.f_delete_active = DELETE_ACTIVE

        self.words_omitted = torus.json.load_json(WORDS_OMITTED_JSON)
        self.words_approved = torus.json.load_json(WORDS_APPROVED_JSON)
        self.words_seen = set(self.words_omitted + self.words_approved)

        if self.source == Source.active_grids:
            t = torus.json.load_json(ACTIVE_WORDS_JSON)
            t.sort(key=lambda x: len(x), reverse=True)
            torus.json.write_json(WORDS_CONSIDERED_JSON, t)
        elif self.source == Source.bad_words:
            t = torus.json.load_json("filter_words/assumed_bad.json")
            t.sort(key=lambda x: len(x), reverse=True)
            torus.json.write_json(WORDS_CONSIDERED_JSON, t)
        elif self.source == Source.good_words:
            torus.json.write_json(
                WORDS_CONSIDERED_JSON,
                torus.json.load_json("filter_words/assumed_good.json"),
            )

        self.words_considered = torus.json.load_json(WORDS_CONSIDERED_JSON)
        if self.f_delete_active:
            torus.json.write_json(ACTIVE_WORDS_JSON, [])

        self.total_words = len(self.words_considered)  # Total number of words
        self.num_printed = 6
        self.params = {"search_redirect": "True"}
        self.headers = {"User-Agent": "Mozilla/5.0"}

        self.word_index = 0
        self.initUI()
        self.process_next_word()

    def initUI(self):
        self.setWindowTitle("Word Sorting Application")

        # Set window size and background color
        self.resize(700, 500)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Progress label
        self.progress_label = QLabel("", self)
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setFont(QFont("Arial", 12))
        self.progress_label.setStyleSheet("color: #666666;")

        # Word label (now selectable)
        self.word_label = QLabel("", self)
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.word_label.setStyleSheet("color: #333333;")
        self.word_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.word_label.setToolTip("Select and copy this word")
        self.word_label.setCursor(Qt.IBeamCursor)

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        # Clues text box
        self.clues_text = QTextEdit(self)
        self.clues_text.setReadOnly(True)
        self.clues_text.setFont(QFont("Arial", 12))
        self.clues_text.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #cccccc; padding: 5px;"
        )

        # Buttons
        self.accept_button = QPushButton("Accept ✅", self)
        self.reject_button = QPushButton("Reject ❌", self)
        self.pass_button = QPushButton("Pass ⏭️", self)
        self.exit_button = QPushButton("Exit 🚪", self)

        self.accept_button.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;"
        )
        self.reject_button.setStyleSheet(
            "background-color: #f44336; color: white; padding: 10px; font-size: 14px;"
        )
        self.pass_button.setStyleSheet(
            "background-color: #2196F3; color: white; padding: 10px; font-size: 14px;"
        )
        self.exit_button.setStyleSheet(
            "background-color: #757575; color: white; padding: 10px; font-size: 14px;"
        )

        self.accept_button.clicked.connect(self.accept_word)
        self.reject_button.clicked.connect(self.reject_word)
        self.pass_button.clicked.connect(self.pass_word)
        self.exit_button.clicked.connect(self.exit_app)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.reject_button)
        button_layout.addWidget(self.pass_button)
        button_layout.addWidget(self.exit_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.word_label)
        main_layout.addWidget(line)
        main_layout.addWidget(self.clues_text)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.show()

    def process_next_word(self):
        if self.word_index >= self.total_words:
            QMessageBox.information(self, "Completed", "All words have been processed.")
            self.close()
            return

        # Update progress label
        current_word_number = self.word_index + 1  # Since index starts at 0
        self.progress_label.setText(f"Word {current_word_number} of {self.total_words}")

        word = self.words_considered[self.word_index]
        self.current_word = word

        if word in self.words_seen:
            torus.json.remove_from_json_list(WORDS_CONSIDERED_JSON, word)
            self.word_index += 1
            self.process_next_word()
            return

        self.word_label.setText(f"{word.upper()}")

        url = f"https://crosswordtracker.com/answer/{word.lower()}/"

        try:
            response = requests.get(url, headers=self.headers, params=self.params)
            code = response.status_code
        except:
            code = 1

        clues_text = ""
        if code != 200:
            # No clues found, make the clues text box pink
            self.clues_text.setStyleSheet(
                "background-color: #ffe6f2; border: 1px solid #ff80bf; padding: 5px;"
            )
            clues_text = f"No clues found for '{word}'."
        else:
            time.sleep(random.uniform(0.5, 2))
            if self.without_clues_only:
                self.word_index += 1
                self.process_next_word()
                return
            soup = BeautifulSoup(response.text, "lxml")
            clue_container = soup.find("h3", string="Referring crossword puzzle clues")
            clues = []
            if clue_container:
                clue_container = clue_container.find_next_sibling("div")
                clues = clue_container.find_all("li")
                clues_text = "\n".join(
                    [f"- {clue.get_text()}" for clue in clues[: self.num_printed]]
                )
                # Reset clues text box style
                self.clues_text.setStyleSheet(
                    "background-color: #ffffff; border: 1px solid #cccccc; padding: 5px;"
                )
            else:
                # No clues found, make the clues text box pink
                self.clues_text.setStyleSheet(
                    "background-color: #ffe6f2; border: 1px solid #ff80bf; padding: 5px;"
                )
                clues_text = f"No clues found for '{word}'."

        self.clues_text.setPlainText(clues_text)

    def accept_word(self):
        word = self.current_word
        torus.json.append_json(WORDS_APPROVED_JSON, word)
        torus.json.remove_from_json_list(WORDS_CONSIDERED_JSON, word)
        self.word_index += 1
        self.process_next_word()

    def reject_word(self):
        word = self.current_word
        torus.json.append_json(WORDS_OMITTED_JSON, word)
        torus.json.remove_from_json_list(WOR_JSON, word)
        torus.json.remove_from_json_list(WORDS_CONSIDERED_JSON, word)
        self.word_index += 1
        self.process_next_word()

    def pass_word(self):
        self.word_index += 1
        self.process_next_word()

    def exit_app(self):
        self.close()


if __name__ == "__main__":
    stuff = []
    if WORDS_SOURCE == Source.active_grids:
        stuff = torus.json.load_json(ACTIVE_WORDS_JSON)
    elif WORDS_SOURCE == Source.bad_words:
        stuff = torus.json.load_json("filter_words/assumed_bad.json")
    elif WORDS_SOURCE == Source.good_words:
        stuff = (torus.json.load_json("filter_words/assumed_good.json"),)
    elif WORDS_SOURCE == Source.in_consideration:
        stuff = torus.json.load_json(WORDS_CONSIDERED_JSON)

    if not stuff:
        print("No words to process.")
        exit()

    app = QApplication(sys.argv)
    ex = WordSortingApp()
    sys.exit(app.exec_())
