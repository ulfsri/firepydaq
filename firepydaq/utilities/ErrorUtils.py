# Utilities
from functools import wraps
from PySide6.QtWidgets import QMessageBox

import logging
import os

def setup_logger(name, logfile, formatter, stream_handler=False, level=logging.DEBUG):
    """Logger file when acquisition is running"""

    file_handler   = logging.FileHandler(logfile)
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

def logger_thread(q):
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)

# formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s -> %(message)s\n')
# Generate the log object
cwd = os.getcwd()
fullLogPath = cwd+os.sep+'FirePyDAQLog.log'
if os.path.exists(fullLogPath):
    os.remove(fullLogPath)
firepydaq_logger = setup_logger('firepydaq_logger', fullLogPath , formatter)

### A function wrapper to catch errors, notify in a message box and save it in a log file
def error_logger(error_func_info:str):
    '''
    Takes a str to indicate the location or the function where an error might occur
    '''
    def decorated(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                print('there')
                return f(*args, **kwargs)
            except Exception as e:
                print('here')
                err_txt = 'In ' +error_func_info + ':' + str(type(e)) + str(e)
                err_msg = __name__ + err_txt
                firepydaq_logger.error(err_msg)

                msg = QMessageBox()
                msg.setWindowTitle("FIREpyDAQ: Release Panic Attack!")
                msg.setText(err_txt)
                msg.exec()

        return wrapped
    return decorated
