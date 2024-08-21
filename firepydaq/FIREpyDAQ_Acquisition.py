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

def FIREpyDAQ_Acquisition():
    """Function that compiles the acquisiton application
    and opens the user interface.
    """
    import multiprocessing as mp
    mp.freeze_support()
    from firepydaq.acquisition.acquisition import application
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    main_app = application()
    main_app.show()
    app.exec()
