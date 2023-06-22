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


input_files = 'urbs_file.xlsx'  # for single year file name, for intertemporal folder name
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
noTypicalPeriods = 2
hoursPerPeriod = 24

# simulation timesteps
(offset, length) = (0,8760)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# detailed reporting commodity/sites
#report_tuples = []
import pandas as pd
import glob
if os.path.isdir(input_path):
    glob_input = os.path.join(input_path, '*.xlsx')
    input_files = sorted(glob.glob(glob_input))
else:
    input_files = [input_path]
for filename in input_files:
    print("Reading for site names and mode")
    with pd.ExcelFile(filename) as xls:
        site = xls.parse('Site').set_index(['Name'])
        print("Site reading complete")

        global_props = xls.parse('Global').set_index('Property')
        tsam = global_props.loc['tsam']['value']
        uncoordinated = global_props.loc['uncoordinated']['value']
        flexible = global_props.loc['flexible']['value']
        lp = global_props.loc['lp']['value']
        excel = global_props.loc['excel']['value']
        assumelowq = global_props.loc['assumelowq']['value']
        grid_curtailment = global_props.loc['grid_curtailment']['value']
        #uncoordinated = 1
        print("Mode reading complete:")
        print('tsam:             {}'.format(tsam))
        print('uncoordinated:    {}'.format(uncoordinated))
        print('flexible:         {}'.format(flexible))
        print('grid_curtailment: {}'.format(grid_curtailment))
        print('lp:               {}'.format(lp))
        print('excel:            {}'.format(excel))
        print('assumelowq:       {}'.format(assumelowq))



report_tuples =           [(2022, sit, 'electricity') for sit in site.index if sit[0:4] == 'load'] \
                        + [(2022, sit, 'electricity-reactive') for sit in site.index if sit[0:4] == 'load'] \
                        + [(2022, sit, 'common_heat') for sit in site.index if sit[0:4] == 'load'] \
                        + [(2022, sit, 'electricity_hp') for sit in site.index if sit[0:4] == 'load']

report_tuples_grid_plan = [(2022, sit, 'electricity') for sit in site.index if sit[0:4] == 'load'] \
                          + [(2022, sit, 'electricity-reactive') for sit in site.index if sit[0:4] == 'load']

#report_tuples = []

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
#time_series_for_aggregation = {'demand': ['electricity', ']}
# select scenarios to be run
scenarios = [
             urbs.flex_all
            ]


cross_scenario_data = dict()
for scenario in scenarios:
    if uncoordinated:
        prob, prob_grid_plan, prob_hp_react, cross_scenario_data = urbs.run_dist_opt(input_path, solver, timesteps, scenario, result_dir, dt, objective, microgrid_paths,
                         plot_tuples=plot_tuples,
                         plot_sites_name=plot_sites_name,
                         plot_periods=plot_periods,
                         report_tuples=report_tuples,
                         cross_scenario_data = cross_scenario_data,
                         report_sites_name=report_sites_name,
                         noTypicalPeriods=noTypicalPeriods,
                         hoursPerPeriod=hoursPerPeriod,
                         uncoordinated = uncoordinated,
                         flexible = flexible,
                         grid_curtailment=grid_curtailment,
                         lp=lp,
                         xls=excel,
                         assumelowq = assumelowq)
    else:
        prob, cross_scenario_data = urbs.run_dist_opt(input_path, solver, timesteps, scenario, result_dir, dt, objective, microgrid_paths,
                         plot_tuples=plot_tuples,
                         plot_sites_name=plot_sites_name,
                         plot_periods=plot_periods,
                         report_tuples=report_tuples,
                         cross_scenario_data = cross_scenario_data,
                         report_sites_name=report_sites_name,
                         noTypicalPeriods=noTypicalPeriods,
                         hoursPerPeriod=hoursPerPeriod,
                         uncoordinated = uncoordinated,
                         flexible = flexible,
                         grid_curtailment=grid_curtailment,
                         lp=lp,
                         xls=excel,
                         assumelowq = assumelowq)   