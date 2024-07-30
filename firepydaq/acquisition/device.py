from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QComboBox, QHBoxLayout, QPushButton
from ..utilities.Utils import COMports

class thorlabs_laser(QWidget):
    def __init__(self, parent, str_name):
        super().__init__()
        self.type = "laser"
        self.dev_id = str_name
        self.parent = parent
        self.settings = {}
        self.content = self.create_thorlabs_laser_content()
        self.parent.device_tab_widget.addTab(self.content, self.dev_id)
    
    def create_thorlabs_laser_content(self):
        
        # Adds Layout
        self.device_widget = QWidget()
        self.device_layout = QGridLayout()

        # Adds COMPORT input field 
        self.comport_label =  QLabel("Enter COMPORT name:")
        self.comport_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.comport_label, 0, 0)

        self.comport_input = QLineEdit()
        self.comport_input.setMaximumWidth(200)
        self.comport = self.comport_input.text() 
        self.device_layout.addWidget(self.comport_input, 0, 1)

        # Adds P input field 
        self.p_label = QLabel("Enter P value:")
        self.device_layout.addWidget(self.p_label, 1, 0)
        self.p_label.setMaximumWidth(200)

        self.p_input = QLineEdit()
        self.p_input.setMaximumWidth(200)
        self.p = self.p_input.text() 
        self.device_layout.addWidget(self.p_input, 1, 1)
        
        # Adds I input field 
        self.i_label = QLabel("Enter I value:")
        self.device_layout.addWidget(self.i_label, 2, 0)
        self.i_label.setMaximumWidth(200)

        self.i_input = QLineEdit()
        self.i_input.setMaximumWidth(200)
        self.i = self.i_input.text() 
        self.device_layout.addWidget(self.i_input, 2, 1)

        # Adds D input field 
        self.d_label = QLabel("Enter D value:")
        self.device_layout.addWidget(self.d_label, 3, 0)
        self.d_label.setMaximumWidth(200)

        self.d_input = QLineEdit()
        self.d_input.setMaximumWidth(200)
        self.d = self.d_input.text() 
        self.device_layout.addWidget(self.d_input, 3, 1)

        # Adds TEC rate
        self.tec_label = QLabel("Enter TEC rate:")
        self.tec_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.tec_label, 4, 0)

        self.tec_layout = QHBoxLayout()
        self.tec_input = QLineEdit()
        self.tec_input.setMaximumWidth(150)
        self.tec = self.tec_input.text()
        self.tec_button = QPushButton("Start")
        self.tec_button.setMaximumWidth(50)
        self.tec_layout.addWidget(self.tec_input)
        self.tec_layout.addWidget(self.tec_button)
        self.device_layout.addLayout(self.tec_layout, 4, 1)

        # Adds Laser rate
        self.laser_label = QLabel("Set Laser Output:")
        self.laser_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.laser_label, 5, 0)

        self.laser_layout = QHBoxLayout()
        self.laser_input = QLineEdit()
        self.laser_input.setMaximumWidth(150)
        self.laser_rate = self.laser_input.text()
        self.laser_button = QPushButton("Start")
        self.laser_button.setMaximumWidth(50)
        self.laser_layout.addWidget(self.laser_input)
        self.laser_layout.addWidget(self.laser_button)
        self.device_layout.addLayout(self.laser_layout, 5, 1)
        self.device_widget.setLayout(self.device_layout)
        return self.device_widget

    def load_device_data(self, p , i, d , comport, tec, laser_rate):
        self.comport = comport
        self.comport_input.setText(self.comport)
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
        return self.type
    
    def settings_to_dict(self):
        try:
            self.settings["COMPORT"] = self.comport_input.text()
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

    #set methods gas, rate, establish connection


class alicat_mfc(QWidget):

    def __init__(self, parent, tabs, str_name):
        super().__init__()
        self.type = "mfc"
        self.dev_id = str_name
        self.parent = parent
        self.settings = {}
        self.content = self.create_alicat_mfc_content()
        self.parent.device_tab_widget.addTab(self.content, self.dev_id)
    
    def create_alicat_mfc_content(self):
        
        # Adds Layout
        self.device_widget = QWidget()
        self.device_layout = QGridLayout()

        # Adds COMPORT input field 
        self.comport_label =  QLabel("Enter COMPORT name:")
        self.comport_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.comport_label, 0, 0)
        self.comport_input = QLineEdit()
        self.comport_input.setMaximumWidth(200)
        self.comport = self.comport_input.text() 
        self.device_layout.addWidget(self.comport_input, 0, 1)

        # Adds gas input field 
        self.gas_label = QLabel("Enter gas name:")
        self.device_layout.addWidget(self.gas_label, 1, 0)
        self.gas_label.setMaximumWidth(200)
        self.gas_input = QComboBox()
        self.gas_input.addItem(u'N\u2082')
        self.gas_input.addItem(u'C\u2083H\u2088')
        self.gas_input.addItem(u'Air')
        self.gas = self.gas_input.currentText() 
        self.gas_input.setMaximumWidth(200)
        self.device_layout.addWidget(self.gas_input, 1, 1)

        # Adds dilution rate
        self.dil_rate_label = QLabel("Enter gas dilution rate:")
        self.dil_rate_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.dil_rate_label, 2, 0)
        self.dil_rate_input = QLineEdit()
        self.dil_rate_input.setPlaceholderText("1:50")
        self.dil_rate_input.setMaximumWidth(200)
        self.dil_rate = self.dil_rate_input.text()
        self.device_layout.addWidget(self.dil_rate_input, 2, 1)
        self.device_widget.setLayout(self.device_layout)

        return self.device_widget
    
    def get_name(self):
        return self.dev_id
    
    def get_dil_rate(self):
        self.dil_rate =  self.dil_rate_input.text()
        return self.dil_rate
    
    def get_gas(self):
        self.gas = self.gas_input.currentText()
        return self.gas
    
    def load_device_data(self, gas_val, rate_val, comp_val):
        self.gas = gas_val
        self.gas_input.setCurrentText(gas_val)
        self.dil_rate = rate_val
        self.dil_rate_input.setText(rate_val)
        self.comport = comp_val
        self.comport_input.setText(comp_val)
    
    def get_type(self):
        return self.type
    
    def settings_to_dict(self):
        self.settings["COMPORT"] = self.comport_input.text()
        self.settings["Gas"] = self.gas_input.currentText()
        self.settings["Type"] = self.type
        try:
         self.settings["Rate"] = float(self.dil_rate_input.text())
        except ValueError as v:
            self.settings.clear()
            raise ValueError("Data Invalid for" + self.dev_id) from v
        return self.settings
    

class mfm(QWidget):

    def __init__(self, parent, str_name):
        super().__init__()
        self.type = "mfm"
        self.dev_id = str_name
        self.parent = parent
        self.settings = {}
        self.content = self.create_mfm_content()
        self.parent.device_tab_widget.addTab(self.content, self.dev_id)
    
    def create_mfm_content(self):
        
        # Adds Layout
        self.device_widget = QWidget()
        self.device_layout = QGridLayout()

        # Adds COMPORT input field 
        self.comport_label =  QLabel("Enter COMPORT name:")
        self.comport_label.setMaximumWidth(200)
        self.device_layout.addWidget(self.comport_label, 0, 0)
        self.comport_input = QLineEdit()
        self.comport_input.setMaximumWidth(200)
        self.comport = self.comport_input.text() 
        self.device_layout.addWidget(self.comport_input, 0, 1)

        # Adds gas input field 
        self.gas_label = QLabel("Enter gas name:")
        self.device_layout.addWidget(self.gas_label, 1, 0)
        self.gas_label.setMaximumWidth(200)
        self.gas_input = QComboBox()
        self.gas_input.addItem(u'N\u2082')
        self.gas_input.addItem(u'C\u2083H\u2088')
        self.gas_input.addItem(u'Air')
        self.gas = self.gas_input.currentText() 
        self.gas_input.setMaximumWidth(200)
        self.device_layout.addWidget(self.gas_input, 1, 1)

        # Adds dilution rate
        self.flow_rate_btn = QPushButton("Update Flow Rate")
        self.flow_rate_btn.setMaximumWidth(200)
        self.device_layout.addWidget(self.flow_rate_btn, 2, 0)
        self.device_widget.setLayout(self.device_layout)

        return self.device_widget
    
    def get_name(self):
        return self.dev_id
    
    def get_gas(self):
        self.gas = self.gas_input.currentText()
        return self.gas
    
    def load_device_data(self, gas_val, comport):
        self.gas = gas_val
        self.gas_input.setCurrentText(gas_val)
        self.comport = comport
        self.comport_input.setText(comport)
    
    def get_type(self):
        return self.type
    
    def settings_to_dict(self):
        self.settings["COMPORT"] = self.comport_input.text()
        self.settings["Gas"] = self.gas_input.currentText()
        return self.settings

    #set methods gas, rate, establish connection


