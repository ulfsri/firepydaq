# Data Acquisition Related Utilities
import serial.tools.list_ports as COMPortChecker

COMports = [tuple(p)[0] for p in list(COMPortChecker.comports())]

AlicatGases = {
                'N2': u'N\u2082',
                'C3H8': u'C\u2083H\u2088',
                'Air': u'Air'
        }

Formulae_dict = {"sqrt": "np.sqrt",
                 "pi": "np.pi",
                 "mean": "np.mean",
                 "max": "max",
                 "abs": "np.abs",
                 "exp": "np.exp"}
""" dict:
    A dictionary of functions that maps user-inputted variable in the
    formulae file to equivalent numpy functions.
    For example, `exp` used in a formulae file is converted into
    `np.exp` while executing the formulae
"""
