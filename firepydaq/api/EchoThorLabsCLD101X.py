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

import time
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
        self._makeconnect()

    def _makeconnect(self):
        print("Connecting to pyvisa resources...")
        self.rm = pyvisa.ResourceManager()
        self.All_ports = self.rm.list_resources()
        only_USB_instr = [n for n, i in enumerate(self.All_ports) if 'USB0' in i]  # noqa #501
        self.All_ports = [self.All_ports[i] for i in only_USB_instr]
        print(self.All_ports)

    def set_connection(self, port):
        '''Set connection to a serial port with Arroyo

        Parameters
        ----------
        port: str
            COM port for the device.
            Example `COM1` on Windows

        '''
        self.port = port
        self.ThorCLD = self.rm.open_resource(self.port)
        print(type(self.ThorCLD))
        self.Device = self.ThorCLD.query("*IDN?")
        print('Device:',self.Device)
        self.ThorCLD.write("*CLS")
        time.sleep(0.1)

    def TEC_settings(self, Temp_SPoint=25, Temp_HI=50, Temp_LO=15, Amp_Lim=1.0):  # noqa #501
        '''Set TEC settings
        Parameters
        ----------
            Temp_SPoint: float
                Temp in C
            Temp_HI : float
                Temp in C
            Temp_LO: float
                Temp in C
            Amp_Lim: float
                Current in mA

        '''
        self.ThorCLD.write("Source2:CURRent:AMPLitude "+str(Amp_Lim))
        self.ThorCLD.write("Source2:TEMPerature:LIMit:UPPer "+str(Temp_HI))
        self.ThorCLD.write("Source2:TEMPerature:LIMit:LOWer "+str(Temp_LO))
        self.ThorCLD.write("Source2:TEMPerature:SPOint "+str(Temp_SPoint))
        # print(self.ThorCLD.query("Source2:TEMPerature:LIMit:LOWer?"))
        time.sleep(1)

    def TEC_SetPID(self, gain="PID", PID_values=[8.0, 3.7, 3.2], Osc_Period=2.0):  # noqa #501
        '''Set PID for the controller
        Parameters
        ----------
            PID_Values : list of floats
                Default: [8.0, 3.7, 3.2]
            Osc_Period : float
                Oscillation period in seconds

        '''
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:GAIN "+str(PID_values[0]))  # noqa #501
        time.sleep(0.2)
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:INTegral "+str(PID_values[1]))  # noqa #501
        time.sleep(0.2)
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:DERivative "+str(PID_values[2]))  # noqa #501
        time.sleep(0.2)
        self.ThorCLD.write("Source2:TEMPerature:LCONstants:PERiod "+str(Osc_Period))  # noqa #501
        time.sleep(0.2)

    def read_TECPID(self):
        '''Queries the TEC PID parameters
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
            PID_set = {'P': P.strip('\n'), 'I': I.strip('\n'),
                       'D': D.strip('\n'), 'O': Osc.strip('\n')}
            return (PID_set)
        except Exception:
            print("PID read error")
            return ()

    def set_TECPID(self, Proportional: float, Integral: float, Derivative: float, Osc: str):
        """ Writes controller PID values
            takes in P I D, and Osc period in order as float type values
        """
        print("Previous PID:    " + str(self.read_TECPID()))
        self.TEC_SetPID(PID_values=[Proportional, Integral, Derivative], Osc_Period=Osc)
        time.sleep(1)
        print("     New PID:    " + str(self.read_TECPID()))
        return

    def StartTEC(self, Switch=False):
        '''Starts the TEC Output
        Args:
            Switch: False (TEC OFF), True (TEC On)
        '''
        self.ThorCLD.write("OUTPut2:STATe " + str(int(Switch)))
        return

    def TECSTatus(self):
        '''Checks the TEC Output Status
        '''
        return self.ThorCLD.query("OUTPut2:STATe?")

    def SetTECTemp(self, Temp):
        '''Sets TEC
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
        '''Initialize laser settings
        Parameters
        ----------
            Laser_HI_Amp: float
                Current limit for the laser in mA
        '''
        self.ThorCLD.write("SOURce1:FUNCtion:MODE CURRent")
        time.sleep(0.1)
        self.ThorCLD.write("SOURce1:CURRent:AMPLitude " + str(Laser_HI_Amp/1000))

    def UpdateLaserCurrent(self, Current):
        '''Updates laser current
        Parameters
        ----------
            Current: float
                Current in mA
        '''
        self.ThorCLD.write("SOURce1:CURRent:LEVel:AMPLitude " + str(Current))
        return

    def GetLaserCurrent(self):
        '''
        Returns:
            Actual Laser Current in mA
        '''
        return self.ThorCLD.write("SOURce1:CURRent:LEVel:AMPLitude?")

    def SwitchLaser(self, Switch=False):
        '''Starts the Laser Output
        Parameters
        ----------
            Switch: bool
                Default: False
                Switches laser On (True) or Off (False)
        '''
        self.ThorCLD.write("OUTPut1:STATe " + str(int(Switch)))
        return

    def LaserStatus(self):
        '''Gets the Laser status
        '''
        return self.ThorCLD.write("OUTPut1:STATe?")

    def close(self):
        """Closes serial connection with controller
        """
        if float(self.GetLaserCurrent()) > 0:
            self.UpdateLaserCurrent(0.0)
            time.sleep(0.5)
            self.SwitchLaser()
        self.StartTEC()
        time.sleep(0.5)
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

    t = 0

    test.Laser_settings()
    AnyError = test.getError()
    print(AnyError, type(int(re.findall(r"\d+", AnyError)[0])))
    AnyError = bool(int(re.findall(r"\d+", AnyError)[0]))
    print(AnyError)
    if not AnyError:
        print("TEC Set point Temp (C): "+test.checkTECSPoint())

        time.sleep(1)
        temp = []
        Laser_current = []
        while t < 30:  # run for 30 s
            temp.append(float(test.GetTECTemp()))
            tcurrent = time.time()
            t = tcurrent - tbegin

            Laser_on = False
            print(temp[-1])
            if abs(np.mean(temp[-5:])-25) < 0.04 and not Laser_on:
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
