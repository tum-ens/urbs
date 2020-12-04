import os
import shutil
import urbs

# import sys
# import time as t
# import numpy as np
# import multiprocessing as mp
# from os import getpid
# import matplotlib.pyplot as plt
# from urbs.runfunctions import *

input_files = 'Bundesländer_Trans.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

microgrid_files = ['Microgrid_A.xlsx', 'Microgrid_B.xlsx']
microgrid_dir = 'Input/microgrid_types'
microgrid_paths = []
for i, microgrid_file in enumerate(microgrid_files):
    microgrid_paths.append(os.path.join(microgrid_dir, microgrid_file))

result_name = 'Trans-Dist'
result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

#microgrid_files = {
  # 'Microgrid_A': 'Microgrid_A.xlsx'
  # 'Microgrid_B': 'Microgrid_B.xlsx'
#    }


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
(offset, length) = (0, 10)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# detailed reporting commodity/sites
report_tuples = [
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
                      # ('Baden-Württemberg', 'Bavaria', 'Berlin',
                      # 'Brandenburg', 'Bremen', 'Hamburg', 'Hesse', 'Lower Saxony',
                      # 'Mecklenburg-Vorpommern', 'North Rhine-Westphalia',
                      # 'Rhineland-Palatinate', 'Saarland', 'Saxony', 'Saxony-Anhalt',
                      # 'Schleswig-Holstein',    'Thuringia', 'Offshore'): 'Germany'}
                    }

# plotting commodities/sites
plot_tuples = [
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
#if __name__ == '__main__': # todo - nachfragen: wo ist Name main definiert?
for scenario in scenarios:
    prob = urbs.run_scenario(input_path, solver, timesteps, scenario,
                             result_dir, dt, objective, microgrid_paths,
                             plot_tuples=plot_tuples,
                             plot_sites_name=plot_sites_name,
                             plot_periods=plot_periods,
                             report_tuples=report_tuples,
                             report_sites_name=report_sites_name)

