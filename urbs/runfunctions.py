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
import multiprocessing as mp
import os
import random
import numpy as np

import sys
import pdb

class ForkedPdb(pdb.Pdb):
    """A Pdb subclass that may be used
    from a forked multiprocessing child

    """
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

def run_worker(cluster, func_args, lp, xls, tsam, i, result_dir, return_dict,
               react=False, prob_bui=None, prob_grid_plan=None, mode_evu_sperre=None):

    year = date.today().year
    step_no = 1
    data_cluster = get_cluster_data(func_args['get_cluster_data'][0],  # data
                                    cluster)  # cluster

    demand_nodes = [sit for (sit, demand) in data_cluster['demand'].columns if demand == 'space_heat']

    if react:
        #disable slack
        for building in demand_nodes:
            data_cluster['process'].loc[(year, building, 'Slack'), 'cap-up'] = 999
            data_cluster['process'].loc[(year, building, 'Slack'), 'inst-cap'] = 999
            data_cluster['process'].loc[(year, building, 'Slack'), 'var-cost'] = 999
            #slack_heat for water heating only
            slack_heat_pro_com = data_cluster['process_commodity'][
                data_cluster['process_commodity'].index.get_level_values(1) == 'Slack_heat']
            slack_heat_pro_com.rename(index={'common_heat': 'water_heat'}, level=2, inplace=True)

        data_cluster['process_commodity'].drop((year, 'Slack_heat', 'common_heat', 'Out'), inplace=True, axis=0)
        data_cluster['process_commodity'] = pd.concat([data_cluster['process_commodity'], slack_heat_pro_com])


    prob_cluster = create_model(data_cluster,
                                dt=func_args['create_model'][0],
                                timesteps=func_args['create_model'][1],
                                objective=func_args['create_model'][2],
                                weighting_order=func_args['create_model'][3],
                                assumelowq=func_args['create_model'][4],
                                hoursPerPeriod=func_args['create_model'][5],
                                grid_plan_model=func_args['create_model'][6],
                                bui_react_model=react,
                                dual=func_args['create_model'][7],
                                flexible_heat=func_args['create_model'][8])
    #ForkedPdb().set_trace()

    if react:
        step_no = 3
        capacity_variables = ['cap_pro_new', 'cap_decommissioned',
                              'cap_sto_c_new', 'cap_sto_p_new', 'cap_sto_c_decommissioned',
                              'cap_sto_p_decommissioned']

        for cap_var in capacity_variables:
            caps = get_entity(prob_bui, cap_var)
            for var_idx in getattr(prob_cluster, cap_var):
                if ('Slack' not in var_idx) and ('Slack_heat' not in var_idx):
                    getattr(prob_cluster, cap_var)[var_idx].fix(caps[var_idx])
            # write lp file # lp writing needs huge RAM capacities for bigger models

        # fix curtailment
        tau_values = get_entity(prob_grid_plan, 'tau_pro')
        for var_idx in getattr(prob_cluster, 'tau_pro'):
            if var_idx[3] == 'curtailment':
                if var_idx[0] != 0:
                    getattr(prob_cluster, 'tau_pro')[var_idx].fix(tau_values[var_idx])

        # delete single hp rule, not necessary and causes infeasibility
        if mode_evu_sperre:
            del prob_cluster.res_single_heatpump

    if lp:
        prob_cluster.write('{}{}{}{}{}_{}_step{}.lp'.format(func_args['write'][0],
                                                            func_args['write'][1],
                                                            func_args['write'][2],
                                                            func_args['write'][3],
                                                            func_args['write'][4],
                                                            func_args['write'][5], str(step_no)),
                           io_options={'symbolic_solver_labels': True})
    optim = SolverFactory(func_args['SolverFactory'][0])
    if react:
        optim = setup_solver_mip(optim,
                             logfile=os.path.join(result_dir, '{}{}.log').format(func_args['write'][0],
                                                                                 func_args['write'][5]),
                             clusters=True, MIPGap=0.02, TimeLimit=1800)
    else:
        optim = setup_solver_mip(optim,
                             logfile=os.path.join(result_dir, '{}{}.log').format(func_args['write'][0],
                                                                                 func_args['write'][5]),
                             clusters=True, MIPGap=0.05)
    result = optim.solve(prob_cluster, tee=func_args['solve'][0], report_timing=func_args['solve'][0])

    if str(result.solver.termination_condition) == 'infeasibleOrUnbounded':
        print(f"Not feasible!: {str(result.solver.termination_condition)}")
        prob_cluster.write('{}{}{}{}{}_{}_step{}.lp'.format(func_args['write'][0],
                                                            func_args['write'][1],
                                                            func_args['write'][2],
                                                            func_args['write'][3],
                                                            func_args['write'][4],
                                                            func_args['write'][5], str(step_no)),
                           io_options={'symbolic_solver_labels': True})
    # save(prob_cluster, os.path.join(result_dir, '{}{}{}{}_{}_step{}.h5'.format(func_args['write'][0],
    #                                                                         func_args['write'][1],
    #                                                                         func_args['write'][2],
    #                                                                         func_args['write'][3],
    #                                                                         func_args['write'][4], str(step_no))))
    if xls:
        sites = data_cluster['site'].index.get_level_values(1)
        try:
            report_tuples = [(2022, sit, 'electricity') for sit in sites] \
                            + [(2022, sit, 'electricity-reactive') for sit in sites] \
                            + [(2022, sit, 'common_heat') for sit in sites] \
                            + [(2022, sit, 'electricity_hp') for sit in sites] \
                            + [(2022, sit, 'electricity_bev') for sit in sites]

        except:
            report_tuples = [(2022, sit, 'electricity') for sit in sites] \
                            + [(2022, sit, 'electricity-reactive') for sit in sites] \
                            + [(2022, sit, 'common_heat') for sit in sites]
        report_sites_name = {}

        report(prob_cluster[i], os.path.join(result_dir, '{}{}{}{}{}_{}_step{}.xlsx'.format(func_args['write'][0],
                                                                                            func_args['write'][1],
                                                                                            func_args['write'][2],
                                                                                            func_args['write'][3],
                                                                                            func_args['write'][4],
                                                                                            func_args['write'][5],
                                                                                            str(step_no))),
               report_tuples=report_tuples,
               report_sites_name=report_sites_name)

    return_dict[i] = (data_cluster, prob_cluster)
    return (data_cluster, prob_cluster)

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
    result_dir = os.path.join('result', '{}-{}'.format(now, result_name))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    return result_dir


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
        pass
        # optim.options['threads'] = 32
        # optim.options['mip display'] = 5
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
        pass
        optim.options['threads'] = 8
        # optim.options['log'] = "={}".format(logfile)
    return optim


def setup_solver_mip(optim, logfile='solver.log', precision='low', clusters=None, **gurobiparams): #mipgap=None, startnodelimit = None):
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        # optim.set_options("NumericFocus=3")
        # optim.set_options("Crossover=0")
        optim.set_options("Method=3") # ohne method: concurrent optimization. Method=1 -> dual simplex
        optim.set_options("MIPFocus=1")  #
        for (key, value) in gurobiparams.items():
            optim.set_options(f"{key}={value}")
        #if mipgap:
        #    optim.set_options(f"MIPGap={mipgap}")
        #if startnodelimit:
        #    optim.set_options(f"StartNodeLimit={startnodelimit}")
        if precision == 'high':
            optim.set_options("BarConvTol=1e-10")
            optim.set_options("FeasibilityTol=1e-9")
            optim.set_options("OptimalityTol=1e-9")
        if clusters is None:
            pass
            #optim.set_options("Parallel=1")
            #optim.set_options("Threads=20")

        # optim.set_options("NodeMethod=2")
        # optim.set_options("Crossover=2")
        # optim.set_options("NoRelHeurTime=3600") # seconds
        # optim.set_options("Presolve=0")
        # optim.set_options("BarHomogeneous=1")
        # optim.set_options("timelimit=7200")  # seconds

        # optim.set_options("MIPGap=1e-2")  # default = 1e-4
        # optim.set_options("SimplexPricing=2")
        # optim.set_options("DegenMoves=0")
    if optim.name == 'cplexdirect' or optim.name == 'cplex_direct':
        optim.options['threads'] = 32
        if "MIPGap" in gurobiparams.keys():
            optim.options['mip_tolerances_mipgap'] = gurobiparams['MIPGap']
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
                 assumelowq=True,
                 electrification=1,
                 grid_opt=1):
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
        :param assumelowq:
    """
    # uncoordinated = True
    lp=0
    year = date.today().year
    sce = scenario.__name__
    data = read_input(input_files, year)
    data, cross_scenario_data = scenario(data, cross_scenario_data)
    validate_input(data)
    validate_dc_objective(data, objective)

    data['trafo_node'] = data['process'].query("Process == 'import'").index.get_level_values(1)[0]
    data['mainbusbar_node'] = data['process'].query("Process == 'Q_feeder_central'").index.get_level_values(1)[0]

    # read and modify microgrid data
    mode = identify_mode(data)
    coordination_text = '_uncoordinated' if uncoordinated else '_coordinated'
    flexible_text = '_flexible' if flexible else '_inflexible'
    if data['site']['power_price_kw'].dropna().iloc[0] > 0.01:
        capacity_price_text = '_capacity_price'
    else:
        capacity_price_text = ''

    if mode['evu_sperre']:
        regulation_text = '_evu_sperre'
    elif mode['14a_steuve']:
        regulation_text = '_14a_steuve'
    elif mode['14a_steune']:
        regulation_text = '_14a_steune'
    else:
        regulation_text = ''

    if not flexible:
        # delete all storages and flexibility
        mode['sto'] = False
        data = remove_battery(data)
        data = remove_heat_storage(data)
        data = remove_mob_flexibility(data)

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
    add_curtailment_heat(data)
    if mode['evu_sperre'] or mode['14a_steuve']:
        data = add_import_hp_bev_process(data, mode)  # For EVU Sperre and 14a_SteuVE
        data = add_electricity_hp_bev_commodity(data, mode)  # For EVU Sperre and 14a_SteuVE
        # data = add_electricity_hp_bev_usable_commodity(data, mode)  # For EVU Sperre and 14a_SteuVE
        data = modify_hp_bev_processes(data, mode)  # For EVU Sperre and 14a_SteuVE
        # data = add_elec_hp_bev_to_usable_process(data, mode)  # For EVU Sperre and 14a_SteuVE
    if mode['14a_steuve']:
        data = add_elec_to_hp_bev_process(data, mode)  # only for 14a_SteuVE:

    # add dummy process that converts PV electricity to usable HP and BEV

    if not uncoordinated:
        add_hp_bev_flows(data, mode)

    else:
        # uncoordinated optimization of buildings. delete all transmissions
        data['transmission'] = data['transmission'].iloc[0:0]
        mode['tra'] = False
        mode['acpf'] = False

        # add all
        data = distributed_building_specific_import_processes(data, mode)

    if mode['tsam']:
        # run timeseries aggregation method before creating model
        data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods,
                                                                         hoursPerPeriod,
                                                                         cross_scenario_data,
                                                                         mode['tsam_season'],
                                                                         uncoordinated=uncoordinated,
                                                                         uhp=mode['uhp'])
    else:
        weighting_order = None
        data['demand'] = data['demand'][data['demand'].index.get_level_values(1).isin(timesteps)]
        data['supim'] = data['supim'][data['supim'].index.get_level_values(1).isin(timesteps)]
        data['eff_factor'] = data['eff_factor'][data['eff_factor'].index.get_level_values(1).isin(timesteps)]
        data['availability'] = data['availability'][data['availability'].index.get_level_values(1).isin(timesteps)]
        data['buy_sell_price'] = data['buy_sell_price'][
            data['buy_sell_price'].index.get_level_values(1).isin(timesteps)]
        if mode['uhp']:
            data['uhp'] = data['uhp'][
                data['uhp'].index.get_level_values(1).isin(timesteps)]
    # create model and clock process
    tt = time.time()

    #remove heatpumps from some special buildings
    no_heatpump_nodes = ['7014014_001001_007007_00020002_01002',  # Pflegetagesstätte, Stadt-Model
                         '7014014_001001_015015_00080008_01001',  # Schule, Stadt-Model
                         '7091091_001001_001001_00160016_01001',  # Kindergarten, Dorf-Model
                         '7097097_001001_001001_00040004_01001']  # Greenhouse, Land-Model

    data['process'].loc[((data['process'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                         (data['process'].index.get_level_values(2) == 'heatpump_air')), 'cap-up'] = 0
    data['commodity'].loc[((data['commodity'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                         (data['commodity'].index.get_level_values(2) == 'common_heat')), 'price'] = 0.12
    data['commodity'].loc[((data['commodity'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                         (data['commodity'].index.get_level_values(2) == 'common_heat')), 'max'] = np.inf
    data['commodity'].loc[((data['commodity'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                         (data['commodity'].index.get_level_values(2) == 'common_heat')), 'maxperhour'] = np.inf

    if electrification < 1:
        # remove electrification measures randomly
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']

        # unelectrify heat in some buildings
        random.seed(1)
        unelectrified_heat_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1-electrification)))
        pd.DataFrame(unelectrified_heat_nodes).to_excel('unelectrified_heat_buildings.xlsx',index=None)
        data['process'].loc[(year, unelectrified_heat_nodes, 'heatpump_air'), 'cap-up'] = 0
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'price'] = 0.12 # gas price
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'max'] = np.inf
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'maxperhour'] = np.inf

        # dont allow PV in some buildings
        random.seed(2)
        disable_pv_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1-electrification)))
        pd.DataFrame(disable_pv_nodes).to_excel('disabled_pv_nodes.xlsx',index=None)

        data['process'].loc[((data['process'].index.get_level_values(1).isin(disable_pv_nodes)) &
                             (data['process'].index.get_level_values(2).str.startswith('Rooftop PV'))), 'cap-up'] = 0

        # unelectrify some cars
        random.seed(3)
        all_cars = [col for col in data['demand'].columns if col[1].startswith('mobility')]
        unelectrified_cars = random.sample(all_cars, int(len(all_cars) * (1-electrification)))
        pd.DataFrame(unelectrified_cars).to_excel('unelectrified_cars.xlsx',index=None)

        for (site, car) in unelectrified_cars:
            car_idx = car[-1]
            data['process'].loc[(year,site,'charging_station'+car_idx),'inst-cap'] = 0
            data['process'].loc[(year,site,'charging_station'+car_idx),'cap-up'] = 0 # set charging_station capacity to zero
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'price'] = 0.6
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'max'] = np.inf
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'maxperhour'] = np.inf # add stock availabiltiy for mobility commodity

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
    if lp:
        prob.write('{}{}{}{}_step1.lp'.format(sce,
                                              coordination_text,
                                              flexible_text,
                                              regulation_text),
                   io_options={'symbolic_solver_labels': True})

    # solve model and read results
    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # import pdb;pdb.set_trace()
    # warm_start all cables triple
    triple_cable_indices = [(stf, sitin, sitout, tra, com)
                            for (stf, sitin, sitout, tra, com) in prob.tra_tuples_ac
                            if tra.endswith("*3")
                            if com == 'electricity']
    double_cable_indices = [(stf, sitin, sitout, tra, com)
                            for (stf, sitin, sitout, tra, com) in prob.tra_tuples_ac
                            if tra.endswith("*2")
                            if com == 'electricity']
    single_cable_indices = [(stf, sitin, sitout, tra, com)
                            for (stf, sitin, sitout, tra, com) in prob.tra_tuples_ac
                            if tra.endswith("*1")
                            if com == 'electricity']
    largest_ront_indices = [(stf, sitin, sitout, tra, com)
                            for (stf, sitin, sitout, tra, com) in prob.tra_tuples
                            if tra.endswith("2000")
                            if com == 'electricity']
    ront_indices = [(stf, sitin, sitout, tra, com)
                            for (stf, sitin, sitout, tra, com) in prob.tra_tuples
                            if tra.startswith("ront")
                            if com == 'electricity']
    nonlarge_ront_indices = set(ront_indices) - set(largest_ront_indices)
    kont_indices = [(stf, sitin, sitout, tra, com)
                            for (stf, sitin, sitout, tra, com) in prob.tra_tuples
                            if tra.startswith("kont")
                            if com == 'electricity']
    largest_ront_indices = [(stf, sitin, sitout, tra, com)
                            for (stf, sitin, sitout, tra, com) in prob.tra_tuples
                            if tra.endswith("2000")
                            if com == 'electricity']
    for idx in triple_cable_indices:
        prob.cap_tra_unit[idx] = 1
    for idx in double_cable_indices:
        prob.cap_tra_unit[idx] = 0
    for idx in single_cable_indices:
        prob.cap_tra_unit[idx] = 0

    for idx in nonlarge_ront_indices:
        prob.cap_tra_unit[idx] = 0
    for idx in kont_indices:
        prob.cap_tra_unit[idx] = 0

    for idx in largest_ront_indices:
        prob.cap_tra_unit[idx] = 1

    for idx in prob.pro_cap_expands:
        prob.pro_cap_expands[idx] = 1

    if 1:
        optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    else:
        optim = SolverFactory('cplex_direct')
    if not uncoordinated:
        optim = setup_solver_mip(optim, logfile=log_filename, MIPGap=0.05, ConcurrentMIP = 6, Threads=24)#StartNodeLimit = -2,

    print("problem sent to solver")

    # result = optim.solve(prob, tee=True, report_timing=True,  warmstart = True)
    result = optim.solve(prob, tee=True, report_timing=True)
    # assert str(result.solver.termination_condition) == 'optimal'
    grid_text = input_files.split('_')[2]
    paradigm_text = input_files.split('_')[3][:-4]
    if electrification == 1:
        electrification_text = 'full'
    elif electrification == 0.5:
        electrification_text = 'half'
    elif electrification == 0.25:
        electrification_text = 'quarter'
    else:
        electrification_text = 'unknown'
    save(prob, os.path.join(result_dir, '{}_{}_{}_step1.h5'.format(grid_text,
                                                                     paradigm_text,
                                                                     electrification_text)))

    if xls:
        report(prob, os.path.join(result_dir, '{}{}{}{}{}_{}_step1.xlsx'.format(sce,
                                                                             coordination_text,
                                                                             flexible_text,
                                                                             regulation_text,
                                                                             capacity_price_text,
                                                                             str(electrification))),
               report_tuples=report_tuples,
               report_sites_name=report_sites_name)

    if uncoordinated and grid_opt:
        ## use the new loads for grid planning
        data_grid_plan = read_input(input_files, year)
        data_grid_plan, cross_scenario_data = scenario(data_grid_plan, cross_scenario_data)
        validate_input(data_grid_plan)
        validate_dc_objective(data_grid_plan, objective)

        # read and modify microgrid data
        mode = identify_mode(data_grid_plan)
        data['trafo_node'] = data['process'].query("Process == 'import'").index.get_level_values(1)[0]
        data['mainbusbar_node'] = data['process'].query("Process == 'Q_feeder_central'").index.get_level_values(1)[0]

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
        add_hp_bev_flows(data_grid_plan, mode)
        # create model and clock process
        tt = time.time()
        if mode['tsam']:
            # run timeseries aggregation method before creating model
            data_grid_plan, timesteps, weighting_order, cross_scenario_data = run_tsam(data_grid_plan, noTypicalPeriods,
                                                                                       hoursPerPeriod,
                                                                                       cross_scenario_data,
                                                                                       mode['tsam_season'],
                                                                                       uncoordinated=uncoordinated)
        else:
            weighting_order = None
            data_grid_plan['demand'] = data_grid_plan['demand'][
                data_grid_plan['demand'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['supim'] = data_grid_plan['supim'][
                data_grid_plan['supim'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['eff_factor'] = data_grid_plan['eff_factor'][
                data_grid_plan['eff_factor'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['availability'] = data_grid_plan['availability'][
                data_grid_plan['availability'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['buy_sell_price'] = data_grid_plan['buy_sell_price'][
                data_grid_plan['buy_sell_price'].index.get_level_values(1).isin(timesteps)]

        # delete all dsm
        data_grid_plan['dsm'] = pd.DataFrame(columns=data_grid_plan['dsm'].columns)

        # delete all storages
        data_grid_plan['storage'] = pd.DataFrame(columns=data_grid_plan['storage'].columns)

        # electricity as stock commodity in each region
        demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns if demand == 'electricity']

        for building in demand_nodes:
            # delete supim timeseries
            bui_solar_comms = [solcom for (bui, solcom) in data_grid_plan['supim'].columns
                               if solcom.startswith('solar') and bui == building]
            for scs in bui_solar_comms:
                data_grid_plan['supim'].drop((building, scs), inplace=True, axis=1)

            # delete time-var-effs for heatpumps and charging stations
            bui_charging_stations = [cs for (stf, bui, cs) in data_grid_plan['process'].index
                                     if cs.startswith('charging_station') and bui == building
                                     and stf == year]
            for bcs in bui_charging_stations:
                data_grid_plan['eff_factor'].drop((building, bcs), inplace=True, axis=1)

            data_grid_plan['eff_factor'].drop((building, 'heatpump_air'), inplace=True, axis=1)

            # delete all non-electric demand, shift heating/mobility demand to electricity
            data_grid_plan['demand'].drop((building, 'space_heat'), inplace=True, axis=1)
            data_grid_plan['demand'].drop((building, 'water_heat'), inplace=True, axis=1)

            bui_mob_demands = [dem for (bui, dem) in data_grid_plan['demand'].columns
                               if dem.startswith('mobility') and bui == building]
            for mob_demand in bui_mob_demands:
                data_grid_plan['demand'].drop((building, mob_demand), inplace=True, axis=1)

            # EVU_Sperre: if HP electricity is cheaper (heizstromtarif),
            # the grid operator can lock HP electricity 6 hours a day,
            # maximum 2 hours per lock, has to be recovered in the next 2 hours (1 hour recover for 1 hour lock)
            # we need to define electricity_hp as a separate demand for modeling this.

            if mode['evu_sperre'] or mode['14a_steuve']:
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                        - prob._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

                data_grid_plan['demand'][(building, 'electricity_hp')] = copy.deepcopy(
                    data_grid_plan['demand'][(building, 'electricity')])

                data_grid_plan['demand'].loc[year, :][(building, 'electricity_hp')].iloc[1:] = \
                    prob._result['tau_pro'].loc[:, year, building, 'import_hp'].iloc[1:]
                if mode['14a_steuve']:
                    data_grid_plan['demand'][(building, 'electricity_bev')] = copy.deepcopy(
                        data_grid_plan['demand'][(building, 'electricity')])

                    data_grid_plan['demand'].loc[year, :][(building, 'electricity_bev')].iloc[1:] = \
                        prob._result['tau_pro'].loc[:, year, building, 'import_bev'].iloc[1:]

            else:
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                        - prob._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

            # if mode['14a_steune']:
            # data_grid_plan = redefine_elec_demand_for_steune(data_grid_plan, prob)
            # data_grid_plan = add_elec_to_elec_usable_process(data_grid_plan)

            data_grid_plan['demand'].loc[year, :][(building, 'electricity-reactive')].iloc[1:] = \
                prob._result['e_pro_out'] \
                    .loc[:, year, building, 'Q_feeder_central', 'electricity-reactive']

            # delete all processes besides Q-compensation, import and feed-in
            bui_rooftop_pvs = [pv for (stf, bui, pv) in data_grid_plan['process'].index
                               if pv.startswith('Rooftop PV') and bui == building
                               and stf == year]
            for pvs in bui_rooftop_pvs:
                data_grid_plan['process'].drop((year, building, pvs), inplace=True, axis=0)

            data_grid_plan['process'].drop((year, building, 'Heat_dummy_space'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'Heat_dummy_water'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'heatpump_air'), inplace=True, axis=0)

            bui_charging_stations = [cs for (stf, bui, cs) in data['process'].index
                                     if cs.startswith('charging_station') and bui == building and stf == year]
            for bcs in bui_charging_stations:
                data_grid_plan['process'].drop((year, building, bcs), inplace=True, axis=0)

            if not grid_curtailment:
                data_grid_plan['process'].drop((year, building, 'curtailment'), inplace=True, axis=0)
            else:
                data_grid_plan['process'].loc[(year, building, 'curtailment'), 'var-cost'] = \
                    data_grid_plan['buy_sell_price']['electricity_feed_in'].values[-1]
            data_grid_plan['process'].drop((year, building, 'Slack_heat'), inplace=True, axis=0)

            data_grid_plan['commodity'].drop((year, building, 'space_heat', 'Demand'), inplace=True, axis=0)
            data_grid_plan['commodity'].drop((year, building, 'water_heat', 'Demand'), inplace=True, axis=0)
            bui_solar_comms = [solcom for (bui, solcom) in data_grid_plan['supim'].columns
                               if solcom.startswith('solar') and bui == building]
            for scs in bui_solar_comms:
                data_grid_plan['commodity'].drop((year, building, scs, 'SupIm'), inplace=True, axis=0)

            bui_mob_commodities = [com for (stf, sit, com, typ) in data_grid_plan['commodity'].index
                                   if com.startswith('mobility') and sit == building]
            for com in bui_mob_commodities:
                data_grid_plan['commodity'].drop((year, building, com, 'Demand'), inplace=True, axis=0)
            data_grid_plan['commodity'].drop((year, building, 'common_heat', 'Stock'), inplace=True, axis=0)

        if grid_curtailment:
            grid_curtailment = set_curtailment_limits(data_grid_plan)

        # set very small demand values to zero
        data_grid_plan['demand'][(data_grid_plan['demand'] > 0) & (data_grid_plan['demand']<1e-6)] = 0
        #import pdb;
        #pdb.set_trace()
        # delete all process_commodity for deleted processes
        # data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'solar', 'In'), inplace=True, axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'electricity', 'Out'), inplace=True, axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'electricity-reactive', 'Out'), inplace=True,
        #                                         axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'common_heat', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'space_heat', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'common_heat', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'water_heat', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'electricity', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'common_heat', 'Out'), inplace=True, axis=0)

        unique_charging_stations = [ucs for (stf, ucs, com, direction) in data_grid_plan['process_commodity'].index
                                    if ucs.startswith('charging_station') and direction == 'In']
        for ucs in unique_charging_stations:
            data_grid_plan['process_commodity'].drop((year, ucs, 'electricity', 'In'), inplace=True, axis=0)
            data_grid_plan['process_commodity'].drop((year, ucs, 'mobility' + ucs[16:], 'Out'), inplace=True, axis=0)

        if not grid_curtailment:
            data_grid_plan['process_commodity'].drop((year, 'curtailment', 'electricity', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Slack_heat', 'common_heat', 'Out'), inplace=True, axis=0)

        # NEW: no cost for electricity import and feed-in (so the significance of grid costs dominates)
        data_grid_plan['buy_sell_price'] = data_grid_plan['buy_sell_price'] * 0

        if mode['evu_sperre'] or mode['14a_steuve']:
            # data_grid_plan = add_electricity_hp_bev_usable_commodity(data_grid_plan, mode,
            #                                                         comtype='Demand')
            data_grid_plan = add_electricity_hp_bev_commodity(data_grid_plan, mode,
                                                              comtype=['Stock', 'Demand'])
            # data_grid_plan = add_elec_hp_bev_to_usable_process(data_grid_plan, mode)

            data_grid_plan = add_import_hp_bev_process(data_grid_plan, mode)

        if mode['evu_sperre'] or mode['14a_steuve'] or mode['14a_steune']:
            data_grid_plan = add_hp_bev_regulation_process(data_grid_plan, data, mode, var_cost=0.0001)

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
            prob_grid_plan.write('{}{}{}{}_{}_step2.lp'.format(sce,
                                                            coordination_text,
                                                            flexible_text,
                                                            regulation_text,
                                                            str(electrification)),
                                 io_options={'symbolic_solver_labels': True})

        # refresh time stamp string and create filename for logfile
        log_filename = os.path.join(result_dir, '{}.log').format(sce)

        # set presolve to conservative, as this step takes way too long
        optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...

        optim = setup_solver_mip(optim, logfile=log_filename, MIPGap=0.05)

        # set presolve to off, as this step takes way too long
        # optim.set_options("Presolve=0")

        print("problem sent to solver")
        result = optim.solve(prob_grid_plan, tee=True, report_timing=True)

        grid_text = input_files.split('_')[2]
        paradigm_text = input_files.split('_')[3][:-4]
        if electrification == 1:
            electrification_text = 'full'
        elif electrification == 0.5:
            electrification_text = 'half'
        elif electrification == 0.25:
            electrification_text = 'quarter'
        else:
            electrification_text = 'unknown'
        save(prob, os.path.join(result_dir, '{}_{}_{}_step2.h5'.format(grid_text,
                                                                       paradigm_text,
                                                                       electrification_text)))

        if xls:
            report(prob_grid_plan, os.path.join(result_dir, '{}{}{}{}_{}_step2.xlsx'.format(sce,
                                                                                         coordination_text,
                                                                                         flexible_text,
                                                                                         str(electrification),
                                                                                         regulation_text)),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)

        if mode['evu_sperre'] or mode['14a_steuve'] or mode['14a_steune']:
            print("Third step, for the reaction of households to the NB regulations")
            data_hp_react = copy.deepcopy(data)
            for building in demand_nodes:
                #make slack way more expensive than temperature reduction
                data['process'].loc[(year, building, 'Slack'),'var-cost'] = 100
                data['process'].loc[(year, building, 'Slack_heat'),'var-cost'] = 100

            if mode['evu_sperre']:
                for building in demand_nodes:
                    data_hp_react['eff_factor'][(building, 'import_hp')] = 1 - \
                                                                           prob_grid_plan._result['on_off'].loc[:, :,
                                                                           building,
                                                                           'hp_lock'].values
            if mode['14a_steuve']:
                for building in demand_nodes:
                    # wherever regulation is used, reduce the import capacity to the level allowed by the grid operator.
                    data_hp_react['availability'][(building, 'heatpump_air')] = data_hp_react['availability'][
                        ('Trafostation_OS', 'import')].values
                    data_hp_react['availability'][(building, 'heatpump_air')].iloc[1:] = \
                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                         'electricity_hp'] <= 0) * 1 + \
                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                         'electricity_hp'] > 0) * \
                        (data_grid_plan['demand'][(building, 'electricity_hp')].iloc[1:] - prob_grid_plan._result[
                                                                                               'e_pro_out']. \
                         loc[:, :, building, 'hp_14a_steuve_regulate', 'electricity_hp'].values) / \
                        prob._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0]

                    bui_charging_stations = [cs for (stf, bui, cs) in data['process'].index
                                             if cs.startswith('charging_station') and bui == building
                                             and stf == year]
                    for cs in bui_charging_stations:
                        data_hp_react['availability'][(building, cs)] = data_hp_react['availability'][
                            ('Trafostation_OS', 'import')].values
                        data_hp_react['availability'][(building, cs)].iloc[1:] = \
                            (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'bev_14a_steuve_regulate',
                             'electricity_bev'] <= 0) * 1 + \
                            (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'bev_14a_steuve_regulate',
                             'electricity_bev'] > 0) * \
                            (data_grid_plan['demand'][(building, 'electricity_bev')].iloc[1:] - prob_grid_plan._result[
                                                                                                    'e_pro_out']. \
                             loc[:, :, building, 'bev_14a_steuve_regulate', 'electricity_bev'].values) / \
                            prob._result['cap_pro'].loc[:, building, cs].values[0] / len(bui_charging_stations)

            if mode['14a_steune']:
                for building in demand_nodes:
                    data_hp_react['availability'][(building, 'import')] = data_hp_react['availability'][
                        ('Trafostation_OS', 'import')].values
                    data_hp_react['availability'][(building, 'import')].iloc[1:] = \
                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'elec_14a_steune_regulate',
                         'electricity'] <= 0) * 1 + \
                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'elec_14a_steune_regulate',
                         'electricity'] > 0) * \
                        (data_grid_plan['demand'][(building, 'electricity')].iloc[1:] - prob_grid_plan._result[
                                                                                            'e_pro_out']. \
                         loc[:, :, building, 'elec_14a_steune_regulate', 'electricity'].values) / \
                        prob._result['cap_pro'].loc[:, building, 'import'].values[0]


            prob_hp_react = create_model(data_hp_react, dt=dt,
                                         timesteps=timesteps,
                                         objective='cost',
                                         weighting_order=weighting_order,
                                         assumelowq=assumelowq,
                                         hoursPerPeriod=hoursPerPeriod,
                                         grid_plan_model=False,
                                         bui_react_model=False,
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

            # fix curtailment
            tau_values = get_entity(prob_grid_plan, 'tau_pro')
            for var_idx in getattr(prob_hp_react, 'tau_pro'):
                if var_idx[3] == 'curtailment':
                    if var_idx[0] != 0:
                        getattr(prob_hp_react, 'tau_pro')[var_idx].fix(tau_values[var_idx])

            # delete single hp rule, not necessary and causes infeasibility
            if mode['evu_sperre']:
                del prob_hp_react.res_single_heatpump

            if lp:
                prob_hp_react.write('{}{}{}{}_step3.lp'.format(sce,
                                                               coordination_text,
                                                               flexible_text,
                                                               regulation_text),
                                    io_options={'symbolic_solver_labels': True})

            optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
            optim = setup_solver_mip(optim, logfile=log_filename, precision='high')
            result = optim.solve(prob_hp_react, tee=True, report_timing=True)

            grid_text = input_files.split('_')[2]
            paradigm_text = input_files.split('_')[3][:-4]
            if electrification == 1:
                electrification_text = 'full'
            elif electrification == 0.5:
                electrification_text = 'half'
            elif electrification == 0.25:
                electrification_text = 'quarter'
            else:
                electrification_text = 'unknown'
            save(prob, os.path.join(result_dir, '{}_{}_{}_step3.h5'.format(grid_text,
                                                                           paradigm_text,
                                                                           electrification_text)))

            if xls:
                report(prob_hp_react, os.path.join(result_dir, '{}{}{}{}_{}_step3.xlsx'.format(sce,
                                                                                            coordination_text,
                                                                                            flexible_text,
                                                                                            regulation_text,
                                                                                            str(electrification))),
                       report_tuples=report_tuples,
                       report_sites_name=report_sites_name)
            return prob, prob_grid_plan, prob_hp_react, cross_scenario_data

    if uncoordinated and grid_opt:
        return prob, prob_grid_plan, cross_scenario_data
    else:
        return prob, cross_scenario_data


def run_lvds_opt(input_files, solver_name, timesteps, scenario, result_dir, dt,
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
                          assumelowq=True,
                          clusters=None,
                          electrification=1,
                          grid_opt=1,
                          bev_ratio=1,
                          hp_ratio=1,
                          pv_ratio=1,
                          vartariff=0):
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
        :param assumelowq:
    """
    lp=0

    # uncoordinated = True
    year = date.today().year
    sce = scenario.__name__
    data = read_input(input_files, year)
    data, cross_scenario_data = scenario(data, cross_scenario_data)
    validate_input(data)
    validate_dc_objective(data, objective)

    if clusters:
        clusters = [lst for lst in clusters if len(lst) > 0]

    coordination_text = '_uncoordinated' if uncoordinated else '_coordinated'
    flexible_text = '_flexible' if flexible else '_inflexible'

    # read and modify microgrid data
    mode = identify_mode(data)
    tsam_text = '_tsam' if mode['tsam'] else ''

    if mode['evu_sperre']:
        regulation_text = '_evu_sperre'
    elif mode['14a_steuve']:
        regulation_text = '_14a_steuve'
    elif mode['14a_steune']:
        regulation_text = '_14a_steune'
    else:
        regulation_text = ''

    if data['site']['power_price_kw'].dropna().iloc[0] > 0.01:
        capacity_price_text = '_capacity_price'
    else:
        capacity_price_text = ''
    if not flexible:
        # delete all storages and flexibility

        data = remove_battery(data)
        data = remove_heat_storage(data)
        if not mode['14a_steuve']: # let mobility flexibility in case of 14a steuve while inflexible (to avoid infeasibility)
            data = remove_mob_flexibility(data)
            mode['sto'] = False

    data['trafo_node'] = data['process'].query("Process == 'import'").index.get_level_values(1)[0]
    data['mainbusbar_node'] = data['process'].query("Process == 'Q_feeder_central'").index.get_level_values(1)[0]

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
    add_curtailment_heat(data)
    if mode['evu_sperre'] or mode['14a_steuve']:
        data = add_import_hp_bev_process(data, mode)  # For EVU Sperre and 14a_SteuVE
        data = add_electricity_hp_bev_commodity(data, mode)  # For EVU Sperre and 14a_SteuVE
        # data = add_electricity_hp_bev_usable_commodity(data, mode)  # For EVU Sperre and 14a_SteuVE
        data = modify_hp_bev_processes(data, mode)  # For EVU Sperre and 14a_SteuVE
        # data = add_elec_hp_bev_to_usable_process(data, mode)  # For EVU Sperre and 14a_SteuVE
    if mode['14a_steuve']:
        data = add_elec_to_hp_bev_process(data, mode)  # only for 14a_SteuVE:

    # add dummy process that converts PV electricity to usable HP and BEV

    if not uncoordinated:
        if mode['evu_sperre'] or mode['14a_steuve']:
            add_hp_bev_flows(data, mode)
    else:
        # uncoordinated optimization of buildings. delete all transmissions
        data['transmission'] = data['transmission'].iloc[0:0]
        mode['tra'] = False
        mode['acpf'] = False

        # add all
        data = distributed_building_specific_import_processes(data, mode)

    if mode['tsam']:
        # run timeseries aggregation method before creating model
        data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods,
                                                                         hoursPerPeriod,
                                                                         cross_scenario_data,
                                                                         mode['tsam_season'],
                                                                         uncoordinated=uncoordinated,
                                                                         uhp=mode['uhp'])
    else:
        weighting_order = None
        data['demand'] = data['demand'][data['demand'].index.get_level_values(1).isin(timesteps)]
        data['supim'] = data['supim'][data['supim'].index.get_level_values(1).isin(timesteps)]
        data['eff_factor'] = data['eff_factor'][data['eff_factor'].index.get_level_values(1).isin(timesteps)]
        data['availability'] = data['availability'][data['availability'].index.get_level_values(1).isin(timesteps)]
        data['buy_sell_price'] = data['buy_sell_price'][
            data['buy_sell_price'].index.get_level_values(1).isin(timesteps)]
        if mode['uhp']:
            data['uhp'] = data['uhp'][
                data['uhp'].index.get_level_values(1).isin(timesteps)]
    # create model and clock process
    tt = time.time()

    # remove heatpumps from some special buildings
    no_heatpump_nodes = ['7014014_001001_007007_00020002_01002',  # Pflegetagesstätte, Stadt-Model
                         '7014014_001001_015015_00080008_01001',  # Schule, Stadt-Model
                         '7091091_001001_001001_00160016_01001',  # Kindergarten, Dorf-Model
                         '7097097_001001_001001_00040004_01001']  # Greenhouse, Land-Model

    data['process'].loc[((data['process'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                         (data['process'].index.get_level_values(2) == 'heatpump_air')), 'cap-up'] = 0
    data['commodity'].loc[((data['commodity'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                           (data['commodity'].index.get_level_values(2) == 'common_heat')), 'price'] = 0.12
    data['commodity'].loc[((data['commodity'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                           (data['commodity'].index.get_level_values(2) == 'common_heat')), 'max'] = np.inf
    data['commodity'].loc[((data['commodity'].index.get_level_values(1).isin(no_heatpump_nodes)) &
                           (data['commodity'].index.get_level_values(2) == 'common_heat')), 'maxperhour'] = np.inf


    if electrification < 1:
        # remove electrification measures randomly
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']

        # unelectrify heat in some buildings
        random.seed(1)
        unelectrified_heat_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1-electrification)))
        pd.DataFrame(unelectrified_heat_nodes).to_excel('unelectrified_heat_buildings.xlsx',index=None)
        data['process'].loc[(year, unelectrified_heat_nodes, 'heatpump_air'), 'cap-up'] = 0
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'price'] = 0.12 # gas price
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'max'] = np.inf
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'maxperhour'] = np.inf

        # dont allow PV in some buildings
        random.seed(2)
        disable_pv_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1-electrification)))
        pd.DataFrame(disable_pv_nodes).to_excel('disabled_pv_nodes.xlsx',index=None)

        data['process'].loc[((data['process'].index.get_level_values(1).isin(disable_pv_nodes)) &
                             (data['process'].index.get_level_values(2).str.startswith('Rooftop PV'))), 'cap-up'] = 0

        # unelectrify some cars
        random.seed(3)
        all_cars = [col for col in data['demand'].columns if col[1].startswith('mobility')]
        unelectrified_cars = random.sample(all_cars, int(len(all_cars) * (1-electrification)))
        pd.DataFrame(unelectrified_cars).to_excel('unelectrified_cars.xlsx',index=None)

        for (site, car) in unelectrified_cars:
            car_idx = car[-1]
            data['process'].loc[(year,site,'charging_station'+car_idx),'inst-cap'] = 0
            data['process'].loc[(year,site,'charging_station'+car_idx),'cap-up'] = 0 # set charging_station capacity to zero
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'price'] = 0.6 #60 cent for public charging
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'max'] = np.inf
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'maxperhour'] = np.inf # add stock availabiltiy for mobility commodity

    if pv_ratio < 1:
        random.seed(2)

        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
        # dont allow PV in some buildings
        disable_pv_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1-pv_ratio)))
        pd.DataFrame(disable_pv_nodes).to_excel('disabled_pv_nodes.xlsx',index=None)
        data['process'].loc[((data['process'].index.get_level_values(1).isin(disable_pv_nodes)) &
                             (data['process'].index.get_level_values(2).str.startswith('Rooftop PV'))), 'cap-up'] = 0
    if bev_ratio < 1:
        # unelectrify some cars
        random.seed(3)
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']

        all_cars = [col for col in data['demand'].columns if col[1].startswith('mobility')]
        unelectrified_cars = random.sample(all_cars, int(len(all_cars) * (1-bev_ratio)))
        pd.DataFrame(unelectrified_cars).to_excel('unelectrified_cars.xlsx',index=None)

        for (site, car) in unelectrified_cars:
            car_idx = car[-1]
            data['process'].loc[(year,site,'charging_station'+car_idx),'inst-cap'] = 0
            data['process'].loc[(year,site,'charging_station'+car_idx),'cap-up'] = 0 # set charging_station capacity to zero
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'price'] = 0.6 #60 cent for public charging
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'max'] = np.inf
            data['commodity'].loc[(year,site,'mobility'+car_idx,'Demand'),'maxperhour'] = np.inf # add stock availabiltiy for mobility commodity
    if hp_ratio < 1:

        # unelectrify heat in some buildings
        random.seed(1)
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']

        unelectrified_heat_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1-hp_ratio)))
        pd.DataFrame(unelectrified_heat_nodes).to_excel('unelectrified_heat_buildings.xlsx',index=None)
        data['process'].loc[(year, unelectrified_heat_nodes, 'heatpump_air'), 'cap-up'] = 0
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'price'] = 0.12 # gas price
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'max'] = np.inf
        data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'maxperhour'] = np.inf

    if vartariff > 0:
        random.seed(4)
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
        vartariff_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (vartariff)))

        # rename import to import_var process for those nodes
        for building in vartariff_nodes:
            import_pro =  data['process'][
            data['process'].index.get_level_values(2) == 'import']
            import_pro = import_pro[import_pro.index.get_level_values(1) == building]
            import_pro = import_pro.copy(deep=True)
            import_pro.rename(index={'import':'import_var'},level=2,inplace=True)
            data['process'].drop((year, building, 'import'),inplace=True, axis=0)
            data['process'] = pd.concat([data['process'], import_pro])

        # rename commodities "electricity_import" to "electricity_import_var" for those nodes
        for building in vartariff_nodes:
            electricity_import_com =  data['commodity'][
            data['commodity'].index.get_level_values(2) == 'electricity_import']
            electricity_import_com = electricity_import_com[electricity_import_com.index.get_level_values(1) == building]
            electricity_import_com = electricity_import_com.copy(deep=True)
            electricity_import_com.rename(index={'electricity_import':'electricity_import_var'},level=2,inplace=True)
            data['commodity'].drop((year, building, 'electricity_import', 'Buy'),inplace=True, axis=0)
            data['commodity'] = pd.concat([data['commodity'], electricity_import_com])
        # add process-commodity for import_var (same as import, just commodity different)
        import_var_pro_com = data['process_commodity'][
            data['process_commodity'].index.get_level_values(1) == 'import']
        import_var_pro_com = import_var_pro_com.copy(deep=True)
        import_var_pro_com.rename(index={'electricity_import': 'electricity_import_var'}, level=2, inplace=True)
        import_var_pro_com.rename(index={'import': 'import_var'}, level=1, inplace=True)
        data['process_commodity'] = pd.concat([data['process_commodity'], import_var_pro_com])

    #import pdb;pdb.set_trace()
    # data_cluster = {}
    # prob_cluster = {}
    #
    # # parallel
    # procs = []
    # manager = mp.Manager()
    # return_dict = manager.dict()
    # for i, cluster in enumerate(clusters):
    #     proc = mp.Process(target=run_worker,
    #                       args=(cluster,
    #                             dict(get_cluster_data=[data],
    #                                  create_model=[dt,  # dt
    #                                                timesteps,  # timesteps
    #                                                'cost',  # objective
    #                                                weighting_order,  # weighting_order
    #                                                assumelowq,  # assumelowq
    #                                                hoursPerPeriod,  # hoursPerPeriod
    #                                                False,  # grid_plan_model
    #                                                False],
    #                                  write=[sce,
    #                                         coordination_text,
    #                                         flexible_text,
    #                                         regulation_text,
    #                                         capacity_price_text,
    #                                         str(i)],
    #                                  SolverFactory=[solver_name],
    #                                  solve=[True,  # tee
    #                                         True]),  # report timing
    #                             lp,
    #                             xls,
    #                             mode['tsam'],
    #                             i,
    #                             result_dir,
    #                             return_dict),
    #                       )  # dual
    #     procs.append(proc)
    #     proc.start()
    #
    # for proc in procs:
    #     proc.join()
    #
    # for i, cluster in enumerate(clusters):
    #     data_cluster[i] = return_dict[i][0]
    #     prob_cluster[i] = return_dict[i][1]
    #     prob_cluster[i]._result = create_result_cache(prob_cluster[i])
    #
    # save(prob_cluster, os.path.join(result_dir, '{}{}{}{}{}_step1.h5'.format(sce,
    #                                                                          coordination_text,
    #                                                                          flexible_text,
    #                                                                          regulation_text, capacity_price_text
    #                                                                          )), parallel=True)

    # set power_price and adjust import price slightly
    if data['global_prop'].loc[pd.IndexSlice[:, 'power_price_kw'], 'value'].iloc[0] > 0:
        kwh_per_peakkw = 1000
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
        for building in demand_nodes:
            for i, cluster in enumerate(clusters):
                if building in cluster:
                    data['site'].loc[year, building]['power_price_kw'] = \
                    data['global_prop'].loc[pd.IndexSlice[:, 'power_price_kw'], 'value'].iloc[0]
        data['buy_sell_price']['electricity_import'] = data['buy_sell_price']['electricity_import'] - \
                                                       data['global_prop'].loc[
                                                           pd.IndexSlice[:, 'power_price_kw'], 'value'].iloc[
                                                           0] / kwh_per_peakkw
        # if data['global_prop'].loc[pd.IndexSlice[:,'power_price_kw'],'value'].iloc[0] > 0:
        #
        #    demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
        #    for building in demand_nodes:
        #        for i, cluster in enumerate(clusters):
        #            if building in cluster:
        #                total_import_spending = (prob_cluster[i]._result['e_pro_in'].loc[:,year,building,'import','electricity_import'] * \
        #                                        data_cluster[i]['buy_sell_price'].loc[year, :]['electricity_import'] * \
        #                                        data_cluster[i]['type period'].loc[year, :]['weight_typeperiod']).sum()

        #               peak_injection = prob_cluster[i]._result['peak_injection'].loc[year,building]

        #                data['site'].loc[year, building]['power_price_kw'] = total_import_spending * \
        #                                                                    data['global_prop'].loc[pd.IndexSlice[:,'power_price_kw'],'value'].iloc[0]\
        #                                                                    / peak_injection
        #    data['buy_sell_price']['electricity_import'] = \
        #        data_cluster[i]['buy_sell_price']['electricity_import'] * \
        #        (1 - data['global_prop'].loc[pd.IndexSlice[:,'power_price_kw'],'value'].iloc[0])

    data_cluster = {}
    prob_cluster = {}
    #sequential
    return_dict = {}
    for i, cluster in enumerate(clusters):
        return_dict[i] = run_worker(cluster,
                                    dict(get_cluster_data=[data],
                                         create_model=[dt,  # dt
                                                       timesteps,  # timesteps
                                                       'cost',  # objective
                                                       weighting_order,  # weighting_order
                                                       assumelowq,  # assumelowq
                                                       hoursPerPeriod,  # hoursPerPeriod
                                                       False,  # grid_plan_model
                                                       False,  # dual
                                                       flexible],
                                         write=[sce,
                                                coordination_text,
                                                flexible_text,
                                                regulation_text,
                                                capacity_price_text,
                                                str(i)],
                                         SolverFactory=[solver_name],
                                         solve=[True,  # tee
                                                True]),  # report timing
                                    lp,
                                    xls,
                                    mode['tsam'],
                                    i,
                                    result_dir,
                                    return_dict,
                                    )  # mode_evu_sperre
        # dual


    #parallel
    # procs = []
    # manager = mp.Manager()
    # return_dict = manager.dict()
    #
    # for i, cluster in enumerate(clusters):
    #     proc = mp.Process(target=run_worker,
    #                       args=(cluster,
    #                             dict(get_cluster_data=[data],
    #                                  create_model=[dt,  # dt
    #                                                timesteps,  # timesteps
    #                                                'cost',  # objective
    #                                                weighting_order,  # weighting_order
    #                                                assumelowq,  # assumelowq
    #                                                hoursPerPeriod,  # hoursPerPeriod
    #                                                False,  # grid_plan_model
    #                                                False, # dual
    #                                                flexible],
    #                                  write=[sce,
    #                                         coordination_text,
    #                                         flexible_text,
    #                                         regulation_text,
    #                                         capacity_price_text,
    #                                         str(i)],
    #                                  SolverFactory=[solver_name],
    #                                  solve=[True,  # tee
    #                                         True]),  # report timing
    #                             lp,
    #                             xls,
    #                             mode['tsam'],
    #                             i,
    #                             result_dir,
    #                             return_dict),
    #                       )  # dual
    #     procs.append(proc)
    #     proc.start()
    #
    # for proc in procs:
    #     proc.join()
    #
    for i, cluster in enumerate(clusters):
        data_cluster[i] = return_dict[i][0]
        prob_cluster[i] = return_dict[i][1]

    grid_text = input_files.split('_')[2]
    paradigm_text = input_files.split('_')[3][:-4]
    if electrification == 1:
        electrification_text = 'full'
    elif electrification == 0.5:
        electrification_text = 'half'
    elif electrification == 0.25:
        electrification_text = 'quarter'
    else:
        electrification_text = 'unknown'
    save(prob_cluster, os.path.join(result_dir, '{}_{}_{}_step1.h5'.format(grid_text,
                                                                     paradigm_text,
                                                                     electrification_text)), parallel=True)
    #
    #        }))
    # sequential
    # for i, cluster in enumerate(clusters):
    #     print('creating data for cluster {}, step 1'.format(str(i + 1)))
    #     data_cluster[i] = get_cluster_data(data, cluster)
    #     print('creating prob for cluster {}, step 1'.format(str(i + 1)))
    #     if mode['tsam']:
    #         prob_cluster[i] = create_model(data_cluster[i], dt=dt,
    #                                        timesteps=timesteps,
    #                                        objective='cost',
    #                                        weighting_order=weighting_order,
    #                                        assumelowq=assumelowq,
    #                                        hoursPerPeriod=hoursPerPeriod,
    #                                        grid_plan_model=False,
    #                                        dual=False)
    #     else:
    #         prob_cluster[i] = create_model(data_cluster[i], dt=dt,
    #                                        timesteps=timesteps,
    #                                        objective='cost',
    #                                        # weighting_order=weighting_order,
    #                                        assumelowq=assumelowq,
    #                                        # hoursPerPeriod=hoursPerPeriod,
    #                                        grid_plan_model=False,
    #                                        dual=False)
    #     if lp:
    #         prob_cluster[i].write('{}{}{}{}_{}_step1.lp'.format(sce,
    #                                                             coordination_text,
    #                                                             flexible_text,
    #                                                             regulation_text,
    #                                                             str(i)),
    #                               io_options={'symbolic_solver_labels': True})
    #     # refresh time stamp string and create filename for logfile
    #     log_filename = os.path.join(result_dir, '{}{}.log').format(sce, str(i))
    #
    #     # solve model and read results
    #     optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    #     optim = setup_solver_mip(optim, logfile=log_filename, clusters=clusters)
    #     print("problem sent to solver")
    #
    #     print('solving cluster {}, step 1'.format(str(i + 1)))
    #     result = optim.solve(prob_cluster[i], tee=True, report_timing=True)
    #     # assert str(result.solver.termination_condition) == 'optimal'
    #
    #     save(prob_cluster[i], os.path.join(result_dir, '{}{}{}{}_{}_step1.h5'.format(sce,
    #                                                                                  coordination_text,
    #                                                                                  flexible_text,
    #                                                                                  regulation_text,
    #                                                                                  str(i))))
    #
    #     if xls:
    #         report(prob_cluster[i], os.path.join(result_dir, '{}{}{}{}_{}_step1.xlsx'.format(sce,
    #                                                                                          coordination_text,
    #                                                                                          flexible_text,
    #                                                                                          regulation_text, str(i))),
    #                report_tuples=report_tuples,
    #                report_sites_name=report_sites_name)

    ## use the new loads for grid planning
    if grid_opt:
        data_grid_plan = read_input(input_files, year)
        data_grid_plan, cross_scenario_data = scenario(data_grid_plan, cross_scenario_data)
        validate_input(data_grid_plan)
        validate_dc_objective(data_grid_plan, objective)

        # read and modify microgrid data
        mode = identify_mode(data_grid_plan)
        data_grid_plan['trafo_node'] = data_grid_plan['process'].query("Process == 'import'").index.get_level_values(1)[0]
        data_grid_plan['mainbusbar_node'] = \
        data_grid_plan['process'].query("Process == 'Q_feeder_central'").index.get_level_values(1)[0]

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
        add_hp_bev_flows(data_grid_plan, mode)

        # create model and clock process
        tt = time.time()
        if mode['tsam']:
            # run timeseries aggregation method before creating model
            data_grid_plan, timesteps, weighting_order, cross_scenario_data = run_tsam(data_grid_plan, noTypicalPeriods,
                                                                                       hoursPerPeriod,
                                                                                       cross_scenario_data,
                                                                                       mode['tsam_season'],
                                                                                       uncoordinated=uncoordinated)
        else:
            weighting_order = None
            data_grid_plan['demand'] = data_grid_plan['demand'][
                data_grid_plan['demand'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['supim'] = data_grid_plan['supim'][
                data_grid_plan['supim'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['eff_factor'] = data_grid_plan['eff_factor'][
                data_grid_plan['eff_factor'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['availability'] = data_grid_plan['availability'][
                data_grid_plan['availability'].index.get_level_values(1).isin(timesteps)]
            data_grid_plan['buy_sell_price'] = data_grid_plan['buy_sell_price'][
                data_grid_plan['buy_sell_price'].index.get_level_values(1).isin(timesteps)]

        # delete all dsm
        data_grid_plan['dsm'] = pd.DataFrame(columns=data_grid_plan['dsm'].columns)

        # delete all storages
        data_grid_plan['storage'] = pd.DataFrame(columns=data_grid_plan['storage'].columns)

        demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns if demand == 'space_heat']

        for building in demand_nodes:
            # delete supim timeseries
            bui_solar_comms = [solcom for (bui, solcom) in data_grid_plan['supim'].columns
                               if solcom.startswith('solar') and bui == building]
            for scs in bui_solar_comms:
                data_grid_plan['supim'].drop((building, scs), inplace=True, axis=1)
            # data_grid_plan['supim'].drop((building, 'solar'), inplace=True, axis=1)

            # delete time-var-effs for heatpumps and charging stations
            bui_charging_stations = [cs for (stf, bui, cs) in data_grid_plan['process'].index
                                     if cs.startswith('charging_station') and bui == building
                                     and stf == year]
            for bcs in bui_charging_stations:
                data_grid_plan['eff_factor'].drop((building, bcs), inplace=True, axis=1)

            data_grid_plan['eff_factor'].drop((building, 'heatpump_air'), inplace=True, axis=1)

            # delete all non-electric demand, shift heating/mobility demand to electricity
            data_grid_plan['demand'].drop((building, 'space_heat'), inplace=True, axis=1)
            data_grid_plan['demand'].drop((building, 'water_heat'), inplace=True, axis=1)

            bui_mob_demands = [dem for (bui, dem) in data_grid_plan['demand'].columns
                               if dem.startswith('mobility') and bui == building]
            for mob_demand in bui_mob_demands:
                data_grid_plan['demand'].drop((building, mob_demand), inplace=True, axis=1)

            # EVU_Sperre: if HP electricity is cheaper (heizstromtarif),
            # the grid operator can lock HP electricity 6 hours a day,
            # maximum 2 hours per lock, has to be recovered in the next 2 hours (1 hour recover for 1 hour lock)
            # we need to define electricity_hp as a separate demand for modeling this.

            for i, cluster in enumerate(clusters):
                if building in cluster:
                    if mode['evu_sperre'] or mode['14a_steuve']:
                        if vartariff >0 :
                            if building in vartariff_nodes:
                                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                                        prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import_var'].iloc[1:]
                                        - prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])
                            else:
                                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                                        prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                                        - prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])
                        else:
                            data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                                    prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                                    - prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

                        data_grid_plan['demand'][(building, 'electricity_hp')] = copy.deepcopy(
                            data_grid_plan['demand'][(building, 'electricity')])

                        data_grid_plan['demand'].loc[year, :][(building, 'electricity_hp')].iloc[1:] = \
                            prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import_hp'].iloc[1:]
                        if mode['14a_steuve']:
                            data_grid_plan['demand'][(building, 'electricity_bev')] = copy.deepcopy(
                                data_grid_plan['demand'][(building, 'electricity')])

                            data_grid_plan['demand'].loc[year, :][(building, 'electricity_bev')].iloc[1:] = \
                                prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import_bev'].iloc[1:]

                    else:
                        if vartariff >0 :
                            if building in vartariff_nodes:
                                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                                        prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import_var'].iloc[1:]
                                        - prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])
                            else:
                                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                                        prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                                        - prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])
                        else:
                            data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                                    prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                                    - prob_cluster[i]._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

                    data_grid_plan['demand'].loc[year, :][(building, 'electricity-reactive')].iloc[1:] = \
                        prob_cluster[i]._result['e_pro_out'] \
                            .loc[:, year, building, 'Q_feeder_central', 'electricity-reactive']

            # set very small demand values to zero
            data_grid_plan['demand'][(data_grid_plan['demand'] > 0) & (data_grid_plan['demand']<1e-6)] = 0

            # delete all processes besides Q-compensation, import and feed-in
            bui_rooftop_pvs = [pv for (stf, bui, pv) in data_grid_plan['process'].index
                               if pv.startswith('Rooftop PV') and bui == building
                               and stf == year]
            for pvs in bui_rooftop_pvs:
                data_grid_plan['process'].drop((year, building, pvs), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'Heat_dummy_space'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'Heat_dummy_water'), inplace=True, axis=0)
            data_grid_plan['process'].drop((year, building, 'heatpump_air'), inplace=True, axis=0)
            try:
                data_grid_plan['process'].drop((year, building, 'heatpump_booster'), inplace=True, axis=0)
            except:
                pass
            bui_charging_stations = [cs for (stf, bui, cs) in data_grid_plan['process'].index
                                     if cs.startswith('charging_station') and bui == building and stf == year]
            for bcs in bui_charging_stations:
                data_grid_plan['process'].drop((year, building, bcs), inplace=True, axis=0)

            if not grid_curtailment:
                data_grid_plan['process'].drop((year, building, 'curtailment'), inplace=True, axis=0)
            else:
                data_grid_plan['process'].loc[(year, building, 'curtailment'), 'var-cost'] = \
                    data_grid_plan['buy_sell_price']['electricity_feed_in'].values[-1]
            data_grid_plan['process'].drop((year, building, 'Slack_heat'), inplace=True, axis=0)

            data_grid_plan['commodity'].drop((year, building, 'space_heat', 'Demand'), inplace=True, axis=0)
            data_grid_plan['commodity'].drop((year, building, 'water_heat', 'Demand'), inplace=True, axis=0)
            bui_solar_comms = [solcom for (bui, solcom) in data_grid_plan['supim'].columns
                               if solcom.startswith('solar') and bui == building]
            for scs in bui_solar_comms:
                data_grid_plan['commodity'].drop((year, building, scs, 'SupIm'), inplace=True, axis=0)

            bui_mob_commodities = [com for (stf, sit, com, typ) in data_grid_plan['commodity'].index
                                   if com.startswith('mobility') and sit == building]
            for com in bui_mob_commodities:
                data_grid_plan['commodity'].drop((year, building, com, 'Demand'), inplace=True, axis=0)
            data_grid_plan['commodity'].drop((year, building, 'common_heat', 'Stock'), inplace=True, axis=0)

        if grid_curtailment:
            grid_curtailment = set_curtailment_limits(data_grid_plan)
        #import pdb;
        #pdb.set_trace()
        # delete all process_commodity for deleted processes
        # data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'solar', 'In'), inplace=True, axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'electricity', 'Out'), inplace=True, axis=0)
        # data_grid_plan['process_commodity'].drop((year, 'Rooftop PV', 'electricity-reactive', 'Out'), inplace=True,
        #                                         axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'common_heat', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_space', 'space_heat', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'common_heat', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Heat_dummy_water', 'water_heat', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'electricity', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'common_heat', 'Out'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'heatpump_air', 'electricity-reactive', 'In'), inplace=True, axis=0)
        try:
            data_grid_plan['process_commodity'].drop((year, 'heatpump_booster', 'electricity', 'In'), inplace=True, axis=0)
            data_grid_plan['process_commodity'].drop((year, 'heatpump_booster', 'common_heat', 'Out'), inplace=True, axis=0)
        except:
            pass

        unique_charging_stations = [ucs for (stf, ucs, com, direction) in data_grid_plan['process_commodity'].index
                                    if ucs.startswith('charging_station') and direction == 'In']
        for ucs in unique_charging_stations:
            data_grid_plan['process_commodity'].drop((year, ucs, 'electricity', 'In'), inplace=True, axis=0)
            data_grid_plan['process_commodity'].drop((year, ucs, 'mobility' + ucs[16:], 'Out'), inplace=True, axis=0)

        if not grid_curtailment:
            data_grid_plan['process_commodity'].drop((year, 'curtailment', 'electricity', 'In'), inplace=True, axis=0)
        data_grid_plan['process_commodity'].drop((year, 'Slack_heat', 'common_heat', 'Out'), inplace=True, axis=0)

        # NEW: very low costs for electricity import and feed-in (so the significance of grid costs dominates)
        data_grid_plan['buy_sell_price'] = data_grid_plan['buy_sell_price'] * 0.0001
        # same with Q compensation
        data_grid_plan['process'].loc[(year, data_grid_plan['mainbusbar_node'], 'Q_feeder_central'),'var-cost'] *= 0.0001

        if mode['evu_sperre'] or mode['14a_steuve']:
            # data_grid_plan = add_electricity_hp_bev_usable_commodity(data_grid_plan, mode,
            #                                                         comtype='Demand')
            data_grid_plan = add_electricity_hp_bev_commodity(data_grid_plan, mode,
                                                              comtype=['Stock', 'Demand'])
            # data_grid_plan = add_elec_hp_bev_to_usable_process(data_grid_plan, mode)

            data_grid_plan = add_import_hp_bev_process(data_grid_plan, mode)

        if mode['evu_sperre'] or mode['14a_steuve'] or mode['14a_steune']:
            data_grid_plan = add_hp_bev_regulation_process(data_grid_plan, data, mode, var_cost=0.0001)

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
            prob_grid_plan.write('{}{}{}{}_step2.lp'.format(sce,
                                                            coordination_text,
                                                            flexible_text,
                                                            regulation_text),
                                 io_options={'symbolic_solver_labels': True})

        # refresh time stamp string and create filename for logfile
        log_filename = os.path.join(result_dir, '{}.log').format(sce)

        # set presolve to conservative, as this step takes way too long

        optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
        optim = setup_solver_mip(optim, logfile=log_filename, MIPGap=0.05, Presolve=2, TimeLimit= 12*3600, ConcurrentMIP = 4)
        # set presolve to off, as this step takes way too long
        # optim.set_options("Presolve=0")

        print("problem sent to solver")
        result = optim.solve(prob_grid_plan, tee=True, report_timing=True)

        save(prob_grid_plan, os.path.join(result_dir, '{}_{}_{}_step2.h5'.format(grid_text,
                                                                         paradigm_text,
                                                                         electrification_text)))

        if xls:
            report(prob_grid_plan, os.path.join(result_dir, '{}{}{}{}{}_{}_step2.xlsx'.format(sce,
                                                                                         coordination_text,
                                                                                         flexible_text,
                                                                                         regulation_text,
                                                                                         capacity_price_text,
                                                                                         str(electrification))),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)

        if mode['evu_sperre'] or mode['14a_steuve'] or mode['14a_steune']:
            print("Third step, for the reaction of households to the NB regulations")
            data_hp_react = copy.deepcopy(data)
            for building in demand_nodes:
                # make slack way more expensive than temperature reduction
                data['process'].loc[(year, building, 'Slack'),'var-cost'] = 100
                data['process'].loc[(year, building, 'Slack_heat') ,'var-cost'] = 100

            for building in demand_nodes:
                # wherever regulation is used, reduce the import capacity to the level allowed by the grid operator.
                for i, cluster in enumerate(clusters):
                    if building in cluster:
                        if mode['evu_sperre']:
                            data_hp_react['eff_factor'][(building, 'import_hp')] = 1 - \
                                                                                   prob_grid_plan._result['on_off'].loc[:,
                                                                                   :,
                                                                                   building,
                                                                                   'hp_lock'].values
                        if mode['14a_steuve']:
                            #new approach


                            #outdated approach
                            cap_hp = (0.01 if prob_cluster[i]._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0] == 0
                                      else prob_cluster[i]._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0])
                            cap_booster = (0.01 if prob_cluster[i]._result['cap_pro'].loc[:, building, 'heatpump_booster'].values[0] == 0
                                      else prob_cluster[i]._result['cap_pro'].loc[:, building, 'heatpump_booster'].values[0])

                            # commented 02.04.
                            # data_hp_react['availability'][(building, 'heatpump_air')] = data_hp_react['availability'][
                            #     (data['trafo_node'], 'import')].values
                            #
                            # data_hp_react['availability'][(building, 'heatpump_air')].iloc[1:] = \
                            #     (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                            #      'electricity_hp'] <= 0) * 1 + \
                            #     (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                            #      'electricity_hp'] > 0) * \
                            #     (data_grid_plan['demand'][(building, 'electricity_hp')].iloc[1:] - prob_grid_plan._result[
                            #                                                                            'e_pro_out']. \
                            #      loc[:, :, building, 'hp_14a_steuve_regulate', 'electricity_hp'].values) / cap_hp

                            # added 02.04
                            data_hp_react['availability'][(building, 'heatpump_air')] = data_hp_react['availability'][
                                (data['trafo_node'], 'import')].values
                            data_hp_react['availability'][(building, 'heatpump_booster')] = data_hp_react['availability'][
                                (data['trafo_node'], 'import')].values

                            if prob_cluster[i]._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0] <= 4.2:
                                # no restrictions if cap is smaller than 4
                                data_hp_react['availability'][(building, 'heatpump_air')].iloc[1:] = 1
                                if (prob_cluster[i]._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0] +
                                    prob_cluster[i]._result['cap_pro'].loc[:, building, 'heatpump_booster'].values[0]) <= 4.2:
                                    # total cap is smaller too, no restriction on peaker heater.
                                    data_hp_react['availability'][(building, 'heatpump_booster')].iloc[1:] = 1
                                else:
                                    # total cap exceeds 3.7, peaker may be curtailed:
                                    ## no restriction is regulation is zero
                                    ## if regulation is nonzero, reduce availability by the regulated amount
                                    data_hp_react['availability'][(building, 'heatpump_booster')].iloc[1:] = \
                                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                         'electricity_hp'] <= 0) * 1 + \
                                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                         'electricity_hp'] > 0) * \
                                        (prob_cluster[i]._result['e_pro_in'].loc[
                                         :, :, building, 'heatpump_booster', 'electricity_hp'].values -
                                         prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                         'electricity_hp'].values) / cap_booster

                            else:
                                # heat pump capacity larger than 3.7, regulation possible
                                data_hp_react['availability'][(building, 'heatpump_air')].iloc[1:] = \
                                    (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                         'electricity_hp'] <= prob_cluster[i]._result['e_pro_in'].loc[
                                         :, :, building, 'heatpump_booster', 'electricity_hp'].values) * 1 + \
                                    (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                 'electricity_hp'] > prob_cluster[i]._result['e_pro_in'].loc[
                                                      :, :, building, 'heatpump_booster', 'electricity_hp'].values) * \
                                    (prob_cluster[i]._result['e_pro_in'].loc[
                                                      :, :, building, 'heatpump_air', 'electricity_hp'].values -
                                     prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                     'electricity_hp'] +
                                     prob_cluster[i]._result['e_pro_in'].loc[
                                     :, :, building, 'heatpump_booster', 'electricity_hp'].values) / cap_hp

                                data_hp_react['availability'][(building, 'heatpump_booster')].iloc[1:] = \
                                    (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                         'electricity_hp'] == 0) * 1 + \
                                    ((prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                         'electricity_hp'] > 0) &
                                     (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                 'electricity_hp'] <= prob_cluster[i]._result['e_pro_in'].loc[
                                                      :, :, building, 'heatpump_booster', 'electricity_hp'].values)) * \
                                    (prob_cluster[i]._result['e_pro_in'].loc[
                                                      :, :, building, 'heatpump_booster', 'electricity_hp'].values -
                                     prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                     'electricity_hp']) / cap_booster + \
                                    ( (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                                      'electricity_hp'] >
                                       prob_cluster[i]._result['e_pro_in'].loc[:, :, building, 'heatpump_booster', 'electricity_hp'].values) * 0)


                            bui_charging_stations = [cs for (stf, bui, cs) in data['process'].index
                                                 if cs.startswith('charging_station') and bui == building
                                                 and stf == year]
                            for cs in bui_charging_stations:
                                data_hp_react['availability'][(building, cs)] = data_hp_react['availability'][
                                    (data['trafo_node'], 'import')].values
                                if prob_cluster[i]._result['cap_pro'].loc[year, building, cs] == 0:
                                    data_hp_react['availability'][(building, cs)].iloc[1:]  = 0
                                else:
                                    data_hp_react['availability'][(building, cs)].iloc[1:] = \
                                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'bev_14a_steuve_regulate',
                                         'electricity_bev'] <= 0) * 1 + \
                                        (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'bev_14a_steuve_regulate',
                                         'electricity_bev'] > 0) * \
                                        (data_grid_plan['demand'][(building, 'electricity_bev')].iloc[1:] -
                                         prob_grid_plan._result[
                                             'e_pro_out']. \
                                         loc[:, :, building, 'bev_14a_steuve_regulate', 'electricity_bev'].values) / \
                                        prob_cluster[i]._result['cap_pro'].loc[year, building, cs] / len(
                                            bui_charging_stations)

                        if mode['14a_steune']:
                            data_hp_react['availability'][(building, 'import')] = data_hp_react['availability'][
                                (data['trafo_node'], 'import')].values
                            if prob_cluster[i]._result['cap_pro'].loc[:, building, 'import'].values[0] == 0:
                                data_hp_react['availability'][(building, 'import')].iloc[1:] = 0
                            else:
                                data_hp_react['availability'][(building, 'import')].iloc[1:] = \
                                    (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'elec_14a_steune_regulate',
                                     'electricity'] <= 0) * 1 + \
                                    (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'elec_14a_steune_regulate',
                                     'electricity'] > 0) * \
                                    (data_grid_plan['demand'][(building, 'electricity')].iloc[1:] - prob_grid_plan._result[
                                                                                                        'e_pro_out']. \
                                     loc[:, :, building, 'elec_14a_steune_regulate', 'electricity'].values) / \
                                    prob_cluster[i]._result['cap_pro'].loc[:, building, 'import'].values[0]

            data_hp_react_cluster = {}
            prob_hp_react_cluster = {}
            # sequential
            return_dict = {}
            for i, cluster in enumerate(clusters):
                return_dict[i] = run_worker(cluster,
                                        dict(get_cluster_data=[data_hp_react],
                                             create_model=[dt,  # dt
                                                           timesteps,  # timesteps
                                                           'cost',  # objective
                                                           weighting_order,  # weighting_order
                                                           assumelowq,  # assumelowq
                                                           hoursPerPeriod,  # hoursPerPeriod
                                                           False,  # grid_plan_model
                                                           False, # dual
                                                           flexible],
                                             write=[sce,
                                                    coordination_text,
                                                    flexible_text,
                                                    regulation_text,
                                                    capacity_price_text,
                                                    str(i)],
                                             SolverFactory=[solver_name],
                                             solve=[True,  # tee
                                                    True]),  # report timing
                                        lp,
                                        xls,
                                        mode['tsam'],
                                        i,
                                        result_dir,
                                        return_dict,
                                        True,  # react
                                        prob_cluster[i],
                                        prob_grid_plan,  # prob_grid_plan
                                        mode['evu_sperre'])  # mode_evu_sperre
                                    # dual
            for i, cluster in enumerate(clusters):
                data_hp_react_cluster[i] = return_dict[i][0]
                prob_hp_react_cluster[i] = return_dict[i][1]

            save(prob_hp_react_cluster, os.path.join(result_dir, '{}_{}_{}_step3.h5'.format(grid_text,
                                                                                   paradigm_text,
                                                                                   electrification_text)), parallel=True)

            # parallel
            # procs = []
            # manager = mp.Manager()
            # return_dict = manager.dict()
            # for i, cluster in enumerate(clusters):
            #     proc = mp.Process(target=run_worker,
            #                       args=(cluster,
            #                             dict(get_cluster_data=[data_hp_react],
            #                                  create_model=[dt,  # dt
            #                                                timesteps,  # timesteps
            #                                                'cost',  # objective
            #                                                weighting_order,  # weighting_order
            #                                                assumelowq,  # assumelowq
            #                                                hoursPerPeriod,  # hoursPerPeriod
            #                                                False,  # grid_plan_model
            #                                                False],
            #                                  write=[sce,
            #                                         coordination_text,
            #                                         flexible_text,
            #                                         regulation_text,
            #                                         capacity_price_text,
            #                                         str(i)],
            #                                  SolverFactory=[solver_name],
            #                                  solve=[True,  # tee
            #                                         True]),  # report timing
            #                             lp,
            #                             xls,
            #                             mode['tsam'],
            #                             i,
            #                             result_dir,
            #                             return_dict,
            #                             True,  # react
            #                             prob_cluster[i],
            #                             prob_grid_plan,  # prob_grid_plan
            #                             mode['evu_sperre'])  # mode_evu_sperre
            #                       )  # dual
            #     procs.append(proc)
            #     proc.start()
            #
            # for proc in procs:
            #     proc.join()
            #
            # for i, cluster in enumerate(clusters):
            #     data_hp_react_cluster[i] = return_dict[i][0]
            #     prob_hp_react_cluster[i] = return_dict[i][1]
            #
            # save(prob_hp_react_cluster, os.path.join(result_dir, '{}_{}_{}_step3.h5'.format(grid_text,
            #                                                                        paradigm_text,
            #                                                                        electrification_text)), parallel=True)


            # for i, cluster in enumerate(clusters):
            #     print('creating data for cluster {str(i)+1}, step 3')
            #
            #     data_hp_react_cluster[i] = get_cluster_data(data_hp_react, cluster)
            #     print('creating prob for cluster {str(i)+1}, step 3')
            #     if mode['tsam']:
            #         prob_hp_react_cluster[i] = create_model(data_hp_react_cluster[i], dt=dt,
            #                                                 timesteps=timesteps,
            #                                                 objective='cost',
            #                                                 weighting_order=weighting_order,
            #                                                 assumelowq=assumelowq,
            #                                                 hoursPerPeriod=hoursPerPeriod,
            #                                                 grid_plan_model=False,
            #                                                 dual=False)
            #     else:
            #
            #         prob_hp_react_cluster[i] = create_model(data_hp_react_cluster[i], dt=dt,
            #                                                 timesteps=timesteps,
            #                                                 objective='cost',
            #                                                 # weighting_order=weighting_order,
            #                                                 assumelowq=assumelowq,
            #                                                 # hoursPerPeriod=hoursPerPeriod,
            #                                                 grid_plan_model=False,
            #                                                 dual=False)
            #
            #     # fix all capacitties in building model to see hp reaction
            #     capacity_variables = ['cap_pro_new', 'cap_decommissioned',
            #                           'cap_sto_c_new', 'cap_sto_p_new', 'cap_sto_c_decommissioned',
            #                           'cap_sto_p_decommissioned']
            #
            #     for cap_var in capacity_variables:
            #         caps = get_entity(prob_cluster[i], cap_var)
            #         for var_idx in getattr(prob_hp_react_cluster[i], cap_var):
            #             getattr(prob_hp_react_cluster[i], cap_var)[var_idx].fix(caps[var_idx])
            #         # write lp file # lp writing needs huge RAM capacities for bigger models
            #
            #     # fix curtailment
            #     tau_values = get_entity(prob_grid_plan, 'tau_pro')
            #     for var_idx in getattr(prob_hp_react_cluster[i], 'tau_pro'):
            #         if var_idx[3] == 'curtailment':
            #             if var_idx[0] != 0:
            #                 getattr(prob_hp_react_cluster[i], 'tau_pro')[var_idx].fix(tau_values[var_idx])
            #
            #     # delete single hp rule, not necessary and causes infeasibility
            #     if mode['evu_sperre']:
            #         del prob_hp_react_cluster[i].res_single_heatpump
            #
            #     if lp:
            #         prob_hp_react_cluster[i].write('{}{}{}{}_{}_step3.lp'.format(sce,
            #                                                                      coordination_text,
            #                                                                      flexible_text,
            #                                                                      regulation_text, str(i)),
            #                                        io_options={'symbolic_solver_labels': True})
            #
            #     optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
            #     optim = setup_solver_mip(optim, logfile=log_filename, precision='high', clusters=clusters)
            #     print('solving cluster {str(i)+1}, step 3')
            #
            #     result = optim.solve(prob_hp_react_cluster[i], tee=True, report_timing=True)
            #
            #     save(prob_hp_react_cluster[i], os.path.join(result_dir, '{}{}{}{}_{}_step3.h5'.format(sce,
            #                                                                                           coordination_text,
            #                                                                                           flexible_text,
            #                                                                                           regulation_text,
            #                                                                                           str(i))))
            #
            #     if xls:
            #         report(prob_hp_react_cluster[i], os.path.join(result_dir, '{}{}{}{}_{}_step3.xlsx'.format(sce,
            #                                                                                                   coordination_text,
            #                                                                                                   flexible_text,
            #                                                                                                   regulation_text,
            #                                                                                                   str(i))),
            #                report_tuples=report_tuples,
            #                report_sites_name=report_sites_name)
        else:
            prob_hp_react_cluster = {}

    if grid_opt:
        return prob_cluster, prob_grid_plan, prob_hp_react_cluster, cross_scenario_data
    else:
        return prob_cluster, cross_scenario_data

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
