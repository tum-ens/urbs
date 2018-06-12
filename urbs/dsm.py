

 
    # demand side management
    m.dsm_up = pyomo.Var(
        m.tm, m.dsm_site_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM upshift')
    m.dsm_down = pyomo.Var(
        m.dsm_down_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM downshift')

    # modelled Demand Side Management time steps (downshift):
    # downshift effective in tt to compensate for upshift in t
    m.tt = pyomo.Set(
        within=m.t,
        initialize=m.timesteps[1:],
        ordered=True,
        doc='Set of additional DSM time steps')


    # demand side management
    m.def_dsm_variables = pyomo.Constraint(
        m.tm, m.dsm_site_tuples,
        rule=def_dsm_variables_rule,
        doc='DSMup * efficiency factor n == DSMdo')

    m.res_dsm_upward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples,
        rule=res_dsm_upward_rule,
        doc='DSMup <= Cup (threshold capacity of DSMup)')

    m.res_dsm_downward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples,
        rule=res_dsm_downward_rule,
        doc='DSMdo <= Cdo (threshold capacity of DSMdo)')

    m.res_dsm_maximum = pyomo.Constraint(
        m.tm, m.dsm_site_tuples,
        rule=res_dsm_maximum_rule,
        doc='DSMup + DSMdo <= max(Cup,Cdo)')

    m.res_dsm_recovery = pyomo.Constraint(
        m.tm, m.dsm_site_tuples,
        rule=res_dsm_recovery_rule,
        doc='DSMup(t, t + recovery time R) <= Cup * delay time L')

    m.res_global_co2_limit = pyomo.Constraint(
        m.stf,
        rule=res_global_co2_limit_rule,
        doc='total co2 commodity output <= global.prop CO2 limit')

# demand side management (DSM) constraints


# DSMup == DSMdo * efficiency factor n
def def_dsm_variables_rule(m, tm, sit, com):
    dsm_down_sum = 0
    for tt in dsm_time_tuples(tm,
                              m.timesteps[1:],
                              m.dsm_dict['delay'][(sit, com)]):
        dsm_down_sum += m.dsm_down[tm, tt, sit, com]
    return dsm_down_sum == (m.dsm_up[tm, sit, com] *
                            m.dsm_dict['eff'][(sit, com)])


# DSMup <= Cup (threshold capacity of DSMup)
def res_dsm_upward_rule(m, tm, sit, com):
    return m.dsm_up[tm, sit, com] <= int(m.dsm_dict['cap-max-up'][(sit, com)])


# DSMdo <= Cdo (threshold capacity of DSMdo)
def res_dsm_downward_rule(m, tm, sit, com):
    dsm_down_sum = 0
    for t in dsm_time_tuples(tm,
                             m.timesteps[1:],
                             m.dsm_dict['delay'][(sit, com)]):
        dsm_down_sum += m.dsm_down[t, tm, sit, com]
    return dsm_down_sum <= m.dsm_dict['cap-max-do'][(sit, com)]


# DSMup + DSMdo <= max(Cup,Cdo)
def res_dsm_maximum_rule(m, tm, sit, com):
    dsm_down_sum = 0
    for t in dsm_time_tuples(tm,
                             m.timesteps[1:],
                             m.dsm_dict['delay'][(sit, com)]):
        dsm_down_sum += m.dsm_down[t, tm, sit, com]

    max_dsm_limit = max(m.dsm_dict['cap-max-up'][(sit, com)],
                        m.dsm_dict['cap-max-do'][(sit, com)])
    return m.dsm_up[tm, sit, com] + dsm_down_sum <= max_dsm_limit


# DSMup(t, t + recovery time R) <= Cup * delay time L
def res_dsm_recovery_rule(m, tm, sit, com):
    dsm_up_sum = 0
    for t in dsm_recovery(tm,
                          m.timesteps[1:],
                          m.dsm_dict['recov'][(sit, com)]):
        dsm_up_sum += m.dsm_up[t, sit, com]
    return dsm_up_sum <= (m.dsm_dict['cap-max-up'][(sit, com)] *
                          m.dsm_dict['delay'][(sit, com)])