import math
import pyomo.core as pyomo

# storage (e.g. hydrogen, pump storage)
    
def create_storage_model()
    # Sets
    # ====
    # Syntax: m.{name} = Set({domain}, initialize={values})
    # where name: set name
    #       domain: set domain for tuple sets, a cartesian set product
    #       values: set values, a list or array of element tuples
    
    m.sto = pyomo.Set(
        initialize=m.storage.index.get_level_values('Storage').unique(),
        doc='Set of storage technologies')
    
    # Tuples
    m.sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com,
        initialize=m.storage.index,
        doc='Combinations of possible storage by site, e.g. (Mid,Bat,Elec)')
    m.sto_tuples_p_exp = pyomo.Set(
        within=m.sit*m.sto*m.com,
        initialize=m.storage_exp.index,
        doc='Combinations of possible storage by site with power expansion'
        ' e.g. (Mid,Bat,Elec)')   
    m.sto_tuples_c_exp = pyomo.Set(
        within=m.sit*m.sto*m.com,
        initialize=m.storage_const.index,
        doc='Combinations of possible storage by site with capacity expansion'
        ' e.g. (Mid,Bat,Elec)')    
        
    # Variables
    m.cap_sto_c = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage size (MWh)')
    m.cap_sto_c_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New storage size (MWh)')
    m.cap_sto_p = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage power (MW)')
    m.cap_sto_p_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New  storage power (MW)')
    m.e_sto_in = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into storage (MW) per timestep')
    m.e_sto_out = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of storage (MW) per timestep')
    m.e_sto_con = pyomo.Var(
        m.t, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Energy content of storage (MWh) in timestep')
   
    # constraints
    m.def_storage_state = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=def_storage_state_rule,
        doc='storage[t] = storage[t-1] * (1 - discharge) + input - output')
    m.def_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_power_rule,
        doc='storage power = inst-cap + new power')
    m.def_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_capacity_rule,
        doc='storage capacity = inst-cap + new capacity')
    m.res_storage_input_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_input_by_power_rule,
        doc='storage input <= storage power')
    m.res_storage_output_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_output_by_power_rule,
        doc='storage output <= storage power')
    m.res_storage_state_by_capacity = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_storage_state_by_capacity_rule,
        doc='storage content <= storage capacity')
    m.res_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_power_rule,
        doc='storage.cap-lo-p <= storage power <= storage.cap-up-p')
    m.res_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_capacity_rule,
        doc='storage.cap-lo-c <= storage capacity <= storage.cap-up-c')
    m.res_initial_and_final_storage_state = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_initial_and_final_storage_state_rule,
        doc='storage content initial == and final >= storage.init * capacity')
    
    return m
 
# Constraints

# storage content in timestep [t] == storage content[t-1] * (1-discharge)
# + newly stored energy * input efficiency
# - retrieved energy / output efficiency
def def_storage_state_rule(m, t, sit, sto, com):
    return (m.e_sto_con[t, sit, sto, com] ==
            m.e_sto_con[t-1, sit, sto, com] *
            (1 - m.storage_dict['discharge'][(sit, sto, com)]) +
            m.e_sto_in[t, sit, sto, com] *
            m.storage_dict['eff-in'][(sit, sto, com)] * m.dt -
            m.e_sto_out[t, sit, sto, com] /
            m.storage_dict['eff-out'][(sit, sto, com)] * m.dt)


# storage power == new storage power + existing storage power
def def_storage_power_rule(m, sit, sto, com):
    return (m.cap_sto_p[sit, sto, com] ==
            m.cap_sto_p_new[sit, sto, com] +
            m.storage_dict['inst-cap-p'][(sit, sto, com)])


# storage capacity == new storage capacity + existing storage capacity
def def_storage_capacity_rule(m, sit, sto, com):
    return (m.cap_sto_c[sit, sto, com] ==
            m.cap_sto_c_new[sit, sto, com] +
            m.storage_dict['inst-cap-c'][(sit, sto, com)])


# storage input <= storage power
def res_storage_input_by_power_rule(m, t, sit, sto, com):
    return m.e_sto_in[t, sit, sto, com] <= m.cap_sto_p[sit, sto, com]
def res_storage_input_by_power_rule_const_p(m, t, sit, sto, com):
    return m.e_sto_in[t, sit, sto, com] <= m.storage_dict['inst-cap-p'][(sit, sto, com)]

# storage output <= storage power
def res_storage_output_by_power_rule(m, t, sit, sto, com):
    return m.e_sto_out[t, sit, sto, com] <= m.cap_sto_p[sit, sto, com]
def res_storage_output_by_power_rule_const_p(m, t, sit, sto, com):
    return m.e_sto_out[t, sit, sto, com] <= m.storage_dict['inst-cap-p'][(sit, sto, com)]

# storage content <= storage capacity
def res_storage_state_by_capacity_rule(m, t, sit, sto, com):
    return m.e_sto_con[t, sit, sto, com] <= m.cap_sto_c[sit, sto, com]
def res_storage_state_by_capacity_rule_const_c(m, t, sit, sto, com):
    return m.e_sto_con[t, sit, sto, com] <= m.storage_dict['inst-cap-c'][(sit, sto, com)]

# lower bound <= storage power <= upper bound
def res_storage_power_rule(m, sit, sto, com):
    return (m.storage_dict['cap-lo-p'][(sit, sto, com)],
            m.cap_sto_p[sit, sto, com],
            m.storage_dict['cap-up-p'][(sit, sto, com)])


# lower bound <= storage capacity <= upper bound
def res_storage_capacity_rule(m, sit, sto, com):
    return (m.storage_dict['cap-lo-c'][(sit, sto, com)],
            m.cap_sto_c[sit, sto, com],
            m.storage_dict['cap-up-c'][(sit, sto, com)])


# initialization of storage content in first timestep t[1]
# forced minimun  storage content in final timestep t[len(m.t)]
# content[t=1] == storage capacity * fraction <= content[t=final]
def res_initial_and_final_storage_state_rule(m, t, sit, sto, com):
    if t == m.t[1]:  # first timestep (Pyomo uses 1-based indexing)
        return (m.e_sto_con[t, sit, sto, com] ==
                m.cap_sto_c[sit, sto, com] *
                m.storage_dict['init'][(sit, sto, com)])
    elif t == m.t[len(m.t)]:  # last timestep
        return (m.e_sto_con[t, sit, sto, com] >=
                m.cap_sto_c[sit, sto, com] *
                m.storage_dict['init'][(sit, sto, com)])
    else:
        return pyomo.Constraint.Skip
def res_initial_and_final_storage_state_rule_const_c(m, t, sit, sto, com):
    if t == m.t[1]:  # first timestep (Pyomo uses 1-based indexing)
        return (m.e_sto_con[t, sit, sto, com] ==
                m.storage_dict['cap-up-c'][(sit, sto, com)] *
                m.storage_dict['init'][(sit, sto, com)])
    elif t == m.t[len(m.t)]:  # last timestep
        return (m.e_sto_con[t, sit, sto, com] >=
                m.storage_dict['cap-up-c'][(sit, sto, com)] *
                m.storage_dict['init'][(sit, sto, com)])
    else:
        return pyomo.Constraint.Skip
