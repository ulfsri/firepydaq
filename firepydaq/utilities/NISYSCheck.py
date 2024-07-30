import nidaqmx.system as nisys

import nidaqmx.system
system = nidaqmx.system.System.local()
print(system.driver_version)



# print(nisys.Device)
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

if __name__ == "__main__":
    check_system_config()