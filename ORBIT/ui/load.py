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


class LoadSave(QWidget):
    """Widget for loading or saving ORBIT configuration files."""

    def __init__(self):
        """Creates an instance of `LoadSave`."""

        super().__init__()
        self.initUI()
        self.name = "Load/Save"

    def initUI(self):
        """Initializes the UI."""

        vbox = QVBoxLayout()

        top = QGroupBox()
        tLayout = QHBoxLayout()
        tLayout.addWidget(QLabel("Filepath:"))
        tLayout.addWidget(QLineEdit())
        top.setLayout(tLayout)

        bot = QGroupBox()
        bLayout = QHBoxLayout()

        self.load = QPushButton("Load")
        self.save = QPushButton("Save")

        bLayout.addWidget(self.load)
        bLayout.addWidget(self.save)
        bot.setLayout(bLayout)

        vbox.addWidget(top)
        vbox.addWidget(bot)

        self.setLayout(vbox)

    def onLoad(self):
        """"""
        pass

    def onSave(self):
        """"""
        pass
