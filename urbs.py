"""urbs: A linear optimisation model for distributed energy systems

urbs minimises total cost for providing energy in form of desired commodities
(usually electricity) to satisfy a given demand in form of timeseries. The
model contains commodities (electricity, fossil fuels, renewable energy
sources, greenhouse gases), processes that convert one commodity to another
(while emitting greenhouse gases as a secondary output), transmission for
transporting commodities between sites and storage for saving/retrieving
commodities.

"""
import coopr.pyomo as pyomo
import math
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from operator import itemgetter
from random import random
from xlrd import XLRDError

COLORS = {
    'Biomass plant': (0, 122, 55),
    'Coal plant': (100, 100, 100),
    'Gas plant': (237, 227, 0),
    'Hydro plant': (198, 188, 240),
    'Lignite plant': (116, 66, 65),
    'Photovoltaics': (243, 174, 0),
    'Slack powerplant': (163, 74, 130),
    'Wind park': (122, 179, 225),
    'Decoration': (128, 128, 128),  # plot labels
    'Demand': (25, 25, 25),  # thick demand line
    'Grid': (128, 128, 128),  # background grid
    'Overproduction': (190, 0, 99),  # excess power
    'Storage': (60, 36, 154),  # storage area
    'Stock': (222, 222, 222)}  # stock commodity power


def read_excel(filename):
    """Read Excel input file and prepare URBS input dict.

    Reads an Excel spreadsheet that adheres to the structure shown in
    mimo-example.xlsx. Two preprocessing steps happen here:
    1. Column titles in 'Demand' and 'SupIm' are split, so that
    'Site.Commodity' becomes the MultiIndex column ('Site', 'Commodity').
    2. The attribute 'annuity-factor' is derived here from the columns 'wacc'
    and 'depreciation' for 'Process', 'Transmission' and 'Storage'.

    Args:
        filename: filename to an Excel spreadsheet with the required sheets
            'Commodity', 'Process', 'Transmission', 'Storage', 'Demand' and
            'SupIm'.

    Returns:
        a dict of 6 DataFrames

    Example:
        >>> data = read_excel('mimo-example.xlsx')
        >>> data['hacks'].loc['Global CO2 limit', 'Value']
        150000000
    """
    with pd.ExcelFile(filename) as xls:
        commodity = xls.parse(
            'Commodity',
            index_col=['Site', 'Commodity', 'Type'])
        process = xls.parse(
            'Process',
            index_col=['Site', 'Process'])
        process_commodity = xls.parse(
            'Process-Commodity',
            index_col=['Process', 'Commodity', 'Direction'])
        transmission = xls.parse(
            'Transmission',
            index_col=['Site In', 'Site Out', 'Transmission', 'Commodity'])
        storage = xls.parse(
            'Storage',
            index_col=['Site', 'Storage', 'Commodity'])
        demand = xls.parse(
            'Demand',
            index_col=['t'])
        supim = xls.parse(
            'SupIm',
            index_col=['t'])
        buy_sell_price = xls.parse(
            'Buy-Sell-Price',
            index_col=['t'])
        try:
            hacks = xls.parse(
                'Hacks',
                index_col=['Name'])
        except XLRDError:
            hacks = None

    # prepare input data
    # split columns by dots '.', so that 'DE.Elec' becomes the two-level
    # column index ('DE', 'Elec')
    demand.columns = split_columns(demand.columns, '.')
    supim.columns = split_columns(supim.columns, '.')
    buy_sell_price.columns = split_columns(buy_sell_price.columns, '.')

    # derive annuity factor from WACC and depreciation periods
    process['annuity-factor'] = annuity_factor(
        process['depreciation'], process['wacc'])
    transmission['annuity-factor'] = annuity_factor(
        transmission['depreciation'], transmission['wacc'])
    storage['annuity-factor'] = annuity_factor(
        storage['depreciation'], storage['wacc'])

    data = {
        'commodity': commodity,
        'process': process,
        'process_commodity': process_commodity,
        'transmission': transmission,
        'storage': storage,
        'demand': demand,
        'supim': supim,
        'buy_sell_price': buy_sell_price}
    if hacks is not None:
        data['hacks'] = hacks

    # sort nested indexes to make direct assignments work, cf
    # http://pandas.pydata.org/pandas-docs/stable/indexing.html#the-need-for-sortedness-with-multiindex
    for key in data:
        if isinstance(data[key].index, pd.core.index.MultiIndex):
            data[key].sortlevel(inplace=True)
    return data


def create_model(data, timesteps=None, dt=1):
    """Create a pyomo ConcreteModel URBS object from given input data.

    Args:
        data: a dict of 6 DataFrames with the keys 'commodity', 'process',
            'transmission', 'storage', 'demand' and 'supim'.
        timesteps: optional list of timesteps, default: demand timeseries
        dt: timestep duration in hours (default: 1)

    Returns:
        a pyomo ConcreteModel object
    """
    m = pyomo.ConcreteModel()    
    m.name = 'URBS'
    m.created = datetime.now().strftime('%Y%m%dT%H%M')
    
    # Optional
    if not timesteps:
        timesteps = data['demand'].index.tolist()

    # Preparations
    # ============
    # Data import. Syntax to access a value within equation definitions looks
    # like this:
    #
    #     m.storage.loc[site, storage, commodity][attribute]
    #
    m.commodity = data['commodity']
    m.process = data['process']
    m.process_commodity = data['process_commodity']
    m.transmission = data['transmission']
    m.storage = data['storage']
    m.demand = data['demand']
    m.supim = data['supim']
    m.buy_sell_price = data['buy_sell_price']
    m.timesteps = timesteps

    # process input/output ratios
    m.r_in = m.process_commodity.xs('In', level='Direction')['ratio']
    m.r_out = m.process_commodity.xs('Out', level='Direction')['ratio']

    # Sets
    # ====
    # Syntax: m.{name} = Set({domain}, initialize={values})
    # where name: set name
    #       domain: set domain for tuple sets, a cartesian set product
    #       values: set values, a list or array of element tuples

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
        doc='Set of modelled timesteps')

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
    m.pro = pyomo.Set(
        initialize=m.process.index.get_level_values('Process').unique(),
        doc='Set of conversion processes')

    # tranmission (e.g. hvac, hvdc, pipeline...)
    m.tra = pyomo.Set(
        initialize=m.transmission.index.get_level_values('Transmission').unique(),
        doc='Set of transmission technologies')

    # storage (e.g. hydrogen, pump storage)
    m.sto = pyomo.Set(
        initialize=m.storage.index.get_level_values('Storage').unique(),
        doc='Set of storage technologies')

    # cost_type
    m.cost_type = pyomo.Set(
        initialize=['Inv', 'Fix', 'Var', 'Fuel','Revenue','Purchase'],
        doc='Set of cost types (hard-coded)')

    # tuple sets
    m.com_tuples = pyomo.Set(
        within=m.sit*m.com*m.com_type,
        initialize=m.commodity.index,
        doc='Combinations of defined commodities, e.g. (Mid,Elec,Demand)')
    m.pro_tuples = pyomo.Set(
        within=m.sit*m.pro,
        initialize=m.process.index,
        doc='Combinations of possible processes, e.g. (North,Coal plant)')
    m.tra_tuples = pyomo.Set(
        within=m.sit*m.sit*m.tra*m.com,
        initialize=m.transmission.index,
        doc='Combinations of possible transmission, e.g. (South,Mid,hvac,Elec)')
    m.sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com,
        initialize=m.storage.index,
        doc='Combinations of possible storage by site, e.g. (Mid,Bat,Elec)')

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

    # Parameters

    # weight = length of year (hours) / length of simulation (hours)
    # weight scales costs and emissions from length of simulation to a full
    # year, making comparisons among cost types (invest is annualized, fixed
    # costs are annual by default, variable costs are scaled by weight) and
    # among different simulation durations meaningful.
    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.t) * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')

    # dt = spacing between timesteps. Required for storage equation that
    # converts between energy (storage content, e_sto_con) and power (all other
    # quantities that start with "e_")
    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')

    # Variables

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
        doc='Use of sell commodity source (kW) per timestep')
    m.e_co_buy = pyomo.Var(
       m.tm, m.com_tuples,
       within=pyomo.NonNegativeReals,
       doc='Use of buy commodity source (kW) per timestep')

    # process
    m.cap_pro = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total process capacity (MW)')
    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')
    m.tau_pro = pyomo.Var(
        m.tm, m.pro_tuples,
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

    # transmission
    m.cap_tra = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total transmission capacity (MW)')
    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')
    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into transmission line (MW) per timestep')
    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of transmission line (MW) per timestep')

    # storage
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

    # Equation declarations
    # equation bodies are defined in separate functions, referred to here by 
    # their name in the "rule" keyword.
    
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
        m.pro_tuples,
        rule=def_process_capacity_rule,
        doc='total process capacity = inst-cap + new capacity')
    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')
    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')
    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')
    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')
    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')
    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='total power connection capacity must be symmetric in both directions')

    # transmission
    m.def_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity = inst-cap + new capacity')
    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')
    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')
    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')
    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

    # storage
    m.def_storage_state = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=def_storage_state_rule,
        doc='storage[t] = storage[t-1] + input - output')
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

    # costs
    m.def_costs = pyomo.Constraint(
        m.cost_type,
        rule=def_costs_rule,
        doc='main cost function by cost type')
    m.obj = pyomo.Objective(
        rule=obj_rule,
        sense=pyomo.minimize,
        doc='minimize(cost = sum of all cost types)')

    # possibly: add hack features
    if 'hacks' in data:
        m = add_hacks(m, data['hacks'])

    return m


# Constraints

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
            power_surplus -= m.demand.loc[tm][sit, com]
        except KeyError:
            pass
    return power_surplus == 0

# stock commodity purchase == commodity consumption, according to
# commodity_balance of current (time step, site, commodity);
# limit stock commodity use per time step
def res_stock_step_rule(m, tm, sit, com, com_type):
    if com not in m.com_stock:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_stock[tm, sit, com, com_type] <=
                m.commodity.loc[sit, com, com_type]['maxperstep'])

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
                m.commodity.loc[sit, com, com_type]['max'])

# limit sell commodity use per time step
def res_sell_step_rule(m, tm, sit, com, com_type):
    if com not in m.com_sell:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_sell[tm, sit, com, com_type] <=
                   m.commodity.loc[sit, com, com_type]['maxperstep'])

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
                  m.commodity.loc[sit, com, com_type]['max'])

# limit buy commodity use per time step
def res_buy_step_rule(m, tm, sit, com, com_type):
    if com not in m.com_buy:
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_buy[tm, sit, com, com_type] <=
                   m.commodity.loc[sit, com, com_type]['maxperstep'])

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
                  m.commodity.loc[sit, com, com_type]['max'])

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
                m.commodity.loc[sit, com, com_type]['maxperstep'])

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
                m.commodity.loc[sit, com, com_type]['max'])

# process
# process capacity == new capacity + existing capacity
def def_process_capacity_rule(m, sit, pro):
    return (m.cap_pro[sit, pro] ==
            m.cap_pro_new[sit, pro] +
            m.process.loc[sit, pro]['inst-cap'])

# process input power == process throughput * input ratio
def def_process_input_rule(m, tm, sit, pro, co):
    return (m.e_pro_in[tm, sit, pro, co] ==
            m.tau_pro[tm, sit, pro] * m.r_in.loc[pro, co])

# process output power = process throughput * output ratio
def def_process_output_rule(m, tm, sit, pro, co):
    return (m.e_pro_out[tm, sit, pro, co] ==
            m.tau_pro[tm, sit, pro] * m.r_out.loc[pro, co])

# process input (for supim commodity) = process capacity * timeseries
def def_intermittent_supply_rule(m, tm, sit, pro, coin):
    if coin in m.com_supim:
        return (m.e_pro_in[tm, sit, pro, coin] ==
                m.cap_pro[sit, pro] * m.supim.loc[tm][sit, coin])
    else:
        return pyomo.Constraint.Skip

# process throughput <= process capacity
def res_process_throughput_by_capacity_rule(m, tm, sit, pro):
    return (m.tau_pro[tm, sit, pro] <= m.cap_pro[sit, pro])

# lower bound <= process capacity <= upper bound
def res_process_capacity_rule(m, sit, pro):
    return (m.process.loc[sit, pro]['cap-lo'],
            m.cap_pro[sit, pro],
            m.process.loc[sit, pro]['cap-up'])

# power connection capacity: Sell == Buy
def res_sell_buy_symmetry_rule(m, sit_in, pro_in, coin):
# constraint only for sell and buy processes
# and the processes musst be in the same site
    if coin in m.com_buy:
        sell_pro = search_sell_buy_tuple(m, sit_in, pro_in, coin)
        if sell_pro is None:
            return pyomo.Constraint.Skip
        else:
            return (m.cap_pro[sit_in, pro_in] ==
                        m.cap_pro[sit_in, sell_pro])
    else:
        return pyomo.Constraint.Skip

# transmission

# transmission capacity == new capacity + existing capacity
def def_transmission_capacity_rule(m, sin, sout, tra, com):
    return (m.cap_tra[sin, sout, tra, com] ==
            m.cap_tra_new[sin, sout, tra, com] +
            m.transmission.loc[sin, sout, tra, com]['inst-cap'])

# transmission output == transmission input * efficiency
def def_transmission_output_rule(m, tm, sin, sout, tra, com):
    return (m.e_tra_out[tm, sin, sout, tra, com] ==
            m.e_tra_in[tm, sin, sout, tra, com] *
            m.transmission.loc[sin, sout, tra, com]['eff'])

# transmission input <= transmission capacity
def res_transmission_input_by_capacity_rule(m, tm, sin, sout, tra, com):
    return (m.e_tra_in[tm, sin, sout, tra, com] <=
            m.cap_tra[sin, sout, tra, com])

# lower bound <= transmission capacity <= upper bound
def res_transmission_capacity_rule(m, sin, sout, tra, com):
    return (m.transmission.loc[sin, sout, tra, com]['cap-lo'],
            m.cap_tra[sin, sout, tra, com],
            m.transmission.loc[sin, sout, tra, com]['cap-up'])

# transmission capacity from A to B == transmission capacity from B to A
def res_transmission_symmetry_rule(m, sin, sout, tra, com):
    return m.cap_tra[sin, sout, tra, com] == m.cap_tra[sout, sin, tra, com]

# storage

# storage content in timestep [t] == storage content[t-1]
# + newly stored energy * input efficiency
# - retrieved energy / output efficiency
def def_storage_state_rule(m, t, sit, sto, com):
    return (m.e_sto_con[t, sit, sto, com] ==
            m.e_sto_con[t-1, sit, sto, com] +
            m.e_sto_in[t, sit, sto, com] *
            m.storage.loc[sit, sto, com]['eff-in'] * m.dt -
            m.e_sto_out[t, sit, sto, com] /
            m.storage.loc[sit, sto, com]['eff-out'] * m.dt)

# storage power == new storage power + existing storage power
def def_storage_power_rule(m, sit, sto, com):
    return (m.cap_sto_p[sit, sto, com] ==
            m.cap_sto_p_new[sit, sto, com] +
            m.storage.loc[sit, sto, com]['inst-cap-p'])

# storage capacity == new storage capacity + existing storage capacity
def def_storage_capacity_rule(m, sit, sto, com):
    return (m.cap_sto_c[sit, sto, com] ==
            m.cap_sto_c_new[sit, sto, com] +
            m.storage.loc[sit, sto, com]['inst-cap-c'])

# storage input <= storage power
def res_storage_input_by_power_rule(m, t, sit, sto, com):
    return m.e_sto_in[t, sit, sto, com] <= m.cap_sto_p[sit, sto, com]

# storage output <= storage power
def res_storage_output_by_power_rule(m, t, sit, sto, co):
    return m.e_sto_out[t, sit, sto, co] <= m.cap_sto_p[sit, sto, co]

# storage content <= storage capacity
def res_storage_state_by_capacity_rule(m, t, sit, sto, com):
    return m.e_sto_con[t, sit, sto, com] <= m.cap_sto_c[sit, sto, com]

# lower bound <= storage power <= upper bound
def res_storage_power_rule(m, sit, sto, com):
    return (m.storage.loc[sit, sto, com]['cap-lo-p'],
            m.cap_sto_p[sit, sto, com],
            m.storage.loc[sit, sto, com]['cap-up-p'])

# lower bound <= storage capacity <= upper bound
def res_storage_capacity_rule(m, sit, sto, com):
    return (m.storage.loc[sit, sto, com]['cap-lo-c'],
            m.cap_sto_c[sit, sto, com],
            m.storage.loc[sit, sto, com]['cap-up-c'])

# initialization of storage content in first timestep t[1]
# forced minimun  storage content in final timestep t[len(m.t)]
# content[t=1] == storage capacity * fraction <= content[t=final]
def res_initial_and_final_storage_state_rule(m, t, sit, sto, com):
    if t == m.t[1]:  # first timestep (Pyomo uses 1-based indexing)
        return (m.e_sto_con[t, sit, sto, com] ==
                m.cap_sto_c[sit, sto, com] *
                m.storage.loc[sit, sto, com]['init'])
    elif t == m.t[len(m.t)]:  # last timestep
        return (m.e_sto_con[t, sit, sto, com] >=
                m.cap_sto_c[sit, sto, com] *
                m.storage.loc[sit, sto, com]['init'])
    else:
        return pyomo.Constraint.Skip

# Objective
def def_costs_rule(m, cost_type):
    """Calculate total costs by cost type.

    Sums up process activity and capacity expansions
    and sums them in the cost types that are specified in the set
    m.cost_type. To change or add cost types, add/change entries
    there and modify the if/elif cases in this function accordingly.

    Cost types are
      - Investment costs for process power, storage power and
        storage capacity. They are multiplied by the annuity
        factors.
      - Fixed costs for process power, storage power and storage
        capacity.
      - Variables costs for usage of processes, storage and transmission.
      - Fuel costs for stock commodity purchase.

    """
    if cost_type == 'Inv':
        return m.costs['Inv'] == \
            sum(m.cap_pro_new[p] *
                m.process.loc[p]['inv-cost'] *
                m.process.loc[p]['annuity-factor']
                for p in m.pro_tuples) + \
            sum(m.cap_tra_new[t] *
                m.transmission.loc[t]['inv-cost'] *
                m.transmission.loc[t]['annuity-factor']
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p_new[s] *
                m.storage.loc[s]['inv-cost-p'] *
                m.storage.loc[s]['annuity-factor'] +
                m.cap_sto_c_new[s] *
                m.storage.loc[s]['inv-cost-c'] *
                m.storage.loc[s]['annuity-factor']
                for s in m.sto_tuples)

    elif cost_type == 'Fix':
        return m.costs['Fix'] == \
            sum(m.cap_pro[p] * m.process.loc[p]['fix-cost']
                for p in m.pro_tuples) + \
            sum(m.cap_tra[t] * m.transmission.loc[t]['fix-cost']
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p[s] * m.storage.loc[s]['fix-cost-p'] +
                m.cap_sto_c[s] * m.storage.loc[s]['fix-cost-c']
                for s in m.sto_tuples)

    elif cost_type == 'Var':
        return m.costs['Var'] == \
            sum(m.tau_pro[(tm,) + p] * m.dt *
                m.process.loc[p]['var-cost'] *
                m.weight
                for tm in m.tm for p in m.pro_tuples) + \
            sum(m.e_tra_in[(tm,) + t] * m.dt *
                m.transmission.loc[t]['var-cost'] *
                m.weight
                for tm in m.tm for t in m.tra_tuples) + \
            sum(m.e_sto_con[(tm,) + s] *
                m.storage.loc[s]['var-cost-c'] * m.weight +
                (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) * m.dt *
                m.storage.loc[s]['var-cost-p'] * m.weight
                for tm in m.tm for s in m.sto_tuples)

    elif cost_type == 'Fuel':
        return m.costs['Fuel'] == sum(
            m.e_co_stock[(tm,) + c] * m.dt *
            m.commodity.loc[c]['price'] *
            m.weight
            for tm in m.tm for c in m.com_tuples
            if c[1] in m.com_stock)

    elif cost_type == 'Revenue':
        sell_tuples = commodity_subset(m.com_tuples, m.com_sell)
        com_prices = get_com_price(m, sell_tuples)

        return m.costs['Revenue'] == -sum(
            m.e_co_sell[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in sell_tuples)

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)
        com_prices = get_com_price(m, buy_tuples)

        return m.costs['Purchase'] == sum(
            m.e_co_buy[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in buy_tuples)

    else:
        raise NotImplementedError("Unknown cost type.")

def obj_rule(m):
    return pyomo.summation(m.costs)


# Hacks

def add_hacks(model, hacks):
    """ add hackish features to model object

    This function is reserved for corner cases/features that still lack a
    satisfyingly general solution that could become part of create_model.
    Use hack features sparingly and think about how to incorporate into main
    model function before adding here. Otherwise, these features might become
    a maintenance burden.

    """

    # Store hack data
    model.hacks = hacks

    # Global CO2 limit
    try:
        global_co2_limit = hacks.loc['Global CO2 limit', 'Value']
    except KeyError:
        global_co2_limit = float('inf')

    # only add constraint if limit is finite
    if not math.isinf(global_co2_limit):
        model.res_global_co2_limit = pyomo.Constraint(
            rule=res_global_co2_limit_rule,
            doc='total co2 commodity output <= hacks.Glocal CO2 limit')

    return model

# total CO2 output <= Global CO2 limit
def res_global_co2_limit_rule(m):
    co2_output_sum = 0
    for tm in m.tm:
        for sit in m.sit:
            # minus because negative commodity_balance represents creation of 
            # that commodity.
            co2_output_sum += (- commodity_balance(m, tm, sit, 'CO2') * m.dt)

    # scaling to annual output (cf. definition of m.weight)
    co2_output_sum *= m.weight
    return (co2_output_sum <= m.hacks.loc['Global CO2 limit', 'Value'])

# Helper functions


def annuity_factor(n, i):
    """Annuity factor formula.

    Evaluates the annuity factor formula for depreciation duration
    and interest rate. Works also well for equally sized numpy arrays
    of values for n and i.

    Args:
        n: depreciation period (years)
        i: interest rate (percent, e.g. 0.06 means 6 %)

    Returns:
        Value of the expression :math:`\\frac{(1+i)^n i}{(1+i)^n - 1}`

    Example:
        >>> round(annuity_factor(20, 0.07), 5)
        0.09439

    """
    return (1+i)**n * i / ((1+i)**n - 1)


def commodity_balance(m, tm, sit, com):
    """Calculate commodity balance at given timestep.

    For a given commodity co and timestep tm, calculate the balance of
    consumed (to process/storage/transmission, counts positive) and provided
    (from process/storage/transmission, counts negative) power. Used as helper
    function in create_model for constraints on demand and stock commodities.

    Args:
        m: the model object
        tm: the timestep
        site: the site
        com: the commodity

    Returns
        balance: net value of consumed (positive) or provided (negative) power

    """
    balance = 0
    for site, process in m.pro_tuples:
        if site == sit and com in m.r_in.loc[process].index:
            # usage as input for process increases balance
            balance += m.e_pro_in[(tm, site, process, com)]
        if site == sit and com in m.r_out.loc[process].index:
            # output from processes decreases balance
            balance -= m.e_pro_out[(tm, site, process, com)]
    for site_in, site_out, transmission, commodity in m.tra_tuples:
        # exports increase balance
        if site_in == sit and commodity == com:
            balance += m.e_tra_in[(tm, site_in, site_out, transmission, com)]
        # imports decrease balance
        if site_out == sit and commodity == com:
            balance -= m.e_tra_out[(tm, site_in, site_out, transmission, com)]
    for site, storage, commodity in m.sto_tuples:
        # usage as input for storage increases consumption
        # output from storage decreases consumption
        if site == sit and commodity == com:
            balance += m.e_sto_in[(tm, site, storage, com)]
            balance -= m.e_sto_out[(tm, site, storage, com)]
    return balance


def split_columns(columns, sep='.'):
    """Split columns by separator into MultiIndex.

    Given a list of column labels containing a separator string (default: '.'),
    derive a MulitIndex that is split at the separator string.

    Args:
        columns: list of column labels, containing the separator string
        sep: the separator string (default: '.')

    Returns:
        a MultiIndex corresponding to input, with levels split at separator

    Example:
        >>> split_columns(['DE.Elec', 'MA.Elec', 'NO.Wind'])
        MultiIndex(levels=[[u'DE', u'MA', u'NO'], [u'Elec', u'Wind']],
                   labels=[[0, 1, 2], [0, 0, 1]])

    """
    column_tuples = [tuple(col.split('.')) for col in columns]
    return pd.MultiIndex.from_tuples(column_tuples)

def commodity_subset(com_tuples, type_name):
    """ Unique list of commodity names for given type. 

    Args:
        com_tuples: a list of (site, commodity, commodity type) tuples
        type_name: a commodity type or a ist of a commodity types

    Returns:
        The set (unique elements/list) of commodity names of the desired type
    """
    if type(type_name) is str:
        # type_name: ('Stock', 'SupIm', 'Env' or 'Demand')
        return set(com for sit, com, com_type in com_tuples
                   if com_type == type_name)
    else:
        # type(type_name) is a class 'coopr.pyomo.base.sets.SimpleSet'
        # type_name: ('Buy')=>('Elec buy', 'Heat buy')
        return set((sit, com, com_type) for sit, com, com_type in com_tuples
                   if com in type_name)

def get_com_price(instance, tuples):
    """ Calculate commodity prices for each modelled timestep.

    Args:
        instance: a Pyomo ConcreteModel instance
        tuples: a list of (site, commodity, commodity type) tuples

    Returns:
        a Pandas DataFrame with entities as columns and timesteps as index
    """
    com_price = pd.DataFrame(index=instance.tm)
    for c in tuples:
        # check commodity price: fix or has a timeseries
        # type(instance.commodity.loc[c]['price']):
        # float => fix: com price = 0.15
        # string => var: com price = '1.25xBuy' (Buy: refers to timeseries)
        if not isinstance(instance.commodity.loc[c]['price'], float):
            # a different commodity price for each hour
            # factor, to realize a different commodity price for each site
            factor = extract_number_str(instance.commodity.loc[c]['price'])
            price = factor * instance.buy_sell_price.loc[(instance.tm,) + (c[1],)]
            com_price[c] = pd.Series(price, index=com_price.index)
        else:
            # same commdoity price for each hour
            price = instance.commodity.loc[c]['price']
            com_price[c] = pd.Series(price, index=com_price.index)
    return com_price

def extract_number_str(str_in):
    """ Extract first number from a given string and convert to a float number.

    The function works with the following formats (,25), (.25), (2), (2,5), (2.5),
    (1,000.25), (1.000,25) and  doesn't with (1e3), (1.5-0.4j) and negative numbers.

    Args:
        str_in: a string ('1,20BUY')

    Returns:
        A float number (1.20)
    """
    import re
    # deletes all char starting after the number
    start_char = re.search('[*:!%$&?a-zA-Z]',str_in).start()
    str_num = str_in[:start_char]

    if re.search('\d+',str_num) is None:
        # no number in str_num
        return 1.0
    elif re.search('^(\d+|\d{1,3}(,\d{3})*)(\.\d+)?$',str_num) is not None:
        #Commas required between powers of 1,000
        #Can't start with "."
        #Pass: (1,000,000), (0.001)
        #Fail: (1000000), (1,00,00,00), (.001)
        str_num = str_num.replace(',','')
        return float(str_num)
    elif re.search('^(\d+|\d{1,3}(.\d{3})*)(\,\d+)?$',str_num) is not None:
        #Dots required between powers of 1.000
        #Can't start with ","
        #Pass: (1.000.000), (0,001)
        #Fail: (1000000), (1.00.00,00), (,001)
        str_num = str_num.replace('.','')
        return float(str_num.replace(',','.'))
    elif re.search('^\d*\.?\d+$',str_num) is not None:
        #No commas allowed
        #Pass: (1000.0), (001), (.001)
        #Fail: (1,000.0
        return float(str_num)
    elif re.search('^\d*\,?\d+$',str_num) is not None:
        #No dots allowed
        #Pass: (1000,0), (001), (,001)
        #Fail: (1.000,0
        str_num = str_num.replace(',','.')
        return float(str_num)

def search_sell_buy_tuple(instance, sit_in, pro_in, coin):
    """ Return the equivalent sell-process for a given buy-process.

    Args:
        instance: a Pyomo ConcreteModel instance
        sit_in: a site
        pro_in: a process
        co_in: a commodity

    Returns:
        a process
    """
    pro_output_tuples = list(instance.pro_output_tuples.value)
    pro_input_tuples = list(instance.pro_input_tuples.value)
    # search the output commodities for the "buy" process
    # buy_out = (site,output_commodity)
    buy_out = set([(x[0],x[2]) for x in pro_output_tuples if x[1] == pro_in])
    # search the sell process for the output_commodity from the buy process
    sell_output_tuple = ([x for x in pro_output_tuples if x[2] in instance.com_sell])
    for k in range(len(sell_output_tuple)):
        sell_pro = sell_output_tuple[k][1]
        sell_in = set([(x[0],x[2]) for x in pro_input_tuples if x[1] == sell_pro])
        # check: buy - commodity == commodity - sell; for a site
        if not(sell_in.isdisjoint(buy_out)):
            return sell_pro
    return None

def get_entity(instance, name):
    """ Return a DataFrame for an entity in model instance.

    Args:
        instance: a Pyomo ConcreteModel instance
        name: name of a Set, Param, Var, Constraint or Objective

    Returns:
        a single-columned Pandas DataFrame with domain as index
    """

    # retrieve entity, its type and its onset names
    entity = instance.__getattribute__(name)
    labels = _get_onset_names(entity)

    # extract values
    if isinstance(entity, pyomo.Set):
        # Pyomo sets don't have values, only elements
        results = pd.DataFrame([(v, 1) for v in entity.value])

        # for unconstrained sets, the column label is identical to their index
        # hence, make index equal to entity name and append underscore to name
        # (=the later column title) to preserve identical index names for both
        # unconstrained supersets
        if not labels:
            labels = [name]
            name = name+'_'

    elif isinstance(entity, pyomo.Param):
        if entity.dim() > 1:
            results = pd.DataFrame([v[0]+(v[1],) for v in entity.iteritems()])
        else:
            results = pd.DataFrame(entity.iteritems())
    else:
        # create DataFrame
        if entity.dim() > 1:
            # concatenate index tuples with value if entity has
            # multidimensional indices v[0]
            results = pd.DataFrame(
                [v[0]+(v[1].value,) for v in entity.iteritems()])
        else:
            # otherwise, create tuple from scalar index v[0]
            results = pd.DataFrame(
                [(v[0], v[1].value) for v in entity.iteritems()])

    # check for duplicate onset names and append one to several "_" to make
    # them unique, e.g. ['sit', 'sit', 'com'] becomes ['sit', 'sit_', 'com']
    for k, label in enumerate(labels):
        if label in labels[:k]:
            labels[k] = labels[k] + "_"

    if not results.empty:
        # name columns according to labels + entity name
        results.columns = labels + [name]
        results.set_index(labels, inplace=True)

    return results


def get_entities(instance, names):
    """ Return one DataFrame with entities in columns and a common index.

    Works only on entities that share a common domain (set or set_tuple), which
    is used as index of the returned DataFrame.

    Args:
        instance: a Pyomo ConcreteModel instance
        names: list of entity names (as returned by list_entities)

    Returns:
        a Pandas DataFrame with entities as columns and domains as index
    """

    df = pd.DataFrame()
    for name in names:
        other = get_entity(instance, name)

        if df.empty:
            df = other
        else:
            index_names_before = df.index.names

            df = df.join(other, how='outer')

            if index_names_before != df.index.names:
                df.index.names = index_names_before

    return df


def list_entities(instance, entity_type):
    """ Return list of sets, params, variables, constraints or objectives

    Args:
        instance: a Pyomo ConcreteModel object
        entity_type: "set", "par", "var", "con" or "obj"

    Returns:
        DataFrame of entities

    Example:
        >>> data = read_excel('mimo-example.xlsx')
        >>> model = create_model(data, range(1,25))
        >>> list_entities(model, 'obj')  #doctest: +NORMALIZE_WHITESPACE
                                         Description Domain
        Name
        obj   minimize(cost = sum of all cost types)     []

    """

    # helper function to discern entities by type
    def filter_by_type(entity, entity_type):
        if entity_type == 'set':
            return isinstance(entity, pyomo.Set) and not entity.virtual
        elif entity_type == 'par':
            return isinstance(entity, pyomo.Param)
        elif entity_type == 'var':
            return isinstance(entity, pyomo.Var)
        elif entity_type == 'con':
            return isinstance(entity, pyomo.Constraint)
        elif entity_type == 'obj':
            return isinstance(entity, pyomo.Objective)
        else:
            raise ValueError("Unknown entity_type '{}'".format(entity_type))

    # iterate through all model components and keep only
    iter_entities = instance.__dict__.iteritems()
    entities = sorted(
        (name, entity.doc, _get_onset_names(entity))
        for (name, entity) in iter_entities
        if filter_by_type(entity, entity_type))

    # if something was found, wrap tuples in DataFrame, otherwise return empty
    if entities:
        entities = pd.DataFrame(entities,
                                columns=['Name', 'Description', 'Domain'])
        entities.set_index('Name', inplace=True)
    else:
        entities = pd.DataFrame()
    return entities


def _get_onset_names(entity):
    """
        Example:
            >>> data = read_excel('mimo-example.xlsx')
            >>> model = create_model(data, range(1,25))
            >>> _get_onset_names(model.e_co_stock)
            ['t', 'sit', 'com', 'com_type']
    """
    # get column titles for entities from domain set names
    labels = []

    if isinstance(entity, pyomo.Set):
        if entity.dimen > 1:
            # N-dimensional set tuples, possibly with nested set tuples within
            if entity.domain:
                domains = entity.domain.set_tuple
            else:
                domains = entity.set_tuple

            for domain_set in domains:
                labels.extend(_get_onset_names(domain_set))

        elif entity.dimen == 1:
            if entity.domain:
                # 1D subset; add domain name
                labels.append(entity.domain.name)
            else:
                # unrestricted set; add entity name
                labels.append(entity.name)
        else:
            # no domain, so no labels needed
            pass

    elif isinstance(entity, (pyomo.Param, pyomo.Var, pyomo.Constraint,
                    pyomo.Objective)):
        if entity.dim() > 0 and entity._index:
            labels = _get_onset_names(entity._index)
        else:
            # zero dimensions, so no onset labels
            pass

    else:
        raise ValueError("Unknown entity type!")

    return labels


def get_constants(instance):
    """Return summary DataFrames for important variables

    Usage:
        costs, cpro, ctra, csto = get_constants(instance)

    Args:
        instance: a urbs model instance

    Returns:
        (costs, cpro, ctra, csto) tuple

    Example:
        >>> import coopr.environ
        >>> from coopr.opt.base import SolverFactory
        >>> data = read_excel('mimo-example.xlsx')
        >>> model = create_model(data, range(1,25))
        >>> prob = model.create()
        >>> optim = SolverFactory('glpk')
        >>> result = optim.solve(prob)
        >>> prob.load(result)
        True
        >>> cap_pro = get_constants(prob)[1]['Total']
        >>> cap_pro.xs('Wind park', level='Process').apply(int)
        Site
        Mid      13000
        North    27271
        South     2674
        Name: Total, dtype: int64
    """
    costs = get_entity(instance, 'costs')
    cpro = get_entities(instance, ['cap_pro', 'cap_pro_new'])
    ctra = get_entities(instance, ['cap_tra', 'cap_tra_new'])
    csto = get_entities(instance, ['cap_sto_c', 'cap_sto_c_new',
                                   'cap_sto_p', 'cap_sto_p_new'])

    # better labels and index names and return sorted
    if not cpro.empty:
        cpro.index.names = ['Site', 'Process']
        cpro.columns = ['Total', 'New']
        cpro.sortlevel(inplace=True)
    if not ctra.empty:
        ctra.index.names = ['Site In', 'Site Out', 'Transmission', 'Commodity']
        ctra.columns = ['Total', 'New']
        ctra.sortlevel(inplace=True)
    if not csto.empty:
        csto.columns = ['C Total', 'C New', 'P Total', 'P New']
        csto.sortlevel(inplace=True)

    return costs, cpro, ctra, csto


def get_timeseries(instance, com, sit, timesteps=None):
    """Return DataFrames of all timeseries referring to given commodity

    Usage:
        create, consume, store, imp, exp = get_timeseries(instance, co,
                                                          sit, timesteps)

    Args:
        instance: a urbs model instance
        com: a commodity
        sit: a site
        timesteps: optional list of timesteps, defaults: all modelled timesteps

    Returns:
        a (created, consumed, storage, imported, exported) tuple of DataFrames
        timeseries. These are:

        * created: timeseries of commodity creation, including stock source
        * consumed: timeseries of commodity consumption, including demand
        * storage: timeseries of commodity storage (level, stored, retrieved)
        * imported: timeseries of commodity import (by site)
        * exported: timeseries of commodity export (by site)
    """
    if timesteps is None:
        # default to all simulated timesteps
        timesteps = sorted(get_entity(instance, 'tm').index)

    # DEMAND
    # default to zeros if commodity has no demand, get timeseries
    try:
        demand = instance.demand.loc[timesteps][sit, com]
    except KeyError:
        demand = pd.Series(0, index=timesteps)
    demand.name = 'Demand'

    # STOCK
    eco = get_entity(instance, 'e_co_stock')['e_co_stock'].unstack()['Stock']
    eco = eco.xs(sit, level='sit').unstack().fillna(0)
    try:
        stock = eco.loc[timesteps][com]
    except KeyError:
        stock = pd.Series(0, index=timesteps)
    stock.name = 'Stock'

    # PROCESS
    # select all entries of created and consumed desired commodity com and site
    # sit. Keep only entries with non-zero values and unstack process column.
    # Finally, slice to the desired timesteps.
    epro = get_entities(instance, ['e_pro_in', 'e_pro_out'])
    epro = epro.xs(sit, level='sit').xs(com, level='com')
    try:
        created = epro[epro['e_pro_out'] > 0]['e_pro_out'].unstack(level='pro')
        created = created.loc[timesteps].fillna(0)
    except KeyError:
        created = pd.DataFrame(index=timesteps)

    try:
        consumed = epro[epro['e_pro_in'] > 0]['e_pro_in'].unstack(level='pro')
        consumed = consumed.loc[timesteps].fillna(0)
    except KeyError:
        consumed = pd.DataFrame(index=timesteps)

    # TRANSMISSION
    etra = get_entities(instance, ['e_tra_in', 'e_tra_out'])
    try:
        etra.index.names = ['tm', 'sitin', 'sitout', 'tra', 'com']
        etra = etra.groupby(level=['tm', 'sitin', 'sitout', 'com']).sum()
        etra = etra.xs(com, level='com')

        imported = etra.xs(sit, level='sitout')['e_tra_out'].unstack().fillna(0)
        exported = etra.xs(sit, level='sitin')['e_tra_in'].unstack().fillna(0)
        
    except (ValueError, KeyError):
        imported = pd.DataFrame(index=timesteps)
        exported = pd.DataFrame(index=timesteps)

    # STORAGE
    # group storage energies by commodity
    # select all entries with desired commodity co
    esto = get_entities(instance, ['e_sto_con', 'e_sto_in', 'e_sto_out'])
    esto = esto.groupby(level=['t', 'sit', 'com']).sum()
    try:
        esto = esto.xs(sit, level='sit')
        stored = esto.xs(com, level='com')
        stored = stored.loc[timesteps]
        stored.columns = ['Level', 'Stored', 'Retrieved']
    except (KeyError, ValueError):
        stored = pd.DataFrame(0, index=timesteps,
                              columns=['Level', 'Stored', 'Retrieved'])

    # show stock as created
    created = created.join(stock)

    # show demand as consumed
    consumed = consumed.join(demand)

    return created, consumed, stored, imported, exported


def report(instance, filename, commodities=None, sites=None):
    """Write result summary to a spreadsheet file

    Args:
        instance: a urbs model instance
        filename: Excel spreadsheet filename, will be overwritten if exists
        commodities: optional list of commodities for which to write timeseries
        sites: optional list of sites for which to write timeseries

    Returns:
        Nothing
    """
    # get the data
    costs, cpro, ctra, csto = get_constants(instance)

    # create spreadsheet writer object
    with pd.ExcelWriter(filename) as writer:

        # write constants to spreadsheet
        costs.to_excel(writer, 'Costs')
        cpro.to_excel(writer, 'Process caps')
        ctra.to_excel(writer, 'Transmission caps')
        csto.to_excel(writer, 'Storage caps')

        # initialize timeseries tableaus
        energies = []
        timeseries = {}

        # collect timeseries data
        for co in commodities:
            for sit in sites:
                created, consumed, stored, imported, exported = get_timeseries(
                    instance, co, sit)

                overprod = pd.DataFrame(
                    columns=['Overproduction'],
                    data=created.sum(axis=1) - consumed.sum(axis=1) +
                    imported.sum(axis=1) - exported.sum(axis=1) +
                    stored['Retrieved'] - stored['Stored'])

                tableau = pd.concat(
                    [created, consumed, stored, imported, exported, overprod],
                    axis=1,
                    keys=['Created', 'Consumed', 'Storage',
                          'Import from', 'Export to', 'Balance'])
                timeseries[(co, sit)] = tableau.copy()

                # timeseries sums
                sums = pd.concat([created.sum(),
                                  consumed.sum(),
                                  stored.sum().drop('Level'),
                                  imported.sum(),
                                  exported.sum(),
                                  overprod.sum()], axis=0,
                                 keys=['Created', 'Consumed', 'Storage',
                                 'Import', 'Export', 'Balance'])
                energies.append(sums.to_frame("{}.{}".format(co, sit)))

        # write timeseries data (if any)
        if timeseries:
            # concatenate energy sums
            energy = pd.concat(energies, axis=1).fillna(0)
            energy.to_excel(writer, 'Energy sums')
    
            # write timeseries to individual sheets
            for co in commodities:
                for sit in sites:
                    # sheet names cannot be longer than 31 characters...
                    sheet_name = "{}.{} timeseries".format(co, sit)[:31]
                    timeseries[(co, sit)].to_excel(writer, sheet_name)


def plot(prob, com, sit, timesteps=None, power_unit='MW', energy_unit='MWh'):
    """Plot a stacked timeseries of commodity balance and storage.

    Creates a stackplot of the energy balance of a given commodity, together
    with stored energy in a second subplot.

    Args:
        prob: urbs model instance
        com: commodity name to plot
        sit: site name to plot
        timesteps: optional list of  timesteps to plot; default: prob.tm
        power_unit: optional string for unit; default: 'MW'
        energy_unit: optional string for storage plot; default: 'MWh'

    Returns:
        fig: figure handle
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    if timesteps is None:
        # default to all simulated timesteps
        timesteps = sorted(get_entity(prob, 'tm').index)

    # FIGURE
    fig = plt.figure(figsize=(16, 8))
    gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[2, 1])

    created, consumed, stored, imported, exported = get_timeseries(
        prob, com, sit, timesteps)

    costs, cpro, ctra, csto = get_constants(prob)

    # move retrieved/stored storage timeseries to created/consumed and
    # rename storage columns back to 'storage' for color mapping
    created = created.join(stored['Retrieved'])
    consumed = consumed.join(stored['Stored'])
    created.rename(columns={'Retrieved': 'Storage'}, inplace=True)
    consumed.rename(columns={'Stored': 'Storage'}, inplace=True)

    # only keep storage content in storage timeseries
    stored = stored['Level']

    # add imported/exported timeseries
    created = created.join(imported)
    consumed = consumed.join(exported)

    # move demand to its own plot
    demand = consumed.pop('Demand')

    # remove all columns from created which are all-zeros in both created and
    # consumed (except the last one, to prevent a completely empty frame)
    for col in created.columns:
        if not created[col].any() and len(created.columns) > 1:
            if col not in consumed.columns or not consumed[col].any():
                created.pop(col)

    # PLOT CREATED
    ax0 = plt.subplot(gs[0])
    sp0 = ax0.stackplot(created.index, created.as_matrix().T, linewidth=0.15)

    # Unfortunately, stackplot does not support multi-colored legends itself.
    # Therefore, a so-called proxy artist - invisible objects that have the
    # correct color for the legend entry - must be created. Here, Rectangle
    # objects of size (0,0) are used. The technique is explained at
    # http://stackoverflow.com/a/22984060/2375855
    proxy_artists = []
    for k, commodity in enumerate(created.columns):
        commodity_color = to_color(commodity)

        sp0[k].set_facecolor(commodity_color)
        sp0[k].set_edgecolor(to_color('Decoration'))

        proxy_artists.append(mpl.patches.Rectangle(
            (0, 0), 0, 0, facecolor=commodity_color))

    # label
    ax0.set_title('Energy balance of {} in {}'.format(com, sit))
    ax0.set_ylabel('Power ({})'.format(power_unit))

    # legend
    # add "only" consumed commodities to the legend
    lg_items = tuple(created.columns)
    for item in consumed.columns:
        # if item not in created add to legend, except items
        # from consumed which are all-zeros
        if item in created.columns or not consumed[item].any():
            pass
        else:
            # add item/commodity is not consumed
            commodity_color = to_color(item)
            proxy_artists.append(mpl.patches.Rectangle(
                (0, 0), 0, 0, facecolor=commodity_color))
            lg_items = lg_items + (item,)

    lg = ax0.legend(proxy_artists,
                    lg_items,
                    frameon=False,
                    ncol=len(proxy_artists),
                    loc='upper center',
                    bbox_to_anchor=(0.5, -0.01))
    plt.setp(lg.get_patches(), edgecolor=to_color('Decoration'),
             linewidth=0.15)
    plt.setp(ax0.get_xticklabels(), visible=False)

    # PLOT CONSUMED
    sp00 = ax0.stackplot(consumed.index, -consumed.as_matrix().T,
                         linewidth=0.15)

    # color
    for k, commodity in enumerate(consumed.columns):
        commodity_color = to_color(commodity)

        sp00[k].set_facecolor(commodity_color)
        sp00[k].set_edgecolor((.5, .5, .5))

    # PLOT DEMAND
    ax0.plot(demand.index, demand.values, linewidth=1.2,
             color=to_color('Demand'))

    # PLOT STORAGE
    ax1 = plt.subplot(gs[1], sharex=ax0)
    sp1 = ax1.stackplot(stored.index, stored.values, linewidth=0.15)

    # color
    sp1[0].set_facecolor(to_color('Storage'))
    sp1[0].set_edgecolor(to_color('Decoration'))

    # labels & y-limits
    ax1.set_xlabel('Time in year (h)')
    ax1.set_ylabel('Energy ({})'.format(energy_unit))
    try:
        ax1.set_ylim((0, 0.5 + csto.loc[sit, :, com]['C Total'].sum()))
    except KeyError:
        pass

    # make xtick distance duration-dependent
    if len(timesteps) > 26*168:
        steps_between_ticks = 168*4
    elif len(timesteps) > 3*168:
        steps_between_ticks = 168
    elif len(timesteps) > 2 * 24:
        steps_between_ticks = 24
    elif len(timesteps) > 24:
        steps_between_ticks = 6
    else:
        steps_between_ticks = 3
    xticks = timesteps[::steps_between_ticks]

    # set limits and ticks for both axes
    for ax in [ax0, ax1]:
        # ax.set_axis_bgcolor((0, 0, 0, 0))
        plt.setp(ax.spines.values(), color=to_color('Decoration'))
        ax.set_frame_on(False)
        ax.set_xlim((timesteps[0], timesteps[-1]))
        ax.set_xticks(xticks)
        ax.xaxis.grid(True, 'major', color=to_color('Grid'),
                      linestyle='-')
        ax.yaxis.grid(True, 'major', color=to_color('Grid'),
                      linestyle='-')
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        # group 1,000,000 with commas
        group_thousands = mpl.ticker.FuncFormatter(
            lambda x, pos: '{:0,d}'.format(int(x)))
        ax.yaxis.set_major_formatter(group_thousands)

    return fig


def result_figures(prob, figure_basename, plot_title_prefix=None, periods={}, **kwds):
    """Create plot for each site and demand commodity and save to files.
    
    Args:
        prob: urbs model instance
        figure_basename: relative filename prefix that is shared
        plot_title_prefix: (optional) plot title identifier
        periods: (optional) dict of 'period name': timesteps_list items
                 if omitted, one period 'all' with all timesteps is assumed
        **kwds: (optional) keyword arguments are forwarded to urbs.plot()
    """
    # default to all timesteps if no
    if not periods:
        periods = {'all': sorted(get_entity(prob, 'tm').index)}
            
    # create timeseries plot for each demand (site, commodity) timeseries
    for sit, com in prob.demand.columns:
        for period, timesteps in periods.items():
            # do the plotting
            fig = plot(prob, com, sit, timesteps=timesteps, **kwds)

            # change the figure title
            ax0 = fig.get_axes()[0]
            # if no custom title prefix is specified, use the figure 
            if not plot_title_prefix:
                plot_title_prefix = os.path.basename(figure_basename)
            new_figure_title = ax0.get_title().replace(
                'Energy balance of ', '{}: '.format(plot_title_prefix))
            ax0.set_title(new_figure_title)
            
            # save plot to files
            for ext in ['png', 'pdf']:
                fig_filename = '{}-{}-{}-{}.{}'.format(
                                    figure_basename, com, sit, period, ext)
                fig.savefig(fig_filename, bbox_inches='tight')
            plt.close(fig)


def to_color(obj=None):
    """Assign a deterministic pseudo-random color to argument.

    If COLORS[obj] is set, return that. Otherwise, create a random color from
    the hash(obj) representation string. For strings, this value depends only
    on the string content, so that same strings always yield the same color.

    Args:
        obj: any hashable object

    Returns:
        a (r, g, b) color tuple if COLORS[obj] is set, otherwise a hexstring
    """
    if obj is None:
        obj = random()
    try:
        color = tuple(rgb/255.0 for rgb in COLORS[obj])
    except KeyError:
        # random deterministic color
        color = "#{:06x}".format(abs(hash(obj)))[:7]
    return color
    

def save(prob, filename):
    """Save urbs model instance to a gzip'ed pickle file.
    
    Pickle is the standard Python way of serializing and de-serializing Python
    objects. By using it, saving any object, in case of this function a 
    Pyomo ConcreteModel, becomes a twoliner. 
    <https://docs.python.org/2/library/pickle.html>
    GZip is a standard Python compression library that is used to transparently
    compress the pickle file further.
    <https://docs.python.org/2/library/gzip.html>
    It is used over the possibly more compact bzip2 compression due to the
    lower runtime. Source: <http://stackoverflow.com/a/18475192/2375855>
    
    Args:
        prob: a urbs model instance
        filename: pickle file to be written
        
    Returns:
        Nothing
    """
    import gzip
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    with gzip.GzipFile(filename, 'wb') as file_handle:
        pickle.dump(prob, file_handle, pickle.HIGHEST_PROTOCOL)


def load(filename):
    """Load a urbs model instance from a gzip'ed pickle file
    
    Args:
        filename: pickle file
    
    Returns:
        prob: the unpickled urbs model instance
    """
    import gzip
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    with gzip.GzipFile(filename, 'r') as file_handle:
        prob = pickle.load(file_handle)
    return prob


if __name__ == "__main__":
    # if executed as a script, run doctests on this module
    import doctest
    (failure_count, test_count) = doctest.testmod(report=True)
    passed_count = test_count - failure_count
    print('{} of {} tests passed.'.format(passed_count, test_count))
