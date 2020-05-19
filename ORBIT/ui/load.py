__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from PySide2.QtWidgets import (
    QWidget,
    QGroupBox,
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
        """Initializes the widget UI."""

        vbox = QVBoxLayout()

        bot = QGroupBox()
        bLayout = QHBoxLayout()

        self.load = QPushButton("Load")
        self.save = QPushButton("Save")

        bLayout.addWidget(self.load)
        bLayout.addWidget(self.save)
        bot.setLayout(bLayout)

        vbox.addWidget(bot)
        self.setLayout(vbox)
