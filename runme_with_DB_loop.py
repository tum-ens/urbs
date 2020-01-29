import os
import shutil
import urbs
from Database_to_urbs import Database_to_urbs

# # User preferences

version = 'v2.00'
suffix = "_eu"
result_folder = 'v2.00_2035_eu-20200126T1344'
fs = os.path.sep

for year in [2040, 2045, 2050]:
    
    # Generate input file from database
    Database_to_urbs(version, suffix, year, result_folder)
    year = str(int(year))
    
    input_files = year + suffix + '.xlsx'  # for single year file name, for intertemporal folder name
    input_dir = 'Input' + fs + version
    input_path = os.path.join(input_dir, input_files)

    result_name = version + '_' + str(year) + suffix 
    result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp
    result_folder = result_dir
    
    # copy input file to result directory
    try:
        shutil.copytree(input_path, os.path.join(result_dir, input_dir))
    except NotADirectoryError:
        shutil.copyfile(input_path, os.path.join(result_dir, input_files))
    # copy run file to result directory
    shutil.copy(__file__, result_dir)
    
    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective
    
    # Choose Solver (cplex, glpk, gurobi, ...)
    solver = 'gurobi'
    
    # simulation timesteps
    (offset, length) = (0, 8760)  # time step selection
    timesteps = range(offset, offset+length+1)
    dt = 1  # length of each time step (unit: hours)
    
    # detailed reporting commodity/sites
    report_tuples = [(int(year), 'AT', 'Elec'),
                    (int(year), 'BE', 'Elec'),
                    (int(year), 'BG', 'Elec'),
                    (int(year), 'CH', 'Elec'),
                    (int(year), 'CZ', 'Elec'),
                    (int(year), 'DE', 'Elec'),
                    (int(year), 'DK', 'Elec'),
                    (int(year), 'EE', 'Elec'),
                    (int(year), 'EL', 'Elec'),
                    (int(year), 'ES', 'Elec'),
                    (int(year), 'FI', 'Elec'),
                    (int(year), 'FR', 'Elec'),
                    (int(year), 'HR', 'Elec'),
                    (int(year), 'HU', 'Elec'),
                    (int(year), 'IE', 'Elec'),
                    (int(year), 'IT', 'Elec'),
                    (int(year), 'LT', 'Elec'),
                    (int(year), 'LU', 'Elec'),
                    (int(year), 'LV', 'Elec'),
                    (int(year), 'NL', 'Elec'),
                    (int(year), 'NO', 'Elec'),
                    (int(year), 'PL', 'Elec'),
                    (int(year), 'PT', 'Elec'),
                    (int(year), 'RO', 'Elec'),
                    (int(year), 'SE', 'Elec'),
                    (int(year), 'SI', 'Elec'),
                    (int(year), 'SK', 'Elec'),
                    (int(year), 'UK', 'Elec'),
                    ]
    
    # optional: define names for sites in report_tuples
    report_sites_name = {}
    
    # plotting commodities/sites
    plot_tuples = []
    
    # optional: define names for sites in plot_tuples
    plot_sites_name = {}
    
    # plotting timesteps
    plot_periods = {
        'all': timesteps[1:]
    }
    
    # add or change plot colors
    my_colors = {}
    for country, color in my_colors.items():
        urbs.COLORS[country] = color
    
    # select scenarios to be run
    scenarios = [
                urbs.scenario_base
                ]
    
    for scenario in scenarios:
        prob = urbs.run_scenario(input_path, solver, timesteps, scenario,
                                result_dir, dt, objective,
                                plot_tuples=plot_tuples,
                                plot_sites_name=plot_sites_name,
                                plot_periods=plot_periods,
                                report_tuples=report_tuples,
                                report_sites_name=report_sites_name)
    del prob
    