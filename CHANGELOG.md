# firepydaq v 0.1.0 (July 17, 2024)

### Functionalities:
- Reads/Writes Analog Input/Output from cDAQ and PXI NI hardware using NIDAQmx python API
- Reads/Writes from Alicat devices over serial communication
- Reads/Writes from ThorlabsCLD101X device via serial communication
- Basic dashboard for displaying depending on the configuration and processing formulae csv files

### Known Issues:
- Parallel programming restricted to NIDAQ above 10 Hz (i.e. less than 10 samples per second). 
- Can run the NIDAQTask standalone to acquire data in the background without the UI at higher frequency if desired.