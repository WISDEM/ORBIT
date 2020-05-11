import sys

from PyQt5.QtWidgets import (
    QWidget,
    QTabWidget,
    QMainWindow,
    QVBoxLayout,
    QApplication,
    QDesktopWidget,
)

from ORBIT.ui import App, LoadSave, PhaseSelect

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App([LoadSave(), PhaseSelect()])
    sys.exit(app.exec_())
