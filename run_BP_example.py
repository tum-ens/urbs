import os
import pandas as pd
import pyomo.environ
import shutil
import urbs
from datetime import datetime, date
from pyomo.opt.base import SolverFactory


input_file = 'Input'
result_name = 'Business_park'
# problem without Input folder
# result_name = os.path.splitext(input_file)[0]  # cut away file extension
result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

# copy input file to result directory
# shutil.copyfile(input_file, os.path.join(result_dir, input_file))
# copy runme.py to result directory
shutil.copy(__file__, result_dir)

# objective function
objective = 'cost' # set either 'cost' or 'CO2' as objective

# Choose Solver (cplex, glpk, gurobi, ...)
Solver = 'gurobi'

# simulation timesteps
(offset, length) = (3000, 168)  # time step selection
timesteps = range(offset, offset+length+1)
dt = 1  # length of each time step (unit: hours)

# plotting commodities/sites
plot_tuples = [
    (2020, 'Business park', 'Electricity'),
    (2020, 'Business park', 'Heat'),
    (2020, 'Business park', 'Cooling'),
    (2020, 'Business park', 'Intermediate low temperature'),
    (2030, 'Business park', 'Electricity'),
    (2030, 'Business park', 'Heat'),
    (2030, 'Business park', 'Cooling'),
    (2030, 'Business park', 'Intermediate low temperature'),
    (2040, 'Business park', 'Electricity'),
    (2040, 'Business park', 'Heat'),
    (2040, 'Business park', 'Cooling'),
    (2040, 'Business park', 'Intermediate low temperature'),
    (2020, 'City', 'Electricity'),
    (2020, 'City', 'Heat'),
    (2030, 'City', 'Electricity'),
    (2030, 'City', 'Heat'),
    (2040, 'City', 'Electricity'),
    (2040, 'City', 'Heat'),
    (2020, ['Business park', 'City'], 'Electricity'),
    (2020, ['Business park', 'City'], 'Heat'),
    (2030, ['Business park', 'City'], 'Electricity'),
    (2030, ['Business park', 'City'], 'Heat'),
    (2040, ['Business park', 'City'], 'Electricity'),
    (2040, ['Business park', 'City'], 'Heat')
    ]

# optional: define names for sites in plot_tuples
plot_sites_name = {('Business park', 'City'): 'Together'}

# detailed reporting commodity/sites
report_tuples = [
    (2020, 'Business park', 'Electricity'),
    (2020, 'Business park', 'Heat'),
    (2020, 'Business park', 'Cooling'),
    (2030, 'Business park', 'Electricity'),
    (2030, 'Business park', 'Heat'),
    (2030, 'Business park', 'Cooling'),
    (2040, 'Business park', 'Electricity'),
    (2040, 'Business park', 'Heat'),
    (2040, 'Business park', 'Cooling'),
    (2020, 'City', 'Electricity'),
    (2020, 'City', 'Heat'),
    (2030, 'City', 'Electricity'),
    (2030, 'City', 'Heat'),
    (2040, 'City', 'Electricity'),
    (2040, 'City', 'Heat'),
    (2020, ['Business park', 'City'], 'Electricity'),
    (2020, ['Business park', 'City'], 'Heat'),
    (2030, ['Business park', 'City'], 'Electricity'),
    (2030, ['Business park', 'City'], 'Heat'),
    (2040, ['Business park', 'City'], 'Electricity'),
    (2040, ['Business park', 'City'], 'Heat')
    ]

# optional: define names for sites in report_tuples
report_sites_name = {('Business park', 'City'): 'Together'}

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
    #urbs.scenario_stock_prices,
    #urbs.scenario_co2_limit,
    #urbs.scenario_co2_tax_mid,
    #urbs.scenario_no_dsm,
    #urbs.scenario_north_process_caps,
    #urbs.scenario_all_together
    ]

for scenario in scenarios:
    prob = urbs.run_scenario(input_files, solver, timesteps, scenario, 
                        result_dir, dt, objective, 
                        plot_tuples=plot_tuples,
                        plot_sites_name=plot_sites_name,
                        plot_periods=plot_periods,
                        report_tuples=report_tuples,
                        report_sites_name=report_sites_name)
