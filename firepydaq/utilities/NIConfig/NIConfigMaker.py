
# PyQT Related
from PySide6.QtCore import QTimer, QRect, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QSlider, QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QFileDialog

from multiprocessing import Process, freeze_support
from multiprocessing.pool import ThreadPool

# import threading

import time
import sys
# time.sleep(5)

class NIConfigMaker(QMainWindow):

    def __init__(self):
         
        super().__init__()
        # Set window properties
        self.setGeometry(0, 0, 900, 600)
        self.setFixedSize(900, 600)
        self.setWindowTitle("NI Config Maker")    

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)
        self.initialise_tabs()

        # self.main_layout.setStretch(0, 2.5)
        # self.main_layout.setStretch(1, 1.5)
    
    def initialise_tabs(self):
        self.input_tab_widget = QTabWidget()
        self.input_tab_content = self.input_content()
        self.input_tab_widget.addTab(self.input_tab_content, "Input Settings")
        self.main_layout.addWidget(self.input_tab_widget)
    
    def input_content(self):
        #Input Settings Layout
        self.input_settings_widget = QWidget()
        self.main_input_layout = QHBoxLayout(self.input_tab_widget)
        self.input_layout_container = QWidget()
        self.input_layout = QGridLayout()

        self.thread_button = QPushButton("Run threaded sleep")
        self.thread_button.clicked.connect(self.thread_sleep)
        self.thread_button.setMaximumWidth(200)
        self.input_layout.addWidget(self.thread_button, 7, 1)

        self.slider = QSlider()
        self.slider.setGeometry(QRect(190, 100, 160, 16))
        self.input_layout.addWidget(self.slider,0,0)
        self.slider.setOrientation(Qt.Horizontal)

        self.main_input_layout.addLayout(self.input_layout)
        self.input_settings_widget.setLayout(self.main_input_layout)

        return self.input_settings_widget
    
    def thread_sleep(self):
        t1 = time.time()
        thread = ThreadPool(1)
        thread.apply_async(self.sleep,[5])
        t2 = time.time()
        print("Async for " + str(t2-t1))
        return
    
    def sleep(self,sl_time):
        t1 = time.time()
        time.sleep(sl_time)
        t2 = time.time()
        print("Succesfully slept for " + str(t2-t1))
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = application()
    time.sleep(5)
    main_app.show()
    
    sys.exit(app.exec())
        