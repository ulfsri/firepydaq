#######################
# This script will first post processes experiment data by scaling them into respective units in real time ##
# Then, this will produce custom data fields based on predefined formulae in the formulae file ##
# All processed data will be saved in the same location as the experimental data
# By: Dushyant M. Chaudhari ##
# Updated: June 20, 2024 #####
#######################

import polars as pl
import re
import numpy as np
import sys
import json
# from .ErrorUtils import firepydaq_logger

class PostProcessData():
    """ An object that processes data based on the config and formulae file

    Attributes
    ---------
    arg_nos: int
        Number of arguments passed by the user

    Formulae_dict: dict
        A dictionary of functions that maps user-inputted functions in the formulae file to equivalent numpy functions.

        For example, `exp` used in a formulae file is converted into `np.exp` while executing the formulae

        This formulae_dict is defined in DAQUtils.py

    Errors: dict
        A dictionary that maps the label (or LHS) for which an error was encountered while parsing the formulae to the corresponding error.

    path_dict: dict
        Contains a dictionary that maps `datapath`,`configpath`, and `formulaepath`. 
        The items of the keys are read as `polars.DataFrame`

        `datapath` can be path to live data, or data collected after an experiment, or randomly created numpy array to validate formulae before acquisition begins.

        `configpath` can be path to the configuration file for the NI hardware that uses ni-daqmx driver.

        `formulaepath` can be a path to the formulae file. Optionally, if processing formulae needs to be skipped, the path is passed as an either an empty string ('').
        Formulae file should use the variables defined in the `Label` column of the config file. The formulae file will be processed in the order that the formulae appears, from the topmost row to the bottom.

    data_dict: dict
        Contains a dictionary that maps the keys `data`, `config`, and `formulae` to the data read from `datapath`, `configpath`, and `formulaepath` in `path_dict`
        The items of the keys are read as `polars.DataFrame`
        
        `data` can be live data, data collected after an experiment, or randomly created numpy array to validate formulae before acquisition begins.

        `config` is the NI configuration file.

        `formulae` is the the formulae stored as a DataFrame. If `formulaepath` key in `path_dict` does not exist (if '' is passed as `formulaepath` argument while instantiating this object), `formulae` key does not exist in `data_dict` either.
    """
    def __init__(self, **files) -> object:
        '''Setting up how the post processing will be done, as a utility or use in the dash app

        Arguments:
        ---------
        files: Will accept a maximum of 3 keyword arguments
            If the Input keyword is 'json', it must have a path to the json for the corresponding experiment.

            Alternatively the Input keyword must be at least 'data' or 'config', in this order.
        Input keyword can be 'data', 'config', and 'formulae' with formulae being being optional. 
        The input must have reference to data and config paths

        '''
        arg_nos = len(files.items())
        initializing_path_lists = []
        for ftype, fpath in files.items():
            try:
                if ftype == 'jsonpath' and arg_nos == 1:  # Reading from the .json file
                    with open(fpath) as f:
                        path_dict = json.load(f)
                    par_f = path_dict["Test Name"]
                    config_f = path_dict["Config File"]
                    formula_f = path_dict["Formulae File"]
                    initializing_path_lists.append(par_f)
                    initializing_path_lists.append(config_f)
                    if formula_f.strip() != '':
                        initializing_path_lists.append(formula_f)
                elif ftype == 'datapath' and arg_nos <= 3:
                    par_f = fpath
                    initializing_path_lists.append(par_f)
                elif ftype == 'configpath' and arg_nos <= 3:
                    config_f = fpath
                    initializing_path_lists.append(config_f)
                elif ftype == 'formulaepath' and arg_nos <= 3:
                    formula_f = fpath
                    if formula_f.strip() != '':
                        initializing_path_lists.append(formula_f)
            except Exception as e:
                print(e)  # Remove Print after all debug and tests and completed
                # firepydaq_logger.error(__name__+':'+str(type(e)) + str(e)) 
        
        # todo: move this formulae dict to DAQUtils
        self.Formulae_dict = {"sqrt": "np.sqrt",
                              "pi": "np.pi",
                              "mean": "np.mean",
                              "max": "max",
                              "abs": "np.abs"}
        self.Errors = {}  # Empty error dict. Any errors will be saved in the log file

        self.pathdict, self.data_dict = self.initialize_Data(initializing_path_lists)
        self.MergeConfig_Formulae()
        # firepydaq_logger.info(__name__ + ": PostProcessing initiated succesfully")
    
    def _CallParser(self):
        '''
        :meta private:
        '''
        if len(self.pathdict.keys()) == 3:
            self.ParseFormulae()
        return

    def _CallScaler(self):
        '''
        :meta private:
        '''
        self.ScaleData()
        return
        
    def MergeConfig_Formulae(self):
        select_cols = ["Label", "Chart", "Layout", "Position", "Processed_Unit", "Legend"]
        
        config_info = self.data_dict['config'].select(select_cols)
        # Ensure Layout an position are integers
        config_info = config_info.with_columns(pl.col("Layout").cast(pl.String))
        config_info = config_info.with_columns(pl.col("Position").cast(pl.String))
        config_info = config_info.with_columns(pl.col("Layout").str.strip_chars().cast(pl.Int64))
        config_info = config_info.with_columns(pl.col("Position").str.strip_chars().cast(pl.Int64))
        
        if len(self.pathdict.keys())==3:
            self.read_formulae = True
            formulae_info = self.data_dict['formulae'].select(select_cols)
            All_chart_info = pl.concat([config_info, formulae_info])
        else:
            self.read_formulae = False # Only data scaling
            All_chart_info = config_info
        All_chart_info = All_chart_info.filter(~pl.col("Chart").str.contains("Intermediate"))
        All_chart_info = All_chart_info.filter(~pl.col("Chart").str.contains("Constant"))
        self.All_chart_info = All_chart_info
        self.All_chart_info.rename(str.strip).columns
        self.All_chart_info = self.All_chart_info.with_columns(pl.col(pl.String).str.strip_chars())
        
    def initialize_Data(self, *paths):
        fpath = paths[0][0]
        configpath = paths[0][1]
        if type(fpath) is str:
            self.fpathIsDf = False
            df = pl.read_parquet(fpath)
            dfpath_dict = {'datapath':fpath, 'configpath':configpath}
        else:
            self.fpathIsDf = True
            df = fpath
            dfpath_dict = {'datapath':'', 'configpath':configpath}
        df_config = pl.read_csv(configpath)
        df_config.columns = [i.strip() for i in df_config.columns]
        dfdata_dict = {'data': df, 'config': df_config}
        
        if len(paths[0]) == 3:
            formulae_path = paths[0][2]
            df_formulae = pl.read_csv(formulae_path)
            dfpath_dict['formulaepath'] = formulae_path
            dfdata_dict['formulae'] = df_formulae
        
        return dfpath_dict, dfdata_dict

    def UpdateData(self, dump_output=True):
        """A method to update the processed data using the initiated path configs
        
        An attribute df_processed: `polars.DataFrame`

            If `dump_output = True` (Default), A new file having the name `self.pathdict['datapath'].split('.parquet')[0]+'_PostProcessed.parquet'` will be created.
        
        Parameters
        ----------
        dump_output: bool, Optional
            Default `dump_outut = True`

            `True`: Processed data will be saved at the location where the data is read from.

            `False`: Processed data will not save the processed data

        Returns
        _______

        None: None

        
        """
        if not self.fpathIsDf:  # Used for authenticating formulae file using random numbers before acquisition begins
            self.data_dict['data'] = pl.read_parquet(self.pathdict['datapath'])
        self._CallScaler()
        self._CallParser()
        if dump_output:
            self.df_processed.write_parquet(self.pathdict['datapath'].split('.parquet')[0]+'_PostProcessed.parquet')

    def ScaleData(self):
        '''Data is scaled assuming linear scaling from `ScaleMax` and `ScaleMin` for the corresponding analog input of `AIRangeMax` and `AIRangeMin`.

        For each label in the config file, a corresponding `min_AI` and `max_AI` are read, which correspond to `AIRangeMin` and `AIRangeMax` respectively.
        `ScaleMax` and `ScaleMin` are also used for this scaling. `ScaleMin` is also the offset in this linear correlation.

        `Unit_per_V` variable is created which is the ratio of the differrence between the `ScaleMax` and `ScaleMin`, to the difference between `AIRangeMax` and `AIRangeMin`
        Scaled data, scaled_data is then obtained as follows,
            `scaled_data` = (`raw_data` - `min_AI`)*`unit_per_V` + `ScaleMin`


        '''
        self.df_processed = pl.DataFrame()
        for col in self.data_dict['data'].columns:
            if ("AbsoluteTime" not in col) and ("Absolute_Time" not in col): # Checking for either these two strings in the data df. Absolute_Time will be backward compatible for data collected so far
                self.data_dict['data'] = self.data_dict['data'].cast({col: pl.Float32})
            if "Time" in col:
                self.df_processed = self.df_processed.with_columns(pl.Series(self.data_dict['data'].select(col)).alias(col))
            elif not self.data_dict['config'].filter(pl.col("Type") == "Thermocouple").filter(pl.col("Label") == col).is_empty():
                self.df_processed = self.df_processed.with_columns(pl.Series(self.data_dict['data'].select(col)).alias(col))
            else:
                try:
                    local_scales = self.data_dict['config'].filter(pl.col("Label") == col)
                    min_AI = np.float32(local_scales.select("AIRangeMin").item())
                    max_AI = np.float32(local_scales.select("AIRangeMax").item())
                    min_Scale = np.float32(local_scales.select("ScaleMin").item())
                    max_Scale = np.float32(local_scales.select("ScaleMax").item())
                    unit_per_V = (max_Scale - min_Scale)/(max_AI - min_AI)
                    self.df_processed = self.df_processed.with_columns((pl.Series((self.data_dict['data'].select(pl.col(col))-min_AI)*unit_per_V+min_Scale)).alias(col))
                except ValueError:
                    self.df_processed = self.df_processed.with_columns(pl.Series(self.data_dict['data'].select(col)).alias(col))

    def CheckVarMacthes(self, var, rhs, replacement):
        # Look for variable with non alphanumeric, and underscore characters before or after the string. i.e. a-zA-Z0-9_
        pattern = r"(?<![\w])"+var+r"(?![\w])" 
        matcher = re.finditer(pattern, rhs, re.IGNORECASE)
        matchy_spans = [(re.findall(var, i.group())[0], i.span()) for i in matcher]
        for i in range(len(matchy_spans)):
            matches = matchy_spans[i]
            rhs = rhs[:matches[1][0]] + replacement + rhs[matches[1][1]:]
            
            # Updating the variable match based on given replacement string
            matcher = re.finditer(pattern, rhs, re.IGNORECASE)
            matchy_spans = [(i.group(), i.span()) for i in matcher]

        return rhs

    def ExecEqn(self, lhs, rhs):
        try:
            exec('setattr(self,lhs,eval(rhs))')
            return
        except:
            the_type, the_value, the_traceback = sys.exc_info()
            # print(the_value.__str__())
            if the_type == NameError:
                err_val = the_value.__str__()
            elif the_type == SyntaxError:
                err_val = the_value.text.split('=')[0]
            if not (lhs, err_val) in self.Errors:
                self.Errors[(lhs, err_val)] = str(the_type)
                print(lhs, the_type, ': ', err_val.strip())
    
    def ParseFormulae(self):
        '''This function can be used to test the formulae file for sanity before running the dash
        Needs to have scaled data before running this
        '''
        formulae_df = self.data_dict['formulae']
        for row in formulae_df.iter_rows(named=True):
            skip_processing = False
            lhs = row["Label"].strip()
            rhs = row["RHS"].strip()
            eqn = lhs + '=' + rhs
            if "Constant" in row["Chart"]:
                self.ExecEqn(lhs, rhs)
            else:
                # vars = re.findall(r'[A-Za-z]+_?[A-Za-z0-9]+',rhs)
                vars = re.findall(f'[a-zA-Z_][a-zA-Z0-9_]*', rhs)
                if vars == []: # Constant
                    self.ExecEqn(lhs, rhs)
                    continue
                unique_vars = pl.Series(vars).unique()
                for var in unique_vars:
                    # processed_in_df = False
                    if any([var in i for i in self.Formulae_dict.keys()]):
                        continue
                    if var in locals(): # Checking for Constants and Intermediates
                        # var_exists = True
                        continue
                    elif var not in locals() and hasattr(self, var):
                        rhs = self.CheckVarMacthes(var, rhs, 'getattr(self,\"'+var+'\")')
                        continue
                    try:
                        # Checking for variable in the processed_df
                        if not self.df_processed.select(var).is_empty():
                            # processed_in_df = True
                            setattr(self, var, self.df_processed.select(var).to_numpy().flatten())
                            rhs = self.CheckVarMacthes(var, rhs, 'getattr(self,\"'+var+'\")')
                        else:
                            # "Variable " + var + ", does not exist in locals or in collected/processed data. Please check variables. Skipping with the processing"
                            skip_processing = True
                    except:
                        the_type, the_value, _ = sys.exc_info()
                        err_val = the_value.__str__()
                        if not (lhs, err_val) in self.Errors:
                            self.Errors[(lhs, err_val)] = str(the_type)
                            # firepydaq_logger.error(__name__ + ": " + lhs + ' '+ the_type, ': ' + err_val.strip())
                        skip_processing = True
                for i in self.Formulae_dict.keys():  # final replacement of formulae to python parseable functions
                    if i in rhs:
                        rhs = self.CheckVarMacthes(i,rhs,self.Formulae_dict[i])
                eqn = lhs + '=' + rhs

            if not skip_processing:
                try:
                    exec('setattr(self,lhs,eval(rhs))')
                    if isinstance(getattr(self,lhs), np.ndarray) and ((row["Chart"] != "Intermediate") and (row["Chart"] != "Constant")):
                        self.df_processed = self.df_processed.with_columns(pl.Series(getattr(self,lhs)).alias(lhs))
                except:
                    the_type, the_value, _ = sys.exc_info()
                    err_val = the_value
                    if the_type == NameError:
                        err_val = the_value.__str__()
                    elif the_type == SyntaxError:
                        err_val = the_value.text.split('=')[0]
                    if not (lhs, err_val) in self.Errors:
                        self.Errors[(lhs, err_val)] = str(the_type)
                        # firepydaq_logger.error(__name__ + ": " + lhs + ' '+ the_type, ': ' + err_val.strip())
                    skip_processing = True
                
        if self.Errors !=[]:
            with open('Errorlog_formulae.log','w') as f:
                for key,error_item in self.Errors.items():
                    f.write(key[0] + " : " + key[1] + " :: " + error_item +'\n')
    
    @property
    def Processed_df(self):
        """Returns processed data frame
        """
        return self.df_processed

if __name__ == "__main__":
    print("Testing with pytest and poetry")


