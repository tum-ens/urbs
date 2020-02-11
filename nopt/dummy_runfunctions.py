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


def run_objective(objective_pro, objective_sites, prob):
    return None


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

    for k, item in enumerate(objective):

        if isinstance(objective[k], tuple):
            objective_pro = objective[k][-1]
            objective_sites = list(objective[k][:-1])
        else:
            objective_pro = objective[k]
            objective_sites = []
            site_dict = data['site'].to_dict()
            for key in site_dict['area']:
                objective_sites.append(key[1])

        # validate_input(data)
        # validate_dc_objective(data, objective_pro)

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

            # store real objective in model because model.obj is still cost
            prob.cap_obj = objective_pro
            prob.cap_sites = objective_sites

            # Minimized costs
            opt_cost_sum = 0
            for key in prob.costs.keys():
                opt_cost_sum += prob.costs[key].value
            prob.opt_cost_sum = opt_cost_sum

            cost_optimized_cap_pro = read_capacity(prob, 'Minimum Cost')
            prob.near_optimal_capacities = cost_optimized_cap_pro
            # plot_tuple_values
            prob.plot_tuple = (prob.stf_list, ('cost', 'minimize'))
            # Record minimum costs for reporting
            prob.minimum_cost = read_costs(prob, 'Minimum Cost')

            # del objective_function  component to write real objective
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
            plot_nopt(prob, os.path.join(result_dir, 'nopt'))
        else:
            prob = create_model(data, dt, timesteps, objective)
            # solve model and read results
            optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
            optim = setup_solver(optim, logfile=log_filename)
            result = optim.solve(prob, tee=True)
            assert str(result.solver.termination_condition) == 'optimal'
            # result plots
            result_figures(
                prob,
                os.path.join(result_dir,
                             '{} {} {} {}'.format(str(prob.stf_list).strip("[]").replace("'", ""), objective_pro,
                                                  str(objective_sites).strip("[]").replace("'", ""), sce)),
                timesteps,
                plot_title_prefix=sce.replace('_', ' '),
                plot_tuples=plot_tuples,
                plot_sites_name=plot_sites_name,
                periods=plot_periods,
                figure_size=(24, 9))

        # save problem solution (and input data) to HDF5 file
        save(prob, os.path.join(result_dir, '{}.h5'.format(sce)))

        # write report to spreadsheet
        report(
            prob,
            os.path.join(result_dir, '{}-{}-{}-{}.xlsx').format(str(prob.stf_list).strip("[]").replace("'", ""),
                                                                objective_pro,
                                                                str(objective_sites).strip("[]").replace("'", ""), sce),
            report_tuples=report_tuples,
            report_sites_name=report_sites_name)

    return prob

def plot_nopt(prob, figure_basename,figure_size=(16, 12),extensions=None):
    """Plot a stacked timeseries of commodity balance and storage.

       Creates a stackplot of the energy balance of a given commodity, together
       with stored energy in a second subplot.

       Args:
           - prob: urbs model instance
           - figure_size: optional (width, height) tuple in inch; default: (16, 12)

       Returns:
           fig: figure handle
       """
    import matplotlib.pyplot as plt
    import matplotlib as mpl


    #prob.near_optimal_capacities.index.names
    #Out[4]: FrozenList(['Objective_Process', 'Objective_Sites', 'Stf', 'Site'])
    #objective process  prob.cap_obj
    #objectivesites prob.cap_sites
    #site list prob.sit.value_list

    slack_array=[]
    cap_array_min=[]
    cap_array_max=[]

    slack_array.append(0)
    cap_array_min.append(prob.near_optimal_capacities.sum(level=['Objective_Process', 'Objective_Sites', 'Stf']).loc[prob.cap_obj, str(prob.cap_sites), 2020]['Minimum Cost'])
    cap_array_max.append(prob.near_optimal_capacities.sum(level=['Objective_Process', 'Objective_Sites', 'Stf']).loc[
                             prob.cap_obj, str(prob.cap_sites), 2020]['Minimum Cost'])
    for slack in prob.cost_slack_list:
        try:
            cap_array_max.append(
                prob.near_optimal_capacities.sum(level=['Objective_Process', 'Objective_Sites', 'Stf']).loc[
                    prob.cap_obj, str(prob.cap_sites), 2020]['Max-{}'.format(slack)])
            slack_array.append(slack)
        except:
            pass
        try:
            cap_array_min.append(prob.near_optimal_capacities.sum(level=['Objective_Process', 'Objective_Sites', 'Stf']).loc[prob.cap_obj, str(prob.cap_sites), 2020]['Min-{}'.format(slack)])
            if not slack in slack_array:
                slack_array.append(slack)
        except:
            pass

    slack_array=np.array(slack_array)
    slack_array=slack_array*100
    cap_array_min = np.array(cap_array_min)
    cap_array_max = np.array(cap_array_max)

    # FIGURE
    fig = plt.figure(figsize=figure_size)
    all_axes = []

    gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[2, 1], hspace=0.05)


    ax0 = plt.subplot(gs[0])

    all_axes.append(ax0)

    ax0.plot(slack_array, cap_array_max, linewidth=3,marker='o', markerfacecolor= to_color(prob.cap_obj+'marker'), color=to_color(prob.cap_obj),label=prob.cap_obj)
    ax0.plot(slack_array, cap_array_min, linewidth=3,marker='o', markerfacecolor= to_color(prob.cap_obj+'marker'),
             color=to_color(prob.cap_obj))


    ax0.set_title('Maximum and Minimum {} Capacities for Increased Cost'.format(prob.cap_obj))
    ax0.set_xlabel('{} ({})'.format('Increase in cost', '%'))
    ax0.set_ylabel('{} Process Capacity ({})'.format(prob.cap_obj, 'MW'))
    ax0.grid(b=0, linestyle='-', linewidth=0.5)
    ax0.legend()
    # if no custom title prefix is specified, use the figure_basename

    new_figure_title = 'Near Optimal Analysis  objected-sites: {} year(s) {} '.format(
        str(prob.cap_sites).strip('[]'),str(prob.stf_list).strip('[]'))
    ax0.set_title(new_figure_title)

    if extensions is None:
        extensions = ['png']

    # save plot to files
    for ext in extensions:
        fig_filename = '{}-{}-{}-{}.{}'.format(
            figure_basename,prob.cap_obj, str(prob.cap_sites).strip('[]'),str(prob.stf_list).strip('[]'),''.join(ext))
        fig.savefig(fig_filename, bbox_inches='tight')
    plt.close(fig)

