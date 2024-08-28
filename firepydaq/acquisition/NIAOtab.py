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

from PySide6.QtWidgets import (QWidget, QGridLayout,
                               QLabel, QLineEdit, QPushButton)
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class NIAOtab(QWidget):
    """Analog Output Manager object"""
    def __init__(self, parent, aolabelmap) -> None:
        self._makeinit(parent, aolabelmap)

    def _makeinit(self, parent, aolabelmap):
        self.parent = parent
        self.aolabelmap = aolabelmap
        self.aocontent = self.CreateAOTab()
        self.parent.input_tab_widget.addTab(self.aocontent, "AO Manager")

    def CreateAOTab(self):
        """Method to make NI AO manager tab created based
        on NI config file.

        Creates a QLabel and a QLineEdit
        for each `AO` label in the config file.

        A `setbtn` is created that connects with `GetAOVals()`
        """
        reg_ex_1 = QRegularExpression("[0-9]+.?[0-9]{,2}")  # double
        self.ao_widget = QWidget()
        self.ao_layout = QGridLayout()

        ao_counter = 0
        for key, item in self.aolabelmap.items():
            setattr(self, key, QLabel(key + ":"))
            getattr(self, key).setMaximumWidth(100)

            setattr(self, key+'_AOvalue', QLineEdit())
            getattr(self, key+'_AOvalue').setMaximumWidth(100)
            getattr(self, key+'_AOvalue').setText("0")
            getattr(self, key+'_AOvalue').setValidator(QRegularExpressionValidator(reg_ex_1))  # noqa E501

            self.ao_layout.addWidget(getattr(self, key), ao_counter, 0)
            self.ao_layout.addWidget(getattr(self, key+'_AOvalue'), ao_counter, 1)  # noqa E501
            ao_counter += 1

        self.setbtn = QPushButton("Set AO values")
        self.setbtn.setMaximumWidth(100)
        self.setbtn.connect(self.GetAOVals)
        self.ao_layout.addWidget(self.setbtn, ao_counter, 1)
        self.ao_widget.setLayout(self.ao_layout)
        return self.ao_widget

    def GetAOVals(self):
        """Method to collect all AO input values

        Returns
        _______
            ao_map: dict
                Dictionary that maps the keys in AO Labels
                to the values of respective LineEdit inputs.
        """
        ao_map = {}
        for key, _ in self.aolabelmap.items():
            ao_map[key] = getattr(self, key+'_AOvalue').text()

        return ao_map
