import nidaqmx.system as nisys

import nidaqmx.system
system = nidaqmx.system.System.local()


class check_system_config():

    def __init__(self):
        system = nisys.System.local()
        print("NiDAQmx Driver info: "+str(system.driver_version))
        self.Devs = {}
        self.Chans = {}
        self.AOChans = {}
        n = 0
        for device in system.devices:
            self.Devs[n] = device
            self.Chans[device.name] = [chan.name.split('/')[1] for chan in device.ai_physical_chans]  # noqa E501
            self.AOChans[device.name] = [chan.name.split('/')[1] for chan in device.ao_physical_chans]  # noqa E501
            n += 1

        aichans, aidevs, ainames = self.GetCleanInfo(self.Devs, self.Chans)
        aochans, aodevs, aonames = self.GetCleanInfo(self.Devs, self.AOChans)
        print("Analog Input info:", aichans, aidevs, ainames)
        print("Analog Output Info:", aochans, aodevs, aonames)

    def GetCleanInfo(self, Devs, Chans):
        Devs_names = [n.name for n in Devs.values()]
        chassis_locs = [item != [] for item in Chans.values()]
        Chans = {key: value for key, value in Chans.items() if value}
        Devs = {key: Devs[key] for n, key in enumerate(Devs.keys()) if chassis_locs[n]}  # noqa E501
        Devs_names = [val for n, val in enumerate(Devs_names) if chassis_locs[n]]  # noqa E501
        return (Chans, Devs, Devs_names)


if __name__ == "__main__":
    check_system_config()
