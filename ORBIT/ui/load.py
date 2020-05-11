__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
)


class LoadSave(QWidget):
    """Widget for loading or saving ORBIT configuration files."""

    def __init__(self):
        """Creates an instance of `LoadSave`."""

        super().__init__()
        self.initUI()
        self.name = "Load/Save"

    def initUI(self):
        """Initializes the UI."""

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Filepath:"))
        hbox.addWidget(QLineEdit())
        self.setLayout(hbox)
