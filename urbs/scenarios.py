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

def flex_all(data, cross_scenario_data):
    # do nothing
    return data, cross_scenario_data
