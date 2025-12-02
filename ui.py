import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableView,
    QTextEdit,
    QMenuBar,
    QStatusBar
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Subtitle Downloader")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create input fields
        input_layout = QFormLayout()
        self.movie_name_input = QLineEdit()
        self.timestamp_input = QLineEdit()
        self.language_input = QLineEdit("en")
        input_layout.addRow("Movie Name:", self.movie_name_input)
        input_layout.addRow("Timestamp:", self.timestamp_input)
        input_layout.addRow("Language:", self.language_input)
        main_layout.addLayout(input_layout)

        # Create a search button
        self.search_button = QPushButton("Search")
        main_layout.addWidget(self.search_button)

        # Create a table for subtitle results
        self.results_table = QTableView()
        main_layout.addWidget(self.results_table)

        # Create a text area for subtitle content
        self.subtitle_content = QTextEdit()
        main_layout.addWidget(self.subtitle_content)

        # Create a save button
        self.save_button = QPushButton("Save as...")
        main_layout.addWidget(self.save_button)

        # Create a menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        self.settings_action = file_menu.addAction("Settings")

        # Create a status bar
        self.setStatusBar(QStatusBar(self))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
