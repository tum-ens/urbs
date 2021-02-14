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
from multiprocessing import freeze_support

input_files = 'mimo-example_internal.xlsx'  # for single year file name, for intertemporal folder name
#input_files = 'germany.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

result_name = 'Run'
result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

    # subproblem input files
sub_input_files = {
  # 'Bavaria': 'bavaria.xlsx'
    }
    
    
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
(offset, length) = (0, 10)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

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
#    ('South','Elec'),('North','Elec'),('Mid'),('Elec')
    ]

#clusters = [(('Schleswig-Holstein'),('Hamburg'),('Mecklenburg-Vorpommern'),('Offshore'),('Lower Saxony'),('Bremen'),('Saxony-Anhalt'),('Brandenburg'),('Berlin'),('North Rhine-Westphalia')),
#                (('Baden-Württemberg'),('Hesse'),('Bavaria'),('Rhineland-Palatinate'),('Saarland'),('Saxony'),('Thuringia'))]
#clusters = [[('Schleswig-Holstein')],[('Hamburg')],[('Mecklenburg-Vorpommern')],[('Offshore')],[('Lower Saxony')],[('Bremen')],[('Saxony-Anhalt')],[('Brandenburg')],[('Berlin')],[('North Rhine-Westphalia')],
#                [('Baden-Württemberg')],[('Hesse')],[('Bavaria')],[('Rhineland-Palatinate')],[('Saarland')],[('Saxony')],[('Thuringia')]]

clusters = [[('Mid'),('Mid_int')],[('South'),('North')]]
# optional: define names for plot_tuples
# plot_sites_name = {
    # ('Baden-Württemberg', 'Bavaria', 'Berlin', 'Brandenburg', 'Bremen',
     # 'Hamburg', 'Hesse', 'Lower Saxony', 'Mecklenburg-Vorpommern', 'North Rhine-Westphalia',
     # 'Rhineland-Palatinate', 'Saarland', 'Saxony', 'Saxony-Anhalt', 'Schleswig-Holstein',
     # 'Thuringia', 'Offshore'): 'Germany'}
# plot_sites_name = {
    # (, ,
     # '', '',
     # , , , 
     # ): 'Germany'}
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
    # ('Baden-Württemberg', 'CO2'),
    # ('Bavaria', 'CO2'),
    # ('Berlin', 'CO2'),
    # ('Brandenburg', 'CO2'),
    # ('Bremen', 'CO2'),
    # ('Hamburg', 'CO2'),
    # ('Hesse', 'CO2'),
    # ('Lower Saxony', 'CO2'),
    # ('Mecklenburg-Vorpommern', 'CO2'),
    # ('North Rhine-Westphalia', 'CO2'),
    # ('Rhineland-Palatinate', 'CO2'),
    # ('Saarland', 'CO2'),
    # ('Saxony', 'CO2'),
    # ('Saxony-Anhalt', 'CO2'),
    # ('Schleswig-Holstein', 'CO2'),
    # ('Thuringia', 'CO2'),
    # ('Offshore', 'CO2'),
    # (['Baden-Württemberg', 'Bavaria', 'Berlin', 'Brandenburg',
      # 'Bremen', 'Hamburg', 'Hesse', 'Lower Saxony', 'Mecklenburg-Vorpommern',
      # 'North Rhine-Westphalia', 'Rhineland-Palatinate', 'Saarland', 'Saxony',
      # 'Saxony-Anhalt', 'Schleswig-Holstein', 'Thuringia', 'Offshore'], 'CO2')
#        ('South','Elec'),('North','Elec'),('Mid'),('Elec')
    ]

# optional: define names for report_tuples
# report_sites_name = {('Baden-Württemberg', 'Bavaria', 'Berlin',
                      # 'Brandenburg', 'Bremen', 'Hamburg', 'Hesse', 'Lower Saxony',
                      # 'Mecklenburg-Vorpommern', 'North Rhine-Westphalia',
                      # 'Rhineland-Palatinate', 'Saarland', 'Saxony', 'Saxony-Anhalt',
                      # 'Schleswig-Holstein',    'Thuringia', 'Offshore'): 'Germany'}

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

# test scenarios
test_scenarios = [
    urbs.scenario_base
    #test_time_2,
    #test_time_3,
    #test_supim_1,
    #test_supim_2,
    #test_tra_var
    ]

if __name__ == '__main__':
    freeze_support()
    for scenario in test_scenarios:
        prob = urbs.run_regional(input_path, solver, sub_input_files, timesteps,
                                 scenario,result_dir,dt,objective, 
                                 plot_tuples=plot_tuples,
                                 plot_periods=plot_periods,
                                 report_tuples=report_tuples,
                                 clusters=clusters)
