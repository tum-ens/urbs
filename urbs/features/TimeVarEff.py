import math
import pyomo.core as pyomo

def add_time_variable_efficiency(m):

    # process tuples for time variable efficiency
    tve_stflist = set()
    # get all support timeframes for which time variable efficiency is enabled
    for key in m.eff_factor_dict[tuple(m.eff_factor_dict.keys())[0]]:
        tve_stflist.add(tuple(key)[0])
    m.pro_timevar_output_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for stf in tve_stflist
                    for (site, process) in tuple(m.eff_factor_dict.keys())
                    for (st, pro, commodity) in tuple(m.r_out_dict.keys())
                    if process == pro and st == stf and commodity not in
                    m.com_env],
    doc='Outputs of processes with time dependent efficiency')

    # time variable efficiency rules
    m.def_process_timevar_output = pyomo.Constraint(
        m.tm, (m.pro_timevar_output_tuples -
               (m.pro_partial_output_tuples & m.pro_timevar_output_tuples)),
        rule=def_pro_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')
    m.def_process_partial_timevar_output = pyomo.Constraint(
        m.tm, m.pro_partial_output_tuples & m.pro_timevar_output_tuples,
        rule=def_pro_partial_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')

    return m

# constraints

# process output == process throughput *
#                   input ratio at maximum operation point *
#                   efficiency factor                
def def_pro_timevar_output_rule(m, tm, stf, sit, pro, com):
    return(m.e_pro_out[tm, stf, sit, pro, com] ==
           m.tau_pro[tm, stf, sit, pro] * m.r_out_dict[(stf, pro, com)] *
           m.eff_factor_dict[(sit, pro)][stf, tm])


def def_pro_partial_timevar_output_rule(m, tm, stf, sit, pro, coo):
    # input ratio at maximum operation point
    R = m.r_out_dict[stf, pro, coo]
    # input ratio at lowest operation point
    r = m.r_out_min_fraction_dict[stf, pro, coo]
    min_fraction = m.process_dict['min-fraction'][(stf, sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)
    return (m.e_pro_out[tm, stf, sit, pro, coo] ==
            (m.dt * m.cap_pro[stf, sit, pro] * online_factor +
             m.tau_pro[tm, stf, sit, pro] * throughput_factor) *
            m.eff_factor_dict[(sit, pro)][(stf, tm)])