__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


import pandas as pd
from PySide2.QtWidgets import (
    QLabel,
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)


class LoadWeather(QWidget):
    """Widget for loading weather files for use in ORBIT runs."""

    def __init__(self):
        """Creates an instance of `LoadWeather`."""

        super().__init__()
        self.name = "Weather"
        self.data = None
        self.initUI()

    def initUI(self):
        """Initializes the widget UI."""

        vbox = QVBoxLayout()

        self.btn = QPushButton("Load")
        vbox.addWidget(self.btn)

        self.bot = QGroupBox()
        self.preview_layout = QHBoxLayout()

        self.preview = QLabel(self._preview)
        self.preview_layout.addWidget(self.preview)
        self.bot.setLayout(self.preview_layout)

        vbox.addWidget(self.bot)
        self.setLayout(vbox)

    def update_preview(self):
        """Triggers an update to the preview table."""

        self.preview.setText(self._preview)

    @property
    def _preview(self):
        """Returns a preview of the loaded weather data, if available."""

        if isinstance(self.data, pd.DataFrame):
            return str(self.data.describe())

        elif not self.data:
            return "No Weather Data Loaded"

        else:
            return "Error Displaying Weather Preview"
