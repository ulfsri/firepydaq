from PySide6.QtWidgets import (QWidget, QGridLayout, QLabel,
                               QLineEdit, QComboBox, QHBoxLayout,
                               QPushButton)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from ..utilities.DAQUtils import COMports, AlicatGases

# APIs
from ..api.EchoAlicat import EchoController
from ..api.EchoThorLabsCLD101X import EchoThor

# Communication related
import asyncio
import time


class thorlabs_laser(QWidget):
    """User-added ThorlabsCLD101X Controller

    Attributes
    ----------
        reg_ex_1: QRegularExpression
            Only accept float values
        type: str
            Value is "laser"
        parent: Object
            Defines parent class
        settings: dict
            Stores settings for the controller

    """
    reg_ex_1 = QRegularExpression(r"[0-9]*\.[0-9]{0,4}")  # double

    def __init__(self, parent, str_name):
        super().__init__()
        self._makelaser(parent, str_name)

    def _makelaser(self, parent, str_name):
        self.type = "laser"
        self.dev_id = str_name
        self.parent = parent
        self.settings = {}
        self.content = self.create_thorlabs_laser_content()
        self.parent.device_tab_widget.addTab(self.content, self.dev_id)

    def create_thorlabs_laser_content(self):
        """Method that creates laser controller contents

        Fields
        ----------------------
        - comport_input: QComboBox
            Dropdown of list of available COMPorts
        - p_input: QLineEdit
            Value for proportional component
            of the PID controller for ThorlabsCLD101X
        - i_input: QLineEdit
            Value for integral component
            of the PID controller for ThorlabsCLD101X
        - d_input: QLineEdit
            Value for derivative component
            of the PID controller for ThorlabsCLD101X
        - osc_input: QLineEdit
            Value for Oscillation period in seconds
            of the PID controller for ThorlabsCLD101X
        - tec_input: QLineEdit
            Value in Celsius that will be used
            to set TEC.
        - tec_button: QPushButton
            Calls set_tec()
        - laser_input: QLineEdit
            Value in mA that will be used
            to set the laser current.
        - laser_button: QPushButton
            Calls set_laser()
        - pid_btn: QPushButton
            Calls set_pID()
        - laser_connection_btn: QPushButton
            Calls establish_connection()
        """
        # Adds Layout
        self.device_widget = QWidget()
        self.device_layout = QGridLayout()

        # Adds COMPORT input field
        self.comport_label = QLabel("Select COMPORT:")
        self.comport_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.comport_label, 0, 0)

        self.comport_input = QComboBox()
        for comport in COMports:
            self.comport_input.addItem(comport)
        self.comport_input.setMaximumWidth(200)
        self.comport = self.comport_input.currentText()
        self.device_layout.addWidget(self.comport_input, 0, 1)

        # Adds P input field
        self.p_label = QLabel("Enter P value:")
        self.device_layout.addWidget(self.p_label, 1, 0)
        self.p_label.setMaximumWidth(200)

        self.p_input = QLineEdit()
        self.p_input.setMaximumWidth(200)
        self.p_input.setPlaceholderText("8.0")
        self.p_input.setValidator(QRegularExpressionValidator(self.reg_ex_1))  # noqa: E501
        self.device_layout.addWidget(self.p_input, 1, 1)

        # Adds I input field
        self.i_label = QLabel("Enter I value:")
        self.device_layout.addWidget(self.i_label, 2, 0)
        self.i_label.setMaximumWidth(200)

        self.i_input = QLineEdit()
        self.i_input.setPlaceholderText("3.7")
        self.i_input.setMaximumWidth(200)
        self.i_input.setValidator(QRegularExpressionValidator(self.reg_ex_1))
        self.device_layout.addWidget(self.i_input, 2, 1)

        # Adds D input field
        self.d_label = QLabel("Enter D value:")
        self.device_layout.addWidget(self.d_label, 3, 0)
        self.d_label.setMaximumWidth(200)

        self.d_input = QLineEdit()
        self.d_input.setPlaceholderText("3.2")
        self.d_input.setValidator(QRegularExpressionValidator(self.reg_ex_1))
        self.d_input.setMaximumWidth(200)
        self.device_layout.addWidget(self.d_input, 3, 1)

        # Adds Osc Period input field
        self.osc_label = QLabel("Enter Osc period (s):")
        self.device_layout.addWidget(self.osc_label, 4, 0)
        self.osc_label.setMaximumWidth(200)

        self.osc_input = QLineEdit()
        self.osc_input.setPlaceholderText("2")
        self.osc_input.setMaximumWidth(200)
        self.osc_input.setValidator(QRegularExpressionValidator(self.reg_ex_1))
        self.device_layout.addWidget(self.osc_input, 4, 1)

        # Adds TEC rate
        self.tec_label = QLabel("Set TEC Temperature (C):")
        self.tec_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.tec_label, 5, 0)

        self.tec_layout = QHBoxLayout()
        self.tec_input = QLineEdit()
        self.tec_input.setMaximumWidth(150)
        self.tec = self.tec_input.text()
        self.tec_input.setPlaceholderText("25")
        self.tec_input.setValidator(QRegularExpressionValidator(self.reg_ex_1))
        self.tec_button = QPushButton("Set")
        self.tec_button.clicked.connect(self.set_tec)
        self.tec_button.setEnabled(False)
        self.tec_button.setMaximumWidth(50)
        self.tec_layout.addWidget(self.tec_input)
        self.tec_layout.addWidget(self.tec_button)
        self.device_layout.addLayout(self.tec_layout, 5, 1)

        # Adds Laser rate
        self.laser_label = QLabel("Set Laser Output (mA):")
        self.laser_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.laser_label, 6, 0)

        self.laser_layout = QHBoxLayout()
        self.laser_input = QLineEdit()
        self.laser_input.setPlaceholderText("0")
        self.laser_input.setMaximumWidth(150)
        self.laser_input.setValidator(QRegularExpressionValidator(self.reg_ex_1))  # noqa E501
        self.laser_rate = self.laser_input.text()
        self.laser_button = QPushButton("Set")
        self.laser_button.clicked.connect(self.set_laser)
        self.laser_button.setEnabled(False)
        self.laser_button.setMaximumWidth(50)
        self.laser_layout.addWidget(self.laser_input)
        self.laser_layout.addWidget(self.laser_button)
        self.device_layout.addLayout(self.laser_layout, 6, 1)

        self.pid_btn = QPushButton("Set PID values")
        self.pid_btn.setMaximumWidth(200)
        self.pid_btn.clicked.connect(self.set_pid)
        self.pid_btn.setEnabled(False)
        self.device_layout.addWidget(self.pid_btn, 7, 0)

        self.laser_switch = QPushButton("Start laser")
        self.laser_switch.setMaximumWidth(200)
        self.laser_switch.clicked.connect(self.start_laser)
        self.laser_switch.setEnabled(False)
        self.device_layout.addWidget(self.laser_switch, 7, 1)

        self.laser_connection_btn = QPushButton("Establish Connection")
        self.laser_connection_btn.setMaximumWidth(200)
        self.laser_connection_btn.clicked.connect(self.establish_connection)  # noqa E501
        self.laser_connection_btn.setCheckable(True)
        self.device_layout.addWidget(self.laser_connection_btn, 7, 2)

        self.device_widget.setLayout(self.device_layout)

        return self.device_widget

    def set_laser(self):
        """Method that sets the laser output
        for the connected ThorlabsCLD101X device
        to `laser_input` mA.
        """
        self.thor.UpdateLaserCurrent(float(self.laser_input.text()))
        notif_txt = self.dev_id + " laser set to " + self.laser_input.text() + " mA"  # noqa E501
        self.parent.notify(notif_txt)
        return

    def set_tec(self):
        """Method that sets TEC temperature
        for the connected ThorlabsCLD101X device
        to `tec_input` C.
        """
        self.thor.SetTECTemp(self.tec_input.text())
        self.laser_switch.setEnabled(True)
        self.parent.notify(self.dev_id + " TEC set to " + self.tec_input.text() +" C")  # noqa E501
        return

    def start_laser(self):
        """Method to start the laser
        connected to the Thoelabs CLD101X device"""
        self.thor.SwitchLaser(Switch=True)
        self.laser_button.setEnabled(True)
        self.thor.StartTEC(Switch=True)
        self.parent.notify(self.dev_id + " laser on")
        return

    def set_pid(self):
        """Method that sets the P, I, and D
        component of the connected ThorlabCLD101X.
        """
        Prop = float(self.p_input.text())
        Intgrl = float(self.i_input.text())
        Derivative = float(self.d_input.text())
        Osc = float(self.osc_input.text())
        self.thor.set_TECPID(Prop, Intgrl, Derivative, Osc)
        self.parent.notify("P,I,D, Osc period for " + self.dev_id + "set to " + str(Prop) + str(Intgrl) + str(Derivative) + str(Osc) + " s, respectively")  # noqa #E501

    def establish_connection(self):
        """Method that connects to the
        ThorlabsCLD101X connected at selected
        `comport_input`.
        The P, I, D, and osc input labels will be
        updated with the present values on the controller.
        """
        if self.laser_connection_btn.isChecked():
            self.thor = EchoThor()
            self.thor.set_connection(self.comport_input.currentText())
            PID_set = self.thor.read_TECPID()
            self.p_input.setText(PID_set["P"])
            self.i_input.setText(PID_set["I"])
            self.d_input.setText(PID_set["D"])
            self.osc_input.setText(PID_set["O"])
            self.parent.notify(self.dev_id + " succesfully connected. Present PID values updatesd.")  # noqa #E501
            self.laser_connection_btn.setText("Stop Connection")
            self.tec_button.setEnabled(True)
            self.pid_btn.setEnabled(True)
        else:
            self.laser_connection_btn.setText("Establish Connection")
            self.thor.close()
            self.tec_button.setEnabled(False)
            self.laser_button.setEnabled(False)
            self.laser_switch.setEnabled(False)
            self.pid_btn.setEnabled(False)

    def load_device_data(self, p, i, d, o, comport, tec, laser_rate):
        """Method to load a previously saved laser device data
        """
        self.comport = comport
        self.comport_input.setCurrentText(self.comport)
        self.p = p
        self.p_input.setText(self.p)
        self.i = i
        self.i_input.setText(self.i)
        self.tec = tec
        self.tec_input.setText(self.tec)
        self.d = d
        self.d_input.setText(self.d)
        self.o = o
        self.osc_input.setText(self.o)
        self.laser_rate = laser_rate
        self.laser_input.setText(self.laser_rate)

    def get_type(self):
        """Method that returns the type of the device
        """
        return self.type

    def settings_to_dict(self):
        """Method that stores laser device
        information to `settings` dictionary.
        """
        try:
            self.settings["COMPORT"] = self.comport_input.currentText()
            self.settings["P"] = float(self.p_input.text())
            self.settings["I"] = float(self.i_input.text())
            self.settings["D"] = float(self.d_input.text())
            self.settings["O"] = float(self.osc_input.text())
            self.settings["Laser Rate"] = float(self.laser_input.text())
            self.settings["Tec Rate"] = float(self.tec_input.text())
            self.settings["Type"] = self.type
        except ValueError as e:
            self.settings.clear()
            raise ValueError("Data Invalid for " + self.dev_id) from e
        return self.settings


class alicat_mfc(QWidget):
    """User-added Alicat Mass Flow Controller

    Attributes
    ----------
        type: str
            Value is "mfc"
        parent: Object
            Defines parent class
        dev_id: str
            Device ID
        settings: dict
            Stores settings for the controller
    """
    reg_ex_1 = QRegularExpression(r"[0-9]*\.[0-9]{0,4}")  # double

    def __init__(self, parent, tabs, str_name):
        super().__init__()
        self._makemfc(parent, tabs, str_name)

    def _makemfc(self, parent, tabs, str_name):
        self.type = "mfc"
        self.dev_id = str_name
        self.parent = parent
        self.settings = {}
        self.content = self.create_alicat_mfc_content()
        self.parent.device_tab_widget.addTab(self.content, self.dev_id)

    def create_alicat_mfc_content(self):
        """Method that creates Alicat MFC contents

        Fields
        ----------------------
        - comport_input: QComboBox
            Dropdown of list of available COMPorts
        - gas_input: QComboBox
            Dropdown of list of available COMPorts.
            Currently available gases are listed
            in utilities.DAQUtils submodule.
        - dil_rate_input: QLineEdit
            Value in default Alicat flow-rate unit.
            Usually slpm/sccm.
            This input will be used
            to set the MFC flow-rate.
        - set_flow_btn: QPushButton
            Calls set_flow_rate()
        - stop_flow_btn: QPushButton
            Calls stop_flow_rate()
        - mfc_connection_btn: QPushButton
            Calls establish_connection()
        """
        # Adds Layout
        self.device_widget = QWidget()
        self.device_layout = QGridLayout()

        # Adds COMPORT input field
        self.comport_label = QLabel("Select COMPORT:")
        self.comport_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.comport_label, 0, 0)
        self.comport_input = QComboBox()
        for comport in COMports:
            self.comport_input.addItem(comport)
        self.comport_input.setMaximumWidth(200)
        self.comport = self.comport_input.currentText()
        self.device_layout.addWidget(self.comport_input, 0, 1)

        # Adds gas input field
        self.gas_label = QLabel("Select gas:")
        self.device_layout.addWidget(self.gas_label, 1, 0)
        self.gas_label.setMaximumWidth(200)
        self.gas_input = QComboBox()
        for _, gas in AlicatGases.items():
            self.gas_input.addItem(gas)
        self.gas = self.gas_input.currentText()
        self.gas_input.setMaximumWidth(200)
        self.device_layout.addWidget(self.gas_input, 1, 1)

        # Adds dilution rate
        self.dil_rate_label = QLabel("Enter gas flow rate \n(default Alicat, slpm/sccm):")  # noqa E501
        self.dil_rate_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.dil_rate_label, 2, 0)
        self.dil_rate_input = QLineEdit()
        self.dil_rate_input.setText("0")
        self.dil_rate_input.setValidator(QRegularExpressionValidator(self.reg_ex_1))  # noqa E501
        self.dil_rate_input.setMaximumWidth(200)
        self.dil_rate = self.dil_rate_input.text()
        self.device_layout.addWidget(self.dil_rate_input, 2, 1)
        self.device_widget.setLayout(self.device_layout)

        self.flow_layout = QHBoxLayout()
        self.set_flow_btn = QPushButton("Set Flow Rate")
        self.set_flow_btn.setEnabled(False)
        self.stop_flow_btn = QPushButton("Stop Flow Rate")
        self.stop_flow_btn.setEnabled(False)
        self.set_flow_btn.clicked.connect(self.set_flow_rate)
        self.stop_flow_btn.clicked.connect(self.stop_flow_rate)
        self.stop_flow_btn.setMaximumWidth(100)
        self.set_flow_btn.setMaximumWidth(100)
        self.flow_layout.addWidget(self.set_flow_btn)
        self.flow_layout.addWidget(self.stop_flow_btn)
        self.device_layout.addLayout(self.flow_layout, 3, 0)

        self.mfc_connection_btn = QPushButton("Establish Connection")
        self.set_flow_btn.setMaximumWidth(200)
        self.mfc_connection_btn.clicked.connect(self.establish_connection)
        self.mfc_connection_btn.setCheckable(True)
        self.device_layout.addWidget(self.mfc_connection_btn, 3, 1)

        return self.device_widget

    def set_flow_rate(self):
        """Method that sets the flow rate of the Alicat MFC
        to the value input `dil_rate_input`.
        """
        new_flow = float(self.dil_rate_input.text())
        self.loop.run_until_complete(self.MFC.set_MFC_val(flow_rate=new_flow))
        self.parent.notify(str(self.dev_id) + " flow set to " + str(new_flow), "success") # noqa E501

    def stop_flow_rate(self):
        """Method that sets the flow-rate of the Alicat MFC
        to zero
        """
        self.loop.run_until_complete(self.MFC.set_MFC_val(flow_rate=0))
        self.parent.notify(str(self.dev_id) + " flow set to zero", "success")
        self.dil_rate_input.setText('0.0')
        return

    def GetMFCFlow(self):
        MFC_Vals = self.loop.run_until_complete(self.MFC.get_MFC_val())
        return MFC_Vals

    def establish_connection(self):
        """Method that establishes connection with
        Alicat device at `comport_input`
        and sets the gas type to gas_input.
        """
        if self.mfc_connection_btn.isChecked():
            try:
                self.MFC = EchoController()
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                com = self.comport_input.currentText()
                gas = self.gas_input.currentText()
                gas = [gastxt for gastxt, gasunicode in AlicatGases.items() if bytes(gasunicode, "utf-8") == bytes(gas, "utf-8")][0]  # noqa E501
                time.sleep(0.1)
                self.loop.run_until_complete(self.MFC.set_params(com, gas=gas))
                self.parent.notify(self.dev_id + " connected successfully", "success")  # noqa E501

                self.mfc_connection_btn.setText("Stop Connection")
                self.set_flow_btn.setEnabled(True)
                self.stop_flow_btn.setEnabled(True)
            except Exception as e:
                self.parent.notify(self.dev_id + " connection error" +str(e), "error")  # noqa E501
        else:
            self.loop.run_until_complete(self.MFC.end_connection())
            self.parent.notify("Connection to " + self.dev_id + " ended successfully", "success")  # noqa E501
            self.mfc_connection_btn.setText("Establish Connection")

            self.set_flow_btn.setEnabled(False)
            self.stop_flow_btn.setEnabled(False)

    def get_name(self):
        """Method to get the id of the MFC.
        """
        return self.dev_id

    def get_dil_rate(self):
        """Method to get flow-rate input defined byt he user.
        """
        self.dil_rate = self.dil_rate_input.text()
        return self.dil_rate

    def get_gas(self):
        """Method to read the gas type selected by the user.
        """
        self.gas = self.gas_input.currentText()
        return self.gas

    def load_device_data(self, gas_val, rate_val, comp_val):
        """Method to load the pre-saved Alicat MFC device data
        """
        self.gas = gas_val
        self.gas_input.setCurrentText(gas_val)
        self.dil_rate = rate_val
        self.dil_rate_input.setText(rate_val)
        self.comport = comp_val
        self.comport_input.setCurrentText(comp_val)

    def get_type(self):
        """Method to get the type of the device
        """
        return self.type

    def settings_to_dict(self):
        """Method that saves the MFC device data to `settings` dictionary.
        """
        self.settings["COMPORT"] = self.comport_input.currentText()
        self.settings["Gas"] = self.gas_input.currentText()
        self.settings["Type"] = self.type
        try:
            self.settings["Rate"] = float(self.dil_rate_input.text())
        except ValueError as v:
            self.settings.clear()
            raise ValueError("Data Invalid for " + self.dev_id) from v
        return self.settings


class mfm(QWidget):
    """User-added Alicat Mass Flow Meter device.

    Attributes
    ----------
        type: str
            Value is "mfm"
        parent: Object
            Defines parent class
        dev_id: str
            Device ID
        settings: dict
            Stores settings for the meter
    """
    def __init__(self, parent, str_name):
        super().__init__()
        self._makemfm(parent, str_name)

    def _makemfm(self, parent, str_name):
        self.type = "mfm"
        self.dev_id = str_name
        self.parent = parent
        self.settings = {}
        self.content = self.create_mfm_content()
        self.parent.device_tab_widget.addTab(self.content, self.dev_id)

    def create_mfm_content(self):
        """Method to add Mass Flow Meter content.

        Fields
        ----------------------
        - comport_input: QComboBox
            Dropdown of list of available COMPorts
        - gas_input: QComboBox
            Dropdown of list of available COMPorts.
            Currently available gases are listed
            in utilities.DAQUtils submodule.
        - mfm_connection_btn: QPushButton
            Calls establish_connection()
        """
        # Adds Layout
        self.device_widget = QWidget()
        self.device_layout = QGridLayout()

        # Adds COMPORT input field
        self.comport_label = QLabel("Select COMPORT:")
        self.comport_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.comport_label, 0, 0)
        self.comport_input = QComboBox()
        for comport in COMports:
            self.comport_input.addItem(comport)
        self.comport_input.setMaximumWidth(200)
        self.comport = self.comport_input.currentText()
        self.device_layout.addWidget(self.comport_input, 0, 1)

        # Adds gas input field
        self.gas_label = QLabel("Enter gas name:")
        self.device_layout.addWidget(self.gas_label, 1, 0)
        self.gas_label.setMaximumWidth(200)
        self.gas_input = QComboBox()
        for _, gas_text in AlicatGases.items():
            self.gas_input.addItem(gas_text)
        self.gas = self.gas_input.currentText()
        self.gas_input.setMaximumWidth(200)
        self.device_layout.addWidget(self.gas_input, 1, 1)

        # Adds dilution rate
        self.rate_updtLabel = QLabel("Flow Rate")
        self.rate_updtLabel.setMaximumWidth(200)
        self.device_layout.addWidget(self.rate_updtLabel, 2, 0)
        self.flow_rateVal = QLabel("Flow rate will be updated here.")
        self.flow_rateVal.setMaximumWidth(200)
        self.device_layout.addWidget(self.flow_rateVal, 2, 1)

        self.mfm_connection_btn = QPushButton("Establish Connection")
        self.mfm_connection_btn.setMaximumWidth(200)
        self.mfm_connection_btn.setCheckable(True)
        self.mfm_connection_btn.clicked.connect(self.establish_connection)  # noqa E501
        self.device_layout.addWidget(self.mfm_connection_btn, 3, 1)
        self.device_widget.setLayout(self.device_layout)

        return self.device_widget

    def establish_connection(self):
        """Method to establish connection with an Alicat
        MFM device connected at `comport_input` with
        `gas_input` selected gas type.
        """
        if self.mfm_connection_btn.isChecked():
            self.mfm_connection_btn.setText("Establish Connection")
            self.flow_rate_btn.setEnabled(True)
            self.parent.notify(self.dev_id + " connected successfully", "success")  # noqa E501
        else:
            self.mfm_connection_btn.setText("Stop Connection")
            self.flow_rate_btn.setEnabled(False)
            self.parent.notify("Connection to " + self.dev_id + " ended successfully", "success")  # noqa E501

    def get_name(self):
        """Method to get device id for the MFM device
        """
        return self.dev_id

    def get_gas(self):
        """Method to get the user-selected gas type for the MFM device
        """
        self.gas = self.gas_input.currentText()
        return self.gas

    def load_device_data(self, gas_val, comport):
        """Method to load pre-saved MFM device data
        """
        self.gas = gas_val
        self.gas_input.setCurrentText(gas_val)
        self.comport = comport
        self.comport_input.setCurrentText(comport)

    def get_type(self):
        """Method to get the type of the device
        """
        return self.type

    def settings_to_dict(self):
        """Method that saves the MFM device data to `settings` dictionary.
        """
        self.settings["COMPORT"] = self.comport_input.currentText()
        self.settings["Gas"] = self.gas_input.currentText()
        return self.settings
