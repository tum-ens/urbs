import os
import time

from pyomo.environ import SolverFactory
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *
from .features import *
from .scenarios import *
import os
import multiprocessing as mp
import random
import numpy as np



def run_worker(cluster, func_args, lp, xls, i, result_dir, return_dict,
               react=False, prob_bui=None, prob_grid_plan=None):

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

    if lp:
        prob_cluster.write('{}_{}_step{}.lp'.format(func_args['write'][0],
                                                            func_args['write'][1], str(step_no)),
                           io_options={'symbolic_solver_labels': True})
    optim = SolverFactory(func_args['SolverFactory'][0])
    if react:
        optim = setup_solver_mip(optim,
                             logfile=os.path.join(result_dir, '{}{}.log').format(func_args['write'][0],
                                                                                 func_args['write'][1]),
                             clusters=True, MIPGap=0.02, TimeLimit=1800)
    else:
        optim = setup_solver_mip(optim,
                             logfile=os.path.join(result_dir, '{}{}.log').format(func_args['write'][0],
                                                                                 func_args['write'][1]),
                             clusters=True, MIPGap=0.05)
    result = optim.solve(prob_cluster, tee=func_args['solve'][0], report_timing=func_args['solve'][0])

    if str(result.solver.termination_condition) == 'infeasibleOrUnbounded':
        print(f"Not feasible!: {str(result.solver.termination_condition)}")
        prob_cluster.write('{}_{}_step{}.lp'.format(func_args['write'][0],
                                                            func_args['write'][1], str(step_no)),
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

def setup_solver_mip(optim, logfile='solver.log', precision='low', clusters=None, **gurobiparams):
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
        if precision == 'high':
            optim.set_options("BarConvTol=1e-10")
            optim.set_options("FeasibilityTol=1e-9")
            optim.set_options("OptimalityTol=1e-9")
        if clusters is None:
            pass

    if optim.name == 'cplexdirect' or optim.name == 'cplex_direct':
        optim.options['threads'] = 32
        if "MIPGap" in gurobiparams.keys():
            optim.options['mip_tolerances_mipgap'] = gurobiparams['MIPGap']
        # optim.options['epgap'] = 0.01
    # reference with list of options
    # execute 'glpsol --help'
    return optim


def run_lvds_opt(input_files, solver_name, timesteps, scenario, result_dir, dt,
                          objective,
                          microgrid_files=None,
                          report_tuples=None,
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
                          vartariff=0,
                          parallel=0):

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

    year = date.today().year
    sce = scenario.__name__
    data = read_input(input_files, year)
    data, cross_scenario_data = scenario(data, cross_scenario_data)
    validate_input(data)
    validate_dc_objective(data, objective)

    # remove empty elements in the clusters list (relevant for parallel prosumer runs)
    if clusters:
        clusters = [lst for lst in clusters if len(lst) > 0]

    # identify the mode of the model
    mode = identify_mode(data)

    #create labels for created files
    coordination_text, flexible_text, regulation_text, capacity_price_text = create_xls_file_labels(uncoordinated, flexible, mode, data)

    # adjustments in case flexibilities are deactivated (Global sheet)
    if not flexible:
        # delete all storages and flexibility
        data = remove_battery(data)
        data = remove_heat_storage(data)

        if not mode['14a']: # only remove mobility flexibility if 14a not activated (otherwise model can be infeasible)
            data = remove_mob_flexibility(data)
            mode['sto'] = False

    # identify the transformer and the main busbar nodes (transformer has the import process, main busbar the Q_comp)
    data['trafo_node'] = data['process'].query("Process == 'import'").index.get_level_values(1)[0]
    data['mainbusbar_node'] = data['process'].query("Process == 'Q_feeder_central'").index.get_level_values(1)[0]

    # add transdist functionality if activated
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

    # add curtailment option for heat (see lvdshelper.py).
    # acts to "ventilate" the building, in case the internal or solar gains heat it beyond the T_max
    add_curtailment_heat(data)

    if mode['14a']:
        # 14a related functions, see lvdshelper.py
        data = add_import_hp_bev_process(data) # create processes that import "hp" and "bev" 14a commodities
        data = add_electricity_hp_bev_commodity(data) # define "hp" and "bev" 14a commodities
        data = modify_hp_bev_processes(data) # moditfy "hp" and "charging_stations" so that they input 14a commodities
        data = add_elec_to_hp_bev_process(data) # create processes that convert electricity to 14a commodities

    if not uncoordinated:
        if mode['14a']:
            add_hp_bev_flows(data) # coordinated opt. with 14a (not typical); add 14a commodity flows the grid

    if uncoordinated:
        # uncoordinated optimization of buildings. delete all transmissions
        data['transmission'] = data['transmission'].iloc[0:0]
        mode['tra'] = False
        mode['acpf'] = False

        # add building-specific import/feed-in processes (see lvdshelper.py)
        data = distributed_building_specific_import_processes(data, mode) # each building gets an import/feed-in process

    if mode['tsam']:
        # run timeseries aggregation method before creating model
        data, timesteps, weighting_order, cross_scenario_data = run_tsam(data, noTypicalPeriods,
                                                                         hoursPerPeriod,
                                                                         cross_scenario_data,
                                                                         mode['tsam_season'],
                                                                         uncoordinated=uncoordinated,
                                                                         uhp=mode['uhp'])
    else:
        # tsam disabled, just filter the time series according to the defined time steps
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

    # user can define a percentual electrification rate (0<= electrification <<1) that removes electrification measures
    # in random buildings
    # alternatively, adjust pv, hp, or bev penetration individually through the variables pv_ratio, bev_ratio, hp_ratio

    if electrification < 1 or pv_ratio < 1:
        data = remove_pv_in_random(data, electrification)

    if electrification < 1 or bev_ratio < 1:
        data = unelectrify_mobility_in_random(data, electrification)

    if electrification < 1 or hp_ratio < 1:
        data = unelectrify_heat_in_random(data, electrification)

    # allow participation to variable grid tariffs.  0<=vartariff<=1: share of prosumers which opt to variable tariffs.
    if vartariff > 0:
        random.seed(4)
        demand_nodes = set([sit for (sit, demand) in data['demand'].columns])
        vartariff_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (vartariff)))
        data = adopt_variable_tariffs(data, vartariff_nodes)

    # if non-zero capacity prices (power_price_kw index in Global) are defined:
    # assign these for each site (power_price_kw column in Site) and adjust the import prices slightly to compensate
    if data['global_prop'].loc[pd.IndexSlice[:, 'power_price_kw'], 'value'].iloc[0] > 0:
        kwh_per_peakkw = 1000 # assumed average annual kWh consumption to peak kW ratio
        demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
        for building in demand_nodes:
            for i, cluster in enumerate(clusters):
                if building in cluster:
                    data['site'].loc[year, building]['power_price_kw'] = \
                    data['global_prop'].loc[pd.IndexSlice[:, 'power_price_kw'], 'value'].iloc[0]
        # optional: adjust the import prices slightly to compensate (so that the total payments do not increase much)
        data['buy_sell_price']['electricity_import'] = data['buy_sell_price']['electricity_import'] - \
                                                       data['global_prop'].loc[
                                                           pd.IndexSlice[:, 'power_price_kw'], 'value'].iloc[
                                                           0] / kwh_per_peakkw

    # data is constructed finally, now to solve the HOODS-Bui (or HOODS-Sys, if coordinated) problem.
    if not uncoordinated: #if HOODS-Sys: just solve the model normally
        prob = create_model(data, dt=dt,
                            timesteps=timesteps,
                            objective='cost',
                            weighting_order=weighting_order,
                            assumelowq=assumelowq,
                            hoursPerPeriod=hoursPerPeriod,
                            grid_plan_model=False,
                            dual=False)

        # write lp file # lp writing needs huge RAM capacities for bigger models
        if lp:
            prob.write('{}{}{}{}_step1.lp'.format(sce,
                                                  coordination_text,
                                                  flexible_text,
                                                  regulation_text),
                       io_options={'symbolic_solver_labels': True})
        log_filename = os.path.join(result_dir, '{}.log').format(sce)
        optim = SolverFactory(solver_name)
        optim = setup_solver_mip(optim, logfile=log_filename, MIPGap=0.05, ConcurrentMIP=6, Threads=24)
        result = optim.solve(prob, tee=True, report_timing=True)

        # create h5 file label by using grid name, model type etc.
        # grid_text, paradigm_text, electrification_text = create_h5_file_labels(input_files, electrification) # lvdshelper.py

        # save h5 for HOODS-Sys
        save(prob, os.path.join(result_dir, '{}_step1.h5'.format(sce)), manyprob=False)

        if xls:
            report(prob, os.path.join(result_dir, '{}_step1.h5'.format(sce)),
                   report_tuples=report_tuples,
                   report_sites_name=report_sites_name)

        #return prob

    else: # i.e. uncoordinated optimziation (HOODS-Bui subproblems): there are two ways to solve the problems

        data_cluster = {} # containers for cluster data
        prob_cluster = {} # containers for cluster models

        # there are two ways to solve the problems (parallel or sequential
        if not parallel: # each HOODS-Bui cluster is solved sequentially after another  (slower, but reliable)
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
                                                        str(i)],
                                                 SolverFactory=[solver_name],
                                                 solve=[True,  # tee
                                                        True]),  # report timing
                                            lp,
                                            xls,
                                            i,
                                            result_dir,
                                            return_dict,
                                            )
        else: #parallel = 1 -> each HOODS-Bui cluster solved in separate CPUs in parallel (faster, can get stuck in h5 step)
            procs = []
            manager = mp.Manager()
            return_dict = manager.dict()

            for i, cluster in enumerate(clusters):
                proc = mp.Process(target=run_worker,
                                  args=(cluster,
                                        dict(get_cluster_data=[data],
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
                                                    str(i)],
                                             SolverFactory=[solver_name],
                                             solve=[True,  # tee
                                                    True]),  # report timing
                                        lp,
                                        xls,
                                        i,
                                        result_dir,
                                        return_dict),
                                  )  # dual
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()

        # HOODS-Bui problems are solved either in parallel or sequentially.
        # now save the solutions into the data and solution containers (data_cluster and prob_cluster)
        for i, cluster in enumerate(clusters):
            data_cluster[i] = return_dict[i][0]
            prob_cluster[i] = return_dict[i][1]

        # create h5 file label by using grid name, model type etc.
        # grid_text, paradigm_text, electrification_text = create_h5_file_labels(input_files, electrification) # lvdshelper.py

        # save h5 file for HOODS-Bui
        save(prob_cluster, os.path.join(result_dir, '{}_step1.h5'.format(sce)), manyprob=True)



        if grid_opt: # move on to building the OODS-Grid problem (grid optimization with fixed prosumer loads)
            # similar processing as the previous step (based on the same model, to be modified)
            data_grid_plan = read_input(input_files, year)
            data_grid_plan, cross_scenario_data = scenario(data_grid_plan, cross_scenario_data)
            validate_input(data_grid_plan)
            validate_dc_objective(data_grid_plan, objective)

            # similar processing as the previous step
            mode = identify_mode(data_grid_plan)
            data_grid_plan['trafo_node'] = data_grid_plan['process'].query("Process == 'import'").index.get_level_values(1)[0]
            data_grid_plan['mainbusbar_node'] = \
            data_grid_plan['process'].query("Process == 'Q_feeder_central'").index.get_level_values(1)[0]

            # transdist considerations
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

            if mode['14a']:
                add_hp_bev_flows(data_grid_plan) # add 14a commodity flows the grid

            # tsam considerations
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



            #### All modifications required to establish the HOODS-Grid model

            # delete all dsm (irrelevant in HOODS-Grid)
            data_grid_plan['dsm'] = pd.DataFrame(columns=data_grid_plan['dsm'].columns)

            # delete all storages (irrelevant in HOODS-Grid)
            data_grid_plan['storage'] = pd.DataFrame(columns=data_grid_plan['storage'].columns)

            # identify prosumer nodes (buildings)
            demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns if demand == 'space_heat']
            for building in demand_nodes:
                # delete solar SupIm timeseries
                data_grid_plan = delete_solar_supim_timeseries(data_grid_plan, building)
                data_grid_plan = delete_charging_station_eff_factors(data_grid_plan, building)
                data_grid_plan = delete_heatpump_eff_factors(data_grid_plan, building)

                # delete all non-electric demand (space_heat, water_heat, mobility
                data_grid_plan = delete_non_electric_demand(data_grid_plan, building)

                # shift heat pump and charging station operation to electricity demand (see function in lvdshelper.py)
                for i, cluster in enumerate(clusters):
                    if building in cluster:
                        if vartariff:
                            data_grid_plan = shift_demand_to_elec(data_grid_plan, building,
                                                                  prob_cluster[i], mode, vartariff, vartariff_nodes)
                        else:
                            data_grid_plan = shift_demand_to_elec(data_grid_plan, building,
                                                                  prob_cluster[i], mode, vartariff)


                # set very small demand values to zero (for improved numerical performance)
                data_grid_plan['demand'][(data_grid_plan['demand'] > 0) & (data_grid_plan['demand']<1e-6)] = 0

                # delete all processes besides Q_compensation, import and feed-in
                data_grid_plan = delete_processes_for_hoods_grid(data_grid_plan, building, grid_curtailment)

                # delete all commodities irrelevant to HOODS-Grid
                data_grid_plan = delete_commodities_for_hoods_grid(data_grid_plan, building)

            # set limits to DSO-side grid curtailment (it cannot be greater than the feed-in at each hour!)
            if grid_curtailment:
                grid_curtailment = set_curtailment_limits(data_grid_plan)

            # delete all process_commodity for deleted processes
            data_grid_plan = delete_procoms_for_hoods_grid(data_grid_plan, grid_curtailment)

            # set very low costs for electricity import and feed-in (so the significance of grid costs dominates)
            # Note: they are not set to zero, to prevent simultaneous import and feed-in
            data_grid_plan['buy_sell_price'] = data_grid_plan['buy_sell_price'] * 0.0001

            # same with Q compensation
            data_grid_plan['process'].loc[(year, data_grid_plan['mainbusbar_node'], 'Q_feeder_central'),'var-cost'] *= 0.0001

            if mode['14a']:
                #### add 14a related processes and commodities
                # add 14a commodities (like in HOODS-Bui-14a)
                data_grid_plan = add_electricity_hp_bev_commodity(data_grid_plan,
                                                                  comtype=['Stock', 'Demand'])
                # add import process for the 14a commodities at the trafo node
                data_grid_plan = add_import_hp_bev_process(data_grid_plan)

                # add 14a regulation processes that reduce production by "generating" 14a commodities with a slightly
                # higher cost (default: 0.0001)
                data_grid_plan = add_hp_bev_regulation_process(data_grid_plan, data, var_cost=0.0001)

            # Data for the HOODS_Grid problem is configured, build model
            prob_grid_plan = create_model(data_grid_plan, dt=dt,
                                          timesteps=timesteps,
                                          objective='cost',
                                          weighting_order=weighting_order,
                                          assumelowq=assumelowq,
                                          hoursPerPeriod=hoursPerPeriod,
                                          grid_plan_model=True,
                                          dual=False)

            # write lp file if desired
            if lp:
                prob_grid_plan.write('{}_step2.lp'.format(sce),
                                     io_options={'symbolic_solver_labels': True})

            # refresh time stamp string and create filename for logfile
            log_filename = os.path.join(result_dir, '{}.log').format(sce)

            # optional: set presolve to conservative, as this step may take way too long
            optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
            optim = setup_solver_mip(optim, logfile=log_filename, MIPGap=0.05, Presolve=2, TimeLimit= 12*3600, ConcurrentMIP = 4)

            print("problem sent to solver")
            result = optim.solve(prob_grid_plan, tee=True, report_timing=True)

            save(prob_grid_plan, os.path.join(result_dir, '{}_step2.h5'.format(sce)), manyprob=False)

            if xls:
                report(prob_grid_plan, os.path.join(result_dir, '{}_step2.xlsx'.format(sce)),
                       report_tuples=report_tuples,
                       report_sites_name=report_sites_name)


            # HOODS-Grid is solved and the result is saved as a h5 file ("...step2.h5")
            # If 14a is active, the HOODS-Bui-React model will be solved now (to assess thermal comfort loss etc.).
            if mode['14a']:
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
                            if mode['14a']:
                                data_hp_react = limit_hp_for_hoods_bui_react(
                                    data_hp_react, data, building, prob_cluster[i], prob_grid_plan)
                                data_hp_react = limit_bev_for_hoods_bui_react(
                                    data_hp_react, data, building, prob_cluster[i], prob_grid_plan, data_grid_plan)

                data_hp_react_cluster = {}
                prob_hp_react_cluster = {}

                if not parallel:
                    # sequential solving of HOODS-Bui-React models
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
                                                            str(i)],
                                                     SolverFactory=[solver_name],
                                                     solve=[True,  # tee
                                                            True]),  # report timing
                                                lp,
                                                xls,
                                                i,
                                                result_dir,
                                                return_dict,
                                                True,  # react
                                                prob_cluster[i],
                                                prob_grid_plan,  # prob_grid_plan
                                                )
                                            # dual
                    for i, cluster in enumerate(clusters):
                        data_hp_react_cluster[i] = return_dict[i][0]
                        prob_hp_react_cluster[i] = return_dict[i][1]

                    save(prob_hp_react_cluster, os.path.join(result_dir, '{}_step3.h5'.format(sce)), manyprob=True)
                else:
                    # parallel solving of HOODS-Bui-React models
                    procs = []
                    manager = mp.Manager()
                    return_dict = manager.dict()
                    for i, cluster in enumerate(clusters):
                        proc = mp.Process(target=run_worker,
                                          args=(cluster,
                                                dict(get_cluster_data=[data_hp_react],
                                                     create_model=[dt,  # dt
                                                                   timesteps,  # timesteps
                                                                   'cost',  # objective
                                                                   weighting_order,  # weighting_order
                                                                   assumelowq,  # assumelowq
                                                                   hoursPerPeriod,  # hoursPerPeriod
                                                                   False,  # grid_plan_model
                                                                   False,
                                                                   flexible],
                                                     write=[sce,
                                                            str(i)],
                                                     SolverFactory=[solver_name],
                                                     solve=[True,  # tee
                                                            True]),  # report timing
                                                lp,
                                                xls,
                                                i,
                                                result_dir,
                                                return_dict,
                                                True,  # react
                                                prob_cluster[i],
                                                prob_grid_plan,  # prob_grid_plan
                                                )
                                          )  # dual
                        procs.append(proc)
                        proc.start()

                    for proc in procs:
                        proc.join()

                    for i, cluster in enumerate(clusters):
                        data_hp_react_cluster[i] = return_dict[i][0]
                        prob_hp_react_cluster[i] = return_dict[i][1]

                    save(prob_hp_react_cluster, os.path.join(result_dir, '{}_step3.h5'.format(sce)), manyprob=True)

            else:
                prob_hp_react_cluster = {}

    #if grid_opt:
    #    return prob_cluster, prob_grid_plan, prob_hp_react_cluster, cross_scenario_data
    #else:
    #    return prob_cluster, cross_scenario_data

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
