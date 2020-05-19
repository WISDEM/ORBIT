__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


import os
import sys

import yaml
import pandas as pd
import PySide2
from yaml import Dumper
from PySide2.QtWidgets import (
    QWidget,
    QTabWidget,
    QFileDialog,
    QMainWindow,
    QVBoxLayout,
    QApplication,
)

import ORBIT
from ORBIT import ProjectManager
from ORBIT.ui import Config, LoadSave, RunOrbit, LoadWeather, ModuleSelect
from ORBIT.library import _extract_file

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

    def connect_widgets(self):
        """Connects widgets across the app."""

        module = self.widgets["Modules"]
        load = self.widgets["Load/Save"]
        run = self.widgets["Run"]
        weather = self.widgets["Weather"]

        for cb in module.checkboxes:
            cb.stateChanged.connect(self._modules_changed)

        run.btn.clicked.connect(self._run)

        load.load.clicked.connect(self._load_config)
        load.save.clicked.connect(self._save_config)

        weather.btn.clicked.connect(self._load_weather)

    def _modules_changed(self):
        """Method triggered when the selected modules are changed."""

        module = self.widgets["Modules"]
        config = self.widgets["Configuration"]

        config.update_tree(module.selected_modules)

    def _run(self):
        """Method triggered when the run button is clicked."""

        module = self.widgets["Modules"]
        config = self.widgets["Configuration"]
        weather = self.widgets["Weather"]

        c = config.config(module.selected_modules)
        c["design_phases"] = module.selected_designs
        c["install_phases"] = module.selected_installs

        project = ProjectManager(c, weather=weather.data)
        project.run_project()

    def _load_weather(self):
        """Triggers a QFileDialog to load a weather file."""

        weather = self.widgets["Weather"]

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "csv(*.csv);;All Files (*)",
            options=options,
        )

        if filepath:
            weather.data = pd.read_csv(filepath)
            weather.update_preview()
            return

        weather.data = None
        weather.update_preview()

    def _load_config(self):
        """Triggers a QFileDialog to load a configuration file."""

        module = self.widgets["Modules"]
        config = self.widgets["Configuration"]

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "yaml (*.yaml);;All Files (*)",
            options=options,
        )

        if filepath:
            loaded = _extract_file(filepath)
            design_phases = loaded.pop("design_phases", [])
            install_phases = loaded.pop("install_phases", [])

            config.inputs = loaded
            module.select_modules([*design_phases, *install_phases])

    def _save_config(self):
        """Triggers a QFileDialog to save a configuration file."""

        module = self.widgets["Modules"]
        config = self.widgets["Configuration"]

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "QFileDialog.getSaveFileName()",
            "",
            "yaml (*.yaml)",
            options=options,
        )
        if filepath:

            data = config.inputs
            data["design_phases"] = module.selected_designs
            data["install_phases"] = module.selected_installs

            f = open(filepath, "w")
            yaml.dump(data, f, Dumper=Dumper, default_flow_style=False)
            f.close()


class Navigation(QWidget):
    def __init__(self, parent, widgets):
        """
        Initializes the navigation widget.

        Parameters
        ----------
        parent : QObject
        widgets : list
            List of QWidgets.
        """

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
