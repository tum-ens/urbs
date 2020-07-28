import math
import pyomo.core as pyomo

def add_typeday(m):

    # Validation:
    if not (len(m.timesteps) % 24 == 0 or len(m.timesteps) % 24 == 1):
        print('Warning: length of timesteps does not end at the end of a day!')

    # change weight parameter to 1, since the whole year is representated by weight_typeday
    m.del_component(m.weight)
    m.weight = pyomo.Param(
        initialize=1,
        doc='Pre-factor for variable costs and emissions for annual result for type days = 1')

    m.t_endofday = pyomo.Set(
        within=m.t,
        initialize=[i * 24 * m.dt for i in list(range(1,1+int(len(m.timesteps) / m.dt / 24)))],
        ordered=True,
        doc='timestep at the end of each day')

    m.res_storage_state_cyclicity_typeday = pyomo.Constraint(
        m.t_endofday, m.sto_tuples,
        rule=res_storage_state_cyclicity_typeday_rule,
        doc='storage content initial == storage content at the end of each day')

    return m

def res_storage_state_cyclicity_typeday_rule(m, t, stf, sit, sto, com):
    return (m.e_sto_con[m.t[1], stf, sit, sto, com] ==
            m.e_sto_con[t, stf, sit, sto, com])
