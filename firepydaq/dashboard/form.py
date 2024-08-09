import sys
from .app_v1 import create_dash_app
from PySide6.QtWidgets import (QLineEdit, QWidget, QVBoxLayout, QPushButton, QLabel, 
    QHBoxLayout, QGridLayout, QMainWindow, QMenuBar, QTabWidget, QFileDialog, QApplication)
from PySide6.QtGui import QAction, QActionGroup
import os

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FIREpyDAQ Dashboard")
        self.setFixedSize(500, 300)
        self.setGeometry(0, 0, 500, 300)
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.menu = QMenuBar()
        self.setMenuBar(self.menu)
        self.intialise_menu()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)
        self.assets_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "assets"
        self.style_light = self.assets_folder + os.path.sep + "styles_light.css"
        self.style_dark = self.assets_folder + os.path.sep + "styles_dark.css"
        self.popup_light = self.assets_folder + os.path.sep + "popup_light.css"
        self.popup_dark = self.assets_folder + os.path.sep + "popup_dark.css"
        self.switch_mode("Light")
        self.input_tab_widget = QTabWidget()
        self.input_tab_content = self.intialise_layout()
        self.input_tab_widget.addTab(self.input_tab_content, "Input Settings")
        self.main_layout.addWidget(self.input_tab_widget)
        self.intialise_layout()

    def intialise_layout(self):
        #Parquet File Name 
        self.input_settings_widget = QWidget()
        self.input_layout = QGridLayout(self.input_settings_widget)

        self.parq_label = QLabel("Select Parquet File:")
        self.input_layout.addWidget(self.parq_label, 0, 0)
        self.parq_label.setMaximumWidth(200)

        self.parq_file_layout = QHBoxLayout()
        self.parq_file_edit = QLineEdit()
        self.parq_input = QPushButton("Select")
        self.parq_input.clicked.connect(self.set_parq_file)
        self.parq_input.setMaximumWidth(50)
        self.parq_file_edit.setMaximumWidth(150)
        self.parq_file_layout.addWidget(self.parq_file_edit)
        self.parq_file_layout.addWidget(self.parq_input)
        self.input_layout.addLayout(self.parq_file_layout, 0, 1)

        # Configuration File Name
        self.config_label = QLabel("Select Configuration File:")
        self.input_layout.addWidget(self.config_label, 1, 0)
        self.config_label.setMaximumWidth(200)

        self.config_file_layout = QHBoxLayout()
        self.config_file_edit = QLineEdit()
        self.config_input = QPushButton("Select")
        self.config_input.clicked.connect(self.set_config_file)
        self.config_input.setMaximumWidth(50)
        self.config_file_edit.setMaximumWidth(150)
        self.config_file_layout.addWidget(self.config_file_edit)
        self.config_file_layout.addWidget(self.config_input)
        self.input_layout.addLayout(self.config_file_layout, 1, 1)

        # Formulae File Name
        self.form_label = QLabel("Select Formulae File:")
        self.input_layout.addWidget(self.form_label, 2, 0)
        self.form_label.setMaximumWidth(200)

        self.form_file_layout = QHBoxLayout()
        self.form_file_edit = QLineEdit()
        self.form_input = QPushButton("Select")
        self.form_input.clicked.connect(self.set_formula_file)
        self.form_input.setMaximumWidth(50)
        self.form_file_edit.setMaximumWidth(150)
        self.form_file_layout.addWidget(self.form_file_edit)
        self.form_file_layout.addWidget(self.form_input)
        self.input_layout.addLayout(self.form_file_layout, 2, 1)

        self.visualize = QPushButton("Visualize Files")
        self.input_layout.addWidget(self.visualize, 3, 1)
        self.visualize.clicked.connect(self.dashboard)
        self.visualize.setMaximumWidth(200)

        return self.input_settings_widget

    def dashboard(self):
        self.close()
        create_dash_app(datapath = self.parquet_file, configpath = self.config_file, formulapath = self.formula_file)

    def switch_mode(self, str):
        if str == "Light":
            f = open(self.style_light, "r")
            self.curr_mode = "Light"
        else:
            f = open(self.style_dark, "r")
            self.curr_mode = "Dark"
        style_str = f.read()
        self.setStyleSheet(style_str)
        f.close()

    def intialise_menu(self):
        display_menu = self.menu.addMenu("&Mode")

        # Design Mode Switch
        self.dark_mode = QAction("Dark Mode", self)
        self.dark_mode.triggered.connect(lambda: self.switch_mode("Dark"))
        display_menu.addAction(self.dark_mode)

        self.light_mode = QAction("Light Mode", self)
        self.light_mode.triggered.connect(lambda: self.switch_mode("Light"))
        display_menu.addAction(self.light_mode)

    def load_settings(self):
        dlg = QFileDialog(self, 'Select a File', None, "JSON files (*.json)")
        dlg.exec()

    def set_formula_file(self): 
        dlg = QFileDialog(self, 'Select a File', None, "CSV files (*.csv)")
        f = ""
        if dlg.exec():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
        if not isinstance(f, str):         
            self.formula_file = f.name
            self.form_file_edit.setText(self.formula_file)
        return self.formula_file
    
    def set_parq_file(self): 
        dlg = QFileDialog(self, 'Select a File', None, "Parquet files (*.parquet)")
        f = ""
        if dlg.exec():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
        if not isinstance(f, str):         
            self.parquet_file = f.name
            self.parq_file_edit.setText(self.parquet_file)
            QApplication.processEvents()
            self.parq_file_edit.update()
        return self.parquet_file
    
    def set_config_file(self): 
        dlg = QFileDialog(self, 'Select a File', None, "CSV files (*.csv)")
        f = ""
        if dlg.exec():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
        if not isinstance(f, str):         
            self.config_file = f.name
            self.config_file_edit.setText(self.config_file)
        return self.config_file

