__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem

from ORBIT import ProjectManager


class Config(QTreeWidget):
    """Widget for viewing and editing project configurations."""

    def __init__(self):
        """
        Creates an instance of `Config`.

        Parameters
        ----------
        config : dict
            Configuration to view and allow editing.
        """

        super().__init__()
        # self.initUI()
        self.name = "Configuration"

    def update(self, modules):

        self.clear()
        _dict = ProjectManager.compile_input_dict(modules)
        self.create_item(self.invisibleRootItem(), _dict)

    def new_item(self, parent, text, val=None, editable=False):
        """
        Creates a new item.

        Parameters
        ----------
        parent : QTreeWidgetItem
            Parent object.
        text : str
            Item key.
        val : varies
            Item value.
        editable : bool
            Editable flag used for non-container values.
        """

        child = QTreeWidgetItem([text])
        self.create_item(child, val)
        parent.addChild(child)

        if editable:
            child.setFlags(child.flags() | Qt.ItemIsEditable)

    def create_item(self, item, value):

        if value is None:
            return

        elif isinstance(value, dict):
            for key, val in sorted(value.items()):
                self.new_item(item, str(key), val)

        elif isinstance(value, (list, tuple)):
            for val in value:
                text = (
                    str(val)
                    if not isinstance(val, (dict, list, tuple))
                    else "[%s]" % type(val).__name__
                )
                self.new_item(item, text, val)

        else:
            self.new_item(item, str(value), editable=True)
