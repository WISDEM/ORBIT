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

    def update_tree(self, modules):
        """
        Updates the tree view to include the parameters of `modules`.

        Parameters
        ----------
        modules : list
            List of ORBIT modules to display configuration parameters for.
        """

        try:
            self.itemChanged.disconnect()

        except RuntimeError:
            pass

        self.clear()

        base = ProjectManager.compile_input_dict(modules)
        user = ProjectManager.merge_dicts(base, self.inputs)

        self.create_tree_from_dict(self.invisibleRootItem(), user)
        self.itemChanged.connect(lambda x: self.save_input(x))

    def config(self, modules, remove_optional=True):
        """
        Returns the current configuration related to input `modules`. Precedence
        is given to inputs in `self.inputs` and default values are removed.

        Parameters
        ----------
        modules : list
            List of ORBIT modules to display configuration parameters for.
        remove_optional : bool
            Flag to toggle if the optional paramater strings are returned or
            removed.
        """

        base = ProjectManager.compile_input_dict(modules)
        base = self._remove_empty(base)
        if remove_optional:
            base = self._remove_optional(base)

        user = ProjectManager.merge_dicts(base, self.inputs)
        return user

    @classmethod
    def _remove_optional(cls, dct):
        """Removes any keys from `dct` if the value includes 'optional'."""

        for key in list(dct.keys()):

            if isinstance(dct[key], str) and "optional" in dct[key]:
                del dct[key]

            elif isinstance(dct[key], dict):
                cls._remove_optional(dct[key])

            else:
                pass

        return dct

    @classmethod
    def _remove_empty(cls, dct):
        """Removes any keys from `dct` if the values are empty."""

        for key in list(dct.keys()):

            if isinstance(dct[key], str) and not dct[key]:
                del dct[key]

            elif isinstance(dct[key], dict):
                cls._remove_empty(dct[key])

            else:
                pass

        return dct

    def create_child(self, parent, text, value=None):
        """
        Creates `QTreeWidgetItem` as a child of `parent`.

        Parameters
        ----------
        parent : QWidget
        text : str
            Child key.
        value : str | list | dict
            Child value.
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

    def save_input(self, item):
        """
        Saves the input `item` in the nested dict `self.inputs`.

        Parameters
        ----------
        item : QTreeWidgetItem
        """

        if item.text(1):
            updated = self.item_location(item)
            self.inputs = ProjectManager.merge_dicts(self.inputs, updated)

    def item_location(self, item):
        """
        Returns a dictionary containing `item` at it's location from
        `self.invisibleRootItem()`.

        Parameters
        ----------
        item : QTreeWidgetItem
        """

        val = self._type_conv(item.text(1))
        parents = [item.text(0)]

        while True:
            try:
                parent = item.parent()
                parents.append(parent.text(0))
                item = parent

            except AttributeError:
                break

        return self._path_to_dict(parents[::-1], val)

    @staticmethod
    def _path_to_dict(lst, val):
        """Returns a nested dictionary with keys from `lst` ending at `val`."""

        dct = {}
        for i, key in enumerate(reversed(lst)):
            if i == 0:
                dct = {key: val}

            else:
                dct = {key: dct}

        return dct

    @staticmethod
    def _type_conv(val):
        """Returns `val` as float if possible, then int, then str."""

        try:
            if float(val) == int(val):
                val = int(val)

            else:
                val = float(val)

        # TODO: list/dict input types
        except ValueError:
            val = val

        return val

    def view_tree(self):
        """Returns a nested dict view of the entire tree."""

        return self._get_children(self.invisibleRootItem())

    def _get_children(self, item):
        """Recursive method to return children of `item` as a `dict`."""

        children = {}
        for i in range(item.childCount()):
            child = item.child(i)

            if child.childCount() > 0:
                children[child.text(0)] = self._get_children(child)

            else:
                children[child.text(0)] = self._type_conv(child.text(1))

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
