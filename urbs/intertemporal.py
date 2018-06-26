import math
import pyomo.core as pyomo
from .modelhelper import*

def create_stf_set(m)
    # support timeframes (e.g. 2020, 2030...)
    m.stf = pyomo.Set(
        initialize=(m.commodity.index.get_level_values('support_timeframe')
                    .unique()),
        doc='Set of modeled support timeframes (e.g. years)')
    
    return m
    
def create_int_tuples(m):
    # tuple sets
    m.sit_tuples = pyomo.Set(
        within=m.stf*m.sit,
        initialize=m.site.index,
        doc='Combinations of support timeframes and sites')
    m.com_tuples = pyomo.Set(
        within=m.stf*m.sit*m.com*m.com_type,
        initialize=m.commodity.index,
        doc='Combinations of defined commodities, e.g. (2020,Mid,Elec,Demand)')
    m.pro_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=m.process.index,
        doc='Combinations of possible processes, e.g. (2020,North,Coal plant)')
    m.tra_tuples = pyomo.Set(
        within=m.stf*m.sit*m.sit*m.tra*m.com,
        initialize=m.transmission.index,
        doc='Combinations of possible transmissions, e.g. '
            '(2020,South,Mid,hvac,Elec)')
    m.sto_tuples = pyomo.Set(
        within=m.stf*m.sit*m.sto*m.com,
        initialize=m.storage.index,
        doc='Combinations of possible storage by site,'
            'e.g. (2020,Mid,Bat,Elec)')
    m.dsm_site_tuples = pyomo.Set(
        within=m.stf*m.sit*m.com,
        initialize=m.dsm.index,
        doc='Combinations of possible dsm by site, e.g. (2020, Mid, Elec)')
    m.dsm_down_tuples = pyomo.Set(
        within=m.tm*m.tm*m.stf*m.sit*m.com,
        initialize=[(t, tt, stf, site, commodity)
                    for (t, tt, stf, site, commodity)
                    in dsm_down_time_tuples(m.timesteps[1:],
                                            m.dsm_site_tuples,
                                            m)],
        doc='Combinations of possible dsm_down combinations, e.g. '
            '(5001,5003,2020,Mid,Elec)')

    # tuples for operational status of technologies
    m.operational_pro_tuples = pyomo.Set(
        within=m.sit*m.pro*m.stf*m.stf,
        initialize=[(sit, pro, stf, stf_later)
                    for (sit, pro, stf, stf_later)
                    in op_pro_tuples(m.pro_tuples, m)],
        doc='Processes that are still operational through stf_later'
            '(and the relevant years following), if built in stf'
            'in stf.')
    m.operational_tra_tuples = pyomo.Set(
        within=m.sit*m.sit*m.tra*m.com*m.stf*m.stf,
        initialize=[(sit, sit_, tra, com, stf, stf_later)
                    for (sit, sit_, tra, com, stf, stf_later)
                    in op_tra_tuples(m.tra_tuples, m)],
        doc='Transmissions that are still operational through stf_later'
            '(and the relevant years following), if built in stf'
            'in stf.')
    m.operational_sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com*m.stf*m.stf,
        initialize=[(sit, sto, com, stf, stf_later)
                    for (sit, sto, com, stf, stf_later)
                    in op_sto_tuples(m.sto_tuples, m)],
        doc='Processes that are still operational through stf_later'
            '(and the relevant years following), if built in stf'
            'in stf.')

    # tuples for residual value of technologies
    m.rv_pro_tuples = pyomo.Set(
        within=m.sit*m.pro*m.stf,
        initialize=[(sit, pro, stf)
                    for (sit, pro, stf)
                    in rest_val_pro_tuples(m.pro_tuples, m)],
        doc='Processes built in stf that are operational through the last'
            'modeled stf')
    m.rv_tra_tuples = pyomo.Set(
        within=m.sit*m.sit*m.tra*m.com*m.stf,
        initialize=[(sit, sit_, tra, com, stf)
                    for (sit, sit_, tra, com, stf)
                    in rest_val_tra_tuples(m.tra_tuples, m)],
        doc='Transmissions built in stf that are operational through the last'
            'modeled stf')
    m.rv_sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com*m.stf,
        initialize=[(sit, sto, com, stf)
                    for (sit, sto, com, stf)
                    in rest_val_sto_tuples(m.sto_tuples, m)],
        doc='Storages built in stf that are operational through the last'
            'modeled stf')

    # tuples for rest lifetime of installed capacities of technologies
    m.inst_pro_tuples = pyomo.Set(
        within=m.sit*m.pro*m.stf,
        initialize=[(sit, pro, stf)
                    for (sit, pro, stf)
                    in inst_pro_tuples(m)],
        doc=' Installed processes that are still operational through stf')
    m.inst_tra_tuples = pyomo.Set(
        within=m.sit*m.sit*m.tra*m.com*m.stf,
        initialize=[(sit, sit_, tra, com, stf)
                    for (sit, sit_, tra, com, stf)
                    in inst_tra_tuples(m)],
        doc='Installed transmissions that are still operational through stf')
    m.inst_sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com*m.stf,
        initialize=[(sit, sto, com, stf)
                    for (sit, sto, com, stf)
                    in inst_sto_tuples(m)],
        doc='Installed storages that are still operational through stf')

    # process tuples for area rule
    m.pro_area_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=m.proc_area.index,
        doc='Processes and Sites with area Restriction')

    # process input/output
    m.pro_input_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in m.r_in.index
                    if process == pro and s == stf],
        doc='Commodities consumed by process by site,'
            'e.g. (2020,Mid,PV,Solar)')
    m.pro_output_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in m.r_out.index
                    if process == pro and s == stf],
        doc='Commodities produced by process by site, e.g. (2020,Mid,PV,Elec)')

    # process tuples for maximum gradient feature
    m.pro_maxgrad_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=[(stf, sit, pro)
                    for (stf, sit, pro) in m.pro_tuples
                    if m.process.loc[stf, sit, pro]['max-grad'] < 1.0 / dt],
        doc='Processes with maximum gradient smaller than timestep length')

    # process tuples for partial feature
    m.pro_partial_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=[(stf, site, process)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, _) in m.r_in_min_fraction.index
                    if process == pro and s == stf],
        doc='Processes with partial input')

    m.pro_partial_input_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_partial_tuples
                    for (s, pro, commodity) in m.r_in_min_fraction.index
                    if process == pro and s == stf],
        doc='Commodities with partial input ratio,'
            'e.g. (2020,Mid,Coal PP,Coal)')

    m.pro_partial_output_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_partial_tuples
                    for (s, pro, commodity) in m.r_out_min_fraction.index
                    if process == pro and s == stf],
        doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,CO2)')
    
    return m 

def derive_multiplier(m):
    # Derive multiplier for all energy based costs
    m.commodity['stf_dist'] = (m.commodity['support_timeframe'].
                               apply(stf_dist, m=m))
    m.commodity['c_helper'] = (m.commodity['support_timeframe'].
                               apply(cost_helper, m=m))
    m.commodity['c_helper2'] = m.commodity['stf_dist'].apply(cost_helper2, m=m)
    m.commodity['cost_factor'] = (m.commodity['c_helper'] *
                                  m.commodity['c_helper2'])

    m.process['stf_dist'] = m.process['support_timeframe'].apply(stf_dist, m=m)
    m.process['c_helper'] = (m.process['support_timeframe'].
                             apply(cost_helper, m=m))
    m.process['c_helper2'] = m.process['stf_dist'].apply(cost_helper2, m=m)
    m.process['cost_factor'] = m.process['c_helper'] * m.process['c_helper2']

    m.transmission['stf_dist'] = (m.transmission['support_timeframe'].
                                  apply(stf_dist, m=m))
    m.transmission['c_helper'] = (m.transmission['support_timeframe'].
                                  apply(cost_helper, m=m))
    m.transmission['c_helper2'] = (m.transmission['stf_dist'].
                                   apply(cost_helper2, m=m))
    m.transmission['cost_factor'] = (m.transmission['c_helper'] *
                                     m.transmission['c_helper2'])

    m.storage['stf_dist'] = m.storage['support_timeframe'].apply(stf_dist, m=m)
    m.storage['c_helper'] = (m.storage['support_timeframe']
                             .apply(cost_helper, m=m))
    m.storage['c_helper2'] = m.storage['stf_dist'].apply(cost_helper2, m=m)
    m.storage['cost_factor'] = m.storage['c_helper'] * m.storage['c_helper2']
    
    return m

"""
# Constraints

# commodity

# vertex equation: calculate balance for given commodity and site;
# contains implicit constraints for process activity, import/export and
# storage activity (calculated by function commodity_balance);
# contains implicit constraint for stock commodity source term
def res_vertex_rule(m, tm, stf, sit, com, com_type):
    # environmental or supim commodities don't have this constraint (yet)
    if com in m.com_env:
        return pyomo.Constraint.Skip
    if com in m.com_supim:
        return pyomo.Constraint.Skip

    # helper function commodity_balance calculates balance from input to
    # and output from processes, storage and transmission.
    # if power_surplus > 0: production/storage/imports create net positive
    #                       amount of commodity com
    # if power_surplus < 0: production/storage/exports consume a net
    #                       amount of the commodity com
    power_surplus = - commodity_balance(m, tm, stf, sit, com)

    # if com is a stock commodity, the commodity source term e_co_stock
    # can supply a possibly negative power_surplus
    if com in m.com_stock:
        power_surplus += m.e_co_stock[tm, stf, sit, com, com_type]

    # if com is a sell commodity, the commodity source term e_co_sell
    # can supply a possibly positive power_surplus
    if com in m.com_sell:
        power_surplus -= m.e_co_sell[tm, stf, sit, com, com_type]

    # if com is a buy commodity, the commodity source term e_co_buy
    # can supply a possibly negative power_surplus
    if com in m.com_buy:
        power_surplus += m.e_co_buy[tm, stf, sit, com, com_type]

    # if com is a demand commodity, the power_surplus is reduced by the
    # demand value; no scaling by m.dt or m.weight is needed here, as this
    # constraint is about power (MW), not energy (MWh)
    if com in m.com_demand:
        try:
            power_surplus -= m.demand_dict[(sit, com)][(stf, tm)]

        except KeyError:
            pass
    # if sit com is a dsm tuple, the power surplus is decreased by the
    # upshifted demand and increased by the downshifted demand.
    if (stf, sit, com) in m.dsm_site_tuples:
        power_surplus -= m.dsm_up[tm, stf, sit, com]
        power_surplus += sum(m.dsm_down[t, tm, stf, sit, com]
                             for t in dsm_time_tuples(
                                 tm, m.timesteps[1:],
                                 m.dsm_dict['delay'][(stf, sit, com)]))
    return power_surplus == 0


# demand side management (DSM) constraints


# DSMup == DSMdo * efficiency factor n
def def_dsm_variables_rule(m, tm, stf, sit, com):
    dsm_down_sum = 0
    for tt in dsm_time_tuples(tm,
                              m.timesteps[1:],
                              m.dsm_dict['delay'][(stf, sit, com)]):
        dsm_down_sum += m.dsm_down[tm, tt, stf, sit, com]
    return dsm_down_sum == (m.dsm_up[tm, stf, sit, com] *
                            m.dsm_dict['eff'][(stf, sit, com)])


# DSMup <= Cup (threshold capacity of DSMup)
def res_dsm_upward_rule(m, tm, stf, sit, com):
    return (m.dsm_up[tm, stf, sit, com] <=
            int(m.dsm_dict['cap-max-up'][(stf, sit, com)]))


# DSMdo <= Cdo (threshold capacity of DSMdo)
def res_dsm_downward_rule(m, tm, stf, sit, com):
    dsm_down_sum = 0
    for t in dsm_time_tuples(tm,
                             m.timesteps[1:],
                             m.dsm_dict['delay'][(stf, sit, com)]):
        dsm_down_sum += m.dsm_down[t, tm, stf, sit, com]
    return dsm_down_sum <= m.dsm_dict['cap-max-do'][(stf, sit, com)]


# DSMup + DSMdo <= max(Cup,Cdo)
def res_dsm_maximum_rule(m, tm, stf, sit, com):
    dsm_down_sum = 0
    for t in dsm_time_tuples(tm,
                             m.timesteps[1:],
                             m.dsm_dict['delay'][(stf, sit, com)]):
        dsm_down_sum += m.dsm_down[t, tm, stf, sit, com]

    max_dsm_limit = max(m.dsm_dict['cap-max-up'][(stf, sit, com)],
                        m.dsm_dict['cap-max-do'][(stf, sit, com)])
    return m.dsm_up[tm, stf, sit, com] + dsm_down_sum <= max_dsm_limit


# DSMup(t, t + recovery time R) <= Cup * delay time L
def res_dsm_recovery_rule(m, tm, stf, sit, com):
    dsm_up_sum = 0
    for t in dsm_recovery(tm,
                          m.timesteps[1:],
                          m.dsm_dict['recov'][(stf, sit, com)]):
        dsm_up_sum += m.dsm_up[t, stf, sit, com]
    return dsm_up_sum <= (m.dsm_dict['cap-max-up'][(stf, sit, com)] *
                          m.dsm_dict['delay'][(stf, sit, com)])


# stock commodity purchase == commodity consumption, according to
# commodity_balance of current (time step, site, commodity);
# limit stock commodity use per time step
def res_stock_step_rule(m, tm, stf, sit, com, com_type):
    if com not in m.com_stock:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_stock[tm, stf, sit, com, com_type] <=
                m.commodity_dict['maxperstep'][(stf, sit, com, com_type)])


# limit stock commodity use in total (scaled to annual consumption, thanks
# to m.weight)
def res_stock_total_rule(m, stf, sit, com, com_type):
    if com not in m.com_stock:
        return pyomo.Constraint.Skip
    else:
        # calculate total consumption of commodity com
        total_consumption = 0
        for tm in m.tm:
            total_consumption += (
                m.e_co_stock[tm, stf, sit, com, com_type] * m.dt)
        total_consumption *= m.weight
        return (total_consumption <=
                m.commodity_dict['max'][(stf, sit, com, com_type)])


# limit sell commodity use per time step
def res_sell_step_rule(m, tm, stf, sit, com, com_type):
    if com not in m.com_sell:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_sell[tm, stf, sit, com, com_type] <=
                m.commodity_dict['maxperstep'][(stf, sit, com, com_type)])


# limit sell commodity use in total (scaled to annual consumption, thanks
# to m.weight)
def res_sell_total_rule(m, stf, sit, com, com_type):
    if com not in m.com_sell:
        return pyomo.Constraint.Skip
    else:
        # calculate total sale of commodity com
        total_consumption = 0
        for tm in m.tm:
            total_consumption += (
                m.e_co_sell[tm, stf, sit, com, com_type] * m.dt)
        total_consumption *= m.weight
        return (total_consumption <=
                m.commodity_dict['max'][(stf, sit, com, com_type)])


# limit buy commodity use per time step
def res_buy_step_rule(m, tm, stf, sit, com, com_type):
    if com not in m.com_buy:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_buy[tm, stf, sit, com, com_type] <=
                m.commodity_dict['maxperstep'][(stf, sit, com, com_type)])


# limit buy commodity use in total (scaled to annual consumption, thanks
# to m.weight)
def res_buy_total_rule(m, stf, sit, com, com_type):
    if com not in m.com_buy:
        return pyomo.Constraint.Skip
    else:
        # calculate total sale of commodity com
        total_consumption = 0
        for tm in m.tm:
            total_consumption += (
                m.e_co_buy[tm, stf, sit, com, com_type] * m.dt)
        total_consumption *= m.weight
        return (total_consumption <=
                m.commodity_dict['max'][(stf, sit, com, com_type)])


# environmental commodity creation == - commodity_balance of that commodity
# used for modelling emissions (e.g. CO2) or other end-of-pipe results of
# any process activity;
# limit environmental commodity output per time step
def res_env_step_rule(m, tm, stf, sit, com, com_type):
    if com not in m.com_env:
        return pyomo.Constraint.Skip
    else:
        environmental_output = - commodity_balance(m, tm, stf, sit, com)
        return (environmental_output <=
                m.commodity_dict['maxperstep'][(stf, sit, com, com_type)])


# limit environmental commodity output in total (scaled to annual
# emissions, thanks to m.weight)
def res_env_total_rule(m, stf, sit, com, com_type):
    if com not in m.com_env:
        return pyomo.Constraint.Skip
    else:
        # calculate total creation of environmental commodity com
        env_output_sum = 0
        for tm in m.tm:
            env_output_sum += (- commodity_balance(m, tm, stf, sit, com) *
                               m.dt)
        env_output_sum *= m.weight
        return (env_output_sum <=
                m.commodity_dict['max'][(stf, sit, com, com_type)])


# process

# process capacity == new capacity + existing capacity
def def_process_capacity_rule(m, stf, sit, pro):
    if (sit, pro, stf) in m.inst_pro_tuples:
        return (m.cap_pro[stf, sit, pro] ==
            sum(m.cap_pro_new[stf_built, sit, pro]
            for stf_built in m.stf
            if (sit, pro, stf_built, stf) in m.operational_pro_tuples) + 
            m.process_dict['inst-cap'][(min(m.stf), sit, pro)])
    else:
        return (m.cap_pro[stf, sit, pro] ==
            sum(m.cap_pro_new[stf_built, sit, pro]
            for stf_built in m.stf
            if (sit, pro, stf_built, stf) in m.operational_pro_tuples))


# process input power == process throughput * input ratio
def def_process_input_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_in[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m.r_in_dict[(stf, pro, com)])


# process output power = process throughput * output ratio
def def_process_output_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_out[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m.r_out_dict[(stf, pro, com)])


# process input (for supim commodity) = process capacity * timeseries
def def_intermittent_supply_rule(m, tm, stf, sit, pro, coin):
    if coin in m.com_supim:
        return (m.e_pro_in[tm, stf, sit, pro, coin] ==
                m.cap_pro[stf, sit, pro] *
                m.supim_dict[(sit, coin)][(stf, tm)])
    else:
        return pyomo.Constraint.Skip


# process throughput <= process capacity
def res_process_throughput_by_capacity_rule(m, tm, stf, sit, pro):
    return (m.tau_pro[tm, stf, sit, pro] <= m.cap_pro[stf, sit, pro])


def res_process_maxgrad_lower_rule(m, t, stf, sit, pro):
    return (m.tau_pro[t-1, stf, sit, pro] -
            m.cap_pro[stf, sit, pro] *
            m.process_dict['max-grad'][(stf, sit, pro)] * m.dt <=
            m.tau_pro[t, stf, sit, pro])


def res_process_maxgrad_upper_rule(m, t, stf, sit, pro):
    return (m.tau_pro[t-1, stf, sit, pro] +
            m.cap_pro[stf, sit, pro] *
            m.process_dict['max-grad'][(stf, sit, pro)] * m.dt >=
            m.tau_pro[t, stf, sit, pro])


def res_throughput_by_capacity_min_rule(m, tm, stf, sit, pro):
    return (m.tau_pro[tm, stf, sit, pro] >=
            m.cap_pro[stf, sit, pro] *
            m.process_dict['min-fraction'][(stf, sit, pro)])


def def_partial_process_input_rule(m, tm, stf, sit, pro, coin):
    # input ratio at maximum operation point
    R = m.r_in.loc[stf, pro, coin]
    # input ratio at lowest operation point
    r = m.r_in_min_fraction[stf, pro, coin]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)

    return (m.e_pro_in[tm, stf, sit, pro, coin] ==
            m.cap_pro[stf, sit, pro] * online_factor +
            m.tau_pro[tm, stf, sit, pro] * throughput_factor)


def def_partial_process_output_rule(m, tm, stf, sit, pro, coo):
    # input ratio at maximum operation point
    R = m.r_out.loc[stf, pro, coo]
    # input ratio at lowest operation point
    r = m.r_out_min_fraction[stf, pro, coo]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)

    return (m.e_pro_out[tm, stf, sit, pro, coo] ==
            m.cap_pro[stf, sit, pro] * online_factor +
            m.tau_pro[tm, stf, sit, pro] * throughput_factor)


# lower bound <= process capacity <= upper bound
def res_process_capacity_rule(m, stf, sit, pro):
    return (m.process_dict['cap-lo'][stf, sit, pro],
            m.cap_pro[stf, sit, pro],
            m.process_dict['cap-up'][stf, sit, pro])


# used process area <= maximal process area
def res_area_rule(m, stf, sit):
    if m.site.loc[stf, sit]['area'] >= 0 and sum(
                         m.process.loc[(st, s, p), 'area-per-cap']
                         for (st, s, p) in m.pro_area_tuples
                         if s == sit and st == stf) > 0:
        total_area = sum(m.cap_pro[st, s, p] *
                         m.process.loc[(st, s, p), 'area-per-cap']
                         for (st, s, p) in m.pro_area_tuples
                         if s == sit and st == stf)
        return total_area <= m.site.loc[stf, sit]['area']
    else:
        # Skip constraint, if area is not numeric
        return pyomo.Constraint.Skip


# power connection capacity: Sell == Buy
def res_sell_buy_symmetry_rule(m, stf, sit_in, pro_in, coin):
    # constraint only for sell and buy processes
    # and the processes must be in the same site
    if coin in m.com_buy:
        sell_pro = search_sell_buy_tuple(m, stf, sit_in, pro_in, coin)
        if sell_pro is None:
            return pyomo.Constraint.Skip
        else:
            return (m.cap_pro[stf, sit_in, pro_in] ==
                    m.cap_pro[stf, sit_in, sell_pro])
    else:
        return pyomo.Constraint.Skip


# transmission

# transmission capacity == new capacity + existing capacity
def def_transmission_capacity_rule(m, stf, sin, sout, tra, com):
    if (sin, sout, tra, com, stf) in m.inst_tra_tuples:
        return (m.cap_tra[stf, sin, sout, tra, com] ==
                sum(m.cap_tra_new[stf_built, sin, sout, tra, com]
                for stf_built in m.stf
                if (sin, sout, tra, com, stf_built, stf) in
                m.operational_tra_tuples) +
                m.transmission_dict['inst-cap']
                [(min(m.stf), sin, sout, tra, com)])
    else:
        return (m.cap_tra[stf, sin, sout, tra, com] ==
                sum(m.cap_tra_new[stf_built, sin, sout, tra, com]
                for stf_built in m.stf
                if (sin, sout, tra, com, stf_built, stf) in
                m.operational_tra_tuples))


# transmission output == transmission input * efficiency
def def_transmission_output_rule(m, tm, stf, sin, sout, tra, com):
    return (m.e_tra_out[tm, stf, sin, sout, tra, com] ==
            m.e_tra_in[tm, stf, sin, sout, tra, com] *
            m.transmission_dict['eff'][(stf, sin, sout, tra, com)])


# transmission input <= transmission capacity
def res_transmission_input_by_capacity_rule(m, tm, stf, sin, sout, tra, com):
    return (m.e_tra_in[tm, stf, sin, sout, tra, com] <=
            m.cap_tra[stf, sin, sout, tra, com])


# lower bound <= transmission capacity <= upper bound
def res_transmission_capacity_rule(m, stf, sin, sout, tra, com):
    return (m.transmission_dict['cap-lo'][(stf, sin, sout, tra, com)],
            m.cap_tra[stf, sin, sout, tra, com],
            m.transmission_dict['cap-up'][(stf, sin, sout, tra, com)])


# transmission capacity from A to B == transmission capacity from B to A
def res_transmission_symmetry_rule(m, stf, sin, sout, tra, com):
    return m.cap_tra[stf, sin, sout, tra, com] == (m.cap_tra
                                                   [stf, sout, sin, tra, com])


# storage

# storage content in timestep [t] == storage content[t-1] * (1-discharge)
# + newly stored energy * input efficiency
# - retrieved energy / output efficiency
def def_storage_state_rule(m, t, stf, sit, sto, com):
    return (m.e_sto_con[t, stf, sit, sto, com] ==
            m.e_sto_con[t-1, stf, sit, sto, com] *
            (1 - m.storage_dict['discharge'][(stf, sit, sto, com)]) +
            m.e_sto_in[t, stf, sit, sto, com] *
            m.storage_dict['eff-in'][(stf, sit, sto, com)] * m.dt -
            m.e_sto_out[t, stf, sit, sto, com] /
            m.storage_dict['eff-out'][(stf, sit, sto, com)] * m.dt)


def def_storage_power_rule(m, stf, sit, sto, com):
    if (sit, sto, com, stf) in m.inst_sto_tuples:
        return (m.cap_sto_p[stf, sit, sto, com] ==
                sum(m.cap_sto_p_new[stf_built, sit, sto, com]
                for stf_built in m.stf
                if (sit, sto, com, stf_built, stf) in
                    m.operational_sto_tuples) +
                    m.storage_dict['inst-cap-p'][(stf, sit, sto, com)])
    else:
        return (m.cap_sto_p[stf, sit, sto, com] ==
                sum(m.cap_sto_p_new[stf_built, sit, sto, com]
                for stf_built in m.stf
                if (sit, sto, com, stf_built, stf) in m.operational_sto_tuples)
                )

# storage capacity == new storage capacity + existing storage capacity
def def_storage_capacity_rule(m, stf, sit, sto, com):
    if (sit, sto, com, stf) in m.inst_sto_tuples:
        return (m.cap_sto_c[stf, sit, sto, com] ==
                sum(m.cap_sto_c_new[stf_built, sit, sto, com]
                for stf_built in m.stf
                if (sit, sto, com, stf_built, stf) in
                    m.operational_sto_tuples) +
                    m.storage_dict['inst-cap-c'][(stf, sit, sto, com)])
    else:
        return (m.cap_sto_c[stf, sit, sto, com] ==
                sum(m.cap_sto_c_new[stf_built, sit, sto, com]
                for stf_built in m.stf
                if (sit, sto, com, stf_built, stf) in m.operational_sto_tuples)
                )


# storage input <= storage power
def res_storage_input_by_power_rule(m, t, stf, sit, sto, com):
    return m.e_sto_in[t, stf, sit, sto, com] <= m.cap_sto_p[stf, sit, sto, com]


# storage output <= storage power
def res_storage_output_by_power_rule(m, t, stf, sit, sto, co):
    return m.e_sto_out[t, stf, sit, sto, co] <= m.cap_sto_p[stf, sit, sto, co]


# storage content <= storage capacity
def res_storage_state_by_capacity_rule(m, t, stf, sit, sto, com):
    return (m.e_sto_con[t, stf, sit, sto, com] <=
            m.cap_sto_c[stf, sit, sto, com])


# lower bound <= storage power <= upper bound
def res_storage_power_rule(m, stf, sit, sto, com):
    return (m.storage_dict['cap-lo-p'][(stf, sit, sto, com)],
            m.cap_sto_p[stf, sit, sto, com],
            m.storage_dict['cap-up-p'][(stf, sit, sto, com)])


# lower bound <= storage capacity <= upper bound
def res_storage_capacity_rule(m, stf, sit, sto, com):
    return (m.storage_dict['cap-lo-c'][(stf, sit, sto, com)],
            m.cap_sto_c[stf, sit, sto, com],
            m.storage_dict['cap-up-c'][(stf, sit, sto, com)])


# initialization of storage content in first timestep t[1]
# forced minimun  storage content in final timestep t[len(m.t)]
# content[t=1] == storage capacity * fraction <= content[t=final]
def res_initial_and_final_storage_state_rule(m, t, stf, sit, sto, com):
    if t == m.t[1]:  # first timestep (Pyomo uses 1-based indexing)
        return (m.e_sto_con[t, stf, sit, sto, com] ==
                m.cap_sto_c[stf, sit, sto, com] *
                m.storage_dict['init'][(stf, sit, sto, com)])
    elif t == m.t[len(m.t)]:  # last timestep
        return (m.e_sto_con[t, stf, sit, sto, com] >=
                m.cap_sto_c[stf, sit, sto, com] *
                m.storage_dict['init'][(stf, sit, sto, com)])
    else:
        return pyomo.Constraint.Skip


# total CO2 output <= Global CO2 limit
def res_global_co2_limit_rule(m, stf):
    if math.isinf(m.global_prop.loc[stf, 'CO2 limit']['value']):
        return pyomo.Constraint.Skip
    elif m.global_prop.loc[stf, 'CO2 limit']['value'] >= 0:
        co2_output_sum = 0
        for tm in m.tm:
            for sit in m.sit:
                # minus because negative commodity_balance represents creation
                # of that commodity.
                co2_output_sum += (- commodity_balance(m, tm,
                                                       stf, sit, 'CO2') *
                                   m.dt)

        # scaling to annual output (cf. definition of m.weight)
        co2_output_sum *= m.weight
        return (co2_output_sum <= m.global_prop.loc[stf, 'CO2 limit']['value'])
    else:
        return pyomo.Constraint.Skip
    
    
"""

def invcost_factor(m, n, i, year_built):
    """Investment cost factor formula.

    Evaluates the factor multiplied to the invest costs
    for depreciation duration and interest rate.

    Args:
        n: depreciation period (years)
        i: interest rate (e.g. 0.06 means 6 %)
        year_built: year utility is built
        j: discount rate for intertmeporal planning
    """
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])
    if j == 0:
        return n * ((1+i) ** n * i)/((1+i) ** n - 1)
    else:
        return ((1+j) ** (-(year_built-m.global_prop.index.min()[0])) *
                (i * (1+i) ** n * ((1+j) ** n - 1)) /
                (j * (1+j) ** n * ((1+i) ** n - 1)))


def rv_factor(m, n, i, year_built):
    """Rest value factor formula.

    Evaluates the factor multiplied to the invest costs
    for the rest value of a unit after the end of the
    optimization period.

    Args:
        n: depreciation period (years)
        i: interest rate (e.g. 0.06 means 6 %)
        year_built: year utility is built
        j: discount rate for intertmeporal planning
        k: operational time after simulation horizon
    """
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])
    k = (year_built + n) - m.global_prop.index.max()[0] - 1

    if j == 0:
        return k * ((1+i) ** n * i)/((1+i) ** n - 1)
    else:
        return ((1+j) ** (-(year_built-m.global_prop.index.min()[0])) *
                (i * (1+i)** n * ((1+j) ** k - 1)) /
                (j * (1+j) ** n * ((1+i) ** n - 1)))


# Energy related costs
def stf_dist(stf, m):
    """Calculates the distance between the modeled support timeframes.
    """
    sorted_stf = sorted(list(m.commodity.index.
                             get_level_values('support_timeframe').unique()))
    dist = []

    for s in sorted_stf:
        if s == max(sorted_stf):
            dist.append(1)
        else:
            dist.append(sorted_stf[sorted_stf.index(s) + 1] - s)

    return dist[sorted_stf.index(stf)]


def cost_helper(stf, m):
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])

    return (1+j) ** (1-(stf-m.global_prop.index.min()[0]))


def cost_helper2(dist, m):
    """Factor for variable, fuel, purchase, sell, and fix costs.
    Calculated by repetition of modeled stfs and discount utility.
    """
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])

    if j == 0:
        return dist
    else:
        return (1-(1+j) ** (-dist)) / j
    
def op_pro_tuples(pro_tuple, m):
    """ Tuples for operational status of units (processes, transmissions,
    storages) for intertemporal planning.

    Only such tuples where the unit is still operational until the next
    support time frame are valid.
    """
    op_pro = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, pro) in pro_tuple:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(sorted_stf):
                if stf_later <= stf + m.process.loc[(stf, sit, pro),
                                                    'depreciation']:
                    op_pro.append((sit, pro, stf, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  stf + m.process.loc[(stf, sit, pro), 'depreciation'] and
                  stf <= stf_later):
                op_pro.append((sit, pro, stf, stf_later))
            else:
                pass

    return op_pro


def op_tra_tuples(tra_tuple, m):
    """ s.a. op_pro_tuples
    """
    op_tra = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit1, sit2, tra, com) in tra_tuple:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(sorted_stf):
                if (stf_later <=
                    stf + m.transmission.loc[(stf, sit1, sit2, tra, com),
                                             'depreciation']):
                    op_tra.append((sit1, sit2, tra, com, stf, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  stf + m.transmission.loc[(stf, sit1, sit2, tra, com),
                                           'depreciation'] and
                  stf <= stf_later):
                op_tra.append((sit1, sit2, tra, com, stf, stf_later))
            else:
                pass

    return op_tra


def op_sto_tuples(sto_tuple, m):
    """ s.a. op_pro_tuples
    """
    op_sto = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, sto, com) in sto_tuple:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(sorted_stf):
                if stf_later <= stf + m.storage.loc[(stf, sit, sto, com),
                                                    'depreciation']:
                    op_sto.append((sit, sto, com, stf, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  stf +
                  m.storage.loc[(stf, sit, sto, com), 'depreciation'] and
                  stf <= stf_later):
                op_sto.append((sit, sto, com, stf, stf_later))
            else:
                pass

    return op_sto


def rest_val_pro_tuples(pro_tuple, m):
    """ Tuples for rest value determination of units.

        The last entry represents the remaining life time after the end of the
        modeled time frame.
    """
    rv_pro = []

    for (stf, sit, pro) in pro_tuple:
        if stf + m.process.loc[(stf, sit, pro), 'depreciation'] > max(m.stf):
            rv_pro.append((sit, pro, stf))

    return rv_pro


def rest_val_tra_tuples(tra_tuple, m):
    """ s.a. rest_val_pro_tuples
    """
    rv_tra = []

    for (stf, sit1, sit2, tra, com) in tra_tuple:
        if (stf +
            m.transmission.loc[(stf, sit1, sit2, tra, com), 'depreciation'] >
            max(m.stf)):
            rv_tra.append((sit1, sit2, tra, com, stf))

    return rv_tra


def rest_val_sto_tuples(sto_tuple, m):
    """ s.a. rest_val_pro_tuples
    """
    rv_sto = []

    for (stf, sit, sto, com) in sto_tuple:
        if (stf + m.storage.loc[(stf, sit, sto, com), 'depreciation'] >
            max(m.stf)):
            rv_sto.append((sit, sto, com, stf))

    return rv_sto


def inst_pro_tuples(m):
    """ Tuples for operational status of already installed units
    (processes, transmissions, storages) for intertemporal planning.

    Only such tuples where the unit is still operational until the next
    support time frame are valid.
    """
    inst_pro = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, pro) in m.inst_pro.index:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(m.stf):
                if (stf_later <
                    min(m.stf) + m.process.loc[(stf, sit, pro),
                                               'lifetime']):
                    inst_pro.append((sit, pro, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  min(m.stf) + m.process.loc[(stf, sit, pro),
                                             'lifetime']):
                inst_pro.append((sit, pro, stf_later))

    return inst_pro


def inst_tra_tuples(m):
    """ s.a. inst_pro_tuples
    """
    inst_tra = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit1, sit2, tra, com) in m.inst_tra.index:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(m.stf):
                if (stf_later <
                    min(m.stf) +
                    m.transmission.loc[(stf, sit1, sit2, tra, com),
                                       'lifetime']):
                    inst_tra.append((sit1, sit2, tra, com, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  min(m.stf) + m.transmission.loc[(stf, sit1, sit2, tra, com),
                                                  'lifetime']):
                inst_tra.append((sit1, sit2, tra, com, stf_later))

    return inst_tra


def inst_sto_tuples(m):
    """ s.a. inst_pro_tuples
    """
    inst_sto = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, sto, com) in m.inst_sto.index:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(m.stf):
                if (stf_later <
                    min(m.stf) + m.storage.loc[(stf, sit, sto, com),
                                               'lifetime']):
                    inst_sto.append((sit, sto, com, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  min(m.stf) + m.storage.loc[(stf, sit, sto, com),
                                             'lifetime']):
                inst_sto.append((sit, sto, com, stf_later))

    return inst_sto