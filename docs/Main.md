FIREpyDAQ is a python based Facilitated Interface for Recording Experiments (FIRE), for devices that are traditionally used for data acquisition. The device list and general requirements are given below.

## Installation

Using `pip`, you can install this package. `pip` will also install relevant dependencies.

```bash
$ pip install firepydaq
```
## Hardware/Communication Requirements

This interface can be used for three types of devices simultaneously,

- NI hardware, which requires installation of <a href="https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#532710" target="_blank">NI-DAQmx driver</a> from National Instruments.
  - This has been built so far only for Analog Input and Output data.
- Alicat Mass Flow Controllers and Mass Flow Meter, which is based via serial communication and python API available from <a href="https://github.com/numat/alicat" target="_blank">Numat</a>.
- Thorlabs CLD101X, which is based on serial communication

## Usage

`firepydaq` can be used to compile PyQT based user interface.

```python
# On Windows: Protect your script from importing child processes
# Required if you need dashboard access.
# Dashboard is spawned as a separate process. 
if __name__ == "__main__":
    from firepydaq.FIREpyDAQ_Acquisition import FIREpyDAQ_Acquisition
    FIREpyDAQ_Acquisition()

```

Alternatively, you can run the following.
 
```python
# On Windows: Protect your script from importing child processes 
# Required if you need dashboard access.
# Dashboard is spawned as a separate process. 
if __name__ == "__main__":
  import multiprocessing as mp
  mp.freeze_support()
  from firepydaq.acquisition.acquisition import application
  import sys
  from PySide6.QTWidgets import QApplication

  app = QApplication(sys.argv)
  main_app = application()
  main_app.show()
  sys.exit(app.exec())
```

