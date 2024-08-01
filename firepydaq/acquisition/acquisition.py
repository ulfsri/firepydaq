"""
General imports 
"""
import sys
# PyQT Related
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QDialog, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QFileDialog, QScrollArea
from .save_setting_to_json_dialog import SaveSettingsDialog
import pyqtgraph as pg
from .main_menu import MyMenu
import threading
from .device import alicat_mfc
import json
from .display_data_tab import data_vis
from ..dashboard.app import create_dash_app
import time
import concurrent.futures
import multiprocessing as mp
from datetime import datetime,timedelta
import polars as pl
import pandas as pd
import numpy as np
import traceback
import pyarrow.parquet as pq
import pyarrow as pa
import glob
import re
import os

from .exception_list import UnfilledFieldError
from ..api.CreateNIDAQTask import CreateDAQTask

from ..utilities.PostProcessing import PostProcessData

#Logger
from ..utilities.ErrorUtils import error_logger, firepydaq_logger

#All commented out code is to be removed later

class application(QMainWindow):

    def __init__(self):
         
        super().__init__()
        # Set window properties
        self.setGeometry(0, 0, 900, 600)
        self.setFixedSize(900, 600)
        self.setWindowTitle("Facilitated Interface for Recording Experiments (FIRE)") 
        self.menu = MyMenu(self)
        self.setMenuBar(self.menu)

        self.setWindowIcon(QIcon('assets/fsri-logo.ico'))
        
        # Create main widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)
        self.initialise_tabs()

        self.main_layout.setStretch(0, 2.5)
        self.main_layout.setStretch(1, 1.5)

        #array holding all device objects 
        self.device_arr = {}
        self.settings = {}
        self.lasers = {}
        self.mfms = {}
        self.mfcs = {}
        self.running = True
        self.labels_to_save = []
        self.acquiring_data = False 
        self.display = False
        self.tab = False
        self.dashboard = False

    def initialise_tabs(self):
        self.input_tab_widget = QTabWidget()
        self.input_tab_content = self.input_content()
        self.input_tab_widget.addTab(self.input_tab_content, "Input Settings")
        self.main_layout.addWidget(self.input_tab_widget)

    def input_content(self):
        #Input Settings Layout
        self.input_settings_widget = QWidget()
        self.main_input_layout = QHBoxLayout(self.input_tab_widget)
        self.input_layout = QGridLayout()

        #Experimenter's Name
        self.name_label = QLabel("Enter your name:")
        self.name_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setMaximumWidth(200)
        self.name_input.setPlaceholderText("Your name")
        self.input_layout.addWidget(self.name_input, 0, 1)

        #Experimenter's Name
        self.test_label = QLabel("Enter your Test name:")
        self.test_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.test_label, 2, 0)

        self.test_layout = QHBoxLayout()
        self.test_input = QLineEdit()
        self.test_btn = QPushButton("Select")
        self.test_btn.clicked.connect(self.set_test_file)
        self.test_input.setMaximumWidth(150)
        self.test_btn.setMaximumWidth(50)
        self.test_layout.addWidget(self.test_input)
        self.test_layout.addWidget(self.test_btn)
        self.input_layout.addLayout(self.test_layout, 2, 1)

        #Experiment Name
        self.exp_label = QLabel("Enter your Project's name:")
        self.exp_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.exp_label, 1, 0)

        self.exp_input = QLineEdit()
        self.exp_input.setPlaceholderText("Enter your Project's name")
        self.exp_input.setMaximumWidth(200)
        self.input_layout.addWidget(self.exp_input, 1, 1)

        #Test Name
        self.test_type_label = QLabel("Select Experiment Type:")
        self.test_type_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.test_type_label, 3, 0)

        self.test_type_input = QComboBox()
        self.test_type_input.addItem('Experiment')
        self.test_type_input.addItem('Calibration')
        self.test_type_input.setMaximumWidth(200)
        self.input_layout.addWidget(self.test_type_input, 3, 1)

        #Sampling Rate
        self.sample_rate_label = QLabel("Enter Sampling Rate:")
        self.sample_rate_label.setMaximumWidth(200)
        self.input_layout.addWidget(self.sample_rate_label, 4, 0)
    
        self.sample_rate_input = QLineEdit()
        self.sample_rate_input.setMaximumWidth(200)
        self.sample_rate_input.setPlaceholderText("10 datapoints per second")
        self.input_layout.addWidget(self.sample_rate_input, 4, 1)

        #Configuration File Name
        self.config_label = QLabel("Select Configuration File:")
        self.input_layout.addWidget(self.config_label, 5, 0)
        self.config_label.setMaximumWidth(200)

        self.config_file_layout = QHBoxLayout()
        self.config_file_edit = QLineEdit()
        self.config_input = QPushButton("Select")
        self.config_input.clicked.connect(self.set_config_file)
        self.config_input.setMaximumWidth(50)
        self.config_file_edit.setMaximumWidth(150)
        self.config_file_layout.addWidget(self.config_file_edit)
        self.config_file_layout.addWidget(self.config_input)
        self.input_layout.addLayout(self.config_file_layout, 5, 1)

        #Formulae File Name
        self.formulae_label = QLabel("Select Formulae File:")
        self.input_layout.addWidget(self.formulae_label, 6, 0)
        self.formulae_label.setMaximumWidth(200)

        self.formulae_file_layout = QHBoxLayout()
        self.formulae_file_edit = QLineEdit()
        self.formulae_input = QPushButton("Select")
        self.formulae_input.clicked.connect(self.set_formulae_file)
        self.formulae_input.setMaximumWidth(50)
        self.formulae_file_edit.setMaximumWidth(150)
        self.formulae_file_layout.addWidget(self.formulae_file_edit)
        self.formulae_file_layout.addWidget(self.formulae_input)
        self.input_layout.addLayout(self.formulae_file_layout, 6, 1)
        
        #Buttons to begin DAQ
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

        self.notifications_layout = QVBoxLayout()
        self.notif_bar = QScrollArea()
        self.notif_bar.setWidgetResizable(True)
        self.notif_bar.setMaximumHeight(375)
        self.notif_bar.setFixedWidth(250)
        self.notif_bar.setAlignment(Qt.AlignRight)
        self.notif_bar.setAlignment(Qt.AlignTop)
        self.notif_text_slot = QLabel("Welcome User!")
        self.notif_text_slot.setAlignment(Qt.AlignTop)
        self.notif_bar.setWidget(self.notif_text_slot)
        self.notifications_layout.addWidget(self.notif_bar)

        self.notif_save_layout = QHBoxLayout()
        self.notif_save_edit = QLineEdit()
        self.notif_save_btn = QPushButton("Save")
        self.notif_save_btn.clicked.connect(self.print)
        self.notif_save_btn.setMaximumWidth(50)
        self.notif_save_btn.setMaximumHeight(25)
        self.notif_save_edit.setMaximumWidth(200)
        self.notif_save_edit.setMaximumHeight(25)
        self.notif_save_layout.addWidget(self.notif_save_edit)
        self.notif_save_layout.addWidget(self.notif_save_btn)
        self.notifications_layout.addLayout(self.notif_save_layout)
        
        self.main_input_layout.addLayout(self.input_layout)
        self.main_input_layout.addLayout(self.notifications_layout)
        self.data_visualizer_layout = QHBoxLayout()
        self.main_input_layout.addLayout(self.data_visualizer_layout)
        self.input_settings_widget.setLayout(self.main_input_layout)

        return self.input_settings_widget
    
    def print(self):
        self.notify(self.notif_save_edit.text())
        self.notif_save_edit.clear()
    
    def set_test_file(self):
        dlg_save_file = SaveSettingsDialog("Select File to Save Data")
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
    
    def notify(self, str):
        line = self.notif_text_slot.text()
        str_time = time.strftime("%X")
        new_txt = line + "\n" + "[" + str_time + "]: " + str
        self.notif_text_slot.setText(new_txt)
    
    def dev_arr_to_dict(self):
        dict_dev =  {}
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
        try:
            if os.path.isabs(path):
                if os.path.normpath(path):
                    return True
            return False
        except(TypeError, ValueError):
            return False
        
    def set_up(self):
        self.notify("Validating data . . .")
        self.all_fields_filled()
        self.settings["Experiment Type"] = self.test_type_input.currentText()

        try:
            sampling_rate = int(self.sample_rate_input.text())
        except ValueError as e:
            raise ValueError("Invalid Sampling Rate") from e
        self.settings["Sampling Rate"] = sampling_rate

        if (all(c.isalnum() or c == "_" for c in self.name_input.text()) 
            and all(c.isalnum() or c == "_" for c in self.exp_input.text())):
            self.settings["Name"] = (self.name_input.text())
            self.settings["Experiment Name"] = self.exp_input.text()
        else:
            raise ValueError("Names can only be alphanumeric or contain spaces.")

        if self.is_valid_path(self.test_input.text()):
            if os.path.isfile(self.test_input.text()):
                file_name = f"{self.common_path}"
                counter = 1
                while os.path.isfile(file_name + ".json") or os.path.isfile(file_name + ".parquet"):
                    file_name = f"{self.common_path}_{counter}"
                    counter = counter + 1  
                self.json_file = file_name + ".json"
                self.parquet_file = file_name + ".parquet"
                self.settings["Test Name"] = self.parquet_file
                self.common_path = file_name
                self.test_input.setText(self.parquet_file)
            else:
                self.settings["Test Name"] = self.test_input.text()
                self.common_path = self.settings["Test Name"].split(".parquet")[0]
                self.parquet_file = self.settings["Test Name"] 
                self.json_file = self.common_path + ".json"
        else:
            if (all(c.isalnum() or c == "_" for c in self.test_input.text())):
                cwd = os.getcwd()
                now = datetime.now()
                self.save_dir = cwd + os.sep + self.settings["Experiment Type"]
                self.common_path = self.save_dir + os.sep + now.strftime("%Y%m%d_%H%M") + "_" + self.settings["Name"] + "_" + self.settings["Experiment Name"] + "_" + self.test_input.text()
                self.settings["Test Name"] = (self.common_path + ".parquet")
                self.json_file = self.common_path + ".json"
                self.parquet_file = self.settings["Test Name"]
                self.test_input.setText(self.settings["Test Name"])
            else:
                raise ValueError("Names can only be alphanumeric or contain underscores.")       

        if self.formulae_file_edit.text().strip() == "" or self.validate_df("f", self.formulae_file_edit.text()):
            self.settings["Formulae File"] = self.formulae_file_edit.text()
            self.formulae_file = self.formulae_file_edit.text()
        else:
            self.inform_user("Formulae File does not meet requirements.")

        if self.validate_df("c", self.config_file_edit.text()):
            self.settings["Config File"] = self.config_file_edit.text()
            self.config_df = pl.read_csv(self.config_file)
            self.labels_to_save = self.config_df.select("Label").to_series().to_list()
        else:
            self.inform_user("Config File does not meet requirements.")

        if self.device_arr:
            self.settings["Devices"] = self.dev_arr_to_dict()


    def settings_to_json(self):
        self.all_fields_filled()
        self.settings["Experiment Type"] = self.test_type_input.currentText()
        try:
            sampling_rate = int(self.sample_rate_input.text())
        except ValueError as e:
            raise ValueError("Invalid Sampling Rate") from e
        self.settings["Sampling Rate"] = sampling_rate
        if (all(c.isalnum() or c == "_" for c in self.name_input.text()) 
            and all(c.isalnum() or c == "_" for c in self.exp_input.text())):
            self.settings["Name"] = (self.name_input.text())
            self.settings["Experiment Name"] = self.exp_input.text()
        self.settings["Test Name"] = self.test_input.text()
        self.settings["Formulae File"] = self.formulae_file_edit.text()
        self.settings["Config File"] = self.config_file_edit.text()
        if self.device_arr:
            self.settings["Devices"] = self.dev_arr_to_dict()
        json_string = json.dumps(self.settings, indent=4) 
        return json_string
    
    def set_texts(self):
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
        msg = QMessageBox()
        msg.setWindowTitle("Error Encountered")
        msg.setText(err_txt)
        msg.exec()

    def validate_fields(self):
        self.set_up()
        if self.display and self.tab and hasattr(self, "data_vis_tab"):
            self.data_vis_tab.set_labels(self.config_file)
        config_df = pl.read_csv(self.settings["Config File"])
        random_input = np.array([np.random.randint(0,10)*i for i in np.ones(config_df.select("Label").shape)])
        random_dict = {i : random_input[n] for n,i in enumerate(self.labels_to_save)}
        random_df = pl.DataFrame(data=random_dict)
        CheckPP = PostProcessData(datapath = random_df, configpath = self.settings['Config File'], formulaepath = self.settings['Formulae File'])
        CheckPP.ScaleData()
        CheckPP.UpdateData(dump_output=False)

    def initiate_dataArrays(self):
        
        if self.NIDAQ_Device.ai_counter>0:
            self.ydata=np.empty((len(self.NIDAQ_Device.ailabel_map),0))
        else: # To check for bugs
            self.ydata = np.empty((len(self.settings["Label"]),0))
        
        self.xdata=np.array([0])
        self.abs_timestamp= np.array([])
        self.timing_np = np.empty((0,3))

    def acquisition_begins(self):
        if self.acquisition_button.isChecked():
            try:
                self.validate_fields()
                self.save_button.setEnabled(True)
                self.acquisition_button.setText("Stop Acquisition")
            except Exception as e:
                self.inform_user(str(e))
                self.notify("Validation failed.")
                return 
        
            self.run_counter = 0
        
            if hasattr(self,'NIDAQ_Device'):
                self.NIDAQ_Device.aitask.stop()
                self.NIDAQ_Device.aitask.close()
                if hasattr(self.NIDAQ_Device,"aotask"):
                    self.NIDAQ_Device.aotask.stop()
                    self.NIDAQ_Device.aotask.close()
                del self.NIDAQ_Device

            try:
                self.NIDAQ_Device = CreateDAQTask(self,"NI Task")
                self.NIDAQ_Device.CreateFromConfig()
            except Exception as e:
                self.inform_user("Terminating acquisition due to DAQ Connection Errors")
                return
            
            if self.NIDAQ_Device.ai_counter > 0:
                sample_rate = int(self.settings["Sampling Rate"])
                self.NIDAQ_Device.StartAIContinuousTask(sample_rate, sample_rate)
            if self.NIDAQ_Device.ao_counter > 0:
                AO_initials = [0 for i in self.NIDAQ_Device.ao_counter]
                self.NIDAQ_Device.StartAOContinuousTask(AO_initials = AO_initials)
            self.initiate_dataArrays()
            self.ContinueAcquisition = True
            self.notify("Validation complete. Acquisition begins.")
            self.runpyDAQ()
            self.notify("Acquiring Data . . .")
        else:
            self.ContinueAcquisition = False
            time.sleep(1)
            self.save_bool = False
            self.run_counter = 0
            self.save_button.setEnabled(False)
            self.notify("Acquisition stopped.")
            self.acquisition_button.setText("Start Acquisition")
    
    def save_data_thread(self):
        time_data = np.array(self.xdata_new)
        time_data = time_data[np.newaxis,:]
        abs_time = np.array(self.abs_timestamp)
        abs_time = abs_time[np.newaxis,:]
        temp_data = np.append(time_data, np.array(self.ydata_new), axis=0)
        temp_data = np.append(abs_time, temp_data, axis=0).T 
        print(self.labels_to_save)
        pl_cols = np.insert(self.labels_to_save, 0, "Time")
        pl_cols = np.insert(pl_cols, 0, "AbsoluteTime")
        pl_list = pl_cols.tolist()
        self.save_dataframe = pl.DataFrame(schema = pl_list, data = temp_data)
        
        self.parquet_file = self.common_path + ".parquet"

        try:
            if os.path.isfile(self.parquet_file):
                table = pq.read_table(self.parquet_file)
                old_pq = pl.from_arrow(table)
                new_df = pl.concat([old_pq, self.save_dataframe])
            else:
                new_df = self.save_dataframe

            new_df.write_parquet(self.parquet_file)
        except:
            pass
        return

    def runpyDAQ(self):
        '''
        Method that runs the Data acquisition system
        
        '''
        # Will only work for AI. Add functionality for AO only 
        # if self.save_button.isChecked(): 
        # # Condition for saving TDMS
        self.run_counter += 1
        no_samples = self.NIDAQ_Device.numberOfSamples
        self.ActualSamplingRate = self.NIDAQ_Device.aitask.timing.samp_clk_rate
        samplesAvailable = self.NIDAQ_Device.aitask._in_stream.avail_samp_per_chan

        if(samplesAvailable >= no_samples):
            try:
                t_bef_read = time.time() 
                parallels_bef = time.time()
                with concurrent.futures.ThreadPoolExecutor() as executor: # threading input and output tasks
                    aithread = executor.submit(self.NIDAQ_Device.threadaitask)
                    par_ai = time.time()
                    self.ydata_new = aithread.result()
                    self.ydata_new = np.array(self.ydata_new)
                    if self.NIDAQ_Device.ao_counter> 0:
                        AO_outputs = [0 for i in range(self.NIDAQ_Device.ao_counter)]
                        # AO_outputs will need user iniput. either on/off, or a float value input 
                        aothread = executor.submit(self.threadaotask, AO_initials =  AO_outputs)
                        self.written_data = aothread.result()
                    par_ao = time.time()
                    # print("Par AI-AO: " +str(par_ao - par_ai))
                    # alicatthread = executor.submit(self.threadalicat)
                    # self.ydata_new = aithread.result()
                    # self.MFC1Vals, self.MFC2Vals = alicatthread.result()
                    # par_ali = time.time()
                t_aft_read = time.time()
                t_now = datetime.now()
                t_now_str = t_now.strftime("%d/%m/%Y, %H:%M:%S")

                if (t_aft_read-t_bef_read)>1/self.ActualSamplingRate:#self.task.sampleRate:
                    self.inform_user("Time to read exceeds frequency. Reduce the frequency.")
                    return

                # print(self.ydata.shape,self.ydata_new.shape,self.ydata,self.ydata_new)
                
                if len(self.ydata.shape)==1:
                    self.ydata = np.append(self.ydata,self.ydata_new,axis=0)
                else:
                    self.ydata = np.append(self.ydata,self.ydata_new,axis=1)
                # print(self.ydata)
                t_diff = no_samples/self.ActualSamplingRate#self.task.sampleRate
                tdiff_array = np.linspace(1/self.ActualSamplingRate,t_diff,no_samples)
                if self.xdata[-1]==0:
                    self.xdata_new = np.linspace(self.xdata[-1],self.xdata[-1]+t_diff,no_samples,endpoint=False)
                    if self.ydata.shape[1]>1 and len(self.xdata_new)==1:
                        self.xdata_new = [no_samples/self.ActualSamplingRate] # np.append(self.xdata,self.task.numberOfSamples/self.ActualSamplingRate)
                    self.xdata=self.xdata_new
                    self.abs_timestamp = [(t_now+timedelta(seconds=sec)).strftime("%d/%m/%Y, %H:%M:%S:%f)")[:-3] for sec in tdiff_array]
                    # self.MFC1Vals["Time"] = self.xdata[-1]
                    # self.MFC2Vals["Time"] = self.xdata[-1]
                else:
                    self.xdata_new = np.linspace(self.xdata[-1]+1/self.ActualSamplingRate,self.xdata[-1]+t_diff,no_samples)
                    self.abs_timestamp = [(t_now+timedelta(seconds=sec)).strftime("%d/%m/%Y, %H:%M:%S:%f")[:-3] for sec in tdiff_array]
                    self.xdata = np.append(self.xdata,self.xdata_new)
                    # self.MFC1Vals["Time"] = self.xdata[-1]+t_diff
                    # self.MFC2Vals["Time"] = self.xdata[-1]+t_diff

                if self.save_bool:
                    # self.save_data_thread()
                    self.save_thread = threading.Thread(target = self.save_data_thread)
                    self.save_thread.start()
                
                #Plots
                if hasattr(self, "data_vis_tab"):
                    if not hasattr(self.data_vis_tab, "dev_edit"):
                        self.data_vis_tab.set_labels(self.config_file)
                    self.data_vis_tab.set_data_and_plot(self.xdata, self.ydata[self.data_vis_tab.get_curr_selection()])

            except:
                the_type, the_value, the_traceback = sys.exc_info()
                print(str(the_type) + the_value, the_traceback)
    
        if self.ContinueAcquisition and self.running:
            QTimer.singleShot(10, self.runpyDAQ)
        else:
            self.run_counter = 0
            self.save_button.setEnabled(False)
            if hasattr(self, "dash_thread"):
                self.dash_thread.terminate()
                self.notify("Dashboard closed.")

    @error_logger("SaveData")
    def save_data(self):
        if self.save_button.isChecked():
            self.save_button.setText("Stop")
            self.save_bool = True
            self.run_counter = 0

            if hasattr(self, "save_dir"):
                if not os.path.exists(self.save_dir):
                    os.makedirs(self.save_dir)

            if not os.path.exists(self.json_file):
                with open(self.json_file, "x") as outfile:
                    outfile.write(json.dumps(self.settings, indent=4))

            y_len = int(len(self.config_df["Device"]))
            print(y_len)
            self.ydata = np.empty((y_len,0))
            self.xdata = np.array([0])
            firepydaq_logger.info("Saving initiated properly.")

            self.notify("Saving Data in " + self.parquet_file)

            if self.dashboard:
                firepydaq_logger.info("Dash app Process initiated after saving initiations")
                self.notify("Launching Dashboard on https://127.0.0.1:1222")
                mp.freeze_support()
                self.dash_thread = mp.Process(target = create_dash_app, kwargs = {"jsonpath": self.json_file})
                self.dash_thread.start()
        else:
            self.save_button.setText("Save")
            self.notify("Saving Stopped")
            if hasattr(self,"dash_thread"):
                self.dash_thread.terminate()
            self.save_bool = False
        
    def all_fields_filled(self):
        if (self.name_input.text().strip() == "" or self.exp_input.text().strip() == "" 
            or self.test_input.text().strip() == "" or self.config_file.strip() == "" 
            or self.sample_rate_input.text().strip() == "") :
            raise UnfilledFieldError("Unfilled fields encountered.")
        return True
    
    def validate_df(self, letter, path):
        try:
            df = pl.read_csv(path)
            cols = []
        except:
            return False
        if letter == "f":
            cols = ["Label", "RHS", "Chart", "Legend", "Layout", "Position", "Processed_Unit"]
        if letter == "c":
            cols = ["", "Panel", "Device" , "Channel" , "ScaleMax" , "ScaleMin" , "Label" , 
            "Type", "Chart" , "AIRangeMin", "AIRangeMax", "Layout", "Position", "Processed_Unit", "Legend"]
        
        if cols == df.columns:
            return True
        return False

    def set_formulae_file(self):
        dlg = QFileDialog(self, 'Select a File', None, "CSV files (*.csv)")
        f = ""
        if dlg.exec():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
        if not isinstance(f, str):
            self.formulae_file = f.name
            self.formulae_file_edit.setText(self.formulae_file)
        

    def set_config_file(self): 
        dlg = QFileDialog(self, 'Select a File', None, "CSV files (*.csv)")
        f = ""
        if dlg.exec():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
        if not isinstance(f, str):         
            self.config_file = f.name
            self.config_file_edit.setText(self.config_file)
            

    def safe_exit(self):
        if hasattr(self,'NIDAQ_Device'):
                self.NIDAQ_Device.aitask.stop()
                self.NIDAQ_Device.aitask.close()
                if hasattr(self.NIDAQ_Device,"aotask"):
                    self.NIDAQ_Device.aotask.stop()
                    self.NIDAQ_Device.aotask.close()
                del self.NIDAQ_Device
        self.close()

    def closeEvent(self, *args, **kwargs):
        self.running = False
        time.sleep(1)
        if hasattr(self, "dash_thread"):
                self.dash_thread.terminate()
        if hasattr(self,'NIDAQ_Device'):
            if hasattr(self.NIDAQ_Device,'aitask'):
                self.NIDAQ_Device.aitask.stop()
                self.NIDAQ_Device.aitask.close()
                if hasattr(self.NIDAQ_Device,"aotask"):
                    self.NIDAQ_Device.aotask.stop()
                    self.NIDAQ_Device.aotask.close()
                del self.NIDAQ_Device
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        