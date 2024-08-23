import asyncio
from alicat import FlowController, FlowMeter
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class EchoController:
    """Object to communicate with Alicat MFC.
    """
    def __init__(self):
        pass

    async def set_params(self, Com_port, gas='N2'):
        """Method to connect with the Alicat flow controller

        Parameters
        ---------
            Com_port: str
                Comport where the MFM device
                is connected.

                Of the form `COM1` on windows.
            gas : str, optional
                Default: 'N2'
                Gas set for the connected Alicat.
        """
        time.sleep(0.1)
        self.flow_controller = FlowController(Com_port)
        time.sleep(0.1)
        await self.flow_controller.set_gas(gas)

    async def _check_get_vals(self, elapsed_time):
        if elapsed_time > self.run_for:
            self.get_vals = False

    async def set_MFC_val(self, flow_rate=0):
        """Method to set the flow-rate of the connected MFC
        Parameters
        ---------
            flow_rate: float
                Default: 0.0

                Flow rate to set for the MFC device
        """
        await self.flow_controller.set_flow_rate(flow_rate)

    async def get_MFC_val(self):
        """Method to get all values for the connected MFC

        Returns
        -------
        A dictionary type object

                {
                'setpoint': float (mass or pressure),
                'control_point':'flow' or 'pressure',
                'gas':str,
                'mass_flow': float,
                'pressure': float (psia),
                'temperature': float (usually C),
                'total_flow': float (Optional only for totalizer),
                'volumetric_flow': float (units specified during purchase)
                }
        """
        return await self.flow_controller.get()

    async def get_until_true(self, run_for=0, read_boolean=True, flow_rate=0):
        """ Method to run Alicat MFC for a set duration
        Parameters
        ----------
            run_for: int
                Default: 0
                Duration in seconds to run the Alicat device
            read_boolean: bool
                Default: True
                Boolean that is set to True until the
                time for which the data is acquired exceeds `run_for` seconds
            flow_rate: float
                Default: True
                Flow rate to set before acquisition begins

        Returns
        -------
            all_vals : pandas DataFrame
                Dataframe containing all acquired values
                during `run_for` seconds.
        """
        self.run_for = run_for
        self.get_vals = read_boolean
        await self.flow_controller.set_flow_rate(flow_rate)
        begin_time = time.time()
        all_vals = pd.DataFrame()
        dict_vals = []
        all_time = []
        while self.get_vals:
            t1 = time.time()
            vals = await self.flow_controller.get()

            dict_vals.append(vals)

            t2 = time.time()
            await self._check_get_vals(t2-begin_time)
            if not all_time:
                all_time.append(0)
            else:
                all_time.append(np.round(all_time[-1]+(t2-t1), 2))
            if all_time[-1] % 2 < 0.15:
                print(all_time[-1])

        all_vals = pd.DataFrame(dict_vals)
        all_vals['Time'] = all_time
        # Set flow rate back to zero when the process is complete
        await self.end_connection()
        return all_vals

    async def end_connection(self):
        """Method to end connection with the flow controller.

        Sets the flow-rate to zero before ending connection.
        """
        await self.flow_controller.set_flow_rate(0.0)
        await self.flow_controller.close()


class EchoMeter:
    """Object to communicate with MFM.
    """
    def __init__(self):
        pass

    async def set_params(self, Com_port, gas='N2'):
        """Method to connect with the Alicat flow meter

        Parameters
        ---------
            Com_port: str
                Comport where the MFM device
                is connected.

                Of the form `COM1` on Windows.
            gas : str, optional
                Default: 'N2'
                Gas set for the connected Alicat.
        """
        time.sleep(0.1)
        self.flow_meter = FlowMeter(Com_port)
        time.sleep(0.1)
        await self.flow_meter.set_gas(gas)

    async def _check_get_vals(self, elapsed_time):
        if elapsed_time > self.run_for:
            self.get_vals = False

    async def get_MFM_val(self):
        """Method to get the MFM value
        """
        vals = await self.flow_meter.get()
        return vals

    async def get_until_true(self, run_for=0, read_boolean=True):
        """ Method to run Alicat MFM for a set duration

        Parameters
        ----------
            run_for: int
                Duration in seconds to run the Alicat device
                Default is zero.
            read_boolean: bool
                Boolean that is set to True until the
                time for which the data is acquired exceeds `run_for` seconds
                Default: True
        Returns
        -------
            all_vals : pandas DataFrame
                Dataframe containing all acquired values
                during `run_for` seconds.
        """
        self.run_for = run_for
        self.get_vals = read_boolean
        begin_time = time.time()
        all_vals = pd.DataFrame()
        dict_vals = []
        all_time = []
        while self.get_vals:
            t1 = time.time()
            vals = await self.flow_meter.get()

            dict_vals.append(vals)

            t2 = time.time()
            await self._check_get_vals(t2-begin_time)
            if not all_time:
                all_time.append(0)
            else:
                all_time.append(np.round(all_time[-1]+(t2-t1), 2))
            if all_time[-1] % 2 < 0.15:
                print(all_time[-1])

        all_vals = pd.DataFrame(dict_vals)
        all_vals['Time'] = all_time
        # Set flow rate back to zero when the process is complete
        await self.end_connection()
        return all_vals

    async def end_connection(self):
        """Method to end connection with the flow controller.
        """
        await self.flow_meter.close()


if __name__ == "__main__":
    # todo: to move this to tests
    Ali = EchoController()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Ali.set_params("COM4", gas='C3H8'))
    MF_Vals = loop.run_until_complete(Ali.get_until_true(run_for=4, read_boolean=True, flow_rate=1))  # noqa E501
    fig, ax = plt.subplots()
    ax.plot(MF_Vals['Time'], MF_Vals['mass_flow'])
    plt.show()
