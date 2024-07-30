from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox

import pyqtgraph as pg
import polars as pd

class data_vis(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.ydata = []
        self.xdata = []
        self.index = 0
        self.parent = parent
        self.content = self.create_data_vis_content()
        self.parent.input_tab_widget.addTab(self.content, "Data Visualizer")

    def create_data_vis_content(self):
        self.widget = QWidget()
        self.data_layout = QVBoxLayout()
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.plot(self.ydata, self.xdata)
        self.plot_graph.setLabel('bottom', "Time (s)")
        self.data_layout.addWidget(self.plot_graph)
        self.widget.setLayout(self.data_layout )
        return self.widget 

    def set_data_and_plot(self, xdata, ydata):
        self.plot_graph.clear()
        self.plot_graph.plot(xdata, ydata) 
        self.plot_graph.setLabel('left', self.dev_edit.currentText())

    def set_labels(self, config_file):
        self.label = QLabel("Select Channel to View:")
        self.data_layout.addWidget(self.label)
        self.dev_edit = QComboBox()
        self.data_layout.addWidget(self.dev_edit)
        df = pd.read_csv(config_file)
        for dev in df["Label"]:
            self.dev_edit.addItem(dev)
        
    def get_curr_selection(self):
        self.index = self.dev_edit.currentIndex()
        return self.index