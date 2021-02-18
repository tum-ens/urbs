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

input_files = 'Bundesländer_Trans.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

microgrid_files = ['Microgrid_A_Dorf.xlsx', 'Microgrid_B_Dorf.xlsx']
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
(offset, length) = (0,120)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# detailed reporting commodity/sites
report_tuples = [
     (2021, 'Bayern', 'Elec'),
     (2021, 'Hessen', 'Elec'),
     (2021, 'node0_A1_Bayern', 'Elec'),
     (2021, 'node1_A1_Bayern', 'Elec'),
     (2021, 'node2_A1_Bayern', 'Elec'),
     (2021, 'node3_A1_Bayern', 'Elec'),
     (2021, 'node4_A1_Bayern', 'Elec'),
     (2021, 'node5_A1_Bayern', 'Elec'),
     (2021, 'node6_A1_Bayern', 'Elec'),
     (2021, 'node7_A1_Bayern', 'Elec'),
     (2021, 'node8_A1_Bayern', 'Elec'),
     (2021, 'node9_A1_Bayern', 'Elec'),
    (2021, 'node0_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node1_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node2_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node3_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node4_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node5_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node6_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node7_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node8_A1_Bayern', 'Elec-Reactive'),
    (2021, 'node9_A1_Bayern', 'Elec-Reactive')
    # ('Baden-Württemberg', 'Elec'),
    # ('Bavaria', 'Elec'),
    # ('Berlin', 'Elec'),
    # ('Brandenburg', 'Elec'),
    # ('Bremen', 'Elec'),
    # ('Hamburg', 'Elec'),
    # ('Hesse', 'Elec'),
    # ('Lower Saxony', 'Elec'),
    # ('Mecklenburg-Vorpommern', 'Elec'),
    # ('North Rhine-Westphalia', 'Elec'),
    # ('Rhineland-Palatinate', 'Elec'),
    # ('Saarland', 'Elec'),
    # ('Saxony', 'Elec'),
    # ('Saxony-Anhalt', 'Elec'),
    # ('Schleswig-Holstein', 'Elec'),
    # ('Thuringia', 'Elec'),
    # ('Offshore', 'Elec'),
    # (['Baden-Württemberg', 'Bavaria', 'Berlin', 'Brandenburg',
    # 'Bremen', 'Hamburg', 'Hesse', 'Lower Saxony', 'Mecklenburg-Vorpommern',
    # 'North Rhine-Westphalia', 'Rhineland-Palatinate', 'Saarland', 'Saxony',
    # 'Saxony-Anhalt', 'Schleswig-Holstein', 'Thuringia', 'Offshore'], 'Elec'),
    ]

# optional: define names for sites in report_tuples
report_sites_name = {
  ('Bayern','Hessen','node0_A1_Bayern','node1_A1_Bayern','node2_A1_Bayern',
   'node3_A1_Bayern','node4_A1_Bayern','node5_A1_Bayern','node6_A1_Bayern',
   'node7_A1_Bayern','node8_A1_Bayern','node9_A1_Bayern'):'Germany'
  # ('Baden-Württemberg', 'Bavaria', 'Berlin',
  # 'Brandenburg', 'Bremen', 'Hamburg', 'Hesse', 'Lower Saxony',
  # 'Mecklenburg-Vorpommern', 'North Rhine-Westphalia',
  # 'Rhineland-Palatinate', 'Saarland', 'Saxony', 'Saxony-Anhalt',
  # 'Schleswig-Holstein',    'Thuringia', 'Offshore'): 'Germany'}
  }

# plotting commodities/sites
plot_tuples = [
    # (2021, 'Bayern', 'Elec'),
    # (2021, 'Hessen', 'Elec'),
    # (2021, ['Bayern', 'Hessen'], 'Elec')
    # ('Baden-Württemberg', 'Elec'),
    # ('Bavaria', 'Elec'),
    # ('Berlin', 'Elec'),
    # ('Brandenburg', 'Elec'),
    # ('Bremen', 'Elec'),
    # ('Hamburg', 'Elec'),
    # ('Hesse', 'Elec'),
    # ('Lower Saxony', 'Elec'),
    # ('Mecklenburg-Vorpommern', 'Elec'),
    # ('North Rhine-Westphalia', 'Elec'),
    # ('Rhineland-Palatinate', 'Elec'),
    # ('Saarland', 'Elec'),
    # ('Saxony', 'Elec'),
    # ('Saxony-Anhalt', 'Elec'),
    # ('Schleswig-Holstein', 'Elec'),
    # ('Thuringia', 'Elec'),
    #(['Baden-Württemberg', 'Bavaria', 'Berlin', 'Brandenburg',
    # 'Bremen', 'Hamburg', 'Hesse', 'Lower Saxony', 'Mecklenburg-Vorpommern',
    #  'North Rhine-Westphalia', 'Rhineland-Palatinate', 'Saarland', 'Saxony',
    #  'Saxony-Anhalt', 'Schleswig-Holstein', 'Thuringia', 'Offshore'], 'Elec')
    # ('South','Elec'),('North','Elec'),('Mid'),('Elec')
    ]

# optional: define names for sites in plot_tuples
plot_sites_name = {
     # ('Bayern','Hessen'): 'Germany'
     # ('Baden-Württemberg', 'Bavaria', 'Berlin', 'Brandenburg', 'Bremen',
     # 'Hamburg', 'Hesse', 'Lower Saxony', 'Mecklenburg-Vorpommern', 'North Rhine-Westphalia',
     # 'Rhineland-Palatinate', 'Saarland', 'Saxony', 'Saxony-Anhalt', 'Schleswig-Holstein',
     # 'Thuringia', 'Offshore'): 'Germany'
     }

# plotting timesteps
plot_periods = {
    'all': timesteps[1:]
}

# add or change plot colors
my_colors = {
    'South': (230, 200, 200),
    'Mid': (200, 230, 200),
    'North': (200, 200, 230)}
for country, color in my_colors.items():
    urbs.COLORS[country] = color

# select scenarios to be run
scenarios = [
             urbs.scenario_base#,
             #urbs.scenario_co2_limit,
            ]
#if __name__ == '__main__':
for scenario in scenarios:
    prob = urbs.run_scenario(input_path, solver, timesteps, scenario,
                             result_dir, dt, objective, microgrid_paths,
                             plot_tuples=plot_tuples,
                             plot_sites_name=plot_sites_name,
                             plot_periods=plot_periods,
                             report_tuples=report_tuples,
                             report_sites_name=report_sites_name)

