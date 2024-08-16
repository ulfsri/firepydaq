import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                               QVBoxLayout, QWidget, QPushButton,
                               QLineEdit, QMenu, QFileDialog,
                               QHBoxLayout)
from PySide6.QtGui import QColor, QAction, QTextCursor
from PySide6.QtCore import Qt
import time


class NotificationPanel(QTextEdit):
    def __init__(self, parent=None):
        super(NotificationPanel, self).__init__(parent)
        self.setWindowTitle("Testing tite")
        self.setReadOnly(True)
        self.message_types = {
            "info": QColor("blue"),
            "warning": QColor("orange"),
            "error": QColor("red"),
            "success": QColor("green"),
            "default": QColor("gray"),
            "observation": QColor("darkgreen")
        }
        self.setPlaceholderText("Welcome User!")

    def add_message(self, message_type, text):
        str_time = time.strftime("%X")
        str_time = "[" + str_time + "]: "

        color = self.message_types.get(message_type, QColor("black"))
        formatted_text = f"<font color='{color.name()}'>{str_time} {text}</font><br>"  # noqa E501

        # move cursor to the top of the document block
        # Ensure accidental clicking inside the box doesn't
        # affect text update
        cursor = QTextCursor(
            self.document().findBlockByLineNumber(0)
        )
        self.setTextCursor(cursor)
        self.insertHtml(formatted_text)


# Unused. Can be used for debug
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Notification Panel Example")
        self.setGeometry(100, 100, 600, 400)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Initialize NotificationPanel
        self.panel = NotificationPanel()
        self.panel.setMaximumHeight(375)
        self.panel.setFixedWidth(250)
        self.panel.setAlignment(Qt.AlignRight)
        self.panel.setAlignment(Qt.AlignTop)
        layout.addWidget(self.panel)

        # Create input area
        self.log_area = QHBoxLayout()
        layout.addLayout(self.log_area)
        self.log_obs_txt = QLineEdit()
        self.log_obs_txt.setPlaceholderText("Write observations here")
        self.log_area.addWidget(self.log_obs_txt)
        self.submit_button = QPushButton("Add Event")
        self.submit_button.clicked.connect(self.notify_log)
        self.log_area.addWidget(self.submit_button)

        self.menu = QMenu()
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.panel.clear)
        self.menu.addAction(clear_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_notifs)
        self.menu.addAction(save_action)

        # Create dropdown menu for clear and save actions
        self.dropdown_button = QPushButton("Options")
        self.dropdown_button.setMaximumWidth(100)
        self.dropdown_button.setMaximumHeight(24)
        self.dropdown_button.setMenu(self.menu)
        layout.insertWidget(0, self.dropdown_button, alignment=Qt.AlignRight)

    def notify_log(self):
        text = self.log_obs_txt.text().strip()
        if text:
            # Will not post an empty message
            self.notify(text, type="observation")
            self.log_obs_txt.clear()

    def notify(self, text="", type="default"):
        self.panel.add_message(type, text)

    def save_notifs(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")  # noqa E501
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.panel.toPlainText())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
