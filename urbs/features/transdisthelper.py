from urbs.identify import *
import copy
import math
import numpy as np
import os
from datetime import datetime, date


### main module to define and concatenate transmission-distribution data
def create_transdist_data(data, microgrid_data_initial, cross_scenario_data):
    if 'transdist_share' not in data:
        data['transdist_share'] = pd.Series([1])

    mode = identify_mode(data)
    ### read standard load profile from csv
    loadprofile_BEV = pd.read_csv(os.path.join(os.getcwd(), 'Input', 'Microgrid_types', 'loadprofile_BEV.csv'))
    loadprofile_BEV = loadprofile_BEV.set_index(data['demand'].index).squeeze()
    ### prepare dicts for the demand shift from distribution to transmission level
    mobility_transmission_shift = dict()
    heat_transmission_shift = dict()
    ### read the efficiency at the transmission-distribution interface to consider within demand shift
    transdist_eff = \
        microgrid_data_initial[0]['transmission'].loc[pd.IndexSlice[:, 'top_region_dummy', :, 'tdi', :], 'eff'].values[
            0]
    ### define lists to be used in loops
    microgrid_set_list = build_set_list(data)
    microgrid_multiplicator_list = build_multiplicator_list(data)

    ### process microgrid data for every region and microgrid type
    for set_number, set in enumerate(microgrid_set_list):  # top region microgrid setting
        top_region_name = data['site'].index.get_level_values(1)[set_number]
        n = 0
        for type_nr, quantity_nr in enumerate(set):
            microgrid_entries = microgrid_data_initial[type_nr]['site'].index.get_level_values(1)
            microgrid_data_input = copy.deepcopy(microgrid_data_initial[type_nr])
            for entry in microgrid_entries:
                ### microgrids are derived from the predefined microgrid types and setting
                create_microgrid_data(microgrid_data_input, entry, n, top_region_name)
            n += 1
            ### scale capacities, commodities, demand, areas and the loadprofile with multiplicator number of the microgrid
            microgrid_data_input, demand_shift = multiplicator_scaling(mode, data, microgrid_data_input,
                                                                       microgrid_multiplicator_list, set_number,
                                                                       type_nr)
            shift_demand = data['global_prop'].loc[pd.IndexSlice[:, 'shift_demand'], 'value'].iloc[0]
            ### shift demand from transmission level to distribution level
            if shift_demand:
                data, mobility_transmission_shift, heat_transmission_shift = shift_demand(data, microgrid_data_input,
                                                                                          set_number,
                                                                                          type_nr, demand_shift,
                                                                                          loadprofile_BEV,
                                                                                          top_region_name,
                                                                                          mobility_transmission_shift,
                                                                                          heat_transmission_shift,
                                                                                          transdist_eff)
            ### copy SupIm data from respective state to the microgrid within that state
            copy_SupIm_data(data, microgrid_data_input, top_region_name)
            ### model additional transmission lines for the reactive power
            add_reactive_transmission_lines(microgrid_data_input)
            ### add reactive output ratios for ac sites
            add_reactive_output_ratios(microgrid_data_input)
            ### concatenate main data with microgrid data with
            concatenate_with_micros(data, microgrid_data_input)
    if data['transdist_share'].values[0] == 1 and shift_demand:
        store_additional_demand(cross_scenario_data, mobility_transmission_shift, heat_transmission_shift)
    return data, cross_scenario_data


def build_set_list(data):
    transdist_dict = data['site'].drop(columns=['base-voltage', 'area'], axis=1).to_dict()
    microgrid_set = transdist_dict['microgrid-setting']
    microgrid_set_list = []
    for item in microgrid_set:
        if type(microgrid_set[item]) == int:
            microgrid_set[item] = str(microgrid_set[item])
        microgrid_set_list.append(list(map(int, microgrid_set[item].split(','))))
    return microgrid_set_list


def build_multiplicator_list(data):
    transdist_dict = data['site'].drop(columns=['base-voltage', 'area'], axis=1).to_dict()
    microgrid_multiplicator = transdist_dict['multiplicator']
    microgrid_multiplicator_list = []
    for item in microgrid_multiplicator:
        if type(microgrid_multiplicator[item]) == int:
            microgrid_multiplicator[item] = str(microgrid_multiplicator[item])
        microgrid_multiplicator_list.append(list(map(int, microgrid_multiplicator[item].split(','))))
    return microgrid_multiplicator_list


### Rename indices to allocate microgrid data to respective region and enable direct connection with new
### transport model line representing the transformer interface between both levels
def create_microgrid_data(microgrid_data_input, entry, n, top_region_name):
    microgrid_data_input['site'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['commodity'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['process'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['process_commodity'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['demand'].rename(
        columns={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    microgrid_data_input['supim'].rename(
        columns={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    microgrid_data_input['storage'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['dsm'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['buy_sell_price'].rename(
        columns={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    microgrid_data_input['eff_factor'].rename(
        columns={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    ### for transmission data indexes on two levels must be changed
    microgrid_data_input['transmission'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['transmission'].rename(
        index={entry: entry + '_' + str(n + 1) + '_' + top_region_name}, level=2, inplace=True)

    ### add transmission line from microgrids to top level region
    microgrid_data_input['transmission'].rename(
        index={'top_region_dummy': top_region_name}, level=1, inplace=True)
    microgrid_data_input['transmission'].rename(
        index={'top_region_dummy': top_region_name}, level=2, inplace=True)
    return microgrid_data_input


### Scale microgrid types according to multiplicator list
def multiplicator_scaling(mode, data, microgrid_data_input, microgrid_multiplicator_list, set_number, type_nr):
    ### determine multiplicator for region and microgrid type
    multi = data['transdist_share'].values[0] * microgrid_multiplicator_list[set_number][type_nr]
    ### base voltage is scaled with the root value of the multiplicator for a correct consideration within the voltage rule
    microgrid_data_input['site'].loc[:, 'base-voltage'] *= math.sqrt(multi)
    ### scale other relevant quantities
    microgrid_data_input['commodity'].loc[:, 'max':'maxperhour'] *= multi
    microgrid_data_input['process'].loc[:, ['inst-cap', 'cap-lo', 'cap-up', 'cap-block']] *= multi
    microgrid_data_input['transmission'].loc[:, ['inst-cap', 'cap-lo', 'cap-up', 'tra-block']] *= multi
    microgrid_data_input['storage'].loc[:, ['inst-cap-c', 'cap-lo-c', 'cap-up-c', 'inst-cap-p', 'cap-lo-p',
                                            'cap-up-p', 'c-block', 'p-block']] *= multi
    microgrid_data_input['dsm'].loc[:, 'cap-max-do':'cap-max-up'] *= multi
    ### if tsam activated postpone demand scaling to reduce number of tsam input timeseries, but still pass demand shift
    if mode['tsam'] == True:
        demand_shift = microgrid_data_input['demand'] * multi
    ### otherwise also scale demand data
    if mode['tsam'] == False:
        microgrid_data_input['demand'] *= multi
        demand_shift = microgrid_data_input['demand']
    return microgrid_data_input, demand_shift


### Shift demand between scenarios for better comparability
def shift_demand(data, microgrid_data_input, set_number, type_nr, demand_shift, loadprofile_BEV, top_region_name,
                 mobility_transmission_shift, heat_transmission_shift, transdist_eff):
    ### subtract private electricity demand at distribution level (increased by tdi efficiency) from transmission level considering line losses
    data['demand'].iloc[:, set_number] -= demand_shift.loc[:, pd.IndexSlice[:, 'electricity']].sum(
        axis=1) / transdist_eff
    if data['transdist_share'].values[0] == 1:
        ### store scaled full mobility and heat demand for 100% active distribution network for subsequent scenarios
        mobility_transmission_shift[(top_region_name, type_nr)] = loadprofile_BEV * demand_shift.loc[:, pd.IndexSlice[:,
                                                                                                        'mobility']].sum().sum() / transdist_eff
        COP_ts = microgrid_data_input['eff_factor'].loc[:, pd.IndexSlice[:, 'heatpump_air']].iloc[:,
                 0].squeeze()  # get COP timeseries to transform hourly heat to electricity demand
        heat_transmission_shift[(top_region_name, type_nr)] = demand_shift.loc[:, pd.IndexSlice[:, 'heat']].sum(
            axis=1).divide(COP_ts).fillna(0) / transdist_eff
    return data, mobility_transmission_shift, heat_transmission_shift


### Copy capacity factor timeseries from top level region to all microgrids within that region
def copy_SupIm_data(data, microgrid_data_input, top_region_name):
    for col in microgrid_data_input['supim'].columns:
        microgrid_data_input['supim'].loc[:, col] = data['supim'].loc[:, (top_region_name, col[1])]
    return microgrid_data_input


### Model new imaginary lines to enable reactive power flow on respective lines with defined resistance
def add_reactive_transmission_lines(microgrid_data_input):
    ### copy transmission lines with resistance to model transmission lines for reactive power flows
    reactive_transmission_lines = microgrid_data_input['transmission'][
        microgrid_data_input['transmission'].index.get_level_values(4) == 'electricity'][
        ~microgrid_data_input['transmission'].loc[:, 'resistance'].isna()]
    reactive_transmission_lines = reactive_transmission_lines.copy(deep=True)
    reactive_transmission_lines.rename(index={'electricity': 'electricity-reactive'}, level=4, inplace=True)
    ### set costs to zero as lines are not really built -

    reactive_transmission_lines.loc[:, ['inv-cost', 'fix-cost', 'var-cost', 'decom-saving']] *= 0
    ### concat new line data
    microgrid_data_input['transmission'] = pd.concat(
        [microgrid_data_input['transmission'], reactive_transmission_lines], sort=True)
    return microgrid_data_input


#######
def add_import_hp_bev_process(data, mode):
    year = date.today().year
    if mode['evu_sperre'] or mode['14a_steuve']:  # add import hp to Trafostation_OS
        data['process'].loc[year, data['trafo_node'], 'import_hp'] = \
            data['process'].loc[year, data['trafo_node'], 'import'].copy(deep=True)
        data['process_commodity'].loc[year, 'import_hp', 'electricity_hp_import', 'In'] = (1, np.nan)
        data['process_commodity'].loc[year, 'import_hp', 'electricity_hp', 'Out'] = (1, np.nan)

        data['buy_sell_price']['electricity_hp_import'] = \
            data['buy_sell_price']['electricity_import'] * \
            data['global_prop'].loc[pd.IndexSlice[:, 'hp_heizstrom_mult'], 'value'].iloc[0]
        data['commodity'].loc[year, data['trafo_node'], 'electricity_hp_import', 'Buy'] = \
            data['commodity'].loc[year, data['trafo_node'], 'electricity_import', 'Buy'].copy(deep=True)

    if mode['14a_steuve']:  # add import bev to Trafostation_OS
        data['process'].loc[year, data['trafo_node'], 'import_bev'] = \
            data['process'].loc[year, data['trafo_node'], 'import'].copy(deep=True)
        data['process_commodity'].loc[year, 'import_bev', 'electricity_bev_import', 'In'] = (1, np.nan)
        data['process_commodity'].loc[year, 'import_bev', 'electricity_bev', 'Out'] = (1, np.nan)
        data['buy_sell_price']['electricity_bev_import'] = \
            data['buy_sell_price']['electricity_import']
        data['commodity'].loc[year, data['trafo_node'], 'electricity_bev_import', 'Buy'] = \
            data['commodity'].loc[year, data['trafo_node'], 'electricity_import', 'Buy'].copy(deep=True)

    return data


def add_electricity_hp_bev_commodity(data, mode, comtype='Stock'):
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

    if comtype == ['Stock', 'Demand']:
        if mode['evu_sperre'] or mode['14a_steuve']:
            for site in data['site'].index.get_level_values(1):
                if site in demand_nodes:
                    data['commodity'].loc[year, site, 'electricity_hp', 'Demand'] = (0, 0, 0)
                else:
                    data['commodity'].loc[year, site, 'electricity_hp', 'Stock'] = (0, 0, 0)
        if mode['14a_steuve']:
            for site in data['site'].index.get_level_values(1):
                if site in demand_nodes:
                    data['commodity'].loc[year, site, 'electricity_bev', 'Demand'] = (0, 0, 0)
                else:
                    data['commodity'].loc[year, site, 'electricity_bev', 'Stock'] = (0, 0, 0)
    else:
        if mode['evu_sperre'] or mode['14a_steuve']:
            for site in data['site'].index.get_level_values(1):
                data['commodity'].loc[year, site, 'electricity_hp', comtype] = (0, 0, 0)
        if mode['14a_steuve']:
            for site in data['site'].index.get_level_values(1):
                data['commodity'].loc[year, site, 'electricity_bev', comtype] = (0, 0, 0)

    return data


def add_electricity_hp_bev_usable_commodity(data, mode, comtype='Stock'):
    # add commodity "electricity_hp_usable" to all buildings
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
    # demand_nodes.append(data['mainbusbar_node'])

    if mode['evu_sperre'] or mode['14a_steuve']:
        for building in demand_nodes:
            data['commodity'].loc[year, building, 'electricity_hp_usable', comtype] = (0, 0, 0)
    if mode['14a_steuve']:
        for building in demand_nodes:
            data['commodity'].loc[year, building, 'electricity_bev_usable', comtype] = (0, 0, 0)
    return data


def modify_hp_bev_processes(data, mode):
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

    if mode['evu_sperre']:
        # add process heatpump_air_evu_sperre to all buildings
        heatpump_evu_sperre_pro = data['process'][
            data['process'].index.get_level_values(2) == 'heatpump_air']
        heatpump_evu_sperre_pro = heatpump_evu_sperre_pro.copy(deep=True)
        heatpump_evu_sperre_pro.rename(index={'heatpump_air': 'heatpump_air_evu_sperre'}, level=2, inplace=True)
        data['process'] = pd.concat([data['process'], heatpump_evu_sperre_pro])

        for building in demand_nodes:
            data['eff_factor'][building, 'heatpump_air_evu_sperre'] = data['eff_factor'][building, 'heatpump_air']

        # add process-commodity for heatpump_air_evu_sperre
        heatpump_evu_sperre_pro_com = data['process_commodity'][
            data['process_commodity'].index.get_level_values(1) == 'heatpump_air']
        heatpump_evu_sperre_pro_com = heatpump_evu_sperre_pro_com.copy(deep=True)
        heatpump_evu_sperre_pro_com.rename(index={'heatpump_air': 'heatpump_air_evu_sperre'}, level=1, inplace=True)
        heatpump_evu_sperre_pro_com.rename(index={'electricity': 'electricity_hp'}, level=2, inplace=True)
        data['process_commodity'] = pd.concat([data['process_commodity'], heatpump_evu_sperre_pro_com])

    if mode['14a_steuve']:
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


def add_elec_hp_bev_to_usable_process(data, mode):
    year = date.today().year
    # demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    # demand_nodes.append(data['mainbusbar_node'])
    if mode['evu_sperre'] or mode['14a_steuve']:
        # add process elec_hp_to_usable to all buildings (same properties as curtailment)
        elec_hp_to_usable_pro = data['process'][
            data['process'].index.get_level_values(2) == 'curtailment']
        elec_hp_to_usable_pro = elec_hp_to_usable_pro.copy(deep=True)
        elec_hp_to_usable_pro.rename(index={'curtailment': 'elec_hp_to_usable'}, level=2, inplace=True)
        data['process'] = pd.concat([data['process'], elec_hp_to_usable_pro])
        # add process-commodity for heatpump_air_evu_sperre and elec_hp_to_usable
        data['process_commodity'].loc[year, 'elec_hp_to_usable', 'electricity_hp', 'In'] = (1, np.nan)
        data['process_commodity'].loc[year, 'elec_hp_to_usable', 'electricity_hp_usable', 'Out'] = (1, np.nan)
        data['process'].loc[year, :, 'elec_hp_to_usable']['var-cost'] = 0

    if mode['14a_steuve']:
        # add process elec_bev_to_usable to all buildings (same properties as curtailment)
        elec_bev_to_usable_pro = data['process'][
            data['process'].index.get_level_values(2) == 'curtailment']
        elec_bev_to_usable_pro = elec_bev_to_usable_pro.copy(deep=True)
        elec_bev_to_usable_pro.rename(index={'curtailment': 'elec_bev_to_usable'}, level=2, inplace=True)
        data['process'] = pd.concat([data['process'], elec_bev_to_usable_pro])
        # add process-commodity for elec_hp_to_usable
        data['process_commodity'].loc[year, 'elec_bev_to_usable', 'electricity_bev', 'In'] = (1, np.nan)
        data['process_commodity'].loc[year, 'elec_bev_to_usable', 'electricity_bev_usable', 'Out'] = (1, np.nan)
        data['process'].loc[year, :, 'elec_hp_to_usable']['var-cost'] = 0
    return data


def add_elec_to_hp_bev_process(data, mode):
    year = date.today().year
    # demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    # demand_nodes.append(data['mainbusbar_node'])
    if mode['14a_steuve']:
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
    # demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    # demand_nodes.append(data['mainbusbar_node'])

    # add process curtailment_heat to all buildings (same properties as curtailment)
    curtailment_heat_pro = data['process'][data['process'].index.get_level_values(2) == 'curtailment']
    curtailment_heat_pro = curtailment_heat_pro.copy(deep=True)
    curtailment_heat_pro.rename(index={'curtailment': 'curtailment_heat'}, level=2, inplace=True)
    data['process'] = pd.concat([data['process'], curtailment_heat_pro])
    # add process-commodity for elec_to_elec_usable
    data['process_commodity'].loc[year, 'curtailment_heat', 'space_heat', 'In'] = (1, np.nan)

    return data

def add_elec_to_elec_usable_process(data, mode='14a_steune'):
    year = date.today().year
    # demand_nodes = [sit for (sit, demand) in data['demand'].columns if demand == 'space_heat']
    # demand_nodes.append(data['mainbusbar_node'])
    if mode == '14a_steune':
        # add process elec_to_elec_usable to all buildings (same properties as curtailment)
        elec_to_elec_usable_pro = data['process'][data['process'].index.get_level_values(2) == 'curtailment']
        elec_to_elec_usable_pro = elec_to_elec_usable_pro.copy(deep=True)
        elec_to_elec_usable_pro.rename(index={'curtailment': 'elec_to_elec_usable'}, level=2, inplace=True)
        data['process'] = pd.concat([data['process'], elec_to_elec_usable_pro])
        # add process-commodity for elec_to_elec_usable
        data['process_commodity'].loc[year, 'elec_to_elec_usable', 'electricity', 'In'] = (1, np.nan)
        data['process_commodity'].loc[year, 'elec_to_elec_usable', 'electricity_usable', 'Out'] = (1, np.nan)
        data['process'].loc[year, :, 'elec_to_elec_usable']['var-cost'] = 0

    return data


def add_hp_bev_flows(data, mode):
    ### copy transmission lines with resistance to model transmission lines for reactive power flows
    if mode['evu_sperre'] or mode['14a_steuve']:
        heatpump_flow_lines = data['transmission'][data['transmission'].index.get_level_values(4) == 'electricity']
        heatpump_flow_lines = heatpump_flow_lines.copy(deep=True)
        heatpump_flow_lines.rename(index={'electricity': 'electricity_hp'}, level=4, inplace=True)
        ### set costs to zero as lines are not really built -

        heatpump_flow_lines.loc[:, ['inv-cost', 'fix-cost', 'var-cost', 'decom-saving']] *= 0
        ### concat new line data
        data['transmission'] = pd.concat([data['transmission'], heatpump_flow_lines])

    if mode['14a_steuve']:
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

        # add importing commodities to each
        if mode['evu_sperre'] or mode['14a_steuve']:

            data['commodity'].loc[year, building, 'electricity_hp_import', 'Buy'] = (data['commodity']['price'].
                                                                                     loc[:, :,
                                                                                     'electricity_import',
                                                                                     :].iloc[0], np.inf, np.inf)
            data['process'].loc[year, building, 'import_hp'] = data['process'].loc[
                year, data['trafo_node'], 'import_hp']
            data['process'].loc[year, building, 'import_hp']['cap-up'] = 999
            data['process'].loc[year, building, 'import_hp']['inst-cap'] = 999
            if mode['14a_steuve']:
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

def set_curtailment_limits(data_grid_plan):
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

def add_hp_bev_regulation_process(data_grid_plan, data_bui, mode, var_cost=0):
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

    if mode['evu_sperre']:
        for building in demand_nodes:
            data_grid_plan['commodity'].loc[year, building, 'regulate_com', 'Buy'] = (1, np.inf, np.inf)
            data_grid_plan['process'].loc[year, building, 'hp_lock'] = copy.deepcopy(
                data_grid_plan['process'].loc[
                    year, data_grid_plan['trafo_node'], 'import'])

            data_grid_plan['process'].loc[year, building, 'hp_lock']['min-fraction'] = 1
            data_grid_plan['process'].loc[year, building, 'hp_lock']['on-off'] = 1
            data_grid_plan['process'].loc[year, building, 'hp_lock']['inst-cap'] = 1
            data_grid_plan['process'].loc[year, building, 'hp_lock']['cap-up'] = 1
            data_grid_plan['process'].loc[year, building, 'hp_lock']['var-cost'] = var_cost
            data_grid_plan['eff_factor'][(building, 'hp_lock')] = data_grid_plan['demand'][
                (building, 'electricity_hp')]

        data_grid_plan['buy_sell_price']['regulate_com'] = data_grid_plan['buy_sell_price'][
                                                               'electricity_hp_import'] * 1.01  # costs one percent higher to regulate
        data_grid_plan['process_commodity'].loc[year, 'hp_lock', 'regulate_com', 'In'] = (
            1, np.nan)
        data_grid_plan['process_commodity'].loc[year, 'hp_lock', 'electricity_hp', 'Out'] = (
            1, np.nan)
        data_grid_plan['process_commodity'].loc[year, 'hp_lock', 'electricity-reactive', 'Out'] = \
            (np.tan(np.arccos(data_grid_plan['global_prop'].loc[year, 'PF_HP']['value'])), np.nan)

    if mode['14a_steuve']:
        for building in demand_nodes:
            #import pdb;pdb.set_trace()
            data_grid_plan['commodity'].loc[year, building, 'regulate_com', 'Buy'] = (1, np.inf, np.inf)
            data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate'] = copy.deepcopy(
                data_grid_plan['process'].loc[
                    year, data_grid_plan['trafo_node'], 'import'])
            # data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['min-fraction'] = 1
            # data_grid_plan['process'].loc[year, building, 'hp_lock']['on-off'] = 1
            data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['inst-cap'] = 1
            data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['cap-up'] = 1
            data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['var-cost'] = var_cost

            no_14a_nodes = ['7014014_001001_007007_00020002_01002',  # Pflegetagesstätte, Stadt-Model
                                 '7014014_001001_015015_00080008_01001',  # Schule, Stadt-Model
                                 '7014014_001001_014014_00050005_01001',  # Arztpraxis, Stadt-Model
                                 '7091091_001001_001001_00160016_01001']  # Kindergarten, Dorf-Model

            if building not in no_14a_nodes:
                data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')] = (data_grid_plan['demand'][
                                                                                        (building,
                                                                                         'electricity_hp')] - 4.2)
            else:
                data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')] = 0 * data_grid_plan['demand'][
                                                                                        (building, 'electricity')]

            ## added 02.04
            #data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')] = (['demand'][
            #                                                                            (building,
            #                                                                             'electricity_hp')] - 4.2)

            data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')][ \
                data_grid_plan['availability'][(building, 'hp_14a_steuve_regulate')] < 0] = 0

            data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate'] = copy.deepcopy(
                data_grid_plan['process'].loc[
                    year, data_grid_plan['trafo_node'], 'import'])
            # data_grid_plan['process'].loc[year, building, 'hp_14a_steuve_regulate']['min-fraction'] = 1
            # data_grid_plan['process'].loc[year, building, 'hp_lock']['on-off'] = 1
            data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate']['inst-cap'] = 1
            data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate']['cap-up'] = 1
            data_grid_plan['process'].loc[year, building, 'bev_14a_steuve_regulate']['var-cost'] = var_cost

            # get car count in building
            bui_car_count = data_bui['process'].loc[year, building, :]
            bui_car_count = len(bui_car_count[bui_car_count.index.get_level_values(0).str.startswith('charging')])

            data_grid_plan['availability'][(building, 'bev_14a_steuve_regulate')] = (data_grid_plan['demand'][
                                                                                         (building,
                                                                                          'electricity_bev')] - 4.2 * bui_car_count)
            data_grid_plan['availability'][(building, 'bev_14a_steuve_regulate')][ \
                data_grid_plan['availability'][(building, 'bev_14a_steuve_regulate')] < 0] = 0

        data_grid_plan['buy_sell_price']['regulate_com'] = data_grid_plan['buy_sell_price'][
                                                               'electricity_import'] * 1.00  # costs the same as import, to lockdown
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

    if mode['14a_steune']:
        for building in demand_nodes:
            data_grid_plan['commodity'].loc[year, building, 'regulate_com', 'Buy'] = (1, np.inf, np.inf)
            data_grid_plan['process'].loc[year, building, 'elec_14a_steune_regulate'] = copy.deepcopy(
                data_grid_plan['process'].loc[
                    year, data_grid_plan['trafo_node'], 'import'])
            # data_grid_plan['process'].loc[year, building, 'elec_14a_steune_regulate']['min-fraction'] = 1
            # data_grid_plan['process'].loc[year, building, 'elec_14a_steune_regulate']['on-off'] = 1
            data_grid_plan['process'].loc[year, building, 'elec_14a_steune_regulate']['inst-cap'] = 1
            data_grid_plan['process'].loc[year, building, 'elec_14a_steune_regulate']['cap-up'] = 1
            data_grid_plan['process'].loc[year, building, 'elec_14a_steune_regulate']['var-cost'] = var_cost

            no_14a_nodes = ['7014014_001001_007007_00020002_01002',  # Pflegetagesstätte, Stadt-Model
                            '7014014_001001_015015_00080008_01001',  # Schule, Stadt-Model
                            '7014014_001001_014014_00050005_01001',  # Arztpraxis, Stadt-Model
                            '7091091_001001_001001_00160016_01001',  # Kindergarten, Dorf-Model
                            '7097097_001001_001001_00040004_01001']  # Greenhouse, Land_model

            if building not in no_14a_nodes:
                data_grid_plan['availability'][(building, 'elec_14a_steune_regulate')] = (data_grid_plan['demand'][
                                                                                          (building,
                                                                                           'electricity')] - 5)
            else:
                data_grid_plan['availability'][(building, 'elec_14a_steune_regulate')] = 0 * (data_grid_plan['demand'][
                                                                                          (building, 'electricity')])
            data_grid_plan['availability'][(building, 'elec_14a_steune_regulate')][ \
                data_grid_plan['availability'][(building, 'elec_14a_steune_regulate')] < 0] = 0

        data_grid_plan['buy_sell_price']['regulate_com'] = data_grid_plan['buy_sell_price'][
                                                               'electricity_import'] * 1.00  # costs one percent higher to lockdown
        data_grid_plan['process_commodity'].loc[year, 'elec_14a_steune_regulate', 'regulate_com', 'In'] = (
            1, np.nan)
        data_grid_plan['process_commodity'].loc[year, 'elec_14a_steune_regulate', 'electricity', 'Out'] = \
            (1, np.nan)

    return data_grid_plan


def redefine_elec_demand_for_steune(data, prob_bui):
    year = date.today().year
    demand_nodes = set([sit for (sit, demand) in data['demand'].columns if demand == 'electricity'])
    # try:
    #    demand_nodes.remove('Trafostation_OS')
    # except ValueError:
    #    pass
    # try:
    #    demand_nodes.remove(data['mainbusbar_node'])
    # except ValueError:
    #    pass
    for building in demand_nodes:
        ## re-introduce electricity demand as electricity_usable (instead of electricity which flows in the grid)
        # initialize electricity_usable demand curve
        data['demand'][(building, 'electricity_usable')] = copy.deepcopy(
            data['demand'][(building, 'electricity')])
        # assign electricity_usable demand curve
        data['demand'].loc[year, :][(building, 'electricity_usable')].iloc[1:] = (
                prob_bui._result['tau_pro'].loc[:, year, building, 'import'].iloc[1:]
                - prob_bui._result['tau_pro'].loc[:, year, building, 'feed_in'].iloc[1:])

        # drop electricity demand curves
        data['demand'].drop((building, 'electricity'), axis=1, inplace=True)
        # add electricity_usable as a Demand commodity
        data['commodity'].loc[year, building, 'electricity_usable', 'Demand'] = (0, 0, 0)
        # rename
        # import pdb;pdb.set_trace()
        elec_com = data['commodity'][data['commodity'].index.get_level_values(2) == 'electricity']
        elec_com = elec_com[elec_com.index.get_level_values(1) == building]
        elec_com = elec_com[elec_com.index.get_level_values(0) == year]
        elec_com.rename(index={'Demand': 'Stock'}, level=3, inplace=True)
        data['commodity'].drop((year, building, 'electricity', 'Demand'), inplace=True, axis=0)
        data['commodity'] = pd.concat([data['commodity'], elec_com])

    return data


### Implement reactive power outputs as commodity according to predefined power factors for processes
def add_reactive_output_ratios(microgrid_data_input):
    pro_Q = microgrid_data_input['process'][microgrid_data_input['process'].loc[:, 'pf-min'] > 0]
    ratios_elec = microgrid_data_input['process_commodity'].loc[pd.IndexSlice[:, :, 'electricity', 'Out'], :]
    for process_idx, process in pro_Q.iterrows():
        for ratio_P_idx, ratio_P in ratios_elec.iterrows():
            if process_idx[2] == ratio_P_idx[1]:
                ratio_Q = ratios_elec.loc[pd.IndexSlice[:, ratio_P_idx[1], 'electricity', 'Out'], :].copy(deep=True)
                ratio_Q.rename(index={'electricity': 'electricity-reactive'}, level=2, inplace=True)
                microgrid_data_input['process_commodity'] = pd.concat(
                    [microgrid_data_input['process_commodity'], ratio_Q])
                microgrid_data_input['process_commodity'] = microgrid_data_input['process_commodity'] \
                    [~microgrid_data_input['process_commodity'].index.duplicated(keep='first')]
    return microgrid_data_input


### Merge main data with microgrid data
def concatenate_with_micros(data, microgrid_data):
    data['site'] = pd.concat([data['site'], microgrid_data['site']], sort=True)
    data['commodity'] = pd.concat([data['commodity'], microgrid_data['commodity']], sort=True)
    data['process'] = pd.concat([data['process'], microgrid_data['process']], sort=True)
    data['process_commodity'] = pd.concat([data['process_commodity'], microgrid_data['process_commodity']], sort=True)
    data['process_commodity'] = data['process_commodity'][~data['process_commodity'].index.duplicated(
        keep='first')]  # delete duplicated process commodities (for different ratios from different systems, the processes need adapted names)
    data['demand'] = pd.concat([data['demand'], microgrid_data['demand']], axis=1, sort=True)
    data['supim'] = pd.concat([data['supim'], microgrid_data['supim']], axis=1, sort=True)
    data['transmission'] = pd.concat([data['transmission'], microgrid_data['transmission']], sort=True)
    data['storage'] = pd.concat([data['storage'], microgrid_data['storage']], sort=True)
    data['dsm'] = pd.concat([data['dsm'], microgrid_data['dsm']], sort=True)
    data['buy_sell_price'] = pd.concat([data['buy_sell_price'], microgrid_data['buy_sell_price']], axis=1, sort=True)
    data['eff_factor'] = pd.concat([data['eff_factor'], microgrid_data['eff_factor']], axis=1, sort=True)
    return data


### store additional demand in cross scenario data to be used in subsequent scenarios
def store_additional_demand(cross_scenario_data, mobility_transmission_shift, heat_transmission_shift):
    ###transform dicts into dataframe and summarize timeseries for regions
    mobility_transmission_shift = pd.DataFrame.from_dict(mobility_transmission_shift).sum(level=0, axis=1)
    heat_transmission_shift = pd.DataFrame.from_dict(heat_transmission_shift).sum(level=0, axis=1)
    heat_transmission_shift.index = pd.MultiIndex.from_tuples(mobility_transmission_shift.index)
    ###write data into an excel file
    with pd.ExcelWriter(os.path.join(os.path.join(os.getcwd(), 'Input', 'additional_demand.xlsx'))) as writer:
        mobility_transmission_shift.to_excel(writer, 'mobility')
        heat_transmission_shift.to_excel(writer, 'heat')
    ###save cross scenario data in dict
    cross_scenario_data['mobility_transmission_shift'] = mobility_transmission_shift
    cross_scenario_data['heat_transmission_shift'] = heat_transmission_shift
    return cross_scenario_data
