# -*- coding: utf-8 -*-
import os
import shutil
import urbs
from urbs.runfunctions import *
from multiprocessing import freeze_support
import pandas as pd
import glob

import warnings
if __name__ == '__main__':
    freeze_support()

    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=UserWarning)

    input_files = 'urbs_DG.xlsx'  # for single year file name, for intertemporal folder name
    input_dir = 'Input'
    input_path = os.path.join(input_dir, input_files)

    microgrid_files = ['Microgrid_rural_A.xlsx', 'Microgrid_urban_A.xlsx']
    microgrid_dir = 'Input/microgrid_types'
    microgrid_paths = []
    for i, microgrid_file in enumerate(microgrid_files):
        microgrid_paths.append(os.path.join(microgrid_dir, microgrid_file))

    result_name = os.path.basename(__file__)
    result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

    # #copy input file to result directory
    try:
        shutil.copytree(input_path, os.path.join(result_dir, input_dir))
    except NotADirectoryError:
        shutil.copyfile(input_path, os.path.join(result_dir, input_files))

    # #copy run file to result directory
    shutil.copy(__file__, result_dir)

    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective

    # Choose Solver (cplex, glpk, gurobi, ...)
    solver = 'gurobi'

    # simulation timesteps
    (offset, length) = (0, 8760)  # time step selection
    timesteps = range(offset, offset + length + 1)
    dt = 1  # length of each time step (unit: hours)

    # detailed reporting commodity/sites
    if os.path.isdir(input_path):
        glob_input = os.path.join(input_path, '*.xlsx')
        input_files = sorted(glob.glob(glob_input))
    else:
        input_files = [input_path]

    for filename in input_files:
        print("Reading for site names and mode")
        with pd.ExcelFile(filename) as xls:
            demand = xls.parse('Demand').set_index(['t'])
            print("Site reading complete")

            global_props       = xls.parse('Global').set_index('Property')
            tsam               = global_props.loc['tsam']['value']
            noTypicalPeriods   = int(global_props.loc['noTypicalPeriods']['value'])
            hoursPerPeriod     = int(global_props.loc['hoursPerPeriod']['value'])
            uncoordinated      = global_props.loc['uncoordinated']['value']
            flexible           = global_props.loc['flexible']['value']
            lp                 = global_props.loc['lp']['value']
            excel              = global_props.loc['excel']['value']
            electrification    = global_props.loc['electrification']['value']
            vartariff          = global_props.loc['vartariff']['value']
            parallel           = global_props.loc['parallel']['value']

    demcollist = demand.columns.to_list()
    demcollist.remove('weight_typeperiod')

    report_tuples = [(2023, col.split('.')[0], 'electricity') for col in demcollist if col.split('.')[1] == 'electricity'] \
                    + [(2023, col.split('.')[0], 'electricity-reactive') for col in demcollist if col.split('.')[1] == 'electricity-reactive'] \
                    + [(2023, col.split('.')[0], 'common_heat') for col in demcollist if col.split('.')[1] == 'common_heat'] \
                    + [(2023, col.split('.')[0], 'electricity_hp') for col in demcollist if col.split('.')[1] == 'electricity'] \
                    + [(2023, col.split('.')[0], 'electricity_bev') for col in demcollist if col.split('.')[1] == 'electricity']

    report_tuples_grid_plan =[(2023, col.split('.')[0], 'electricity') for col in demcollist if col.split('.')[1] == 'electricity'] \
                    + [(2023, col.split('.')[0], 'electricity-reactive') for col in demcollist if col.split('.')[1] == 'electricity-reactive']

    # report_tuples = []

    # optional: define names for sites in report_tuples
    report_sites_name = {}
    # plotting commodities/sites
    plot_tuples = []
    # optional: define names for sites in plot_tuples
    plot_sites_name = {}

    # plotting timesteps
    plot_periods = {
        'all': timesteps[1:]
    }
    # time_series_for_aggregation = {'demand': ['electricity', ']}
    # select scenarios to be run
    scenarios = [
        urbs.flex_all
    ]

    cross_scenario_data = dict()

    if uncoordinated:  # LVDS: create clusters list for, if activated, parallel prosumer runs
        n_cpu = int(os.cpu_count() / 2)
        buildings = [col.split('.')[0] for col in demcollist if col.split('.')[1] == 'electricity']
        div, mod = divmod(len(buildings), n_cpu)
        clusters = [buildings[i * div + min(i, mod):(i + 1) * div + min(i + 1, mod)] for i in range(n_cpu)]
    else:
        clusters = None

    for scenario in scenarios:
        urbs.run_lvds_opt(input_path, solver, timesteps,
                         scenario, result_dir, dt,
                         objective, microgrid_paths,
                         report_tuples=report_tuples,
                         cross_scenario_data=cross_scenario_data,
                         report_sites_name=report_sites_name,
                         noTypicalPeriods=noTypicalPeriods,
                         hoursPerPeriod=hoursPerPeriod,
                         uncoordinated=uncoordinated,
                         flexible=1,
                         grid_curtailment=1,
                         lp=lp,
                         xls=excel,
                         assumelowq=1,
                         clusters=clusters,
                         electrification=electrification,
                         vartariff=vartariff,
                         parallel=parallel)

       # prob, prob_grid_plan, prob_hp_react, cross_scenario_data = urbs.run_lvds_opt(input_path, solver, timesteps,

