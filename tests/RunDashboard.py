if __name__ == '__main__':
    # import qdarktheme
    from PySide6.QtWidgets import QApplication
    import sys
    from firepydaq.dashboard.form  import MyWindow

    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec()