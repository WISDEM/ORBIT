"""Tests for common infrastructure for quayside assembly tow-out simulations"""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import pytest

from ORBIT.core import WetStorage
from ORBIT.phases.install.quayside_assembly_tow.common import (
    SubstructureAssemblyLine,
)


@pytest.mark.parametrize(
    "num, assigned, expected",
    [
        (1, [], 0),
        (1, [1] * 10, 100),
        (2, [1] * 10, 50),
        (3, [1] * 10, 40),
        (5, [1] * 10, 20),
        (10, [1] * 10, 10),
    ],
)
def test_SubstructureAssemblyLine(env, num, assigned, expected):

    _assigned = len(assigned)
    storage = WetStorage(env)

    for a in range(num):
        assembly = SubstructureAssemblyLine(assigned, 10, storage, a + 1)
        env.register(assembly)
        assembly.start()

    env.run()

    assert len(env.actions) == _assigned
    assert env.now == expected
