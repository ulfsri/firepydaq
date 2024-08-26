import polars as pl
import re
import numpy as np
import sys
import json
from .DAQUtils import Formulae_dict


class PostProcessData():
    """An object that processes data based on the config and formulae file

    Setting up how the post processing will be done,
    as a utility or use in the dash app

    Keyword Arguments
    ---------
    jsonpath: str
            If the Input keyword is 'jsonpath', it must have a path
            to the json file for the corresponding experiment.
    datapath: str
            Path to the data `.parquet file`
    configpath: str
            Path to the config .csv file
    formulaepath: str (Optional)
            Path to the formulae .csv file

    Note
    ----
    Will accept a maximum of 3 keyword args

    Alternatively (if not using `jsonpath`), the input keyword must be
    at least 'datapath' and 'configpath'.
    Input keyword can be 'datapath', 'configpath', and 'formulaepath'.

    **The input must have reference to data and config paths**

    Attributes
    ----------
        path_dict: dict
            Contains a dictionary that maps
            `datapath`,`configpath`, and `formulaepath`.

            The items of the keys are read as `polars.DataFrame`

            `datapath` can be path to live data, or data collected
            after an experiment, or randomly created numpy array
            to validate formulae before acquisition begins.

            `configpath` can be path to the configuration file
            for the NI hardware that uses ni-daqmx driver.

            `formulaepath` can be a path to the formulae file. Optionally,
            if processing formulae needs to be skipped,
            the path is passed as an either an empty string ('').

            Formulae file should use the variables defined in the `Label`
            column of the config file. The formulae file will be
            processed in the order that the formulae appears,
            from the topmost row to the bottom.

        data_dict: dict
            'data': polars.DataFrame,
            'config': polars.DataFrame,
            'formulae': polars.DataFrame

        All_chart_info: polars.DataFrame
            A polars DataFrame concatenated using
            the config and the formulae file.
            Excludes values in "Chart" column
            in config or formulae file
            that contains either "Intermediate" or "Constant".

    """
    def __init__(self, **files) -> object:
        _arg_nos = len(files.items())
        _initializing_path_lists = []
        for ftype, fpath in files.items():
            try:
                if ftype == 'jsonpath' and _arg_nos == 1:
                    # Reading from the .json file
                    with open(fpath) as f:
                        path_dict = json.load(f)
                    par_f = path_dict["Test Name"]
                    config_f = path_dict["Config File"]
                    formula_f = path_dict["Formulae File"]
                    _initializing_path_lists.append(par_f)
                    _initializing_path_lists.append(config_f)
                    if formula_f.strip() != '':
                        _initializing_path_lists.append(formula_f)
                elif ftype == 'datapath' and _arg_nos <= 3:
                    par_f = fpath
                    _initializing_path_lists.append(par_f)
                elif ftype == 'configpath' and _arg_nos <= 3:
                    config_f = fpath
                    _initializing_path_lists.append(config_f)
                elif ftype == 'formulaepath' and _arg_nos <= 3:
                    formula_f = fpath
                    if formula_f.strip() != '':
                        _initializing_path_lists.append(formula_f)
            except Exception as e:
                # Remove Print after all debug and tests and completed
                print(e)

        self._all_dicts = self._initialize_Data(_initializing_path_lists)
        self._initiateDicts()
        self.MergeConfig_Formulae()

    def _initialize_Data(self, *paths):
        """ Creates dictionaries of paths and data.
        """
        fpath = paths[0][0]
        configpath = paths[0][1]
        if type(fpath) is str:
            self.fpathIsDf = False
            df = pl.read_parquet(fpath)
            dfpath_dict = {'datapath': fpath, 'configpath': configpath}
        else:
            self.fpathIsDf = True
            df = fpath
            dfpath_dict = {'datapath': '', 'configpath': configpath}
        df_config = pl.read_csv(configpath)
        df_config.columns = [i.strip() for i in df_config.columns]
        dfdata_dict = {'data': df, 'config': df_config}

        if len(paths[0]) == 3:
            formulae_path = paths[0][2]
            df_formulae = pl.read_csv(formulae_path)
            df_formulae.columns = [i.strip() for i in df_formulae.columns]
            dfpath_dict['formulaepath'] = formulae_path
            dfdata_dict['formulae'] = df_formulae

        return (dfpath_dict, dfdata_dict)

    def _initiateDicts(self):
        """
        Attributes
        ---------
        Formulae_dict: dict
            A dictionary that maps the label (or LHS) for which an error
            was encountered while parsing
            the formulae to the corresponding error.
            Errors are also logged in `Formulae.log` file,
            which is created in the working directory
        """
        self.Formulae_dict = Formulae_dict
        self.Errors = {}

        self.path_dict = self._all_dicts[0]
        self.data_dict = self._all_dicts[1]

        return

    def _CallParser(self):
        '''
        :meta private:
        '''
        if len(self.path_dict.keys()) == 3:
            self.ParseFormulae()
        return

    def _CallScaler(self):
        '''
        :meta private:
        '''
        self.ScaleData()
        return

    def MergeConfig_Formulae(self):
        """Will merge config and formulae file csvs
        into a polars DataFrame.

        Creates the attribute All_chart_info.
        """
        select_cols = ["Label", "Chart", "Layout",
                       "Position", "Processed_Unit", "Legend"]
        config_info = self.data_dict['config'].select(select_cols)
        # Ensure Layout an position are integers
        config_info = config_info.with_columns(pl.col("Layout").cast(pl.String))  # noqa E501
        config_info = config_info.with_columns(pl.col("Position").cast(pl.String))  # noqa E501
        config_info = config_info.with_columns(pl.col("Layout").str.strip_chars().cast(pl.Int64))  # noqa E501
        config_info = config_info.with_columns(pl.col("Position").str.strip_chars().cast(pl.Int64))  # noqa E501

        if len(self.path_dict.keys()) == 3:
            self.read_formulae = True
            formulae_info = self.data_dict['formulae'].select(select_cols)
            formulae_info = formulae_info.with_columns(pl.col("Layout").cast(pl.String))  # noqa E501
            formulae_info = formulae_info.with_columns(pl.col("Position").cast(pl.String))  # noqa E501
            formulae_info = formulae_info.with_columns(pl.col("Layout").str.strip_chars().cast(pl.Int64))  # noqa E501
            formulae_info = formulae_info.with_columns(pl.col("Position").str.strip_chars().cast(pl.Int64))  # noqa E501
            All_chart_info = pl.concat([config_info, formulae_info])
        else:
            self.read_formulae = False  # Only data scaling
            All_chart_info = config_info
        All_chart_info = All_chart_info.filter(~pl.col("Chart").str.contains("Intermediate"))  # noqa E501
        All_chart_info = All_chart_info.filter(~pl.col("Chart").str.contains("Constant"))  # noqa E501
        All_chart_info = All_chart_info.filter(~pl.col("Chart").str.contains("None"))  # noqa E501
        All_chart_info = All_chart_info
        All_chart_info.rename(str.strip).columns
        All_chart_info = All_chart_info.with_columns(pl.col(pl.String).str.strip_chars())  # noqa E501
        self.All_chart_info = All_chart_info

        return

    def UpdateData(self, dump_output=True):
        """A method to update the processed data
        using the initiated path configs

        Creates the attribute df_processed: `polars.DataFrame`

            If `dump_output = True` (Default), A new file having the name
            `self.path_dict['datapath'].split('.parquet')[0]+'_PostProcessed.parquet'` will be created.  # noqa E501

        Parameters
        ----------
        dump_output: bool, Optional
            Default `dump_outut = True`

            `True`: Processed data will be saved at the
            location where the data is read from.

            `False`: Processed data will not save the processed data
        """
        if not self.fpathIsDf:
            # Used for authenticating formulae file using
            # random numbers before acquisition begins
            self.data_dict['data'] = pl.read_parquet(self.path_dict['datapath'])  # noqa E501
        self._CallScaler()
        self._CallParser()
        if dump_output:
            self.df_processed.write_parquet(self.path_dict['datapath'].split('.parquet')[0]+'_PostProcessed.parquet')  # noqa E501

    def ScaleData(self):
        '''Method to scale the raw data.

        Data is scaled assuming linear scaling from
        `ScaleMax` and `ScaleMin` for the corresponding
        analog input of `AIRangeMax` and `AIRangeMin`.

        For each label in the config file, a corresponding
        ``min_AI`` and `max_AI` are read,
        which correspond to `AIRangeMin` and `AIRangeMax` respectively.
        `ScaleMax` and `ScaleMin` are also used for this scaling.
        `ScaleMin` is the offset in this linear correlation.

        `Unit_per_V` variable is created which is the ratio of the
        differrence between the `ScaleMax` and `ScaleMin`,
        to the difference between `AIRangeMax` and `AIRangeMin`
        Scaled data, scaled_data is then obtained as follows,
            `scaled_data` = (`raw_data` - `min_AI`)*`unit_per_V` + `ScaleMin`

        '''
        self.df_processed = pl.DataFrame()
        for col in self.data_dict['data'].columns:
            crow_df = self.data_dict['config'].filter(pl.col("Label") == col)
            if ("AbsoluteTime" not in col) and ("Absolute_Time" not in col):
                # Checking for either these two strings in the data df
                self.data_dict['data'] = self.data_dict['data'].cast({col: pl.Float32})  # noqa E501
            if "Time" in col:
                self.df_processed = self.df_processed.with_columns(pl.Series(self.data_dict['data'].select(col)).alias(col))  # noqa E501
            elif "None" in crow_df.select("Chart").item().strip() == "None":
                continue
            elif not self.data_dict['config'].filter(pl.col("Type") == "Thermocouple").filter(pl.col("Label") == col).is_empty():  # noqa E501
                self.df_processed = self.df_processed.with_columns(pl.Series(self.data_dict['data'].select(col)).alias(col))  # noqa E501
            else:
                try:
                    min_AI = np.float32(crow_df.select("AIRangeMin").item())
                    max_AI = np.float32(crow_df.select("AIRangeMax").item())
                    min_Scale = np.float32(crow_df.select("ScaleMin").item())
                    max_Scale = np.float32(crow_df.select("ScaleMax").item())
                    unit_per_V = (max_Scale - min_Scale)/(max_AI - min_AI)
                    self.df_processed = self.df_processed.with_columns((pl.Series((self.data_dict['data'].select(pl.col(col))-min_AI)*unit_per_V+min_Scale)).alias(col))  # noqa E501
                except ValueError:
                    # Is there is any ValueError
                    # no scaling will be done to the data
                    self.df_processed = self.df_processed.with_columns(pl.Series(self.data_dict['data'].select(col)).alias(col))  # noqa E501

    def _CheckVarMacthes(self, var, rhs, replacement):
        # Look for variable with non alphanumeric, and
        # underscore characters before or after the string.
        # i.e. a-zA-Z0-9_
        pattern = r"(?<![\w])"+var+r"(?![\w])"
        matcher = re.finditer(pattern, rhs, re.IGNORECASE)
        matchy_spans = [(re.findall(var, i.group())[0], i.span()) for i in matcher]  # noqa E501
        for i in range(len(matchy_spans)):
            matches = matchy_spans[i]
            rhs = rhs[:matches[1][0]] + replacement + rhs[matches[1][1]:]
            # Updating the variable match based on given replacement string
            matcher = re.finditer(pattern, rhs, re.IGNORECASE)
            matchy_spans = [(i.group(), i.span()) for i in matcher]

        return rhs

    def ExecEqn(self, lhs, rhs):
        """Method to execute an equation of the form lhs = rhs

        This will set the lhs string as an attribute for this object

        Parameters
        ---------
            lhs : string
                Left-hand side of the equation.
                This variable will be created upon execution
            rhs : string
                Right-hand side of the equation.
                Express the rhs in the form of what
                can be interpreted by python.
                Use formulae_dictoinary in DAQUtils to guide with that.
        """
        try:
            exec('setattr(self,lhs,eval(rhs))')
            return
        except Exception:
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
        '''A method to parse the formulae listed in a csv file.

        This function can be used to test the formulae file for sanity
        before running the dash.

        Needs to have scaled data before calling this method.
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
                vars = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', rhs)
                if vars == []:  # Constant
                    self.ExecEqn(lhs, rhs)
                    continue
                unique_vars = pl.Series(vars).unique()
                for var in unique_vars:
                    if any([var in i for i in self.Formulae_dict.keys()]):
                        continue
                    if var in locals():
                        # Checking for Constants and Intermediates
                        continue
                    elif var not in locals() and hasattr(self, var):
                        rhs = self._CheckVarMacthes(var, rhs, 'getattr(self,\"' + var + '\")')  # noqa E501
                        continue
                    try:
                        # Checking for variable in the processed_df
                        if not self.df_processed.select(var).is_empty():
                            setattr(self, var, self.df_processed.select(var).to_numpy().flatten())  # noqa E501
                            rhs = self._CheckVarMacthes(var, rhs, 'getattr(self, \"'+var+'\")')  # noqa E501
                        else:
                            # "Variable " + var + ", does not exist in locals
                            # or in collected/processed data.
                            # Skipping the processing"
                            skip_processing = True
                    except Exception:
                        the_type, the_value, _ = sys.exc_info()
                        err_val = the_value.__str__()
                        if not (lhs, err_val) in self.Errors:
                            self.Errors[(lhs, err_val)] = str(the_type)
                        skip_processing = True
                for i in self.Formulae_dict.keys():
                    # final replacement of formulae
                    # to python parseable functions
                    if i in rhs:
                        rhs = self._CheckVarMacthes(i, rhs, self.Formulae_dict[i])  # noqa E501
                eqn = lhs + '=' + rhs

            if not skip_processing:
                try:
                    exec('setattr(self,lhs,eval(rhs))')
                    if (isinstance(getattr(self, lhs), np.ndarray) and
                            (row["Chart"].strip() != "Intermediate") and
                            (row["Chart"].strip() != "Constant") and
                            (row["Chart"].strip() != "None")):
                        self.df_processed = self.df_processed.with_columns(pl.Series(getattr(self,lhs)).alias(lhs))  # noqa E501
                except Exception:
                    the_type, the_value, _ = sys.exc_info()
                    err_val = the_value
                    if the_type == NameError:
                        err_val = the_value.__str__()
                    elif the_type == SyntaxError:
                        err_val = the_value.text.split('=')[0]
                    if not (lhs, err_val) in self.Errors:
                        self.Errors[(lhs, err_val)] = str(the_type)
                    skip_processing = True

        if self.Errors != []:
            with open('Formulae.log', 'w') as f:
                for key, error_item in self.Errors.items():
                    f.write(key[0] + " : " + key[1] + " :: " + error_item + '\n')  # noqa E501
