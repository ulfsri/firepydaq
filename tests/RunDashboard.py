if __name__ == '__main__':
    from firepydaq.dashboard.app import create_dash_app

create_dash_app(datapath="Example_ExpData/20240612_1717_ExampleFireData_Testing_Dushyant.parquet",  # noqa E501
configpath="Example_Config_Formulae/20240329_1354_CalorimetryWLaser_Dushyant.csv",  # noqa E501
formulaepath = "Example_Config_Formulae/Processing_formulae.csv")  # noqa E501
