##########################################################################
# FIREpyDAQ - Facilitated Interface for Recording Experiments,
# a python-package for Data Acquisition.
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
                               QLineEdit, QPushButton)


class DeviceNameDialog(QDialog):
    """A dialog box to add a device."""
    def __init__(self, string):

        super().__init__()
        self._makeinit(string)

    def _makeinit(self, string):
        self.device_name = ""
        layout = QVBoxLayout()
        self.setWindowTitle(string)

        self.label = QLabel("Enter Device Name:")
        layout.addWidget(self.label)
        self.dev_edit = QLineEdit()
        layout.addWidget(self.dev_edit)

        self.ok_button = QPushButton("Done")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self._save_name)
        self.cancel_button.clicked.connect(self._cancel_name)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def _save_name(self):
        """Method that saves the user input name for a device"""
        self.device_name = self.dev_edit.text()
        self.accept()
        return

    def _cancel_name(self):
        self.reject()
