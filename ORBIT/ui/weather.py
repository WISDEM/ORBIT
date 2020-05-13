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


class LoadWeather(QWidget):
    """Widget for loading weather files for use in ORBIT runs."""

    def __init__(self):
        """Creates an instance of `LoadWeather`."""

        super().__init__()
        self.initUI()
        self.name = "Weather"

    def initUI(self):
        """Initializes the widget UI."""

        vbox = QVBoxLayout()

        top = QGroupBox()
        tLayout = QHBoxLayout()
        tLayout.addWidget(QLabel("Filepath:"))
        tLayout.addWidget(QLineEdit())
        top.setLayout(tLayout)
        vbox.addWidget(top)

        self.btn = QPushButton("Load")
        vbox.addWidget(self.btn)

        bot = QGroupBox()
        # Table preview of weather data.
        vbox.addWidget(bot)

        self.setLayout(vbox)

    def onLoad(self):
        """"""
        pass

    def updateTable(self):
        """"""
        pass
