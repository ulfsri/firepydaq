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

    For example, 'N2': u'N\u2082'.

    You can add custom gas map in this dictionary before you import
    and compile the application interface.
"""

Formulae_dict = {"sqrt": "np.sqrt",
                 "pi": "np.pi",
                 "mean": "np.mean",
                 "max": "max",
                 "abs": "np.abs",
                 "exp": "np.exp"}
""" dict
    A dictionary of functions that maps user-inputted variable in the
    formulae file to equivalent numpy functions.

    For example, `exp` used in a formulae file is converted into
    `np.exp` while executing the formulae

    You can add a custom map to this dictionary before you import
    and compile the application interface.
"""
