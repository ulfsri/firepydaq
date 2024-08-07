# General Utilities
import pandas as pd
import pyarrow.parquet as pq

def read_pq(file):
    """Reads parquet file

    Parameters
    ---------
    file: path
        path string to a .parquet file

    Returns
    -------
    df: pandas DataFrame
        Parquet file converted into pandas DataFrame 
    """
    table = pq.read_table(file)
    df = table.to_pandas()
    df.iloc[:,1:] = df.iloc[:,1:].astype(float)
    return df
