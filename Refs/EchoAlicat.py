### Alicat flow controller check
import asyncio
from alicat import FlowController
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class EchoAlicat:
    def __init__(self,run_for=0, parent= None):
        self.parent = parent
        self.run_for = run_for
    
    async def set_params(self,Com_port,gas='N2'):
        time.sleep(1)
        self.flow_controller = FlowController(Com_port)
        if gas == 'HCN':
            gas = 'N2'
        time.sleep(1)
        await self.flow_controller.set_gas(gas)
        time.sleep(0.3)

    async def check_get_vals(self,elapsed_time):
        if elapsed_time>self.run_for:
            self.get_vals=False
    
    async def set_MFC_val(self,flow_rate=0):
        await self.flow_controller.set_flow_rate(flow_rate)

    async def get_MFC_val(self):
        vals = await self.flow_controller.get()
        return vals

    async def get_until_true(self,read_boolean,flow_rate=0):
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
            await self.check_get_vals(t2-begin_time)
            if not all_time:
                all_time.append(0)
            else:
                all_time.append(np.round(all_time[-1]+(t2-t1),2))
            if all_time[-1]%2<0.15:
                print(all_time[-1])

        all_vals = pd.DataFrame(dict_vals)
        all_vals['Time'] = all_time
        # Set flow rate back to zero when the process is complete
        await self.end_collection()
        print(all_vals)
        return all_vals
    
    async def end_collection(self):
        await self.flow_controller.set_flow_rate(0.0)
        await self.flow_controller.close()

if __name__=="__main__":   
    Ali = EchoAlicat(run_for = 4)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Ali.set_params("COM4",gas='C3H8'))
    MF_Vals = loop.run_until_complete(Ali.get_until_true(read_boolean=True,flow_rate=10))
    fig,ax = plt.subplots()
    ax.plot(MF_Vals['Time'],MF_Vals['mass_flow'])
    plt.show()

