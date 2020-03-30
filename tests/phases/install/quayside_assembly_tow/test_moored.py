"""Tests for the `MooredSubInstallation` class and related infrastructure."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from copy import deepcopy

import pytest

from tests.data import test_weather
from ORBIT.library import initialize_library, extract_library_specs
from ORBIT.phases.install import MooredSubInstallation

initialize_library(pytest.library)
