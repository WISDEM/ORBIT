__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]

import sys

from PySide2.QtWidgets import QApplication

from ORBIT.ui import App, Config, LoadSave, RunOrbit, LoadWeather, ModuleSelect

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App([LoadSave(), ModuleSelect(), Config(), LoadWeather(), RunOrbit()])
    sys.exit(app.exec_())
