def FIREpyDAQ_Acquisition():
    """Function that compiles the acquisiton application
    and opens the user interface.
    """
    import multiprocessing as mp
    mp.freeze_support()
    from firepydaq.acquisition.acquisition import application
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    main_app = application()
    main_app.show()
    app.exec()
