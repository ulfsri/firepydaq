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

# Error Utilities
from functools import wraps
from PySide6.QtWidgets import QMessageBox

import logging
import os
import sys
import traceback


def setup_logger(name, logfile, formatter, stream_handler=False, level=logging.DEBUG):  # noqa E501
    """Logger file when acquisition is running"""

    file_handler = logging.FileHandler(logfile)
    stdout_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        logger.addHandler(file_handler)
        if stream_handler:
            logger.addHandler(stdout_handler)

    return logger


# formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s -> %(message)s\n')
# Generate the log object
cwd = os.getcwd()
fullLogPath = cwd+os.sep+'FIREyDAQ.log'
if os.path.exists(fullLogPath):
    os.remove(fullLogPath)
firepydaq_logger = setup_logger('firepydaq_logger', fullLogPath, formatter)


# A function wrapper to catch errors,
# notify in a message box and save it in a log file
def error_logger(error_func_info: str):
    '''
    Takes a str to indicate the location or
    the function where an error might occur.
    '''
    def decorated(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception:
                print('error utils exception')
                type, value, tb = sys.exc_info()
                err_txt = 'In ' + error_func_info + ':' + str(type) + str(value) + str(traceback.print_tb(tb))  # noqa E501
                err_msg = __name__ + err_txt
                firepydaq_logger.error(err_msg)

                msg = QMessageBox()
                msg.setWindowTitle("FIREpyDAQ: Release Panic Attack!")
                msg.setText(err_txt)
                msg.exec()

        return wrapped
    return decorated
