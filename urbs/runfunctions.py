import pyomo.environ
from pyomo.opt.base import SolverFactory
from datetime import datetime, date
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *
from . import progress


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

def run_scenario_config(config, Solver, timesteps, result_dir, dt,
                 objective, generate_report=None, generate_h5=False):
    """ run an urbs model for given input, time steps and scenario

    Args:
        - input_files: filenames of input Excel spreadsheets
        - Solver: the user specified solver
        - timesteps: a list of timesteps, e.g. range(0,8761)
        - result_dir: directory name for result spreadsheet and plots
        - dt: length of each time step (unit: hours)
        - objective: objective function chosen (either "cost" or "CO2")
        - report: None generate nothing, "summary" generate xlsx report, "full" generate xlsx report with timeseries

    Returns:
        the urbs model instance
    """

    # sets a modeled year for non-intertemporal problems
    # (necessary for consitency)
    year = date.today().year

    current_step = progress.STEP_BUILDING_MODEL
    try:
        progress.set_step_in_progress(result_dir, current_step)

        # scenario name, read and modify data for scenario
        data = read_config(config, year)
        validate_input(data)
        validate_dc_objective(data, objective)

        # create model
        prob = create_model(data, dt, timesteps, objective)
        progress.complete_step(result_dir, current_step)

        # refresh time stamp string and create filename for logfile
        log_filename = os.path.join(result_dir, 'result.log')

        # solve model and read results
        current_step = progress.STEP_OPTIMIZING
        optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
        optim = setup_solver(optim, logfile=log_filename)
        time_setup_finished = datetime.now()
        progress.advance_to_step(result_dir, current_step)
        result = optim.solve(prob, tee=True)
        time_solve_finished = datetime.now()
        progress.complete_step(result_dir, current_step)

        # When the solver does not return an optimal solution (e.g. infeasible
        # or unbounded), the model variables stay uninitialized. Reporting or
        # saving would try to evaluate those variables and raise, so stop here
        # and let the caller surface the termination condition.
        termination = str(result.solver.termination_condition)
        if termination != 'optimal':
            return (
                result.solver.termination_condition,
                prob,
                time_setup_finished,
                time_solve_finished,
            )

        if generate_report is not None:
            current_step = progress.STEP_SAVING_XLSX
            progress.advance_to_step(result_dir, current_step)
            run_config = config.get('run_config') or {}
            commodity_types = run_config.get('timeseries_commodity_types')
            ts_tuples = (
                report_tuples(config, year, commodity_types)
                if generate_report == "full"
                else []
            )
            print(
                'Excel timeseries types:',
                commodity_types,
                'tuples:',
                ts_tuples,
            )
            report(
                prob,
                os.path.join(result_dir, 'result.xlsx'),
                report_tuples=ts_tuples,
            )
            progress.complete_step(result_dir, current_step)

        if generate_h5:
            current_step = progress.STEP_SAVING_H5
            progress.advance_to_step(result_dir, current_step)
            save(prob, os.path.join(result_dir, 'result.h5'))
            progress.complete_step(result_dir, current_step)

        return (
            result.solver.termination_condition,
            prob,
            time_setup_finished,
            time_solve_finished,
        )
    except Exception as exc:
        progress.fail_step(result_dir, current_step, str(exc))
        raise


def run_scenario(input_files, Solver, timesteps, scenario, result_dir, dt,
                 objective, plot_tuples=None, plot_sites_name=None,
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
    optim = setup_solver(optim, logfile=log_filename)
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
