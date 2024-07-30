# print('Testing')
# from fsripydaq.dashboard.app import create_dash_app
# import time

print("test file opens")

# create_dash_app(jsonpath = r"C:\Users\MishraAnvii\Documents\GitHub\fsripydaq\tests\Example_ExpData\20240724_1045_Anvii_Project1_Test1.json")
import sys
from PySide6.QtWidgets import QApplication
from fsripydaq.acquisition.acquisition import application
# import multiprocessing
# multiprocessing.freeze_support()

if __name__=="__main__":
    app = QApplication(sys.argv)
    main_app = application()
    main_app.show()
    sys.exit(app.exec())
