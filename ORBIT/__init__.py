""" Initializes ORBIT and provides the top-level import objects."""

__author__ = ["Jake Nunemaker", "Matt Shields", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov", "robert.hammond@nrel.gov"]
__status__ = "Development"


from ORBIT.manager import ProjectManager  # isort:skip
from ORBIT.config import load_config, save_config
from ORBIT.parametric import ParametricManager
from ORBIT.supply_chain import SupplyChainManager

__version__ = "1.0.8"
