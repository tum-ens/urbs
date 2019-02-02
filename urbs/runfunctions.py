import os
import pyomo.environ
import time
from pyomo.opt.base import SolverFactory
from datetime import datetime
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *


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


def run_scenario(input_files, year, Solver, timesteps, scenario, result_dir, 
                 dt, objective, plot_tuples=None,  plot_sites_name=None,
                 plot_periods=None, report_tuples=None,
                 report_sites_name=None):
    """ run an urbs model for given input, time steps and scenario

    Args:
        input_file: filename to an Excel spreadsheet for urbs.read_excel
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

    # start time measurement
    t_start = time.time()

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = read_input(input_files,year)
    data = scenario(data)
    validate_input(data)

    # measure time to read file
    t_read = time.time() - t_start
    print("Time to read file: %.2f sec" % t_read)

    t = time.time()
    # create model
    prob = create_model(data, dt, timesteps, objective)
    # prob.write('model.lp', io_options={'symbolic_solver_labels':True})

    # measure time to create model
    t_model = time.time() - t
    print("Time to create model: %.2f sec" % t_model)

    # refresh time stamp string and create filename for logfile
    # now = prob.created
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    t = time.time()

    # solve model and read results
    optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(prob, tee=True)
    assert str(result.solver.termination_condition) == 'optimal'

    # measure time to solve
    t_solve = time.time() - t
    print("Time to solve model: %.2f sec" % t_solve)

    t = time.time()

    # save problem solution (and input data) to HDF5 file
    save(prob, os.path.join(result_dir, '{}.h5'.format(sce)))

    # # measure time to save solution
    # save_time = time.time() - t
    # print("Time to save solution in HDF5 file: %.2f sec" % save_time)

    # t = time.time()

    # write report to spreadsheet
    report(
        prob,
        os.path.join(result_dir, '{}.xlsx').format(sce),
        report_tuples=report_tuples,
        report_sites_name=report_sites_name)

    # result plots
    result_figures(
        prob,
        os.path.join(result_dir, '{}'.format(sce)),
        timesteps,
        plot_title_prefix=sce.replace('_', ' '),
        plot_tuples=plot_tuples,
        plot_sites_name=plot_sites_name,
        periods=plot_periods,
        figure_size=(24, 9))

    t_repplot = time.time() - t
    print("Time to report and plot: %.2f sec" % t_repplot)

    # measure time to run scenario
    t_sce = time.time() - t_start
    print("Time to run scenario: %.2f sec" % t_sce)

    # write time measurements into file "timelog.txt" in result directory
    timelog = open(os.path.join(result_dir, "timelog.txt"), "a")
    timelog.write("%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s\n"
                  % (t_sce, t_read, t_model, t_solve, t_repplot, sce))

    return prob
