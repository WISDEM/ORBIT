"""

"""

from marmot import Object

from ORBIT.core.defaults import process_times as pt


class Cargo(Object):
    def __repr__(self):
        return self.type

    @property
    def type(self):
        """Returns type of `Cargo`."""
        return self.__class__.__name__


class Monopile(Cargo):
    """Monopile Cargo"""

    def __init__(
        self, length=None, diameter=None, mass=None, deck_space=None, **kwargs
    ):
        """
        Creates an instance of `Monopile`.
        """

        self.length = length
        self.diameter = diameter
        self.mass = mass
        self.deck_space = deck_space

    @staticmethod
    def fasten(**kwargs):
        """Returns time required to fasten a monopile at port."""

        key = "mono_fasten_time"
        time = kwargs.get(key, pt[key])

        return "Fasten Monopile", time

    @staticmethod
    def release(**kwargs):
        """Returns time required to release tmonopile from fastenings."""

        key = "mono_release_time"
        time = kwargs.get(key, pt[key])

        return "Release Monopile", time


class TransitionPiece(Cargo):
    """Transition Piece Cargo"""

    def __init__(self, mass=None, deck_space=None, **kwargs):
        """
        Creates an instance of `TransitionPiece`.
        """

        self.mass = mass
        self.deck_space = deck_space

    @staticmethod
    def fasten(**kwargs):
        """Returns time required to fasten a transition piece at port."""

        key = "tp_fasten_time"
        time = kwargs.get(key, pt[key])

        return "Fasten Transition Piece", time

    @staticmethod
    def release(**kwargs):
        """Returns time required to release transition piece from fastenings."""

        key = "tp_release_time"
        time = kwargs.get(key, pt[key])

        return "Release Transition Piece", time
