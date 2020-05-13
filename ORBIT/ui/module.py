__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from PySide2.QtWidgets import (
    QWidget,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QVBoxLayout,
)

from ORBIT import ProjectManager


class ModuleSelect(QWidget):
    """Widget for selecting ORBIT modules."""

    def __init__(self):
        """Creates an instance of `ModuleSelect`."""

        super().__init__()
        self.checkboxes = []
        self.initUI()
        self.name = "Modules"

    def initUI(self):
        """Initializes the UI."""

        grid = QGridLayout()
        grid.addWidget(self.create_design_module_group(), 0, 0)
        grid.addWidget(self.create_install_module_group(), 1, 0)

        self.setLayout(grid)

    @property
    def selected_modules(self):
        """Returns list of selected modules."""

        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def create_design_module_group(self):
        """"""

        box = QGroupBox("Design Modules")
        layout = QVBoxLayout()

        for k in ProjectManager._design_phases:
            cb = QCheckBox(k.__name__)
            self.checkboxes.append(cb)
            layout.addWidget(cb)

        box.setLayout(layout)

        return box

    def create_install_module_group(self):
        """"""

        box = QGroupBox("Install Modules")
        layout = QVBoxLayout()

        for k in ProjectManager._install_phases:
            cb = QCheckBox(k.__name__)
            self.checkboxes.append(cb)
            layout.addWidget(cb)

        box.setLayout(layout)

        return box
