import pytest
from firepydaq.acquisition.acquisition import application
from PySide6.QtWidgets import QApplication, QMessageBox
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QGuiApplication
import time
from firepydaq.api.CreateNIDAQTask import CreateDAQTask

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
            assert message_box.text() == "Unfilled fields encountered"
            message_box.close()
    
    QTimer.singleShot(2, dialog_creation) 
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton) 
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds. Dialog type: {type(message_box)}"

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
    main_app.formulae_file = r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv"
    main_app.formulae_file_edit.setText(r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv")
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv"
    main_app.config_file_edit.setText( r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv")


    def dialog_creation():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            assert message_box.text() == "Invalid Sampling Rate"
            message_box.close()
    
    QTimer.singleShot(2, dialog_creation) 
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton) 
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds. Dialog type: {type(message_box)}"


def test_save_disabled(qtbot, monkeypatch):
    try:
        acq_calls = []
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
    main_app.formulae_file = r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv"
    main_app.formulae_file_edit.setText(r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv")
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv"
    main_app.config_file_edit.setText( r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv")

    def dialog_creation():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            assert message_box.text() == "Names can only be alphanumeric or contain spaces."
            message_box.close()
    
    QTimer.singleShot(2, dialog_creation) 
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton) 
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds. Dialog type: {type(message_box)}"


def test_save_disabled(qtbot, monkeypatch):
    try:
        acq_calls = []
        main_app = application()
        qtbot.addWidget(main_app)
        button = main_app.save_button
        assert not button.isEnabled()
    except Exception as e:
        pytest.fail(e, pytrace=True)
    assert True, "Button is not disabled"


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
    main_app.formulae_file = r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv"
    main_app.formulae_file_edit.setText(r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv")
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv"
    main_app.config_file_edit.setText( r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv")

    def dialog_creation():
        nonlocal message_box
        while message_box is None and time.time() - start_time < time_out:
            message_box = QApplication.activeModalWidget()
        if message_box is not None:
            assert message_box.text() == "Names can only be alphanumeric or contain spaces."
            message_box.close()
    
    QTimer.singleShot(2, dialog_creation) 
    qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton) 
    while message_box is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        message_box, QMessageBox
    ), f"No message box was created after {time_out} seconds. Dialog type: {type(message_box)}"



def test_save_enabled(qtbot, monkeypatch):
    main_app = application()
    qtbot.addWidget(main_app)
    message_box = None
    main_app.exp_input.setText("Experiment")
    main_app.name_input.setText("Anvii")
    main_app.test_input.setText("test45")
    main_app.sample_rate_input.setText("34")
    main_app.formulae_file = r"C:\Users\MishraAnvii\Documents\GitHub\firepydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv"
    main_app.formulae_file_edit.setText(r"C:\Users\MishraAnvii\Documents\GitHub\firepydaq\tests\Example_Config_Formulae\Processing_formulaeTesting.csv")
    main_app.test_type_input.setCurrentText("Experiment")
    main_app.config_file = r"C:\Users\MishraAnvii\Documents\GitHub\firepydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv"
    main_app.config_file_edit.setText( r"C:\Users\MishraAnvii\Documents\GitHub\firepydaq\tests\Example_Config_Formulae\20240329_1354_Testing.csv")  
    button = main_app.save_button
    def my_init():
        CreateDAQTask.a = 4

    try:
        acq_calls = []
        monkeypatch.setattr(CreateDAQTask , name= "__init__", value = my_init())
        print(acq_calls)
        qtbot.mouseClick(main_app.acquisition_button, Qt.LeftButton)   
        print("here")
        assert button.isEnabled()
    except Exception as e:
        print("there")
        assert button.isEnabled()
        pass
    assert True, "Button is disabled"
