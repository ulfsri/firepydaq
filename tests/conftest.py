import pytest

jsonpath = 'tests/Example_ExpData/20240612_1717_ExampleFireData_Testing_Dushyant.json'  # noqa E501
datapath = 'tests/Example_ExpData/20240612_1717_ExampleFireData_Testing_Dushyant.parquet'  # noqa E501
formulaepath = 'tests/Example_Config_Formulae/Processing_formulae.csv'
configpath = 'tests/Example_Config_Formulae/20240329_1354_CalorimetryWLaser_Dushyant.csv'  # noqa E501

# Defining test paths using pytest for sharing the
# variables across different functions
pytest.jsonpath = jsonpath
pytest.datapath = datapath
pytest.formulaepath = formulaepath
pytest.configpath = configpath
