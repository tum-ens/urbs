from urbs.identify import *
import copy
import math
import numpy as np
import os
from datetime import datetime, date
import random

def remove_battery(data):
    # de-flexiblise electricity demand by disallowing battery investment
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['inst-cap-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['inst-cap-c']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['cap-up-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['cap-up-c']] = 0
    return data

def remove_heat_storage(data):
    # de-flexiblise electricity demand by disallowing battery investment
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['cap-up-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['cap-up-c']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['inst-cap-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['inst-cap-c']] = 0
    return data

def remove_mob_flexibility(data):
    # remove mobility flexibility
    for (stf, sit, sto, com) in data['storage'].index:
        if sto.startswith('mobility'):
            data['storage'].loc[(stf, sit, sto, com), 'inst-cap-p'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'inst-cap-c'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'cap-up-p'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'cap-up-c'] = 0

    return data

def create_xls_file_labels(uncoordinated, flexible, mode, data):
    coordination_text = '_uncoordinated' if uncoordinated else '_coordinated'
    flexible_text = '_flexible' if flexible else '_inflexible'

    if mode['14a']:
        regulation_text = '_14a'
    else:
        regulation_text = ''

    if data['site']['power_price_kw'].dropna().iloc[0] > 0.01:
        capacity_price_text = '_capacity_price'
    else:
        capacity_price_text = ''

    return coordination_text, flexible_text, regulation_text, capacity_price_text

def create_h5_file_labels(input_files, electrification):
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
    return grid_text, paradigm_text, electrification_text

def add_import_hp_bev_process(data):
    year = date.today().year

    #add import_hp as a process
    data['process'].loc[year, data['trafo_node'], 'import_hp'] = \
        data['process'].loc[year, data['trafo_node'], 'import'].copy(deep=True)
    data['process_commodity'].loc[year, 'import_hp', 'electricity_hp_import', 'In'] = (1, np.nan)
    data['process_commodity'].loc[year, 'import_hp', 'electricity_hp', 'Out'] = (1, np.nan)

    data['buy_sell_price']['electricity_hp_import'] = \
        data['buy_sell_price']['electricity_import'] * \
        data['global_prop'].loc[pd.IndexSlice[:, 'heatpump_elec_mult'], 'value'].iloc[0]
    data['commodity'].loc[year, data['trafo_node'], 'electricity_hp_import', 'Buy'] = \
        data['commodity'].loc[year, data['trafo_node'], 'electricity_import', 'Buy'].copy(deep=True)

    #add import_bev as a process
    data['process'].loc[year, data['trafo_node'], 'import_bev'] = \
        data['process'].loc[year, data['trafo_node'], 'import'].copy(deep=True)
    data['process_commodity'].loc[year, 'import_bev', 'electricity_bev_import', 'In'] = (1, np.nan)
    data['process_commodity'].loc[year, 'import_bev', 'electricity_bev', 'Out'] = (1, np.nan)
    data['buy_sell_price']['electricity_bev_import'] = \
        data['buy_sell_price']['electricity_import']
    data['commodity'].loc[year, data['trafo_node'], 'electricity_bev_import', 'Buy'] = \
        data['commodity'].loc[year, data['trafo_node'], 'electricity_import', 'Buy'].copy(deep=True)

    return data


def add_electricity_hp_bev_commodity(data, comtype='Stock'):
    # add commodity "electricity_hp" to all sites
    year = date.today().year
    demand_nodes = set([sit for (sit, demand) in data['demand'].columns])
    try:
        demand_nodes.remove(data['trafo_node'])
    except KeyError:
        pass
    try:
        demand_nodes.remove(data['mainbusbar_node'])
    except KeyError:
        pass

    if (comtype == ['Stock', 'Demand']):
        for site in data['site'].index.get_level_values(1):
            if site in demand_nodes:
                data['commodity'].loc[year, site, 'electricity_hp', 'Demand'] = (0, 0, 0)
                data['commodity'].loc[year, site, 'electricity_bev', 'Demand'] = (0, 0, 0)
            else:
                data['commodity'].loc[year, site, 'electricity_hp', 'Stock'] = (0, 0, 0)
                data['commodity'].loc[year, site, 'electricity_bev', 'Stock'] = (0, 0, 0)
    else:
        for site in data['site'].index.get_level_values(1):
            data['commodity'].loc[year, site, 'electricity_hp', comtype] = (0, 0, 0)
            data['commodity'].loc[year, site, 'electricity_bev', comtype] = (0, 0, 0)

    return data

def modify_hp_bev_processes(data):
    year = date.today().year
    demand_nodes = set([sit for (sit, demand) in data['demand'].columns])
    try:
        demand_nodes.remove(data['trafo_node'])
    except KeyError:
        pass
    try:
        demand_nodes.remove(data['mainbusbar_node'])
    except KeyError:
        pass

    # modify the input commodities of charging stations to usable commodities
    # data['process_commodity'][data['process_commodity'].index.get_level_values(1) == 'heatpump_air'].rename(
    #    index={'electricity': 'electricity_hp_usable'}, level=2, inplace=True)
    heat_pump_pro_com = data['process_commodity'][
        data['process_commodity'].index.get_level_values(1) == 'heatpump_air']
    heat_pump_pro_com.rename(index={'electricity': 'electricity_hp'}, level=2, inplace=True)
    data['process_commodity'].drop((year, 'heatpump_air', 'electricity', 'In'), inplace=True, axis=0)
    data['process_commodity'].drop((year, 'heatpump_air', 'common_heat', 'Out'), inplace=True, axis=0)
    data['process_commodity'].drop((year, 'heatpump_air', 'electricity-reactive', 'In'), inplace=True, axis=0)
    data['process_commodity'] = pd.concat([data['process_commodity'], heat_pump_pro_com])

    try:
        booster_pro_com = data['process_commodity'][
            data['process_commodity'].index.get_level_values(1) == 'heatpump_booster']
        booster_pro_com.rename(index={'electricity': 'electricity_hp'}, level=2, inplace=True)
        data['process_commodity'].drop((year, 'heatpump_booster', 'electricity', 'In'), inplace=True, axis=0)
        data['process_commodity'].drop((year, 'heatpump_booster', 'common_heat', 'Out'), inplace=True, axis=0)
        data['process_commodity'] = pd.concat([data['process_commodity'], booster_pro_com])
    except:
        pass

    charging_stations_pro_com = data['process_commodity'][
        data['process_commodity'].index.get_level_values(1).str.startswith('charging')]
    charging_stations_pro_com = charging_stations_pro_com.rename(index={'electricity': 'electricity_bev'},
                                                                 level=2)
    # drop existing charging stations
    unique_charging_stations = [ucs for (stf, ucs, com, direction) in data['process_commodity'].index \
                                if ucs.startswith('charging_station') and direction == 'In']
    for ucs in unique_charging_stations:
        data['process_commodity'].drop((year, ucs, 'electricity', 'In'), inplace=True, axis=0)
        data['process_commodity'].drop((year, ucs, 'mobility' + ucs[16:], 'Out'), inplace=True, axis=0)
    data['process_commodity'] = pd.concat([data['process_commodity'], charging_stations_pro_com])

    return data

def add_elec_to_hp_bev_process(data):
    year = date.today().year

    # add process elec_hp_to_usable to all buildings (same properties as curtailment)
    elec_to_hp_usable_pro = data['process'][
        data['process'].index.get_level_values(2) == 'curtailment']
    elec_to_hp_usable_pro = elec_to_hp_usable_pro.copy(deep=True)
    elec_to_hp_usable_pro.rename(index={'curtailment': 'elec_to_elec_hp'}, level=2, inplace=True)
    data['process'] = pd.concat([data['process'], elec_to_hp_usable_pro])
    data['process'].loc[pd.IndexSlice[year, :, 'elec_to_elec_hp'], ('var-cost')] = 0.01
    # one cent offset, to motivate always
    # buying the electricity_hp and electricity_bev instead of  buying electricity indirectly

    data['process_commodity'].loc[year, 'elec_to_elec_hp', 'electricity', 'In'] = (1, np.nan)
    data['process_commodity'].loc[year, 'elec_to_elec_hp', 'electricity_hp', 'Out'] = (1, np.nan)

    # same procedure for elec_bev
    elec_to_bev_usable_pro = data['process'][
        data['process'].index.get_level_values(2) == 'curtailment']
    elec_to_bev_usable_pro = elec_to_bev_usable_pro.copy(deep=True)
    elec_to_bev_usable_pro.rename(index={'curtailment': 'elec_to_elec_bev'}, level=2, inplace=True)
    data['process'] = pd.concat([data['process'], elec_to_bev_usable_pro])
    data['process'].loc[pd.IndexSlice[year, :, 'elec_to_elec_bev'], ('var-cost')] = 0.01

    # one cent offset, to motivate always
    # buying the electricity_hp and electricity_bev instead of buying electricity and converting indirectly

    data['process_commodity'].loc[year, 'elec_to_elec_bev', 'electricity', 'In'] = (1, np.nan)
    data['process_commodity'].loc[year, 'elec_to_elec_bev', 'electricity_bev', 'Out'] = (1, np.nan)

    return data


def add_curtailment_heat(data):
    year = date.today().year

    # add process curtailment_heat to all buildings (same properties as curtailment)
    curtailment_heat_pro = data['process'][data['process'].index.get_level_values(2) == 'curtailment']
    curtailment_heat_pro = curtailment_heat_pro.copy(deep=True)
    curtailment_heat_pro.rename(index={'curtailment': 'curtailment_heat'}, level=2, inplace=True)
    data['process'] = pd.concat([data['process'], curtailment_heat_pro])
    data['process_commodity'].loc[year, 'curtailment_heat', 'space_heat', 'In'] = (1, np.nan)

    return data


def add_hp_bev_flows(data):
    ### copy transmission lines with resistance to model transmission lines for reactive power flows

    heatpump_flow_lines = data['transmission'][data['transmission'].index.get_level_values(4) == 'electricity']
    heatpump_flow_lines = heatpump_flow_lines.copy(deep=True)
    heatpump_flow_lines.rename(index={'electricity': 'electricity_hp'}, level=4, inplace=True)
    ### set costs to zero as lines are not really built -

    heatpump_flow_lines.loc[:, ['inv-cost', 'fix-cost', 'var-cost', 'decom-saving']] *= 0
    ### concat new line data
    data['transmission'] = pd.concat([data['transmission'], heatpump_flow_lines])

    bev_flow_lines = data['transmission'][data['transmission'].index.get_level_values(4) == 'electricity']
    bev_flow_lines = bev_flow_lines.copy(deep=True)
    bev_flow_lines.rename(index={'electricity': 'electricity_bev'}, level=4, inplace=True)

    ### set costs to zero as lines are not really built -
    bev_flow_lines.loc[:, ['inv-cost', 'fix-cost', 'var-cost', 'decom-saving']] *= 0
    ### concat new line data
    data['transmission'] = pd.concat([data['transmission'], bev_flow_lines])
    return data


def distributed_building_specific_import_processes(data, mode):
    # add all building-specific import options for uncoordinated planning
    year = date.today().year
    demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    demand_nodes.append(data['mainbusbar_node'])

    for building in demand_nodes:
        data['commodity'].loc[year, building, 'electricity_feed_in', 'Sell'] = (data['commodity']['price'].
                                                                                loc[:, :, 'electricity_feed_in',
                                                                                :].iloc[0], np.inf, np.inf)
        data['commodity'].loc[year, building, 'electricity_import', 'Buy'] = (data['commodity']['price'].
                                                                              loc[:, :, 'electricity_import',
                                                                              :].iloc[0], np.inf, np.inf)

        data['process'].loc[year, building, 'feed_in'] = data['process'].loc[year, data['trafo_node'], 'feed_in']
        data['process'].loc[year, building, 'import'] = data['process'].loc[
            year, data['trafo_node'], 'import']

        data['process'].loc[year, building, 'feed_in']['cap-up'] = 999
        data['process'].loc[year, building, 'feed_in']['inst-cap'] = 999
        data['process'].loc[year, building, 'import']['cap-up'] = 999
        data['process'].loc[year, building, 'import']['inst-cap'] = 999

        # data_uncoordinated['commodity'].loc[year, building, 'reactive-corr','Stock'] = (1, np.inf, np.inf)
        data['process'].loc[year, building, 'Q_feeder_central'] = data['process'].loc[
            year, data['mainbusbar_node'], 'Q_feeder_central']
        data['process'].loc[year, building, 'Q_feeder_central']['cap-up'] = 999
        data['process'].loc[year, building, 'Q_feeder_central']['inst-cap'] = 999

        # add the import processes for each 14a commodity too
        if mode['14a']:
            data['commodity'].loc[year, building, 'electricity_hp_import', 'Buy'] = (data['commodity']['price'].
                                                                                     loc[:, :,
                                                                                     'electricity_import',
                                                                                     :].iloc[0], np.inf, np.inf)
            data['process'].loc[year, building, 'import_hp'] = data['process'].loc[
                year, data['trafo_node'], 'import_hp']
            data['process'].loc[year, building, 'import_hp']['cap-up'] = 999
            data['process'].loc[year, building, 'import_hp']['inst-cap'] = 999
            data['commodity'].loc[year, building, 'electricity_bev_import', 'Buy'] = (data['commodity']['price'].
                                                                                      loc[:, :,
                                                                                      'electricity_import',
                                                                                      :].iloc[0], np.inf, np.inf)
            data['buy_sell_price']['electricity_bev_import'] = data['buy_sell_price']['electricity_import'].values
            data['process'].loc[year, building, 'import_bev'] = data['process'].loc[
                year, data['trafo_node'], 'import']

            bui_cs_cap = data['process'].loc[year, building, :]
            bui_cs_cap = bui_cs_cap[bui_cs_cap.index.get_level_values(0).str.startswith('charging')][
                'inst-cap'].sum()
            data['process'].loc[year, building, 'import_bev']['cap-up'] = bui_cs_cap
            data['process'].loc[year, building, 'import_bev']['inst-cap'] = bui_cs_cap
    return data

def unelectrify_heat_in_random(data, electrification):
    year = date.today().year
    demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    random.seed(1)
    unelectrified_heat_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1 - electrification)))
    data['process'].loc[(year, unelectrified_heat_nodes, 'heatpump_air'), 'cap-up'] = 0

    # instead of HP, provide heat by another means, e.g. gas boiler
    data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'price'] = 0.12  # assumed gas price
    data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'max'] = np.inf # allow gas supply
    data['commodity'].loc[(year, unelectrified_heat_nodes, 'common_heat'), 'maxperhour'] = np.inf # allow gas supply
    return data

def remove_pv_in_random(data, electrification):
    year = date.today().year
    demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    random.seed(2)
    disable_pv_nodes = random.sample(demand_nodes, int(len(demand_nodes) * (1 - electrification)))

    data['process'].loc[((data['process'].index.get_level_values(1).isin(disable_pv_nodes)) &
                         (data['process'].index.get_level_values(2).str.startswith('Rooftop PV'))), 'cap-up'] = 0
    return data

def unelectrify_mobility_in_random(data, electrification):
    year = date.today().year
    demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    random.seed(3)
    all_cars = [col for col in data['demand'].columns if col[1].startswith('mobility')]
    unelectrified_cars = random.sample(all_cars, int(len(all_cars) * (1 - electrification)))

    for (site, car) in unelectrified_cars:
        car_idx = car[-1]
        data['process'].loc[(year, site, 'charging_station' + car_idx), 'inst-cap'] = 0
        data['process'].loc[
            (year, site, 'charging_station' + car_idx), 'cap-up'] = 0  # set charging_station capacity to zero
        data['commodity'].loc[(year, site, 'mobility' + car_idx, 'Demand'), 'price'] = 0.6  # 60 cent for public charging
        data['commodity'].loc[(year, site, 'mobility' + car_idx, 'Demand'), 'max'] = np.inf
        data['commodity'].loc[(year, site, 'mobility' + car_idx,
                               'Demand'), 'maxperhour'] = np.inf  # add stock availabiltiy for mobility commodity
    return data

def adopt_variable_tariffs(data, vartariff_nodes):
    year = date.today().year
    demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']

    # rename import to import_var process for those nodes
    for building in vartariff_nodes:
        import_pro = data['process'][
            data['process'].index.get_level_values(2) == 'import']
        import_pro = import_pro[import_pro.index.get_level_values(1) == building]
        import_pro = import_pro.copy(deep=True)
        import_pro.rename(index={'import': 'import_var'}, level=2, inplace=True)
        data['process'].drop((year, building, 'import'), inplace=True, axis=0)
        data['process'] = pd.concat([data['process'], import_pro])

    # rename commodities "electricity_import" to "electricity_import_var" for those nodes
    for building in vartariff_nodes:
        electricity_import_com = data['commodity'][
            data['commodity'].index.get_level_values(2) == 'electricity_import']
        electricity_import_com = electricity_import_com[electricity_import_com.index.get_level_values(1) == building]
        electricity_import_com = electricity_import_com.copy(deep=True)
        electricity_import_com.rename(index={'electricity_import': 'electricity_import_var'}, level=2, inplace=True)
        data['commodity'].drop((year, building, 'electricity_import', 'Buy'), inplace=True, axis=0)
        data['commodity'] = pd.concat([data['commodity'], electricity_import_com])

    # add process-commodity for import_var (same as import, just different import commodity with variable prices)
    import_var_pro_com = data['process_commodity'][
        data['process_commodity'].index.get_level_values(1) == 'import']
    import_var_pro_com = import_var_pro_com.copy(deep=True)
    import_var_pro_com.rename(index={'electricity_import': 'electricity_import_var'}, level=2, inplace=True)
    import_var_pro_com.rename(index={'import': 'import_var'}, level=1, inplace=True)
    data['process_commodity'] = pd.concat([data['process_commodity'], import_var_pro_com])
    return data

def set_curtailment_limits(data_grid_plan):
    # set limits to DSO-side grid curtailment using the "availability" functionality
    # (it cannot be greater than the feed-in (minus demand) at each hour!)
    year = date.today().year
    demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns
                    if demand == 'electricity']
    try:
        demand_nodes.remove(data_grid_plan['trafo_node'])
    except ValueError:
        pass
    try:
        demand_nodes.remove(data_grid_plan['mainbusbar_node'])
    except ValueError:
        pass

    for building in demand_nodes:
        data_grid_plan['process'].loc[(year, building, 'curtailment'),'inst-cap'] = 1
        data_grid_plan['process'].loc[(year, building, 'curtailment'),'cap-up'] = 1

        data_grid_plan['availability'][(building, 'curtailment')] = - (data_grid_plan['demand'][
                                                                                        (building,
                                                                                         'electricity')])
        data_grid_plan['availability'][(building, 'curtailment')][ \
            data_grid_plan['availability'][(building, 'curtailment')] < 0] = 0
    return data_grid_plan


### START - HOODS-Grid routines

def delete_solar_supim_timeseries(data_grid_plan, building):
    bui_solar_comms = [solcom for (bui, solcom) in data_grid_plan['supim'].columns
                       if solcom.startswith('solar') and bui == building]
    for scs in bui_solar_comms:
        data_grid_plan['supim'].drop((building, scs), inplace=True, axis=1)
    return data_grid_plan

def delete_charging_station_eff_factors(data_grid_plan, building):
    year = date.today().year

    bui_charging_stations = [cs for (stf, bui, cs) in data_grid_plan['process'].index
                             if cs.startswith('charging_station') and bui == building
                             and stf == year]
    for bcs in bui_charging_stations:
        data_grid_plan['eff_factor'].drop((building, bcs), inplace=True, axis=1)
    return data_grid_plan

def delete_heatpump_eff_factors(data_grid_plan, building):
    data_grid_plan['eff_factor'].drop((building, 'heatpump_air'), inplace=True, axis=1)
    return data_grid_plan

def delete_non_electric_demand(data_grid_plan, building):
    #delete heat demands
    data_grid_plan['demand'].drop((building, 'space_heat'), inplace=True, axis=1)
    data_grid_plan['demand'].drop((building, 'water_heat'), inplace=True, axis=1)

    #delete all mobility demands
    bui_mob_demands = [dem for (bui, dem) in data_grid_plan['demand'].columns
                       if dem.startswith('mobility') and bui == building]
    for mob_demand in bui_mob_demands:
        data_grid_plan['demand'].drop((building, mob_demand), inplace=True, axis=1)
    return data_grid_plan

def shift_demand_to_elec(data_grid_plan, building, prob_cluster, mode, vartariff, vartariff_nodes=None):
    year = date.today().year

    if mode['14a']:
        # 14a mode: define electricity, electricity_hp, and electricity_bev demands separately.
        if vartariff > 0:
            # vartariff on: include import AND import_var for the participating buildings (otherwise only import)
            if building in vartariff_nodes: # buildings participating in vartariff
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob_cluster._result['tau_pro'].loc[:, year, building, 'import_var'].iloc[1:]
                        - prob_cluster._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])
            else: # buildings NOT participating in vartariff
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob_cluster._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                        - prob_cluster._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

        else: # vartariff off: only include import, not import_var
            data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                    prob_cluster._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                    - prob_cluster._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

        # demand for electricity_hp, initialize
        data_grid_plan['demand'][(building, 'electricity_hp')] = copy.deepcopy(
            data_grid_plan['demand'][(building, 'electricity')])
        # demand for electricity_hp, set
        data_grid_plan['demand'].loc[year, :][(building, 'electricity_hp')].iloc[1:] = \
            prob_cluster._result['tau_pro'].loc[:, year, building, 'import_hp'].iloc[1:]

        # demand for electricity_bev, initialize
        data_grid_plan['demand'][(building, 'electricity_bev')] = copy.deepcopy(
            data_grid_plan['demand'][(building, 'electricity')])
        # demand for electricity_bev, set
        data_grid_plan['demand'].loc[year, :][(building, 'electricity_bev')].iloc[1:] = \
            prob_cluster._result['tau_pro'].loc[:, year, building, 'import_bev'].iloc[1:]
    else:
        # no 14a: define only electricity demand (not the 14a commodities such as electricity_hp or electricity_bev).
        if vartariff > 0:
            if building in vartariff_nodes:
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob_cluster._result['tau_pro'].loc[:, year, building, 'import_var'].iloc[1:]
                        - prob_cluster._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])
            else:
                data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                        prob_cluster._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                        - prob_cluster._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])
        else:
            data_grid_plan['demand'].loc[year, :][(building, 'electricity')].iloc[1:] = (
                    prob_cluster._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                    - prob_cluster._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

    # define reactive power demand as Q_feeder_central values from HOODS-Bui
    data_grid_plan['demand'].loc[year, :][(building, 'electricity-reactive')].iloc[1:] = \
        prob_cluster._result['e_pro_out'] \
            .loc[:, year, building, 'Q_feeder_central', 'electricity-reactive']

    return data_grid_plan

def delete_processes_for_hoods_grid(data_grid_plan, building, grid_curtailment):
    ### delete all processes besides Q-compensation, import and feed-in
    year = date.today().year

    #delete all pv processes
    bui_rooftop_pvs = [pv for (stf, bui, pv) in data_grid_plan['process'].index
                       if pv.startswith('Rooftop PV') and bui == building
                       and stf == year]
    for pvs in bui_rooftop_pvs:
        data_grid_plan['process'].drop((year, building, pvs), inplace=True, axis=0)

    # delete heat-related processes
    data_grid_plan['process'].drop((year, building, 'Heat_dummy_space'), inplace=True, axis=0)
    data_grid_plan['process'].drop((year, building, 'Heat_dummy_water'), inplace=True, axis=0)
    data_grid_plan['process'].drop((year, building, 'heatpump_air'), inplace=True, axis=0)
    try:
        data_grid_plan['process'].drop((year, building, 'heatpump_booster'), inplace=True, axis=0)
    except:
        pass

    # delete charging stations
    bui_charging_stations = [cs for (stf, bui, cs) in data_grid_plan['process'].index
                             if cs.startswith('charging_station') and bui == building and stf == year]
    for bcs in bui_charging_stations:
        data_grid_plan['process'].drop((year, building, bcs), inplace=True, axis=0)

    # delete curtailment, if a DSO-side curtailment is not allowed
    if not grid_curtailment:
        data_grid_plan['process'].drop((year, building, 'curtailment'), inplace=True, axis=0)
    else:
        # if a DSO-side PV curtailment is allowed, set a variable cost to it (DSO pays FIT to building)
        data_grid_plan['process'].loc[(year, building, 'curtailment'), 'var-cost'] = \
            data_grid_plan['buy_sell_price']['electricity_feed_in'].values[-1]

    # delete heat slack
    data_grid_plan['process'].drop((year, building, 'Slack_heat'), inplace=True, axis=0)
    return data_grid_plan

def delete_commodities_for_hoods_grid(data_grid_plan, building):
    year = date.today().year

    # delete heat commodities (demand and stocK)
    data_grid_plan['commodity'].drop((year, building, 'space_heat', 'Demand'), inplace=True, axis=0)
    data_grid_plan['commodity'].drop((year, building, 'water_heat', 'Demand'), inplace=True, axis=0)
    data_grid_plan['commodity'].drop((year, building, 'common_heat', 'Stock'), inplace=True, axis=0)

    # delete solar supim commodities
    bui_solar_comms = [solcom for (bui, solcom) in data_grid_plan['supim'].columns
                       if solcom.startswith('solar') and bui == building]
    for scs in bui_solar_comms:
        data_grid_plan['commodity'].drop((year, building, scs, 'SupIm'), inplace=True, axis=0)

    # delete mobility demand commodities
    bui_mob_commodities = [com for (stf, sit, com, typ) in data_grid_plan['commodity'].index
                           if com.startswith('mobility') and sit == building]
    for com in bui_mob_commodities:
        data_grid_plan['commodity'].drop((year, building, com, 'Demand'), inplace=True, axis=0)
    return data_grid_plan


def delete_procoms_for_hoods_grid(data_grid_plan, grid_curtailment):
    year = date.today().year

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
    return data_grid_plan




def add_hp_bev_regulation_process(data_grid_plan, data_bui, var_cost=0):
    year = date.today().year
    demand_nodes = [sit for (sit, demand) in data_grid_plan['demand'].columns
                    if demand == 'electricity']
    try:
        demand_nodes.remove(data_grid_plan['trafo_node'])
    except ValueError:
        pass
    try:
        demand_nodes.remove(data_grid_plan['mainbusbar_node'])
    except ValueError:
        pass

    # GENERAL EXPLANATION:
    # 1. the regulation processes consumer "regulate_com" commodity, which costs exactly the same as import electricity,
    # plus a very small process variable cost (var_cost; default: 0.0001)
    # 2. there are two regulation processes: "hp_14a_steuve_regulate" and "bev_14a_steuve_regulate", for HP and BEV.
    # 3. these processes are only available at the time steps, where the demand for 14a commodities are higher than 4.2 kW
    # per HP or BEV. this is satisfied by setting its capacity to 1, and the availability to the surplus above 4.2 kW.
    # (if in a time step the HP imports 6 kW, then the availability will be equal to 6 - 4.2 = 1.8 kW)
    # if this surplus is negative (demand < 4.2 kW), the availability will be set to zero (no regulation possible).
    # 4. these processes generate the corresponding 14a commodity, effectively reducing its import from the grid
    # (:= reduced grid load)

    for building in demand_nodes:
        # HP downregulation process
        data_grid_plan['commodity'].loc[year, building, 'regulate_com', 'Buy'] = (1, np.inf, np.inf)
        data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate'] = copy.deepcopy(
            data_grid_plan['process'].loc[
                year, data_grid_plan['trafo_node'], 'import'])
        data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['inst-cap'] = 1
        data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['cap-up'] = 1
        data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['var-cost'] = var_cost
        data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')] = (data_grid_plan['demand'][
                                                                                (building,
                                                                                 'electricity_hp')] - 4.2)
        data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')][ \
            data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')] < 0] = 0

        # BEV downregulation process
        data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate'] = copy.deepcopy(
            data_grid_plan['process'].loc[
                year, data_grid_plan['trafo_node'], 'import'])
        data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate']['inst-cap'] = 1
        data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate']['cap-up'] = 1
        data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate']['var-cost'] = var_cost
        bui_car_count = data_bui['process'].loc[year, building, :]
        bui_car_count = len(bui_car_count[bui_car_count.index.get_level_values(0).str.startswith('charging')])
        data_grid_plan['availability'][(building, 'bev_14a_steuve_regulate')] = (data_grid_plan['demand'][
                                                                                     (building,
                                                                                      'electricity_bev')] - 4.2 * bui_car_count)
        data_grid_plan['availability'][(building, 'bev_14a_steuve_regulate')][ \
            data_grid_plan['availability'][(building, 'bev_14a_steuve_regulate')] < 0] = 0

    data_grid_plan['buy_sell_price']['regulate_com'] = data_grid_plan['buy_sell_price'][
                                                           'electricity_import'] * 1.00
    data_grid_plan['process_commodity'].loc[year, 'hp_14a_steuve_regulate', 'regulate_com', 'In'] = (
        1, np.nan)
    data_grid_plan['process_commodity'].loc[year, 'bev_14a_steuve_regulate', 'regulate_com', 'In'] = (
        1, np.nan)
    data_grid_plan['process_commodity'].loc[year, 'hp_14a_steuve_regulate', 'electricity_hp', 'Out'] = \
        (1, np.nan)
    data_grid_plan['process_commodity'].loc[year, 'hp_14a_steuve_regulate', 'electricity-reactive', 'Out'] = \
        (np.tan(np.arccos(data_grid_plan['global_prop'].loc[year, 'PF_HP']['value'])), np.nan)
    data_grid_plan['process_commodity'].loc[year, 'bev_14a_steuve_regulate', 'electricity_bev', 'Out'] = \
        (1, np.nan)

    return data_grid_plan


### START - HOODS-Bui-React routines
def limit_hp_for_hoods_bui_react(data_hp_react, data, building, prob_cluster, prob_grid_plan):

    # replace zero capacities by 0.01 to avoid division by zero later
    cap_hp = (0.01 if prob_cluster._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0] == 0
              else prob_cluster._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0])
    cap_booster = (0.01 if prob_cluster._result['cap_pro'].loc[:, building, 'heatpump_booster'].values[0] == 0
                   else prob_cluster._result['cap_pro'].loc[:, building, 'heatpump_booster'].values[0])


    # See equations (2.89) and (2.91) in the dissertation of Soner Candas for the interpretation of the following
    # operations

    # the capacity limitations are imposed using the "availability" feature
    # initialize availabilities
    data_hp_react['availability'][(building, 'heatpump_air')] = data_hp_react['availability'][
        (data['trafo_node'], 'import')].values
    data_hp_react['availability'][(building, 'heatpump_booster')] = data_hp_react['availability'][
        (data['trafo_node'], 'import')].values

    if prob_cluster._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0] <= 4.2: # Case 1
        # no restrictions if cap is smaller than 4.2
        data_hp_react['availability'][(building, 'heatpump_air')].iloc[1:] = 1 # Case 1, no restriction
        if (prob_cluster._result['cap_pro'].loc[:, building, 'heatpump_air'].values[0] + # Case 1.1, no restriction
            prob_cluster._result['cap_pro'].loc[:, building, 'heatpump_booster'].values[0]) <= 4.2:
            # total cap is smaller too, no restriction on peaker heater.
            data_hp_react['availability'][(building, 'heatpump_booster')].iloc[1:] = 1
        else:
            # total cap exceeds 4.2 (case 1.2), peaker may be curtailed:
            data_hp_react['availability'][(building, 'heatpump_booster')].iloc[1:] = \
                (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                 'electricity_hp'] <= 0) * 1 + \
                (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                 'electricity_hp'] > 0) * \
                (prob_cluster._result['e_pro_in'].loc[
                 :, :, building, 'heatpump_booster', 'electricity_hp'].values -
                 prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
                 'electricity_hp'].values) / cap_booster

    else: # heat pump capacity larger than 4.2, regulation possible (Case 2)
        # restrict main HP cap (equation 2.90)
        data_hp_react['availability'][(building, 'heatpump_air')].iloc[1:] = \
            (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
             'electricity_hp'] <= prob_cluster._result['e_pro_in'].loc[
                                  :, :, building, 'heatpump_booster', 'electricity_hp'].values) * 1 + \
            (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
             'electricity_hp'] > prob_cluster._result['e_pro_in'].loc[
                                 :, :, building, 'heatpump_booster', 'electricity_hp'].values) * \
            (prob_cluster._result['e_pro_in'].loc[
             :, :, building, 'heatpump_air', 'electricity_hp'].values -
             prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
             'electricity_hp'] +
             prob_cluster._result['e_pro_in'].loc[
             :, :, building, 'heatpump_booster', 'electricity_hp'].values) / cap_hp

        # restrict HP peaker cap (equation 2.91)
        data_hp_react['availability'][(building, 'heatpump_booster')].iloc[1:] = \
            (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
             'electricity_hp'] == 0) * 1 + \
            ((prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
              'electricity_hp'] > 0) &
             (prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
              'electricity_hp'] <= prob_cluster._result['e_pro_in'].loc[
                                   :, :, building, 'heatpump_booster', 'electricity_hp'].values)) * \
            (prob_cluster._result['e_pro_in'].loc[
             :, :, building, 'heatpump_booster', 'electricity_hp'].values -
             prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
             'electricity_hp']) / cap_booster + \
            ((prob_grid_plan._result['e_pro_out'].loc[:, :, building, 'hp_14a_steuve_regulate',
              'electricity_hp'] >
              prob_cluster._result['e_pro_in'].loc[:, :, building, 'heatpump_booster', 'electricity_hp'].values) * 0)
    return data_hp_react

def limit_bev_for_hoods_bui_react(data_hp_react, data, building, prob_cluster, prob_grid_plan, data_grid_plan):
    # See equation 2.92 in the dissertation of Soner Candas
    year = date.today().year
    bui_charging_stations = [cs for (stf, bui, cs) in data['process'].index
                             if cs.startswith('charging_station') and bui == building
                             and stf == year]
    for cs in bui_charging_stations:
        data_hp_react['availability'][(building, cs)] = data_hp_react['availability'][
            (data['trafo_node'], 'import')].values
        if prob_cluster._result['cap_pro'].loc[year, building, cs] == 0:
            data_hp_react['availability'][(building, cs)].iloc[1:] = 0
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
                prob_cluster._result['cap_pro'].loc[year, building, cs] / len(
                    bui_charging_stations)
    return data_hp_react

################################## END LVDS ##################################