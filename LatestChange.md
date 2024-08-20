## FIREpyDAQ v0.1.0
**Functionalities**:
- Reads/Writes Analog Input/Output from cDAQ and PXI NI hardware using NIDAQmx python API.
- Reads/Writes from Alicat devices over serial communication.
- Basic dashboard for displaying depending on the configuration and processing formulae csv files.
- Can run the NIDAQTask standalone to acquire data in the background without the UI. This is recommended for this release, especially for higher frequency acquisition.

**Future scope**
- Reads/Writes from ThorlabsCLD101X device via serial communication.
- Identify way to store and collect data via a buffer or more efficiently to allow collection at for longer duration and without potential memory issues.

**Known Issues**
- Data acquisition for 100 AI channels, at 5Hz, requires more time to save data than 1/5 s after 60 minutes. Potential data loss possible for high frequency acquisition, or long duration experiments with low frequency. The GUI will notify if this limit is reached.
- Memory issues to store the collected data can limit how much data you can collect. This will be addressed in future releases. 100 AI channels at 5Hz sampling rate on a 2.4 GHz, 8 GB RAM Laptop worked without issues until about 60 minutes.

**Primary Contributors**
@dushyant-fire, @anviimishra