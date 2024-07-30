import nidaqmx
import nidaqmx.system as nisys
import pandas as pd
import numpy as np
# Maybe check transition to Polars

class CreateDAQTask:
    def __init__(self,parent,name):
        """
        Initiate a DAQ task. 

        AI: Temp, V, Current
        AO : Only Voltage
        """
        self.parent = parent
        self.name=name

    def CreateFromConfig(self):
        self.initialize_config(self.parent.settings["Config File"])
        if self.ailabel_map:
            self.aitask = nidaqmx.Task(new_task_name=self.name+"_AI")
        if self.aolabel_map:
            self.aotask = nidaqmx.Task(new_task_name=self.name+'_AO')

        for n in self.ChanConfig.index:
            devname = self.ChanConfig.loc[n,'Device'].strip()
            aichan = self.ChanConfig.loc[n,'Channel'].strip()
            measurement = self.ChanConfig.loc[n,'Type'].strip()
            if "ai" in aichan.lower(): # add AI tasks
                self.addAITask(devname,aichan,measurement)
            elif 'ao' in aichan.lower() and self.inputSettingsFrame.GasStr.get()=='HCN': # Add AO tasks
                self.addAOTask(devname,aichan,measurement)

    def initialize_config(self,filepath):
        # f = open(filepath)
        self.ChanConfig =  pd.read_csv(filepath)# json.load(f)
        # f.close()
        self.Fig_titles = self.ChanConfig["Label"]
        self.ailabel_map={}
        self.aolabel_map = {}
        self.ao_inputs = False
        self.ai_counter=0
        self.ao_counter = 0
        for n,i in enumerate(self.ChanConfig["Label"]):
            if 'ai' in self.ChanConfig.Channel[n]:
                self.ailabel_map[i] = self.ai_counter
                self.ai_counter+=1
            elif 'ao' in self.ChanConfig.Channel[n]:
                self.ao_inputs = True
                self.aolabel_map[i] = self.ao_counter
                self.ao_counter+=1
        print('AI Labels: '+ str(list(self.ailabel_map.keys())),'AO Labels: '+ str(list(self.aolabel_map.keys())))

    def addAITask(self,daqname,aichan,measurement):
        """
            Add continous sampling channels to the created task
        """
        ## Needs to have a functionality to add other type of Thermocouple. Perhaps from config file?
        PhysChannelName = daqname+'/'+aichan
        print(PhysChannelName)
        if measurement == "Thermocouple":
            TC = nidaqmx.constants.ThermocoupleType.K
            TC_unit= nidaqmx.constants.TemperatureUnits.DEG_C
            getattr(self.aitask.ai_channels, 'add_ai_thrmcpl_chan')(PhysChannelName,units=TC_unit, thermocouple_type=TC)
        elif measurement =='Voltage':
            V_unit= nidaqmx.constants.VoltageUnits.VOLTS
            getattr(self.aitask.ai_channels, 'add_ai_voltage_chan')(PhysChannelName,units=V_unit)
        elif measurement=="Current":
            A_unit = nidaqmx.constants.CurrentUnits.AMPS
            getattr(self.aitask.ai_channels, 'add_ai_current_chan')(PhysChannelName,units=A_unit)
    
    def addAOTask(self,daqname,aochan,measurement):
        """
            Add analog voltage output task to the same chassis
        """
        PhysChannelName = daqname+'/'+aochan
        if measurement != 'Voltage':
            raise AttributeError("Analog Output task should be Voltage")
        else:
            V_unit= nidaqmx.constants.VoltageUnits.VOLTS
            getattr(self.aotask.ao_channels, 'add_ao_voltage_chan')(PhysChannelName,units=V_unit, min_val=0.0, max_val=3.0)

    def CreateTasks(self,ChanConfig):
        '''
            Requires Channel configuration dataframe (pandas dataframe for now)
        '''
        self.ChanConfig = ChanConfig
        for n in self.ChanConfig.index:
            devname = self.ChanConfig.loc[n,'Device']
            aichan = self.ChanConfig.loc[n,'Channel']
            measurement = self.ChanConfig.loc[n,'Type']
            if "ai" in aichan.lower(): # add AI tasks
                self.addAITask(devname,aichan,measurement)
            elif 'ao' in aichan.lower(): # Add AO tasks
                self.addAOTask(devname,aichan,measurement)

    def StartAIContinuousTask(self,SamplingRate,HowManySample, save_tdms = False, save_tdms_path = "PreSavedData_AI.tdms"):
        """
            Start a AI task to open up communication with the DAQ
            AO task requires initial array to be given in the form of a linear array

            parameters: 
                AO_initials: numpy array of size n having shape (n,)
                save_tdms: Boolean
        """
        self.save_tdms = save_tdms
        self.sampleRate = SamplingRate
        self.numberOfSamples = HowManySample
        print("Sampling Rate: "+str(self.sampleRate)+", Samples per read: "+str(self.numberOfSamples))
        self.aitask.timing.cfg_samp_clk_timing(rate=self.sampleRate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=self.numberOfSamples)

        if self.save_tdms:
            LOG_AND_READ= 15842
            LOG= 15844
            log_mode = nidaqmx.constants.LoggingMode(LOG_AND_READ)
            self.aitask.in_stream.configure_logging(save_tdms_path,logging_mode=log_mode)
        
        self.aitask.start()

    def StartAOContinuousTask(self, AO_initials=None, save_tdms = False, save_tdms_path = "PreSavedData_AO.tdms"):
        """
            Start a on demand AO task to open up communication with the DAQ
            AO task requires initial array to be given in the form of a linear array

            parameters: 
                AO_initials: numpy array of size n having shape (n,)
                save_tdms: Boolean
        """
        self.save_tdms = save_tdms

        self.aotask.write(AO_initials)
        if self.save_tdms:
            LOG_AND_READ= 15842
            LOG= 15844
            log_mode = nidaqmx.constants.LoggingMode(LOG_AND_READ)
            self.aotask.in_stream.configure_logging(save_tdms_path,logging_mode=log_mode)
        
        self.aotask.start()

    def initiate_dataArrays(self):
        
        if self.ai_counter>0:
            self.parent.ydata=np.empty((len(self.ailabel_map),0))
        else: # To check for bugs
            self.parent.ydata = np.empty((len(self.Fig_titles),0))
        
        self.parent.xdata=np.array([0])
        self.parent.abs_timestamp= np.array([])
        self.parent.timing_np = np.empty((0,3))
    
    ## Method to read data from AI task. 
    def threadaitask(self):
        return self.aitask.read(number_of_samples_per_channel=self.numberOfSamples)

    ## Method to output AO task data
    def threadaotask(self, AO_Outputs):
        return self.task.aotask.write(AO_Outputs)

