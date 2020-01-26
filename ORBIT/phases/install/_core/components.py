"""Provides the `Crane` class."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import itertools
from dataclasses import dataclass

import numpy as np

from ORBIT.vessels.tasks._defaults import defaults


class Crane:
    """Base Crane Class"""

    def __init__(self, crane_specs):
        """
        Creates an instance of Crane.

        Parameters
        ----------
        crane_specs : dict
            Dictionary containing crane system specifications.
        """

        self.extract_crane_specs(crane_specs)

    def extract_crane_specs(self, crane_specs):
        """
        Extracts and defines crane specifications.

        Parameters
        ----------
        crane_specs : dict
            Dictionary of crane specifications.
        """

        # Physical Dimensions
        self.boom_length = crane_specs.get("boom_length", None)
        self.radius = crane_specs.get("radius", None)

        # Operational Parameters
        self.max_lift = crane_specs.get("max_lift", None)
        self.max_hook_height = crane_specs.get("max_hook_height", None)
        self.max_windspeed = crane_specs.get("max_windspeed", 99)

    @staticmethod
    def crane_rate(**kwargs):
        """
        Calculates minimum crane rate based on current wave height equation
        from DNV standards for offshore lifts.

        Parameters
        ----------
        wave_height : int | float
            Significant wave height (m).

        Returns
        -------
        crane_rate : float
            Hoist speed of crane (m/hr).
        """

        wave_height = kwargs.get("wave_height", 2)
        return 0.6 * wave_height * 3600

    @staticmethod
    def reequip(**kwargs):
        """
        Calculates time taken to change crane equipment.

        Parameters
        ----------
        crane_reequip_time : int | float
            Time required to change crane equipment (h).

        Returns
        -------
        reequip_time : float
            Time required to change crane equipment (h).
        """

        _key = "crane_reequip_time"
        duration = kwargs.get(_key, defaults[_key])

        return duration


class JackingSys:
    """Base Jacking System Class"""

    def __init__(self, jacksys_specs):
        """
        Creates an instance of JackingSys.

        Parameters
        ----------
        jacksys_specs : dict
            Dictionary containing jacking system specifications.
        """

        self.extract_jacksys_specs(jacksys_specs)

    def extract_jacksys_specs(self, jacksys_specs):
        """
        Extracts and defines jacking system specifications.

        Parameters
        ----------
        jacksys_specs : dict
            Dictionary containing jacking system specifications.
        """

        # Physical Dimensions
        self.num_legs = jacksys_specs.get("num_legs", None)
        self.leg_length = jacksys_specs.get("leg_length", None)
        self.air_gap = jacksys_specs.get("air_gap", None)
        self.leg_pen = jacksys_specs.get("leg_pen", None)

        # Operational Parameters
        self.max_depth = jacksys_specs.get("max_depth", None)
        self.max_extension = jacksys_specs.get("max_extension", None)
        self.speed_below_depth = jacksys_specs.get("speed_below_depth", None)
        self.speed_above_depth = jacksys_specs.get("speed_above_depth", None)

    def jacking_time(self, extension, depth):
        """
        Calculates jacking time for a given depth.

        Parameters
        ----------
        extension : int | float
            Height to jack-up to or jack-down from (m).
        depth : int | float
            Depth at jack-up location (m).

        Returns
        -------
        extension_time : float
            Time required to jack-up to given extension (h).
        """

        if extension > self.max_extension:
            raise Exception(
                "{} extension is greater than {} maximum"
                "".format(extension, self.max_extension)
            )

        elif depth > self.max_depth:
            raise Exception(
                "{} is beyond the operating depth {}"
                "".format(depth, self.max_depth)
            )

        elif depth > extension:
            raise Exception("Extension must be greater than depth")

        else:
            return (
                depth / self.speed_below_depth
                + (extension - depth) / self.speed_above_depth
            ) / 60


@dataclass
class Carousel:
    """
    Data class that represents the cable information contained on a single
    carousel.
    """

    name: str
    length: float
    weight: float
    section_lengths: list
    section_masses: list
    section_bury_speeds: list
    deck_space: int


class CarouselSystem:
    """
    CarouselSystem to define the carousels required for an installation.

    Parameters
    ----------
    cables : dict
        Dictionary of cable names with their respective sections to be
        installed and linear densities.
    vessel : Vessel
        An initialized vessel with property vessel.storage

    Attributes
    ----------
    cables : dict
        Dictionary of cable names with their respective sections to be
        installed and linear densities.
    max_cargo_weight : int | float
        Maximum cargo weight or carousel weight allowed.
    carousels : dict
        A dictionary of `Carousel` objects to be loaded onto a cable
        installation vessel.

    Methods
    -------
    create_carousels
        Creates the carousel objects to install all required cable sections.
    """

    def __init__(self, cables, max_cargo_weight):
        """
        Carousel object that produces the carousels required for installation.

        Parameters
        ----------
        cables : dict
            Dictionary of cables section lengths to be installed and the linear
            denisty of each cable. This is the `output_config` from
            `ArraySystemDesign` or `ExportSystemDesign` that is created in the
            method `design_result` if not provided as custom input.
            cables = {
                "name": {
                    "linear_density": "int | float",
                    "cable_sections": [("float", "int")]
                }
            }
        max_cargo_weight : int | float
            Maximum weight allowed on a vessel/in a carousel.
        """

        self.cables = cables
        self.max_cargo_weight = max_cargo_weight

        self.carousels = {}

    def _create_section_list(self, cable_name):
        """
        Creates a list of section lengths and masses to be installed.

        Parameters
        ----------
        cable_name : str
            Name of the cable type to create the sections list.

        Returns
        -------
        lengths : np.ndarray
            Array of all cable section lengths to be installed in km.
        masses : np.ndarray
            Array of cable section masses to be installed in tonnes.
        """

        length_speed = np.array(
            list(
                itertools.chain.from_iterable(
                    [[length, *_]] * n
                    for length, *_, n in self.cables[cable_name][
                        "cable_sections"
                    ]
                )
            )
        )
        if length_speed.shape[1] == 1:
            bury_speeds = np.full(length_speed.shape[0], -1)
        else:
            bury_speeds = length_speed[:, 1]

        lengths = length_speed[:, 0]

        masses = np.round_(
            lengths * self.cables[cable_name]["linear_density"], 10
        )

        return lengths, masses, bury_speeds

    def _create_cable_carousel_with_splice(
        self,
        max_length,
        cable_index,
        section_lengths,
        section_masses,
        section_bury_speeds,
    ):
        """
        Creates a `Carousel` of spliced cables with only a single cable section
        on any individual carousel.
        """

        j = 1
        name = f"Carousel {cable_index}-{j}"
        section_lengths = section_lengths.tolist()
        section_masses = section_masses.tolist()
        section_bury_speeds = section_bury_speeds.tolist()

        while section_lengths:
            remaining_length = section_lengths.pop(0)
            remaining_mass = section_masses.pop(0)
            speed = section_bury_speeds.pop(0)

            while remaining_length:
                length = min(max_length, remaining_length)
                pct = length / remaining_length
                mass = remaining_mass * pct
                self.carousels[name] = Carousel(
                    name, length, mass, [length], [mass], [speed], 1
                )

                j += 1
                name = name = f"Carousel {cable_index}-{j}"
                remaining_length -= length
                remaining_mass -= mass

    def _create_cable_carousel_without_splice(
        self,
        max_length,
        cable_index,
        section_lengths,
        section_masses,
        section_bury_speeds,
    ):
        """
        Creates carousels of unspliced cables with only a single cable type on
        any individual carousel.

        Parameters
        ----------
        max_length : float
            Maximum length of cable that can fit on a carousel.
        cable_index : int
            1-indexed index of the cable that has a cable being created.
        section_lengths : np.ndarray
            Array of section lengths that need to be installed. Lengths
            correspond to`section_masses`.
        section_masses : np.ndarray
            Array of section masses that need to be installed. Masses
            correspond to`section_lengths`.
        """

        j = 1
        name = f"Carousel {cable_index}-{j}"

        while section_lengths.size > 0:
            sum_lengths = np.cumsum(section_lengths)
            max_sections_ix = np.where(sum_lengths <= max_length)[0][-1]

            self.carousels[name] = Carousel(
                name,
                sum_lengths[max_sections_ix],
                section_masses[: max_sections_ix + 1].sum(),
                section_lengths[: max_sections_ix + 1].tolist(),
                section_masses[: max_sections_ix + 1].tolist(),
                section_bury_speeds[: max_sections_ix + 1].tolist(),
                1,
            )

            j += 1
            name = f"Carousel {cable_index}-{j}"
            section_lengths = section_lengths[max_sections_ix + 1 :]
            section_masses = section_masses[max_sections_ix + 1 :]
            section_bury_speeds = section_bury_speeds[max_sections_ix + 1 :]

    def _create_cable_carousel(self, cable_name, max_length, cable_index):
        """
        Creates the individual `Carousel`s.

        Parameters
        ----------
        cable_name : str
            Dictionary key the cable.
        max_length : float
            Maximum length of cable allowed on a single carousel.
        cable_index : int
            1-indexed index of cable to keep track of which `Carousel` has what
            type of cable.
        """

        lengths, masses, bury_speeds = self._create_section_list(cable_name)
        if (lengths > max_length).sum() > 0:
            self._create_cable_carousel_with_splice(
                max_length, cable_index, lengths, masses, bury_speeds
            )
        else:
            self._create_cable_carousel_without_splice(
                max_length, cable_index, lengths, masses, bury_speeds
            )

    def create_carousels(self):
        """
        Creates the carousel information by cable type.
        """

        for i, (name, cable) in enumerate(self.cables.items()):
            max_cable_len_per_carousel = (
                self.max_cargo_weight / cable["linear_density"]
            )
            if cable["cable_sections"]:
                self._create_cable_carousel(
                    name, max_cable_len_per_carousel, i + 1
                )
