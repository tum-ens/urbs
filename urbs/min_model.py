import math
import pyomo.core as pyomo
from .modelhelper import*
from .objective import*

def create_min_model_sets(m):
    # generate ordered time step sets
    m.t = pyomo.Set(
        initialize=m.timesteps,
        ordered=True,
        doc='Set of timesteps')
    # modelled (i.e. excluding init time step for storage) time steps
    m.tm = pyomo.Set(
        within=m.t,
        initialize=m.timesteps[1:],
        ordered=True,
        doc='Set of modelled timesteps within each stf')
    # site (e.g. north, middle, south...)
    m.sit = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Site').unique(),
        doc='Set of sites')
    # commodity (e.g. solar, wind, coal...)
    m.com = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Commodity').unique(),
        doc='Set of commodities')
    # commodity type (i.e. SupIm, Demand, Stock, Env)
    m.com_type = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Type').unique(),
        doc='Set of commodity types')
    # process (e.g. Wind turbine, Gas plant, Photovoltaics...)
        # process (e.g. Wind turbine, Gas plant, Photovoltaics...)
    m.pro = pyomo.Set(
        initialize=m.process.index.get_level_values('Process').unique(),
        doc='Set of conversion processes')   
    # cost_type
    m.cost_type = pyomo.Set(
        initialize=['Invest', 'Fixed', 'Variable', 'Fuel', 'Revenue',
                    'Purchase', 'Environmental'],
        doc='Set of cost types (hard-coded)')
    
    return m

def create_min_model_tuples(m,dt=1):
    m.com_tuples = pyomo.Set(
        within=m.sit*m.com*m.com_type,
        initialize=m.commodity.index,
        doc='Combinations of defined commodities, e.g. (Mid,Elec,Demand)')
    # commodity type subsets
    m.com_supim = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'SupIm'),
        doc='Commodities that have intermittent (timeseries) input')
    m.com_stock = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Stock'),
        doc='Commodities that can be purchased at some site(s)')
    m.com_sell = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Sell'),
        doc='Commodities that can be sold')
    m.com_buy = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Buy'),
        doc='Commodities that can be purchased')
    m.com_demand = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Demand'),
        doc='Commodities that have a demand (implies timeseries)')
    m.com_env = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Env'),
        doc='Commodities that (might) have a maximum creation limit')
    #process tuples    
    m.pro_tuples = pyomo.Set(
        within=m.sit*m.pro,
        initialize=m.process.index,
        doc='Combinations of possible processes, e.g. (North,Coal plant)')
    # process expansion tuples
    if not m.process_exp.empty:
        m.pro_tuples_exp = pyomo.Set(
            within=m.sit*m.pro,
            initialize=m.process_exp.index,
            doc='Combinations of possible processes with expansion, e.g. (North,Coal plant)')  
    # process tuples for area rule
    if not m.proc_area_exp.empty:
        m.pro_area_tuples_exp = pyomo.Set(
            within=m.sit*m.pro,
            initialize=m.proc_area_exp.index,
            doc='Processes and Sites with area Restriction')
    if not m.proc_area_const.empty:
        m.pro_area_tuples_const = pyomo.Set(
            within=m.sit*m.pro,
            initialize=m.proc_area_const.index,
            doc='Processes and Sites with area Restriction')
    # process input/output
    m.pro_input_tuples = pyomo.Set(
        within=m.sit*m.pro*m.com,
        initialize=[(site, process, commodity)
                    for (site, process) in m.pro_tuples
                    for (pro, commodity) in m.r_in.index
                    if process == pro],
        doc='Commodities consumed by process by site, e.g. (Mid,PV,Solar)')
    m.pro_output_tuples = pyomo.Set(
        within=m.sit*m.pro*m.com,
        initialize=[(site, process, commodity)
                    for (site, process) in m.pro_tuples
                    for (pro, commodity) in m.r_out.index
                    if process == pro],
        doc='Commodities produced by process by site, e.g. (Mid,PV,Elec)')
    # process tuples for maximum gradient feature
    m.pro_maxgrad_tuples = pyomo.Set(
        within=m.sit*m.pro,
        initialize=[(sit, pro)
                    for (sit, pro) in m.pro_tuples
                    if m.process.loc[sit, pro]['max-grad'] < 1.0 / dt],
        doc='Processes with maximum gradient smaller than timestep length')
    # process tuples for partial feature
    m.pro_partial_tuples = pyomo.Set(
        within=m.sit*m.pro,
        initialize=[(site, process)
                    for (site, process) in m.pro_tuples
                    for (pro, _) in m.r_in_min_fraction.index
                    if process == pro],
        doc='Processes with partial input')
    m.pro_partial_input_tuples = pyomo.Set(
        within=m.sit*m.pro*m.com,
        initialize=[(site, process, commodity)
                    for (site, process) in m.pro_partial_tuples
                    for (pro, commodity) in m.r_in_min_fraction.index
                    if process == pro],
        doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,Coal)')
    m.pro_partial_output_tuples = pyomo.Set(
        within=m.sit*m.pro*m.com,
        initialize=[(site, process, commodity)
                        for (site, process) in m.pro_partial_tuples
                        for (pro, commodity) in m.r_out_min_fraction.index
                        if process == pro],
        doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,CO2)')
    
    return m
    
def create_params(m,dt=1):
    # Parameters

    # weight = length of year (hours) / length of simulation (hours)
    # weight scales costs and emissions from length of simulation to a full
    # year, making comparisons among cost types (invest is annualized, fixed
    # costs are annual by default, variable costs are scaled by weight) and
    # among different simulation durations meaningful.
    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.tm) * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')

    # dt = spacing between timesteps. Required for storage equation that
    # converts between energy (storage content, e_sto_con) and power (all other
    # quantities that start with "e_")
    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')
        
    return m
    
def create_min_model_vars(m):

    # costs
    m.costs = pyomo.Var(
        m.cost_type,
        within=pyomo.Reals,
        doc='Costs by type (EUR/a)')

    # commodity
    m.e_co_stock = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of stock commodity source (MW) per timestep')
    m.e_co_sell = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of sell commodity source (MW) per timestep')
    m.e_co_buy = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of buy commodity source (MW) per timestep')

    # process																
    m.cap_pro = pyomo.Var(
        m.pro_tuples_exp,
        within=pyomo.NonNegativeReals,
        doc='Total process capacity (MW)')         
    m.cap_pro_new = pyomo.Var(
        m.pro_tuples_exp,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')
    m.tau_pro = pyomo.Var(
        m.t, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow (MW) through process')
    m.e_pro_in = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Power flow of commodity into process (MW) per timestep')
    m.e_pro_out = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of process (MW) per timestep')
        
    return m

def declare_min_model_equations(m):
    """ Equation declarations
    equation bodies are defined in separate functions, referred to here by
    their name in the "rule" keyword."""

    # commodity
    m.res_vertex = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_vertex_rule,
        doc='storage + transmission + process + source + buy - sell == demand')
    m.res_stock_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_stock_step_rule,
        doc='stock commodity input per step <= commodity.maxperstep')
    m.res_stock_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_stock_total_rule,
        doc='total stock commodity input <= commodity.max')
    m.res_sell_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_sell_step_rule,
        doc='sell commodity output per step <= commodity.maxperstep')
    m.res_sell_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_sell_total_rule,
        doc='total sell commodity output <= commodity.max')
    m.res_buy_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_buy_step_rule,
        doc='buy commodity output per step <= commodity.maxperstep')
    m.res_buy_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_buy_total_rule,
        doc='total buy commodity output <= commodity.max')
    m.res_env_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_env_step_rule,
        doc='environmental output per step <= commodity.maxperstep')
    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

    # process		
    m.def_process_capacity = pyomo.Constraint(                            
        m.pro_tuples_exp,
        rule=def_process_capacity_rule,
        doc='total process capacity = inst-cap + new capacity')
    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples - m.pro_partial_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')
    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples - m.pro_partial_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio') 
    m.def_intermittent_supply = pyomo.Constraint(                           
        m.tm, m.pro_input_tuples-m.pro_input_tuples_const_cap,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')       
    m.res_process_throughput_by_capacity = pyomo.Constraint(                
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')       
    m.res_process_maxgrad_lower = pyomo.Constraint(                                     
        m.tm, m.pro_maxgrad_tuples,
        rule=res_process_maxgrad_lower_rule,
        doc='throughput may not decrease faster than maximal gradient')
    m.res_process_maxgrad_upper = pyomo.Constraint(                                     
        m.tm, m.pro_maxgrad_tuples,
        rule=res_process_maxgrad_upper_rule,
        doc='throughput may not increase faster than maximal gradient')        
    m.res_process_capacity = pyomo.Constraint(                                           
        m.pro_tuples_exp,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')        
    m.res_throughput_by_capacity_min = pyomo.Constraint(                                
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_capacity_min_rule,
        doc='cap_pro * min-fraction <= tau_pro')        
    m.def_partial_process_input = pyomo.Constraint(                                     
        m.tm, m.pro_partial_input_tuples,
        rule=def_partial_process_input_rule,
        doc='e_pro_in = '
            ' cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction)')           
    m.def_partial_process_output = pyomo.Constraint(                                             
        m.tm, m.pro_partial_output_tuples,
        rule=def_partial_process_output_rule,
        doc='e_pro_out = '
            ' cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction)')
    m.res_area = pyomo.Constraint(
        m.sit,
        rule=res_area_rule,
        doc='used process area <= total process area')
    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='power connection capacity must be symmetric in both directions')
    m.res_global_co2_limit = pyomo.Constraint(
            rule=res_global_co2_limit_rule,
            doc='total co2 commodity output <= Global CO2 limit')
    # costs
    m.def_costs = pyomo.Constraint(
        m.cost_type,
        rule=def_costs_rule,
        doc='main cost function by cost type')
    m.obj = pyomo.Objective(
        rule=obj_rule,
        sense=pyomo.minimize,
        doc='minimize(cost = sum of all cost types)')    

    return m


# commodity

# vertex equation: calculate balance for given commodity and site;
# contains implicit constraints for process activity, import/export and
# storage activity (calculated by function commodity_balance);
# contains implicit constraint for stock commodity source term
def res_vertex_rule(m, tm, sit, com, com_type):
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
    power_surplus = - commodity_balance(m, tm, sit, com)

    # if com is a stock commodity, the commodity source term e_co_stock
    # can supply a possibly negative power_surplus
    if com in m.com_stock:
        power_surplus += m.e_co_stock[tm, sit, com, com_type]

    # if com is a sell commodity, the commodity source term e_co_sell
    # can supply a possibly positive power_surplus
    if com in m.com_sell:
        power_surplus -= m.e_co_sell[tm, sit, com, com_type]

    # if com is a buy commodity, the commodity source term e_co_buy
    # can supply a possibly negative power_surplus
    if com in m.com_buy:
        power_surplus += m.e_co_buy[tm, sit, com, com_type]

    # if com is a demand commodity, the power_surplus is reduced by the
    # demand value; no scaling by m.dt or m.weight is needed here, as this
    # constraint is about power (MW), not energy (MWh)
    if com in m.com_demand:
        try:
            power_surplus -= m.demand_dict[(sit, com)][tm]
        except KeyError:
            pass
    # if sit com is a dsm tuple, the power surplus is decreased by the
    # upshifted demand and increased by the downshifted demand.
    if (sit, com) in m.dsm_site_tuples:
        power_surplus -= m.dsm_up[tm, sit, com]
        power_surplus += sum(m.dsm_down[t, tm, sit, com]
                             for t in dsm_time_tuples(
                                 tm, m.timesteps[1:],
                                 m.dsm_dict['delay'][(sit, com)]))
    return power_surplus == 0

# stock commodity purchase == commodity consumption, according to
# commodity_balance of current (time step, site, commodity);
# limit stock commodity use per time step
def res_stock_step_rule(m, tm, sit, com, com_type):
    if com not in m.com_stock:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_stock[tm, sit, com, com_type] <=
                m.commodity_dict['maxperstep'][(sit, com, com_type)])


# limit stock commodity use in total (scaled to annual consumption, thanks
# to m.weight)
def res_stock_total_rule(m, sit, com, com_type):
    if com not in m.com_stock:
        return pyomo.Constraint.Skip
    else:
        # calculate total consumption of commodity com
        total_consumption = 0
        for tm in m.tm:
            total_consumption += (
                m.e_co_stock[tm, sit, com, com_type] * m.dt)
        total_consumption *= m.weight
        return (total_consumption <=
                m.commodity_dict['max'][(sit, com, com_type)])


# limit sell commodity use per time step
def res_sell_step_rule(m, tm, sit, com, com_type):
    if com not in m.com_sell:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_sell[tm, sit, com, com_type] <=
                m.commodity_dict['maxperstep'][(sit, com, com_type)])


# limit sell commodity use in total (scaled to annual consumption, thanks
# to m.weight)
def res_sell_total_rule(m, sit, com, com_type):
    if com not in m.com_sell:
        return pyomo.Constraint.Skip
    else:
        # calculate total sale of commodity com
        total_consumption = 0
        for tm in m.tm:
            total_consumption += (
                m.e_co_sell[tm, sit, com, com_type] * m.dt)
        total_consumption *= m.weight
        return (total_consumption <=
                m.commodity_dict['max'][(sit, com, com_type)])


# limit buy commodity use per time step
def res_buy_step_rule(m, tm, sit, com, com_type):
    if com not in m.com_buy:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_buy[tm, sit, com, com_type] <=
                m.commodity_dict['maxperstep'][(sit, com, com_type)])


# limit buy commodity use in total (scaled to annual consumption, thanks
# to m.weight)
def res_buy_total_rule(m, sit, com, com_type):
    if com not in m.com_buy:
        return pyomo.Constraint.Skip
    else:
        # calculate total sale of commodity com
        total_consumption = 0
        for tm in m.tm:
            total_consumption += (
                m.e_co_buy[tm, sit, com, com_type] * m.dt)
        total_consumption *= m.weight
        return (total_consumption <=
                m.commodity_dict['max'][(sit, com, com_type)])


# environmental commodity creation == - commodity_balance of that commodity
# used for modelling emissions (e.g. CO2) or other end-of-pipe results of
# any process activity;
# limit environmental commodity output per time step
def res_env_step_rule(m, tm, sit, com, com_type):
    if com not in m.com_env:
        return pyomo.Constraint.Skip
    else:
        environmental_output = - commodity_balance(m, tm, sit, com)
        return (environmental_output <=
                m.commodity_dict['maxperstep'][(sit, com, com_type)])


# limit environmental commodity output in total (scaled to annual
# emissions, thanks to m.weight)
def res_env_total_rule(m, sit, com, com_type):
    if com not in m.com_env:
        return pyomo.Constraint.Skip
    else:
        # calculate total creation of environmental commodity com
        env_output_sum = 0
        for tm in m.tm:
            env_output_sum += (- commodity_balance(m, tm, sit, com) * m.dt)
        env_output_sum *= m.weight
        return (env_output_sum <=
                m.commodity_dict['max'][(sit, com, com_type)])

                
# process

# process capacity == new capacity + existing capacity
def def_process_capacity_rule(m, sit, pro):
    return (m.cap_pro[sit, pro] ==
                m.cap_pro_new[sit, pro] +
                m.process_dict['inst-cap'][(sit, pro)])
    
# process input power == process throughput * input ratio
def def_process_input_rule(m, tm, sit, pro, co):
    return (m.e_pro_in[tm, sit, pro, co] ==
            m.tau_pro[tm, sit, pro] * m.r_in_dict[(pro, co)])


# process output power = process throughput * output ratio
def def_process_output_rule(m, tm, sit, pro, co):
    return (m.e_pro_out[tm, sit, pro, co] ==
            m.tau_pro[tm, sit, pro] * m.r_out_dict[(pro, co)])


# process input (for supim commodity) = process capacity * timeseries
def def_intermittent_supply_rule(m, tm, sit, pro, coin):                                 
    if coin in m.com_supim:
        if (sit,pro) in m.pro_tuples_exp:
            return (m.e_pro_in[tm, sit, pro, coin] ==
                    m.cap_pro[sit, pro] * m.supim_dict[(sit, coin)][tm])
        else:
            return (m.e_pro_in[tm, sit, pro, coin] ==
                    m.process_dict['inst-cap'][(sit, pro)] * m.supim_dict[(sit, coin)][tm])
    else:
        return pyomo.Constraint.Skip


# process throughput <= process capacity                                    
def res_process_throughput_by_capacity_rule(m, tm, sit, pro):
    if (sit,pro) in m.pro_tuples_exp:               
        return (m.tau_pro[tm, sit, pro] <= m.cap_pro[sit, pro])
    else:
        return (m.tau_pro[tm, sit, pro] <= m.process_dict['inst-cap'][(sit, pro)])   


def res_process_maxgrad_lower_rule(m, t, sit, pro): 
    if (sit,pro) in m.pro_tuples_exp:
        return (m.tau_pro[t-1, sit, pro] -
                m.cap_pro[sit, pro] * m.process_dict['max-grad'][(sit, pro)] *
                m.dt <= m.tau_pro[t, sit, pro])
    else:
        return (m.tau_pro[t-1, sit, pro] -
                m.process_dict['inst-cap'][(sit, pro)] * 
                m.process_dict['max-grad'][(sit, pro)] *
                m.dt <= m.tau_pro[t, sit, pro])        

            
def res_process_maxgrad_upper_rule(m, t, sit, pro):                            
    if (sit,pro) in m.pro_tuples_exp:
        return (m.tau_pro[t-1, sit, pro] +
                m.cap_pro[sit, pro] * m.process_dict['max-grad'][(sit, pro)] *
                m.dt >= m.tau_pro[t, sit, pro])
    else:
        return (m.tau_pro[t-1, sit, pro] +
                m.process_dict['inst-cap'][(sit, pro)] * 
                m.process_dict['max-grad'][(sit, pro)] *
                m.dt >= m.tau_pro[t, sit, pro])
                        
        
# lower bound <= process capacity <= upper bound                          
def res_process_capacity_rule(m, sit, pro):
    return (m.process_dict['cap-lo'][sit, pro],
            m.cap_pro[sit, pro],
            m.process_dict['cap-up'][sit, pro])

def res_throughput_by_capacity_min_rule(m, tm, sit, pro):
    if (sit,pro) in m.pro_tuples_exp:
        return (m.tau_pro[tm, sit, pro] >=
                m.cap_pro[sit, pro] *
                m.process_dict['min-fraction'][(sit, pro)])
    else:
        return (m.tau_pro[tm, sit, pro] >=
                m.process_dict['inst-cap'][(sit, pro)] * 
                m.process_dict['min-fraction'][(sit, pro)])        

def def_partial_process_input_rule(m, tm, sit, pro, coin):   
    R = m.r_in_dict[(pro, coin)]  # input ratio at maximum operation point
    r = m.r_in_min_fraction[pro, coin]  # input ratio at lowest
    # operation point
    min_fraction = m.process_dict['min-fraction'][(sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)

    if (sit,pro) in m.pro_tuples_exp:
        return (m.e_pro_in[tm, sit, pro, coin] ==
                m.cap_pro[sit, pro] * online_factor +
                m.tau_pro[tm, sit, pro] * throughput_factor)
    else:
        return (m.e_pro_in[tm, sit, pro, coin] ==
                m.process_dict['inst-cap'][(sit, pro)] * online_factor +
                m.tau_pro[tm, sit, pro] * throughput_factor)                

def def_partial_process_output_rule(m, tm, sit, pro, coo):                     
    R = m.r_out.loc[pro, coo]  # input ratio at maximum operation point
    r = m.r_out_min_fraction[pro, coo]  # input ratio at lowest operation point
    min_fraction = m.process_dict['min-fraction'][(sit, pro)]

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)

    if (sit,pro) in m.pro_tuples_exp:    
        return (m.e_pro_out[tm, sit, pro, coo] ==
                m.cap_pro[sit, pro] * online_factor +
                m.tau_pro[tm, sit, pro] * throughput_factor)
    else:
        return (m.e_pro_out[tm, sit, pro, coo] ==
                m.process_dict['inst-cap'][(sit, pro)] * online_factor +
                m.tau_pro[tm, sit, pro] * throughput_factor)


# used process area <= maximal process area
def res_area_rule(m, sit):                                                     
    if m.site.loc[sit]['area'] >= 0 and sum(
                         m.process.loc[(s, p), 'area-per-cap']
                         for (s, p) in m.pro_area_tuples_exp
                         if s == sit) +\
                         sum(m.process.loc[(s, p), 'area-per-cap']
                         for (s, p) in m.pro_area_tuples_const
                         if s == sit) > 0:
        total_area = sum(m.cap_pro[s, p] *
                        m.process.loc[(s, p), 'area-per-cap']
                        for (s, p) in m.pro_area_tuples_exp
                        if s == sit) + \
                     sum(m.process_dict['inst-cap'][(s, p)] *
                        m.process.loc[(s, p), 'area-per-cap']
                        for (s, p) in m.pro_area_tuples_const
                        if s == sit)
        return total_area <= m.site.loc[sit]['area']
    else:
        # Skip constraint, if area is not numeric
        return pyomo.Constraint.Skip


# power connection capacity: Sell == Buy
def res_sell_buy_symmetry_rule(m, sit_in, pro_in, coin):                    
    # constraint only for sell and buy processes
    # and the processes must be in the same site
    if coin in m.com_buy:
        sell_pro = search_sell_buy_tuple(m, sit_in, pro_in, coin)
        if sell_pro is None:
            return pyomo.Constraint.Skip
        else:
            if (sit_in, pro_in) in m.pro_tuples_exp:
                return (m.cap_pro[sit_in, pro_in] == m.cap_pro[sit_in, sell_pro])
            else:
                return (m.process_dict['inst-cap'][(sit_in, pro_in)] 
                        == m.process_dict['inst-cap'][(sit_in, sell_pro)])
    else:
        return pyomo.Constraint.Skip

        
# total CO2 output <= Global CO2 limit
def res_global_co2_limit_rule(m):
    if math.isinf(m.global_prop.loc['CO2 limit', 'value']):
        return pyomo.Constraint.Skip
    elif m.global_prop.loc['CO2 limit', 'value'] >= 0:
        co2_output_sum = 0
        for tm in m.tm:
            for sit in m.sit:
                # minus because negative commodity_balance represents creation
                # of that commodity.
                co2_output_sum += (- commodity_balance(m, tm, sit, 'CO2') *
                                   m.dt)

        # scaling to annual output (cf. definition of m.weight)
        co2_output_sum *= m.weight
        return (co2_output_sum <= m.global_prop.loc['CO2 limit', 'value'])
    else:
        return pyomo.Constraint.Skip

        