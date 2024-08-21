#########################################################################
# FIREpyDAQ - Facilitated Interface for Recording Experiemnts,
# a python-based Data Acquisition program.
# Copyright (C) 2024  Dushyant M. Chaudhari

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#########################################################################

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                               QHBoxLayout, QLineEdit,
                               QPushButton, QFileDialog)


class LoadSettingsDialog(QDialog):
    """A pyqt dialog box to
    load a `.json` configuration.
    """
    def __init__(self):
        super().__init__()
        self._makeinit()

    def _makeinit(self):
        self.file_name = ""
        layout = QVBoxLayout()
        self.setWindowTitle("Loading Settings")

        self.sec_label = QLabel("Select a File (.json):")
        layout.addWidget(self.sec_label)
        folder_layout = QHBoxLayout()
        self.folder_name = QLineEdit()
        self.folder_button = QPushButton("Select")
        self.folder_button.clicked.connect(self._set_file)
        folder_layout.addWidget(self.folder_name)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        self.ok_button = QPushButton("Done")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self._save_name)
        self.cancel_button.clicked.connect(self._cancel_name)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def _set_file(self):
        self.file_name = QFileDialog.getOpenFileName(self, 'Select a File', None, "JSON files (*.json)")  # noqa E501
        self.folder_name.setText(self.file_name[0])
        self.file_name = self.file_name[0]

    def _save_name(self):
        self.file_name = self.folder_name.text()
        self.accept()

    def _cancel_name(self):
        self.reject()
