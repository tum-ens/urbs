# -*- coding: utf-8 -*-
import os
import shutil
import urbs
# import sys
# import time as t
# import numpy as np
# import multiprocessing as mp
# from os import getpid
# import matplotlib.pyplot as plt
from urbs.runfunctions import *


input_files = 'Transmission_Level.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

microgrid_files = ['Microgrid_rural_A.xlsx','Microgrid_urban_A.xlsx']
microgrid_dir = 'Input/microgrid_types'
microgrid_paths = []
for i, microgrid_file in enumerate(microgrid_files):
    microgrid_paths.append(os.path.join(microgrid_dir, microgrid_file))

result_name = 'Trans-Dist'
result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

# #copy input file to result directory
try:
    shutil.copytree(input_path, os.path.join(result_dir, input_dir))
except NotADirectoryError:
    shutil.copyfile(input_path, os.path.join(result_dir, input_files))

# #copy run file to result directory
shutil.copy(__file__, result_dir)

# objective function
objective = 'cost'  # set either 'cost' or 'CO2' as objective

# Choose Solver (cplex, glpk, gurobi, ...)
solver = 'gurobi'

# input data for tsam method
noTypicalPeriods = 4
hoursPerPeriod = 168

# simulation timesteps
(offset, length) = (0,8760)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# detailed reporting commodity/sites
report_tuples = []
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

# select scenarios to be run
scenarios = [
             urbs.transdist100, # transdist100 scenarios must be simulated first to store distribution demand
             #urbs.transdist66,
             #urbs.transdist33,
             #urbs.transmission
            ]

cross_scenario_data = dict()
for scenario in scenarios:
    prob, cross_scenario_data = urbs.run_scenario(input_path, solver, timesteps, scenario,
                             result_dir, dt, objective, microgrid_paths,
                             plot_tuples=plot_tuples,
                             plot_sites_name=plot_sites_name,
                             plot_periods=plot_periods,
                             report_tuples=report_tuples,
                             cross_scenario_data = cross_scenario_data,
                             report_sites_name=report_sites_name,
                             noTypicalPeriods=noTypicalPeriods,
                             hoursPerPeriod=hoursPerPeriod)

    # save cross_Scenario dara
    # PV_private_rooftop capacity results for 100% distribution grids are saved to use equal PV capacities in the subsequent scenarios
    if scenario.__name__ == 'transdist100':
        cap_PV_private = prob._result['cap_pro'].loc[:, :, 'PV_private_rooftop'].droplevel(level=[0])
        cap_PV_private.index = pd.MultiIndex.from_tuples(cap_PV_private.index.str.split('_').tolist())
        cap_PV_private = cap_PV_private.groupby(level=[2]).sum().to_frame()
        cap_PV_private.index.name = 'sit'
        cap_PV_private['pro'] = 'PV_private_rooftop'
        cap_PV_private.set_index(['pro'], inplace=True, append=True)
        cap_PV_private = cap_PV_private.squeeze()
        cross_scenario_data['PV_cap_shift'] = cap_PV_private

