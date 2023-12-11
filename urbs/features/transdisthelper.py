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

################################## START LVDS ##################################

#######


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
