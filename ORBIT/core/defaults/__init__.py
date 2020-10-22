"""Default inputs used throughout ORBIT."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"

import os

import yaml

DIR = os.path.split(__file__)[0]

with open(os.path.join(DIR, "process_times.yaml"), "r") as f:
    process_times = yaml.load(f, Loader=yaml.Loader)
