import os
import shutil
import urbs
from urbs.runfunctions_admm import *
from multiprocessing import freeze_support

# input_files = 'mimo-example_internal.xlsx'  # for single year file name, for intertemporal folder name
input_files = 'germany.xlsx'  # for single year file name, for intertemporal folder name
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

# simulation timesteps
(offset, length) = (0, 8760)  # time step selection
timesteps = range(offset, offset + length + 1)
dt = 1  # length of each time step (unit: hours)

# clusters = [(('Schleswig-Holstein'),('Hamburg'),('Mecklenburg-Vorpommern'),('Offshore'),('Lower Saxony'),('Bremen'),('Saxony-Anhalt'),('Brandenburg'),('Berlin'),('North Rhine-Westphalia')),
#                (('Baden-Württemberg'),('Hesse'),('Bavaria'),('Rhineland-Palatinate'),('Saarland'),('Saxony'),('Thuringia'))]
clusters = [[('Schleswig-Holstein')], [('Hamburg')], [('Mecklenburg-Vorpommern')], [('Offshore')], [('Lower Saxony')],
            [('Bremen')], [('Saxony-Anhalt')], [('Brandenburg')], [('Berlin')], [('North Rhine-Westphalia')],
            [('Baden-Württemberg')], [('Hesse')], [('Bavaria')], [('Rhineland-Palatinate')], [('Saarland')],
            [('Saxony')], [('Thuringia')]]

# clusters = [[('Mid'),('Mid_int')],[('South'),('North')]]

# add or change plot colors
my_colors = {
    'South': (230, 200, 200),
    'Mid': (200, 230, 200),
    'North': (200, 200, 230)}
for country, color in my_colors.items():
    urbs.COLORS[country] = color

# select scenarios to be run
scenarios = [
    urbs.scenario_base
]

# test, ignore
# list_timesteps = [7000, 8000, 8760]

if __name__ == '__main__':
    freeze_support()
    # test, ignore
    for scenario in scenarios:
        # for test_length in list_timesteps:
        #    (offset, length) = (0, test_length)  # time step selection
        # timesteps = range(offset, offset + length + 1)
        prob = urbs.run_regional(input_path, timesteps,
                                 scenario, result_dir, dt, objective,
                                 clusters=clusters)
