import json
import os
import keyring
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")

        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()
        self.api_key_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.form_layout.addRow("API Key:", self.api_key_input)
        self.form_layout.addRow("Username (optional):", self.username_input)
        self.form_layout.addRow("Password (optional):", self.password_input)

        self.layout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

    def get_settings(self):
        return {
            "api_key": self.api_key_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
        }

    def set_settings(self, settings):
        self.api_key_input.setText(settings.get("api_key", ""))
        self.username_input.setText(settings.get("username", ""))
        self.password_input.setText(settings.get("password", ""))


class Settings:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.service_name = "SubtitleDownloader"
        self.settings = self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                settings = json.load(f)
                if "username" in settings:
                    password = keyring.get_password(self.service_name, settings["username"])
                    if password:
                        settings["password"] = password
                return settings
        return {}

    def save(self, settings):
        settings_to_save = settings.copy()
        username = settings_to_save.get("username")
        password = settings_to_save.get("password")

        if username and password:
            keyring.set_password(self.service_name, username, password)
            # Don't save password in the json file
            if "password" in settings_to_save:
                del settings_to_save["password"]

        with open(self.filename, "w") as f:
            json.dump(settings_to_save, f, indent=4)
        self.settings = self.load()

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
