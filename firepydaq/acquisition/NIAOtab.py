from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class NIAOtab(QWidget):
    def __init__(self, parent, aolabelmap) -> None:
        self.parent = parent
        self.aocontent = self.CreateAOTab(aolabelmap)
        self.parent.input_tab_widget.addTab(self.aocontent, "AO Manager")

    def CreateAOTab(self, aolabelmap):
        reg_ex_1 = QRegularExpression("[0-9]+.?[0-9]{,2}")  # double
        self.ao_widget = QWidget()
        self.ao_layout = QGridLayout()

        ao_counter = 0
        for key, item in aolabelmap.items():
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
        self.ao_layout.addWidget(self.setbtn, ao_counter, 1)
        self.ao_widget.setLayout(self.ao_layout)
        return self.ao_widget

