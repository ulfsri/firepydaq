from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout,QLabel, QLineEdit, QPushButton, QFileDialog

class LoadSettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.file_name = ""
        layout = QVBoxLayout()
        self.setWindowTitle("Loading Settings")

        self.sec_label = QLabel("Select a File (.json):")
        layout.addWidget(self.sec_label)
        folder_layout = QHBoxLayout()
        self.folder_name = QLineEdit()
        self.folder_button = QPushButton("Select")
        self.folder_button.clicked.connect(self.set_file)
        folder_layout.addWidget(self.folder_name)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        self.ok_button = QPushButton("Done")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.save_name)
        self.cancel_button.clicked.connect(self.cancel_name)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def set_file(self):
        self.file_name = QFileDialog.getOpenFileName(self, 'Select a File', None, "JSON files (*.json)")
        print(self.file_name[0])
        self.folder_name.setText(self.file_name[0])
        self.file_name = self.file_name[0]

    def save_name(self):
        self.accept()

    def cancel_name(self):
        self.reject()