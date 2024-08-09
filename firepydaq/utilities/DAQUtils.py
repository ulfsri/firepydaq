# Data Acquisition Related Utilities
import serial.tools.list_ports as COMPortChecker
import time
import serial

COMports = [tuple(p)[0] for p in list(COMPortChecker.comports())]

colors = {
    'background': '#111111',
    'text': '#111111'
}

Formulae_dict = {"sqrt": "np.sqrt",
                    "pi": "np.pi",
                    "mean": "np.mean",
                    "max": "max",
                    "abs": "np.abs"}
""" dict:
    A dictionary of functions that maps user-inputted functions in the formulae file to equivalent numpy functions.
    For example, `exp` used in a formulae file is converted into `np.exp` while executing the formulae
    This formulae_dict is defined in DAQUtils.py
"""

class check_Arroyo():
    
    def __init__(self):
        """ Sets up connection to Arroyo device
        Searches through available COM connections and shows available Arroyos
        """
        # Listing all available COM ports on windows computer
        ports = list(COMPortChecker.comports())
        self.COMoptions = []
        self.arroyos=[]
        option = 1
        for p in ports:
            # Lists all available devices by Arroyo Instruments
            if "USB Serial Port" in p[1]:
                try:
                    self.port = p[0]
                    # Setting up and connecting to device
                    self.set_connection(self.port)
                    if self.ser.is_open:
                        self.ser.write(b'*IDN? \r\n')
                        time.sleep(0.1)
                        if 'Arroyo' not in bytes.decode(self.ser.read(256)):
                            continue
                        self.ser.write(b'*IDN? \r\n')
                        time.sleep(0.1)
                        # Collects ports at which Arroyos are present
                        self.arroyos.append(bytes.decode(self.ser.read(256)))
                        self.COMoptions.append(p[0])
                        option += 1 
                        self.ser.close()
                        time.sleep(0.1)
                    else:
                        print("\nDid not connect to " + self.port + "\n")
                except:
                    print("Failed to connect to " + p[0])
        print(self.arroyos,self.COMoptions)
    
    def set_connection(self, port):
        '''
        Set connection to a serial port with Arroyo
        '''
        self.ser = serial.Serial(port =     port,
                                            baudrate = 38400,
                                            parity =   serial.PARITY_NONE,
                                            stopbits = serial.STOPBITS_ONE,
                                            bytesize = serial.EIGHTBITS,
                                            xonxoff = False,
                                            timeout =  0,
                                            write_timeout = 0)
        self.ser.write(b'*IDN? \r\n')
        time.sleep(0.1)