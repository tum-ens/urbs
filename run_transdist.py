# -*- coding: utf-8 -*-
import os
import shutil
import urbs
import sys
import time as t
import numpy as np
import multiprocessing as mp
from os import getpid
import matplotlib.pyplot as plt
from urbs.runfunctions import *


input_files = 'Transmission_Level_reduced_buysell-validation.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

microgrid_files = ['Microgrid_A_Dorf_reduced.xlsx','Microgrid_A_Dorf.xlsx']
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

# simulation timesteps
(offset, length) = (0,10)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# input data for tsam method
noTypicalPeriods = 4
hoursPerPeriod = 168

# detailed reporting commodity/sites
report_tuples = [
     # (2021, 'BB', 'electricity'),
     # (2021, 'BE', 'electricity'),
     # (2021, 'BW', 'electricity'),
     # (2021, 'BY', 'electricity'),
     # (2021, 'HB', 'electricity'),
     # (2021, 'HE', 'electricity'),
     # (2021, 'HH', 'electricity'),
     # (2021, 'MV', 'electricity'),
     # (2021, 'NI', 'electricity'),
     # (2021, 'NW', 'electricity'),
     # (2021, 'RP', 'electricity'),
     # (2021, 'SH', 'electricity'),
     # (2021, 'SL', 'electricity'),
     # (2021, 'SN', 'electricity'),
     # (2021, 'ST', 'electricity'),
     # (2021, 'TH', 'electricity'),
     # (2021, 'Baltic', 'electricity'),
     # (2021, 'North', 'electricity'),
     # (2021, 'BY', 'H2'),
     # (2021, 'MV', 'H2'),
     # (2021, 'NW', 'H2')
    ]
    #  (2021, 'node0_A1_Bayern', 'electricity'),
    #  (2021, 'node1_A1_Bayern', 'electricity'),
    #  (2021, 'node2_A1_Bayern', 'electricity'),
    #  (2021, 'node3_A1_Bayern', 'electricity'),
    #  (2021, 'node4_A1_Bayern', 'electricity'),
    #  (2021, 'node5_A1_Bayern', 'electricity'),
    #  (2021, 'node6_A1_Bayern', 'electricity'),
    #  (2021, 'node7_A1_Bayern', 'electricity'),
    #  (2021, 'node8_A1_Bayern', 'electricity'),
    #  (2021, 'node9_A1_Bayern', 'electricity'),
    # (2021, 'node0_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node1_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node2_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node3_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node4_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node5_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node6_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node7_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node8_A1_Bayern', 'Elec-Reactive'),
    # (2021, 'node9_A1_Bayern', 'Elec-Reactive')

# optional: define names for sites in report_tuples
report_sites_name = {
     # ('BB', 'BE', 'BW', 'BY', 'HB', 'HE', 'HH', 'MV', 'NI', 'NW', 'RP', 'SH',
     #  'SL', 'SN', 'ST', 'TH', 'Baltic', 'North'): 'Germany'
}
   #,'node0_A1_Bayern','node1_A1_Bayern','node2_A1_Bayern',
   #'node3_A1_Bayern','node4_A1_Bayern','node5_A1_Bayern','node6_A1_Bayern',
   #'node7_A1_Bayern','node8_A1_Bayern','node9_A1_Bayern'):'Germany'

# plotting commodities/sites
plot_tuples = [
    # (2021, 'BB', 'electricity'),
    # (2021, 'BE', 'electricity'),
    # (2021, 'BW', 'electricity'),
    # (2021, 'BY', 'electricity'),
    # (2021, 'HB', 'electricity'),
    # (2021, 'HE', 'electricity'),
    # (2021, 'HH', 'electricity'),
    # (2021, 'MV', 'electricity'),
    # (2021, 'NI', 'electricity'),
    # (2021, 'NW', 'electricity'),
    # (2021, 'RP', 'electricity'),
    # (2021, 'SH', 'electricity'),
    # (2021, 'SL', 'electricity'),
    # (2021, 'SN', 'electricity'),
    # (2021, 'ST', 'electricity'),
    # (2021, 'TH', 'electricity'),
    # (2021, 'Baltic', 'electricity'),
    # (2021, 'North', 'electricity'),
    # (2021, ['BB', 'BE', 'BW', 'BY', 'HB', 'HE', 'HH', 'MV', 'NI', 'NW', 'RP', 'SH',
    #         'SL', 'SN', 'ST', 'TH', 'Baltic', 'North'], 'electricity')
]

# optional: define names for sites in plot_tuples
plot_sites_name = {
    # ('BB', 'BE', 'BW', 'BY', 'HB', 'HE', 'HH', 'MV', 'NI', 'NW', 'RP', 'SH',
    #   'SL', 'SN', 'ST', 'TH', 'Baltic', 'North'): 'Germany'
}

# plotting timesteps
plot_periods = {
    'all': timesteps[1:]
}

# add or change plot colors
# my_colors = {
#     'South': (230, 200, 200),
#     'Mid': (200, 230, 200),
#     'North': (200, 200, 230)}
# for country, color in my_colors.items():
#     urbs.COLORS[country] = color

# select scenarios to be run
scenarios = [
             urbs.scenario_base
            ]
#if __name__ == '__main__':
for scenario in scenarios:
    prob = urbs.run_scenario(input_path, solver, timesteps, scenario,
                             result_dir, dt, objective, microgrid_paths,
                             plot_tuples=plot_tuples,
                             plot_sites_name=plot_sites_name,
                             plot_periods=plot_periods,
                             report_tuples=report_tuples,
                             report_sites_name=report_sites_name,
                             noTypicalPeriods=noTypicalPeriods,
                             hoursPerPeriod=hoursPerPeriod)

