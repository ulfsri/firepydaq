from firepydaq.acquisition.acquisition import application
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction
import time


def Adddevice_tester_func(qtbot, monkeypatch,
                          dev_obname: str,
                          deviceTestname: str,
                          dev_connection_btn_name: str,
                          dev_remObj: str):
    time_out = 5
    main_app = application()
    qtbot.addWidget(main_app)
    message_box = None
    start_time = time.time()
    dev_connect = []

    def handle_AddDialog():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            message_box.hide()
            message_box.dev_edit.setText(deviceTestname)
            qtbot.mouseClick(message_box.ok_button, Qt.LeftButton)
            assert message_box.device_name == deviceTestname, False  # noqa: E501
            message_box.close()
        return

    QTimer.singleShot(2, handle_AddDialog)
    main_app.findChild(QAction, dev_obname).trigger()

    if "mfc" in dev_obname.lower():
        main_app.mfcs[deviceTestname].dil_rate_input.setText("0.1")
        assert main_app.mfcs[deviceTestname].get_type() == "mfc"
    elif "mfm" in dev_obname.lower():
        assert main_app.mfms[deviceTestname].get_type() == "mfm"
    elif "laser" in dev_obname.lower():
        assert main_app.lasers[deviceTestname].get_type() == "laser"
    monkeypatch.setattr(main_app.device_arr[deviceTestname], "establish_connection", lambda: dev_connect.append(1))  # noqa E501
    qtbot.mouseClick(getattr(main_app.device_arr[deviceTestname],dev_connection_btn_name), Qt.LeftButton)  # noqa E501

    while message_box is None and time.time() - start_time < time_out:
        continue
    assert dev_connect == [1], deviceTestname + "test failed."

    start_time = time.time()

    def handle_RemDialog():
        nonlocal message_box
        message_box = None
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            message_box.hide()
            qtbot.mouseClick(message_box.ok_button, Qt.LeftButton)
            assert message_box.device_to_del == deviceTestname, False  # noqa: E501
            message_box.close()

    QTimer.singleShot(2, handle_RemDialog)
    main_app.findChild(QAction, dev_remObj).trigger()

    if "mfc" in dev_obname.lower():
        assert main_app.mfcs == {}
    elif "mfm" in dev_obname.lower():
        assert main_app.mfms == {}
    elif "laser" in dev_obname.lower():
        assert main_app.lasers == {}

    assert True, "Device test failed"


def test_AddDevices(qtbot, monkeypatch):
    Adddevice_tester_func(qtbot, monkeypatch, "Add MFC", "TestMFC", "mfc_connection_btn", "Remove MFC")  # noqa E501
    Adddevice_tester_func(qtbot, monkeypatch, "Add Laser", "TestLaser", "laser_connection_btn", "Remove Laser")  # noqa E501
    Adddevice_tester_func(qtbot, monkeypatch, "Add MFM", "TestMFM", "mfm_connection_btn", "Remove MFM")  # noqa E501