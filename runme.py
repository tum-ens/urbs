import os
import shutil
import urbs


input_files = '2016_Laos_20200417.xlsx'  # for single year file name, for intertemporal folder name
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
(offset, length) = (0, 8760)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# detailed reporting commodity/sites
report_tuples = [
                 (2016, 'Attapu', 'Elec'),
                 (2016, 'Bokeo', 'Elec'),
                 (2016, 'Bolikhamxai', 'Elec'),
                 (2016, 'Champasak', 'Elec'),
                 (2016, 'Houaphan', 'Elec'),
                 (2016, 'Khammouan', 'Elec'),
                 (2016, 'LouangNamtha', 'Elec'),
                 (2016, 'Louangphrabang', 'Elec'),
                 (2016, 'Oudomxai', 'Elec'),
                 (2016, 'Phongsali', 'Elec'),
                 (2016, 'Saravan', 'Elec'),
                 (2016, 'Savannakhet', 'Elec'),
                 (2016, 'VientianeProvince', 'Elec'),
                 (2016, 'VientianePrefecture', 'Elec'),
                 (2016, 'Xaignabouri', 'Elec'),
                 (2016, 'Xaisomboun', 'Elec'),
                 (2016, 'Xiangkhoang', 'Elec'),
                 (2016, 'Xekong', 'Elec'),
                 (2016, 'China', 'Elec'),
                 (2016, 'Thailand', 'Elec'),
                 (2016, 'Vietnam', 'Elec'),
                 (2016, 'Cambodia', 'Elec'),
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
