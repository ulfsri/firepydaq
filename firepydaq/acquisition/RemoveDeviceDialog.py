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
                               QComboBox, QPushButton)


class RemoveDeviceDialog(QDialog):
    """PyQT dialog box to remove an existing device"""
    def __init__(self, dev_arr):
        super().__init__()
        self._makeinit(dev_arr)

    def _makeinit(self, dev_arr):
        self.device_to_del = ""
        layout = QVBoxLayout()
        self.setWindowTitle("Remove Device")

        self.label = QLabel("Select Device to Remove:")
        layout.addWidget(self.label)
        self.dev_edit = QComboBox()
        layout.addWidget(self.dev_edit)

        for dev in dev_arr.keys():
            self.dev_edit.addItem(dev)

        self.ok_button = QPushButton("Done")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self._remove_name)
        self.cancel_button.clicked.connect(self._cancel_name)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def _remove_name(self):
        self.device_to_del = self.dev_edit.currentText()
        self.index_to_del = self.dev_edit.currentIndex()
        self.accept()

    def _cancel_name(self):
        self.reject()
