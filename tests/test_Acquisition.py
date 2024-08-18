import pytest
from firepydaq.acquisition.acquisition import application
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Qt
import time
from firepydaq.api.EchoNIDAQTask import CreateDAQTask


def test_click_acq(qtbot, monkeypatch):
    try:
        acq_calls = []
        main_app = application()
        monkeypatch.setattr(main_app, "acquisition_begins", lambda: acq_calls.append(1))  # noqa: E501
        qtbot.addWidget(main_app)
        qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
        assert acq_calls == [1]
    except Exception as e:
        print(e)
        pytest.fail(e, pytrace=True)
    assert True, "Clicks incorrect function"


def test_click_acq_unfilled(qtbot):
    time_out = 5
    main_app = application()
    qtbot.addWidget(main_app)
    message_box = None
    start_time = time.time()

    def dialog_creation():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            message_box.hide()
            assert message_box.text() == "Unfilled fields encountered."
            message_box.close()

    QTimer.singleShot(10, dialog_creation)
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds. Dialog type: {type(message_box)}"  # noqa: E501


def test_acq_value_err(qtbot):
    time_out = 5
    main_app = application()
    qtbot.addWidget(main_app)
    message_box = None
    start_time = time.time()

    main_app.exp_input.setText("Experiment")
    main_app.name_input.setText("Anvii")
    main_app.test_input.setText("Test4")
    main_app.sample_rate_input.setText("Abcd")
    main_app.formulae_file = pytest.formulaepath
    main_app.formulae_file_edit.setText(pytest.formulaepath)
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = pytest.configpath
    main_app.config_file_edit.setText(pytest.configpath)

    def dialog_creation():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            message_box.hide()
            assert message_box.text() == "Invalid Sampling Rate"
            message_box.close()

    QTimer.singleShot(2, dialog_creation)
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds.\n"
    f"Dialog type: {type(message_box)}"


def test_save_disabled(qtbot):
    try:
        main_app = application()
        qtbot.addWidget(main_app)
        button = main_app.save_button
        assert not button.isEnabled()
    except Exception as e:
        pytest.fail(e, pytrace=True)
    assert True, "Button is not disabled"


def test_acq_name_err(qtbot):
    time_out = 5
    main_app = application()
    qtbot.addWidget(main_app)
    message_box = None
    start_time = time.time()

    main_app.exp_input.setText("Experiment")
    main_app.name_input.setText("Anvii***")
    main_app.test_input.setText("Test4")
    main_app.sample_rate_input.setText("Abcd")
    main_app.formulae_file = pytest.formulaepath
    main_app.formulae_file_edit.setText(pytest.formulaepath)
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = pytest.configpath
    main_app.config_file_edit.setText(pytest.configpath)

    def dialog_creation():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            message_box.hide()
            assert message_box.text() == "Names can only be alphanumeric or contain spaces."  # noqa: E501
            message_box.close()

    QTimer.singleShot(2, dialog_creation)
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds. Dialog type: {type(message_box)}"  # noqa: E501


def test_acq_expname_err(qtbot):
    time_out = 5
    main_app = application()
    qtbot.addWidget(main_app)
    message_box = None
    start_time = time.time()

    main_app.exp_input.setText("Experiment***")
    main_app.name_input.setText("Anvii")
    main_app.test_input.setText("test45")
    main_app.sample_rate_input.setText("Abcd")
    main_app.formulae_file = pytest.formulaepath
    main_app.formulae_file_edit.setText(pytest.formulaepath)
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = pytest.configpath
    main_app.config_file_edit.setText(pytest.configpath)

    def dialog_creation():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            message_box.hide()
            assert message_box.text() == "Names can only be alphanumeric or contain spaces."  # noqa: E501
            message_box.close()

    QTimer.singleShot(2, dialog_creation)
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds. Dialog type: {type(message_box)}"  # noqa: E501


def test_save_enabled(qtbot, monkeypatch):
    main_app = application()
    qtbot.addWidget(main_app)

    main_app.exp_input.setText("Experiment")
    main_app.name_input.setText("Anvii")
    main_app.test_input.setText("test45")
    main_app.sample_rate_input.setText("10")
    main_app.formulae_file = ""
    main_app.formulae_file_edit.setText("")
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = pytest.configpath
    main_app.config_file_edit.setText(pytest.configpath)
    button = main_app.save_button

    def my_config(cls, path):
        print(path)
        cls.ai_counter = 1
        cls.ao_counter = 0
        return

    def my_StartAIContinuousTask(cls, x, y):
        print(x, y)
        return

    def my_inform(cls, s):
        print(s)
        return

    def myinit_dataArray(cls):
        return

    def my_runpydaq(cls):
        return

    monkeypatch.setattr(application, "inform_user", my_inform)
    monkeypatch.setattr(CreateDAQTask, "CreateFromConfig", my_config)
    monkeypatch.setattr(CreateDAQTask, "StartAIContinuousTask", my_StartAIContinuousTask)  # noqa: E501
    monkeypatch.setattr(application, "initiate_dataArrays", myinit_dataArray)
    monkeypatch.setattr(application, "runpyDAQ", my_runpydaq)
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)
    assert button.isEnabled(), "Save button not enabled."
