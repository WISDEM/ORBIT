__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


import os
import sys

import PySide2
from PySide2.QtWidgets import (
    QWidget,
    QTabWidget,
    QMainWindow,
    QVBoxLayout,
    QApplication,
)

import ORBIT
from ORBIT import ProjectManager
from ORBIT.ui import Config, LoadSave, RunOrbit, LoadWeather, ModuleSelect

qt = os.path.dirname(PySide2.__file__)
QApplication.addLibraryPath(os.path.join(qt, "plugins"))


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
        self.setWindowTitle(f"ORBIT {ORBIT.__version__}")

        self.navigation = Navigation(self, self.widgets)
        self.setCentralWidget(self.navigation)

        self.connect_widgets()
        self.show()

    @property
    def current_config(self):
        """"""
        pass

    def connect_widgets(self):
        """"""

        config = self.widgets["Configuration"]
        module = self.widgets["Modules"]
        run = self.widgets["Run"]

        for cb in module.checkboxes:
            cb.stateChanged.connect(self._modules_changed)

        run.btn.clicked.connect(self._on_run)

    def _modules_changed(self):

        module = self.widgets["Modules"]
        config = self.widgets["Configuration"]

        config.update(module.selected_modules)

    def _on_run(self):

        module = self.widgets["Modules"]
        config = self.widgets["Configuration"]

        c = config.config
        c["design_phases"] = module.selected_designs
        c["install_phases"] = module.selected_installs

        project = ProjectManager(c)
        project.run_project()


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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ex = App([LoadSave(), ModuleSelect(), Config(), LoadWeather(), RunOrbit()])

    sys.exit(app.exec_())
