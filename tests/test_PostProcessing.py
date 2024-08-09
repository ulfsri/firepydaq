from firepydaq.utilities.PostProcessing import PostProcessData
import matplotlib.pyplot as plt
import numpy as np
import sys
import pytest


# Shared function to test output. Can be switched to something else instead of plotting
def plot_collected(testing):
    for _, chart_df in testing.All_chart_info.group_by(["Chart"]):
        if not chart_df.select("Label")[0].item() in testing.df_processed.columns:
            continue
        _, axes = plt.subplots(chart_df.select("Layout")[0].item())
        if not isinstance(axes, np.ndarray): # If it is only a single axis
            axes = [axes]
        for row in chart_df.iter_rows(named=True):
            try:
                axes[row["Position"]-1].plot(testing.df_processed.select("Time"), testing.df_processed.select(row["Label"]),label=row["Legend"])
                axes[row["Position"]-1].set_xlabel("Time (s)")
                axes[row["Position"]-1].set_ylabel(row["Chart"]+" ( "+row["Processed_Unit"]+" )")
                axes[row["Position"]-1].legend()
            except Exception:
                the_type, the_value, _ = sys.exc_info()
                print(the_type, ': ', the_value)
    return


# Testing Post processing using .json file as input
def single_json_check(jsonpath: str):
    
    testing = PostProcessData(jsonpath=jsonpath)
    testing.UpdateData(dump_output=False)
    plot_collected(testing)


def donttest_json(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    single_json_check(jsonpath=pytest.jsonpath)
    assert True


# Testing Post processing using only two inputs
def data_config_check(datapath, configpath):
    testing = PostProcessData(datapath=datapath, configpath=configpath)
    testing.UpdateData(dump_output=False)
    plot_collected(testing)
    return


def test_data_config(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    data_config_check(datapath=pytest.datapath, configpath=pytest.configpath)
    assert True


# Testing formulae
def formulae_parser_check(datapath, configpath, formulaepath):
    testing = PostProcessData(datapath=datapath, configpath=configpath, formulaepath=formulaepath)
    testing.ScaleData()
    testing.ParseFormulae()
    df_lab = testing.data_dict['formulae'].select("Label")[-1].item()
    processed_lab = testing.df_processed.columns[-1]
    assert processed_lab == df_lab, "Error in parsing formulae"


def test_formulae_parser():
    formulae_parser_check(datapath=pytest.datapath, configpath=pytest.configpath, formulaepath=pytest.formulaepath)


if __name__ == "__main__":
    import os
    user_specific_path = os.getcwd()
    single_json_check(user_specific_path + os.sep + pytest.jsonpath)