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


class PhaseSelect(QWidget):
    """Widget for selecting ORBIT modules."""

    def __init__(self):
        """Creates an instance of `PhaseSelect`."""

        super().__init__()
        self.initUI()
        self.name = "Phase Selection"

    def initUI(self):
        """Initializes the UI."""

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Test:"))
        hbox.addWidget(QLineEdit())
        self.setLayout(hbox)
