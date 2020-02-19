import os
import shutil
import nopt
import ipdb

input_files = 'single_year_example.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

result_name = input_files[0:4]
result_dir = nopt.prepare_result_directory(result_name)  # name + time stamp

# copy input file to result directory
try:
    shutil.copytree(input_path, os.path.join(result_dir, input_dir))
except NotADirectoryError:
    shutil.copyfile(input_path, os.path.join(result_dir, input_files))
# copy run file to result directory
shutil.copy(__file__, result_dir)

# objective is a list of tuples. Last element of the Tuple must be the optimization objective. Possible objectives are given in the list below:
# [ 'cost' 'CO2' 'Biomass plant','Coal plant','Feed-in', 'Gas plant', 'Hydro plant', 'Lignite plant','Photovoltaics', 'Purchase', 'Slack powerplant', 'Wind park']
# Site names that will be subjected to the minimization must be given before the objective name.
# No site name indicates minimize/maximize total capacity of all sites
# example objectives [('South','Photovoltaics'),('Photovoltaics'),('South','North','cost')] etc.

objective = [('Wind park')]
# Choose Solver (cplex, glpk, gurobi, ...)
solver = 'gurobi'

# simulation timesteps
(offset, length) = (8456, 24)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# detailed reporting commodity/sites
report_tuples = [

    ]

# optional: define names for sites in report_tuples
report_sites_name = {}

# plotting commodities/sites
plot_tuples = [

    ]

# optional: define names for sites in plot_tuples
plot_sites_name = {}

# plotting timesteps
plot_periods = {
    'all': timesteps[1:]
}

# add or change plot colors
my_colors = {}
for country, color in my_colors.items():
    nopt.COLORS[country] = color

# select scenarios to be run
scenarios = [
             nopt.scenario_base,
            ]

for scenario in scenarios:
    prob = nopt.run_scenario(input_path, solver, timesteps, scenario,
                             result_dir, dt, objective,
                             plot_tuples=plot_tuples,
                             plot_sites_name=plot_sites_name,
                             plot_periods=plot_periods,
                             report_tuples=report_tuples,
                             report_sites_name=report_sites_name)
