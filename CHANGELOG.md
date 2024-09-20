# Changelog

## FIREpyDAQ v0.1.1
- Path for saving data changed for a text input to file name for improved clarity. Now, for a text input to file name, a directory `02_ExperimentData` or `01_CalibratoinData` will be created. Within this, a project directory of the format `YYYYProjectName` will be created in which all the data for the same project and experiment type will be saved as per the previous format.
- Added tool-tip for Dash chart export and play/pause button.

**Primary Contributors**
@dushyant-fire

## FIREpyDAQ v0.1.0.post0
Readme changes

**Primary Contributors**
@dushyant-fire

## FIREpyDAQ v0.1.0
**Functionalities**:
- Reads/Writes Analog Input/Output from cDAQ and PXI NI hardware using NIDAQmx python API.
- Reads/Writes from Alicat devices over serial communication.
- Basic dashboard for displaying depending on the configuration and processing formulae csv files.
- Can run the NIDAQTask standalone to acquire data in the background without the UI. This is recommended for higher frequency acquisition.

**Future scope**
- Test Read/Write from ThorlabsCLD101X device via serial communication.
- Identify way to store and collect data via a buffer or more efficiently to allow collection at for longer duration and without potential memory issues.

**Known Issues**
- Potential data loss possible due to memory issues (limited RAM), or if saving and processing (minimal time array generation) time exceeds 1 second. The GUI will notify if this limit is reached.
- Memory issues to store the collected data can limit how much data you can collect. For reference, 100 AI channels at 5Hz sampling rate on a 2.8 GHz processor, 8 GB RAM PXIe-1088 system worked without issues until about 50 minutes.

**Primary Contributors**
@dushyant-fire, @anviimishra