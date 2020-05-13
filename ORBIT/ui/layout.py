__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from PySide2.QtWidgets import (
    QWidget,
    QTabWidget,
    QMainWindow,
    QVBoxLayout,
    QDesktopWidget,
)

from ORBIT import ProjectManager


class App(QMainWindow):
    def __init__(self, widgets):
        """
        Initializes the main ORBIT UI window.

        Parameters
        ----------
        widgets : dict
            'name': 'QWidget'
        """

        super().__init__()
        self.widgets = {w.name: w for w in widgets}
        self._inputs = {}

        self.resize(500, 600)
        self.center()
        self.setWindowTitle("ORBIT")

        self.navigation = Navigation(self, self.widgets)
        self.setCentralWidget(self.navigation)

        self.connect_widgets()
        self.show()

    @property
    def current_config(self):
        """"""

    def center(self):
        """Centers the app on the main screen."""

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def connect_widgets(self):
        """"""

        module = self.widgets["Modules"]
        for cb in module.checkboxes:
            cb.stateChanged.connect(self._modules_changed)

    def _modules_changed(self):

        module = self.widgets["Modules"]
        config = self.widgets["Configuration"]

        config.update(module.selected_modules)


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
        Adds input `widgets` to the navigation bar.

        Parameters
        ----------
        widgets : dict
            'name': 'QWidget'
        """

        for name, widget in widgets.items():
            self.tabs.addTab(widget, name)
