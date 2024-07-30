# Utilities
from PIL import Image
import nidaqmx.system as nisys

import pandas as pd
import pyarrow.parquet as pq
import tkinter as tk
import serial.tools.list_ports as COMPortChecker
import serial
import time

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


class create_onoffims():
    def __init__(self,filename):
        self.filename=filename
        self.width_onoff=50
        self.height_onoff=20

        self.create_reduced_imgs()
    
    def create_reduced_imgs(self):
        self.img = Image.open(self.filename)
        self.img = self.img.resize((self.width_onoff,self.height_onoff))#, Image.ANTIALIAS)
        self.img.save(self.filename.split(".")[0]+"_reduced.png")

class check_system_config():

    def __init__(self):
        system = nisys.System.local()
        print("NiDAQmx Driver info: "+str(system.driver_version))
        self.Devs={}
        self.Chans={}
        n=0
        for device in system.devices:
            self.Devs[n]=device
            
            self.Chans[device.name] = [chan.name.split('/')[1] for chan in device.ai_physical_chans]
            n+=1

        self.Devs_names = [n.name for n in self.Devs.values()]
        chassis_locs = [item!=[] for item in self.Chans.values()]
        self.Chans = {key:value for key,value in self.Chans.items() if value}
        self.Devs = {key:self.Devs[key] for n,key in enumerate(self.Devs.keys()) if chassis_locs[n]}
        self.Devs_names = [val for n,val in enumerate(self.Devs_names) if chassis_locs[n]]
        print(self.Chans,self.Devs,self.Devs_names)


class CanvasFrame(tk.Canvas):
    def __init__(self, parent):
        tk.Canvas.__init__(self, parent)
        self.parent = parent

class ScrollbarFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

def read_pq(file):
    table = pq.read_table(file)
    df = table.to_pandas()
    df.iloc[:,1:] = df.iloc[:,1:].astype(float)
    return df

default_configFilePath = "../Config_Formulae_Example/20240329_1354_CalorimetryWLaser_Dushyant.csv" #relative to app 2
MFC_Gases = ["C3H8"]
COMports = [tuple(p)[0] for p in list(COMPortChecker.comports())]

colors = {
    'background': '#111111',
    'text': '#111111'
}

if __name__ == "__main__":
    check_system_config()

    # offimg = create_onoffims('Icons/off.png')
    # onimg = create_onoffims('Icons/on.png')