

def FIREpyDAQ_Acquisition():
    import multiprocessing as mp
    mp.freeze_support()
    from firepydaq.acquisition.acquisition import application
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv + ['-platform', 'windows:darkmode=1'])
    main_app = application()
    main_app.show()
    app.exec()
