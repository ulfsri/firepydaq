# RunAquisitionOnly

from firepydaq.acquisition.acquisition import application
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
main_app = application()
main_app.show()
app.exec()
