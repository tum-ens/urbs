import math
import pyomo.core as pyomo
import pandas as pd
import tsam.timeseriesaggregation as tsam
from datetime import datetime, timedelta
import numpy as np
import itertools  as it
from urbs.identify import *

def run_tsam(data, noTypicalPeriods, hoursPerPeriod):
    ###bring together all time series data
    time_series_data = pd.concat([data['demand'], data['supim'], data['buy_sell_price'], data['eff_factor']], axis=1,sort=True)
    ###prepare datetime vector which is required by tsam method
    date_hour = np.arange(datetime(2021, 1, 1), datetime(2022, 1, 1), timedelta(hours=1)).astype(datetime).T
    ###prepare df for tsam
    time_series_data = time_series_data.iloc[1:, :] #drop initialization timestep
    time_series_data['DateTime'] = date_hour #add column with datetime
    time_series_data = time_series_data.set_index('DateTime') #set required index for tsam method
    ###apply tsam method described in: https://tsam.readthedocs.io/en/latest/index.html
    aggregation = tsam.TimeSeriesAggregation(time_series_data, noTypicalPeriods=noTypicalPeriods,
                                             hoursPerPeriod=hoursPerPeriod, clusterMethod='hierarchical')
    ###store tsam results
    typPeriods = aggregation.createTypicalPeriods()
    orderPeriods = aggregation.clusterOrder
    #tsam_data = aggregation.predictOriginalData()
    #weights = aggregation.clusterPeriodNoOccur # is not used because detailed information considering interruptions is taken out of orderPeriods

    ### adjust the modeling steps and the weight vector accordingly to the generated typeweeks including interruptions and its order
    requiredPeriods = [x[0] for x in it.groupby(orderPeriods)] #determine borders of subsequent typeperiods to model
    timeframe = requiredPeriods.__len__() * hoursPerPeriod + 1 #determine total number of modeled typeperiod timesteps
    last_period_nr = orderPeriods[-1] #identify last element as this one represents only a day not a week
    ### store the occurence with its resulting weight for each modeled part typeperiod
    occurence_weight_factor = []
    for item in np.sort(np.unique(requiredPeriods)):
        occurence_weight_factor.append([sum(1 for _ in group) for key, group in it.groupby(orderPeriods) if key==item]) #create list showing the weight of each part of the typeperiod that must be modeled
    occurence_weight_factor[last_period_nr][-1] = occurence_weight_factor[last_period_nr][-1] \
                                                  - 1 + (8760 % hoursPerPeriod)/hoursPerPeriod #consider that a year normally can not be divided in an integer number of typeperiods
    ###prepare dataframe, Series and helper variables for concatenation of new data
    modeling_steps = time_series_data.iloc[0:1, :]
    modeling_steps.iloc[0,:] = 0
    weight_vector = pd.Series([0])
    weighting_order = []
    occurence_counter = np.zeros(noTypicalPeriods).astype(int)
    ###concat typerperiod time series data according to the modelled typerperiod order and concat its related weight series
    for type_nr in requiredPeriods:
        modeling_steps = pd.concat([modeling_steps, typPeriods.loc[pd.IndexSlice[type_nr, :], :]], ignore_index=True) #concat all relevant timeseries data in one dataframe
        weight_numbers = pd.Series(np.ones(hoursPerPeriod) * occurence_weight_factor[type_nr][occurence_counter[type_nr]])
        weighting_order.append(occurence_weight_factor[type_nr][occurence_counter[type_nr]])
        weight_vector = pd.concat([weight_vector, weight_numbers], ignore_index=True)
        occurence_counter[type_nr] += 1

    ###rewrite weight data with new computed weights for new timeframe
    data['type period'].update(pd.Series(weight_vector.values, name='weight_typeperiod', index =data['type period'].index[0:timeframe]))
    ###rewrite demand load data
    data['demand'] = data['demand'].iloc[0:timeframe, :]
    for column in data['demand']:
        data['demand'][column].iloc[0:timeframe] = modeling_steps[column].values
    ###rewrite fluctuating resource data
    data['supim'] = data['supim'].iloc[0:timeframe, :]
    for column in data['supim']:
        data['supim'][column].iloc[0:timeframe] = modeling_steps[column].values
    ###rewrite Buy/Sell Prices
    data['buy_sell_price'] = data['buy_sell_price'].iloc[0:timeframe, :]
    for column in data['buy_sell_price']:
        data['buy_sell_price'][column].iloc[0:timeframe] = modeling_steps[column].values
    ###rewrite Variable efficiencies
    data['eff_factor'] = data['eff_factor'].iloc[0:timeframe, :]
    for column in data['eff_factor']:
        data['eff_factor'][column].iloc[0:timeframe] = modeling_steps[column].values

    ###return new timestep range
    timesteps_new = range(0, timeframe)

    return data, timesteps_new, weighting_order

###function to store relevant parameters from other modules in model
def store_typeperiod_parameter(m, hoursPerPeriod, weighting_order):
    m.hoursPerPeriod = hoursPerPeriod
    m.weighting_order = weighting_order
    return m

def add_typeperiod(m):
    # Validation:
    # if not (len(m.timesteps) % 168 == 0 or len(m.timesteps) % 168 == 1):
    #     print('Warning: length of timesteps does not end at the end of the type period!')

    ###change weight parameter to 1, since the whole year is representated by weight_typeperiod
    m.del_component(m.weight)
    m.weight = pyomo.Param(
        initialize=1,
        doc='Pre-factor for variable costs and emissions for annual result for type period = 1')

    ###create list with all period ends
    t_endofperiod_list = [i * 168 * m.dt for i in list(range(1,1+int(len(m.timesteps) / m.dt / 168)))]

    if m.mode['tsam']:
        ###prepare time lists for set tuples
        start_end_typeperiods_list = []
        for hour in t_endofperiod_list:
            start_end_typeperiods_list.append((hour + 1 - m.hoursPerPeriod, hour))

        subsequent_typeperiods_list = []
        t_endofperiod_list_without_last = t_endofperiod_list[0:-1]
        for hour in t_endofperiod_list_without_last:
            subsequent_typeperiods_list.append((hour,hour+1))

        ###allocate weights to the specific period with a dict
        m.typeperiod_weights = dict(zip(t_endofperiod_list, m.weighting_order))

        ###define timeperiod sets
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

        ###variable to describe storage SOC
        m.deltaSOC = pyomo.Var(
            m.t_endofperiod, m.sto_tuples,
            within=pyomo.Reals,
            doc='Variable to describe the delta of a storage within each period')

        ###constraint to describe the difference of a storage within a repeating period
        m.res_delta_SOC = pyomo.Constraint(
            m.start_end_typeperiods, m.sto_tuples,
            rule=res_delta_SOC,
            doc='delta SOC = weight * (state(end) - state(start)) of a period')

        ###SOC constraint for consecutive typeperiods
        m.res_typeperiod_delta_SOC = pyomo.Constraint(
            m.subsequent_typeperiods, m.sto_tuples,
            rule=res_typeperiod_deltaSOC_rule,
            doc='Constraint to ensure that the transition between typeperiods includes the seasonal SOC delta to'
                'allow consideration of seasonal storage')

        ### delete old ciclycity rule to enable typeperiod simulation
        del m.res_storage_state_cyclicity
        ### adjusted ciclycity constraint for typeperiods
        m.res_storage_state_cyclicity_typeperiod = pyomo.Constraint(
            m.sto_tuples,
            rule=res_storage_state_cyclicity_rule_typeperiod,
            doc='storage content end >= storage content start - deltaSOC[last_typeperiod]')

    else:
        ###original timeset for cyclicity rule
        m.t_endofperiod = pyomo.Set(
            within=m.t,
            initialize=t_endofperiod_list,
            ordered=True,
            doc='timestep at the end of each timeperiod')
        ###cyclicity contraint
        m.res_storage_state_cyclicity_typeperiod = pyomo.Constraint(
            m.t_endofperiod, m.sto_tuples,
            rule=res_storage_state_cyclicity_typeperiod_rule,
            doc='storage content initial == storage content at the end of each timeperiod')

    return m

###cyclicity rule without tsam
def res_storage_state_cyclicity_typeperiod_rule(m, t, stf, sit, sto, com):
    return (m.e_sto_con[m.t[1], stf, sit, sto, com] ==
            m.e_sto_con[t, stf, sit, sto, com])

###SOC rule for each repeating typeperiod
def res_delta_SOC(m, t_0, t_end, stf, sit, sto, com):
    return ( m.deltaSOC[t_end, stf, sit, sto, com] ==
             (m.typeperiod_weights[t_end] - 1) * (m.e_sto_con[t_end, stf, sit, sto, com] - m.e_sto_con[t_0, stf, sit, sto, com]))

###new storage rule using tsam considering the delta SOC per repeating typeperiod
def res_typeperiod_deltaSOC_rule(m, t_A, t_B, stf, sit, sto, com):
    return (m.e_sto_con[t_B, stf, sit, sto, com] ==
            m.e_sto_con[t_A, stf, sit, sto, com] + m.deltaSOC[t_A, stf, sit, sto, com])

### new ciclycity rule for typeperiods
def res_storage_state_cyclicity_rule_typeperiod(m, stf, sit, sto, com):
    return (m.e_sto_con[m.t[len(m.t)], stf, sit, sto, com] >=
            m.e_sto_con[m.t[1], stf, sit, sto, com] - m.deltaSOC[m.t[len(m.t)], stf, sit, sto, com])