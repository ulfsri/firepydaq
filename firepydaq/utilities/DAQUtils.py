##########################################################################
# FIREpyDAQ - Facilitated Interface for Recording Experiments,
# a python-package for Data Acquisition.
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

# Data Acquisition Related Utilities
import serial.tools.list_ports as COMPortChecker

COMports = [tuple(port)[0] for port in list(COMPortChecker.comports())]
""" List of available communication ports for devices
    A device must be connected before importing and compiling
    the application for the COM ports to appear as options.
"""

AlicatGases = {
                'N2': u'N\u2082',
                'C3H8': u'C\u2083H\u2088',
                'Air': u'Air'
        }
""" dict
    A dictionary that maps gasname to unicode gas names for Alicat device.

    For example, 'N2': u'N\\u2082'.

    You can add custom gas map in this dictionary before you import
    and compile the application interface.

    .. code-block:: python

        from firepydaq.utilities.DAQUtils import AlicatGases
        AlicatGases['C2H2'] = u'C\\u2082H\\u2082'
"""

Formulae_dict = {"len":"len",
                 "min":"min",
                 "max": "max",
                 "sqrt": "np.sqrt",
                 "pi": "np.pi",
                 "mean": "np.mean",
                 "abs": "np.abs",
                 "exp": "np.exp"}
""" dict
    A dictionary of functions that maps user-inputted variable in the
    formulae file to equivalent numpy functions.

    For example, `exp` used in a formulae file is converted into
    `np.exp` while executing the formulae

    You can add a custom map to this dictionary before you import
    and compile the application interface, as shown below for 'log'.
    Once you do this, you can use 'log' in the equations you specify
    and the formulae parser will replace it to the corresponding
    function you define.

    .. code-block:: python
    
        from firepydaq.utilities.DAQUtils import Formulae_dict
        Formulae_dict['log'] = 'np.log10'
"""
