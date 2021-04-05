from urbs.identify import *
import copy
import math

def create_transdist_data(data, microgrid_data_initial):
    microgrid_set_list = build_set_list(data)
    microgrid_multiplicator_list = build_multiplicator_list(data)
    for set_number, set in enumerate(microgrid_set_list):  # top region microgrid setting
        top_region_name = data['site'].index.get_level_values(1)[set_number]
        for type_nr, quantity_nr in enumerate(set):  # Auflistung des settings
            microgrid_entries = microgrid_data_initial[type_nr]['site'].index.get_level_values(1)
            n = 0
            while n < quantity_nr:
                microgrid_data_input = copy.deepcopy(microgrid_data_initial[type_nr])
                for entry in microgrid_entries:
                    # microgrids are derived from the predefined microgrid types and setting
                    create_microgrid_data(microgrid_data_input, entry, n, top_region_name)
                n += 1
                # scale capacities, commodities, demand & areas with multiplicator number of the microgrid
                multiplicator_scaling(microgrid_data_input, microgrid_multiplicator_list, set_number, type_nr)
                # model additional transmission lines for the reactive power
                add_reactive_transmission_lines(microgrid_data_input)
                # add reactive output ratios for ac sites
                add_reactive_output_ratios(microgrid_data_input)
                # concatenate main data with microgrid data with
                concatenate_with_micros(data, microgrid_data_input)

    return data

def build_set_list(data):
    transdist_dict = data['site'].drop(columns=['base-voltage','area'], axis=1).to_dict()
    microgrid_set = transdist_dict['microgrid-setting']
    microgrid_set_list = []
    for item in microgrid_set:
        microgrid_set_list.append(list(map(int, microgrid_set[item].split(','))))
    return microgrid_set_list

def build_multiplicator_list(data):
    transdist_dict = data['site'].drop(columns=['base-voltage','area'], axis=1).to_dict()
    microgrid_multiplicator = transdist_dict['multiplicator']
    microgrid_multiplicator_list = []
    for item in microgrid_multiplicator:
        microgrid_multiplicator_list.append(list(map(int, microgrid_multiplicator[item].split(','))))
    return microgrid_multiplicator_list

# In this function according to the microgrid-setting list and the defined microgrid types, microgrid data are created
def create_microgrid_data(microgrid_data_input, entry, n, top_region_name):
    microgrid_data_input['site'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['commodity'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['process'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['process_commodity'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['demand'].rename(
        columns={entry: entry + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    microgrid_data_input['supim'].rename(
        columns={entry: entry + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    microgrid_data_input['storage'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['dsm'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['buy_sell_price'].rename(
        columns={entry: entry + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    microgrid_data_input['eff_factor'].rename(
        columns={entry: entry + str(n + 1) + '_' + top_region_name}, level=0, inplace=True)
    # for transmission data indexes on two levels must be changed
    microgrid_data_input['transmission'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=1, inplace=True)
    microgrid_data_input['transmission'].rename(
        index={entry: entry + str(n + 1) + '_' + top_region_name}, level=2, inplace=True)
    # add transmission line from microgrids to top level region
    microgrid_data_input['transmission'].rename(
        index={'top_region_dummy': top_region_name}, level=1, inplace=True)
    microgrid_data_input['transmission'].rename(
        index={'top_region_dummy': top_region_name}, level=2, inplace=True)
    return microgrid_data_input

# In this function according to the multiplicator list microgrid types are being scaled
def multiplicator_scaling(microgrid_data_input, microgrid_multiplicator_list, set_number, type_nr):
    microgrid_data_input['site'].loc[:, 'area'] *= microgrid_multiplicator_list[set_number][type_nr]
    microgrid_data_input['site'].loc[:, 'base-voltage'] *= math.sqrt(microgrid_multiplicator_list[set_number][type_nr])
    microgrid_data_input['commodity'].loc[:, 'max':'maxperhour'] *= microgrid_multiplicator_list[set_number][type_nr]
    microgrid_data_input['process'].loc[:, ['inst-cap', 'cap-lo', 'cap-up', 'area-per-cap', 'cap-block']] *= \
        microgrid_multiplicator_list[set_number][type_nr]
    microgrid_data_input['transmission'].loc[:, ['inst-cap', 'cap-lo', 'cap-up', 'tra-block']] *= \
        microgrid_multiplicator_list[set_number][type_nr]
    microgrid_data_input['storage'].loc[:, ['inst-cap-c', 'cap-lo-c', 'cap-up-c', 'inst-cap-p', 'cap-lo-p',
                                            'cap-up-p', 'c-block', 'p-block']] *= microgrid_multiplicator_list[set_number][type_nr]
    microgrid_data_input['dsm'].loc[:, 'cap-max-do':'cap-max-up'] *= microgrid_multiplicator_list[set_number][type_nr]
    microgrid_data_input['demand'].loc[:, :] *= microgrid_multiplicator_list[set_number][type_nr]
    return microgrid_data_input

# In this function according to predefined resistances on lines reactive power flows are enabled by modeling new lines
def add_reactive_transmission_lines(microgrid_data_input):
    # copy transmission lines with resistance to model transmission lines for reactive power flows
    reactive_transmission_lines = microgrid_data_input['transmission'][microgrid_data_input['transmission'].loc[:, 'resistance'] > 0]
    reactive_transmission_lines = reactive_transmission_lines.copy(deep = True)
    reactive_transmission_lines.rename(index={'electricity': 'electricity-reactive'}, level=4, inplace=True)
    # set costs to zero
    reactive_transmission_lines.loc[:, 'inv-cost':'var-cost'] *= 0
    # scale transmission line capacities with predefined Q/P-ratio
    for idx, entry in reactive_transmission_lines.iterrows():
        reactive_transmission_lines.loc[idx, ['inst-cap', 'cap-lo', 'cap-up']] = entry['inst-cap':'cap-up'] * entry['cap-Q/P-ratio']
    microgrid_data_input['transmission'] = pd.concat([microgrid_data_input['transmission'], reactive_transmission_lines], sort=True)
    return microgrid_data_input

# In this function according to predefined power factors for processes, reactive power outputs are implemented as commodity
def add_reactive_output_ratios(microgrid_data_input):
    pro_Q = microgrid_data_input['process'][microgrid_data_input['process'].loc[:, 'pf-min'] > 0]
    ratios_elec = microgrid_data_input['process_commodity'].loc[pd.IndexSlice[:, :, 'electricity', 'Out'], :]
    for process_idx, process in pro_Q.iterrows():
        for ratio_P_idx, ratio_P in ratios_elec.iterrows():
            if process_idx[2] == ratio_P_idx[1]:
                ratio_Q = ratios_elec.loc[pd.IndexSlice[:, ratio_P_idx[1], 'electricity', 'Out'], :].copy(deep = True)
                ratio_Q.rename(index={'electricity': 'electricity-reactive'}, level=2, inplace=True)
                microgrid_data_input['process_commodity'] = microgrid_data_input['process_commodity'].append(ratio_Q)
                microgrid_data_input['process_commodity'] = microgrid_data_input['process_commodity']\
                [~microgrid_data_input['process_commodity'].index.duplicated(keep='first')]
    return microgrid_data_input

# In this function the main data and the microgrid data are merged
def concatenate_with_micros(data, microgrid_data):
    data['site'] = pd.concat([data['site'], microgrid_data['site']], sort=True)
    data['commodity'] = pd.concat([data['commodity'], microgrid_data['commodity']],sort=True)
    data['process'] = pd.concat([data['process'], microgrid_data['process']],sort=True)
    data['process_commodity'] = pd.concat([data['process_commodity'], microgrid_data['process_commodity']],sort=True)
    # delete duplicated process commodities (for different ratios from different systems, the processes need adapted names)
    data['process_commodity'] = data['process_commodity'][~data['process_commodity'].index.duplicated(keep='first')]
    data['demand'] = pd.concat([data['demand'], microgrid_data['demand']], axis=1,sort=True)
    data['supim'] = pd.concat([data['supim'], microgrid_data['supim']], axis=1,sort=True)
    data['transmission'] = pd.concat([data['transmission'], microgrid_data['transmission']],sort=True)
    data['storage'] = pd.concat([data['storage'], microgrid_data['storage']],sort=True)
    data['dsm'] = pd.concat([data['dsm'], microgrid_data['dsm']],sort=True)
    data['buy_sell_price'] = pd.concat([data['buy_sell_price'], microgrid_data['buy_sell_price']], axis=1,sort=True)
    data['eff_factor'] = pd.concat([data['eff_factor'], microgrid_data['eff_factor']], axis=1,sort=True)
    return data