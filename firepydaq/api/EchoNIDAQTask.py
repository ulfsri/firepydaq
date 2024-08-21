#########################################################################
# FIREpyDAQ - Facilitated Interface for Recording Experiemnts,
# a python-based Data Acquisition program.
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

import nidaqmx
import nidaqmx.constants
import nidaqmx.stream_writers
import pandas as pd
from importlib.metadata import version
__version__ = version("firepydaq")


class CreateDAQTask:
    def __init__(self, parent, name):
        """Initiate a DAQ task.

        AI: Temp, V, Current
        AO : Only Voltage
        """
        self.parent = parent
        self.name = name

    def CreateFromConfig(self, cpath):
        """Method to add AI and AO tasks using a config file.

        See Config File Example to learn more
        about the required config file format.
        """
        self.initialize_config(cpath)
        if self.ailabel_map:
            self.aitask = nidaqmx.Task(new_task_name=self.name+"_AI")
        if self.aolabel_map:
            self.aotask = nidaqmx.Task(new_task_name=self.name+'_AO')
        self.ChanConfig = self.ChanConfig.astype(str)
        for n in self.ChanConfig.index:
            devname = self.ChanConfig.loc[n, 'Device'].strip()
            aichan = self.ChanConfig.loc[n, 'Channel'].strip()
            measurement = self.ChanConfig.loc[n, 'Type'].strip()
            TCType = self.ChanConfig.loc[n, 'TCType'].strip()
            chantype = self.ChanConfig.loc[n, 'Channel']
            if self.ai_counter > 0 and 'ai' in chantype:  # add AI tasks
                self.addAITask(devname, aichan, measurement, TCType)
            elif self.ao_counter > 0 and 'ao' in chantype:  # Add AO tasks
                self.addAOTask(devname, aichan, measurement)

    def initialize_config(self, filepath):
        """Method that reads the config file and creates
        dictionaries for AI and AO channels and their indices,
        as per the config .csv file.
        """
        self.ChanConfig = pd.read_csv(filepath)
        self.ChanConfig.columns = [i.strip() for i in self.ChanConfig.columns]
        self.Fig_titles = self.ChanConfig["Label"]
        self.ailabel_map = {}
        self.aolabel_map = {}
        self.ao_inputs = False
        self.ai_counter = 0
        self.ao_counter = 0
        for n, i in enumerate(self.ChanConfig["Label"]):
            if 'ai' in self.ChanConfig.Channel[n]:
                self.ailabel_map[i] = self.ai_counter
                self.ai_counter += 1
            elif 'ao' in self.ChanConfig.Channel[n]:
                self.ao_inputs = True
                self.aolabel_map[i] = self.ao_counter
                self.ao_counter += 1
        print('AI Labels: ' + str(list(self.ailabel_map.keys())), 'AO Labels: ' + str(list(self.aolabel_map.keys())))  # noqa E501

    def addAITask(self, daqname, aichan, measurement, TCtype):
        """Method to add continous analog input
        sampling channels in default terminal configuration.

        Parameters
        ----------
            daqname: str
                Name of the device connected
            aichan: str
                Analog Input channel (usually the type of 'ai0', 'ai1' etc.)
            measurement: str
                Accepts "Thermocouple", "Voltage", and "Current"
            TCType: str
                Accepts "B","E","J","K","N","R","S", or "T" thermocouple type
                Use "NA" in TCType for row corresponding
                to non-thermocouple channels.
        """
        PhysChannelName = daqname+'/'+aichan
        print(PhysChannelName)
        if measurement == "Thermocouple":
            if TCtype.strip() not in ["B", "E", "J", "K", "N", "R", "S", "T"]:
                raise KeyError('"TCType" must be one of "B","E","J","K","N","R","S", or "T" thermocouple type')
            else:
                TC = nidaqmx.constants.ThermocoupleType[TCtype]
            # TC = nidaqmx.constants.ThermocoupleType.K
            TC_unit = nidaqmx.constants.TemperatureUnits.DEG_C
            getattr(self.aitask.ai_channels, 'add_ai_thrmcpl_chan')(PhysChannelName, units=TC_unit, thermocouple_type=TC)
        elif measurement == 'Voltage':
            V_unit = nidaqmx.constants.VoltageUnits.VOLTS
            getattr(self.aitask.ai_channels, 'add_ai_voltage_chan')(PhysChannelName, units=V_unit)
        elif measurement == "Current":
            A_unit = nidaqmx.constants.CurrentUnits.AMPS
            getattr(self.aitask.ai_channels, 'add_ai_current_chan')(PhysChannelName, units=A_unit)

    def addAOTask(self, daqname, aochan, measurement):
        """Method to add Analog Voltage Output task.

        Parameters
        ----------
            daqname: str
                Name of the device connected
            aochan: str
                Analog Output channel (usually the type of 'ao0', 'ao1' etc.)
            measurement: str
                Accepts "Voltage" or "Current".
        """
        PhysChannelName = daqname+'/'+aochan
        if measurement != 'Voltage':
            raise AttributeError('Analog Output task should be "Voltage" or "Current"')
        else:
            V_unit = nidaqmx.constants.VoltageUnits.VOLTS
            getattr(self.aotask.ao_channels, 'add_ao_voltage_chan')(PhysChannelName, units=V_unit, min_val=0.0, max_val=3.0)

    def StartAIContinuousTask(self, SamplingRate, HowManySample, save_tdms=False, save_tdms_path="PreSavedData_AI.tdms"):
        """Method to  start a continous AI task once the `aitask`
        is configured to open up communication with the NI hardware.

        Keyword Arguments
        ----------------
            SamplingRate: float
            HowManySamples: int
                Currently, this is set to match SamplingRate.
            save_tdms: Boolean
                Default is False
            save_tdms_path : str
                Default is "PreSaveData_AI.tdms"
        """
        self.save_tdms = save_tdms
        self.sampleRate = SamplingRate
        self.numberOfSamples = HowManySample
        print("Sampling Rate: "+str(self.sampleRate)+", Samples per read: " + str(self.numberOfSamples))
        self.aitask.timing.cfg_samp_clk_timing(rate=self.sampleRate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=self.numberOfSamples)

        if self.save_tdms:
            LOG_AND_READ = 15842
            LOG = 15844
            log_mode = nidaqmx.constants.LoggingMode(LOG_AND_READ)
            self.aitask.in_stream.configure_logging(save_tdms_path, logging_mode=log_mode)

        self.aitask.start()

    def StartAOContinuousTask(self, AO_initials=None, save_tdms=False, save_tdms_path="PreSavedData_AO.tdms"):
        """Method to start a continous AO task once
        `aotask` is configured.

        Starts an on demand AO task to open up communication with the DAQ
        AO task requires initial array to be given in the form of a linear array

        Keyword Arguments
        ----------------
            AO_initials: numpy array of size n having shape (n,)
                Default is None
            save_tdms: Boolean
                Default is False
            save_tdms_path : str
                Default is "PreSaveData_AO.tdms"
        """
        self.save_tdms = save_tdms
        # self.aotask.start()
        # print(self.aotask.out_stream.num_chans)
        self.aotask.out_stream.regen_mode = nidaqmx.constants.RegenerationMode.DONT_ALLOW_REGENERATION
        self.aotask.timing.cfg_samp_clk_timing(rate=1)
        print(self.aotask.channel_names, AO_initials, AO_initials.shape)
        self.aotask.write(AO_initials)
        # print(self.aotask.out_stream.curr_write_pos)
        # self.AO_Writer = nidaqmx.stream_writers.AnalogMultiChannelWriter(self.aotask.out_stream, auto_start=True)

        # self.AO_Writer.write_one_sample(AO_initials)
        self.aotask.start()
        print(self.aotask.out_stream.curr_write_pos)
        if self.save_tdms:
            LOG_AND_READ = 15842
            LOG = 15844
            log_mode = nidaqmx.constants.LoggingMode(LOG_AND_READ)
            self.aotask.out_stream.configure_logging(save_tdms_path, logging_mode=log_mode)

    # Method to read data from AI task.
    def threadaitask(self):
        """Method to read the `aitask` data

        Returns
        -------
            NI AI data as a numpy array
        """
        return self.aitask.read(number_of_samples_per_channel=self.numberOfSamples)

    # Method to output AO task data
    def threadaotask(self, AO_Outputs):
        """Method to write the `aotask` data

        Returns
        -------
            Written aotask data as a numpy array
        """
        return self.aotask.write(AO_Outputs)
