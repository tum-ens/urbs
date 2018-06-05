import math
import pyomo.core as pyomo


def create_min_model_sets(m)
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
    if not m.process_exp.empty:
        m.pro_exp = pyomo.Set(
            initialize=m.process_exp.index.get_level_values('Process').unique(),
            doc='Set of conversion processes')
    if not m.process_const.empty:
        m.pro_const = pyomo.Set(
            initialize=m.process_const.index.get_level_values('Process').unique(),
            doc='Set of conversion processes')
    # cost_type
    m.cost_type = pyomo.Set(
        initialize=['Invest', 'Fixed', 'Variable', 'Fuel', 'Revenue',
                    'Purchase', 'Environmental'],
        doc='Set of cost types (hard-coded)')
    
    return m

def create_min_model_tuples(m,tm,sit,pro,com)
    m.com_tuples = pyomo.Set(
        within=m.sit*m.com*m.com_type,
        initialize=m.commodity.index,
        doc='Combinations of defined commodities, e.g. (Mid,Elec,Demand)')
    if not m.process_exp.empty:
        m.pro_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_exp,
            initialize=m.process.index,
            doc='Combinations of possible processes, e.g. (North,Coal plant)')  
        # process tuples for area rule
        m.pro_area_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_exp,
            initialize=m.proc_area.index,
            doc='Processes and Sites with area Restriction')    
        # process input/output
        m.pro_input_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_exp*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_tuples_exp
                        for (pro, commodity) in m.r_in.index
                        if process == pro],
            doc='Commodities consumed by process by site, e.g. (Mid,PV,Solar)')
        m.pro_output_tuples_exp = pyomo.Set(
            within=m.sit*m.pro*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_tuples_exp
                        for (pro, commodity) in m.r_out.index
                        if process == pro],
            doc='Commodities produced by process by site, e.g. (Mid,PV,Elec)')
        # process tuples for maximum gradient feature
        m.pro_maxgrad_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_exp,
            initialize=[(sit, pro)
                        for (sit, pro) in m.pro_tuples_exp
                        if m.process.loc[sit, pro]['max-grad'] < 1.0 / dt],
            doc='Processes with maximum gradient smaller than timestep length')
        # process tuples for partial feature
        m.pro_partial_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_exp,
            initialize=[(site, process)
                        for (site, process) in m.pro_tuples_exp
                        for (pro, _) in m.r_in_min_fraction.index
                        if process == pro],
            doc='Processes with partial input')
        m.pro_partial_input_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_exp*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_partial_tuples_exp
                        for (pro, commodity) in m.r_in_min_fraction.index
                        if process == pro],
            doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,Coal)')
        m.pro_partial_output_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_exp*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_partial_tuples_exp
                        for (pro, commodity) in m.r_out_min_fraction.index
                        if process == pro],
            doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,CO2)')
    if not m.process_const.empty:
        m.pro_const_tuples = pyomo.Set(
            within=m.sit*m.pro_const,
            initialize=m.process.index,
            doc='Combinations of possible processes, e.g. (North,Coal plant)')   
        # process tuples for area rule
        m.pro_area_tuples_exp = pyomo.Set(
            within=m.sit*m.pro_const,
            initialize=m.proc_area.index,
            doc='Processes and Sites with area Restriction')   
        # process input/output
        m.pro_input_tuples_const = pyomo.Set(
            within=m.sit*m.pro_exp*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_tuples_const
                        for (pro, commodity) in m.r_in.index
                        if process == pro],
            doc='Commodities consumed by process by site, e.g. (Mid,PV,Solar)')
        m.pro_output_tuples_const = pyomo.Set(
            within=m.sit*m.pro*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_tuples_const
                        for (pro, commodity) in m.r_out.index
                        if process == pro],
            doc='Commodities produced by process by site, e.g. (Mid,PV,Elec)')
        # process tuples for partial feature
        m.pro_partial_tuples_const = pyomo.Set(
            within=m.sit*m.pro_const,
            initialize=[(site, process)
                        for (site, process) in m.pro_tuples_const
                        for (pro, _) in m.r_in_min_fraction.index
                        if process == pro],
            doc='Processes with partial input')
        m.pro_partial_input_tuples_const = pyomo.Set(
            within=m.sit*m.pro_const*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_partial_tuples_const
                        for (pro, commodity) in m.r_in_min_fraction.index
                        if process == pro],
            doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,Coal)')
        m.pro_partial_output_tuples_const = pyomo.Set(
            within=m.sit*m.pro_const*m.com,
            initialize=[(site, process, commodity)
                        for (site, process) in m.pro_partial_tuples_const
                        for (pro, commodity) in m.r_out_min_fraction.index
                        if process == pro],
            doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,CO2)')
    
    return m
    
def create_param(m)
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
        doc='Time step duration (in hours), default: 1')>
        
    return m
    
def create_min_model_var(m,tm,sit,com,pro)

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
    """m.tau_pro = pyomo.Var(
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
        doc='Power flow out of process (MW) per timestep')"""
        