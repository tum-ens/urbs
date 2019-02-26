import os
import time
import pandas as pd
import pyomo.environ
import shutil
import urbs
from datetime import datetime, date
from pyomo.opt.base import SolverFactory


input_file = 'Input'
result_name = 'Mimo-ex'
# problem without Input folder
# result_name = os.path.splitext(input_file)[0]  # cut away file extension
result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

# copy input file to result directory
# shutil.copyfile(input_file, os.path.join(result_dir, input_file))
# copy runme.py to result directory
shutil.copy(__file__, result_dir)

# set modeled year (default: this year)
year = date.today().year

# objective function
objective = 'cost' # set either 'cost' or 'CO2' as objective

# Choose Solver (cplex, glpk, gurobi, ...)
Solver = 'glpk'

# simulation timesteps
(offset, length) = (3500, 168)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# plotting commodities/sites
plot_tuples = [
    (2019, 'North', 'Elec'),
    (2019, 'Mid', 'Elec'),
    (2019, 'South', 'Elec'),
    (2019, ['North', 'Mid', 'South'], 'Elec'),
    (2024, 'North', 'Elec'),
    (2024, 'Mid', 'Elec'),
    (2024, 'South', 'Elec'),
    (2024, ['North', 'Mid', 'South'], 'Elec'),
    (2029, 'North', 'Elec'),
    (2029, 'Mid', 'Elec'),
    (2029, 'South', 'Elec'),
    (2029, ['North', 'Mid', 'South'], 'Elec'),
    (2034, 'North', 'Elec'),
    (2034, 'Mid', 'Elec'),
    (2034, 'South', 'Elec'),
    (2034, ['North', 'Mid', 'South'], 'Elec'),    
    ]

# optional: define names for sites in plot_tuples
plot_sites_name = {('North', 'Mid', 'South'): 'All'}

# detailed reporting commodity/sites
report_tuples = [
    (2019, 'North', 'Elec'),
    (2019, 'Mid', 'Elec'),
    (2019, 'South', 'Elec'),
    (2019, ['North', 'Mid', 'South'], 'Elec'),
    (2024, 'North', 'Elec'),
    (2024, 'Mid', 'Elec'),
    (2024, 'South', 'Elec'),
    (2024, ['North', 'Mid', 'South'], 'Elec'),
    (2029, 'North', 'Elec'),
    (2029, 'Mid', 'Elec'),
    (2029, 'South', 'Elec'),
    (2029, ['North', 'Mid', 'South'], 'Elec'),
    (2034, 'North', 'Elec'),
    (2034, 'Mid', 'Elec'),
    (2034, 'South', 'Elec'),
    (2034, ['North', 'Mid', 'South'], 'Elec'),    
    ]

# optional: define names for sites in report_tuples
report_sites_name = {'North': 'Greenland'}

# # mimo-example
# # plotting commodities/sites
# plot_tuples = [
#     (year, 'North', 'Elec'),
#     (year, 'Mid', 'Elec'),
#     (year, 'South', 'Elec'),
#     (year, ['North', 'Mid', 'South'], 'Elec')]

# # optional: define names for sites in plot_tuples
# plot_sites_name = {('North', 'Mid', 'South'): 'All'}

# # detailed reporting commodity/sites
# report_tuples = [
#     (year,'North', 'Elec'), (year,'Mid', 'Elec'), (year,'South', 'Elec'),
#     (year,'North', 'CO2'), (year,'Mid', 'CO2'), (year,'South', 'CO2')]

# # optional: define names for sites in report_tuples
# report_sites_name = {'North': 'Greenland'}


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
    urbs.scenario_base,
    urbs.scenario_stock_prices,
    urbs.scenario_co2_limit,
    urbs.scenario_co2_tax_mid,
    urbs.scenario_no_dsm,
    urbs.scenario_north_process_caps,
    urbs.scenario_all_together
    ]

# create timelog
timelog = open(os.path.join(result_dir, "timelog.txt"), "a")
timelog.write("Total\tread\tmodel\tsolve\tplot\r\n")
timelog.close()

for scenario in scenarios:
    prob = urbs.run_scenario(input_file, year, Solver, timesteps, scenario, 
                        result_dir, dt, objective, 
                        plot_tuples=plot_tuples,
                        plot_sites_name=plot_sites_name,
                        plot_periods=plot_periods,
                        report_tuples=report_tuples,
                        report_sites_name=report_sites_name)

# open timelog file
os.startfile(os.path.join(result_dir, "timelog.txt"))
