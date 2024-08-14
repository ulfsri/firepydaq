from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
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
            getattr(self, key+'_AOvalue').setValidator(QRegularExpressionValidator(reg_ex_1))

            self.ao_layout.addWidget(getattr(self, key), ao_counter, 0)
            self.ao_layout.addWidget(getattr(self, key+'_AOvalue'), ao_counter, 1)
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
        for key, item in self.aolabelmap.items():
            ao_map[key] = getattr(self, key+'_AOvalue').text()

        return ao_map
