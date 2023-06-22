import math
import pyomo.core as pyomo

def add_advanced_processes(m):

    # process tuples for time variable efficiency
    if m.mode['tve']:
        tve_stflist = set()
        # get all support timeframes for which time variable efficiency is enabled
        for key in m.eff_factor_dict[tuple(m.eff_factor_dict.keys())[0]]:
            tve_stflist.add(tuple(key)[0])
        m.pro_timevar_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, site, process, commodity)
                        for stf in tve_stflist
                        for (site, process) in tuple(m.eff_factor_dict.keys())
                        for (st, pro, commodity) in tuple(m.r_out_dict.keys())
                        if process == pro and st == stf and commodity not in
                        m.com_env],
            doc='Outputs of processes with time dependent efficiency')
    else:
        # empty tuples needed for the other constraints
        m.pro_timevar_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Outputs of processes with time dependent efficiency')

    # process tuples for on/off
    if m.mode['onoff']:
        m.pro_on_off_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            initialize=[(stf, site, process)
                        for (stf, site, process) in
                                                  tuple(m.min_fraction_dict.keys())
                        for (st, sit, pro) in tuple(m.onoff_dict.keys())
                        if stf == st and site == sit and process == pro],
            doc='Processes with minimal fraction which can be turned off')
        m.pro_on_off_input_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, site, process, commodity)
                        for (stf, site, process) in m.pro_on_off_tuples
                        for (s, pro, commodity) in tuple(m.r_in_dict.keys())
                        if process == pro and stf == s],
            doc='Commodities for on/off input')

        m.pro_on_off_output_tuples = pyomo.Set(
                within=m.stf * m.sit * m.pro * m.com,
                initialize=[(stf, site, process, commodity)
                for (stf, site, process) in m.pro_on_off_tuples
                for (s, pro, commodity) in tuple(m.r_out_dict.keys())
                if process == pro and stf == s],
                doc='Commodities for on/off output')

        m.pro_partial_on_off_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            initialize=[(stf, site, process)
                        for (stf, site, process) in m.pro_tuples
                        for (st, pro, _) in tuple(m.r_in_min_fraction_dict.keys()
                                                  or m.r_out_min_fraction_dict)
                        if process == pro and stf == st and
                        m.process_dict['on-off'][stf, site, process] == 1],
            doc='Processes with partial input/output which can be turned off')
        m.pro_partial_on_off_input_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, site, process, commodity)
                        for (stf, site, process) in m.pro_partial_on_off_tuples
                        for (s, pro, commodity) in tuple(m.r_in_min_fraction_dict
                                                         .keys())
                        if process == pro and s == stf],
            doc='Commodities with partial input ratio which can be turned off,'
                'e.g. (2020,Mid,Coal PP,Coal)')
        m.pro_partial_on_off_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, site, process, commodity)
                        for (stf, site, process) in m.pro_partial_on_off_tuples
                        for (s, pro, commodity) in tuple(m.r_out_min_fraction_dict
                                                         .keys())
                        if process == pro and s == stf],
            doc='Commodities for on/off output with partial behaviour')

        m.pro_rampup_start_tuples = pyomo.Set(
            within=m.stf * m.sit *m.pro,
            initialize=[(stf, sit, pro)
                        for (stf, sit, pro) in m.pro_on_off_tuples
                        if m.process_dict['start-time'][stf, sit, pro]
                                                            > 1.0 / m.dt], #and
                            # m.process_dict['starting-ramp'][stf, sit, pro]
                            # < m.min_fraction_dict[stf, sit, pro]
                            # and
                            # m.process_dict['starting-ramp'][stf, sit, pro]
                            # < m.process_dict['ramp-up-grad'][stf, sit, pro]],
            doc='Processes with different starting ramp up gradient')

        m.pro_rampup_divides_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, sit, pro, com)
                        for (stf, sit, pro, com) in m.pro_on_off_output_tuples
                        if m.process_dict['ramp-up-grad'][stf, sit, pro] < 1.0 / m.dt and
                           m.process_dict['ramp-up-grad'][stf, sit, pro] <=
                           m.min_fraction_dict[stf, sit, pro] and
                           m.min_fraction_dict[stf, sit, pro] %
                           m.process_dict['ramp-up-grad'][stf, sit, pro] == 0 and
                           com not in m.com_env],
            doc='Output commodities of processes with ramp-up-grad smaller than'
                'timestep length and smaller equal than min-fraction and is a '
                'divisor of min-fraction')
    
        m.pro_rampup_not_divides_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, sit, pro, com)
                        for (stf, sit, pro, com) in m.pro_on_off_output_tuples
                        if m.process_dict['ramp-up-grad'][stf, sit, pro] < 1.0 / m.dt and
                           m.process_dict['ramp-up-grad'][stf, sit, pro] <
                           m.min_fraction_dict[stf, sit, pro] and
                           m.min_fraction_dict[stf, sit, pro] %
                           m.process_dict['ramp-up-grad'][stf, sit, pro] != 0 and
                           com not in m.com_env],
            doc='Output commodities of processes with ramp-up-grad smaller than'
                'timestep length and smaller than min-fraction and is NOT a '
                'divisor of min-fraction')
    
        m.pro_rampup_bigger_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, sit, pro, com)
                        for (stf, sit, pro, com) in m.pro_on_off_output_tuples
                        if m.process_dict['ramp-up-grad'][stf, sit, pro] < 1.0 / m.dt and
                           m.process_dict['ramp-up-grad'][stf, sit, pro] >
                           m.min_fraction_dict[stf, sit, pro] and
                           com not in m.com_env],
            doc='Output commodities of processes with ramp up gradient smaller'
                'than timestep length and greater than min-fraction')
    
        # processes with fix start-up costs
        m.pro_start_up_tuples = pyomo.Set(
                within=m.stf * m.sit * m.pro,
                initialize=[(stf, site, process)
                for (stf, site, process) in m.pro_on_off_tuples
                for (s, si, pro) in tuple(m.start_price_dict.keys())
                if process == pro and si == site and s == stf],
                doc='Processes with fixed start up costs')
    
        # Variables
    
        # process on/off
        m.on_off = pyomo.Var(
            m.t, m.pro_on_off_tuples,
            within=pyomo.Boolean,
            doc='Turn on/off a process with minimum working load')
    
        # number of start-ups
        m.start_up = pyomo.Var(
            m.tm, m.pro_start_up_tuples,
            within=pyomo.Boolean,
            doc='Number of start-ups')

    else:
        # empty tuples needed for the other constraints
        m.pro_on_off_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc='empty set needed for (partial) on/off processes')
        m.pro_on_off_input_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Commodities for on/off input')
        m.pro_on_off_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Commodities for on/off output')
        m.pro_partial_on_off_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc='Processes with partial input/output which can be turned off')
        m.pro_partial_on_off_input_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Commodities with partial input ratio,'
            'e.g. (2020,Mid,Coal PP,Coal)')
        m.pro_partial_on_off_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Commodities for on/off output with partial behaviour')
        m.pro_rampup_divides_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Output commodities of processes with ramp-up-grad smaller than'
                'timestep length and smaller equal than min-fraction and is a '
                'divisor of min-fraction')
        m.pro_rampup_not_divides_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Output commodities of processes with ramp-up-grad smaller than'
                'timestep length and smaller than min-fraction and is NOT a '
                'divisor of min-fraction')
        m.pro_rampup_bigger_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='Output commodities of processes with ramp up gradient smaller'
                'than timestep length and greater than min-fraction')
        m.pro_start_up_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc='Processes with fix start up costs')
        m.pro_rampup_start_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc='Processes with different starting ramp up gradient')

    # Processes with minimum working load which cannot be turned off
    if m.mode['minfraction']:
        m.pro_minfraction_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            initialize=[(stf, site, process)
                        for (stf, site, process) in m.pro_tuples
                        for (st, sit, pro) in tuple(m.min_fraction_dict.keys())
                        if  stf == st and sit == site and process ==pro and
                        m.process_dict['on-off'][stf, site, process] != 1],
            doc='Processes with constant efficiency and minimum working load which'
                'cannot be turned off')

        m.pro_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, site, process, commodity)
                        for (stf, site, process) in m.pro_minfraction_tuples
                        for (st, pro, commodity) in tuple(m.r_out_dict.keys())
                        if stf == st and process == pro],
            doc='Commodities with minimum working load and NO partial output ratio,'
                'e.g. (2020,Mid,Coal PP,Electricity)')
    
        # process tuples for partial feature
        m.pro_partial_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            initialize=[(stf, site, process)
                        for (stf, site, process) in m.pro_tuples
                        for (s, pro, _) in tuple(m.r_in_min_fraction_dict.keys() or
                                                 m.r_out_min_fraction_dict.keys())
                        if process == pro and s == stf and
                        m.process_dict['on-off'][stf, site, process] != 1],
            doc='Processes with partial input/output which cannot be turned off')

        m.pro_partial_input_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, site, process, commodity)
                        for (stf, site, process) in m.pro_partial_tuples
                        for (s, pro, commodity) in tuple(m.r_in_min_fraction_dict
                                                         .keys())
                        if process == pro and s == stf],
            doc='Commodities with partial input ratio,'
                'e.g. (2020,Mid,Coal PP,Coal)')
    
        m.pro_partial_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            initialize=[(stf, site, process, commodity)
                        for (stf, site, process) in m.pro_partial_tuples
                        for (s, pro, commodity) in tuple(m.r_out_min_fraction_dict
                                                         .keys())
                        if process == pro and s == stf],
            doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,CO2)')
    else:
        m.pro_minfraction_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc=' empty processes with constant efficiency and minimum working'
                ' load which cannot be turned off')
        m.pro_minfraction_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='empty commodities with minimum working load and NO partial'
                ' output ratio')
        m.pro_partial_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc=' empty processes with partial input/output which cannot be '
                ' turned off')
        m.pro_partial_input_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='empty commodities with partial input ratio')
        m.pro_partial_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='empty commodities with partial input ratio')

    
    # time variable efficiency rules
    m.def_process_timevar_output = pyomo.Constraint(
        m.tm, m.pro_timevar_output_tuples - m.pro_partial_output_tuples -
        m.pro_on_off_output_tuples,
        rule=def_pro_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')
    m.def_process_partial_timevar_output = pyomo.Constraint(
        m.tm, m.pro_partial_output_tuples & m.pro_timevar_output_tuples,
        rule=def_pro_partial_timevar_output_rule,
        doc='e_pro_out == tau_pro * r_out * on_off * eff_factor')
    m.def_process_on_off_timevar_output = pyomo.Constraint(
        m.tm, m.pro_timevar_output_tuples & m.pro_on_off_output_tuples -
              m.pro_partial_on_off_output_tuples,
        rule=def_process_on_off_timevar_output_rule,
        doc='e_pro_out == tau_pro * r_out * on_off * eff_factor')
    m.def_process_partial_on_off_timevar_output = pyomo.Constraint(
        m.tm, m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=def_pro_partial_on_off_timevar_output_rule,
        doc='e_pro_out == tau_pro * r_out * on_off * eff_factor')

    m.res_timevar_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples &
              m.pro_timevar_output_tuples - m.pro_partial_on_off_output_tuples,
        rule=res_timevar_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')
    m.res_timevar_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples &
              m.pro_timevar_output_tuples - m.pro_partial_on_off_output_tuples,
        rule=res_timevar_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')
    m.res_timevar_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples &
              m.pro_timevar_output_tuples - m.pro_partial_on_off_output_tuples,
        rule=res_timevar_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')
    m.res_partial_timevar_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=res_partial_timevar_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')
    m.res_partial_timevar_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=res_partial_timevar_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')
    m.res_partial_timevar_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=res_partial_timevar_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')


    # minfraction rules
    m.res_throughput_by_capacity_min = pyomo.Constraint(
        m.tm, m.pro_minfraction_tuples | m.pro_partial_tuples,
        rule=res_throughput_by_capacity_min_rule,
        doc='cap_pro * min-fraction <= tau_pro')

    m.def_partial_process_input = pyomo.Constraint(
        m.tm, m.pro_partial_input_tuples,
        rule=def_partial_process_input_rule,
        doc='e_pro_in = '
            ' cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction)')
    m.def_partial_process_output = pyomo.Constraint(
        m.tm, m.pro_partial_output_tuples - m.pro_timevar_output_tuples,
        rule=def_partial_process_output_rule,
        doc='e_pro_out = '
            ' cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction)')

    # on off rules
    # connection between on_off and tau_pro
    m.res_throughput_by_on_off_lower = pyomo.Constraint(
        m.tm, m.pro_on_off_tuples | m.pro_partial_on_off_tuples,
        rule=res_throughput_by_on_off_lower_rule,
        doc='tau_pro >= min-fraction * cap_pro * on_off')
    m.res_throughput_by_on_off_upper = pyomo.Constraint(
        m.tm, m.pro_on_off_tuples | m.pro_partial_on_off_tuples,
        rule=res_throughput_by_on_off_upper_rule,
        doc='tau_pro <='
            'cap_pro * on_off + min-fraction * cap_pro * (1 - on_off)')

    m.def_process_on_off_input = pyomo.Constraint(
        m.tm, m.pro_on_off_input_tuples - m.pro_partial_on_off_input_tuples,
        rule=def_process_on_off_input_rule,
        doc='e_pro_in ='
            ' tau_pro * r_in')
    m.def_process_on_off_output = pyomo.Constraint(
        m.tm, m.pro_on_off_output_tuples - m.pro_timevar_output_tuples -
              m.pro_partial_on_off_output_tuples,
        rule=def_process_on_off_output_rule,
        doc='e_pro_out = tau_pro * r_out * on_off')

    m.def_partial_process_on_off_input = pyomo.Constraint(
        m.tm, m.pro_partial_on_off_input_tuples,
        rule=def_partial_process_on_off_input_rule,
        doc='e_pro_in = '
            ' (cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction))')
    m.def_partial_process_on_off_output = pyomo.Constraint(
        m.tm, m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=def_partial_process_on_off_output_rule,
        doc='e_pro_out = on_off *'
            ' (cap_pro * min_fraction * (r - R) / (1 - min_fraction) '
            '+ tau_pro * (R - min_fraction * r) / (1 - min_fraction)) ')

    m.res_starting_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_start_tuples,
        rule=res_starting_rampup_rule,
        doc='throughput may not increase faster than maximal starting ramp up '
            'gradient until reaching minimum capacity')

    m.res_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples -
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')
    m.res_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples -
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')
    m.res_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples -
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')

    m.res_partial_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_partial_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')
    m.res_partial_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_partial_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')
    m.res_partial_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_partial_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')

    m.res_start_up = pyomo.Constraint(
        m.tm, m.pro_start_up_tuples,
        rule=res_start_up_rule,
        doc='start >= on_off(t) - on_off(t-1)')

    return m

# constraints

# process output == process throughput *
#                   input ratio at maximum operation point *
#                   efficiency factor


def def_pro_timevar_output_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_out[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m.r_out_dict[(stf, pro, com)] *
            m.eff_factor_dict[(sit, pro)][stf, tm])

def def_pro_partial_timevar_output_rule(m, tm, stf, sit, pro, com):
# input ratio at maximum operation point
    R = m.r_out_dict[stf, pro, com]
    # input ratio at lowest operation point
    r = m.r_out_min_fraction_dict[stf, pro, com]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)
    return (m.e_pro_out[tm, stf, sit, pro, com] ==
            (m.dt * m.cap_pro[stf, sit, pro] * online_factor +
             m.tau_pro[tm, stf, sit, pro] * throughput_factor) *
             m.eff_factor_dict[(sit, pro)][stf, tm])

def def_process_on_off_timevar_output_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_out[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m.r_out_dict[(stf, pro, com)] *
            m.on_off[tm, stf, sit, pro] *
            m.eff_factor_dict[(sit, pro)][stf, tm])

def def_pro_partial_on_off_timevar_output_rule(m, tm, stf, sit, pro, com):
    # input ratio at maximum operation point
    R = m.r_out_dict[stf, pro, com]
    # input ratio at lowest operation point
    r = m.r_out_min_fraction_dict[stf, pro, com]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)
    return (m.e_pro_out[tm, stf, sit, pro, com] ==
            (m.dt * m.cap_pro[stf, sit, pro] * online_factor +
             m.tau_pro[tm, stf, sit, pro] * throughput_factor) *
             m.on_off[tm, stf, sit, pro] *
             m.eff_factor_dict[(sit, pro)][stf, tm])

def res_process_on_off_timevar_output_lower_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_out[tm, stf, sit, pro, com] >=
            m.on_off[tm, stf, sit, pro] *
            m.process_dict['min-fraction'][stf, sit, pro] *
            m.r_out_dict[stf, pro, com] * m.dt *
            m.cap_pro[stf, sit, pro] *
            m.eff_factor_dict[(sit, pro)][stf, tm])

def res_partial_process_on_off_timevar_output_lower_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_out[tm, stf, sit, pro, com] >=
            m.on_off[tm, stf, sit, pro] *
            m.process_dict['min-fraction'][stf, sit, pro] *
            m.r_out_min_fraction_dict[stf, pro, com] * m.dt *
            m.cap_pro[stf, sit, pro] *
            m.eff_factor_dict[(sit, pro)][stf, tm])

def res_process_on_off_timevar_output_upper_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_out[tm, stf, sit, pro, com] <=
            m.on_off[tm, stf, sit, pro] *
            m.r_out_dict[stf, pro, com] * m.dt *
            m.cap_pro[stf, sit, pro] *
            m.eff_factor_dict[(sit, pro)][stf, tm])

def res_timevar_output_minfraction_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['min-fraction'][(stf, sit, pro)] *
                m.r_out_dict[(stf, pro, com)] *
                m.eff_factor_dict[(sit, pro)][stf, tm] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

def res_timevar_output_minfraction_rampup_rampup_rule(m, tm, stf, sit, pro, com):
    ramp_up = m.process_dict['ramp-up-grad'][(stf, sit, pro)]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    first_output_value = (math.floor(min_fraction / ramp_up) + 1) * ramp_up
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                first_output_value *
                m.r_out_dict[(stf, pro, com)] *
                m.eff_factor_dict[(sit, pro)][stf, tm] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

def res_timevar_output_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['ramp-up-grad'][(stf, sit, pro)] *
                m.r_out_dict[(stf, pro, com)] *
                m.eff_factor_dict[(sit, pro)][stf, tm] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

def res_partial_timevar_output_minfraction_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['min-fraction'][(stf, sit, pro)] *
                m.r_out_min_fraction_dict[(stf, pro, com)] *
                m.eff_factor_dict[(sit, pro)][stf, tm] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

def res_partial_timevar_output_minfraction_rampup_rampup_rule(m, tm, stf, sit, pro, com):
    ramp_up = m.process_dict['ramp-up-grad'][(stf, sit, pro)]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    first_output_value = (math.floor(min_fraction / ramp_up) + 1) * ramp_up
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                first_output_value *
                m.r_out_min_fraction_dict[(stf, pro, com)] *
                m.eff_factor_dict[(sit, pro)][stf, tm] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

def res_partial_timevar_output_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['ramp-up-grad'][(stf, sit, pro)] *
                m.r_out_min_fraction_dict[(stf, pro, com)] *
                m.eff_factor_dict[(sit, pro)][stf, tm] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

# minfraction
def res_throughput_by_capacity_min_rule(m, tm, stf, sit, pro):
    return (m.tau_pro[tm, stf, sit, pro] >=
            m.cap_pro[stf, sit, pro] *
            m.process_dict['min-fraction'][(stf, sit, pro)] * m.dt)

def def_partial_process_input_rule(m, tm, stf, sit, pro, com):
    # input ratio at maximum operation point
    R = m.r_in_dict[(stf, pro, com)]
    # input ratio at lowest operation point
    r = m.r_in_min_fraction_dict[stf, pro, com]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)
    return (m.e_pro_in[tm, stf, sit, pro, com] ==
            m.dt * m.cap_pro[stf, sit, pro] * online_factor +
            m.tau_pro[tm, stf, sit, pro] * throughput_factor)

def def_partial_process_output_rule(m, tm, stf, sit, pro, com):
    # input ratio at maximum operation point
    R = m.r_out_dict[stf, pro, com]
    # input ratio at lowest operation point
    r = m.r_out_min_fraction_dict[stf, pro, com]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)
    return (m.e_pro_out[tm, stf, sit, pro, com] ==
            m.dt * m.cap_pro[stf, sit, pro] * online_factor +
            m.tau_pro[tm, stf, sit, pro] * throughput_factor)


# on off
def res_throughput_by_on_off_lower_rule(m, tm, stf, sit, pro):
    return (m.tau_pro[tm, stf, sit, pro] >=
            m.min_fraction_dict[stf, sit, pro] * m.cap_pro[stf, sit, pro] *
            m.dt * m.on_off[tm, stf, sit, pro])
def res_throughput_by_on_off_upper_rule(m, tm, stf, sit, pro):
    return (m.tau_pro[tm, stf, sit, pro] <=
            m.cap_pro[stf, sit, pro] * m.dt * m.on_off[tm, stf, sit, pro] +
            m.min_fraction_dict[stf, sit, pro] * m.cap_pro[stf, sit, pro] *
            m.dt * (1 - m.on_off[tm, stf, sit, pro]))

def def_process_on_off_input_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_in[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m.r_in_dict[(stf, pro, com)])
def def_process_on_off_output_rule(m, tm, stf, sit, pro, com):
    r = m.r_out_dict[(stf, pro, com)]
    if com in m.com_env:
        return (m.e_pro_out[tm, stf, sit, pro, com] ==
                m.tau_pro[tm, stf, sit, pro] * r)
    else:
        return (m.e_pro_out[tm, stf, sit, pro, com] ==
                m.tau_pro[tm, stf, sit, pro] * r * m.on_off[tm, stf, sit, pro])

def def_partial_process_on_off_input_rule(m, tm, stf, sit, pro, com):
    # input ratio at maximum operation point
    R = m.r_in_dict[(stf, pro, com)]
    # input ratio at lowest operation point
    r = m.r_in_min_fraction_dict[stf, pro, com]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)
    return (m.e_pro_in[tm, stf, sit, pro, com] ==
            (m.dt * m.cap_pro[stf, sit, pro] * online_factor +
              m.tau_pro[tm, stf, sit, pro] * throughput_factor) *
              m.on_off[tm, stf, sit, pro] +
              m.tau_pro[tm, stf, sit, pro] * r *
              (1 - m.on_off[tm, stf, sit, pro]))
def def_partial_process_on_off_output_rule(m, tm, stf, sit, pro, com):
    # input ratio at maximum operation point
    R = m.r_out_dict[stf, pro, com]
    # input ratio at lowest operation point
    r = m.r_out_min_fraction_dict[stf, pro, com]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]
    on_off = m.on_off[tm, stf, sit, pro]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)
    if com in m.com_env:
        return(m.e_pro_out[tm, stf, sit, pro, com] ==
               (m.dt * m.cap_pro[stf, sit, pro] * online_factor +
               m.tau_pro[tm, stf, sit, pro] * throughput_factor) * on_off +
               m.tau_pro[tm, stf, sit, pro] * r *
               (1 - on_off))
    else:
        return (m.e_pro_out[tm, stf, sit, pro, com] ==
                (m.dt * m.cap_pro[stf, sit, pro] * online_factor +
                m.tau_pro[tm, stf, sit, pro] * throughput_factor) * on_off)

def res_process_on_off_output_lower_rule(m, tm, stf, sit, pro, com):
    if com in m.com_env:
        return pyomo.Constraint.Skip
    else:
        return (m.e_pro_out[tm, stf, sit, pro, com] >=
                m.on_off[tm, stf, sit, pro] *
                m.process_dict['min-fraction'][stf, sit, pro] *
                m.r_out_dict[stf, pro, com] * m.dt *
                m.cap_pro[stf, sit, pro])
def res_partial_process_on_off_output_lower_rule(m, tm, stf, sit, pro, com):
    if com in m.com_env:
        return pyomo.Constraint.Skip
    else:
        return (m.e_pro_out[tm, stf, sit, pro, com] >=
                m.on_off[tm, stf, sit, pro] *
                m.process_dict['min-fraction'][stf, sit, pro] *
                m.r_out_min_fraction_dict[stf, pro, com] * m.dt *
                m.cap_pro[stf, sit, pro])
def res_process_on_off_output_upper_rule(m, tm, stf, sit, pro, com):
    if com in m.com_env:
        return pyomo.Constraint.Skip
    else:
        return (m.e_pro_out[tm, stf, sit, pro, com] <=
                m.on_off[tm, stf, sit, pro] *
                m.r_out_dict[stf, pro, com] * m.dt *
                m.cap_pro[stf, sit, pro])

def res_starting_rampup_rule(m, t, stf, sit, pro):
    min_fraction = m.min_fraction_dict[stf, sit, pro]
    start_time = m.process_dict['start-time'][(stf, sit, pro)]
    starting_ramp =min_fraction / start_time
    return (m.tau_pro[t - 1, stf, sit, pro] +
            m.cap_pro[stf, sit, pro] *
            m.process_dict['ramp-up-grad'][(stf, sit, pro)] * m.dt *
            m.on_off[t - 1, stf, sit, pro] +
            m.cap_pro[stf, sit, pro] *
            starting_ramp * m.dt *
            (1 - m.on_off[t - 1, stf, sit, pro])
            >=
            m.tau_pro[t, stf, sit, pro])

def res_output_minfraction_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['min-fraction'][(stf, sit, pro)] *
                m.r_out_dict[(stf, pro, com)] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip
def res_output_minfraction_rampup_rampup_rule(m, tm, stf, sit, pro, com):
    ramp_up = m.process_dict['ramp-up-grad'][(stf, sit, pro)]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    first_output_value = (math.floor(min_fraction / ramp_up) + 1) * ramp_up
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                first_output_value *
                m.r_out_dict[(stf, pro, com)] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip
def res_output_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['ramp-up-grad'][(stf, sit, pro)] *
                m.r_out_dict[(stf, pro, com)] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

def res_partial_output_minfraction_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['min-fraction'][(stf, sit, pro)] *
                m.r_out_min_fraction_dict[(stf, pro, com)] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip
def res_partial_output_minfraction_rampup_rampup_rule(m, tm, stf, sit, pro, com):
    ramp_up = m.process_dict['ramp-up-grad'][(stf, sit, pro)]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    first_output_value = (math.floor(min_fraction / ramp_up) + 1) * ramp_up
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                first_output_value *
                m.r_out_min_fraction_dict[(stf, pro, com)] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip
def res_partial_output_rampup_rule(m, tm, stf, sit, pro, com):
    if tm != m.timesteps[1]:
        return (m.e_pro_out[tm - 1, stf, sit, pro, com] +
                m.cap_pro[stf, sit, pro] * m.dt *
                m.process_dict['ramp-up-grad'][(stf, sit, pro)] *
                m.r_out_min_fraction_dict[(stf, pro, com)] >=
                m.e_pro_out[tm, stf, sit, pro, com])
    else:
        return pyomo.Constraint.Skip

# start-ups
def res_start_up_rule(m, t, stf, sit, pro):
    return (m.start_up[t, stf, sit, pro] >= m.on_off[t, stf, sit, pro] -
                                             m.on_off[t - 1, stf, sit, pro])

# Start-up costs
def startup_cost(m, cost_type):
    """returns start-up cost function"""
    if cost_type == 'Start-up':
        return sum(m.start_up[(tm,) + p] * m.weight *
                   m.start_price_dict[p] * m.cap_pro[p] *
                   m.process_dict['cost_factor'][p]
                   for tm in m.tm
                   for p in m.pro_start_up_tuples)
