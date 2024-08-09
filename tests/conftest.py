import pytest

jsonpath = 'tests/Example_ExpData/20240724_1045_Anvii_Project1_Test1.json'
datapath = 'tests/Example_ExpData/20240612_1717_ExampleFireData_Testing_Dushyant.parquet'
formulaepath = 'tests/Example_Config_Formulae/Processing_formulae.csv'
configpath = 'tests/Example_Config_Formulae/20240329_1354_CalorimetryWLaser_Dushyant.csv'

# Defining test paths using pytest for sharing the variables across different functions
pytest.jsonpath = jsonpath
pytest.datapath = datapath
pytest.formulaepath = formulaepath
pytest.configpath = configpath
