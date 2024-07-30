import pytest
from firepydaq.acquisition.acquisition import application
from PySide6.QtWidgets import QApplication, QMessageBox
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QGuiApplication
import time

from firepydaq.utilities.DAQUtils import COMports

@pytest.fixture
def set_up():
        if isinstance(PySide6.QtGui.qApp, type(None)):
            app = QApplication([])
        else:
            app = PySide6.QtGui.qApp

def test_click_acq(qtbot, monkeypatch):
    try:
        acq_calls = []
        main_app = application()
        monkeypatch.setattr(main_app, "acquisition_begins", lambda: acq_calls.append(1))
        qtbot.addWidget(main_app)
        qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
        assert acq_calls == [1]
    except Exception as e:
        print(e)
        pytest.fail(e, pytrace=True)
    assert True, "Clicks correct function"

def test_click_acq_unfilled(qtbot):

    main_app = application()
    qtbot.addWidget(main_app)
    main_app.show()
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
    message = main_app.findChild(QMessageBox)
    qtbot.addWidget(message)
    qtbot.mouseClick(message.Ok, Qt.LeftButton)
    assert True, "Clicks correct function"

def test_save_disabled(qtbot, monkeypatch):
    try:
        acq_calls = []
        main_app = application()
        qtbot.addWidget(main_app)
        button = main_app.save_button
        assert not button.isEnabled()
    except Exception as e:
        pytest.fail(e, pytrace=True)
    assert True, "Button is disabled"


# def test_click_acquisition(qtbot, mocker):
#     try:
#         main_app = application()

#         main_app.show()
#         qtbot.addWidget(main_app)
#         qtbot.mouseClick(main_app.save_button, Qt.LeftButton)
#     except Exception as e:
#         print(e)
#         pytest.fail(e, pytrace=True)
#     assert True, "Click didn't happen"
#     # return

# # DO NOT COMPILE APPLICATION FROM HERE UNTIL PYQT TESTING FRAMEWORK IS ESTABLISHED.

# # def test_app():
# #     app = QApplication(sys.argv)
# #     main_app = application()
# #     main_app.show()
# #     app.exec()
# #     time.sleep(1)
# #     # main_app.quit()
# #     assert True, "Application was not opened correctly"


# app = QApplication(sys.argv)
# main_app = application()
# main_app.show()
# app.exec()