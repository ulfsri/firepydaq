from PySide6.QtWidgets import QApplication
from firepydaq.utilities.NIConfig.NIConfigMaker import NIConfigMaker
import sys

app = QApplication(sys.argv)
main_app = NIConfigMaker()
main_app.show()

sys.exit(app.exec())