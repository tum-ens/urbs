import os
import shutil
import urbs


input_files = 'urbs_model_v1.91_eu_2015.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

result_name = 'Run'
result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

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
(offset, length) = (2200, 3300)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# detailed reporting commodity/sites
report_tuples = [(2015, 'AT', 'Elec'),
                 (2015, 'BE', 'Elec'),
                 (2015, 'BG', 'Elec'),
                 (2015, 'CH', 'Elec'),
                 (2015, 'CZ', 'Elec'),
                 (2015, 'DE', 'Elec'),
                 (2015, 'DK', 'Elec'),
                 (2015, 'EE', 'Elec'),
                 (2015, 'EL', 'Elec'),
                 (2015, 'ES', 'Elec'),
                 (2015, 'FI', 'Elec'),
                 (2015, 'FR', 'Elec'),
                 (2015, 'HR', 'Elec'),
                 (2015, 'HU', 'Elec'),
                 (2015, 'IE', 'Elec'),
                 (2015, 'IT', 'Elec'),
                 (2015, 'LT', 'Elec'),
                 (2015, 'LU', 'Elec'),
                 (2015, 'LV', 'Elec'),
                 (2015, 'NL', 'Elec'),
                 (2015, 'NO', 'Elec'),
                 (2015, 'PL', 'Elec'),
                 (2015, 'PT', 'Elec'),
                 (2015, 'RO', 'Elec'),
                 (2015, 'SE', 'Elec'),
                 (2015, 'SI', 'Elec'),
                 (2015, 'SK', 'Elec'),
                 (2015, 'UK', 'Elec'),
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
