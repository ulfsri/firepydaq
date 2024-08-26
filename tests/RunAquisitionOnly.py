# RunAquisitionOnly

if __name__ == "__main__":
    from firepydaq.FIREpyDAQ_Acquisition import FIREpyDAQ_Acquisition

    from firepydaq.utilities.DAQUtils import AlicatGases
    AlicatGases['C2H2'] = u'C\u2082H\u2082'

    FIREpyDAQ_Acquisition()

# Alterative
# if __name__ == '__main__':
#     import multiprocessing as mp
#     mp.freeze_support()
#     from firepydaq.acquisition.acquisition import application
#     from PySide6.QtWidgets import QApplication
#     import sys

#     app = QApplication(sys.argv)
#     main_app = application()
#     main_app.show()
#     app.exec()
