# Changelog

## firepydaq v 0.1.0 (August 23, 2024)

**Functionalities**:
- Reads/Writes Analog Input/Output from cDAQ and PXI NI hardware using NIDAQmx python API
- Reads/Writes from Alicat devices over serial communication
- Basic dashboard for displaying depending on the configuration and processing formulae csv files
- Can run the NIDAQTask standalone to acquire data in the background without the UI at higher frequency if desired.

**Future scope**
- Reads/Writes from ThorlabsCLD101X device via serial communication
- Identify way to store and collect data via a buffer or more efficiently to allow collection at for longer duration.

**Known Issues**
- Data acquisition for 100 AI channels, @5Hz, requires more time to save data than 1/5 s after 50 minutes. Potential data loss possible for high frequency acquisition, or long duratoin experiments with low frequency. The GUI will notify if this limit is reached.
