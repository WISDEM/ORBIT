"""
Model defaults. Vessel and task related defaults are found in their respective
sub-packages.
"""

__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


defaults = {
    # Development times and durations
    "site_auction_cost": 100e6,  # USD
    "site_auction_duration": 0,  # hrs
    "site_assessment_plan_cost": 0.5e6,  # USD
    "site_assessment_plan_duration": 8760,  # hrs
    "site_assessment_cost": 50e6,  # USD
    "site_assessment_duration": 43800,  # hrs
    "construction_operations_plan_cost": 1e6,  # USD
    "construction_operations_plan_duration": 43800,  # hrs
    "boem_review_cost": 0,  # No cost to developer
    "boem_review_duration": 8760,  # hrs
    "design_install_plan_cost": 0.25e6,  # USD
    "design_install_plan_duration": 8760,  # hrs
    # Phase designs
    "substructure_design_time": 1000,  # hrs
    "array_system_design_time": 1000,  # hrs
    "export_system_design_time": 1000,  # hrs
    "oss_design_time": 1000,  # hrs
    "onshore_trans_design_time": 1000,  # hrs
    # Port properties
    "port_cost_per_month": 5e6,  # USD/month
    # Vessel parameters
    "wtiv_day_rate": 200000,  # USD/day
    "feeder_day_rate": 50000,  # USD/day
    "scour_day_rate": 75000,  # USD/day
    "trench_day_rate": 12000,  # USD/day
    "oss_vessel_day_rate": 250000,  # USD/day
    "array_cable_install_day_rate": 75000,  # USD/day
    "export_cable_install_day_rate": 75000,  # USD/day
}
