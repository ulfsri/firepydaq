# Utilities
import serial.tools.list_ports as COMPortChecker
COMports = [tuple(p)[0] for p in list(COMPortChecker.comports())]

colors = {
    'background': '#111111',
    'text': '#111111'
}