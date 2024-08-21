#########################################################################
# FIREpyDAQ - Facilitated Interface for Recording Experiemnts,
# a python-based Data Acquisition program.
# Copyright (C) 2024  Dushyant M. Chaudhari

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#########################################################################

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox

import pyqtgraph as pg
import polars as pl


class data_vis(QWidget):
    """Object that creates a raw data
    visualization tab next to Input Settings.

    For this to be initiated, dsiplay in tab or display all
    must be selected.

    Attributes
    ----------
        plot_graph: PlotWidget
            pyqtgraph PlotWidget that plots
            the acquired raw data during acquisition
    """
    def __init__(self, parent):
        super().__init__()
        self._makeinit(parent)

    def _makeinit(self, parent):
        self.ydata = []
        self.xdata = []
        self.index = 0
        self.parent = parent
        self.content = self.create_data_vis_content()
        self.parent.input_tab_widget.addTab(self.content, "Data Visualizer")

    def create_data_vis_content(self):
        """Method that creates the raw data visualizer.
        Creates `plot_graph` widget
        """
        self.widget = QWidget()
        self.data_layout = QVBoxLayout()
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.plot(self.ydata, self.xdata)
        self.plot_graph.setLabel('bottom', "Time (s)")
        self.data_layout.addWidget(self.plot_graph)
        self.widget.setLayout(self.data_layout)
        return self.widget

    def set_data_and_plot(self, xdata, ydata):
        """Method that plots the x and y data
        in a separate thread without affecting acquisition.

        Parameters
        ----------
            xdata: numpy array
                Relative time array
            ydata: numpy array
                Raw data selected from a drop down
                `dev_edit` that lists available columns for plotting.
        """
        self.plot_graph.clear()
        self.plot_graph.plot(xdata, ydata)
        self.plot_graph.setLabel('left', self.dev_edit.currentText())

    def set_labels(self, config_file):
        """Method that creates dropdown for letting user select
        from available channel labels
        """
        if not hasattr(self, "label") and not hasattr(self, "dev_edit"):
            self.label = QLabel("Select Channel to View:")
            self.data_layout.addWidget(self.label)
            self.dev_edit = QComboBox()
            self.data_layout.addWidget(self.dev_edit)
            df = pl.read_csv(config_file)
            for dev in df["Label"]:
                self.dev_edit.addItem(dev)

    def get_curr_selection(self):
        """Method to get user selected """
        self.index = self.dev_edit.currentIndex()
        return self.index
