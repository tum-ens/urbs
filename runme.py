import os
import pandas as pd
import pyomo.environ
import shutil
import urbs
from datetime import datetime
from pyomo.opt.base import SolverFactory
from urbs.data import timeseries_number


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
    elif optim.name == 'cplex':
        optim.set_options("log={}".format(logfile))
    else:
        print("Warning from setup_solver: no options set for solver "
              "'{}'!".format(optim.name))
    return optim


def run_scenario(prob, timesteps, scenario, result_dir, timeseries_number, dt,
                 objective, plot_tuples=None,  plot_sites_name=None,
                 plot_periods=None, report_tuples=None,
                 report_sites_name=None):
    """ run an urbs model for given input, time steps and scenario

    Args:
        prob: urbs model instance initialized with base scenario
        timesteps: a list of timesteps, e.g. range(0,8761)
        scenario: a scenario function that modifies the input data dict
        result_dir: directory name for result spreadsheet and plots
        dt: length of each time step (unit: hours)
        plot_tuples: (optional) list of plot tuples (c.f. urbs.result_figures)
        plot_sites_name: (optional) dict of names for sites in plot_tuples
        plot_periods: (optional) dict of plot periods(c.f. urbs.result_figures)
        report_tuples: (optional) list of (sit, com) tuples (c.f. urbs.report)
        report_sites_name: (optional) dict of names for sites in report_tuples

    Returns:
        the urbs model instance
    """

    # scenario name, read and modify data for scenario
    sce = scenario.__name__

    # Only needed for scenario_new_timeseries, but handed to all functions:
    filename = ""
    # scenario_new_timeseries needs special treatment:
    # Add file extension to scenario name and create path to excel sheet
    if str(sce).find("scenario_new_timeseries") >= 0:
        sce = sce+str(timeseries_number.pop())
        filename = os.path.join("input", "{}.xlsx").format(sce)
    # model instance, undo scenario changes?, path to excel sheet
    prob = scenario(prob, False, filename)

    # create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(prob, tee=True)
    assert str(result.solver.termination_condition) == 'optimal'

    # save problem solution (and input data) to HDF5 file
    urbs.save(prob, os.path.join(result_dir, '{}.h5'.format(sce)))

    # write report to spreadsheet
    urbs.report(
        prob,
        os.path.join(result_dir, '{}.xlsx').format(sce),
        report_tuples=report_tuples,
        report_sites_name=report_sites_name)

    # result plots
    urbs.result_figures(
        prob,
        os.path.join(result_dir, '{}'.format(sce)),
        timesteps,
        plot_title_prefix=sce.replace('_', ' '),
        plot_tuples=plot_tuples,
        plot_sites_name=plot_sites_name,
        periods=plot_periods,
        figure_size=(24, 9))
    prob = scenario(prob, True, filename)
    return prob


if __name__ == '__main__':
    input_file = 'mimo-example.xlsx'
    result_name = os.path.splitext(input_file)[0]  # cut away file extension
    result_dir = prepare_result_directory(result_name)  # name + time stamp

    # copy input file to result directory
    shutil.copyfile(input_file, os.path.join(result_dir, input_file))
    # copy runme.py to result directory
    shutil.copy(__file__, result_dir)

    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective

    # simulation timesteps
    (offset, length) = (3500, 168)  # time step selection
    timesteps = range(offset, offset+length+1)
    dt = 1  # length of each time step (unit: hours)

    # plotting commodities/sites
    plot_tuples = [
        ('North', 'Elec'),
        ('Mid', 'Elec'),
        ('South', 'Elec'),
        (['North', 'Mid', 'South'], 'Elec')]

    # optional: define names for sites in plot_tuples
    plot_sites_name = {('North', 'Mid', 'South'): 'All'}

    # detailed reporting commodity/sites
    report_tuples = [
        ('North', 'Elec'), ('Mid', 'Elec'), ('South', 'Elec'),
        ('North', 'CO2'), ('Mid', 'CO2'), ('South', 'CO2')]

    # optional: define names for sites in report_tuples
    report_sites_name = {'North': 'Greenland'}

    # plotting timesteps
    plot_periods = {'all': timesteps[1:]}

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
        urbs.scenario_all_together,
        urbs.scenario_new_timeseries(timeseries_number,
                                     "example_file_extension")
        ]

    # Read data from Excel Sheet and create model for use in scenarios
    data = urbs.read_excel(input_file)
    prob = urbs.create_model(data, dt, timesteps)

    for scenario in scenarios:
        prob = run_scenario(prob, timesteps, scenario, result_dir,
                            timeseries_number, dt, objective,
                            plot_tuples=plot_tuples,
                            plot_sites_name=plot_sites_name,
                            plot_periods=plot_periods,
                            report_tuples=report_tuples,
                            report_sites_name=report_sites_name)
