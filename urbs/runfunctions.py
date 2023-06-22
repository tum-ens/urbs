import os
import time

# import pyomo.environ
# from pyomo.opt.base import SolverFactory

from pyomo.environ import SolverFactory
import pyomo.environ as pyomo
from copy import deepcopy
from datetime import datetime, date
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *
from .features import *
from .scenarios import *


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


def setup_solver_old(optim, logfile='solver.log'):
    """ """
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        optim.set_options("Method=2")  # ohne method concurrent optimization
        optim.set_options("MIPGap=5e-2")  # default = 1e-4
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


def setup_solver(optim, logfile='solver.log'):
    """ """
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        # optim.set_options("NumericFocus=3")
        # optim.set_options("Crossover=0")
        # optim.set_options("Method=1") # ohne method: concurrent optimization. Method=1 -> dual simplex
        optim.set_options("MIPFocus=1")  #
        optim.set_options("BarConvTol=1e-4")
        optim.set_options("FeasibilityTol=1e-2")
        optim.set_options("OptimalityTol=1e-2")
        optim.set_options("Threads=32")
        # optim.set_options("NodeMethod=2")
        # optim.set_options("Crossover=2")
        # optim.set_options("Presolve=0")
        # optim.set_options("timelimit=7200")  # seconds
        optim.set_options("MIPGap=1e-2")  # default = 1e-4
    elif optim.name == 'glpk':
        # reference with list of options
        # execute 'glpsol --help'
        optim.set_options("log={}".format(logfile))
        # optim.set_options("tmlim=7200")  # seconds
        # optim.set_options("mipgap=.0005")
    elif optim.name == 'cplexdirect' or optim.name == 'cplex_direct':
        optim.options['threads'] = 32
        optim.options['mip display'] = 5
        # optim.options['log'] = "={}".format(logfile)
    else:
        print("Warning from setup_solver: no options set for solver "
              "'{}'!".format(optim.name))
    return optim


def setup_solver_lp(optim, logfile='solver.log'):
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        optim.set_options("Crossover=0")
        optim.set_options("Method=2")  # ohne method: concurrent optimization. Method=1 -> dual simplex
        # optim.set_options("BarConvTol=1e-4")
        # optim.set_options("FeasibilityTol=1e-2")
        # optim.set_options("OptimalityTol=1e-2")
        optim.set_options("Threads=8")
        # optim.set_options("timelimit=7200")  # seconds
    elif optim.name == 'cplexdirect' or optim.name == 'cplex_direct':
        optim.options['threads'] = 8
        # optim.options['log'] = "={}".format(logfile)
    return optim


def setup_solver_mip(optim, logfile='solver.log'):
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        # optim.set_options("NumericFocus=3")
        # optim.set_options("Crossover=0")
        # optim.set_options("Method=1") # ohne method: concurrent optimization. Method=1 -> dual simplex
        optim.set_options("MIPFocus=1")  #
        # optim.set_options("BarConvTol=1e-7")
        # optim.set_options("FeasibilityTol=1e-2")
        # optim.set_options("OptimalityTol=1e-2")
        optim.set_options("Parallel=1")
        optim.set_options("Threads=32")
        # optim.set_options("NodeMethod=2")
        # optim.set_options("Crossover=2")
        # optim.set_options("NoRelHeurTime=3600") # seconds
        # optim.set_options("Presolve=0")
        # optim.set_options("BarHomogeneous=1")
        # optim.set_options("timelimit=7200")  # seconds
        optim.set_options("MIPGap=1e-2")  # default = 1e-4
        optim.set_options("SimplexPricing=2")
        optim.set_options("DegenMoves=0")
    if optim.name == 'cplexdirect' or optim.name == 'cplex_direct':
        optim.options['threads'] = 32
        optim.options['mip_tolerances_mipgap'] = 0.01
        # optim.options['epgap'] = 0.01
    # reference with list of options
    # execute 'glpsol --help'
    return optim


def run_dist_opt(input_files, solver_name, timesteps, scenario, result_dir, dt,
                 objective,
                 microgrid_files=None,
                 plot_tuples=None,
                 plot_sites_name=None,
                 plot_periods=None,
                 report_tuples=None,
                 report_tuples_grid_plan=None,
                 report_sites_name=None,
                 cross_scenario_data=None,
                 noTypicalPeriods=None,
                 hoursPerPeriod=None,
                 uncoordinated=False,
                 flexible=False,
                 grid_curtailment=False,
                 lp=True,
                 xls=True,
                 assumelowq=True):
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
    # uncoordinated = True
    year = date.today().year
    sce = scenario.__name__
    data = read_input(input_files, year)
    data, cross_scenario_data = scenario(data, cross_scenario_data)
    validate_input(data)
    validate_dc_objective(data, objective)

    tsam_text = '_tsam' if tsam else ''
    coordination_text = '_uncoordinated' if uncoordinated else '_coordinated'
    flexible_text = '_flexible' if flexible else 'inflexible'
    grid_curtailment_text = '_grid_curtail' if grid_curtailment else ''

    if not flexible:
        # delete all storages and flexibility, add PV reactive power output
        data = remove_battery(data)
        data = remove_heat_storage(data)
        data = remove_mob_flexibility(data)
    # else:
    # data = shuffle_mob_demand(data)

    # read and modify microgrid data
    mode = identify_mode(data)

    if uncoordinated:
        # delete all transmissions
        data['transmission'] = data['transmission'].iloc[0:0]
        mode['tra'] = False
        mode['acpf'] = False

        # electricity as stock commodity in each region
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
        demand_nodes.append('main_busbar')

        for building in demand_nodes:
            data['commodity'].loc[year, building, 'electricity_feed_in', 'Sell'] = (data['commodity']['price'].
                                                                                    loc[:, :, 'electricity_feed_in',
                                                                                    :].iloc[0], np.inf, np.inf)
            data['commodity'].loc[year, building, 'electricity_import', 'Buy'] = (data['commodity']['price'].
                                                                                  loc[:, :, 'electricity_import',
                                                                                  :].iloc[0], np.inf, np.inf)

            data['process'].loc[year, building, 'feed_in'] = data['process'].loc[
                year, 'Trafostation_OS', 'feed_in']
            data['process'].loc[year, building, 'import'] = data['process'].loc[
                year, 'Trafostation_OS', 'import']

            data['process'].loc[year, building, 'feed_in']['cap-up'] = 150
            data['process'].loc[year, building, 'feed_in']['inst-cap'] = 150
            data['process'].loc[year, building, 'import']['cap-up'] = 150
            data['process'].loc[year, building, 'import']['inst-cap'] = 150

            # data_uncoordinated['commodity'].loc[year, building, 'reactive-corr','Stock'] = (1, np.inf, np.inf)
            data['process'].loc[year, building, 'Q_feeder_central'] = data['process'].loc[
                year, 'main_busbar', 'Q_feeder_central']
            data['process'].loc[year, building, 'Q_feeder_central']['cap-up'] = 150
            data['process'].loc[year, building, 'Q_feeder_central']['inst-cap'] = 150

            if mode['hp_elec']:
                if 'heatpump_air_heizstrom' in data['process'].loc[year, building, :, :].index.get_level_values(0):
                    data['commodity'].loc[year, building, 'electricity_hp_import', 'Buy'] = (data['commodity']['price'].
                                                                                             loc[:, :,
                                                                                             'electricity_hp_import',
                                                                                             :].iloc[0], np.inf, np.inf)
                    data['process'].loc[year, building, 'import_hp'] = data['process'].loc[
                        year, 'Trafostation_OS', 'import_hp']
                    data['process'].loc[year, building, 'import_hp']['cap-up'] = 150
                    data['process'].loc[year, building, 'import_hp']['inst-cap'] = 150
                    ##data['process'].loc[year, building, 'Dummy_elec_to_hp'] = data['process'].loc[
                    #     year, building, 'Heat_dummy_water']
    if not flexible:
        mode['sto'] = False

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data, cross_scenario_data = create_transdist_data(data, microgrid_data_initial,
                                                          cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data)
    add_reactive_output_ratios(data)

    if not uncoordinated and mode['hp_elec']:
        add_heatpump_flows(data)

    if tsam:
        # run timeseries aggregation method before creating model
        data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods,
                                                                         hoursPerPeriod,
                                                                         cross_scenario_data,
                                                                         mode['tsam_season'],
                                                                         uncoordinated=uncoordinated)

    # create model and clock process
    tt = time.time()

    prob = create_model(data, dt=dt,
                        timesteps=timesteps,
                        objective='cost',
                        weighting_order=weighting_order,
                        assumelowq=assumelowq,
                        hoursPerPeriod=hoursPerPeriod,
                        grid_plan_model=False,
                        dual=False)
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if 1:
        prob.write('{}{}{}{}{}_step1.lp'.format(sce,
                                                tsam_text,
                                                coordination_text,
                                                flexible_text,
                                                grid_curtailment_text),
                   io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_mip(optim, logfile=log_filename)
    print("problem sent to solver")

    result = optim.solve(prob, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    save(prob, os.path.join(result_dir, '{}{}{}{}{}_step1.h5'.format(sce,
                                                                     tsam_text,
                                                                     coordination_text,
                                                                     flexible_text,
                                                                     grid_curtailment_text)))

    if xls:
        report(prob, os.path.join(result_dir, '{}{}{}{}{}_step1.xlsx'.format(sce,
                                                                             tsam_text,
                                                                             coordination_text,
                                                                             flexible_text,
                                                                             grid_curtailment_text)),
               report_tuples=report_tuples,
               report_sites_name=report_sites_name)
    
    if uncoordinated:
        print("HELLO WORLD", uncoordinated)
        ## use the new loads for grid planning
        data_grid_plan = read_input(input_files, year)
        data_grid_plan, cross_scenario_data = scenario(data_grid_plan, cross_scenario_data)
        validate_input(data_grid_plan)
        validate_dc_objective(data_grid_plan, objective)

        # read and modify microgrid data
        mode = identify_mode(data_grid_plan)

        if mode['transdist']:
            microgrid_data_initial = []
            for i, microgrid_file in enumerate(microgrid_files):
                microgrid_data_initial.append(read_input(microgrid_file, year))
                validate_input(microgrid_data_initial[i])
            # modify and join microgrid data to model data
            data_grid_plan, cross_scenario_data = create_transdist_data(data_grid_plan, microgrid_data_initial,
                                                                        cross_scenario_data)
        # if distribution network has to be modeled without interface to transmission network
        elif mode['acpf']:
            add_reactive_transmission_lines(data_grid_plan)
            add_reactive_output_ratios(data_grid_plan)
        if mode['hp_elec']:
            add_heatpump_flows(data_grid_plan)

        # create model and clock process
        tt = time.time()
        if tsam:
            # run timeseries aggregation method before creating model
            data_grid_plan, timesteps, weighting_order, cross_scenario_data = run_tsam(data_grid_plan, noTypicalPeriods,
                                                                                       hoursPerPeriod,
                                                                                       cross_scenario_data,
                                                                                       mode['tsam_season'],
                                                                                       uncoordinated=uncoordinated)
        # timesteps = range(0,673) so correct.
        # delete all storages
        data_grid_plan['storage'] = pd.DataFrame(columns=data_grid_plan['storage'].columns)
        # delete all eff_factors
        # data_grid_plan['eff_factor'] = data_grid_plan['eff_factor'].drop(data_grid_plan['eff_factor'].columns,
        #                                                                inplace = True,
        #                                                                 axis = 1)

        # electricity as stock commodity in each region
        demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns if demand == 'space_heat']

        for building in demand_nodes:
            # delete supim timeseries
            data_grid_plan['supim'].drop((building, 'solar'), inplace=True, axis=1)

            # delete time-var-effs for heatpumps and charging stations

            #
            bui_charging_stations = [cs for (stf, bui, cs) in data_grid_plan['process'].index
                                     if cs.startswith('charging_station') and bui == building and stf == year]
            for bcs in bui_charging_stations:
                data_grid_plan['eff_factor'].drop((building, bcs), inplace=True, axis=1)

            data_grid_plan['eff_factor'].drop((building, 'heatpump_air'), inplace=True, axis=1)
            data_grid_plan['eff_factor'].drop((building, 'heatpump_air_heizstrom'), inplace=True, axis=1)
            # delete all non-electric demand, shift heating/mobility demand to electricity
            data_grid_plan['demand'].drop((building, 'space_heat'), inplace=True, axis=1)
            data_grid_plan['demand'].drop((building, 'water_heat'), inplace=True, axis=1)

            bui_mob_demands = [dem for (bui, dem) in data_grid_plan['demand'].columns
                               if dem.startswith('mobility') and bui == building]
            for mob_demand in bui_mob_demands:
                data_grid_plan['demand'].drop((building, mob_demand), inplace=True, axis=1)

            # if HP electricity is cheaper (heizstromtarif), the grid operator can lock HP electricity 6 hours a day,
            # maximum 2 hours per lock, has to be recovered in the next 2 hours (1 hour recover for 1hour lock)
            # we need to define electricity_hp as a separate demand for modeling this.
            if not mode['hp_elec']:
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob._result['tau_pro'].loc[:, year, building, 'import']
                        + prob._result['tau_pro'].loc[:, year, building, 'import_hp']
                        - prob._result['tau_pro'].loc[:, year, building, 'feed_in'])
                data_grid_plan['demand'].loc[year, :][(building, 'electricity-reactive')].iloc[1:] = \
                    prob._result['e_pro_out'] \
                        .loc[:, year, building, 'Q_feeder_central', 'electricity-reactive']
            else:
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob._result['tau_pro'].loc[:, year, building, 'import']
                        - prob._result['tau_pro'].loc[:, year, building, 'feed_in'])

                data_grid_plan['demand'][(building, 'electricity_hp_usable')] = copy.deepcopy(
                    data_grid_plan['demand'][(building, 'electricity')])

                data_grid_plan['demand'].loc[year, :][(building, 'electricity_hp_usable')].iloc[1:] = \
                    prob._result['tau_pro'].loc[:, year, building, 'import_hp']

                data_grid_plan['demand'].loc[year, :][(building, 'electricity-reactive')].iloc[1:] = \
                    prob._result['e_pro_out'].loc[:, year, building, 'Q_feeder_central', 'electricity-reactive']

                data_grid_plan['process'].loc[year, building, 'sperrzeit_comp'] = copy.deepcopy(
                    data_grid_plan['process'].loc[
                        year, 'Trafostation_OS', 'import'])

                data_grid_plan['process'].loc[year, building, 'sperrzeit_comp']['min-fraction'] = 1
                data_grid_plan['process'].loc[year, building, 'sperrzeit_comp']['on-off'] = 1
                data_grid_plan['process'].loc[year, building, 'sperrzeit_comp']['inst-cap'] = 1
                data_grid_plan['process'].loc[year, building, 'sperrzeit_comp']['cap-up'] = 1
                data_grid_plan['process'].loc[year, building, 'sperrzeit_comp']['var-cost'] = \
                    data_grid_plan['commodity'].loc[year, 'Trafostation_OS', 'electricity_hp_import', 'Buy'][
                        'price'] + 0.0001
                data_grid_plan['eff_factor'][(building, 'sperrzeit_comp')] = data_grid_plan['demand'][
                    (building, 'electricity_hp_usable')]

            # delete all processes besides Q-compensation, import and feed-in
            data_grid_plan['process'].drop((year, building, 'Rooftop PV'), inplace=True, axis=0)
            # data_grid_plan['process'].drop((year, building, 'charging_station'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'Heat_dummy_space'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'Heat_dummy_water'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'heatpump_air'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'heatpump_air_heizstrom'), inplace=True, axis=0)

            bui_charging_stations = [cs for (stf, bui, cs) in data_grid_plan['process'].index
                                     if cs.startswith('charging_station') and bui == building and stf == year]
            for bcs in bui_charging_stations:
                data_grid_plan['process'].drop((year, building, bcs), inplace=True, axis=0)

            if not grid_curtailment:
                data_grid_plan['process'].drop((year, building, 'curtailment'), inplace=True, axis=0)
            else:
                data_grid_plan['process'].loc[(year, building, 'curtailment'), 'var-cost'] = 0.064
            data_grid_plan['process'].drop((year, building, 'Slack_heat'), inplace=True, axis=0)

            data_grid_plan['commodity'].drop((year, building, 'electricity_hp_usable', 'Stock'), inplace=True, axis=0)
            if mode['hp_elec']:
                data_grid_plan['commodity'].loc[year, building, 'electricity_hp_usable', 'Demand'] = (0, 0, 0)
            data_grid_plan['commodity'].drop((year, building, 'space_heat', 'Demand'), inplace=True, axis=0)
            data_grid_plan['commodity'].drop((year, building, 'water_heat', 'Demand'), inplace=True, axis=0)
            data_grid_plan['commodity'].drop((year, building, 'solar', 'SupIm'), inplace=True, axis=0)

            bui_mob_commodities = [com for (stf, sit, com, typ) in data_grid_plan['commodity'].index
                                   if com.startswith('mobility') and sit == building]
            for com in bui_mob_commodities:
                data_grid_plan['commodity'].drop((year, building, com, 'Demand'), inplace=True, axis=0)
            data_grid_plan['commodity'].drop((year, building, 'common_heat', 'Stock'), inplace=True, axis=0)
            # data_grid_plan['commodity'].drop((year, building, 'CO2','Env'),inplace=True,axis=0)

        # delete all process_commodity for deleted processes
        data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'solar', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'electricity', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'common_heat', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'space_heat', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'common_heat', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'water_heat', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air_heizstrom', 'electricity_hp_usable', 'In'),
                                                 inplace=True,
                                                 axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air_heizstrom', 'common_heat', 'Out'), inplace=True,
                                                 axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'elec_hp_to_usable', 'electricity_hp', 'In'), inplace=True,
        #                                         axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'elec_hp_to_usable', 'electricity_hp_usable', 'Out'), inplace=True,
        #                                         axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'electricity', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'common_heat', 'Out'), inplace=True, axis=0)

        unique_charging_stations = [ucs for (stf, ucs, com, direction) in data_grid_plan['process_commodity'].index
                                    if ucs.startswith('charging_station') and direction == 'In']
        for ucs in unique_charging_stations:
            data_grid_plan['process_commodity'].drop((year, ucs, 'electricity', 'In'), inplace=True, axis=0)
            data_grid_plan['process_commodity'].drop((year, ucs, 'mobility' + ucs[16:], 'Out'), inplace=True, axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'Dummy_elec_to_hp', 'electricity', 'In'), inplace=True, axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'Dummy_elec_to_hp', 'electricity_hp', 'Out'), inplace=True,
        #                                         axis=0)
        if not grid_curtailment:
            data_grid_plan['process_commodity'].drop((year, 'curtailment', 'electricity', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Slack_heat', 'common_heat', 'Out'), inplace=True, axis=0)

        if mode['hp_elec']:
            data_grid_plan['process_commodity'].loc[year, 'sperrzeit_comp', 'electricity_hp_usable', 'Out'] = (
                1, np.nan)
            data_grid_plan['process_commodity'].loc[year, 'sperrzeit_comp', 'electricity-reactive', 'Out'] = \
                (np.tan(np.arccos(data['global_prop'].loc[year, 'PF_HP']['value'])), np.nan)

        prob_grid_plan = create_model(data_grid_plan, dt=dt,
                                      timesteps=timesteps,
                                      objective='cost',
                                      weighting_order=weighting_order,
                                      assumelowq=assumelowq,
                                      hoursPerPeriod=hoursPerPeriod,
                                      grid_plan_model=True,
                                      dual=False)
        print('Elapsed time to build the pyomo model of grid planning: %s s' % round(time.time() - tt, 4))

        # write lp file # lp writing needs huge RAM capacities for bigger models
        if lp:
            prob_grid_plan.write('{}{}{}{}{}_step2.lp'.format(sce,
                                                              tsam_text,
                                                              coordination_text,
                                                              flexible_text,
                                                              grid_curtailment_text),
                                 io_options={'symbolic_solver_labels': True})

        # refresh time stamp string and create filename for logfile
        log_filename = os.path.join(result_dir, '{}.log').format(sce)

        # set presolve to conservative, as this step takes way too long
        optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
        optim = setup_solver_mip(optim, logfile=log_filename)
        # set presolve to off, as this step takes way too long
        # optim.set_options("Presolve=0")

        print("problem sent to solver")
        result = optim.solve(prob_grid_plan, tee=True, report_timing=True)

        save(prob_grid_plan, os.path.join(result_dir, '{}{}{}{}{}_step2.h5'.format(sce,
                                                                                   tsam_text,
                                                                                   coordination_text,
                                                                                   flexible_text,
                                                                                   grid_curtailment_text)))

        if xls:
            report(prob_grid_plan, os.path.join(result_dir, '{}{}{}{}{}_step2.xlsx'.format(sce,
                                                                                           tsam_text,
                                                                                           coordination_text,
                                                                                           flexible_text,
                                                                                           grid_curtailment_text)),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)

        if mode['hp_elec']:
            print("Third step comes now, for the reaction of households to the Sperrzeit")
            data_hp_react = copy.deepcopy(data)

            for building in demand_nodes:
                data_hp_react['eff_factor'][(building, 'import_hp')] = 1 - \
                                                                       prob_grid_plan._result['on_off'].loc[:, :,
                                                                       building,
                                                                       'sperrzeit_comp'].values
            # import pdb;pdb.set_trace()
            prob_hp_react = create_model(data_hp_react, dt=dt,
                                         timesteps=timesteps,
                                         objective='cost',
                                         weighting_order=weighting_order,
                                         assumelowq=assumelowq,
                                         hoursPerPeriod=hoursPerPeriod,
                                         grid_plan_model=False,
                                         dual=False)

            # fix all capacitties in building model to see hp reaction
            capacity_variables = ['cap_pro_new', 'cap_decommissioned',
                                  'cap_sto_c_new', 'cap_sto_p_new', 'cap_sto_c_decommissioned',
                                  'cap_sto_p_decommissioned']

            for cap_var in capacity_variables:
                caps = get_entity(prob, cap_var)
                for var_idx in getattr(prob_hp_react, cap_var):
                    getattr(prob_hp_react, cap_var)[var_idx].fix(caps[var_idx])
                # write lp file # lp writing needs huge RAM capacities for bigger models

            #fix curtailment
            tau_values = get_entity(prob_grid_plan, 'tau_pro')
            for var_idx in getattr(prob_hp_react, 'tau_pro'):
                if var_idx[3] == 'curtailment':
                    if var_idx[0] != 0:
                        getattr(prob_hp_react, 'tau_pro')[var_idx].fix(tau_values[var_idx])

            #delete single hp rule, not necessary and causes infeasibility
            del prob_hp_react.res_single_heatpump

            if lp:
                prob_hp_react.write('{}{}{}{}{}_step3.lp'.format(sce,
                                                                 tsam_text,
                                                                 coordination_text,
                                                                 flexible_text,
                                                                 grid_curtailment_text),
                                    io_options={'symbolic_solver_labels': True})
            result = optim.solve(prob_hp_react, tee=True, report_timing=True)

            save(prob_hp_react, os.path.join(result_dir, '{}{}{}{}{}_step3.h5'.format(sce,
                                                                                      tsam_text,
                                                                                      coordination_text,
                                                                                      flexible_text,
                                                                                      grid_curtailment_text)))

            if xls:
                report(prob_hp_react, os.path.join(result_dir, '{}{}{}{}{}_step3.xlsx'.format(sce,
                                                                                              tsam_text,
                                                                                              coordination_text,
                                                                                              flexible_text,
                                                                                              grid_curtailment_text)),
                       report_tuples=report_tuples,
                       report_sites_name=report_sites_name)
            return prob, prob_grid_plan, prob_hp_react, cross_scenario_data

    if uncoordinated:
        return prob, prob_grid_plan, cross_scenario_data
    else:
        return prob, cross_scenario_data


def run_scenario(input_files, solver_name, timesteps, scenario, result_dir, dt,
                 objective, microgrid_files=None, plot_tuples=None, plot_sites_name=None,
                 plot_periods=None, report_tuples=None, report_sites_name=None,
                 cross_scenario_data=None, noTypicalPeriods=None, hoursPerPeriod=None):
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
    print("input read")
    data, cross_scenario_data = scenario(data, cross_scenario_data)
    print("scenario applied")
    validate_input(data)
    validate_dc_objective(data, objective)
    print("input validated")

    # read and modify microgrid data
    mode = identify_mode(data)
    print("mode identified")

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data, cross_scenario_data = create_transdist_data(data, microgrid_data_initial, cross_scenario_data)
        print("transdist data created")

    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data)
        add_reactive_output_ratios(data)
        print("AC features applied")

    if mode['tsam']:
        # run timeseries aggregation method before creating model
        print("dataset sent to tsam")
        data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods, hoursPerPeriod,
                                                                         cross_scenario_data, mode['tsam_season'])
        print("tsam applied")

        # create model and clock process
        tt = time.time()
        prob = create_model(data, dt, timesteps, objective, hoursPerPeriod, weighting_order,
                            dual=False)
        print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))
    else:
        # create model and clock process
        tt = time.time()
        prob = create_model(data, dt, timesteps, objective, dual=False)
        #
        print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    prob.write(sce + '.lp', io_options={'symbolic_solver_labels': True})
    print("LP file written")

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    print("problem sent to solver")

    result = optim.solve(prob, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    # save problem solution (and input data) to HDF5 file
    save(prob, os.path.join(result_dir, '{}.h5'.format(sce)))

    # no report tuples and plot tuples are defined - postprocessing with h5 file in jupyter
    ## write report to spreadsheet
    report(prob, os.path.join(result_dir, '{}.xlsx').format(sce),
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

    return prob, cross_scenario_data


def coordinated_opt(input_files, solver_name, timesteps, scenario, result_dir, dt,
                    objective, microgrid_files=None, plot_tuples=None, plot_sites_name=None,
                    plot_periods=None, report_tuples=None, report_sites_name=None,
                    cross_scenario_data=None, noTypicalPeriods=None, hoursPerPeriod=None,
                    unaggregated_length=8760, lp=False, xls=False, assumelowq=True):
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
    data, cross_scenario_data = scenario(data, cross_scenario_data)

    data = shuffle_mob_demand(data)

    validate_input(data)
    validate_dc_objective(data, objective)

    # read and modify microgrid data
    mode = identify_mode(data)

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data, cross_scenario_data = create_transdist_data(data, microgrid_data_initial, cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data)
        add_reactive_output_ratios(data)
    mode['tsam'] = True
    mode['tsam_season'] = False

    # run timeseries aggregation method before creating model
    data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods, hoursPerPeriod,
                                                                     cross_scenario_data, mode['tsam_season'])
    # create model and clock process
    tt = time.time()
    prob = create_model(data, dt, timesteps, objective, hoursPerPeriod, weighting_order,
                        assumelowq, dual=False)  # dual false neccessary due to quadratic constraint infeasibility
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    #CHANGED VALUE HERE
    if 1:
        prob.write(sce + '_coordinated_step1' + '.lp', io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_mip(optim, logfile=log_filename)
    print("problem sent to solver")

    result = optim.solve(prob, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    save(prob, os.path.join(result_dir, '{}_coordinated_step1.h5'.format(sce)))
    if xls:
        report(prob, os.path.join(result_dir, '{}_coordinated_step1.xlsx').format(sce),
               report_tuples=report_tuples,
               report_sites_name=report_sites_name)
    prob_with_capacities = deepcopy(prob)

    ## capacities obtained from the aggregated model, now run the whole model for operation
    data = read_input(input_files, year)
    data, cross_scenario_data = scenario(data, cross_scenario_data)
    data = shuffle_mob_demand(data)

    validate_input(data)
    validate_dc_objective(data, objective)

    # read and modify microgrid data
    mode = identify_mode(data)
    mode['tsam'] = False
    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data, cross_scenario_data = create_transdist_data(data, microgrid_data_initial, cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data)
        add_reactive_output_ratios(data)
    # create model and clock process
    tt = time.time()
    timesteps = range(0, unaggregated_length + 1)
    prob = create_model(data, dt, timesteps, objective, assumelowq, dual=False)
    #
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    ## fix capacities from the aggregated model
    capacity_variables = ['pro_cap_unit', 'cap_pro_new', 'cap_decommissioned',
                          'cap_sto_c_new', 'cap_sto_p_new', 'cap_sto_c_decommissioned',
                          'cap_sto_p_decommissioned', 'sto_cap_c_unit', 'sto_cap_p_unit',
                          'cap_tra_unit', 'cap_tra_new', 'cap_tra_decommissioned']

    for cap_var in capacity_variables:
        caps = get_entity(prob_with_capacities, cap_var)
        for var_idx in getattr(prob, cap_var):
            getattr(prob, cap_var)[var_idx].fix(caps[var_idx])

    print(
        'Elapsed time to build the pyomo model of the non-aggregated dispatch model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if lp:
        prob.write(sce + '_coordinated_step2' + '.lp', io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    # no crossover, as no integers anymore
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_lp(optim, logfile=log_filename)
    print("problem sent to solver")
    result = optim.solve(prob, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    if xls:
        report(prob, os.path.join(result_dir, '{}_coordinated_step2.xlsx').format(sce),
               report_tuples=report_tuples,
               report_sites_name=report_sites_name)
    save(prob, os.path.join(result_dir, '{}_coordinated_step2.h5'.format(sce)))

    return prob, cross_scenario_data

    # no report tuples and plot tuples are defined - postprocessing with h5 file in jupyter
    ### write report to spreadsheet
    # report(prob, os.path.join(result_dir, '{}.xlsx').format(sce),
    #       report_tuples=report_tuples,
    #       report_sites_name=report_sites_name)
    # result plots
    # result_figures(
    #    prob,
    #    os.path.join(result_dir, '{}'.format(sce)),
    #    timesteps,
    #    plot_title_prefix=sce.replace('_', ' '),
    #    plot_tuples=plot_tuples,
    #    plot_sites_name=plot_sites_name,
    #    periods=plot_periods,
    #    figure_size=(24, 9))


def uncoordinated(input_files, solver_name, timesteps, scenario, result_dir, dt,
                  objective, microgrid_files=None, plot_tuples=None, plot_sites_name=None,
                  plot_periods=None, report_tuples=None, report_tuples_grid_plan=None, report_sites_name=None,
                  cross_scenario_data=None, noTypicalPeriods=None, hoursPerPeriod=None,
                  unaggregated_length=8760, flexible=False, grid_curtailment=False, lp=True, xls=True, assumelowq=True):
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
    uncoordinated = True

    # sets a modeled year for non-intertemporal problems
    # (necessary for consitency)
    year = date.today().year

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data_uncoordinated = read_input(input_files, year)
    data_uncoordinated, cross_scenario_data = scenario(data_uncoordinated, cross_scenario_data)
    validate_input(data_uncoordinated)
    validate_dc_objective(data_uncoordinated, objective)

    # delete all transmissions
    # import pdb;pdb.set_trace()
    data_uncoordinated['transmission'] = data_uncoordinated['transmission'].iloc[0:0]
    # data_uncoordinated['transmission']['inst-cap'] = 0
    # data_uncoordinated['transmission']['cap-up'] = 0

    # delete all storages and flexibility, add PV reactive power output
    if not flexible:
        data_uncoordinated = remove_battery(data_uncoordinated)
        data_uncoordinated = remove_heat_storage(data_uncoordinated)
        data_uncoordinated = remove_mob_flexibility(data_uncoordinated)
    else:
        data_uncoordinated = shuffle_mob_demand(data_uncoordinated)
    add_reactive_output_ratios(data_uncoordinated)

    # electricity as stock commodity in each region
    demand_nodes = [sit for (sit, demand) in data_uncoordinated['demand'].columns if demand == 'space_heat']
    demand_nodes.append('main_busbar')

    for building in demand_nodes:
        data_uncoordinated['commodity'].loc[year, building, 'electricity_feed_in', 'Sell'] = (1, np.inf, np.inf)
        data_uncoordinated['commodity'].loc[year, building, 'electricity_import', 'Buy'] = (1, np.inf, np.inf)
        data_uncoordinated['process'].loc[year, building, 'feed_in'] = data_uncoordinated['process'].loc[
            year, 'Trafostation_OS', 'feed_in']
        data_uncoordinated['process'].loc[year, building, 'import'] = data_uncoordinated['process'].loc[
            year, 'Trafostation_OS', 'import']
        # import pdb;pdb.set_trace()
        data_uncoordinated['process'].loc[year, building, 'feed_in']['cap-up'] = 150
        data_uncoordinated['process'].loc[year, building, 'feed_in']['inst-cap'] = 150
        data_uncoordinated['process'].loc[year, building, 'import']['cap-up'] = 150
        data_uncoordinated['process'].loc[year, building, 'import']['inst-cap'] = 150

        # data_uncoordinated['commodity'].loc[year, building, 'reactive-corr','Stock'] = (1, np.inf, np.inf)
        data_uncoordinated['process'].loc[year, building, 'Q_feeder_central'] = data_uncoordinated['process'].loc[
            year, 'main_busbar', 'Q_feeder_central']
        data_uncoordinated['process'].loc[year, building, 'Q_feeder_central']['cap-up'] = 150
        data_uncoordinated['process'].loc[year, building, 'Q_feeder_central']['inst-cap'] = 150

    # read and modify microgrid data
    mode = identify_mode(data_uncoordinated)

    mode['tra'] = False

    if not flexible:
        mode['sto'] = False

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data_uncoordinated, cross_scenario_data = create_transdist_data(data_uncoordinated, microgrid_data_initial,
                                                                        cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data_uncoordinated)
        add_reactive_output_ratios(data_uncoordinated)
    mode['tsam'] = True
    mode['tsam_season'] = False

    # run timeseries aggregation method before creating model
    data_uncoordinated, timesteps, weighting_order, cross_scenario_data = run_tsam(data_uncoordinated, noTypicalPeriods,
                                                                                   hoursPerPeriod,
                                                                                   cross_scenario_data,
                                                                                   mode['tsam_season'], uncoordinated)

    # create model and clock process
    tt = time.time()
    prob_uncoordinated = create_model(data_uncoordinated, dt, timesteps, objective, hoursPerPeriod, weighting_order,
                                      dual=False)  # dual false neccessary due to quadratic constraint infeasibility
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if lp:
        if not flexible:
            prob_uncoordinated.write(sce + '_uncoordinated_inflexible_step1' + '.lp',
                                     io_options={'symbolic_solver_labels': True})
        elif not grid_curtailment:
            prob_uncoordinated.write(sce + '_uncoordinated_flexible_step1' + '.lp',
                                     io_options={'symbolic_solver_labels': True})
        else:
            prob_uncoordinated.write(sce + '_uncoordinated_flexible_grid_curtail_step1' + '.lp',
                                     io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_lp(optim, logfile=log_filename)
    print("problem sent to solver")

    result = optim.solve(prob_uncoordinated, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    if not flexible:
        save(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_inflexible_step1.h5'.format(sce)))
    elif not grid_curtailment:
        save(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_flexible_step1.h5'.format(sce)))
    else:
        save(prob_uncoordinated,
             os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step1.h5'.format(sce)))

    if xls:
        if not flexible:
            report(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_inflexible_step1.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)
        elif not grid_curtailment:
            report(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_flexible_step1.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)
        else:
            report(prob_uncoordinated,
                   os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step1.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)

    ## capacities obtained from the aggregated model, now run the whole model for operation of buildings
    data_uncoordinated_yearly = read_input(input_files, year)
    data_uncoordinated_yearly, cross_scenario_data = scenario(data_uncoordinated_yearly, cross_scenario_data)
    validate_input(data_uncoordinated_yearly)
    validate_dc_objective(data_uncoordinated_yearly, objective)

    # delete all transmissions
    data_uncoordinated_yearly['transmission'] = data_uncoordinated_yearly['transmission'].iloc[0:0]

    # delete all storages and flexibility, add PV reactive power output
    if not flexible:
        data_uncoordinated_yearly = remove_battery(data_uncoordinated_yearly)
        data_uncoordinated_yearly = remove_heat_storage(data_uncoordinated_yearly)
        data_uncoordinated_yearly = remove_mob_flexibility(data_uncoordinated_yearly)
    else:
        data_uncoordinated_yearly = shuffle_mob_demand(data_uncoordinated_yearly)

    add_reactive_output_ratios(data_uncoordinated_yearly)

    # electricity as stock commodity in each region
    demand_nodes = [sit for (sit, demand) in data_uncoordinated_yearly['demand'].columns if demand == 'space_heat']
    demand_nodes.append('main_busbar')

    for building in demand_nodes:
        data_uncoordinated_yearly['commodity'].loc[year, building, 'electricity_feed_in', 'Sell'] = (1, np.inf, np.inf)
        data_uncoordinated_yearly['commodity'].loc[year, building, 'electricity_import', 'Buy'] = (1, np.inf, np.inf)
        data_uncoordinated_yearly['process'].loc[year, building, 'feed_in'] = data_uncoordinated_yearly['process'].loc[
            year, 'Trafostation_OS', 'feed_in']
        data_uncoordinated_yearly['process'].loc[year, building, 'import'] = data_uncoordinated_yearly['process'].loc[
            year, 'Trafostation_OS', 'import']
        data_uncoordinated_yearly['process'].loc[year, building, 'feed_in']['cap-up'] = 150
        data_uncoordinated_yearly['process'].loc[year, building, 'feed_in']['inst-cap'] = 150
        data_uncoordinated_yearly['process'].loc[year, building, 'import']['cap-up'] = 150
        data_uncoordinated_yearly['process'].loc[year, building, 'import']['inst-cap'] = 150

        # data_uncoordinated_yearly['commodity'].loc[year, building, 'reactive-corr','Stock'] = (1, np.inf, np.inf)
        data_uncoordinated_yearly['process'].loc[year, building, 'Q_feeder_central'] = \
            data_uncoordinated_yearly['process'].loc[year, 'main_busbar', 'Q_feeder_central']
        data_uncoordinated_yearly['process'].loc[year, building, 'Q_feeder_central']['cap-up'] = 150
        data_uncoordinated_yearly['process'].loc[year, building, 'Q_feeder_central']['inst-cap'] = 150

    # read and modify microgrid data
    mode = identify_mode(data_uncoordinated_yearly)
    mode['tra'] = False
    if not flexible:
        mode['sto'] = False
    mode['tsam'] = False

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data_uncoordinated_yearly, cross_scenario_data = create_transdist_data(data_uncoordinated_yearly,
                                                                               microgrid_data_initial,
                                                                               cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data_uncoordinated_yearly)
        add_reactive_output_ratios(data_uncoordinated_yearly)
    # create model and clock process
    tt = time.time()

    timesteps = range(0, unaggregated_length + 1)

    prob_uncoordinated_yearly = create_model(data_uncoordinated_yearly, dt, timesteps, objective, dual=False)
    #
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    ## fix capacities from the aggregated model for buildings
    capacity_variables = ['pro_cap_unit', 'cap_pro_new', 'cap_decommissioned',
                          'cap_sto_c_new', 'cap_sto_p_new', 'cap_sto_c_decommissioned',
                          'cap_sto_p_decommissioned', 'sto_cap_c_unit', 'sto_cap_p_unit']

    for cap_var in capacity_variables:
        caps = get_entity(prob_uncoordinated, cap_var)
        for var_idx in getattr(prob_uncoordinated_yearly, cap_var):
            getattr(prob_uncoordinated_yearly, cap_var)[var_idx].fix(caps[var_idx])

    print(
        'Elapsed time to build the pyomo model of the non-aggregated dispatch model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if lp:
        if not flexible:
            prob_uncoordinated_yearly.write(sce + '_uncoordinated_inflexible_step2' + '.lp',
                                            io_options={'symbolic_solver_labels': True})
        elif not grid_curtailment:
            prob_uncoordinated_yearly.write(sce + '_uncoordinated_flexible_step2' + '.lp',
                                            io_options={'symbolic_solver_labels': True})
        else:
            prob_uncoordinated_yearly.write(sce + '_uncoordinated_flexible_grid_curtail_step2' + '.lp',
                                            io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    # no crossover, as no integers anymore
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_lp(optim, logfile=log_filename)
    print("problem sent to solver")
    result = optim.solve(prob_uncoordinated_yearly, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    if not flexible:
        save(prob_uncoordinated_yearly, os.path.join(result_dir, '{}_uncoordinated_inflexible_step2.h5'.format(sce)))
    elif not grid_curtailment:
        save(prob_uncoordinated_yearly, os.path.join(result_dir, '{}_uncoordinated_flexible_step2.h5'.format(sce)))
    else:
        save(prob_uncoordinated_yearly,
             os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step2.h5'.format(sce)))

    if xls:
        if not flexible:
            report(prob_uncoordinated_yearly,
                   os.path.join(result_dir, '{}_uncoordinated_inflexible_step2.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)
        elif not grid_curtailment:
            report(prob_uncoordinated_yearly,
                   os.path.join(result_dir, '{}_uncoordinated_flexible_step2.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)
        else:
            report(prob_uncoordinated_yearly,
                   os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step2.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)

    ## use the new loads for grid planning
    data_grid_plan = read_input(input_files, year)
    data_grid_plan, cross_scenario_data = scenario(data_grid_plan, cross_scenario_data)
    validate_input(data_grid_plan)
    validate_dc_objective(data_grid_plan, objective)

    # read and modify microgrid data
    mode = identify_mode(data_grid_plan)
    mode['tsam'] = False  # nonaggregated
    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data_grid_plan, cross_scenario_data = create_transdist_data(data_grid_plan, microgrid_data_initial,
                                                                    cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data_grid_plan)
        add_reactive_output_ratios(data_grid_plan)
    # create model and clock process
    tt = time.time()

    timesteps = range(0, unaggregated_length + 1)

    # remove heat loads
    # add new electricity loads
    # import pdb;pdb.set_trace()
    ##delete all transmissions
    # data['transmission']['inst-cap'] = 0
    # data['transmission']['cap-up'] = 0

    # delete all storages
    data_grid_plan['storage'] = pd.DataFrame(columns=data_grid_plan['storage'].columns)

    # electricity as stock commodity in each region
    demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns if demand == 'space_heat']
    # import pdb;pdb.set_trace()
    for building in demand_nodes:
        # delete supim timeseries
        data_grid_plan['supim'].drop((building, 'solar'), inplace=True, axis=1)

        # delete time-var-effs for heatpumps and charging stations
        data_grid_plan['eff_factor'].drop((building, 'charging_station'), inplace=True, axis=1)
        data_grid_plan['eff_factor'].drop((building, 'heatpump_air'), inplace=True, axis=1)

        # delete all non-electric demand, shift heating/mobility demand to electricity
        data_grid_plan['demand'].drop((building, 'space_heat'), inplace=True, axis=1)
        data_grid_plan['demand'].drop((building, 'water_heat'), inplace=True, axis=1)
        data_grid_plan['demand'].drop((building, 'mobility'), inplace=True, axis=1)
        data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:unaggregated_length + 1] = (
                                                                                                                   prob_uncoordinated_yearly._result[
                                                                                                                       'tau_pro'].loc[
                                                                                                                   :,
                                                                                                                   year,
                                                                                                                   building,
                                                                                                                   'import']
                                                                                                                   -
                                                                                                                   prob_uncoordinated_yearly._result[
                                                                                                                       'tau_pro'].loc[
                                                                                                                   :,
                                                                                                                   year,
                                                                                                                   building,
                                                                                                                   'feed_in']).iloc[
                                                                                                           1:unaggregated_length + 1]
        data_grid_plan['demand'].loc[year, :][(building, 'electricity-reactive')].iloc[1:unaggregated_length + 1] = \
            prob_uncoordinated_yearly._result['e_pro_out'].loc[:, year, building, 'Q_feeder_central',
            'electricity-reactive']

        # delete all processes besides Q-compensation, import and feed-in
        data_grid_plan['process'].drop((year, building, 'Rooftop PV'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'charging_station'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'Heat_dummy_space'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'Heat_dummy_water'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'heatpump_air'), inplace=True, axis=0)
        if not grid_curtailment:
            data_grid_plan['process'].drop((year, building, 'curtailment'), inplace=True, axis=0)
        else:
            data_grid_plan['process'].loc[(year, building, 'curtailment'), 'var-cost'] = 0.064
        data_grid_plan['process'].drop((year, building, 'Slack_heat'), inplace=True, axis=0)

        data_grid_plan['commodity'].drop((year, building, 'space_heat', 'Demand'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'water_heat', 'Demand'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'solar', 'SupIm'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'mobility', 'Demand'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'common_heat', 'Stock'), inplace=True, axis=0)
        # data_grid_plan['commodity'].drop((year, building, 'CO2','Env'),inplace=True,axis=0)

    # delete all process_commodity for deleted processes
    data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'solar', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'electricity', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'common_heat', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'space_heat', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'common_heat', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'water_heat', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'electricity', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'common_heat', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'charging_station', 'electricity', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'charging_station', 'mobility', 'Out'), inplace=True, axis=0)
    if not grid_curtailment:
        data_grid_plan['process_commodity'].drop((year, 'curtailment', 'electricity', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Slack_heat', 'common_heat', 'Out'), inplace=True, axis=0)

    # data_grid_plan['eff_factor'].drop((building,'charging_station'),inplace=True,axis=1)
    # data_grid_plan['eff_factor'].drop((building,'heatpump_air'),inplace=True,axis=1)
    # data_grid_plan['supim'].drop((building,'solar'),inplace=True,axis=1)

    prob_grid_plan = create_model(data_grid_plan, dt, timesteps, objective, assumelowq, dual=False)

    print('Elapsed time to build the pyomo model of grid planning: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if lp:
        if not flexible:
            prob_grid_plan.write(sce + '_uncoordinated_inflexible_step3' + '.lp',
                                 io_options={'symbolic_solver_labels': True})
        elif not grid_curtailment:
            prob_grid_plan.write(sce + '_uncoordinated_flexible_step3' + '.lp',
                                 io_options={'symbolic_solver_labels': True})
        else:
            prob_grid_plan.write(sce + '_uncoordinated_flexible_grid_curtail_step3' + '.lp',
                                 io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # set presolve to conservative, as this step takes way too long
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_mip(optim, logfile=log_filename)
    # set presolve to off, as this step takes way too long
    # optim.set_options("Presolve=0")

    print("problem sent to solver")
    result = optim.solve(prob_grid_plan, tee=True, report_timing=True)

    if not flexible:
        save(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_inflexible_step3.h5'.format(sce)))
    elif not grid_curtailment:
        save(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_flexible_step3.h5'.format(sce)))
    else:
        save(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step3.h5'.format(sce)))

    if xls:
        if not flexible:
            report(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_inflexible_step3.xlsx').format(sce),
                   report_tuples=report_tuples_grid_plan,
                   report_sites_name=report_sites_name)
        elif not grid_curtailment:
            report(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_flexible_step3.xlsx').format(sce),
                   report_tuples=report_tuples_grid_plan,
                   report_sites_name=report_sites_name)
        else:
            report(prob_grid_plan,
                   os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step3.xlsx').format(sce),
                   report_tuples=report_tuples_grid_plan,
                   report_sites_name=report_sites_name)

    return prob_uncoordinated, prob_uncoordinated_yearly, prob_grid_plan, cross_scenario_data


def coordinated_opt_tsam(input_files, solver_name, timesteps, scenario, result_dir, dt,
                         objective, microgrid_files=None, plot_tuples=None, plot_sites_name=None,
                         plot_periods=None, report_tuples=None, report_sites_name=None,
                         cross_scenario_data=None, noTypicalPeriods=None, hoursPerPeriod=None,
                         unaggregated_length=8760, lp=False, xls=False, assumelowq=True):
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
    data, cross_scenario_data = scenario(data, cross_scenario_data)

    data = shuffle_mob_demand(data)

    validate_input(data)
    validate_dc_objective(data, objective)

    # read and modify microgrid data
    mode = identify_mode(data)

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data, cross_scenario_data = create_transdist_data(data, microgrid_data_initial, cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data)
        add_reactive_output_ratios(data)
    add_heatpump_flows(data)
    data['transmission'].to_csv('a.csv')
    mode['tsam'] = True
    mode['tsam_season'] = False

    # run timeseries aggregation method before creating model
    data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods, hoursPerPeriod,
                                                                     cross_scenario_data, mode['tsam_season'])
    # create model and clock process
    tt = time.time()
    prob = create_model(data, dt, timesteps, objective, hoursPerPeriod, weighting_order,
                        assumelowq, dual=False)  # dual false neccessary due to quadratic constraint infeasibility
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if lp:
        prob.write(sce + '_coordinated_tsam_step1' + '.lp', io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_mip(optim, logfile=log_filename)
    print("problem sent to solver")

    result = optim.solve(prob, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    save(prob, os.path.join(result_dir, '{}_coordinated_step1.h5'.format(sce)))
    if xls:
        report(prob, os.path.join(result_dir, '{}_coordinated_step1.xlsx').format(sce),
               report_tuples=report_tuples,
               report_sites_name=report_sites_name)

    return prob, cross_scenario_data


def uncoordinated_tsam(input_files, solver_name, timesteps, scenario, result_dir, dt,
                       objective, microgrid_files=None, plot_tuples=None, plot_sites_name=None,
                       plot_periods=None, report_tuples=None, report_tuples_grid_plan=None, report_sites_name=None,
                       cross_scenario_data=None, noTypicalPeriods=None, hoursPerPeriod=None,
                       unaggregated_length=8760, flexible=False, grid_curtailment=False, lp=True, xls=True,
                       assumelowq=True):
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
    uncoordinated = True

    # sets a modeled year for non-intertemporal problems
    # (necessary for consitency)
    year = date.today().year

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data_uncoordinated = read_input(input_files, year)
    data_uncoordinated, cross_scenario_data = scenario(data_uncoordinated, cross_scenario_data)
    validate_input(data_uncoordinated)
    validate_dc_objective(data_uncoordinated, objective)

    # delete all transmissions
    data_uncoordinated['transmission'] = data_uncoordinated['transmission'].iloc[0:0]

    if not flexible:
        # delete all storages and flexibility, add PV reactive power output
        data_uncoordinated = remove_battery(data_uncoordinated)
        data_uncoordinated = remove_heat_storage(data_uncoordinated)
        data_uncoordinated = remove_mob_flexibility(data_uncoordinated)
    else:
        data_uncoordinated = shuffle_mob_demand(data_uncoordinated)
    add_reactive_output_ratios(data_uncoordinated)
    add_heatpump_flows(data_uncoordinated)

    # electricity as stock commodity in each region
    demand_nodes = [sit for (sit, demand) in data_uncoordinated['demand'].columns if demand == 'space_heat']
    demand_nodes.append('main_busbar')

    for building in demand_nodes:
        data_uncoordinated['commodity'].loc[year, building, 'electricity_feed_in', 'Sell'] = (1, np.inf, np.inf)
        data_uncoordinated['commodity'].loc[year, building, 'electricity_import', 'Buy'] = (1, np.inf, np.inf)
        data_uncoordinated['commodity'].loc[year, building, 'electricity_hp_import', 'Buy'] = (1, np.inf, np.inf)
        data_uncoordinated['process'].loc[year, building, 'feed_in'] = data_uncoordinated['process'].loc[
            year, 'Trafostation_OS', 'feed_in']
        data_uncoordinated['process'].loc[year, building, 'import'] = data_uncoordinated['process'].loc[
            year, 'Trafostation_OS', 'import']
        data_uncoordinated['process'].loc[year, building, 'import_hp'] = data_uncoordinated['process'].loc[
            year, 'Trafostation_OS', 'import_hp']
        # import pdb;pdb.set_trace()
        data_uncoordinated['process'].loc[year, building, 'feed_in']['cap-up'] = 150
        data_uncoordinated['process'].loc[year, building, 'feed_in']['inst-cap'] = 150
        data_uncoordinated['process'].loc[year, building, 'import']['cap-up'] = 150
        data_uncoordinated['process'].loc[year, building, 'import']['inst-cap'] = 150
        data_uncoordinated['process'].loc[year, building, 'import_hp']['cap-up'] = 150
        data_uncoordinated['process'].loc[year, building, 'import_hp']['inst-cap'] = 150
        # data_uncoordinated['commodity'].loc[year, building, 'reactive-corr','Stock'] = (1, np.inf, np.inf)
        data_uncoordinated['process'].loc[year, building, 'Q_feeder_central'] = data_uncoordinated['process'].loc[
            year, 'main_busbar', 'Q_feeder_central']
        data_uncoordinated['process'].loc[year, building, 'Q_feeder_central']['cap-up'] = 150
        data_uncoordinated['process'].loc[year, building, 'Q_feeder_central']['inst-cap'] = 150

    # read and modify microgrid data
    mode = identify_mode(data_uncoordinated)

    mode['tra'] = False

    if not flexible:
        mode['sto'] = False

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data_uncoordinated, cross_scenario_data = create_transdist_data(data_uncoordinated, microgrid_data_initial,
                                                                        cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        # add_reactive_transmission_lines(data_uncoordinated)
        add_reactive_output_ratios(data_uncoordinated)
    mode['tsam'] = True
    mode['tsam_season'] = False

    # run timeseries aggregation method before creating model
    data_uncoordinated, timesteps, weighting_order, cross_scenario_data = run_tsam(data_uncoordinated, noTypicalPeriods,
                                                                                   hoursPerPeriod,
                                                                                   cross_scenario_data,
                                                                                   mode['tsam_season'], uncoordinated)

    # create model and clock process
    tt = time.time()

    prob_uncoordinated = create_model(data_uncoordinated, dt, timesteps, objective, hoursPerPeriod, weighting_order,
                                      dual=False)  # dual false neccessary due to quadratic constraint infeasibility
    print('Elapsed time to build pyomo model: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if lp:
        if not flexible:
            prob_uncoordinated.write(sce + '_uncoordinated_inflexible_tsam_step1' + '.lp',
                                     io_options={'symbolic_solver_labels': True})
        elif not grid_curtailment:
            prob_uncoordinated.write(sce + '_uncoordinated_flexible_tsam_step1' + '.lp',
                                     io_options={'symbolic_solver_labels': True})
        else:
            prob_uncoordinated.write(sce + '_uncoordinated_flexible_grid_curtail_tsam_step1' + '.lp',
                                     io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_mip(optim, logfile=log_filename)
    print("problem sent to solver")

    result = optim.solve(prob_uncoordinated, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'

    if not flexible:
        save(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_inflexible_step1.h5'.format(sce)))
    elif not grid_curtailment:
        save(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_flexible_step1.h5'.format(sce)))
    else:
        save(prob_uncoordinated,
             os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_tsam_step1.h5'.format(sce)))

    if xls:
        if not flexible:
            report(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_inflexible_step1.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)
        elif not grid_curtailment:
            report(prob_uncoordinated, os.path.join(result_dir, '{}_uncoordinated_flexible_step1.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)
        else:
            report(prob_uncoordinated,
                   os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step1.xlsx').format(sce),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)

    ## use the new loads for grid planning
    data_grid_plan = read_input(input_files, year)
    data_grid_plan, cross_scenario_data = scenario(data_grid_plan, cross_scenario_data)
    validate_input(data_grid_plan)
    validate_dc_objective(data_grid_plan, objective)

    # read and modify microgrid data
    mode = identify_mode(data_grid_plan)
    mode['tsam'] = True
    mode['tsam_season'] = False
    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data_grid_plan, cross_scenario_data = create_transdist_data(data_grid_plan, microgrid_data_initial,
                                                                    cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data_grid_plan)
        add_reactive_output_ratios(data_grid_plan)

    # create model and clock process
    tt = time.time()
    # run timeseries aggregation method before creating model
    data_grid_plan, timesteps, weighting_order, cross_scenario_data = run_tsam(data_grid_plan, noTypicalPeriods,
                                                                               hoursPerPeriod,
                                                                               cross_scenario_data, mode['tsam_season'],
                                                                               uncoordinated)
    timesteps = range(0, unaggregated_length + 1)

    # remove heat loads
    # add new electricity loads
    # import pdb;pdb.set_trace()
    ##delete all transmissions
    # data['transmission']['inst-cap'] = 0
    # data['transmission']['cap-up'] = 0

    # delete all storages
    data_grid_plan['storage'] = pd.DataFrame(columns=data_grid_plan['storage'].columns)

    # electricity as stock commodity in each region
    demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns if demand == 'space_heat']
    # import pdb;pdb.set_trace()
    for building in demand_nodes:
        # delete supim timeseries
        data_grid_plan['supim'].drop((building, 'solar'), inplace=True, axis=1)

        # delete time-var-effs for heatpumps and charging stations
        data_grid_plan['eff_factor'].drop((building, 'charging_station'), inplace=True, axis=1)
        data_grid_plan['eff_factor'].drop((building, 'heatpump_air'), inplace=True, axis=1)

        # delete all non-electric demand, shift heating/mobility demand to electricity
        data_grid_plan['demand'].drop((building, 'space_heat'), inplace=True, axis=1)
        data_grid_plan['demand'].drop((building, 'water_heat'), inplace=True, axis=1)
        data_grid_plan['demand'].drop((building, 'mobility'), inplace=True, axis=1)
        data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                prob_uncoordinated._result['tau_pro'].loc[:, year, building, 'import'] \
                + prob_uncoordinated._result['tau_pro'].loc[:, year, building, 'import_hp']
                - prob_uncoordinated._result['tau_pro'].loc[:, year, building, 'feed_in'])
        data_grid_plan['demand'].loc[year, :][(building, 'electricity-reactive')].iloc[1:] = prob_uncoordinated._result[
                                                                                                 'e_pro_out'] \
                                                                                                 .loc[:, year, building,
                                                                                             'Q_feeder_central',
                                                                                             'electricity-reactive']

        # delete all processes besides Q-compensation, import and feed-in
        data_grid_plan['process'].drop((year, building, 'Rooftop PV'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'charging_station'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'Heat_dummy_space'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'Heat_dummy_water'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'heatpump_air'), inplace=True, axis=0)
        data_grid_plan['process'].drop((year, building, 'Dummy_elec_to_hp'), inplace=True, axis=0)

        if not grid_curtailment:
            data_grid_plan['process'].drop((year, building, 'curtailment'), inplace=True, axis=0)
        else:
            data_grid_plan['process'].loc[(year, building, 'curtailment'), 'var-cost'] = 0.064
        data_grid_plan['process'].drop((year, building, 'Slack_heat'), inplace=True, axis=0)

        data_grid_plan['commodity'].drop((year, building, 'electricity_hp', 'Demand'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'space_heat', 'Demand'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'water_heat', 'Demand'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'solar', 'SupIm'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'mobility', 'Demand'), inplace=True, axis=0)
        data_grid_plan['commodity'].drop((year, building, 'common_heat', 'Stock'), inplace=True, axis=0)
        # data_grid_plan['commodity'].drop((year, building, 'CO2','Env'),inplace=True,axis=0)

    # delete all process_commodity for deleted processes
    data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'solar', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'electricity', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'common_heat', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'space_heat', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'common_heat', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'water_heat', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'electricity', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'common_heat', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'charging_station', 'electricity', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'charging_station', 'mobility', 'Out'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Dummy_elec_to_hp', 'electricity', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Dummy_elec_to_hp', 'electricity_hp', 'Out'), inplace=True, axis=0)
    if not grid_curtailment:
        data_grid_plan['process_commodity'].drop((year, 'curtailment', 'electricity', 'In'), inplace=True, axis=0)
    data_grid_plan['process_commodity'].drop((year, 'Slack_heat', 'common_heat', 'Out'), inplace=True, axis=0)

    # data_grid_plan['eff_factor'].drop((building,'charging_station'),inplace=True,axis=1)
    # data_grid_plan['eff_factor'].drop((building,'heatpump_air'),inplace=True,axis=1)
    # data_grid_plan['supim'].drop((building,'solar'),inplace=True,axis=1)

    prob_grid_plan = create_model(data_grid_plan, dt, timesteps, objective, assumelowq, dual=False)

    print('Elapsed time to build the pyomo model of grid planning: %s s' % round(time.time() - tt, 4))

    # write lp file # lp writing needs huge RAM capacities for bigger models
    if lp:
        if not flexible:
            prob_grid_plan.write(sce + '_uncoordinated_inflexible_tsam_step3' + '.lp',
                                 io_options={'symbolic_solver_labels': True})
        elif not grid_curtailment:
            prob_grid_plan.write(sce + '_uncoordinated_flexible_tsam_step3' + '.lp',
                                 io_options={'symbolic_solver_labels': True})
        else:
            prob_grid_plan.write(sce + '_uncoordinated_flexible_grid_curtail_tsam_step3' + '.lp',
                                 io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # set presolve to conservative, as this step takes way too long
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver_mip(optim, logfile=log_filename)
    # set presolve to off, as this step takes way too long
    # optim.set_options("Presolve=0")

    print("problem sent to solver")
    result = optim.solve(prob_grid_plan, tee=True, report_timing=True)

    if not flexible:
        save(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_inflexible_step2.h5'.format(sce)))
    elif not grid_curtailment:
        save(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_flexible_step2.h5'.format(sce)))
    else:
        save(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_flexible_curtail_step2.h5'.format(sce)))

    if xls:
        if not flexible:
            report(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_inflexible_step2.xlsx').format(sce),
                   report_tuples=report_tuples_grid_plan,
                   report_sites_name=report_sites_name)
        elif not grid_curtailment:
            report(prob_grid_plan, os.path.join(result_dir, '{}_uncoordinated_flexible_step2.xlsx').format(sce),
                   report_tuples=report_tuples_grid_plan,
                   report_sites_name=report_sites_name)
        else:
            report(prob_grid_plan,
                   os.path.join(result_dir, '{}_uncoordinated_flexible_grid_curtail_step2.xlsx').format(sce),
                   report_tuples=report_tuples_grid_plan,
                   report_sites_name=report_sites_name)

    return prob_uncoordinated, prob_grid_plan, cross_scenario_data


def get_cross_scenario_data(input_files, solver_name, timesteps, scenario, result_dir, dt,
                            objective, microgrid_files=None, plot_tuples=None, plot_sites_name=None,
                            plot_periods=None, report_tuples=None, report_sites_name=None,
                            cross_scenario_data=None, noTypicalPeriods=None, hoursPerPeriod=None,
                            unaggregated_length=8760, lp=True, xls=True):
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
    data, cross_scenario_data = scenario(data, cross_scenario_data)
    validate_input(data)
    validate_dc_objective(data, objective)

    # read and modify microgrid data
    mode = identify_mode(data)

    if mode['transdist']:
        microgrid_data_initial = []
        for i, microgrid_file in enumerate(microgrid_files):
            microgrid_data_initial.append(read_input(microgrid_file, year))
            validate_input(microgrid_data_initial[i])
        # modify and join microgrid data to model data
        data, cross_scenario_data = create_transdist_data(data, microgrid_data_initial, cross_scenario_data)
    # if distribution network has to be modeled without interface to transmission network
    elif mode['acpf']:
        add_reactive_transmission_lines(data)
        add_reactive_output_ratios(data)
    mode['tsam'] = True
    mode['tsam_season'] = False

    # run timeseries aggregation method before creating model
    data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods, hoursPerPeriod,
                                                                     cross_scenario_data, mode['tsam_season'])

    return cross_scenario_data
