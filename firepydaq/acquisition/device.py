from PySide6.QtWidgets import (QWidget, QGridLayout, QLabel,
                               QLineEdit, QComboBox, QHBoxLayout,
                               QPushButton)
from ..utilities.DAQUtils import COMports, AlicatGases


class thorlabs_laser(QWidget):
    """Object that stores user-added
    ThorlabsCLD101X Controller information

    Attributes
    ----------
        type: str
            Value is "laser"
        parent: Object
            Defines parent class
        settings: dict
            Stores settings for the controller
    """
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
        - establish_connection_btn: QPushButton
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
        self.p_input.setPlaceholderText("0")
        self.p = self.p_input.text()
        self.device_layout.addWidget(self.p_input, 1, 1)

        # Adds I input field
        self.i_label = QLabel("Enter I value:")
        self.device_layout.addWidget(self.i_label, 2, 0)
        self.i_label.setMaximumWidth(200)

        self.i_input = QLineEdit()
        self.i_input.setPlaceholderText("0")
        self.i_input.setMaximumWidth(200)
        self.i = self.i_input.text()
        self.device_layout.addWidget(self.i_input, 2, 1)

        # Adds D input field
        self.d_label = QLabel("Enter D value:")
        self.device_layout.addWidget(self.d_label, 3, 0)
        self.d_label.setMaximumWidth(200)

        self.d_input = QLineEdit()
        self.d_input.setPlaceholderText("0")
        self.d_input.setMaximumWidth(200)
        self.d = self.d_input.text()
        self.device_layout.addWidget(self.d_input, 3, 1)

        # Adds TEC rate
        self.tec_label = QLabel("Set TEC Temperature (C):")
        self.tec_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.tec_label, 4, 0)

        self.tec_layout = QHBoxLayout()
        self.tec_input = QLineEdit()
        self.tec_input.setMaximumWidth(150)
        self.tec = self.tec_input.text()
        self.tec_input.setPlaceholderText("25")
        self.tec_button = QPushButton("Set")
        self.tec_button.clicked.connect(self.set_tec)
        self.tec_button.setEnabled(False)
        self.tec_button.setMaximumWidth(50)
        self.tec_layout.addWidget(self.tec_input)
        self.tec_layout.addWidget(self.tec_button)
        self.device_layout.addLayout(self.tec_layout, 4, 1)

        # Adds Laser rate
        self.laser_label = QLabel("Set Laser Output (mA):")
        self.laser_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.laser_label, 5, 0)

        self.laser_layout = QHBoxLayout()
        self.laser_input = QLineEdit()
        self.laser_input.setPlaceholderText("0")
        self.laser_input.setMaximumWidth(150)
        self.laser_rate = self.laser_input.text()
        self.laser_button = QPushButton("Set")
        self.laser_button.clicked.connect(self.set_laser)
        self.laser_button.setEnabled(False)
        self.laser_button.setMaximumWidth(50)
        self.laser_layout.addWidget(self.laser_input)
        self.laser_layout.addWidget(self.laser_button)
        self.device_layout.addLayout(self.laser_layout, 5, 1)

        self.pid_btn = QPushButton("Set PID values")
        self.pid_btn.setMaximumWidth(200)
        self.pid_btn.clicked.connect(self.set_pid)
        self.pid_btn.setEnabled(False)
        self.device_layout.addWidget(self.pid_btn, 6, 0)

        self.establish_connection_btn = QPushButton("Establish Connection")
        self.establish_connection_btn.setMaximumWidth(200)
        self.establish_connection_btn.clicked.connect(self.establish_connection)
        self.establish_connection_btn.setCheckable(True)
        self.device_layout.addWidget(self.establish_connection_btn, 6, 1)

        self.device_widget.setLayout(self.device_layout)

        return self.device_widget

    def set_laser(self):
        """Method that sets the laser output
        for the connected ThorlabsCLD101X device
        to `laser_input` mA.
        """
        print("set laser")

    def set_tec(self):
        """Method that sets TEC temperature
        for the connected ThorlabsCLD101X device
        to `tec_input` C.
        """
        print("set tec")
        self.laser_button.setEnabled(True)

    def set_pid(self):
        """Method that sets the P, I, and D
        component of the connected ThorlabCLD101X.
        """
        print("pid set")

    def establish_connection(self):
        """Method that connects to the
        ThorlabsCLD101X connected at selected
        `comport_input`
        """
        if self.establish_connection_btn.isChecked():
            self.establish_connection_btn.setText("Establish Connection")
            self.tec_button.setEnabled(True)
            self.pid_btn.setEnabled(True)
        else:
            self.establish_connection_btn.setText("Stop Connection")
            self.tec_button.setEnabled(False)
            self.laser_button.setEnabled(False)
            self.pid_btn.setEnabled(False)

    def load_device_data(self, p, i, d, comport, tec, laser_rate):
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
            self.settings["Laser Rate"] = float(self.laser_input.text())
            self.settings["Tec Rate"] = float(self.tec_input.text())
            self.settings["Type"] = self.type
        except ValueError as e:
            self.settings.clear()
            raise ValueError("Data Invalid for " + self.dev_id) from e
        return self.settings


class alicat_mfc(QWidget):
    """Object that stores user-added
    Alicat Mass Flow Controller information

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

    def __init__(self, parent, tabs, str_name):
        super().__init__()
        self._makeinit()

    def _makeinit(self, parent, tabs, str_name):
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
        - connection_btn: QPushButton
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
        for _, gas_text in AlicatGases.items():
            self.gas_input.addItem(gas_text)
        self.gas = self.gas_input.currentText()
        self.gas_input.setMaximumWidth(200)
        self.device_layout.addWidget(self.gas_input, 1, 1)

        # Adds dilution rate
        self.dil_rate_label = QLabel("Enter gas flow rate \n(default Alicat, slpm/sccm):")
        self.dil_rate_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.dil_rate_label, 2, 0)
        self.dil_rate_input = QLineEdit()
        self.dil_rate_input.setText("0")
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

        self.connection_btn = QPushButton("Establish Connection")
        self.set_flow_btn.setMaximumWidth(200)
        self.connection_btn.clicked.connect(self.establish_connection)
        self.connection_btn.setCheckable(True)
        self.device_layout.addWidget(self.connection_btn, 3, 1)

        return self.device_widget

    def set_flow_rate(self):
        """Method that sets the flow rate of the Alicat MFC
        to the value input `dil_rate_input`.
        """
        # todo: Set flowrate to input text value
        print("set")

    def stop_flow_rate(self):
        """Method that sets the flow-rate of the Alicat MFC
        to zero
        """
        # todo: Set flow rate to zero
        print("set")

    def establish_connection(self):
        """Method that establishes connection with
        Alicat device at `comport_input`
        and sets the gas type to gas_input.
        """
        if self.connection_btn.isChecked():
            # todo: Establish communication
            self.connection_btn.setText("Stop Connection")
            self.set_flow_btn.setEnabled(True)
            self.stop_flow_btn.setEnabled(True)
        else:
            self.connection_btn.setText("Establish Connection")
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
    """Object that stores an added
    Alicat Mass Flow Meter device.

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
        self._makeinit(parent, str_name)

    def _makeinit(self, parent, str_name):
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
        - establish_connection_btn: QPushButton
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

        self.establish_connection_btn = QPushButton("Establish Connection")
        self.establish_connection_btn.setMaximumWidth(200)
        self.establish_connection_btn.setCheckable(True)
        self.establish_connection_btn.clicked.connect(self.establish_connection)
        self.device_layout.addWidget(self.establish_connection_btn, 3, 1)
        self.device_widget.setLayout(self.device_layout)

        return self.device_widget

    def establish_connection(self):
        """Method to establish connection with an Alicat
        MFM device connected at `comport_input` with
        `gas_input` selected gas type.
        """
        if self.establish_connection_btn.isChecked():
            self.establish_connection_btn.setText("Establish Connection")
            self.flow_rate_btn.setEnabled(True)
        else:
            self.establish_connection_btn.setText("Stop Connection")
            self.flow_rate_btn.setEnabled(False)

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

