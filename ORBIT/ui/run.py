__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from PySide2.QtWidgets import (
    QLabel,
    QWidget,
    QGroupBox,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)


class RunOrbit(QWidget):
    """Widget for loading weather files for use in ORBIT runs."""

    def __init__(self):
        """Creates an instance of `RunOrbit`."""

        super().__init__()
        self.initUI()
        self.name = "Run"

    def initUI(self):
        """Initializes the widget UI."""

        vbox = QVBoxLayout()

        self.btn = QPushButton("Run")
        vbox.addWidget(self.btn)

        bot = QGroupBox()
        # Preview of results.
        vbox.addWidget(bot)

        self.setLayout(vbox)

    def onRun(self):
        """"""
        pass

    def updateResultsPreview(self):
        """"""
        pass
