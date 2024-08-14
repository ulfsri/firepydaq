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

    def _cancel_name(self):
        self.reject()
