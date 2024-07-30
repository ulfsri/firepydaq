import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import itertools
import os
import time
import matplotlib.pyplot as plt
import polars as pl
from datetime import datetime,timedelta

class SavepqTester():
    def __init__(self, name,parquet_file):
        self.name = name
        self.time_iterator = itertools.count()
        self.labels_to_save = ["0","1"]
        self.parquet_file = parquet_file
        if os.path.isfile(self.parquet_file):
            os.remove(self.parquet_file)
    
    def save_data_thread(self):

        """
        x: new x data
        y: new y data

        """
        self.x, self.y = self.generate_xy((10,2))
        t_now = datetime.now()
        tdiff_array = np.linspace(1/10,1,10)
        self.abs_timestamp = [[(t_now+timedelta(seconds=sec)).strftime("%d/%m/%Y, %H:%M:%S:%f)")[:-3]] for sec in tdiff_array]
        # print(self.x,self.y)
        self.save_data = np.append(self.x,self.y,axis=1)
        self.save_data = np.append(self.abs_timestamp, self.save_data,axis=1)
        # print(self.save_data)

        pd_cols = np.insert(self.labels_to_save, 0 ,"Time")
        pd_cols = np.insert(pd_cols, 0 ,"Abs Time")
        self.SaveDataFrame = pd.DataFrame(columns = pd_cols, data = self.save_data)

        if os.path.isfile(self.parquet_file): # Appendage if file exists
            table = pq.read_table(self.parquet_file)
            old_pq = table.to_pandas()
            new_df = pd.concat([old_pq, self.SaveDataFrame], ignore_index=True)
        else: # new file if no file exists
            new_df = self.SaveDataFrame
        # print(new_df)
        table = pa.Table.from_pandas(new_df)
        # print(os.path.isfile(self.parquet_file))
        pq.write_table(table, self.parquet_file)
        return

    def generate_xy(self,shape):
        return (np.array([[next(self.time_iterator)/10] for i in range(shape[0])]),np.random.rand(shape[0],shape[1]))

class Readpq():
    def __init__(self) -> None:
        super().__init__()
        self.fig,self.ax = plt.subplots()

    def read_pq(self,file):
        table = pq.read_table(file)
        self.df = table.to_pandas()
        self.df.iloc[:,2:] = self.df.iloc[:,2:].astype(float)
        return self.df

    def simple_plot(self,column):
        self.ax.plot(self.df.iloc[:,1],self.df.loc[:,column])

file = "../../tests/pyarrowSaving.parquet"
test = SavepqTester("Testing pyarrow",file)
read_test = Readpq()
save_for = 2
t_old = time.time()
t_delta = 0
while t_delta<save_for:
    time.sleep(1)
    test.save_data_thread()
    if t_delta == 0:
        print("Saving Data")
    t_new = time.time()
    t_delta = t_new - t_old
    print(t_delta)
    if abs(t_delta%5 - 0) < 0.01:
        print("Saved data until: "+str(t_delta)+" s")

    read_test.read_pq(file)
    read_test.simple_plot("0")
schema_dict = pl.read_parquet_schema(file)
print(schema_dict)

plt.show()

