from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton,
                               QFileDialog)


class SaveSettingsDialog(QDialog):
    """A pyqt dialog box to save the configuration
    """
    def __init__(self, string):
        super().__init__()

        self._makeinit(string)

    def _makeinit(self, string):
        self.file_name = ""
        layout = QVBoxLayout()
        self.setWindowTitle(string)

        self.label = QLabel("Enter File Name:")
        layout.addWidget(self.label)
        self.file_name_edit = QLineEdit()
        layout.addWidget(self.file_name_edit)

        self.sec_label = QLabel("Select Folder:")
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
        self.folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.folder_name.setText(self.folder_path)

    def _save_name(self):
        self.file_name = self.file_name_edit.text()
        self.file_path = self.folder_path + '/' + self.file_name
        self.accept()

    def _cancel_name(self):
        self.reject()
