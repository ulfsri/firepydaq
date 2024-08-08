from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class RemoveDeviceDialog(QDialog):
    def __init__(self, dev_arr):
        super().__init__()
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
        self.ok_button.clicked.connect(self.save_name)
        self.cancel_button.clicked.connect(self.cancel_name)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def save_name(self):
        self.device_to_del = self.dev_edit.currentText()
        self.index_to_del = self.dev_edit.currentIndex()
        self.accept()
    
    def cancel_name(self):
        self.reject()
