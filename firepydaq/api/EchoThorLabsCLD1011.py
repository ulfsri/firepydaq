### Aroyo laser controller check
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import serial
import serial.tools.list_ports as port_list
import numpy as np
import matplotlib.pyplot as plt
import re
import pyvisa

class EchoThor(object):
    """ Arroyo Communication setup for TEC and Laser control """

    def __init__(self):
        """ Sets up connection to Arroyo device
        Searches through available COM connections and shows available Arroyos
        """
        print("Connecting...")
        self.rm = pyvisa.ResourceManager()
        print("here")
        self.All_ports = self.rm.list_resources()
        print(self.All_ports)
        only_USB_instr = [n for n,i in enumerate(self.All_ports) if 'USB0' in i]
        self.All_ports = [self.All_ports[i] for i in only_USB_instr]
        print(self.All_ports)
    
    def set_connection(self, port):
        '''
        Set connection to a serial port with Arroyo
        '''
        self.port = port
        self.ThorCLD = self.rm.open_resource(self.port) # hard coding the USB port option for CLD1011
        print(type(self.ThorCLD))
        self.Device = self.ThorCLD.query("*IDN?")
        print('Device:',self.Device) 
        self.ThorCLD.write("*CLS")
        time.sleep(0.1)
    
    def TEC_settings(self,Temp_SPoint = 25,Temp_HI=50,Temp_LO=15, Amp_Lim=1.0):
        '''
        Set TEC settings
        Parameter:
            Temp_SPoint: Temp in C
            Temp_HI : Temp in C
            Temp_LO: Temp in C
            Amp_Lim: Current in mA
        '''
        self.ThorCLD.write("Source2:CURRent:AMPLitude "+str(Amp_Lim))
        self.ThorCLD.write("Source2:TEMPerature:LIMit:UPPer "+str(Temp_HI))
        self.ThorCLD.write("Source2:TEMPerature:LIMit:LOWer "+str(Temp_LO))
        self.ThorCLD.write("Source2:TEMPerature:SPOint "+str(Temp_SPoint))
        # print(self.ThorCLD.query("Source2:TEMPerature:LIMit:LOWer?"))
        time.sleep(1)

    def TEC_SetPID(self,gain="PID",PID_values = [8.0, 3.7 , 3.2], Osc_Period = 2.0):
        '''
        Set PID
        Params:
            PID_Values = [P, I, D] : {Floats} # Default values from CLD1011
            Osc_Period = Oscillation period in seconds
        '''
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:GAIN "+str(PID_values[0]))
        time.sleep(1)
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:INTegral "+str(PID_values[1]))
        time.sleep(1)
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:DERivative "+str(PID_values[2]))
        time.sleep(1)
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:PERiod "+str(Osc_Period))
        time.sleep(1)

    def read_TECPID(self):
        '''
        Queries the TEC PID parameters
        Returns the TEC PID parameters used when GAIN is set to PID.
        '''
        try:
            P = self.ThorCLD.query("Source2:TEMPerature:LCONstants:GAIN?")
            time.sleep(0.1)
            I = self.ThorCLD.query("Source2:TEMPerature:LCONstants:INTegral?")
            time.sleep(0.1)
            D = self.ThorCLD.query("Source2:TEMPerature:LCONstants:DERivative?")
            time.sleep(0.1)
            Osc = self.ThorCLD.query("Source2:TEMPerature:LCONstants:PERiod?")
            PID_set = ['P:'+P.strip('\n'),'I:'+I.strip('\n'),'D:'+D.strip('\n'),'Osc_period:'+Osc.strip('\n')]
            return(PID_set)
        except:
            print("PID read error")
            return
    
    def set_TECPID(self, P, I, D, Osc):
        """ Writes controller PID values
            takes in P I D, and Osc period in order as float type values """
        print("Previous PID:    " + str(self.read_TECPID()))
        self.TEC_SetPID(PID_values=[P,I,D],Osc_Period=Osc)
        time.sleep(1)
        print("     New PID:    " + str(self.read_TECPID()))
        return

    def StartTEC(self,Switch=False):
        '''
            Starts the TEC Output
        Args:
            Switch: False (TEC OFF), True (TEC On)
        '''
        self.ThorCLD.write("OUTPut2:STATe "+ str(int(Switch)))
        return
    
    def TECSTatus(self):
        '''
            Checks the TEC Output Status
        '''
        return self.ThorCLD.query("OUTPut2:STATe?")
    
    def SetTECTemp(self,Temp):
        '''
        Args:
            Temp: Temp in C
        '''
        self.ThorCLD.write("Source2:TEMPerature:SPOint "+str(Temp))
        return

    def checkTECSPoint(self):
        return self.ThorCLD.query("SOURce2:TEMPerature:SPOint?")
    
    def GetTECTemp(self):
        '''
        Returns:
            Temp: Temp in C
        '''
        return self.ThorCLD.query("SENSe2:TEMPerature:DATA?")

    def Laser_settings(self, Laser_HI_Amp=73.0):
        '''
        Initialize laser settings
        Args:
            Laser_HI_Amp: float, Current limit for the laser in mA
        '''
        self.ThorCLD.write("SOURce1:FUNCtion:MODE CURRent")
        time.sleep(0.1)
        self.ThorCLD.write("SOURce1:CURRent:AMPLitude " +str(Laser_HI_Amp/1000))

    def UpdateLaserCurrent(self,Current):
        '''
        Parameters: 
            Current: Current in mA
        '''
        self.ThorCLD.write("SOURce1:CURRent:LEVel:AMPLitude " +str(Current))
        return
    
    def GetLaserCurrent(self):
        '''
        Returns:
            Actual Laser Current in mA
        '''
        return self.ThorCLD.write("SOURce1:CURRent:LEVel:AMPLitude?")
    
    
    def SwitchLaser(self, Switch = False):
        '''
            Starts the Laser Output
        Args:
            Switches laser On (True) or Off (False)
        '''
        self.ThorCLD.write("OUTPut1:STATe "+ str(int(Switch)))
        return
    
    def LaserStatus(self):
        '''
            Gets the Laser status
        '''
        return self.ThorCLD.write("OUTPut1:STATe?")
    
    def close(self):
        """ Closes serial connection with controller """
        self.ThorCLD.close()
        time.sleep(0.1)
        self.rm.close()
        return

    def getError(self):
        return self.ThorCLD.query("SYSTem:ERRor?")

if __name__ == "__main__":
    test = EchoThor()
    test.set_connection(test.All_ports[0])
    test.TEC_settings()
    test.TEC_SetPID()
    print(test.read_TECPID())
    time.sleep(1)
    test.StartTEC(True)
    tbegin = time.time()
    t=0
    test.Laser_settings()
    AnyError = test.getError()
    print(AnyError,type(int(re.findall("\d+",AnyError)[0])))
    AnyError = bool(int(re.findall("\d+",AnyError)[0]))
    print(AnyError)
    if not AnyError:
        print("TEC Set point Temp (C): "+test.checkTECSPoint())

        time.sleep(1)
        temp = []
        Laser_current=[]
        while t<30: # run for 30 s
            temp.append(float(test.GetTECTemp()))
            tcurrent = time.time()
            t = tcurrent - tbegin

            Laser_on = False
            print(temp[-1])
            if abs(np.mean(temp[-5:])-25)<0.04 and Laser_on==False:
                test.SwitchLaser(True)
                print("Laser on")
                test.UpdateLaserCurrent(1)
                Laser_on = True
            if Laser_on:
                Laser_current.append(test.GetLaserCurrent())
    
        plt.plot(temp)

        print(Laser_current)
        
    test.SwitchLaser(False)
    test.StartTEC(False)
    test.close()
    plt.show()
    # test.Laser_settings()
