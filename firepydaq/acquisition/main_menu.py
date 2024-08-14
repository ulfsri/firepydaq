from PySide6.QtWidgets import QTabWidget, QMenuBar, QDialog
from PySide6.QtGui import QAction, QActionGroup

import webbrowser
from jsonschema import validate
from .device import alicat_mfc 
import json
from .device import mfm
import os
from .device_name_dialog import DeviceNameDialog
from .remove_device_dialog import RemoveDeviceDialog
from .save_setting_to_json_dialog import SaveSettingsDialog
from .load_setting_json_dialog import LoadSettingsDialog
from .schema import schema
from .display_data_tab import data_vis
from .device import thorlabs_laser

from ..utilities.ErrorUtils import error_logger


class MyMenu(QMenuBar):
    """Creates menu bar for the application

    Attributes
    ----------
        parent: object
            Parent class
    """
    def __init__(self, parent):
        super(MyMenu, self).__init__()
        self._makemenu(parent)

    def _makemenu(self, parent):
        self.parent = parent
        # File Menu Button
        self.file_menu = self.addMenu("File")
        self.smell = "Bar"
        # Loading Action
        self.load_daq_action = QAction("Load DAQ Configuration", self)
        self.load_daq_action.triggered.connect(self.load_json_settings)
        self.file_menu.addAction(self.load_daq_action)
        self.load_daq_action.setShortcut("Ctrl+L")

        self.save_daq_action = QAction("Save DAQ Configuration", self)
        self.save_daq_action.triggered.connect(self.save_settings_to_json)
        self.file_menu.addAction(self.save_daq_action)
        self.save_daq_action.setShortcut("Ctrl+S")

        self.save_notif_action = QAction("Save Notifications", self)
        self.save_notif_action.triggered.connect(self.save_notifs)
        self.file_menu.addAction(self.save_notif_action)
        self.save_notif_action.setShortcut("Ctrl+N")

        self.exit_action = QAction("Exit Application", self)
        self.exit_action.triggered.connect(self.parent.safe_exit)
        self.file_menu.addAction(self.exit_action)
        self.exit_action.setShortcut("Alt+X")

        # Add Devices Menu Button
        self.add_devices_menu = self.addMenu("Add Devices")

        # Add Lasers and MFC's
        self.add_laser_action = QAction("Add ThorlabsCLD101X", self)
        self.add_laser_action.triggered.connect(self.add_laser)
        self.add_devices_menu.addAction(self.add_laser_action)
        self.add_laser_action.setShortcut("Shift+Alt+L")

        self.add_mfm_action = QAction("Add MFM", self)
        self.add_mfm_action.triggered.connect(self.add_mfm)
        self.add_devices_menu.addAction(self.add_mfm_action)
        self.add_mfm_action.setShortcut("Shift+Alt+M")

        self.add_mfc_action = QAction("Add MFC", self)
        self.add_mfc_action.triggered.connect(self.add_mfc)
        self.add_devices_menu.addAction(self.add_mfc_action)
        self.add_mfc_action.setShortcut("Shift+Alt+C")

        # Remove Devices Menu Button
        self.remove_devices_menu = self.addMenu("Remove Devices")

        # Remove Lasers and MFC's
        self.rem_laser_action = QAction("Remove ThorlabsCLD101X", self)
        self.rem_laser_action.triggered.connect(self.remove_laser)
        self.remove_devices_menu.addAction(self.rem_laser_action)
        self.rem_laser_action.setShortcut("Ctrl+Shift+L")

        self.rem_mfm_action = QAction("Remove MFM", self)
        self.rem_mfm_action.triggered.connect(self.remove_mfm)
        self.remove_devices_menu.addAction(self.rem_mfm_action)
        self.rem_mfm_action.setShortcut("Ctrl+Shift+F")

        self.rem_mfc_action = QAction("Remove MFC", self)
        self.rem_mfc_action.triggered.connect(self.remove_mfc)
        self.remove_devices_menu.addAction(self.rem_mfc_action)
        self.rem_mfc_action.setShortcut("Ctrl+Shift+M")

        self.rem_all = QAction("Remove All", self)
        self.rem_all.triggered.connect(self.remove_all)
        self.remove_devices_menu.addAction(self.rem_all)
        self.rem_all.setShortcut("Ctrl+Shift+A")

        # Display Data Menu Button
        self.display_data_menu = self.addMenu("Display Data")
        self.display_data_type_menu = self.display_data_menu.addMenu("Display")
        self.display_type = QActionGroup(self, exclusive=True)

        self.no_display = QAction("No Display (Default)", self, checkable=True)
        self.no_display.triggered.connect(self.do_not_display)
        self.no_display.setChecked(True)
        self.display_data_menu.addAction(self.no_display)

        self.dash_display = QAction("Display in a Dashboard", self, checkable=True)
        self.dash_display.triggered.connect(self.display_dashboard)
        self.display_data_type_menu.addAction(self.dash_display)

        self.tab_display = QAction("Display in a Tab", self, checkable=True)
        self.tab_display.triggered.connect(self.display_tab)
        self.display_data_type_menu.addAction(self.tab_display)

        self.all_display = QAction("Display All", self, checkable=True)
        self.all_display.triggered.connect(self.display_all)
        self.display_data_type_menu.addAction(self.all_display)

        self.display_type.addAction(self.tab_display)
        self.display_type.addAction(self.all_display)
        self.display_type.addAction(self.dash_display)
        self.display_type.addAction(self.no_display)

        # Mode
        self.mode_menu = self.addMenu("&Mode")

        # Design Mode Switch
        self.dark_mode = QAction("Dark Mode", self)
        self.dark_mode.triggered.connect(lambda: self.switch_mode("Dark"))
        self.mode_menu.addAction(self.dark_mode)

        self.light_mode = QAction("Light Mode", self)
        self.light_mode.triggered.connect(lambda: self.switch_mode("Light"))
        self.mode_menu.addAction(self.light_mode)

        # Help
        self.help_menu = self.addMenu("&Help")

        # Add Documentation and Reporting Features 
        self.lookup_docs = QAction("Open Documentation", self)
        self.lookup_docs.triggered.connect(self.take_to_docs)
        self.help_menu.addAction(self.lookup_docs)

        self.report_issues = QAction("Report Issue on Github", self)
        self.report_issues.triggered.connect(self.report_issue)
        self.help_menu.addAction(self.report_issues)

    def save_notifs(self):
        f = open("myfile. txt", "w")
        f.write(self.parent.notif_text_slot.text())
        self.parent.notify("File Saved")

    def switch_mode(self, str):
        if str == "Light":
            f = open(self.parent.style_light, "r")
            self.parent.curr_mode = "Light"
        else:
            f = open(self.parent.style_dark, "r")
            self.parent.curr_mode = "Dark"

        style_str = f.read()
        self.parent.setStyleSheet(style_str)
        f.close()

    def display_all(self):
        self.parent.display = True
        self.parent.tab = True
        self.parent.dashboard = True
        if not hasattr(self.parent, "data_vis_tab"):
            self.parent.data_vis_tab = data_vis(self.parent)

    def do_not_display(self):
        if hasattr(self.parent, "data_vis_tab"):
            self.parent.input_tab_widget.removeTab(1)
            del self.parent.data_vis_tab
        self.parent.display = False
        self.parent.tab = False
        self.parent.dashboard = False

    def display_dashboard(self):
        self.parent.display = True
        self.parent.tab = False
        self.parent.dashboard = True
        if hasattr(self.parent, "data_vis_tab"):
            self.parent.input_tab_widget.removeTab(1)
            del self.parent.data_vis_tab

    def display_tab(self):
        self.parent.display = True
        self.parent.tab = True
        self.parent.dashboard = False
        if not hasattr(self.parent, "data_vis_tab"):
            self.parent.data_vis_tab = data_vis(self.parent)

    def take_to_docs(self):
        webbrowser.open("https://doc.qt.io/qtforpython-6/")  # todo replace

    def report_issue(self):
        webbrowser.open("https://github.com/ulfsri/firepydaq/issues/")  # todo replace

    def add_laser(self):
        if not self.parent.device_arr:
            dlg_dev_name = DeviceNameDialog("Add ThorlabsCLD101X")
            self.style_popup(dlg_dev_name)
            if dlg_dev_name.exec() == QDialog.Accepted:
                dev_name = dlg_dev_name.device_name.strip()
                if dev_name == "":
                    self.parent.inform_user("Device name can not be empty.")
                    return
                self.parent.device_tab_widget = QTabWidget()
                self.parent.main_layout.addWidget(self.parent.device_tab_widget)
                self.parent.main_layout.setStretch(0, 2)
                self.parent.main_layout.setStretch(1, 1.5)
                self.parent.device_arr[dev_name] = thorlabs_laser(self.parent, dev_name)
                self.parent.lasers[dev_name] = self.parent.device_arr[dev_name]
            
        elif len(self.parent.lasers) < 6:
            dlg_dev_name = DeviceNameDialog("Add ThorlabsCLD101X")
            self.style_popup(dlg_dev_name)
            if dlg_dev_name.exec() == QDialog.Accepted:
                dev_name = dlg_dev_name.device_name.strip(" ") 
                if dev_name == "":
                    self.parent.inform_user("Device name can not be empty.")
                    return
                if dev_name in self.parent.device_arr:
                    self.parent.inform_user("Device names must be unique.")
                    return
                self.parent.device_arr[dev_name] = thorlabs_laser(self.parent, dev_name)
                self.parent.lasers[dev_name] = self.parent.device_arr[dev_name]
            else:
                print("No ThorlabsCLD101X added.")
        else:
            self.parent.inform_user("Maximum 6 ThorlabsCLD101X devices can be added.")
            return
    
    def remove_mfm(self):
        if not self.parent.mfms:
            self.parent.inform_user("No MFM to remove.")
            return

        dlg_del_name = RemoveDeviceDialog(self.parent.mfms)
        self.style_popup(dlg_del_name)

        if dlg_del_name.exec() == QDialog.Accepted:
            dev_to_del = dlg_del_name.device_to_del
            index_to_del = list(self.parent.device_arr.keys()).index(dev_to_del)
            self.parent.device_tab_widget.removeTab(index_to_del)
            del self.parent.device_arr[dev_to_del]
            del self.parent.mfms[dev_to_del]

            if not self.parent.device_arr:
                self.parent.main_layout.removeWidget(self.parent.device_tab_widget)
                self.parent.device_tab_widget.deleteLater()
        else:
                print("No MFM Removed.")
    
    def add_mfm(self):
        if not self.parent.device_arr:
            dlg_dev_name = DeviceNameDialog("Add MFM")
            self.style_popup(dlg_dev_name)
            if dlg_dev_name.exec() == QDialog.Accepted:
                dev_name = dlg_dev_name.device_name.strip()
                if dev_name == "":
                    self.parent.inform_user("Device name can not be empty.")
                    return
                self.parent.device_tab_widget = QTabWidget()
                self.parent.main_layout.addWidget(self.parent.device_tab_widget)
                self.parent.main_layout.setStretch(0, 2)
                self.parent.main_layout.setStretch(1, 1.5)
                self.parent.device_arr[dev_name] = mfm(self.parent, dev_name)
                self.parent.mfms[dev_name] = self.parent.device_arr[dev_name]

        elif len(self.parent.mfms) < 4:
            dlg_dev_name = DeviceNameDialog("Add MFM")
            self.style_popup(dlg_dev_name)
            if dlg_dev_name.exec() == QDialog.Accepted:
                dev_name = dlg_dev_name.device_name.strip(" ") 
                if dev_name == "":
                    self.parent.inform_user("Device name can not be empty.")
                    return
                if dev_name in self.parent.device_arr:
                    self.parent.inform_user("Device names must be unique.")
                    return
                self.parent.device_arr[dev_name] = mfm(self.parent, dev_name)
                self.parent.mfms[dev_name] = self.parent.device_arr[dev_name]
            else:
                print("No MFM added.")
        else:
            self.parent.inform_user("Maximum 4 MFM's can be added.")
            return

    def add_mfc(self):
        if not self.parent.device_arr:
            dlg_dev_name = DeviceNameDialog("Add MFC")
            self.style_popup(dlg_dev_name)
            if dlg_dev_name.exec() == QDialog.Accepted:
                dev_name = dlg_dev_name.device_name.strip()
                if dev_name == "":
                    self.parent.inform_user("Device name can not be empty.")
                    return
                self.parent.device_tab_widget = QTabWidget()
                self.parent.main_layout.addWidget(self.parent.device_tab_widget)
                self.parent.main_layout.setStretch(0, 2)
                self.parent.main_layout.setStretch(1, 1.5)
                self.parent.device_arr[dev_name] = alicat_mfc(self.parent, self.parent.device_tab_widget, dev_name)
                self.parent.mfcs[dev_name] = self.parent.device_arr[dev_name]

        elif len(self.parent.mfcs) < 4:
            dlg_dev_name = DeviceNameDialog("Add MFC")
            self.style_popup(dlg_dev_name)
            if dlg_dev_name.exec() == QDialog.Accepted:
                dev_name = dlg_dev_name.device_name.strip(" ") 
                if dev_name == "":
                    self.parent.inform_user("Device name can not be empty.")
                    return
                if dev_name in self.parent.device_arr:
                    self.parent.notify("All devices must have unique names.")
                    return
                self.parent.device_arr[dev_name] = alicat_mfc(self.parent, self.parent.device_tab_widget, dev_name)
                self.parent.mfcs[dev_name] = self.parent.device_arr[dev_name]
            else:
                self.parent.notify("No MFC Added.")
        else:
            self.parent.notify("Maximum 4 MFC's can be added.")
            return
        
    def remove_laser(self):

        if not self.parent.lasers:
            self.parent.inform_user("No laser to remove.")
            return

        dlg_del_name = RemoveDeviceDialog(self.parent.lasers)
        self.style_popup(dlg_del_name)

        if dlg_del_name.exec() == QDialog.Accepted:
            dev_to_del = dlg_del_name.device_to_del
            index_to_del = list(self.parent.device_arr.keys()).index(dev_to_del)
            self.parent.device_tab_widget.removeTab(index_to_del)
            del self.parent.device_arr[dev_to_del]
            del self.parent.lasers[dev_to_del]

            if not self.parent.device_arr:
                self.parent.main_layout.removeWidget(self.parent.device_tab_widget)
                self.parent.device_tab_widget.deleteLater()
        else:
                print("No ThorlabsCLD101X laser Removed.")

    def remove_mfc(self):

        if not self.parent.mfcs:
            self.parent.inform_user("No MFC to remove.")
            return

        dlg_del_name = RemoveDeviceDialog(self.parent.mfcs)
        self.style_popup(dlg_del_name)

        if dlg_del_name.exec() == QDialog.Accepted:
            dev_to_del = dlg_del_name.device_to_del
            index_to_del = list(self.parent.device_arr.keys()).index(dev_to_del)
            self.parent.device_tab_widget.removeTab(index_to_del)
            del self.parent.device_arr[dev_to_del]
            del self.parent.mfcs[dev_to_del]

            if not self.parent.device_arr:
                self.parent.main_layout.removeWidget(self.parent.device_tab_widget)
                self.parent.device_tab_widget.deleteLater()
        else:
                print("No MFC Removed.")
    

    def style_popup(self, dlg):
        if self.parent.curr_mode == "Light":
            f = open(self.parent.popup_light)
            str = f.read()
            dlg.setStyleSheet(str)
            f.close()
        else:
            f = open(self.parent.popup_dark)
            str = f.read()
            dlg.setStyleSheet(str)
            f.close()
        return

    @error_logger("SaveSettings")
    def save_settings_to_json(self):
        try:
            json_setting = self.parent.settings_to_json()
        except Exception as e: 
            self.parent.inform_user(str(e))
            return
        
        dlg_save_json = SaveSettingsDialog("Save settings to .json")
        self.style_popup(dlg_save_json)

        if dlg_save_json.exec() == QDialog.Accepted:
            file_json = dlg_save_json.file_path + ".json"
            file_name = dlg_save_json.file_name
            folder_json = dlg_save_json.folder_path
            if os.path.exists(folder_json):
                if os.path.exists(file_json):
                    self.parent.inform_user("File with this name exists.")
                    return
                else:
                    with open(file_json, "w") as outfile:
                        outfile.write(json_setting)
                        outfile.close()
            else:
                self.parent.inform_user("Folder path not found.")
                return

    def load_json_settings(self):
        dlg_load = LoadSettingsDialog()
        self.style_popup(dlg_load)
        if dlg_load.exec() == QDialog.Accepted:
            settings_file = open(dlg_load.file_name)
            data = json.load(settings_file)
            settings_file.close()
            my_schema = schema
            try:
                validate(instance=data, schema=my_schema)
            except Exception as e:
                print(e)
                self.parent.inform_user("Unable to resolve json file.")
                return
            if self.parent.device_arr:
                self.parent.device_arr.clear()
                self.parent.lasers.clear()
                self.parent.mfcs.clear()
                self.parent.main_layout.removeWidget(self.parent.device_tab_widget)
                self.parent.device_tab_widget.deleteLater()
            self.parent.settings.clear()
            self.repopulate_settings(data)
            self.load_devices(data)

    def load_devices(self, data):
        if "Devices" in data:
            dev_dict = data["Devices"]
            self.parent.device_tab_widget = QTabWidget()
            self.parent.main_layout.addWidget(self.parent.device_tab_widget)
            self.parent.main_layout.setStretch(0, 2)
            self.parent.main_layout.setStretch(1, 1.5)
            if "Lasers" in dev_dict:
                laser_dict = dev_dict["Lasers"]
                for laser in laser_dict.keys():
                    my_dict =  dev_dict["Lasers"][laser]
                    self.parent.device_arr[laser] = thorlabs_laser(self.parent,  laser)
                    self.parent.device_arr[laser].load_device_data(str(my_dict["P"]), str(my_dict["I"]), 
                        str(my_dict["D"]), str(my_dict["COMPORT"]), str(my_dict["Tec Rate"]), str(my_dict["Laser Rate"]))
                    self.parent.lasers[laser] = self.parent.device_arr[laser] 
            if "MFCs" in dev_dict:
                mfc_dict = dev_dict["MFCs"]
                for mfc in mfc_dict.keys():
                    my_dict = mfc_dict[mfc]
                    self.parent.device_arr[mfc] = alicat_mfc(self.parent, self.parent.device_tab_widget, mfc)
                    self.parent.device_arr[mfc].load_device_data(my_dict["Gas"], str(my_dict["Rate"]), my_dict["COMPORT"])
                    self.parent.mfcs[mfc] = self.parent.device_arr[mfc] 

    def repopulate_settings(self, data):
        self.parent.settings["Name"] = data["Name"]
        self.parent.settings["Experiment Name"] = data["Experiment Name"] 
        self.parent.settings["Test Name"] = data["Test Name"] 
        self.parent.settings["Sampling Rate"] = data["Sampling Rate"]
        self.parent.settings["Formulae File"] = data["Formulae File"]
        self.parent.settings["Experiment Type"] = data["Experiment Type"]
        self.parent.settings["Config File"] = data["Config File"]
        self.parent._set_texts()
       
    def remove_all(self):
        if self.parent.device_arr:
            self.parent.device_arr.clear()
            if self.parent.mfms:
                self.parent.mfms.clear()
            if self.parent.mfcs:
                self.parent.mfcs.clear()
            if self.parent.lasers:
                self.parent.lasers.clear()
            self.parent.main_layout.removeWidget(self.parent.device_tab_widget)
            self.parent.device_tab_widget.deleteLater()
        else:
            self.parent.inform_user("No devices added yet.")
            return
        