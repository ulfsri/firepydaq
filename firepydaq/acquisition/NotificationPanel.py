from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QColor, QTextCursor
import time


class NotificationPanel(QTextEdit):
    """A QTextEdit object that serves as a notification panel
    for the interface.

    Attributes
    ----------
    message_types: dict
        {
            "info": QColor("darkcyan"),
            "warning": QColor("orange"),
            "error": QColor("red"),
            "success": QColor("green"),
            "default": QColor("gray"),
            "observation": QColor("darkgreen")
        }

    """
    def __init__(self, parent=None):
        super(NotificationPanel, self).__init__(parent)
        self._makeinit()

    def _makeinit(self):
        self.setWindowTitle("Testing tite")
        self.setReadOnly(True)
        self.message_types = {
            "info": QColor("darkcyan"),
            "warning": QColor("orange"),
            "error": QColor("red"),
            "success": QColor("green"),
            "default": QColor("gray"),
            "observation": QColor("darkgreen")
        }
        self.setPlaceholderText("Welcome User!")

    def add_message(self, message_type, text):
        """ Method to add message to the top of the notification panel

        Parameters
        ---------
            message_type: str
                Message type to be posted. Each type has different colors.
                See `message_types`
            text: str
                Message to be posted.
        """
        str_time = time.strftime("%X")
        str_time = "[" + str_time + "]: "

        self.color = self.message_types.get(message_type, QColor("black"))
        formatted_text = f"<font color='{self.color.name()}'>{str_time} {text}</font><br>"  # noqa E501

        # move cursor to the top of the document block
        # Ensure accidental clicking inside the box doesn't
        # affect text update
        cursor = QTextCursor(
            self.document().findBlockByLineNumber(0)
        )
        self.setTextCursor(cursor)
        self.insertHtml(formatted_text)
