import os
import pyomo.environ
from pyomo.opt.base import SolverFactory
from pyomo.contrib.appsi.solvers import Highs, Gurobi, Cplex
from datetime import datetime, date
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *


def prepare_result_directory(result_name):
    """ create a time stamped directory within the result folder.

    Args:
        result_name: user specified result name

    Returns:
        a subfolder in the result folder

    """
    # timestamp for result directory
    now = datetime.now().strftime('%Y%m%dT%H%M')

    # create result directory if not existent
    result_dir = os.path.join('result', '{}-{}'.format(result_name, now))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    return result_dir


def setup_solver(optim, logfile='solver.log', recommendations=True, precision='default'):
    """ Setup options for the chosen solver with parameter value recommendations for ENS models using gurobi.
        This can be used as a first orientation to improve performance and feasibility of the optimization.
        However, the right settings can vary depending on the problem.

    Args:
        - optim: default pyomo object to perform optimization
        - logfile: logfile name
        - precision: decision on predefined decision levels based on ENS modeling experiences
                    (optimal settings might vary for individual problems)

    Returns:
        specified pyomo object to perform optimization

    """
    if optim.name == 'gurobi':
        # reference with list of option names: https://www.gurobi.com/documentation/current/refman/parameters.html
        optim.set_options("logfile={}".format(logfile))
        if recommendations == True:
            optim.set_options("ConcurrentMIP=4") # good for MIP problems by parallelization of multiple solves with different settings (not deterministic!)
            optim.set_options("Threads=8") # number of kernels (kernel>8: performance growth turns logarithmic)
            optim.set_options("Method=2") # 2: barrier method - most performant for large models
            optim.set_options("Crossover=0") # crossover=0: deactivate simplex step to push interior solution from barrier to exact optimal point with no tolerance
            # optim.set_options("NumericFocus=3") # try values only if error "numerical trouble encountered"
            # optim.set_options("timelimit=7200") # in seconds if timelimit is required - suboptimal output
            # optim.set_options("presolve = 2") # 1:conservative, 2:agressive, 0: off, -1: automatic(default)
            if precision == 'default':
                optim.set_options("BarConvTol=1e-4") # Barrier convergence tolerance
                optim.set_options("FeasibilityTol=1e-4") # Primal feasibility tolerance
                optim.set_options("OptimalityTol=1e-4") # Dual feasibility tolerance
                optim.set_options("mipgap=1e-2") # Relative MIP optimality gap
            if precision == 'high':
                optim.set_options("BarConvTol=1e-10") # Barrier convergence tolerance
                optim.set_options("FeasibilityTol=1e-9") # Primal feasibility tolerance
                optim.set_options("OptimalityTol=1e-9") # Dual feasibility tolerance
                optim.set_options("mipgap=1e-4") # Relative MIP optimality gap
    elif optim.name == 'glpk': # execute 'glpsol --help' for reference with list of options
        optim.set_options("log={}".format(logfile))
    elif optim.name == 'cplex':
        optim.set_options("log={}".format(logfile))
    else:
        print("Warning from setup_solver: no options set for solver '{optim.name}'!")
    return optim


def run_scenario(input_files, Solver, timesteps, scenario, result_dir, dt,
                 objective, plot_tuples=None,  plot_sites_name=None,
                 plot_periods=None, report_tuples=None,
                 report_sites_name=None):
    """ run an urbs model for given input, time steps and scenario

    Args:
        - input_files: filenames of input Excel spreadsheets
        - Solver: the user specified solver
        - timesteps: a list of timesteps, e.g. range(0,8761)
        - scenario: a scenario function that modifies the input data dict
        - result_dir: directory name for result spreadsheet and plots
        - dt: length of each time step (unit: hours)
        - objective: objective function chosen (either "cost" or "CO2")
        - plot_tuples: (optional) list of plot tuples (c.f. urbs.result_figures)
        - plot_sites_name: (optional) dict of names for sites in plot_tuples
        - plot_periods: (optional) dict of plot periods
          (c.f. urbs.result_figures)
        - report_tuples: (optional) list of (sit, com) tuples
          (c.f. urbs.report)
        - report_sites_name: (optional) dict of names for sites in
          report_tuples

    Returns:
        the urbs model instance
    """

    # sets a modeled year for non-intertemporal problems
    # (necessary for consitency)
    year = date.today().year

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = read_input(input_files, year)
    data = scenario(data)
    validate_input(data)
    validate_dc_objective(data, objective)

    # create model
    prob = create_model(data, dt, timesteps, objective)
    # prob_filename = os.path.join(result_dir, 'model.lp')
    # prob.write(prob_filename, io_options={'symbolic_solver_labels':True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
    if Solver != 'appsi_highs':
        optim = setup_solver(optim, logfile=log_filename, recommendations=True)
    result = optim.solve(prob, tee=True)
    assert str(result.solver.termination_condition) == 'optimal'

    # save problem solution (and input data) to HDF5 file
    save(prob, os.path.join(result_dir, '{}.h5'.format(sce)))

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

    return prob
