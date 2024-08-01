# RunAquisitionOnly

if __name__ == '__main__':
    # import qdarktheme
    import multiprocessing as mp
    mp.freeze_support()
    from firepydaq.acquisition.acquisition import application
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    # qdarktheme.setup_theme()
    f = open("styles.css")
    str = f.read()
    app.setStyleSheet(str)
    main_app = application()
    main_app.show()
    app.exec()
    f.close()
