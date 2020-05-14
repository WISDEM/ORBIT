__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QStyledItemDelegate

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

        self.name = "Configuration"

        self.inputs = {}
        self.setColumnCount(2)
        self.setHeaderLabels(["Key", "Value"])
        self.setItemDelegateForColumn(0, NoEditDelegate(self))

    def update(self, modules):

        self.clear()
        _dict = ProjectManager.compile_input_dict(modules)
        self.create_tree_from_dict(self.invisibleRootItem(), _dict)

    def create_child(self, parent, text, value=None):
        """
        Creates child `QTreeWidgetItem`.

        Parameters
        ----------
        parent : QWidget
        text : str
        value : str | list | dict
        """

        if isinstance(value, dict):
            child = QTreeWidgetItem(parent)
            child.setText(0, text)
            self.create_tree_from_dict(child, value)
            parent.addChild(child)

        elif isinstance(value, (list, tuple)):
            pass

        else:
            child = QTreeWidgetItem(parent)
            child.setText(0, text)
            child.setText(1, value)
            child.setFlags(child.flags() | Qt.ItemIsEditable)
            parent.addChild(child)

    def create_tree_from_dict(self, parent, _dict):
        """
        Nests additional key, value pairs of `_dict` under `parent`.

        Parameters
        ----------
        parent : QTreeWidget
        _dict : dict
        """

        for k, v in _dict.items():
            self.create_child(parent, k, v)

    @property
    def config(self):
        """Returns the current configuration."""

        return self.get_children(self.invisibleRootItem())

    def get_children(self, item):
        """Recursive method to return children of `item` as a `dict`."""

        children = {}
        for i in range(item.childCount()):
            child = item.child(i)

            if child.childCount() > 0:
                children[child.text(0)] = self.get_children(child)

            else:
                try:
                    if float(child.text(1)) == int(child.text(1)):
                        val = int(child.text(1))

                    else:
                        val = float(child.text(1))

                except ValueError:
                    val = child.text(1)

                children[child.text(0)] = val

        return children


class NoEditDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        """
        Creates an instance of `NoEditDelegate`, used to disable editing a
        column in a `QTreeWidget`.
        """
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        """Overridden method to return no edit when triggered."""
        return
