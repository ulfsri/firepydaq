
if __name__ == '__main__':
    import multiprocessing as mp
    mp.freeze_support()
    from firepydaq.acquisition.acquisitionNoDash import application
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    main_app = application()
    main_app.show()
    sys.exit(app.exec())