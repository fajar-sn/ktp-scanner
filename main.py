import sys

from PyQt5.QtWidgets import QApplication

from src.main.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.user_interface.show()
    exec = app.exec()
    sys.exit(exec)
