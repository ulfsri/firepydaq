# By: Dushyant M. Chaudhari
# Last Updated: Feb 20 2024

import tkinter as tk
import numpy as np
from tkinter import ttk
from datetime import datetime
from Utils import check_system_config,default_configFilePath
from Utils import CanvasFrame, ScrollbarFrame

from tkinter import filedialog
import copy
import re
import itertools
import pandas as pd

sys_config = check_system_config()
Measurement_types = ['Thermocouple','Voltage','Current']

class SecondaryFrame(tk.Frame):
    def __init__(self, parent, title):
        tk.Frame.__init__(self, parent)
        self.title = title
        self.parent = parent
        self.xPadding = (30,30)

        self.Config_list = ["Device","Channel","Measurement","min_val","max_val","Fig_title"]
        self.my_entries= pd.DataFrame(columns =["Panel","Channel","Scale","Offset","Label","Type","Chart","Min","Max","Device"])#dict([(k, []) for k in self.Config_list])
        self.AllChanFrames=[]
        self.entry_row=2
        self.xPadding = (10,10)
        self.ydata=np.array([])
        self.xdata=np.array([0])
        self.temp_chan_dict = copy.deepcopy(sys_config.Chans)

        self.DefaultConfigFile = default_configFilePath
        self.ConfigfileValue = self.DefaultConfigFile
        self.create_widgets()

        self.option_add("*Font", "aerial")
        #Set the font for the Label widget
        self.option_add("*Label.Font", "aerial 14 bold")
    
    def SelectConfigFile(self):
        f = filedialog.askopenfilename(title="Select Configuration File", initialdir='/',filetypes=[("CSV Files", "*.csv")])
        if f:
            self.ConfigfileValue = f
        else:
            self.ConfigfileValue = self.DefaultConfigFile
        self.ConfigFileStr.set(self.ConfigfileValue)
    
    def ClearAllConfig(self):
        if hasattr(self, 'AllChanFrames'):
            for i in self.AllChanFrames:
                i.destroy()
                self.entry_row=2
            
        self.my_entries= pd.DataFrame(columns =["Panel","Device","Channel","Scale","Offset","Label","Type","Chart","Min","Max"])
    
    def UpdatedConfig(self): 
        self.File_config = pd.read_csv(self.ConfigfileValue,header=0)
        self.ClearAllConfig()
        for i in self.File_config.index:
            self.AddChannel()
            self.ChannelFrame.dd_variable.set(self.File_config.loc[i,"Device"])
            self.ChannelFrame.dd_chanvar.set(self.File_config.loc[i,"Channel"])
            self.ChannelFrame.dd_measure.set(self.File_config.loc[i,"Type"])
            self.ChannelFrame.def_minVal.set(self.File_config.loc[i,"Min"])
            self.ChannelFrame.def_maxVal.set(self.File_config.loc[i,"Max"])
            self.ChannelFrame.ChanStr.set(self.File_config.loc[i,"Label"])
            self.ChannelFrame.ChartStr.set(self.File_config.loc[i,"Chart"])
            self.ChannelFrame.scalFactorVar.set(self.File_config.loc[i,"Scale"])
            self.ChannelFrame.OffsetTextVar.set(self.File_config.loc[i,"Offset"])
    
    def create_widgets(self):
        self.NameStr = tk.StringVar()
        self.NameStr.set("Dushyant")
        self.NameLabel = ttk.Label(self, text="Enter your name: ")
        self.NameLabel.grid(row=0, column=0, sticky='w', padx=self.xPadding, pady=(10,0))
        self.OperatorName = ttk.Entry(self, textvariable=self.NameStr)
        self.OperatorName.grid(row=0, column=1, sticky='w', padx=(0,0), pady=(10,0))
        self.OperatorName.columnconfigure(0,weight=3)

        self.ProjectStr = tk.StringVar()
        self.ProjectStr.set("DelcoCalorimetry")
        self.ProjectLabel = ttk.Label(self, text="Enter project name: ")
        self.ProjectLabel.grid(row=0, column=2, sticky='e', padx=(0,0), pady=(10,0))
        self.ProjectrName = ttk.Entry(self, textvariable=self.ProjectStr)
        self.ProjectrName.grid(row=0, column=3, sticky='w', padx=(0,0), pady=(10,0))

        self.ConfigFilePath = ttk.Label(self, text="Config file path:")
        self.ConfigFilePath.grid(row=0, column=4, columnspan=1, sticky='e', padx=self.xPadding)

        self.ConfigFileStr = tk.StringVar(self)
        self.ConfigFileStr.set(self.DefaultConfigFile)
        self.ConfigPathEntry = tk.Entry(self,textvariable=self.ConfigFileStr)
        self.ConfigPathEntry.grid(row=0, column=5, columnspan=1, sticky='ew', padx=self.xPadding)
        self.myscroll = ttk.Scrollbar(self, orient='horizontal', command=self.ConfigPathEntry.xview)
        self.myscroll.grid(row=1,column=5, sticky='new')
        self.ConfigPathEntry.config(xscrollcommand=self.myscroll.set)

        self.ConfigFileButton = ttk.Button(self,text="Select Configuration File",command=self.SelectConfigFile)
        self.ConfigFileButton.grid(row=0,column=6,padx=(0,0),sticky='w')

        self.UpdateConfig = ttk.Button(self,text="Update Configuration Using File",command=self.UpdatedConfig)
        self.UpdateConfig.grid(row=1,column=6,padx=(0,0),sticky='w',pady=(10,0))

        self.addent = ttk.Button(self, text = "Add Analog Input",command = self.AddChannel)
        self.addent.grid(row = 1, column = 0, sticky='w', padx=self.xPadding, pady=(10,0),ipadx=10)
        self.getent = ttk.Button(self,text='Create Config File', command= self.create_config)
        self.getent.grid(row=1, column=1, sticky='w', padx=self.xPadding, pady=(10,0),ipadx=10)

        self.RemChanText = ttk.Label(self, text="Select channel to remove: ")
        self.RemChanText.grid(row=1, column=2, sticky='e', padx=(10,10), pady=(10,0))

        self.dd_remvar = tk.StringVar(self)
        self.remopts = ttk.OptionMenu(self, self.dd_remvar, self.entry_row-1, *np.arange(1,self.entry_row-1))
        self.remopts.grid(row=1, column=3, sticky='e', padx=(10,10), pady=(10,0))
        
        self.RemChan = ttk.Button(self,text='Remove this channel',takefocus=False, command=self.RemoveChannel)
        self.RemChan.grid(row=1, sticky='w', column=4,padx=(0,0), pady=(10,0),ipadx=10)

        self.ClearAll = ttk.Button(self,text='Clear All',takefocus=False, command=self.ClearAllConfig)
        self.ClearAll.grid(row=1, sticky='e', column=8,padx=(40,10), pady=(10,0),ipadx=10)

        if self.my_entries.empty:
            self.RemChan['state'] = 'disabled'
    
    def AddChannel(self):
        self.ChannelFrame = ChannelEntry(self,title="Channel #"+str(self.entry_row-1))
        self.ChannelFrame.grid(row=self.entry_row, column=0, columnspan=10, pady=(0,0), padx=(10,10), ipady=10)

        self.my_entries = pd.concat([self.my_entries,self.ChannelFrame.TheEntry])
        self.my_entries.reset_index(inplace=True,drop=True)
        
        self.entry_row+=1
        
        self.RemButUpdater()
        self.AllChanFrames.append(self.ChannelFrame)
    
    def RemoveChannel(self):
        remove_frame = self.dd_remvar.get()
        poco_loco = int(remove_frame)-1
        print("Removing Channel #"+str(poco_loco+1))
        
        self.my_entries.drop(poco_loco,axis=0,inplace=True)
        self.my_entries.reset_index(inplace=True,drop=True)

        self.AllChanFrames[poco_loco].destroy()
        del self.AllChanFrames[poco_loco]

        self.entry_row = len(self.AllChanFrames)+2
        for n,ChanFrame in enumerate(self.AllChanFrames):
            # print(ChanFrame)
            ChanFrame.updated_chan_opts = ChanFrame.getUpdatedChanEntries(except_col=poco_loco)
            new_options = ChanFrame.updated_chan_opts[ChanFrame.dd_variable.get()]

            menu = ChanFrame.chanopts['menu']
            menu.delete(0, 'end')

            for new_opt in new_options:
                menu.add_radiobutton(label=new_opt, command=tk._setit(ChanFrame.dd_chanvar,new_opt)) #command=lambda chany=new_opt: ChanFrame.dd_chanvar.set(chany))
            
            for i in range(0, menu.index("end")+1):
                menu.entryconfig(i, variable=ChanFrame.dd_chanvar)
            ChanFrame.configure(text="Channel #"+str(n+1))
            ChanFrame.grid(row=n+2,column=0, columnspan=10, pady=(0,0), padx=(10,10), ipady=10)
       
        self.dd_remvar.set('1')
        self.RemButUpdater()
    
    def RemButUpdater(self):
        remopts_list = np.arange(1,self.entry_row-1)
        menu = self.remopts['menu']
        menu.delete(0, 'end')

        for rem_row in remopts_list:
            menu.add_radiobutton(label=rem_row, command=lambda row_loc=rem_row: self.dd_remvar.set(row_loc))
        
        if not self.my_entries.empty:
            for i in range(0, menu.index("end")+1):
                menu.entryconfig(i, variable=self.dd_remvar)
            self.RemChan['state'] = 'enabled'
        else:
            self.RemChan['state'] = 'disabled'
    
    def create_config(self):
        self.config = {}
        for i in self.my_entries.columns:
            self.config[i] = [val.get() for val in self.my_entries.loc[:,i]]
        
        print(self.config)
        now = datetime.now()
        config_filename = "../ConfigFiles/"+now.strftime("%Y%m%d_%H%M_"+self.ProjectrName.get()+"_"+ self.OperatorName.get())
        print(config_filename)
        df_config = pd.DataFrame(self.config)
        df_config.to_csv(config_filename+'.csv')

class ChannelEntry(ttk.LabelFrame):

    def __init__(self, parent, title):
        ttk.LabelFrame.__init__(self, parent, text=title, labelanchor='n')
        self.title = title
        self.parent = parent
        self.xPadding = (10,10)
        
        self.create_widgets()
    
    def getUpdatedChanEntries(self,except_col=''): # do not consider current column for used channel update
        if not self.parent.my_entries.empty:
            self.updated_chan_opts={}
            # print(except_col)
            # print(self.parent.my_entries["Channel"])

            for i in sys_config.Devs_names:
                locs_forthisdevice = [loc for loc,ele in enumerate(self.parent.my_entries["Device"]) if i==ele.get()]
                # print(locs_forthisdevice)
                devs_registerd = [self.parent.my_entries.loc[i,"Device"].get() for i in locs_forthisdevice]
                if devs_registerd:
                    used_chans = [(no,k.get()) for no,k in enumerate(self.parent.my_entries["Channel"]) if no in locs_forthisdevice]
                    used_chan_locs,used_chans = zip(*used_chans)
                    # print(used_chan_locs,used_chans)
                    if except_col =='':
                        used_chans = used_chans
                    elif except_col in used_chan_locs:
                        # print('there')
                        col_pop_index = used_chan_locs.index(except_col)
                        used_chans = list(used_chans)
                        used_chans.pop(col_pop_index)
                        # print(used_chans)
                    else:
                        used_chans =''
                    chan_list = self.parent.temp_chan_dict[i]
                    filtered = [ele for ele in chan_list if ele not in used_chans]
                    # print(filtered)
                    self.updated_chan_opts[i] = filtered
                else:
                    self.updated_chan_opts[i] = self.parent.temp_chan_dict[i]
        else:
            self.updated_chan_opts = self.parent.temp_chan_dict
        return self.updated_chan_opts
    
    def create_widgets(self):
        edc = (self.register(self.checkdigits))

        col_init = itertools.count()
        self.PanelLabel = ttk.Label(self, text="Panel#: ")
        self.PanelLabel.grid(row=0, column=next(col_init), columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))
        self.PanelVar = tk.StringVar(self)
        self.PanelVar.set("1")
        self.PanelEntry = tk.Entry(self, width=4, validate='all', validatecommand=(edc, '%P'), textvariable=self.PanelVar)
        self.PanelEntry.grid(row=0, column=next(col_init), sticky='w', padx=self.xPadding, pady=(10,0))

        self.DevsLabel = ttk.Label(self, text="Device: ")
        self.DevsLabel.grid(row=0, column=next(col_init), columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))
        self.dd_variable = tk.StringVar(self)
        self.dd_variable.set(sys_config.Devs_names[0])
        self.daqopts = ttk.OptionMenu(self, self.dd_variable, sys_config.Devs_names[0], *sys_config.Devs_names)
        self.daqopts.grid(row=0, column=next(col_init), sticky='w', padx=self.xPadding, pady=(10,0))

        self.ChanLabel = ttk.Label(self, text="Channel: ")
        self.ChanLabel.grid(row=0, column=next(col_init), columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))
        self.dd_chanvar = tk.StringVar(self)
        self.updated_chan_opts = self.getUpdatedChanEntries()
        # print(self.updated_chan_opts)
        self.dd_variable.trace_add('write',self.update_dependentChans)
        self.chanopts = ttk.OptionMenu(self, self.dd_chanvar, self.updated_chan_opts[self.dd_variable.get()][0], *self.updated_chan_opts[self.dd_variable.get()])
        self.chanopts.grid(row=0, column=next(col_init), sticky='w', padx=self.xPadding, pady=(10,0))

        self.MeasLabel = ttk.Label(self, text="Measurement Type: ")
        self.MeasLabel.grid(row=0, column=next(col_init), columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))
        self.dd_measure = tk.StringVar(self)
        self.dd_measure.set(Measurement_types[0])
        self.measureopts = ttk.OptionMenu(self, self.dd_measure, Measurement_types[0], *Measurement_types)
        self.measureopts.grid(row=0, column=next(col_init), sticky='w', padx=self.xPadding, pady=(10,0))

        self.minValText = ttk.Label(self, text="AI.Min:")
        self.minValText.grid(row=0, column=next(col_init), sticky='w', padx=self.xPadding, pady=(10,0))
        self.def_minVal = tk.StringVar(self)
        self.def_minVal.set("0")
        self.min_val = tk.Entry(self, width=4, validate='all', validatecommand=(edc, '%P'),textvariable=self.def_minVal)
        self.min_val.grid(row=0, column=next(col_init), sticky='w', padx=self.xPadding, pady=(10,0))

        self.maxValText = ttk.Label(self, text="AI.Max:")
        self.maxValText.grid(row=0, column=next(col_init), sticky='w', padx=(0,0), pady=(10,0))
        self.def_maxVal = tk.StringVar(self)
        self.def_maxVal.set("10")
        self.max_val = tk.Entry(self, width=4, validate='all', validatecommand=(edc, '%P'), textvariable=self.def_maxVal)
        self.max_val.grid(row=0, column=next(col_init), sticky='w', padx=self.xPadding, pady=(10,0))

        sec_rowcol = itertools.count()
        self.scalFactorText = ttk.Label(self, text="Scale:")
        self.scalFactorText.grid(row=1, column=next(sec_rowcol), sticky='w', padx=self.xPadding, pady=(10,0))
        self.scalFactorVar = tk.StringVar(self)
        self.scalFactorVar.set("1")
        self.ScaleEntry = tk.Entry(self, width=4, validate='all', validatecommand=(edc, '%P'), textvariable=self.scalFactorVar)
        self.ScaleEntry.grid(row=1, column=next(sec_rowcol), sticky='w', padx=self.xPadding, pady=(10,0))

        self.OffsetText = ttk.Label(self, text="Offset:")
        self.OffsetText.grid(row=1, column=next(sec_rowcol), sticky='w', padx=self.xPadding, pady=(10,0))
        self.OffsetTextVar = tk.StringVar(self)
        self.OffsetTextVar.set("0")
        self.OffsetEntry = tk.Entry(self, width=4, validate='all', validatecommand=(edc, '%P'), textvariable=self.OffsetTextVar)
        self.OffsetEntry.grid(row=1, column=next(sec_rowcol), sticky='w', padx=self.xPadding, pady=(10,0))

        # self.ChanFigSeparator = ttk.Separator(self, orient=tk.VERTICAL).grid(column=10, row=0, sticky='ns')

        self.ChanTitleText = ttk.Label(self, text="Label:")
        self.ChanTitleText.grid(row=1, column=next(sec_rowcol), sticky='w', padx=self.xPadding, pady=(10,0))
        self.ChanStr = tk.StringVar(self)
        self.ChanStr.set("Dev"+str(sys_config.Devs_names.index(self.dd_variable.get()))+ self.dd_chanvar.get())
        self.ChanTitleEntry = tk.Entry(self, width=8, textvariable=self.ChanStr)
        self.ChanTitleEntry.grid(row=1, column=next(sec_rowcol), sticky='w', padx=self.xPadding, pady=(10,0))

        self.ChartText = ttk.Label(self, text="Chart:")
        self.ChartText.grid(row=1, column=next(sec_rowcol), sticky='w', padx=self.xPadding, pady=(10,0))
        self.ChartStr = tk.StringVar(self)
        self.ChartStr.set("ChartForGrouping")
        self.ChartEntry = tk.Entry(self, width=8, textvariable=self.ChartStr)
        self.ChartEntry.grid(row=1, column=next(sec_rowcol), columnspan=4, sticky='w', padx=self.xPadding, pady=(10,0))

        self.TheEntry = pd.DataFrame(data = [[self.PanelVar,self.dd_variable,self.dd_chanvar, self.scalFactorVar, self.OffsetTextVar, self.ChanStr, self.dd_measure, self.ChartStr, self.def_minVal,self.def_maxVal]],
                                     columns =["Panel","Device","Channel","Scale","Offset","Label","Type","Chart","Min","Max"])
    
    def checkdigits(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
    
    def update_dependentChans(self,*args):
        except_col = int(re.findall(r"\d+",self.title)[0])-1 # ChannelFrames from second row
        # print(except_col)
        self.updated_chan_opts = self.getUpdatedChanEntries(except_col=except_col)
        device_chans = self.updated_chan_opts[self.dd_variable.get()] #sys_config.Chans
        
        menu = self.chanopts['menu']
        menu.delete(0, 'end')
        if device_chans:
            self.dd_chanvar.set(device_chans[0])
        else:
            self.dd_chanvar.set('')
            return

        for chan in device_chans:
            menu.add_command(label=chan, command=lambda chany=chan: self.dd_chanvar.set(chany))


class ConfigAppMainFrame(tk.Frame):

    def __init__(self,parent,title):
        tk.Frame.__init__(self, parent)
        #Configure root tk class
        self.parent = parent
        self.title = title

        self.pack(fill=tk.BOTH,expand=1)
        self.option_add("*Font", "aerial")

        #Set the font for the Label widget
        self.option_add("*Label.Font", "aerial 18 bold")

        self.my_canvas = CanvasFrame(self)
        self.my_canvas.configure(highlightthickness  = 0.5, 
            highlightbackground = "#CDB79E")

        # scrollbar
        self.my_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.my_canvas.yview)
        self.ScrollFrame = ScrollbarFrame(self.my_canvas)

        # configure the canvas
        self.ScrollFrame.bind(
            '<Configure>', lambda e: self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all"))
        )

        self.my_canvas.create_window((0, 0), window=self.ScrollFrame, anchor="nw")
        self.my_canvas.configure(yscrollcommand=self.my_scrollbar.set)

        self.my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.secFrame = SecondaryFrame(self.my_canvas,title="sec_frame")
        self.my_canvas.create_window((40, 40), window=self.secFrame, anchor="nw")
        self.my_canvas.configure(highlightthickness=4)

        self.run = False
        self.pack()


if __name__ == "__main__":
    class MainView(tk.Frame):
        def __init__(self,master,title):
            tk.Frame.__init__(self,master)
            self.master = master
            self.master.title("PyDAQ Continous Input")
            self.master.iconbitmap('Icons/fsri-logo.ico')
            self.master.geometry("1500x800")

            self.pagey = ConfigAppMainFrame(self,title)
            self.exitButton = tk.Button(self.pagey.my_canvas, text="Exit", command=self.ExitAll,bg="#A52A2A",fg="White")
            self.exitButton.pack(anchor='ne',padx=30,pady=30,ipadx=10)
        
        def ExitAll(self):
            self.quit()
            self.destroy()
    # Configuration app for PyDAQ
    root = tk.Tk()
    app = MainView(root,title="App1PyDAQConfig")
    app.pack(side="top", fill="both", expand=True)

    #start the application
    app.mainloop()