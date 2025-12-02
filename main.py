import sys
import re
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from ui import MainWindow
from settings import Settings, SettingsDialog
from opensubtitles import OpenSubtitles, OpenSubtitlesError

class SubtitleApp(MainWindow):
    def __init__(self):
        super().__init__()

        self.settings = Settings()
        self.opensubtitles = None
        self.setup_connections()
        self.init_opensubtitles()

        self.results_model = QStandardItemModel()
        self.results_model.setHorizontalHeaderLabels(["Name", "Uploader", "Rating"])
        self.results_table.setModel(self.results_model)

    def setup_connections(self):
        self.search_button.clicked.connect(self.search_subtitles)
        self.settings_action.triggered.connect(self.open_settings)
        self.save_button.clicked.connect(self.save_subtitle)
        self.results_table.selectionModel().selectionChanged.connect(self.subtitle_selected)

    def init_opensubtitles(self):
        api_key = self.settings.get("api_key")
        if api_key:
            self.opensubtitles = OpenSubtitles(
                api_key,
                self.settings.get("username"),
                self.settings.get("password")
            )
        else:
            self.show_error("API key not set. Please set it in the settings.")

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.set_settings(self.settings.settings)
        if dialog.exec():
            self.settings.save(dialog.get_settings())
            self.init_opensubtitles()

    def search_subtitles(self):
        if not self.opensubtitles:
            self.show_error("OpenSubtitles API not initialized. Please set the API key.")
            return

        movie_name = self.movie_name_input.text()
        language = self.language_input.text()

        if not movie_name:
            self.show_error("Please enter a movie name.")
            return

        try:
            subtitles = self.opensubtitles.search_subtitles(movie_name, language)
        except OpenSubtitlesError as e:
            self.show_error(str(e))
            return

        self.results_model.setRowCount(0)

        if subtitles:
            for sub in subtitles:
                attributes = sub.get('attributes', {})
                files = attributes.get('files', [])
                if files:
                    file_info = files[0] # Taking the first file
                    self.results_model.appendRow([
                        QStandardItem(attributes.get('release', 'N/A')),
                        QStandardItem(attributes.get('uploader', {}).get('name', 'N/A')),
                        QStandardItem(str(attributes.get('ratings', 'N/A'))),
                    ])
                    # Store file_id in the item
                    self.results_model.item(self.results_model.rowCount() - 1).setData(file_info.get('file_id'))
        else:
            self.show_info("No subtitles found.")

    def subtitle_selected(self, selected, deselected):
        if not self.opensubtitles:
            return

        if selected.indexes():
            index = selected.indexes()[0]
            item = self.results_model.itemFromIndex(index)
            file_id = item.data()

            if file_id:
                try:
                    content = self.opensubtitles.download_subtitle(file_id)
                    if content:
                        self.subtitle_content.setText(content)
                        self.scroll_to_timestamp()
                    else:
                        self.show_error("Failed to download subtitle.")
                except OpenSubtitlesError as e:
                    self.show_error(str(e))

    def scroll_to_timestamp(self):
        timestamp_str = self.timestamp_input.text()
        if not timestamp_str:
            return

        total_seconds = self.parse_timestamp(timestamp_str)
        if total_seconds is None:
            self.show_error("Invalid timestamp format.")
            return

        subtitle_content = self.subtitle_content.toPlainText()
        lines = subtitle_content.split('\n')

        for i, line in enumerate(lines):
            if "-->" in line:
                start_time_str, end_time_str = line.split("-->")
                start_seconds = self.srt_time_to_seconds(start_time_str.strip())
                end_seconds = self.srt_time_to_seconds(end_time_str.strip())

                if start_seconds <= total_seconds <= end_seconds:
                    # Move cursor to the start of this subtitle block
                    block_start_line = i - 1
                    cursor = self.subtitle_content.textCursor()
                    cursor.movePosition(cursor.MoveOperation.Start)
                    for _ in range(block_start_line):
                        cursor.movePosition(cursor.MoveOperation.Down)
                    self.subtitle_content.setTextCursor(cursor)
                    self.subtitle_content.ensureCursorVisible()
                    break

    def srt_time_to_seconds(self, time_str):
        parts = time_str.replace(',', ':').split(':')
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]) + int(parts[3]) / 1000

    def parse_timestamp(self, timestamp_str):
        total_seconds = 0

        # Format: 1h 5m 4s
        match = re.match(r'(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s\s*)?$', timestamp_str)
        if match:
            h, m, s = match.groups()
            if h: total_seconds += int(h) * 3600
            if m: total_seconds += int(m) * 60
            if s: total_seconds += int(s)
            return total_seconds

        # Format: 5:04 or 1:05:04
        if ':' in timestamp_str:
            parts = timestamp_str.split(':')
            if len(parts) == 2:
                total_seconds = int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return total_seconds

        return None


    def save_subtitle(self):
        content = self.subtitle_content.toPlainText()
        if not content:
            self.show_error("No subtitle content to save.")
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "Save Subtitle", "", "SubRip files (*.srt)")
        if filepath:
            with open(filepath, "w") as f:
                f.write(content)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message):
        QMessageBox.information(self, "Info", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SubtitleApp()
    window.show()
    sys.exit(app.exec())
