import os
import pyomo.environ
from pyomo.opt.base import SolverFactory
from datetime import datetime
from .model import *
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *
from .data import timeseries_number


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


def run_scenario(input_file, prob, solver, timesteps, scenario, result_dir, dt,
                 objective,
                 plot_tuples=None,  plot_sites_name=None, plot_periods=None,
                 report_tuples=None, report_sites_name=None):
    """ run an urbs model for given input, time steps and scenario

    Args:
        input_file: filename to an Excel spreadsheet for urbs.read_excel
        prob: urbs model instance initialized with base scenario if alternative
            scenario
        solver: name of the solver to be used
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

    # if alternative scenario: special scenario function treatment is necessary
    if str(sce).find("alternative") >= 0:
        # Only needed for scenario_new_timeseries, but handed to all functions:
        filename = ""
        # scenario_new_timeseries needs special treatment:
        # Add file extension to scenario name and create path to excel sheet
        if str(sce).find("scenario_new_timeseries") >= 0:
            sce = sce+str(timeseries_number.pop())
            filename = os.path.join("input", "{}.xlsx").format(sce)
        # model instance, undo scenario changes?, path to excel sheet
        prob = scenario(prob, False, filename)
        instance = prob
    else:
        # it is a normal scenario: load data and build new model instance
        data = read_excel(input_file)
        data = scenario(data)
        validate_input(data)
        instance = create_model(data, dt, timesteps)

    # create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(instance, tee=True)
    assert str(result.solver.termination_condition) == 'optimal'

    # save problem solution (and input data) to HDF5 file
    save(instance, os.path.join(result_dir, '{}.h5'.format(sce)))

    # write report to spreadsheet
    report(
        instance,
        os.path.join(result_dir, '{}.xlsx').format(sce),
        report_tuples=report_tuples,
        report_sites_name=report_sites_name)

    # result plots
    result_figures(
        instance,
        os.path.join(result_dir, '{}'.format(sce)),
        timesteps,
        plot_title_prefix=sce.replace('_', ' '),
        plot_tuples=plot_tuples,
        plot_sites_name=plot_sites_name,
        periods=plot_periods,
        figure_size=(24, 9))

    if str(sce).find("alternative") >= 0:
        # Undo all changes to model instance to retrieve base scenario model
        prob = scenario(prob, True, filename)
    if str(sce).find("scenario_base") >= 0:
        # use base scenario model instance for future alternative scenarios
        return instance
    return prob