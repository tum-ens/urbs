import pandas as pd
import numpy as np
import os


# SCENARIO GENERATORS
# In this script a variety of scenario generator functions are defined to facilitate scenario definitions.

# adjust scenario parameters for different distribution network shares
def variable_distribution_share(data, cross_scenario_data, transdist_share):
    data['transdist_share'] = pd.Series([transdist_share])  # defined as series to avoid validation error
    if transdist_share < 1:
        # recommended: if TD100 is run first, cross scenario data have been stored and can be automatically used for subsequent scenarios
        if bool(cross_scenario_data):
            # expand cap-up capacities of PV_utility_rooftop for shares < 1 in order to achieve equal maximum PV potentials
            # within all scenarios for better comparability from cross_scenario data
            data['process'].loc[pd.IndexSlice[:, :, 'PV_utility_rooftop'], 'cap-up'] = data['process'].loc[
                                                                                           pd.IndexSlice[:, :,
                                                                                           'PV_utility_rooftop'], 'cap-up'].values \
                                                                                       + (1 - transdist_share) * \
                                                                                       cross_scenario_data[
                                                                                           'PV_cap_shift'].values
            # read additional demand (BEV, Heat) from cross_scenario data
            additional_demand_mobility = cross_scenario_data['mobility_transmission_shift']
            additional_demand_heat = cross_scenario_data['heat_transmission_shift']
        else:
            # expand cap-up capacities of PV_utility_rooftop for shares < 1 in order to achieve equal maximum PV potentials
            # within all scenarios for better comparability from manually stored parameters for current input data (has to be changed if model changes)
            PV_priv_cap_100 = np.array(
                [5148, 4800, 21485, 25560, 899, 11952, 2425, 2628, 15529, 29259, 8063, 5726, 2014, 7535, 4354, 4275])
            data['process'].loc[pd.IndexSlice[:, :, 'PV_utility_rooftop'], 'cap-up'] += (
                                                                                                1 - transdist_share) * PV_priv_cap_100
            #  read add additional demand (BEV, Heat) from additional_demand.xlsx
            additional_demand_mobility = pd.read_excel(
                open(os.path.join(os.getcwd(), 'Input', 'additional_demand.xlsx'), 'rb'), sheet_name='mobility',
                index_col=[0, 1])
            additional_demand_heat = pd.read_excel(
                open(os.path.join(os.getcwd(), 'Input', 'additional_demand.xlsx'), 'rb'), sheet_name='heat',
                index_col=[0, 1])

            # The following values will not fit with a new model. They are only given as example if the TD100 scenario isn't run first
            # 4 Typeperiods
            # cross_scenario_data['predefClusterOrder'] = [2,1,1,1,3,3,1,3,1,1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,2,2]
            # cross_scenario_data['predefClusterCenterIndices'] = [29,11,50,5]

        # add additional electricity demand for mobility and heat on transmission level
        for col in data['demand']:
            if col[0] in list(additional_demand_mobility.columns):
                data['demand'].loc[:, col] += additional_demand_mobility.loc[:, col[0]] * (1 - transdist_share)
            if col[0] in list(additional_demand_heat.columns):
                data['demand'].loc[:, col] += additional_demand_heat.loc[:, col[0]] * (1 - transdist_share)
    return data, cross_scenario_data


def transdist100(data, cross_scenario_data):
    data['global_prop'].loc[pd.IndexSlice[:, 'TransDist'], 'value'].iloc[0] = 1
    data, cross_scenario_data = variable_distribution_share(data, cross_scenario_data, 1)
    return data, cross_scenario_data


def transdist66(data, cross_scenario_data):
    data['global_prop'].loc[pd.IndexSlice[:, 'TransDist'], 'value'].iloc[0] = 1
    data, cross_scenario_data = variable_distribution_share(data, cross_scenario_data, 0.66)
    return data, cross_scenario_data


def transdist33(data, cross_scenario_data):
    data['global_prop'].loc[pd.IndexSlice[:, 'TransDist'], 'value'].iloc[0] = 1
    data, cross_scenario_data = variable_distribution_share(data, cross_scenario_data, 0.33)
    return data, cross_scenario_data


def transmission(data, cross_scenario_data):
    ###set transdist parameter to zero
    data['global_prop'].loc[pd.IndexSlice[:, 'TransDist'], 'value'] = 0
    # variable_distribution_share(data, cross_scenario_data, 0)
    data, cross_scenario_data = variable_distribution_share(data, cross_scenario_data, 0)
    return data, cross_scenario_data


############ adjustments into data for scenario variations


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


def remove_mob_flexibility_and_shuffle(data):
    import random

    # de-flexiblise mobility demand by removing virtual storage
    for (stf, sit, sto, com) in data['storage'].index:
        if sto.startswith('mobility'):
            data['storage'].loc[(stf, sit, sto, com), 'inst-cap-p'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'inst-cap-c'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'cap-up-p'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'cap-up-c'] = 0

    # shift car-demand to the evening
    hour_shift = 0
    for mob_demand_site in data['demand'].loc[:, pd.IndexSlice[:, 'mobility']].columns.get_level_values(0):
        # hour_shift = random.randrange(3) - 1
        data['demand'].loc[:, pd.IndexSlice[mob_demand_site, 'mobility']] = data['demand'].loc[:, pd.IndexSlice[
                                                                                                      mob_demand_site, 'mobility']].shift(
            periods=10 + hour_shift, fill_value=0)  # shift from 8 to 17, 18, or 19
        data['demand'].loc[(2022, 18 + hour_shift), pd.IndexSlice[mob_demand_site, 'mobility']] *= 2
        # allow charging at hours 18 + hour_shift, 42 + hour_shift etc.
        data['eff_factor'].loc[:, pd.IndexSlice[mob_demand_site, 'charging_station']] = 1
        if hour_shift == 0:
            hour_shift = 1
        elif hour_shift == 1:
            hour_shift = -1
        elif hour_shift == -1:
            hour_shift = 0
    return data

def remove_mob_flexibility(data):
    for (stf, sit, sto, com) in data['storage'].index:
        if sto.startswith('mobility'):
            data['storage'].loc[(stf, sit, sto, com), 'inst-cap-p'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'inst-cap-c'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'cap-up-p'] = 0
            data['storage'].loc[(stf, sit, sto, com), 'cap-up-c'] = 0

    return data

def shuffle_mob_demand(data):
    import random

    # shift car-demand to the evening
    hour_shift = 0
    for mob_demand_site in data['demand'].loc[:, pd.IndexSlice[:, 'mobility']].columns.get_level_values(0):
        # hour_shift = random.randrange(3) - 1

        data['demand'].loc[:, pd.IndexSlice[mob_demand_site, 'mobility']] = data['demand'].loc[:, pd.IndexSlice[
                                                                                                      mob_demand_site, 'mobility']].shift(
            periods = hour_shift, fill_value=0)  # shift from 8 to 7, 8, or 9
        data['demand'].loc[(2022, 8 + hour_shift), pd.IndexSlice[mob_demand_site, 'mobility']] *= 2
        # allow charging at hours 18 + hour_shift, 42 + hour_shift etc.
        data['eff_factor'].loc[:, pd.IndexSlice[mob_demand_site, 'charging_station']] = \
            data['eff_factor'].loc[:, pd.IndexSlice[mob_demand_site, 'charging_station']].shift(
            periods = hour_shift, fill_value=1)
        if hour_shift == 0:
            hour_shift = 1
        elif hour_shift == 1:
            hour_shift = -1
        elif hour_shift == -1:
            hour_shift = 0
    return data

def remove_mob_demand(data):
    #  remove mobility demand
    data['demand'].loc[:, pd.IndexSlice[:, 'mobility']] = 0
    return data


def remove_heat_pump(data):
    # un-electrify heat demand (release CO2 limit, disallow heatpumps)
    data['global_prop'].loc[pd.IndexSlice[:, 'CO2 limit'], 'value'] = np.inf
    data['process'].loc[pd.IndexSlice[:, :, 'heatpump_air'], 'inst-cap'] = 0
    data['process'].loc[pd.IndexSlice[:, :, 'heatpump_air'], 'cap-up'] = 0
    return data


############# scenarios
def ref(data, cross_scenario_data):
    data = remove_mob_flexibility(data)
    data = remove_battery(data)
    data = remove_heat_storage(data)
    data = remove_heat_pump(data)
    data = remove_mob_demand(data)
    return data, cross_scenario_data


def ref_heat(data, cross_scenario_data):
    data = remove_mob_flexibility(data)
    data = remove_battery(data)
    data = remove_heat_storage(data)
    data = remove_mob_demand(data)
    return data, cross_scenario_data


def ref_mob(data, cross_scenario_data):
    data = remove_mob_flexibility(data)
    data = remove_battery(data)
    data = remove_heat_storage(data)
    data = remove_heat_pump(data)
    return data, cross_scenario_data


def ref_all(data, cross_scenario_data):
    data = remove_mob_flexibility(data)
    data = remove_battery(data)
    data = remove_heat_storage(data)
    return data, cross_scenario_data


def flex_elec(data, cross_scenario_data):
    data = remove_mob_flexibility(data)
    data = remove_heat_storage(data)
    return data, cross_scenario_data


def flex_heat(data, cross_scenario_data):
    data = remove_mob_flexibility(data)
    data = remove_battery(data)
    return data, cross_scenario_data


def flex_mob(data, cross_scenario_data):
    data = remove_battery(data)
    data = remove_heat_storage(data)
    return data, cross_scenario_data


def flex_all(data, cross_scenario_data):
    # do nothing
    return data, cross_scenario_data

def flex_all_plus(data, cross_scenario_data):
    # difference to flexplus: car demand is weekly.
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['inst-cap-p']] *= 7
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['inst-cap-c']] *= 7
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['cap-up-p']] *= 7
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['cap-up-c']] *= 7
    # import pdb;pdb.set_trace()
    for mob_demand_site in data['demand'].loc[:, pd.IndexSlice[:, 'mobility']].columns.get_level_values(0):
        daily_car_demand = data['demand'].loc[[(2022, 32)], pd.IndexSlice[mob_demand_site, 'mobility']].iloc[0]
        weekly_car_demand = daily_car_demand * 7

        data['demand'].loc[:, pd.IndexSlice[mob_demand_site, 'mobility']] = 0
        n = 0
        while 8 + 168 + n <= 8760:
            data['demand'].loc[[(2022, 8 + 168 + n)], pd.IndexSlice[mob_demand_site, 'mobility']] = weekly_car_demand
            n = n + 168
        data['demand'].loc[[(2022, 8)], pd.IndexSlice[mob_demand_site, 'mobility']] = daily_car_demand / 2
    return data, cross_scenario_data

def ref_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = ref(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0

    return data, cross_scenario_data


def ref_heat_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = ref_heat(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0

    return data, cross_scenario_data


def ref_mob_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = ref_mob(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0
    return data, cross_scenario_data


def ref_all_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = ref_all(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0

    return data, cross_scenario_data


def flex_elec_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = flex_elec(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0

    return data, cross_scenario_data


def flex_heat_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = flex_heat(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0

    return data, cross_scenario_data


def flex_mob_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = flex_mob(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0


    return data, cross_scenario_data


def flex_all_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = flex_all(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0

    return data, cross_scenario_data


def flex_all_plus_no_pv(data, cross_scenario_data):
    data, cross_scenario_data = flex_all_plus(data, cross_scenario_data)
    data['process'].loc[pd.IndexSlice[:, :, 'Rooftop PV'], ['cap-up']] = 0

    return data, cross_scenario_data

############ old scenarios


def flexplus(data, cross_scenario_data):
    # do nothing
    return data, cross_scenario_data


def flex(data, cross_scenario_data):
    # difference to flexplus: no heat storage
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['cap-up-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['cap-up-c']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['inst-cap-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['inst-cap-c']] = 0
    return data, cross_scenario_data


def refheatmob(data, cross_scenario_data):
    # apply no heat storage aspect of flex
    data, cross_scenario_data = flex(data, cross_scenario_data)

    import random

    # de-flexiblise electricity demand by disallowing battery investment
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['inst-cap-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['inst-cap-c']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['cap-up-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'battery_private', :], ['cap-up-c']] = 0

    # de-flexiblise mobility demand by removing virtual storage
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['inst-cap-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['inst-cap-c']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['cap-up-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['cap-up-c']] = 0

    # shift car-demand to the evening
    for mob_demand_site in data['demand'].loc[:, pd.IndexSlice[:, 'mobility']].columns.get_level_values(0):
        hour_shift = random.randrange(3) - 1
        data['demand'].loc[:, pd.IndexSlice[mob_demand_site, 'mobility']] = data['demand'].loc[:, pd.IndexSlice[
                                                                                                      mob_demand_site, 'mobility']].shift(
            periods=10 + hour_shift, fill_value=0)  # shift from 8 to 17, 18, or 19
        data['demand'].loc[(2022, 18 + hour_shift), pd.IndexSlice[mob_demand_site, 'mobility']] *= 2
        # allow charging at hours 18 + hour_shift, 42 + hour_shift etc.
        data['eff_factor'].loc[:, pd.IndexSlice[mob_demand_site, 'charging_station']] = 1

    return data, cross_scenario_data


def refmob(data, cross_scenario_data):
    data, cross_scenario_data = refheatmob(data, cross_scenario_data)
    # un-electrify heat demand (release CO2 limit, disallow heatpumps)
    data['global_prop'].loc[pd.IndexSlice[:, 'CO2 limit'], 'value'] = np.inf
    data['process'].loc[pd.IndexSlice[:, :, 'heatpump_air'], 'inst-cap'] = 0
    data['process'].loc[pd.IndexSlice[:, :, 'heatpump_air'], 'cap-up'] = 0
    return data, cross_scenario_data


def refheat(data, cross_scenario_data):
    # deflexiblise heat and mobility demands
    data, cross_scenario_data = refheatmob(data, cross_scenario_data)
    #  remove mobility demand
    data['demand'].loc[:, pd.IndexSlice[:, 'mobility']] = 0
    return data, cross_scenario_data


# def ref(data, cross_scenario_data):
#    data, cross_scenario_data = refheatmob(data, cross_scenario_data)
#    data, cross_scenario_data = refmob(data, cross_scenario_data)
#    data, cross_scenario_data = refheat(data, cross_scenario_data)
#    return data, cross_scenario_data


def flexplusplus(data, cross_scenario_data):
    # difference to flexplus: car demand is weekly.
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['inst-cap-p']] *= 7
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['inst-cap-c']] *= 7
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['cap-up-p']] *= 7
    data['storage'].loc[pd.IndexSlice[:, :, 'mobility_storage', :], ['cap-up-c']] *= 7
    # import pdb;pdb.set_trace()
    for mob_demand_site in data['demand'].loc[:, pd.IndexSlice[:, 'mobility']].columns.get_level_values(0):
        daily_car_demand = data['demand'].loc[[(2022, 32)], pd.IndexSlice[mob_demand_site, 'mobility']].iloc[0]
        weekly_car_demand = daily_car_demand * 7

        data['demand'].loc[:, pd.IndexSlice[mob_demand_site, 'mobility']] = 0
        n = 0
        while 8 + 168 + n <= 8760:
            data['demand'].loc[[(2022, 8 + 168 + n)], pd.IndexSlice[mob_demand_site, 'mobility']] = weekly_car_demand
            n = n + 168
        data['demand'].loc[[(2022, 8)], pd.IndexSlice[mob_demand_site, 'mobility']] = daily_car_demand / 2
    return data, cross_scenario_data


def flexplus_tsam(data, cross_scenario_data):
    # do nothing
    data['global_prop'].loc[pd.IndexSlice[:, 'tsam'], 'value'] = 1
    return data, cross_scenario_data


def flex_tsam(data, cross_scenario_data):
    data['global_prop'].loc[pd.IndexSlice[:, 'tsam'], 'value'] = 1
    # difference to flexplus: no heat storage
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['cap-up-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['cap-up-c']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['inst-cap-p']] = 0
    data['storage'].loc[pd.IndexSlice[:, :, 'heat_storage', :], ['inst-cap-c']] = 0
    return data, cross_scenario_data


def refheatmob_tsam(data, cross_scenario_data):
    # apply no heat storage aspect of flex
    data, cross_scenario_data = refheatmob(data, cross_scenario_data)
    data['global_prop'].loc[pd.IndexSlice[:, 'tsam'], 'value'] = 1
    return data, cross_scenario_data


def refmob_tsam(data, cross_scenario_data):
    data, cross_scenario_data = refmob(data, cross_scenario_data)
    data['global_prop'].loc[pd.IndexSlice[:, 'tsam'], 'value'] = 1
    return data, cross_scenario_data


def refheat_tsam(data, cross_scenario_data):
    data, cross_scenario_data = refheat(data, cross_scenario_data)
    data['global_prop'].loc[pd.IndexSlice[:, 'tsam'], 'value'] = 1
    return data, cross_scenario_data


def ref_tsam(data, cross_scenario_data):
    data, cross_scenario_data = ref(data, cross_scenario_data)
    data['global_prop'].loc[pd.IndexSlice[:, 'tsam'], 'value'] = 1
    return data, cross_scenario_data


def flexplusplus_tsam(data, cross_scenario_data):
    data, cross_scenario_data = flexplusplus(data, cross_scenario_data)
    data['global_prop'].loc[pd.IndexSlice[:, 'tsam'], 'value'] = 1
    return data, cross_scenario_data
