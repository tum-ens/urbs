import os
import pandas as pd
import pyomo.environ
import shutil
import urbs
from datetime import datetime
from pyomo.opt.base import SolverFactory


# SCENARIOS
def scenario_base(data):
    # do nothing
    return data


# def scenario_stock_prices(data):
    #change stock commodity prices
    # co = data['commodity']
    # stock_commodities_only = (co.index.get_level_values('Type') == 'Stock')
    # co.loc[stock_commodities_only, 'price'] *= 1.5
    # return data


def scenario_co2_limit_high(data):
   #change global CO2 limit
    hacks = data['hacks']
    hacks.loc['Global CO2 limit', 'Value'] = 30000
    return data

def scenario_co2_limit_low(data):
   #change global CO2 limit
    hacks = data['hacks']
    hacks.loc['Global CO2 limit', 'Value'] = 25000
    return data

def scenario_co2_price_low(data):
   #change CO2 price
    co = data['commodity']
    co.loc[('Campus', 'CO2', 'Env'), 'price'] = 5
    return data
	
def scenario_co2_price_high(data):
   #change CO2 price
    co = data['commodity']
    co.loc[('Campus', 'CO2', 'Env'), 'price'] = 150
    return data
	
def scenario_co2_price_veryhigh(data):
   #change CO2 price
    co = data['commodity']
    co.loc[('Campus', 'CO2', 'Env'), 'price'] = 1000
    return data


# def scenario_north_process_caps(data):
    #change maximum installable capacity
    # pro = data['process']
    # pro.loc[('North', 'Hydro plant'), 'cap-up'] *= 0.5
    # pro.loc[('North', 'Biomass plant'), 'cap-up'] *= 0.25
    # return data


# def scenario_no_dsm(data):
    #empty the DSM dataframe completely
    # data['dsm'] = pd.DataFrame()
    # return data


# def scenario_all_together(data):
    #combine all other scenarios
    # data = scenario_stock_prices(data)
    # data = scenario_co2_limit(data)
    # data = scenario_north_process_caps(data)
    # return data


def prepare_result_directory(result_name):
    """ create a time stamped directory within the result folder """
    # timestamp for result directory
    now = datetime.now().strftime('%Y%m%dT%H%M')

    # create result directory if not existent
    result_dir = os.path.join('result', '{}-{}'.format(result_name, now))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    return result_dir


def setup_solver(optim, logfile='solver.log'):
    """ """
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        # optim.set_options("timelimit=7200")  # seconds
        # optim.set_options("mipgap=5e-4")  # default = 1e-4
    elif optim.name == 'glpk':
        # reference with list of options
        # execute 'glpsol --help'
        optim.set_options("log={}".format(logfile))
        # optim.set_options("tmlim=7200")  # seconds
        # optim.set_options("mipgap=.0005")
    else:
        print("Warning from setup_solver: no options set for solver "
              "'{}'!".format(optim.name))
    return optim


def run_scenario(input_file, timesteps, scenario, result_dir, plot_periods={}):
    """ run an urbs model for given input, time steps and scenario

    Args:
        input_file: filename to an Excel spreadsheet for urbs.read_excel
        timesteps: a list of timesteps, e.g. range(0,8761)
        scenario: a scenario function that modifies the input data dict
        result_dir: directory name for result spreadsheet and plots

    Returns:
        the urbs model instance
    """

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = urbs.read_excel(input_file)
    data = scenario(data)

    # create model
    prob = urbs.create_model(data, timesteps)

    # refresh time stamp string and create filename for logfile
    now = prob.created
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory('gurobi')  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(prob, tee=True)

    # copy input file to result directory
    shutil.copyfile(input_file, os.path.join(result_dir, input_file))

    # write report to spreadsheet
    urbs.report(
        prob,
        os.path.join(result_dir, '{}.xlsx').format(sce),
        prob.com_demand | prob.com_env | prob.com_stock, ['Campus'])

    urbs.result_figures(
        prob,
        os.path.join(result_dir, '{}'.format(sce)),
        plot_title_prefix=sce.replace('_', ' ').title(),
        periods=plot_periods)
    return prob

if __name__ == '__main__':
    input_file = '1Node.xlsx'
    result_name = os.path.splitext(input_file)[0]  # cut away file extension
    result_dir = prepare_result_directory(result_name)  # name + time stamp

    # simulation timesteps
    (offset, length) = (2000, 1*24)  # time step selection
    timesteps = range(offset, offset+length+1)

    # plotting timesteps
    periods = {
        #'spr': range(1000, 1000+24*7),
        #'sum': range(3000, 3000+24*7),
        #'aut': range(2000, 5000+24*7),
        #'win': range(7000, 7000+24*7),
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
        scenario_co2_limit_high]

    for scenario in scenarios:
        prob = run_scenario(input_file, timesteps, scenario,
                            result_dir, plot_periods=periods)