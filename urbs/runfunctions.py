import os
import time

# import pyomo.environ
# from pyomo.opt.base import SolverFactory

from pyomo.environ import SolverFactory
import pyomo.environ as pyomo

from datetime import datetime, date
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *
from .features import *


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


def setup_solver(optim, logfile='solver.log'):
    """ """
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        optim.set_options("Crossover=0")
        optim.set_options("Method=2") # ohne method concurrent optimization
        optim.set_options("Threads=4")
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


def run_scenario(input_files, solver_name, timesteps, scenario, result_dir, dt,
                 objective, microgrid_files = None, plot_tuples=None,  plot_sites_name=None,
                 plot_periods=None, report_tuples=None,
                 report_sites_name=None,noTypicalPeriods=None, hoursPerPeriod=None):
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


    # read and modify microgrid data
    mode = identify_mode(data)
    if mode['transdist']:
        microgrid_data_initial =[]
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            microgrid_data_initial[i] = scenario(microgrid_data_initial[i])
            validate_input(microgrid_data_initial[i])
            validate_dc_objective(microgrid_data_initial[i], objective) #todo: braucht es das?
        # join microgrid data to model data
        data = create_transdist_data(data, microgrid_data_initial)
    elif mode['acpf']:
        add_reactive_transmission_lines(data)
        add_reactive_output_ratios(data)

    if mode['tsam']:
        data, timesteps, weighting_order = run_tsam(data, noTypicalPeriods, hoursPerPeriod)

    ## Excel Datei zum validieren der create_transdist_data todo: delete at the end
    # with pd.ExcelWriter(os.path.join(result_dir, '{}.xlsx').format(sce)) as writer:
    #     for i, sheet in enumerate(data):
    #         data[sheet].to_excel(writer, str(i))

    # create model
    tt = time.time()
    prob = create_model(data, dt, timesteps, objective, hoursPerPeriod, weighting_order)
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt,4))

    # write lp file
    prob.write('model.lp', io_options={'symbolic_solver_labels':True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(prob, tee=True,report_timing=True)
    assert str(result.solver.termination_condition) == 'optimal'

    # save problem solution (and input data) to HDF5 file
    # save(prob, os.path.join(result_dir, '{}.h5'.format(sce)))
    #save(prob, os.path.join('C:/Users/beneh/Documents/Dokumente/Beneharos_Dokumente/01_Uni/00_Master/4_Semester/Masterarbeit/3_Postprocessing/h5 analysis/case_Test_AC', '{}.h5'.format(sce)))

    # write report to spreadsheet #todo: wieder aktivieren wenn Problem in pyomoio gelöst
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
