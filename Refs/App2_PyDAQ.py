#################################################################################
# By: Dushyant M. Chaudhari
# Last Updated: May 14 2024
# Config file needs to be in the form of a csv. The format is App1_ConfigFile
# Reads continous input from NIDAQ. 
# Opens a Dash app in another thread once the saving the data has begun.
#################################################################################

import nidaqmx
import nidaqmx.system as nisys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from utilities.Utils import default_configFilePath,CanvasFrame, ScrollbarFrame
import os
import sys
import traceback

import concurrent.futures
import threading

# from AlicatSettings import AlicatSettings

import pyarrow.parquet as pq
import pyarrow as pa

import numpy as np
import time
import pandas as pd
from datetime import datetime,timedelta

from dashboard.app import *
import multiprocessing

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class CreateDAQTask:
    def __init__(self,parent,name):
        """
        Initiate a DAQ task. 
        """
        self.parent = parent
        self.name=name
        self.task = nidaqmx.Task(new_task_name=self.name)
    
    def addTask(self,daqname,aichan,measurement,min_val,max_val):
        """
            Add continous sampling channels to the created task
        """
        
        PhysChannelName = daqname+'/'+aichan
        if measurement == "Thermocouple":
            TC = nidaqmx.constants.ThermocoupleType.K
            TC_unit= nidaqmx.constants.TemperatureUnits.DEG_C
            getattr(self.task.ai_channels, 'add_ai_thrmcpl_chan')(PhysChannelName,units=TC_unit, thermocouple_type=TC,min_val=min_val,max_val=max_val)
        elif measurement =='Voltage':
            V_unit= nidaqmx.constants.VoltageUnits.VOLTS
            getattr(self.task.ai_channels, 'add_ai_voltage_chan')(PhysChannelName,units=V_unit,min_val=min_val,max_val=max_val)
        elif measurement=="Current":
            A_unit = nidaqmx.constants.CurrentUnits.AMPS
            getattr(self.task.ai_channels, 'add_ai_current_chan')(PhysChannelName,units=A_unit,min_val=min_val,max_val=max_val)
    
    def StartContinuousTask(self,SamplingRate,HowManySample):
        """
            Start a task to open up communication with the DAQ
        """
        self.sampleRate = SamplingRate
        self.numberOfSamples = HowManySample
        print("Sampling Rate: "+str(self.sampleRate)+", Samples per read: "+str(self.numberOfSamples))
        self.task.timing.cfg_samp_clk_timing(rate=self.sampleRate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=self.numberOfSamples)

        if self.parent.save_tdms:
            LOG_AND_READ= 15842
            LOG= 15844
            log_mode = nidaqmx.constants.LoggingMode(LOG_AND_READ)
            self.task.in_stream.configure_logging("PreSavedData.tdms",logging_mode=log_mode)
        
        self.task.start()

class PyDAQContinuousInput(tk.Frame):

    def __init__(self, parent, title):
        tk.Frame.__init__(self,parent)#,master)
        self.parent = parent
        self.title = title
        self.filePath = "test"
        self.DefConfig = default_configFilePath
        
        self.SaveDataButtonStatus=False
        self.processedDataStatus=True
        self.on = tk.PhotoImage(file = "Icons/on_reduced.png")
        self.off = tk.PhotoImage(file = "Icons/off_reduced.png")

        self.initialize_config(self.DefConfig)
        self.processing_options = ["Linear Scaling","Average"]
        self.create_widgets()
        self.pack()
        self.run = False
    
    def initialize_config(self,filepath):
        # f = open(filepath)
        self.ChanConfig =  pd.read_csv(filepath)# json.load(f)
        # f.close()
        self.Fig_titles=self.ChanConfig["Label"]

    def create_widgets(self):
        
        #The main frame is made up of three subframes
        self.ProcessedFrame = OptionalProcessedDataVisualizer(self, title ="Processed Data Visual")
        self.ProcessedFrame.grid(row=1, column=1, sticky="ew", pady=(20,0), padx=(20,20), ipady=10)

        self.inputSettingsFrame = inputSettings(self, title="Input Settings")
        self.inputSettingsFrame.grid(row=0, column=0, rowspan=2, pady=(0,0), padx=(10,10), ipady=0)

        self.AlicatSettingsFrame = AlicatSettings(self,title="Alicat Settings")
        self.AlicatSettingsFrame.grid(row=0,column=1,pady=(0,0),padx=(10,0))

        self.SaveDataFrame = pd.DataFrame(columns = self.Fig_titles)
        # self.graphDataFrame = graphData(self)
        # self.graphDataFrame.grid(row=0, rowspan=2, columnspan=3, column=2, pady=(0,0), ipady=0)

    def startTask(self):
        self.run_counter =0
        self.save_tdms = False
        #Prevent user from starting task a second time
        self.inputSettingsFrame.startButton['state'] = 'disabled'

        #Shared flag to alert task if it should stop
        self.continueRunning = True

        self.task = CreateDAQTask(self,name="App2Task")
        for n in self.ChanConfig.index:
            devname = self.ChanConfig.loc[n,'Device']
            aichan = self.ChanConfig.loc[n,'Channel']
            measurement = self.ChanConfig.loc[n,'Type']
            min_val = np.float32(self.ChanConfig.loc[n,'Min'])
            max_val = np.float32(self.ChanConfig.loc[n,'Max'])
            self.task.addTask(devname,aichan,measurement,min_val,max_val)

        self.task.StartContinuousTask(np.float32(self.inputSettingsFrame.sampleRateEntry.get()),int(np.ceil(np.float32(self.inputSettingsFrame.sampleRateEntry.get()))))#self.task.addTask

        self.ydata=np.empty((len(self.ChanConfig['Device']),0))
        self.xdata=np.array([0])
        self.abs_timestamp= np.array([])
        self.timing_np = np.empty((0,3))
        # #Get task settings from the user
        self.task.sampleRate = np.float32(self.inputSettingsFrame.sampleRateEntry.get())
        self.task.numberOfSamples = int(np.ceil(np.float32(self.task.sampleRate))) #Share number of samples with runTask

        #spin off call to check 
        self.master.after(10, self.runTask)
    
    def savedatathread(self):
        time_data = np.array(self.xdata_new)
        time_data = time_data[np.newaxis,:]
        abs_time = np.array(self.abs_timestamp)
        abs_time = abs_time[np.newaxis,:]
        temp_data = np.append(time_data,np.array(self.ydata_new),axis=0)
        temp_data = np.append(abs_time,temp_data,axis=0).T

        pd_cols = np.insert(self.Fig_titles.values,0,"Time")
        pd_cols = np.insert(pd_cols,0,"Absolute_Time")
        self.SaveDataFrame = pd.DataFrame(columns=pd_cols, data = temp_data)
        # print(self.SaveDataFrame)

        if os.path.isfile(self.datafile_name+'.parquet'):

            # old_pq = pd.read_parquet(self.datafile_name+'.parquet')
            table = pq.read_table(self.datafile_name+'.parquet')
            old_pq = table.to_pandas()
            new_df = pd.concat([old_pq,self.SaveDataFrame],ignore_index=True)
        else:
            new_df = self.SaveDataFrame
        table = pa.Table.from_pandas(new_df)
        pq.write_table(table, self.datafile_name+'.parquet')
        # only for timing. parquet file is faster and smaller to write/read
        # self.SaveDataFrame.to_csv(self.datafile_name+'.csv',mode='a',header=not os.path.isfile(self.datafile_name+'.csv'))
        
        self.t_aft_save = time.time()
        self.SavingTime = self.t_aft_save-self.t_bef_save

        self.timing_np= np.append(self.timing_np,np.array([[self.xdata[-1],self.ProcessingTime, self.SavingTime]]),axis=0)
        self.TimeDataFrame = pd.DataFrame(data=self.timing_np, columns=["Last time entry (s)", "Processing Time (s)", "Saving time (s)"])
        table_timings = pa.Table.from_pandas(self.TimeDataFrame)
        pq.write_table(table_timings, self.datafile_name+'_time.parquet')
        return

    def threadaitask(self):
        return self.task.task.read(number_of_samples_per_channel=self.task.numberOfSamples)

    def runTask(self):
        if self.SaveDataButtonStatus and self.run_counter==0 and self.save_tdms:
            self.task.task.in_stream.start_new_file(self.datafile_name)
        self.run_counter+=1
        # t_read_in = time.time()
        self.ActualSamplingRate = self.task.task.timing.samp_clk_rate
        samplesAvailable = self.task.task._in_stream.avail_samp_per_chan
        # print(samplesAvailable,self.task.task.timing.samp_clk_rate, self.task.task.name) #self.task.task.channel_names,
        if(samplesAvailable >= self.task.numberOfSamples):
            try:
                t_bef_read = time.time()

                with concurrent.futures.ThreadPoolExecutor() as executor: # threading input and output tasks
                    aithread = executor.submit(self.threadaitask)
                    self.ydata_new = aithread.result()
                
                # self.ydata_new = self.task.task.read(number_of_samples_per_channel=self.task.numberOfSamples)
                t_aft_read = time.time()
                t_now = datetime.now()
                # t_now_str = t_now.strftime("%d/%m/%Y, %H:%M:%S")
                # print(t_aft_read-t_bef_read)
                # self.xdata_new = np.array([t_now_str+datetime.timedelta(seconds=i/self.ActualSamplingRate) for i in range(self.ydata_new.shape[0])])
                if (t_aft_read-t_bef_read)>1/self.ActualSamplingRate:#self.task.sampleRate:
                    raise ConnectionError("Time to read exceeds frequency. Reduce the frequency.")

                self.ydata = np.append(self.ydata,self.ydata_new,axis=1)
                
                self.t_diff = self.task.numberOfSamples/self.ActualSamplingRate#self.task.sampleRate
                tdiff_array = np.linspace(1/self.ActualSamplingRate,self.t_diff,self.task.numberOfSamples)
                if self.xdata[-1]==0:
                    self.xdata_new = np.linspace(self.xdata[-1],self.xdata[-1]+self.t_diff,self.task.numberOfSamples,endpoint=False)
                    if self.ydata.shape[1]>1 and len(self.xdata_new)==1:
                        self.xdata_new = np.append(self.xdata,self.task.numberOfSamples/self.ActualSamplingRate)
                    self.xdata=self.xdata_new
                    self.abs_timestamp = [(t_now+timedelta(seconds=sec)).strftime("%d/%m/%Y, %H:%M:%S:%f)")[:-3] for sec in tdiff_array]
                    
                else:
                    self.xdata_new = np.linspace(self.xdata[-1]+1/self.ActualSamplingRate,self.xdata[-1]+self.t_diff,self.task.numberOfSamples)
                    self.abs_timestamp = [(t_now+timedelta(seconds=sec)).strftime("%d/%m/%Y, %H:%M:%S:%f")[:-3] for sec in tdiff_array]
                    self.xdata = np.append(self.xdata,self.xdata_new)
                    
                # print(self.abs_timestamp)
                if (self.xdata[-1]%5)<=1:
                    text_update = "Last time entry:" +str(self.xdata[-1]) +", Total Samples acquired per channel:" +str(self.task.task.in_stream.total_samp_per_chan_acquired)+',\n Actual sampling rate:'+str(self.task.task.timing.samp_clk_rate)+', Samples per read:'+str(self.task.numberOfSamples)
                    self.inputSettingsFrame.UpdateLabel.config(text=text_update,bg= "gray51", fg= "white")
                
                t_bef_process = time.time()
                if (self.processedDataStatus) and self.ActualSamplingRate<=15: # processing time is about 0.05 s
                    self.ProcessedFrame.ax.cla()
                    if self.ProcessedFrame.ProcessType.get() == self.processing_options[0]: # Linear scaling
                        chan_location = self.Fig_titles.index[self.Fig_titles == self.ProcessedFrame.ScaleSelecter.get()].values
                        # print(chan_location, self.ydata[chan_location,:])
                        data_to_scale = self.ydata[chan_location,:].T
                        processed_ydata = data_to_scale*np.float64(self.ProcessedFrame.ScaleValue.get())
                    elif self.ProcessedFrame.ProcessType.get() == self.processing_options[1]: # Averaging
                        if self.ProcessedFrame.avg_choices:
                            selected_chan_indices = [self.Fig_titles.index[self.Fig_titles==i].values for i in self.ProcessedFrame.avg_choices]
                            # print(selected_chan_indices)
                            processed_ydata = self.ydata[selected_chan_indices,:].mean(axis=0).T
                        else:
                            processed_ydata=np.zeros(len(self.xdata))
                    self.ProcessedFrame.ax.plot(self.xdata,processed_ydata)
                    self.ProcessedFrame.fig.set_tight_layout(True)
                    self.ProcessedFrame.graph.draw()
                t_aft_process = time.time()
                self.ProcessingTime = t_aft_process-t_bef_process

                self.t_bef_save = time.time()
                # Check if save data button is on and save data
                if (self.SaveDataButtonStatus):
                    
                    # with concurrent.futures.ThreadPoolExecutor() as executor: # threading input and output tasks
                    savethread = threading.Thread(target = self.savedatathread)
                    savethread.start()
                    # time_data = np.array(self.xdata_new)
                    # time_data = time_data[np.newaxis,:]
                    # abs_time = np.array(self.abs_timestamp)
                    # abs_time = abs_time[np.newaxis,:]
                    # temp_data = np.append(time_data,np.array(self.ydata_new),axis=0)
                    # temp_data = np.append(abs_time,temp_data,axis=0).T

                    # pd_cols = np.insert(self.Fig_titles.values,0,"Time")
                    # pd_cols = np.insert(pd_cols,0,"Absolute_Time")
                    # self.SaveDataFrame = pd.DataFrame(columns=pd_cols, data = temp_data)
                    # # print(self.SaveDataFrame)

                    # if os.path.isfile(self.datafile_name+'.parquet'):

                    #     # old_pq = pd.read_parquet(self.datafile_name+'.parquet')
                    #     table = pq.read_table(self.datafile_name+'.parquet')
                    #     old_pq = table.to_pandas()
                    #     new_df = pd.concat([old_pq,self.SaveDataFrame],ignore_index=True)
                    # else:
                    #     new_df = self.SaveDataFrame
                    # table = pa.Table.from_pandas(new_df)
                    # pq.write_table(table, self.datafile_name+'.parquet')
                    # # only for timing. parquet file is faster and smaller to write/read
                    # # self.SaveDataFrame.to_csv(self.datafile_name+'.csv',mode='a',header=not os.path.isfile(self.datafile_name+'.csv'))
                    
                    self.t_aft_save = time.time()
                    # self.SavingTime = t_aft_save-t_bef_save

                    # self.timing_np= np.append(self.timing_np,np.array([[self.xdata[-1],self.ProcessingTime, self.SavingTime]]),axis=0)
                    # self.TimeDataFrame = pd.DataFrame(data=self.timing_np, columns=["Last time entry (s)", "Processing Time (s)", "Saving time (s)"])
                    # table_timings = pa.Table.from_pandas(self.TimeDataFrame)
                    # pq.write_table(table_timings, self.datafile_name+'_time.parquet')
                    
                    t_ali = time.time()
                    if hasattr(self.AlicatSettingsFrame,"MFC1"):
                        self.AlicatSettingsFrame.SaveAlicats()
                        t_ali_save = time.time()
                        # print("Alicat Save time: " +str(t_ali_save - t_ali))
                    if (self.t_aft_save - t_bef_read)>1/self.ActualSamplingRate:
                        text_update = "!!!!!!!!!!!!!!!!!!!!! CAUTION: Saving and processing time is: {} s.\n This exceeeds sampling time. !!!!!!!!!!!!!!!!!".format(str(t_aft_save - t_bef_read))
                        self.inputSettingsFrame.UpdateLabel.config(text=text_update,bg= "red", fg= "white")
                        # print("!!!!!!!!!!!!!!!!!!!!! CAUTION: Saving and processing time is: "+str(t_aft_save - t_bef_read)+"s, which exceeeds sampling time. !!!!!!!!!!!!!!!!!")
                        # self.processedDataStatus = False
                        # self.showProcessedGraph()
                
            except:
                if hasattr(self.AlicatSettingsFrame,"MFC1"):
                    print("Exception occured. Alicat flows will be set to zero and acquisition will stop.")
                    self.AlicatSettingsFrame.StopAlicatFlow()
                self.stopTask()
                the_type, the_value, the_traceback = sys.exc_info()
                print(the_type, ': ', the_value, traceback.print_tb(the_traceback))

        #check if the task should sleep or stop
        if(self.continueRunning):
            self.master.after(10, self.runTask)
        else:
            self.run_counter =0
            self.save_tdms = False
            self.task.task.stop()
            self.task.task.close()
            self.inputSettingsFrame.startButton['state'] = 'enabled'

    def stopTask(self):
        #call back for the "stop task" button
        if self.SaveDataButtonStatus:
            self.inputSettingsFrame.saveDataButton.config(image=self.off)
            self.SaveDataButtonStatus = False
            self.SaveEndTime = datetime.now()
            print("Duration of saved data: "+ str(self.SaveEndTime- self.SaveStartTime))
        self.continueRunning = False
        if hasattr(self,"Dashthread"):
            self.Dashthread.terminate()
    
    def SelectSaveFile(self):
        f = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
        self.filePath = f.name
        self.inputSettingsFrame.savePath.set(self.filePath)
        f.close()
    
    def SelectConfigFile(self):
        f = filedialog.askopenfilename(title="Select Configuration File", initialdir='/',filetypes=[("CSV Files", "*.csv")])
        print(f)
        self.ConfigfilePath = f
        self.inputSettingsFrame.ConfigFileStr.set(self.ConfigfilePath)

        self.initialize_config(f)
        self.ProcessedFrame.reset_options()
        self.ProcessedFrame.ScaleSelecter.set(self.Fig_titles[0])
    
    def SaveData(self):
        if self.SaveDataButtonStatus:
            self.inputSettingsFrame.saveDataButton.config(image=self.off)
            self.Dashthread.terminate()
            self.SaveDataButtonStatus = False
            self.SaveEndTime = datetime.now()
            print("Duration of saved data: "+ str(self.SaveEndTime- self.SaveStartTime))

        else:
            savebuttime = time.time()
            self.run_counter =0
            self.save_tdms = True
            self.inputSettingsFrame.saveDataButton.config(image=self.on)
            self.SaveDataButtonStatus = True
            finalsavepath = '/'.join(self.inputSettingsFrame.savePath.get().split("/")[:-1])+'/'
            finalsavename = self.inputSettingsFrame.savePath.get().split("/")[-1].split(".")[0]
            self.SaveStartTime = datetime.now()
            if finalsavepath =='/': # file is saved in the current directory
                if 'Exp' in self.inputSettingsFrame.ExpType.get():
                    dir_num = '02_'
                else:
                    dir_num = '01_'
                Project_Name = self.inputSettingsFrame.ProjectName.get()
                finalsavepath = '../../'+dir_num+self.inputSettingsFrame.ExpType.get()+'/'
                finalsavepath = self.SaveStartTime.strftime(finalsavepath+"%Y"+Project_Name+'/')
            
            if not os.path.exists(finalsavepath):
                os.makedirs(finalsavepath)
            self.datafile_name = self.SaveStartTime.strftime(finalsavepath+"%Y%m%d_%H%M_"+finalsavename+'_'+self.inputSettingsFrame.ProjectName.get()+'_'+self.inputSettingsFrame.OperatorName.get())
            with open("DAQsavefilepath.txt",'w') as f:
                f.write(self.datafile_name+'.parquet')
                f.write("\n")
                f.write(self.inputSettingsFrame.ConfigPathEntry.get())

            self.infoFilePath = self.SaveStartTime.strftime(finalsavepath+"%Y%m%d_%H%M_"+finalsavename+'_'+self.inputSettingsFrame.ProjectName.get()+'_'+self.inputSettingsFrame.OperatorName.get()+'.info')
            with open(self.infoFilePath,'w') as f:
                f.write('TestDataFile:' + self.datafile_name+'.parquet')
                f.write("\n")
                f.write('ConfigFilePath:' + self.inputSettingsFrame.ConfigPathEntry.get())
            print("Saving Data here:"+ self.datafile_name)

            ###### DASH app visualizer in parallel #######
            ###### Will only work when app is not served in the debug mode #####
            self.Dashthread = multiprocessing.Process(target=create_dash_app,name="DashVisualizer")# Thread(target=create_Dashapp,name="DashVisualizer",daemon=True)
            self.Dashthread.start()

            self.ydata=np.empty((len(self.ChanConfig['Device']),0))
            self.xdata=np.array([0])
            savebutprocesstime = time.time()
            print("Time delay to begin saving: " +str(savebutprocesstime-savebuttime))            
        
    def showProcessedGraph(self):
        if self.processedDataStatus:
            self.ProcessedFrame.grid_forget()
            self.inputSettingsFrame.ProcessedSwitcher.config(image=self.off)
            self.processedDataStatus = False
        else:
            self.ProcessedFrame.grid(row=1, column=1, sticky="ew", pady=(20,0), padx=(20,20), ipady=10)
            self.inputSettingsFrame.ProcessedSwitcher.config(image=self.on)
            self.processedDataStatus = True

# Will be used to create a Dash server for plotting and post processing the data
class OptionalProcessedDataVisualizer(tk.LabelFrame):

    def __init__(self, parent, title):
        tk.LabelFrame.__init__(self, parent, text=title, labelanchor='n')
        self.parent = parent
        self.grid_columnconfigure(0, weight=1)
        self.xPadding = (30,30)
        
        self.create_widgets()

    def create_widgets(self):
        self.cautionaryLabel = ttk.Label(self,text="Use this for Channel checks. Flip this off while saving the data.")
        self.cautionaryLabel.grid(row=0,column=0,columnspan=4,sticky='n')

        self.fig = Figure(figsize=(5,4), dpi=100,tight_layout=True)
        self.ax=self.fig.add_subplot(1,1,1)
        self.graph = FigureCanvasTkAgg(self.fig, self)
        self.graph.draw()
        self.graph.get_tk_widget().grid(row=2,columnspan=4)

        self.ProcessType = tk.StringVar(self)
        self.processOptions = ttk.OptionMenu(self, self.ProcessType, self.parent.processing_options[0], *self.parent.processing_options)
        self.processOptions.grid(row=1, column=0, sticky='w', padx=(0,0), pady=(10,10))

        self.ScaleSelecter = tk.StringVar(self)
        self.ScaleOptions = ttk.OptionMenu(self, self.ScaleSelecter, self.parent.Fig_titles[0], *self.parent.Fig_titles)
        self.ScaleOptions.grid(row=1, column=1, sticky='w', padx=(0,0), pady=(10,10))

        self.scalbytext = ttk.Label(self,text="Scale by:")
        self.scalbytext.grid(row=1,column=2)

        edc = (self.register(self.checkfloat))
        self.ScaleValue = tk.StringVar(self)
        self.updateScale()
        self.ScaleValueEntry = ttk.Entry(self,validate='all', validatecommand=(edc, '%P'), textvariable=self.ScaleValue)
        self.ScaleValueEntry.grid(row=1, column=3, sticky='w', padx=(0,0), pady=(10,10))

        self.ScaleSelecter.trace_add('write',self.updateScale)
        self.ProcessType.trace_add('write',self.updateProcessingOptions)

    def reset_options(self):
        new_options = self.parent.Fig_titles
        menu = self.ScaleOptions['menu']
        menu.delete(0, 'end')

        for new_opt in new_options:
            menu.add_radiobutton(label=new_opt, command=tk._setit(self.ScaleSelecter,new_opt)) #command=lambda chany=new_opt: ChanFrame.dd_chanvar.set(chany))
        
        for i in range(0, menu.index("end")+1):
            menu.entryconfig(i, variable=self.ScaleSelecter)

    def updateScale(self,*args):
        try:
            chan_location = self.parent.Fig_titles.index[self.parent.Fig_titles==self.ScaleSelecter.get()]
            self.ScaleValue.set(self.parent.ChanConfig["ScaleFactor"][chan_location])
        except KeyError:
            self.ScaleValue.set('1')
        
    def updateProcessingOptions(self,*args):
        if self.ProcessType.get()==self.parent.processing_options[0]:
            self.ScaleOptions.grid(row=1,column=1)
            self.scalbytext.grid(row=1,column=2)
            self.ScaleValueEntry.grid(row=1,column=3)
            self.ax.cla()

            if hasattr(self,'menubutton'):
                self.menubutton.grid_forget()

        if self.ProcessType.get()==self.parent.processing_options[1]:
            self.ScaleOptions.grid_forget()
            self.scalbytext.grid_forget()
            self.ScaleValueEntry.grid_forget()
            self.ax.cla()

            self.menubutton = tk.Menubutton(self, text="Choose channels for averaging", 
                                   indicatoron=True, borderwidth=1, relief="raised")
            self.menu = tk.Menu(self.menubutton, tearoff=False)
            self.menubutton.configure(menu=self.menu)
            self.menubutton.grid(row=1,column=1,columnspan=3)

            self.avg_choices = []
            self.choices = {}
            for choice in self.parent.Fig_titles:
                self.choices[choice] = tk.IntVar(value=0)
                self.menu.add_checkbutton(label=choice, variable=self.choices[choice], 
                                    onvalue=1, offvalue=0, 
                                    command=self.createAvgChoices)
    def createAvgChoices(self):
        self.avg_choices = [name for name, var in self.choices.items() if var.get()==1]
    
    def checkfloat(self, P):
        if P.replace('.','',1).isdigit(): # Check for float
            return True
        else:
            return False
    
    def show(self):
        self.grid(row=0,column=1)

class inputSettings(tk.LabelFrame):

    def __init__(self, parent, title):
        tk.LabelFrame.__init__(self, parent, text=title, labelanchor='n')
        self.parent = parent
        self.xPadding = (10,10)
        self.create_widgets()

    def create_widgets(self):
        nospaces = (self.register(self.checkspaces))
        # onlydigits = (self.register(self.checkdigits))
        onlyfloats = (self.register(self.checkfloat))

        self.FileRenameLabel = ttk.Label(self, text="File name be renamed to include \nDate, Name, and Project/Fuel")
        self.FileRenameLabel.grid(row=0, column=0, columnspan=2,rowspan=2, sticky='n', padx=self.xPadding, pady=(10,0))

        self.ExpType = tk.StringVar()
        self.ExpType.set("ExperimentData")
        self.ExperimentData = ttk.Radiobutton(self, text="ExperimentData", value="ExperimentData", variable=self.ExpType)#, command=self.parent.sel)
        self.ExperimentData.grid(row=2, column=0, columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))
        self.CalibrationData = ttk.Radiobutton(self, text="CalibrationData", value="CalibrationData", variable=self.ExpType)#, command=self.parent.sel)
        self.CalibrationData.grid(row=2, column=1, columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))

        self.ConfigFilePath = ttk.Label(self, text="Config file path")
        self.ConfigFilePath.grid(row=3, column=0, columnspan=2, sticky='w', padx=self.xPadding, pady=(10,0))

        self.ConfigFileStr = tk.StringVar(self)
        self.ConfigFileStr.set(self.parent.DefConfig)
        self.ConfigPathEntry = tk.Entry(self,textvariable=self.ConfigFileStr)
        self.ConfigPathEntry.grid(row=4, column=0, columnspan=4, sticky='ew', padx=self.xPadding)

        self.ConfigFileButton = ttk.Button(self,text="Select Configuration File",command=self.parent.SelectConfigFile)
        self.ConfigFileButton.grid(row=5,column=0,padx=self.xPadding,pady=(10,0),sticky='w')

        self.sampleRateLabel = ttk.Label(self, text="Sample Rate")
        self.sampleRateLabel.grid(row=6, column=0, sticky='w', padx=self.xPadding, pady=(10,0))

        self.SamRateText = tk.StringVar(self)
        self.SamRateText.set("10")
        self.sampleRateEntry = ttk.Entry(self,textvariable=self.SamRateText, validate='all', validatecommand=(onlyfloats, '%P'))
        self.sampleRateEntry.grid(row=6, column=1, sticky='ew', padx=self.xPadding)

        self.SaveFilePathText = ttk.Label(self, text="Test name")
        self.SaveFilePathText.grid(row=7, column=0, columnspan=2, sticky='w', padx=self.xPadding, pady=(10,0))

        self.savePath = tk.StringVar(self)
        self.savePath.set(self.parent.filePath)
        self.savePathEntry = tk.Entry(self,textvariable=self.savePath)
        self.savePathEntry.grid(row=8, column=0, columnspan=4, sticky='ew', padx=self.xPadding)

        self.saveFileButton = ttk.Button(self,text="Select file destination for data",command=self.parent.SelectSaveFile)
        self.saveFileButton.grid(row=9,column=0,padx=self.xPadding,pady=(10,0),sticky='w')
        
        self.startButton = ttk.Button(self, text="Start Acquisition", command=self.parent.startTask)
        self.startButton.grid(row=10, column=0, sticky='w', padx=self.xPadding, pady=(10,0))

        self.stopButton = ttk.Button(self, text="Stop Acquisition", command=self.parent.stopTask)
        self.stopButton.grid(row=10, column=1, sticky='e', padx=self.xPadding, pady=(10,0))
        
        self.NameStr = tk.StringVar(self)
        self.NameStr.set("Dushyant")
        self.NameLabel = ttk.Label(self, text="Enter your name")
        self.NameLabel.grid(row=11, column=0, sticky='w', padx=self.xPadding, pady=(10,0))
        self.OperatorName = ttk.Entry(self, textvariable=self.NameStr,validate='all', validatecommand=(nospaces, '%P'))
        self.OperatorName.grid(row=11, column=1, sticky='w', padx=(0,0), pady=(10,0))

        self.ProjectStr = tk.StringVar(self)
        self.ProjectStr.set("DelcoCalorimetry")
        self.ProjectLabel = ttk.Label(self, text="Enter Project/Fuel Name")
        self.ProjectLabel.grid(row=12, column=0, sticky='w', padx=self.xPadding, pady=(10,0))
        self.ProjectName = ttk.Entry(self, textvariable=self.ProjectStr,validate='all', validatecommand=(nospaces, '%P'))
        self.ProjectName.grid(row=12, column=1, sticky='w', padx=(0,0), pady=(10,0))

        self.SaveLabel = ttk.Label(self, text="Switch on to save data")
        self.SaveLabel.grid(row=13, column=0, sticky='w', padx=self.xPadding, pady=(10,0))
        self.saveDataButton = ttk.Button(self, image = self.parent.off, command=self.parent.SaveData)
        self.saveDataButton.grid(row=13, column=1, sticky='e', padx=self.xPadding, pady=(10,0))

        self.ShowProcessed = ttk.Label(self, text="Flip to view data")
        self.ShowProcessed.grid(row=14, column=0, sticky='w', padx=self.xPadding, pady=(10,0))
        self.ProcessedSwitcher = ttk.Button(self, image = self.parent.on, command=self.parent.showProcessedGraph)
        self.ProcessedSwitcher.grid(row=14, column=1, sticky='e', padx=self.xPadding, pady=(10,0))

        self.UpdateLabel = tk.Label(self, text="Status update will be posted here")
        self.UpdateLabel.grid(row=15, column=0, rowspan=2, columnspan=2, sticky='n', padx=self.xPadding, pady=(10,0))

    def checkspaces(self, P):
        if ' ' not in P or P == "":
            return True
        else:
            return False
    
    def checkdigits(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
    
    def checkfloat(self, P):
        if P.replace('.','',1).isdigit(): # Check for float
            return True
        else:
            return False

class App2MainFrame(tk.Frame):

    def __init__(self,parent,title): 
        tk.Frame.__init__(self, parent)
        #Configure root tk class
        self.parent = parent
        self.title = title

        self.pack(fill=tk.BOTH,expand=1)
        self.option_add("*Font", "aerial")

        #Set the font for the Label widget
        self.option_add("*Label.Font", "aerial 12 bold")

        self.my_canvas = CanvasFrame(self)
        self.my_canvas.configure(highlightthickness  = 4, 
            highlightbackground = "#CDAA7D")
        
        self.App2Frame = PyDAQContinuousInput(self.my_canvas,title="PyDAQApp2")
        self.my_canvas.create_window((30, 30), window=self.App2Frame, anchor="nw")

        # scrollbar
        self.my_yscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.my_canvas.yview)
        self.YScrollFrame = ScrollbarFrame(self.my_canvas)
        # configure the canvas
        self.YScrollFrame.bind(
            '<Configure>', lambda e: self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all"))
        )
        self.my_canvas.create_window((0, 0), window=self.YScrollFrame, anchor="nw")
        self.my_canvas.configure(yscrollcommand=self.my_yscrollbar.set)
        self.my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.my_yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.run = False
        self.pack(expand=True,fill="both")

if __name__ == "__main__":
    class MainView(tk.Frame):
        def __init__(self,master,title):
            tk.Frame.__init__(self,master)
            self.master = master
            self.master.title("PyDAQ Continous Input")
            self.master.iconbitmap('Icons/fsri-logo.ico')
            self.master.geometry("1020x600")

            self.pagey = App2MainFrame(self,title)
            self.exitButton = tk.Button(self.pagey.my_canvas, text="Exit", command=self.ExitAll,bg="#A52A2A",fg="White")
            self.exitButton.pack(anchor='nw',padx=30,pady=30,ipadx=10)
        
        def ExitAll(self):
            self.quit()
            self.destroy()

    #Runs PyDAQ
    root = tk.Tk()
    app = MainView(root,title="App2PyDAQ")
    app.pack(side="top", fill="both", expand=True)

    #start the application
    app.mainloop()