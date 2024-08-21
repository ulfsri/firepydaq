if __name__ == '__main__':
    # import qdarktheme
    from firepydaq.dashboard.app import create_dash_app

create_dash_app(datapath=r"C:\Users\MishraAnvii\Documents\GitHub\firepydaq\tests\Example_ExpData\20240613_0946_PropaneStepsNoInletFilterNoBlenderFan45Hz_Propane_Dushyant_PostProcessed.parquet", # noqae501
configpath=r"C:\Users\MishraAnvii\Documents\GitHub\firepydaq\tests\Example_Config_Formulae\20240329_1354_CalorimetryWLaser_Dushyant.csv",# noqae501
formulaepath = r"C:\Users\MishraAnvii\Documents\GitHub\firepydaq\tests\Example_Config_Formulae\Processing_formulae.csv")# noqae501
