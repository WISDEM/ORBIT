from ORBIT import ProjectManager
from ORBIT.core.library import initialize_library
import os

if __name__ == "__main__":
    base = {
        'config_name': '600MW',
        # Array cables
        'array_cable_install_vessel': 'example_cable_lay_vessel',
        'array_system_design': {
            'cables': ['XLPE_630mm_66kV'],
        },

        # Plant
        'plant': {
            # 'capacity': 600,
            'layout': 'grid',
            'row_spacing': 5,
            'turbine_spacing': 10,
            'substation_distance': 1,
            'num_turbines': 50
        },
        # turbine
        'turbine': {
          'rotor_diameter': 240,
          'turbine_rating': 10
        },
        # Port
        'port': {
            'monthly_rate': 2000000,
            'num_cranes': 3,
            'sub_assembly_lines': 3,
            'turbine_assembly_cranes': 3
        },
        # Project
        # 'project_parameters': {'turbine_capex': 0},
        # Semisub design - defaults
        # Site
        'site': {
            'distance': 30,
            'distance_to_landfall': 30,
            'depth': 500},
        # Substation design - defaults
        # 'substation_design': {
        #     'num_substations': 1
        # },
        # # Vessels
        # 'support_vessel': 'AHTS_vessel',
        # 'towing_vessel': 'tugboat',
        # 'towing_vessel_groups': {
        #     'num_groups': 3,
        #     'station_keeping_vessels': 1,
        #     'towing_vessels': 2,
        # },
        # # Turbine
        # 'turbine': '12MW_generic',

        'design_phases': ['ArraySystemDesign'
                          ],
        'install_phases': ['ArrayCableInstallation'],

        'orbit_version': {}
    }

    initialize_library(os.getcwd())
    project = ProjectManager(base)
    project.run()
    print(project.design_results)
    print(project.detailed_outputs)