import os
import pyomo.environ
from pyomo.opt.base import SolverFactory
from datetime import datetime, date
from .model_nopt import create_model, capacity_rule
from .report_nopt import *
from .plot_nopt import *
from .input_nopt import *
from .validation_nopt import *
from .saveload_nopt import *

from .features_nopt import *
import math


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


    if isinstance(objective[0],tuple):
        objective_pro = objective[0][-1]
        objective_sites = list(objective[0][:-1])
    else:
        objective_pro = objective[0]
        objective_sites =[]
        site_dict=data['site'].to_dict()
        for key in site_dict['area']:
            objective_sites.append(key[1])

    validate_input(data)
    validate_dc_objective(data, objective_pro)

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)
    # For near optimal analysis (obj!=cost/co2) solve the problem first for cost then update objective function and solve for restricted cost

    if (objective_pro != 'cost' and objective_pro != 'CO2'):

        # create cost opt model
        prob = create_model(data, dt, timesteps, [('cost')])

        # solve cost model and read optimized cost
        optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
        optim = setup_solver(optim, logfile=log_filename)
        result_cost_opt = optim.solve(prob, tee=True)
        assert str(result_cost_opt.solver.termination_condition) == 'optimal'

        #if len(objective_sites) == 0:
            #objective_sites = prob.sit.value_list

        # store real objective in model because model.obj is still cost
        prob.cap_obj = objective_pro
        prob.cap_sites = objective_sites
        opt_cost_sum = 0
        for key in prob.costs.keys():
            opt_cost_sum += prob.costs[key].value
        prob.opt_cost_sum = opt_cost_sum

        cost_optimized_cap_pro = read_capacity(prob, 'Minimum Cost')
        prob.near_optimal_capacities = cost_optimized_cap_pro
        # Calculate minimum total cost
        prob.minimum_cost = read_costs(prob, 'Minimum Cost')

        # del objective component first to write real objective
        prob.del_component(prob.objective_function)

        def res_cost_restrict_rule(m):
            # assert cost_factor < 1.0, "slack value is not defined properly. Slack value must be smaller than 1.0"
            assert m.cost_factor >= 0, "slack value is not defined properly. Slack value must be a positive number."
            return (pyomo.summation(m.costs) == (1 + m.cost_factor) * m.opt_cost_sum)

        for slack in prob.cost_slack_list:
            prob.cost_factor = slack

            if prob.find_component('res_cost_restrict'):
                prob.del_component('res_cost_restrict')

            prob.res_cost_restrict = pyomo.Constraint(
                rule=res_cost_restrict_rule,
                doc='total costs <= Optimum cost *(1+e)')

            # Minimize
            prob.objective_function = pyomo.Objective(
                rule=capacity_rule,
                sense=pyomo.minimize,
                doc='minimize objective process capacity emissions')
            optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
            optim = setup_solver(optim, logfile=log_filename)
            result_min = optim.solve(prob, tee=True)
            assert str(result_min.solver.termination_condition) == 'optimal'
            # read minimized capacities from instance
            minimized_cap_pro = read_capacity(prob, 'Min' + '-' + str(slack))
            minimized_cap_costs = read_costs(prob, 'Min' + '-' + str(slack))
            # del minimization objective for maximization
            prob.del_component(prob.objective_function)
            # Maximize
            prob.objective_function = pyomo.Objective(
                rule=capacity_rule,
                sense=pyomo.maximize,
                doc='maximize objective process capacity emissions')
            # solve model and read results
            optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
            optim = setup_solver(optim, logfile=log_filename)
            result_max = optim.solve(prob, tee=True)
            assert str(result_max.solver.termination_condition) == 'optimal'
            # read maximized capacities from instance
            maximized_cap_pro = read_capacity(prob, 'Max' + '-' + str(slack))
            maximized_cap_costs = read_costs(prob, 'Max' + '-' + str(slack))
            # store optimized capacities in a data frame

            prob.near_optimal_capacities = prob.near_optimal_capacities.join(maximized_cap_pro, how='outer')
            prob.near_optimal_capacities = prob.near_optimal_capacities.join(minimized_cap_pro, how='outer')
            prob.minimum_cost = prob.minimum_cost.join(maximized_cap_costs, how='outer')
            prob.minimum_cost = prob.minimum_cost.join(minimized_cap_costs, how='outer')
    else:
        prob = create_model(data, dt, timesteps, objective)
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
        os.path.join(result_dir, '{}-{}-{}-{}.xlsx').format(prob.stf_list, objective_pro, objective_sites, sce),
        report_tuples=report_tuples,
        report_sites_name=report_sites_name)

    # result plots
    result_figures(
        prob,
        os.path.join(result_dir, '{}-{}-{}-{}'.format(prob.stf_list, objective_pro, objective_sites, sce)),
        timesteps,
        plot_title_prefix=sce.replace('_', ' '),
        plot_tuples=plot_tuples,
        plot_sites_name=plot_sites_name,
        periods=plot_periods,
        figure_size=(24, 9))

    return prob