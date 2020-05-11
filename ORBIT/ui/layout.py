__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


import sys

from PyQt5.QtWidgets import (
    QWidget,
    QTabWidget,
    QMainWindow,
    QVBoxLayout,
    QApplication,
    QDesktopWidget,
)

# from ORBIT.ui import LoadSave, PhaseSelect


class App(QMainWindow):
    def __init__(self, widgets):
        """Initializes the main ORBIT UI window."""

        super().__init__()
        self.widgets = widgets
        self.resize(500, 600)
        self.center()
        self.setWindowTitle("ORBIT")

        self.navigation = Navigation(self, self.widgets)
        self.setCentralWidget(self.navigation)
        self.show()

    def center(self):
        """"""

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Navigation(QWidget):
    def __init__(self, parent, widgets):
        """Initializes the navigation widget."""

        super().__init__(parent)

        self.tabs = QTabWidget()
        self.add_widgets(widgets)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def add_widgets(self, widgets):
        """
        Adds list of `widgets` to the navigation bar.

        Parameters
        ----------
        widgets : list
            List of QWidgets.
        """

        for w in widgets:
            self.tabs.addTab(w, w.name)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = App([LoadSave, PhaseSelect])
#     sys.exit(app.exec_())
