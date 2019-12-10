"""
Jake Nunemaker
National Renewable Energy Lab
07/11/2019

This module contains default vessel process times.
"""


defaults = {
    # Cable Lay Vessel Processes
    "carousel_lift_time": 1,  # hr, GUESS
    "carousel_fasten_time": 5,  # hr, GUESS
    "cable_prep_time": 1,  # hr, GUESS
    "cable_lower_time": 1,  # hr, GUESS
    "cable_pull_in_time": 5.5,  # hr (from Legacy BOS)
    "cable_termination_time": 5.5,  # hr (from Legacy BOS)
    "cable_lay_speed": 1,  # km/hr GUESS
    "cable_lay_bury_speed": 0.3,  # km/hr GUESS
    "cable_bury_speed": 0.5,  # km/hr GUESS
    "cable_splice_time": 48,  # hr, GUESS
    "tow_plow_speed": 5,  # km/hr GUESS
    "pull_winch_speed": 5,  # km/hr GUESS
    "cable_raise_time": 0.5,  # hr GUESS
    "trench_dig_speed": 0.1,  # km/hr GUESS
    # Offshore Substation
    "topside_fasten_time": 2,  # hr, GUESS
    "topside_release_time": 2,  # hr, GUESS
    "topside_attach_time": 6,  # hr, GUESS
    # Monopiles
    "mono_embed_len": 30,
    "mono_drive_rate": 20,  # m/hr
    "mono_fasten_time": 12,  # hr, Source?
    "mono_release_time": 3,  # hr, Source?
    "tp_fasten_time": 8,  # hr, GUESS
    "tp_release_time": 2,  # hr, GUESS
    "tp_bolt_time": 4,  # hr, Source?
    "grout_cure_time": 24,  # hr, anecdotal from industry review
    "grout_pump_time": 2,  # hr, GUESS
    # Scour Protection
    "drop_rocks_time": 10,  # hr, GUESS
    "load_rocks_time": 4,  # hr, GUESS
    # Turbines
    "tower_fasten_time": 4,  # hr, Source?
    "tower_release_time": 3,  # hr, Source?
    "tower_attach_time": 6,  # hr, old version less 1-hour lift time
    "nacelle_fasten_time": 4,  # hr, old version, split into components
    "nacelle_release_time": 3,  # hr, GUESS
    "nacelle_attach_time": 6,  # hr, old version less 1-hour lift time
    "blade_fasten_time": 1.5,  # hr, old version, split into components
    "blade_release_time": 1,  # hr, GUESS
    "blade_attach_time": 3.5,  # hr, old version less 1-hour lift time
    # Misc.
    "site_position_time": 2,
    "rov_survey_time": 1,
    "crane_reequip_time": 1,
}
