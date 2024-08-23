import sys

# PyQT Related
from PySide6.QtCore import QTimer, QRegularExpression
from PySide6.QtGui import QIcon, Qt, QRegularExpressionValidator, QAction
from PySide6.QtWidgets import (
    QDialog, QMainWindow, QWidget, QVBoxLayout, QMenu,
    QTabWidget, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QFileDialog)
from .SaveSettingsDialog import SaveSettingsDialog
from .exception_list import UnfilledFieldError
from .MainMenu import MainMenu
import json
from .NotificationPanel import NotificationPanel

# Dashboard
from ..dashboard.app import create_dash_app
from ..utilities.PostProcessing import PostProcessData

import time
from datetime import datetime, timedelta

# Threading and multiprocesses
import queue
import threading
import concurrent.futures
import multiprocessing as mp

# Data related
import polars as pl
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

# String/Files validations
import glob
import re
import os

# NI related
from .NIAOtab import NIAOtab
from ..api.EchoNIDAQTask import CreateDAQTask

# Error handling
import traceback
from ..utilities.ErrorUtils import error_logger, firepydaq_logger

# To make the application icon in the tab
# appear as the selected icon for Windows
if os.name == 'nt':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('ulfsri.firepydaq.010')  # noqa: E501


class application(QMainWindow):
    """
    The main acquisition GUI that can be compiled
    """

    def __init__(self):

        super().__init__()

        self.MakeMainWindow()
        self.InitialiseTabs()
        self.InitVars()

    def MakeMainWindow(self):
        """Creates Main window and adds menu options

        - Fixed Geometry: 900 x 600
        - Import theme styles from css assets
        - Initiate light theme for the Window and add logo
        """

        # Set window properties
        self.setGeometry(0, 0, 900, 650)
        self.setFixedSize(900, 650)
        self.setWindowTitle("Facilitated Interface for Recording Experiments (FIRE)")  # noqa: E501
        self.menu = MainMenu(self)
        self.setMenuBar(self.menu)

        self.assets_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "assets"  # noqa: E501
        self.style_light = self.assets_folder + os.path.sep + "styles_light.css"  # noqa: E501
        self.style_dark = self.assets_folder + os.path.sep + "styles_dark.css"
        self.popup_light = self.assets_folder + os.path.sep + "popup_light.css"
        self.popup_dark = self.assets_folder + os.path.sep + "popup_dark.css"
        try:
            f = open(self.style_light)
            str = f.read()
            self.setStyleSheet(str)
            f.close()
        except Exception:
            self.notify("Error loading stylesheets", "error")

        ico_path = self.assets_folder + os.path.sep + "FIREpyDAQDark.png"
        self.setWindowIcon(QIcon(ico_path))

        # Create main widget
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        self.main_layout.setStretch(0, 2.5)
        self.main_layout.setStretch(1, 1.5)

    def InitVars(self):
        """Method that initiates various
        variables for later use.

        - Empty dicts:
            - device_arr
                Keeps a log of all Devices added by the user
            - settings
                Stores settings used for NI DAQ
            - lasers
                Stores info of Thorlabs CLD101X devices added by the user.
                Maximum 4 allowed.
            - mfms
                Stores info of all Alicat Mass Flow Meters added by the user.
                Maximum 4 allowed.
            - mfcs
                Stores info of Alicat Mass Flow Controllers added by the user.
                Maximum 4 allowed.
        - Empty lists:
            - labels_to_save
                Stores Labels to save, corresponding to the
                `Label` in NI config file,
                during acquisition
        - Booleans:
            - running = `True`
                If GUI is compiled. Default: True
            - acquiring_data = `False`
                Boolean which is `True` when acquisition is running
            - display = `False`
                Plots or Dashboard
            - dashboard = `False`
                If dashboard display is selected. Default: `False`
            - tab = `False`
                If Tabular plot display is selected. Default: `False`
        - Others:
            - re_StrAllowable = r'^[A-Za-z0-9_]+$'
                regex format for allowable strings for some input fields.
                Alphanumeric with underscores, no spaces allowed.
            - dt_format = "%Y-%m-%d %H:%M:%S:%f"
                Format for how Absolute time is saved during acquisition
            - fext = ".parquet"
                File format for collected NI data
            - curr_mode = "Light"
                GUI mode/Theme
        """
        # array holding all device objects
        self.device_arr = {}
        self.settings = {}
        self.lasers = {}
        self.mfms = {}
        self.mfcs = {}

        self.labels_to_save = []

        self.running = True
        self.acquiring_data = False
        self.display = False
        self.dashboard = False
        self.tab = False

        self.re_strAllowable = r'^[A-Za-z0-9_]+$'
        self.dt_format = "%Y-%m-%d %H:%M:%S:%f"
        self.fext = '.parquet'
        self.curr_mode = "Light"

    def InitialiseTabs(self):
        """Initiates tabs based on `input_content`
        """
        self.input_tab_widget = QTabWidget()
        self.input_tab_content = self.input_content()
        self.input_tab_widget.addTab(self.input_tab_content, "Input Settings")
        self.main_layout.addWidget(self.input_tab_widget)

    def input_content(self):
        """Creates input content for NI device by default

        Generated content
        ------------
        - name_input: QLineEdit
            Name for Operator
            `re_StrAllowable` pattern is checked in `set_up()`
        - test_input: QLineEdit
            Name of the test
            Either a path selected using the `test_btn` button
            or a string that matches `re_StrAllowable` pattern
        - test_btn: QPushButton
            Connects to `set_test_file`
        - exp_input: QLineEdit
            Name of the experiment
            `re_StrAllowable` pattern is checked in `set_up()`
        - test_type_input: QComboBox
            Either "Experiment" or "Calibration"
        - sample_rate_input: QLineEdit
            Sampling rate for NI device (Hz)
            Will only accept floats
        - config_file_edit: QLineEdit
            Select .csv NI Config File.
            The `config_input` button can be used to select a file.
        - config_input: QPushButton
            Connects to `set_config_file()`
        - formulae_file_edit: QLineEdit
            Select an optional .csv formulae file
            to post-process data when dashboard display is selected.

            A corresponding button can be used to select a file.
        - formulae_input: QPushButton
            Connects to `set_formulae_file`
        - acquisition_button: QPushButton
            Connects to `acquisition_begins()`
        - save_button: QPushButton
            Connects to `save_data()`
        - panel: QTextEdit
            Notification panel.
            Placeholder text: "Welcome User!".
            Provides notification of errors/warnings/operations.

            Will be cleared after each `save_button` click
        - log_obs_txt: QLineEdit
            A 25 (width) x 190 (height) for writing observations.
        - notif_log_btn: QPushButton
            Button Text: "Log Obs."
            Connects to `log_Obs()`
        """
        # Input Settings Layout
        self.input_settings_widget = QWidget()
        self.main_input_layout = QHBoxLayout(self.input_tab_widget)
        self.input_layout = QGridLayout()

        # Experimenter's Name
        self.name_label = QLabel("Enter your name:")
        self.name_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setMaximumWidth(200)
        self.name_input.setPlaceholderText("Your name")
        self.input_layout.addWidget(self.name_input, 0, 1)

        # Experimenter's Name
        self.test_label = QLabel("Enter your Test name:")
        self.test_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.test_label, 2, 0)

        self.test_layout = QHBoxLayout()
        self.test_input = QLineEdit()
        self.test_btn = QPushButton("Select")
        self.test_btn.clicked.connect(self.set_test_file)
        self.test_input.setMaximumWidth(150)
        self.test_input.setPlaceholderText("Your Test's name")
        self.test_btn.setMaximumWidth(50)
        self.test_layout.addWidget(self.test_input)
        self.test_layout.addWidget(self.test_btn)
        self.input_layout.addLayout(self.test_layout, 2, 1)

        # Experiment Name
        self.exp_label = QLabel("Enter your Project's name:")
        self.exp_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.exp_label, 1, 0)

        self.exp_input = QLineEdit()
        self.exp_input.setPlaceholderText("Your Project's name")
        self.exp_input.setMaximumWidth(200)
        self.input_layout.addWidget(self.exp_input, 1, 1)

        # Test Name
        self.test_type_label = QLabel("Select Experiment Type:")
        self.test_type_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.test_type_label, 3, 0)

        self.test_type_input = QComboBox()
        self.test_type_input.addItem('Experiment')
        self.test_type_input.addItem('Calibration')
        self.test_type_input.setMaximumWidth(200)
        self.input_layout.addWidget(self.test_type_input, 3, 1)

        # Sampling Rate
        self.sample_rate_label = QLabel("Enter Sampling Rate (Hz):")
        self.sample_rate_label.setToolTip("Will only accept floats")
        self.sample_rate_label.setToolTipDuration(500)
        self.sample_rate_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.sample_rate_label, 4, 0)

        self.sample_rate_input = QLineEdit()
        self.sample_rate_input.setMaximumWidth(200)
        self.sample_rate_input.setPlaceholderText("10")
        reg_ex_1 = QRegularExpression(r"[0-9]*\.[0-9]{0,4}")  # double
        self.sample_rate_input.setValidator(QRegularExpressionValidator(reg_ex_1))  # noqa: E501
        # .setValidator(QRegExpValidator(reg_ex_1))
        self.input_layout.addWidget(self.sample_rate_input, 4, 1)

        # Configuration File Name
        self.config_label = QLabel("Select Configuration File:")
        self.input_layout.addWidget(self.config_label, 5, 0)
        self.config_label.setMaximumWidth(200)

        self.config_file_layout = QHBoxLayout()
        self.config_file_edit = QLineEdit()
        self.config_input = QPushButton("Select")
        self.config_input.clicked.connect(self.set_config_file)
        self.config_input.setMaximumWidth(50)
        self.config_file_edit.setMaximumWidth(150)
        self.config_file_edit.setPlaceholderText("Your Config file")
        self.config_file_layout.addWidget(self.config_file_edit)
        self.config_file_layout.addWidget(self.config_input)
        self.input_layout.addLayout(self.config_file_layout, 5, 1)

        # Formulae File Name
        self.formulae_label = QLabel("Select Formulae File:")
        self.input_layout.addWidget(self.formulae_label, 6, 0)
        self.formulae_label.setMaximumWidth(200)

        self.formulae_file_layout = QHBoxLayout()
        self.formulae_file_edit = QLineEdit()
        self.formulae_input = QPushButton("Select")
        self.formulae_input.clicked.connect(self.set_formulae_file)
        self.formulae_input.setMaximumWidth(50)
        self.formulae_file_edit.setMaximumWidth(150)
        self.formulae_file_edit.setPlaceholderText("Your Formula file")
        self.formulae_file_layout.addWidget(self.formulae_file_edit)
        self.formulae_file_layout.addWidget(self.formulae_input)
        self.input_layout.addLayout(self.formulae_file_layout, 6, 1)

        # Buttons to begin DAQ
        self.acquisition_button = QPushButton("Start Acquisition")
        self.input_layout.addWidget(self.acquisition_button, 7, 0)
        self.acquisition_button.setCheckable(True)
        self.acquisition_button.clicked.connect(self.acquisition_begins)
        self.acquisition_button.setMaximumWidth(200)

        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        self.save_button.setCheckable(True)
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setMaximumWidth(200)
        self.formulae_file = ""
        self.input_layout.addWidget(self.save_button, 7, 1)
        self.save_bool = False

        # Initialize NotificationPanel
        self.notifications_layout = QVBoxLayout()

        # Create dropdown menu for clear and save actions
        self.notif_head = QHBoxLayout()
        self.notif_header = QLabel("Notifications Panel")
        self.notif_header.setMaximumWidth(190)
        self.notif_header.setMaximumHeight(24)
        self.notif_head.addWidget(self.notif_header)# noqa E501
        self.dropdown_button = QPushButton("Options")
        self.dropdown_button.setMaximumWidth(60)
        self.dropdown_button.setMaximumHeight(24)
        self.notif_head.addWidget(self.dropdown_button)
        self.notif_head.addWidget(self.notif_header)
        self.notifications_layout.addLayout(self.notif_head)

        # Panel
        self.panel = NotificationPanel()
        self.panel.setMaximumHeight(375)
        self.panel.setFixedWidth(250)
        self.panel.setAlignment(Qt.AlignRight)
        self.panel.setAlignment(Qt.AlignTop)
        self.notifications_layout.addWidget(self.panel)

        # Create input area
        self.log_area = QHBoxLayout()
        self.log_obs_txt = QLineEdit()
        self.log_obs_txt.setPlaceholderText("Write observations here")
        self.log_area.addWidget(self.log_obs_txt)
        self.notif_log_btn = QPushButton("Log")
        self.notif_log_btn.clicked.connect(self.log_Obs)
        self.log_area.addWidget(self.notif_log_btn)
        self.notifications_layout.addLayout(self.log_area)
        self.notif_log_btn.setMaximumWidth(60)
        self.notif_log_btn.setMaximumHeight(25)
        self.log_obs_txt.setMaximumWidth(190)
        self.log_obs_txt.setMaximumHeight(25)

        self.notifmenu = QMenu()
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.panel.clear)
        self.notifmenu.addAction(clear_action)

        self.dropdown_button.setMenu(self.notifmenu)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_notifs)
        self.notifmenu.addAction(save_action)
        # self.notifmenu.setObjectName("NotifMenu")

        self.main_input_layout.addLayout(self.input_layout)
        self.main_input_layout.addLayout(self.notifications_layout)
        self.data_visualizer_layout = QHBoxLayout()
        self.main_input_layout.addLayout(self.data_visualizer_layout)
        self.input_settings_widget.setLayout(self.main_input_layout)

        return self.input_settings_widget

    def save_notifs(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")  # noqa E501
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.panel.toPlainText())

    def log_Obs(self):
        """Calls `notify` and clears the `notif_txt_edit`
        """
        text = self.log_obs_txt.text()
        if text:
            self.notify(text, type="observation")
            self.log_obs_txt.clear()

    def notify(self, text="", type="default"):
        """Method that logs observations written in `log_obs_txt`
        and adds to the top of the notification panel.

        Any observations written here will be added
        to the notification panel, and a time stamp (format HH:MM:SS)
        at which the "Log Obs." is clicked will be
        appended to the written text.

        Arguments
        _________
            type: str
                Type of event: is one of the folowing
                    "event", "info", "warning", "error", "success", "default"
            str: str
                Any string written in `notif_txt_edit`

        Example
        _______
            If written observation is "Ignition observed"

            Notification text update will be,
                `[13:23:56] Ignition Observed`
        """
        self.panel.add_message(type, text)

    def set_test_file(self):
        """ Method that opens a `SaveSettingsDialog`
        and asks for filename and folder to save the file in.
        """
        dlg_save_file = SaveSettingsDialog("Select File to Save Data")
        self.menu._style_popup(dlg_save_file)
        if dlg_save_file.exec() == QDialog.Accepted:
            self.common_path = dlg_save_file.file_path
            file_pq = self.common_path + ".parquet"
            file_json = self.common_path + ".json"
            folder_pq = dlg_save_file.folder_path
            if os.path.exists(folder_pq):
                if os.path.exists(file_pq) or os.path.exists(file_json):
                    self.inform_user("File to save in already exists.")
                else:
                    self.parquet_file = file_pq
                    self.json_file = file_json
                    self.test_input.setText(self.parquet_file)
        return

    def set_formulae_file(self):
        """ Method that opens a `QFileDialog` to open a
        .csv formulae file
        """
        dlg = QFileDialog(self, 'Select a File', None, "CSV files (*.csv)")
        f = ""
        if dlg.exec():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
        if not isinstance(f, str):
            self.formulae_file = f.name
            self.formulae_file_edit.setText(self.formulae_file)
        return

    def set_config_file(self):
        """ Method that opens a `QFileDialog` to open a
        .csv NI config file
        """
        dlg = QFileDialog(self, 'Select a File', None, "CSV files (*.csv)")
        f = ""
        if dlg.exec():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
        if not isinstance(f, str):
            self.config_file = f.name
            self.config_file_edit.setText(self.config_file)
        return

    def dev_arr_to_dict(self):
        """ Method to store all user-added devices
        in one dictionary to allow saving a global
        configuration for the GUI.
        """
        dict_dev = {}
        if self.lasers:
            dict_dev["Lasers"] = {}
            for laser in self.lasers:
                laser_item = self.lasers[laser]
                dict_dev["Lasers"][laser] = laser_item.settings_to_dict()
        if self.mfcs:
            dict_dev["MFCs"] = {}
            for mfc in self.mfcs:
                mfc_item = self.mfcs[mfc]
                dict_dev["MFCs"][mfc] = mfc_item.settings_to_dict()
        if self.mfms:
            dict_dev["MFMs"] = {}
            for mfm in self.mfms:
                mfm_item = self.mfms[mfm]
                dict_dev["MFMs"][mfm] = mfm_item.settings_to_dict()
        return dict_dev

    def is_valid_path(self, path):
        """ Method that checks if the input path
        is a valid path

        Parameters
        ----------
            path: str
                Path to check for validity

        Returns
        -------
            The return value. True for valid file path. False otherwise.
        """
        try:
            if os.path.isabs(path):
                if os.path.normpath(path):
                    return True
            return False
        except (TypeError, ValueError):
            return False

    def _all_fields_filled(self):
        if (self.name_input.text().strip() == ""
                or self.exp_input.text().strip() == ""
                or self.test_input.text().strip() == ""
                or self.config_file.strip() == ""
                or self.sample_rate_input.text().strip() == ""):
            raise UnfilledFieldError("Unfilled fields encountered.")
        return True

    def validate_df(self, letter, path):
        """Method to check if the config or formulae file path
        provided contains valid columns

        Parameters
        ----------
            letter: str
                Indicating either config ("c") or formulae ("f") file path
            path: str
                path to the indicated file
        Returns
        ------
            The return value.

            True if columns in the file match with columns for each file.
            See details in "Config File Example"
            and "Formulae File Example" for required and
            necessary columns, and how they are used.
        """
        try:
            df = pl.read_csv(path)
            cols = []
        except Exception:
            return False
        if letter == "f":
            cols = ["Label", "RHS", "Chart", "Legend",
                    "Layout", "Position", "Processed_Unit"]
        if letter == "c":
            cols = ["", "Panel", "Device", "Channel",
                    "ScaleMax", "ScaleMin", "Label", "TCType",
                    "Type", "Chart", "AIRangeMin", "AIRangeMax",
                    "Layout", "Position", "Processed_Unit", "Legend"]
        cols.sort()
        df_cols = [i.strip() for i in df.columns]
        df_cols.sort()
        col_intersect = list(set(cols) & set(df_cols))
        # print(col_intersect, " \n", cols, "\n", df_cols)
        if letter == "f":
            if cols == df_cols:
                return True
        elif letter == "c":
            if self.dashboard:
                # todo: Add condition for when display is only tab
                # or display is dashboard, or both
                if len(col_intersect) == len(cols):
                    return True
            else:
                if all(e in col_intersect for e in ["Device", "Channel", "Type", "TCType"]):  # noqa: E501
                    # Allow running acquisition for a minimal config file
                    return True
        return False

    def set_up(self):
        """Method to check NI DAQ setup
        as defined by the user in input settings.

        - First, a check involves if all fields are filled.
        Only Formulae file is optional.

        - Input fields and files selected
        are checked as per requirements
        indicated in `input_content()`.

        - Paths to save all data and NI DAQ settings
        are created via calling
        the method `Create_SavePath()`.
        """
        self._all_fields_filled()

        # Allow only alphunumeric string with underscores in names
        if re.match(self.re_strAllowable, self.name_input.text()) and re.match(self.re_strAllowable, self.exp_input.text()):  # noqa: E501
            self.settings["Name"] = (self.name_input.text())
            self.settings["Experiment Name"] = self.exp_input.text()
        else:
            raise ValueError("Names can only be alphanumeric or contain spaces.")  # noqa: E501

        try:
            sampling_rate = float(self.sample_rate_input.text())
        except ValueError as e:
            raise ValueError("Invalid Sampling Rate") from e
        self.settings["Sampling Rate"] = sampling_rate

        self.settings["Experiment Type"] = self.test_type_input.currentText()

        # Create save path
        self.Create_SavePath()

        if self.formulae_file_edit.text().strip() == "" or self.validate_df("f", self.formulae_file_edit.text()):  # noqa: E501
            self.settings["Formulae File"] = self.formulae_file_edit.text()
            self.formulae_file = self.formulae_file_edit.text()
        else:
            self.inform_user("Formulae File does not meet requirements.")

        if self.validate_df("c", self.config_file_edit.text()):
            self.settings["Config File"] = self.config_file_edit.text()
            self.config_df = pl.read_csv(self.config_file)
            self.config_df.columns = [i.strip() for i in self.config_df.columns]  # noqa: E501
            self.labels_to_save = self.config_df.select("Label").to_series().to_list()  # noqa: E501
        else:
            self.inform_user("Config File does not meet requirements.")
            raise ValueError("Check config file")

        if self.device_arr:
            self.settings["Devices"] = self.dev_arr_to_dict()

    def Create_SavePath(self):
        """Method to create paths to
        save all data, NI settings,
        depending on the test name (`inp_text`).

        - If the user has selected a file to save using
        the `test_btn` generated in `input_content(),
        the filename is checked in the path provided.
        If a filename of that name already exists,
        the filename is appended with `_XX` number,
        that increments by 1 for every repeated
        filename.
            Example: If the filename is `Exp1` in
            directory  `C:/Users/XXX/Tests/`,
            and file by that name exits, the data
            will be saved in the following format.
            `C:/Users/XXX/Tests/Exp1_01`.
            Extensions `.parquet` for NI data,
            `.json` for NI data info, `.csv`
            for Alicat devices will be added to `Exp1_01`.

        - If the user types just a text in `inp_text`,
        a directory and file path to save all data
        is generated in the directory where
        this application is compiled.
            Example: If the `inp_text` is "Test1",
            Experiment type is "Experiment",
            User name is "User",
            Project name is "Project",
            the save path for NI data will be the following.

            "./Experiment/YYYYProject/YYYYMMDD_HHMMSS_User_Project_Test1.parquet".

            `Experiment` directory will be created
            in the current working directory.
            `YYYYProject` directory will be
            created inside `Experiment`.

            The YYYY, MM, DD, HH, MM, SS indicate
            the year, month, date, hour, minute, and seconds
            respectively when the `save_button` is clicked.
        """
        inp_text = self.test_input.text()
        fname = inp_text.split(self.fext)[0]
        fpath = inp_text + self.fext
        if self.is_valid_path(fpath):
            # If the user selected a custom path to save the data
            if os.path.isfile(fpath):
                # If there is already a file by that name
                test_name = f"{fname}"

                files = glob.glob(f"{fname}*{self.fext}")
                if len(files) == 1:  # one previous file
                    # Checking if there is any appended number at the
                    # last 3 characters before extension
                    fnumber = re.findall(r'\d+', files[0].split(self.fext)[0][-3:])  # noqa: E501
                    if not fnumber:
                        # If no number at the end of that file, append `_01`
                        test_name = f"{fname}_01"
                    else:
                        # If there is a number, get the number, increment by 1
                        f_x = str(int(fnumber[0])+1).rjust(2, '0')
                        test_name = f"{fname.split('_'+fnumber[0])[0]}_{f_x}"
                else:
                    # If previous files exits, sort them, get the last one,
                    # and increment the number
                    files = [sorted(files)[-1]]
                    fnumber = re.findall(r'\d+', files[0].split(self.fext)[0][-3:])  # noqa: E501
                    f_x = str(int(fnumber[0])+1).rjust(2, '0')
                    test_name = f"{fname.split('_'+fnumber[0])[0]}_{f_x}"
            else:
                # no previous file
                test_name = fname
        else:
            # If the test name is only the name and the program will create
            # the file path to save
            if re.match(self.re_strAllowable, fname):
                cwd = os.getcwd()
                now = datetime.now()
                self.save_dir = (cwd + os.sep +
                                 self.settings["Experiment Type"] +
                                 os.sep)
                if not os.path.exists(self.save_dir):
                    os.mkdir(self.save_dir)
                self.save_dir = (self.save_dir + now.strftime("%Y%m%d_%H%M%S")
                                 + "_" + self.settings["Name"] + "_" +
                                 self.settings["Experiment Name"] + "_")
                test_name = fname
            else:
                raise ValueError("""Check test name. It should be either a\
                                 valid path or a test name that can only\
                                 contain alphanumeric or\
                                 contain underscores (no spaces).""")

        self.json_file = test_name + ".json"
        self.parquet_file = test_name + ".parquet"
        if self.is_valid_path(inp_text):
            self.settings["Test Name"] = self.parquet_file
        else:
            self.settings["Test Name"] = self.save_dir + self.parquet_file
        self.common_path = test_name
        self.test_input.setText(test_name)

    def settings_to_json(self):
        """Method to save all NI input fields
        and devices added by the user is saved in a
        .json file in a location of user's choice.

        These settings can be loaded later.
        """
        self._all_fields_filled()
        self.settings["Experiment Type"] = self.test_type_input.currentText()
        try:
            sampling_rate = int(self.sample_rate_input.text())
        except ValueError as e:
            raise ValueError("Invalid Sampling Rate") from e
        self.settings["Sampling Rate"] = sampling_rate
        if (all(c.isalnum() or c == "_" for c in self.name_input.text()) and
                all(c.isalnum() or c == "_" for c in self.exp_input.text())):
            self.settings["Name"] = (self.name_input.text())
            self.settings["Experiment Name"] = self.exp_input.text()
        self.settings["Test Name"] = self.test_input.text()
        self.settings["Formulae File"] = self.formulae_file_edit.text()
        self.settings["Config File"] = self.config_file_edit.text()
        if self.device_arr:
            self.settings["Devices"] = self.dev_arr_to_dict()
        json_string = json.dumps(self.settings, indent=4)
        return json_string

    def _set_texts(self):
        # Is called when main menu .json file is loaded.
        # Called in repopulate_settings.
        self.exp_input.setText(self.settings["Experiment Name"])
        self.name_input.setText(self.settings["Name"])
        self.test_input.setText(self.settings["Test Name"])
        self.save_dir = os.path.dirname(self.settings["Test Name"])
        self.common_path = self.settings["Test Name"].split(".parquet")[0]
        self.sample_rate_input.setText(str(self.settings["Sampling Rate"]))
        self.formulae_file = self.settings["Formulae File"]
        self.formulae_file_edit.setText(self.settings["Formulae File"])
        self.test_type_input.setCurrentText(self.settings["Experiment Type"])
        self.config_file = self.settings["Config File"]
        self.config_file_edit.setText(self.settings["Config File"])
        firepydaq_logger.info(__name__ + ": Config texts updated.")

    def inform_user(self, err_txt):
        """Method to inform important
        operations, errors, and warnings
        to the user using a pop-up QMessageBox.
        """
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Error Encountered")
        self.msg.setText(err_txt)
        if self.curr_mode == "Dark":
            f = open(self.popup_dark, "r")
        else:
            f = open(self.popup_light, "r")
        str = f.read()
        self.msg.setStyleSheet(str)
        f.close()
        self.msg.exec()

    def validate_fields(self):
        """Method to validate if the config
        and the formulae file path would be used
        without errors during post processing.

        This is done by creating a random data DataFrame.
        The DataFrame columns correspond to the `Label` column
        in the config file.
        The values corresponding to each `Label` is
        populated with a random integer between 0 and 10.

        The random data DataFrame, config file path, and formulae path
        are supplied to PostProcessData for checking if
        the random DataFrame (simulating collected data)
        can be scaled and post processed without any errors.
        """
        self.set_up()
        if self.display and self.tab and hasattr(self, "data_vis_tab"):
            self.data_vis_tab.set_labels(self.config_file)
        config_df = pl.read_csv(self.settings["Config File"])
        random_input = np.array([np.random.randint(0, 10)*i for i in np.ones(config_df.select("Label").shape)])  # noqa: E501
        random_dict = {i: random_input[n] for n, i in enumerate(self.labels_to_save)}  # noqa: E501
        random_df = pl.DataFrame(data=random_dict)
        CheckPP = PostProcessData(datapath=random_df, configpath=self.settings['Config File'], formulaepath=self.settings['Formulae File'])  # noqa: E501
        CheckPP.ScaleData()
        CheckPP.UpdateData(dump_output=False)

    def initiate_dataArrays(self):
        """A method to initiate empty numpy data array for
        storing NI data during acquisition.

        If the number of Analog Inputs (AI)
        in the config file is 1,
        an empty `ydata` numpy array of shape (1,) is created.

        If the number of AIs are greater than one (example 4),
        an empty `ydata` numpy array of shape (4,) is created

        If there are both AIs and Analog Outputs (AO)
        in the config file, empty `ydata` array with
        shape equal to total AI (say 3) and AOs (say 1),
        (4,) is created.

        An empty `xdata` array of shape (1,)
        for storing relative times
        is created with a single element `0`.

        An empty 1D numpy array of name `abs_timestamp`
        is created to store corresponding
        absolute times during acquisition.
        """
        if self.NIDAQ_Device.ai_counter > 0:
            if len(self.NIDAQ_Device.ailabel_map) == 1:
                self.ydata = np.empty(0)
            else:
                self.ydata = np.empty((len(self.NIDAQ_Device.ailabel_map), 0))
        else:  # Todo: check for bugs with AO module
            self.ydata = np.empty((len(self.settings["Label"]), 0))
        if self.mfcs != {}:
            self.all_mfcData = {}
            for mfcname in self.mfcs:
                self.all_mfcData[mfcname] = pl.DataFrame()
        self.xdata = np.array([0])
        self.abs_timestamp = np.array([])
        self.timing_np = np.empty((0, 3))

    def acquisition_begins(self):
        """Method to begin acquisition for all devices.

        The following methods are called in order.
        1. `validate_fields()`.
        2. `CreateDAQTask()` in `api` module to create
        AI and AO continuous tasks. (See `api` module for details)
        3. `initiate_dataArrays()`

        Once these run without any issues, the `save_button`
        is enabled, `ContinueAcquisition` boolean is set to True,



        """
        # todo: Disable config, formulae, and sampling rate after acq begins.
        # Only allow name changes after acq begins.
        # todo: regarding notification panel: save option pop up
        # after acq stops
        # todo: if the dropdown is possible on notification panel,
        # create a clear notification panel option.
        if self.acquisition_button.isChecked():
            try:
                self.validate_fields()
            except Exception as e:
                self.inform_user(str(e))
                self.notify("Validation of input fields failed.", "error")
                self.acquisition_button.nextCheckState()
                return
            self.run_counter = 0
            if hasattr(self, 'NIDAQ_Device'):
                self.NIDAQ_Device.aitask.stop()
                self.NIDAQ_Device.aitask.close()
                if hasattr(self.NIDAQ_Device, "aotask"):
                    self.input_tab_widget.removeTab(1)
                    self.NIDAQ_Device.aotask.stop()
                    self.NIDAQ_Device.aotask.close()
                del self.NIDAQ_Device

            try:
                self.NIDAQ_Device = CreateDAQTask(self, "NI Task")
                self.NIDAQ_Device.CreateFromConfig(self.settings["Config File"])  # noqa: E501

                if self.NIDAQ_Device.ai_counter > 0:
                    sample_rate = int(self.settings["Sampling Rate"])
                    self.NIDAQ_Device.StartAIContinuousTask(sample_rate, sample_rate)  # noqa: E501
                if self.NIDAQ_Device.ao_counter > 0:
                    self.niaotab = NIAOtab(self, self.NIDAQ_Device.aolabel_map)
                    AO_initials = np.array([0 for i in self.NIDAQ_Device.aolabel_map.keys()], dtype=np.float64)  # noqa: E501
                    self.NIDAQ_Device.StartAOContinuousTask(AO_initials=AO_initials)  # noqa: E501
            except Exception:
                # todo: Parse NI errors properly.. sampling rate? device name? config file error? # noqa: E501
                self.acquisition_button.nextCheckState()
                type, value, tb = sys.exc_info()
                print(type, value, traceback.print_tb(tb))
                self.inform_user("Terminating acquisition due to DAQ Connection Errors\n " + str(type) + str(value))  # noqa: E501
                return

            if self.mfcs != {}:
                all_connected = []
                for mfcname in self.mfcs:
                    all_connected.append(hasattr(self.mfcs[mfcname], "loop"))
                try:
                    if not all(all_connected):
                        raise ConnectionError("All MFC connections must be established before aquisition.")  # noqa E501
                except Exception as e:
                    self.acquisition_button.nextCheckState()
                    self.inform_user(str(e))
                    return

            self.initiate_dataArrays()
            self.ContinueAcquisition = True
            self.save_button.setEnabled(True)
            self.acquisition_button.setText("Stop Acquisition")
            self.notify("Validation complete. Acquisition begins.", "info")
            self.runpyDAQ()
            self.notify("Acquiring Data . . .", "info")
        else:
            self.ContinueAcquisition = False
            time.sleep(1)
            self.save_bool = False
            self.run_counter = 0
            self.save_button.setEnabled(False)
            self.notify("Acquisition stopped.", "info")
            self.acquisition_button.setText("Start Acquisition")

    def save_data_thread(self):
        """Method that saves acquired NI data in a
        `.parquet` file in path created as per `CreateSavePath()`.
        """
        time_data = np.array(self.xdata_new)
        abs_time = np.array(self.abs_timestamp)
        time_data = time_data[np.newaxis, :]
        abs_time = abs_time[np.newaxis, :]
        ydata_new = self._queue.get(block=True, timeout=1)

        if len(ydata_new.shape) == 1:
            # If a single channel, a list is returned by nidaqmx
            ydata_new = ydata_new[np.newaxis, :]
        temp_data = np.append(time_data, np.array(ydata_new), axis=0)

        temp_data = np.append(abs_time, temp_data, axis=0)
        save_dataframe = pl.DataFrame(schema=self.pl_schema_dict, data=temp_data, orient='col')  # noqa: E501
        self.parquet_file = self.common_path + ".parquet"

        try:
            if os.path.isfile(self.parquet_file):
                table = pq.read_table(self.parquet_file)
                old_pq = pl.from_arrow(table)
                new_df = pl.concat([old_pq, save_dataframe])
            else:
                new_df = save_dataframe
            new_df.write_parquet(self.parquet_file)

            if self.mfcs != {}:
                for mfcname, data in self.all_mfcData.items():
                    MFC_filename = self.parquet_file.split(".parquet")[0] + '_' + mfcname + '.csv'  # noqa E501
                    data_df = pd.DataFrame(data, index=[self.xdata_new[0]])
                    data_df.to_csv(MFC_filename, mode="a", header=not os.path.isfile(MFC_filename))  # noqa E501

        except Exception as e:
            self.notify(str(e), "error")
            self.notify("Error during saving operation", "error")
        return

    def runpyDAQ(self):
        '''Method that continuously runs the Data acquisition system
        until "Stop Acquisition" is clicked.

        '''
        # AO debug in process
        no_samples = self.NIDAQ_Device.numberOfSamples
        self.ActualSamplingRate = self.NIDAQ_Device.aitask.timing.samp_clk_rate  # noqa E501
        samplesAvailable = self.NIDAQ_Device.aitask._in_stream.avail_samp_per_chan  # noqa: E501
        if self.mfcs != {}:
            self.alicat_locks = {}
            for mfcname, al_mfc in self.mfcs.items():
                # Lock Alicat thread for release only
                # when NI data is available
                self.alicat_locks[mfcname] = threading.Lock()
                self.alicat_locks[mfcname].acquire()
                self.all_mfcData[mfcname] = al_mfc.GetFlows()

        if (samplesAvailable >= no_samples):
            try:
                t_bef_read = time.time()
                # parallels_bef = time.time()
                # Executor waits for the threads to complete their task.
                # Pauses other buttons or creates delays.
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Threading AI, AO , and Device tasks
                    aithread = executor.submit(self.NIDAQ_Device.threadaitask)
                    self.ydata_new = aithread.result()
                    self.ydata_new = np.array(self.ydata_new)
                    if self.NIDAQ_Device.ao_counter > 0:
                        AO_outputs = [0 for i in range(self.NIDAQ_Device.ao_counter)]  # noqa: E501
                        # AO_outputs will need user iniput.
                        # Currently only float values are accepted.
                        aothread = executor.submit(self.NIDAQ_Device.threadaotask, AO_initials=AO_outputs)  # noqa: E501
                        self.written_data = aothread.result()

                if self.mfcs != {}:
                    for mfcname, _ in self.mfcs.items():
                        # Release alicat threads once the data is acquired.
                        self.alicat_locks[mfcname].release()
                # self.alicat_locks[mfcname].acquire()
                t_aft_read = time.time()
                t_now = datetime.now()

                if (t_aft_read-t_bef_read) > 1/self.ActualSamplingRate:
                    # Read time exceeds prescribed 1/(sampling frequency)
                    self.notify("Data Loss WARNING: Time to read exceeds number of samples per seconds prescribed for acquisition.", "warning")  # noqa: E501

                if len(self.ydata.shape) == 1:
                    self.ydata = np.append(self.ydata, self.ydata_new, axis=0)
                else:
                    self.ydata = np.append(self.ydata, self.ydata_new, axis=1)
                t_diff = no_samples/self.ActualSamplingRate
                tdiff_array = np.linspace(1/self.ActualSamplingRate, t_diff, no_samples)  # noqa: E501
                if self.xdata[-1] == 0:
                    self.xdata_new = np.linspace(self.xdata[-1], self.xdata[-1] + t_diff, no_samples, endpoint=False)  # noqa: E501
                    if len(self.ydata.shape) == 1 and len(self.xdata_new) == 1:  # noqa: E501
                        # For 1 Hz sampling frequency
                        self.xdata_new = [no_samples/self.ActualSamplingRate]
                    self.xdata = self.xdata_new
                    self.abs_timestamp = [(t_now+timedelta(seconds=sec)).strftime(self.dt_format) for sec in tdiff_array]  # noqa: E501
                else:
                    self.xdata_new = np.linspace(self.xdata[-1]+1/self.ActualSamplingRate, self.xdata[-1]+t_diff, no_samples)  # noqa: E501
                    self.abs_timestamp = [(t_now+timedelta(seconds=sec)).strftime(self.dt_format) for sec in tdiff_array]  # noqa: E501
                    self.xdata = np.append(self.xdata, self.xdata_new)

                if self.save_bool:
                    self._queue.put(self.ydata_new, block=True, timeout=1)
                    # As long as save does not take more than 1 s,
                    # there should be no conflict with acquisition.
                    save_thread = threading.Thread(target=self.save_data_thread)  # noqa E501
                    save_thread.start()

                t_aft_save = time.time()
                if (t_aft_save - t_bef_read) > 1/self.ActualSamplingRate:
                    # Time between read and save time exceeds
                    # prescribed 1/(sampling frequency)
                    self.notify("Data Loss WARNING: Time to save exceeds number of samples per seconds prescribed for acquisition.", "warning")  # noqa: E501

                # Plots
                if hasattr(self, "data_vis_tab"):
                    if not hasattr(self.data_vis_tab, "dev_edit"):
                        self.data_vis_tab.set_labels(self.config_file)
                    self.vis_lock = threading.Lock()
                    self.vis_lock.acquire(timeout=0.5)
                    if len(self.ydata.shape) == 1:
                        self.data_vis_tab.set_data_and_plot(self.xdata, self.ydata)  # noqa: E501
                    else:
                        self.data_vis_tab.set_data_and_plot(self.xdata, self.ydata[self.data_vis_tab.get_curr_selection()])  # noqa: E501

                if (self.xdata[-1] % 5) <= 1/self.ActualSamplingRate:
                    text_update = ("Last time entry:" +
                                   str(round(self.xdata[-1], 2)) +
                                   ", Total samples/chan:" +
                                   str(self.NIDAQ_Device.aitask.in_stream.total_samp_per_chan_acquired) +  # noqa: E501
                                   ",\n Actual Hz:" +
                                   str(round(self.NIDAQ_Device.aitask.timing.samp_clk_rate, 2)))  # noqa: E501
                    self.notify(text_update)
            except Exception:
                the_type, the_value, the_traceback = sys.exc_info()
                self.ContinueAcquisition = False
                # print(the_type, the_value, the_traceback)
                self.inform_user(str(the_type) + str(the_value))
                traceback.print_tb(the_traceback)  # noqa: E501

        if self.ContinueAcquisition and self.running:
            QTimer.singleShot(1, self.runpyDAQ)
        else:
            self.run_counter = 0
            self.notify("Acquisition stopped.", "info")
            self.acquisition_button.setText("Start Acquisition")
            self.save_button.setEnabled(False)
            if hasattr(self, "dash_thread"):
                self.dash_thread.terminate()
                self.notify("Dashboard closed.", "info")

    @error_logger("SaveData")
    def save_data(self):
        """Method that initiates data arrays
        """
        if self.save_button.isChecked():
            self.save_button.setText("Stop")
            self.save_bool = True
            self.run_counter = 0
            self._queue = queue.Queue(maxsize=0)  # infinite queue size

            # This will call Create_save path also based on updated fields.
            self.set_up()
            if not self.is_valid_path(self.json_file):
                self.json_file = self.save_dir+self.json_file
            with open(self.json_file, "x") as outfile:
                outfile.write(json.dumps(self.settings, indent=4))

            if not self.is_valid_path(self.common_path):
                self.common_path = self.save_dir + self.common_path
            assert self.is_valid_path(self.common_path)

            self.initiate_dataArrays()
            firepydaq_logger.info("Saving initiated properly.")
            self.save_begin_time = time.time()
            self.notify("Saving Data in " + self.settings["Test Name"], "info")

            pl_cols = self.labels_to_save
            pl_cols.insert(0, "Time")
            pl_cols.insert(0, "AbsoluteTime")
            self.pl_schema_dict = {}
            for col in pl_cols:
                if 'AbsoluteTime' not in col:
                    self.pl_schema_dict[col] = pl.Float32
                else:
                    self.pl_schema_dict[col] = pl.String
            print(self.pl_schema_dict)

            if self.dashboard:
                firepydaq_logger.info("Dash app Process initiated after saving initiations")  # noqa: E501
                self.notify("Launching Dashboard on https://127.0.0.1:1222", "info")  # noqa E501
                mp.freeze_support()
                self.dash_thread = mp.Process(target=create_dash_app, kwargs={"jsonpath": self.json_file})  # noqa: E501
                self.dash_thread.start()
        else:
            self.save_button.setText("Save")
            self.notify("Saving Stopped", "info")
            if hasattr(self, "dash_thread"):
                self.dash_thread.terminate()
            self.save_bool = False

    def safe_exit(self):
        """Method that stops and closes NI AI and AO tasks.
        """
        if hasattr(self, 'NIDAQ_Device'):
            self.NIDAQ_Device.aitask.stop()
            self.NIDAQ_Device.aitask.close()
            if hasattr(self.NIDAQ_Device, "aotask"):
                self.NIDAQ_Device.aotask.stop()
                self.NIDAQ_Device.aotask.close()
            del self.NIDAQ_Device
        self.close()

    def closeEvent(self, *args, **kwargs):
        """Method that gracefully closes the GUI

        In the following order:
        - Terminates the dash thread if it is running
        - Closes AITask
        - Closes AOTask
        - Closes Connection to Other devices
        - Closes the GUI.
        """
        self.running = False
        time.sleep(1)
        if hasattr(self, "dash_thread"):
            self.dash_thread.terminate()
        if hasattr(self, 'NIDAQ_Device'):
            if hasattr(self.NIDAQ_Device, 'aitask'):
                self.NIDAQ_Device.aitask.stop()
                self.NIDAQ_Device.aitask.close()
                if hasattr(self.NIDAQ_Device, "aotask"):
                    self.NIDAQ_Device.aotask.stop()
                    self.NIDAQ_Device.aotask.close()
                del self.NIDAQ_Device
        super(QMainWindow, self).closeEvent(*args, **kwargs)
