import math
import pyomo.core as pyomo
import pandas as pd
import tsam.timeseriesaggregation as tsam
from datetime import datetime, timedelta
import numpy as np
import itertools  as it
from urbs.identify import *
import os

### Apply timeseries aggregation
def run_tsam(data, noTypicalPeriods, hoursPerPeriod, cross_scenario_data):
    ###bring together all time series data
    time_series_data = pd.concat([data['demand'], data['supim'], data['buy_sell_price'], data['eff_factor']], axis=1, sort=True)
    ### dict which allocates the first equal column of the dataframe to each column before droping duplicates of dataframe
    equal_col_dict = dict()
    for col1 in time_series_data.columns:
        time_series_data2 = time_series_data.drop(columns = col1)
        for col2 in time_series_data2.columns:
            if time_series_data[col1].equals(time_series_data2[col2]):
                equal_col_dict[col1] = col2
                break
    ### drop duplicate timeseries
    time_series_data = time_series_data.T.drop_duplicates().T
    ###prepare datetime vector which is required by tsam method
    date_hour = np.arange(datetime(2021, 1, 1), datetime(2022, 1, 1), timedelta(hours=1)).astype(datetime).T
    ### prepare df for tsam
    time_series_data = time_series_data.iloc[1:, :] #drop initialization timestep
    time_series_data['DateTime'] = date_hour #add column with datetime
    time_series_data = time_series_data.set_index('DateTime') #set required index for tsam method
    ### apply tsam method described in: https://tsam.readthedocs.io/en/latest/index.html
    if data['transdist_share'].values[0] == 1:
        aggregation = tsam.TimeSeriesAggregation(time_series_data, noTypicalPeriods=noTypicalPeriods,
                                             hoursPerPeriod=hoursPerPeriod, extremePeriodMethod = 'append', clusterMethod='hierarchical')

        # Different scenarios can yield different typeperiod cluster centers and orders impairing their comparability.
        # For TD100 cluster centers and order are automatically stored in the cross_scenario_data for subsequent scenarios
        cross_scenario_data['predefClusterCenterIndices'] = aggregation.clusterCenterIndices
        cross_scenario_data['predefClusterOrder'] = aggregation.clusterOrder

        # store_name = 'TD' + str(data['transdist_share'].values[0]) + 'cluster_parameter.xlsx'
        # with pd.ExcelWriter(os.path.join(os.path.join(os.getcwd(), store_name))) as writer:
        #     pd.Series(aggregation.clusterOrder).to_excel(writer, 'order')
        #     pd.Series(aggregation.clusterCenterIndices).to_excel(writer, 'centerIndices')
        #     pd.DataFrame.from_dict(aggregation.clusterPeriodDict).to_excel(writer, 'clusterPeriods')
    else:
        ### load predefined clusters from TD100 for better scenario comparability
        aggregation = tsam.TimeSeriesAggregation(time_series_data, noTypicalPeriods=noTypicalPeriods,predefClusterOrder=cross_scenario_data['predefClusterOrder'],
                                                 predefClusterCenterIndices=cross_scenario_data['predefClusterCenterIndices'], hoursPerPeriod=hoursPerPeriod,
                                                 extremePeriodMethod = 'append', clusterMethod='hierarchical')

    ###store tsam results
    typPeriods = aggregation.createTypicalPeriods()
    orderPeriods = aggregation.clusterOrder

    ### tsam paramters for validation
    # timeStepMatching = aggregation.indexMatching(),
    # predictedData = aggregation.predictOriginalData()
    # indicatorRaw = aggregation.accuracyIndicators()
    # tsam_data = aggregation.predictOriginalData()
    # weights = aggregation.clusterPeriodNoOccur # is not used because detailed information considering interruptions is taken out of orderPeriods

    ### adjust the modeling steps and the weight vector accordingly to the generated typeweeks including interruptions and its order
    requiredPeriods = [x[0] for x in it.groupby(orderPeriods)] #determine borders of subsequent typeperiods to model
    print('The total number of typeperiods is: %.2f' % len(requiredPeriods))
    print(requiredPeriods)
    timeframe = requiredPeriods.__len__() * hoursPerPeriod + 1 #determine total number of modeled typeperiod timesteps
    last_period_nr = orderPeriods[-1] #identify last element as this one represents only a day not a week
    ### store the occurence with its resulting weight for each modeled part typeperiod
    occurence_weight_factor = []
    for item in np.sort(np.unique(requiredPeriods)):
        occurence_weight_factor.append([sum(1 for _ in group) for key, group in it.groupby(orderPeriods) if key==item]) #create list showing the weight of each part of the typeperiod that must be modeled
    occurence_weight_factor[last_period_nr][-1] = occurence_weight_factor[last_period_nr][-1] \
                                                  - 1 + (8760 % hoursPerPeriod)/hoursPerPeriod #consider that a year normally can not be divided in an integer number of typeperiods
    ### prepare dataframe, Series and helper variables for concatenation of new data
    modeling_steps = time_series_data.iloc[0:1, :]
    modeling_steps.iloc[0,:] = 0
    weight_vector = pd.Series([0])
    weighting_order = []
    occurence_counter = np.zeros(noTypicalPeriods).astype(int)
    ### concat typerperiod time series data according to the modelled typerperiod order and concat its related weight series
    for type_nr in requiredPeriods:
        modeling_steps = pd.concat([modeling_steps, typPeriods.loc[pd.IndexSlice[type_nr, :], :]], ignore_index=True) #concat all relevant timeseries data in one dataframe
        weight_numbers = pd.Series(np.ones(hoursPerPeriod) * occurence_weight_factor[type_nr][occurence_counter[type_nr]])
        weighting_order.append(occurence_weight_factor[type_nr][occurence_counter[type_nr]])
        weight_vector = pd.concat([weight_vector, weight_numbers], ignore_index=True)
        occurence_counter[type_nr] += 1

    ### rewrite weight data with new computed weights for new timeframe
    data['type period'].update(pd.Series(weight_vector.values, name='weight_typeperiod', index =data['type period'].index[0:timeframe]))

    ### rewrite demand load data
    data['demand'] = data['demand'].iloc[0:timeframe, :]
    for column in data['demand']:
        if column in modeling_steps.columns:
            data['demand'][column].iloc[0:timeframe] = modeling_steps[column].values
        else:
            data['demand'][column].iloc[0:timeframe] = modeling_steps[equal_col_dict[column]].values

    ### now scale distribution level demand data with multiplicator (had to be postponed to this point, to avoid multiple proportional time series')
    multi_data = data['site'][data['site']['multiplicator'].notna()].droplevel(level=0)['multiplicator']
    region_multiplicators = dict()
    for idx in multi_data.index:
        region_multiplicators[idx] = list(map(int, multi_data[idx].split(',')))
    for column in data['demand']:
        if 'node' in column[0]: # 'node' hard coded here
            region_type = column[0].split('_')[1]
            top_region_name = column[0].split('_')[2]
            if 'rural' in region_type: # names rural and urban and its sheet order also hard coded here
                multi = region_multiplicators[top_region_name][0]
            if 'urban' in region_type:
                multi = region_multiplicators[top_region_name][1]
            data['demand'][column] *= multi * data['transdist_share'].values[0]

    ### rewrite fluctuating resource data
    data['supim'] = data['supim'].iloc[0:timeframe, :]
    for column in data['supim']:
        if column in modeling_steps.columns:
            data['supim'][column].iloc[0:timeframe] = modeling_steps[column].values
        else:
            data['supim'][column].iloc[0:timeframe] = modeling_steps[equal_col_dict[column]].values

    ### rewrite Buy/Sell Prices
    data['buy_sell_price'] = data['buy_sell_price'].iloc[0:timeframe, :]
    for column in data['buy_sell_price']:
        if column in modeling_steps.columns:
            data['buy_sell_price'][column].iloc[0:timeframe] = modeling_steps[column].values
        else:
            data['buy_sell_price'][column].iloc[0:timeframe] = modeling_steps[equal_col_dict[column]].values

    ### rewrite Variable efficiencies
    data['eff_factor'] = data['eff_factor'].iloc[0:timeframe, :]
    for column in data['eff_factor']:
        if column in modeling_steps.columns:
            data['eff_factor'][column].iloc[0:timeframe] = modeling_steps[column].values
        else:
            data['eff_factor'][column].iloc[0:timeframe] = modeling_steps[equal_col_dict[column]].values

    ### return new timestep range
    timesteps_new = range(0, timeframe)

    return data, timesteps_new, weighting_order, cross_scenario_data

### function to store relevant parameters from other modules in model
def store_typeperiod_parameter(m, hoursPerPeriod, weighting_order):
    m.hoursPerPeriod = hoursPerPeriod
    m.weighting_order = weighting_order
    return m

def add_typeperiod(m):
    # if not (len(m.timesteps) % 168 == 0 or len(m.timesteps) % 168 == 1):
    #     print('Warning: length of timesteps does not end at the end of the type period!')

    ### change weight parameter to 1, since the whole year is representated by weight_typeperiod
    m.del_component(m.weight)
    m.weight = pyomo.Param(
        initialize=1,
        doc='Pre-factor for variable costs and emissions for annual result for type period = 1')

    ### create list with all period ends
    t_endofperiod_list = [i * 168 * m.dt for i in list(range(1,1+int(len(m.timesteps) / m.dt / 168)))]

    if m.mode['tsam']:
        ### prepare time lists for set tuples
        start_end_typeperiods_list = []
        for hour in t_endofperiod_list:
            start_end_typeperiods_list.append((hour + 1 - m.hoursPerPeriod, hour))
        subsequent_typeperiods_list = []
        t_endofperiod_list_without_last = t_endofperiod_list[0:-1]
        for hour in t_endofperiod_list_without_last:
            subsequent_typeperiods_list.append((hour,hour+1))

        ### allocate weights to the specific period with a dict
        m.typeperiod_weights = dict(zip(t_endofperiod_list, m.weighting_order))

        ### define timeperiod sets
        m.t_endofperiod = pyomo.Set(
            within=m.t,
            initialize=t_endofperiod_list,
            ordered=True,
            doc='timestep at the end of each timeperiod')
        m.subsequent_typeperiods = pyomo.Set(
            within=m.t * m.t,
            initialize=subsequent_typeperiods_list,
            ordered=True,
            doc='subsequent timesteps between two typeperiods')
        m.start_end_typeperiods = pyomo.Set(
            within=m.t * m.t,
            initialize=start_end_typeperiods_list,
            ordered=True,
            doc='start and end of each modeled typeperiod as tuple')


        ### enable seasonal storage with SOC variable and two constraints
        ### SOC variable
        m.deltaSOC = pyomo.Var(
            m.t_endofperiod, m.sto_tuples,
            within=pyomo.Reals,
            doc='Variable to describe the delta of a storage within each period')
        ### constraint to describe the SOC difference of a storage within a repeating period A
        m.res_delta_SOC = pyomo.Constraint(
            m.start_end_typeperiods, m.sto_tuples,
            rule=res_delta_SOC,
            doc='delta_SOC_A = weight * (SOC_A_tN - SOC_A_t0)')
        ### SOC constraint for two consecutive typeperiods A and B
        m.res_typeperiod_delta_SOC = pyomo.Constraint(
            m.subsequent_typeperiods, m.sto_tuples,
            rule=res_typeperiod_deltaSOC_rule,
            doc='SOC_B_t0 = SOC_A_t0 + delta_SOC_A')

        ### delete old ciclycity rule to enable typeperiod simulation
        del m.res_storage_state_cyclicity

        ### new ciclycity constraint for typeperiods
        m.res_storage_state_cyclicity_typeperiod = pyomo.Constraint(
            m.sto_tuples,
            rule=res_storage_state_cyclicity_rule_typeperiod,
            doc='storage content end >= storage content start - deltaSOC[last_typeperiod]')

    else:
        ### if tsam is not active classical
        ### original timeset for cyclicity rule
        m.t_endofperiod = pyomo.Set(
            within=m.t,
            initialize=t_endofperiod_list,
            ordered=True,
            doc='timestep at the end of each timeperiod')
        ### cyclicity contraint
        m.res_storage_state_cyclicity_typeperiod = pyomo.Constraint(
            m.t_endofperiod, m.sto_tuples,
            rule=res_storage_state_cyclicity_typeperiod_rule,
            doc='storage content initial == storage content at the end of each timeperiod')
    return m

### cyclicity rule without tsam
def res_storage_state_cyclicity_typeperiod_rule(m, t, stf, sit, sto, com):
    return (m.e_sto_con[m.t[1], stf, sit, sto, com] ==
            m.e_sto_con[t, stf, sit, sto, com])

### SOC rule for each repeating typeperiod
def res_delta_SOC(m, t_0, t_end, stf, sit, sto, com):
    return ( m.deltaSOC[t_end, stf, sit, sto, com] ==
             (m.typeperiod_weights[t_end] - 1) * (m.e_sto_con[t_end, stf, sit, sto, com] - m.e_sto_con[t_0, stf, sit, sto, com]))

### new storage rule using tsam considering the delta SOC per repeating typeperiod
def res_typeperiod_deltaSOC_rule(m, t_A, t_B, stf, sit, sto, com):
    return (m.e_sto_con[t_B, stf, sit, sto, com] ==
            m.e_sto_con[t_A, stf, sit, sto, com] + m.deltaSOC[t_A, stf, sit, sto, com])

### new ciclycity rule for typeperiods
def res_storage_state_cyclicity_rule_typeperiod(m, stf, sit, sto, com):
    return (m.e_sto_con[m.t[len(m.t)], stf, sit, sto, com] >=
            m.e_sto_con[m.t[1], stf, sit, sto, com] - m.deltaSOC[m.t[len(m.t)], stf, sit, sto, com])