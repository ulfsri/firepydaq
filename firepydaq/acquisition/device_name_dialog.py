from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

import webbrowser
from .device import alicat_mfc 

class DeviceNameDialog(QDialog):
    def __init__(self, string, mode):

        super().__init__()
        self.mode = mode
        self.device_name = ""
        layout = QVBoxLayout()
        self.setWindowTitle(string)

        if self.mode == "Light":
            f = open("popup_light.css", "r")
        else:
            f = open("popup_dark.css", "r")
        str = f.read()
        self.setStyleSheet(str)
        f.close()

        
        self.label = QLabel("Enter Device Name:")
        layout.addWidget(self.label)
        self.dev_edit = QLineEdit()
        layout.addWidget(self.dev_edit)

        self.ok_button = QPushButton("Done")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.save_name)
        self.cancel_button.clicked.connect(self.cancel_name)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    
    def save_name(self):
        self.device_name = self.dev_edit.text()
        self.accept()
    def cancel_name(self):
        self.reject()
