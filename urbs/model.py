import math
import pyomo.core as pyomo
from datetime import datetime
from .modelhelper import *


def create_model(data, timesteps=None, dt=1, dual=False):
    """Create a pyomo ConcreteModel urbs object from given input data.

    Args:
        data: a dict of 6 DataFrames with the keys 'commodity', 'process',
            'transmission', 'storage', 'demand' and 'supim'.
        timesteps: optional list of timesteps, default: demand timeseries
        dt: timestep duration in hours (default: 1)
        dual: set True to add dual variables to model (slower); default: False

    Returns:
        a pyomo ConcreteModel object
    """
    m = pyomo.ConcreteModel()
    m.name = 'urbs'
    m.created = datetime.now().strftime('%Y%m%dT%H%M')
    m._data = data

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
    m.global_prop = data['global_prop'].drop('description', axis=1)
    m.site = data['site']
    m.commodity = data['commodity']
    m.process = data['process']
    m.process_commodity = data['process_commodity']
    m.transmission = data['transmission']
    m.storage = data['storage']
    m.demand = data['demand']
    m.supim = data['supim']
    m.buy_sell_price = data['buy_sell_price']
    m.timesteps = timesteps
    m.dsm = data['dsm']

    # process input/output ratios
    m.r_in = m.process_commodity.xs('In', level='Direction')['ratio']
    m.r_out = m.process_commodity.xs('Out', level='Direction')['ratio']
    m.r_in_dict = m.r_in.to_dict()
    m.r_out_dict = m.r_out.to_dict()

    # process areas
    m.proc_area = m.process['area-per-cap']
    m.sit_area = m.site['area']
    m.proc_area = m.proc_area[m.proc_area >= 0]
    m.sit_area = m.sit_area[m.sit_area >= 0]

    # input ratios for partial efficiencies
    # only keep those entries whose values are
    # a) positive and
    # b) numeric (implicitely, as NaN or NV compare false against 0)
    m.r_in_min_fraction = m.process_commodity.xs('In', level='Direction')
    m.r_in_min_fraction = m.r_in_min_fraction['ratio-min']
    m.r_in_min_fraction = m.r_in_min_fraction[m.r_in_min_fraction > 0]

    # output ratios for partial efficiencies
    # only keep those entries whose values are
    # a) positive and
    # b) numeric (implicitely, as NaN or NV compare false against 0)
    m.r_out_min_fraction = m.process_commodity.xs('Out', level='Direction')
    m.r_out_min_fraction = m.r_out_min_fraction['ratio-min']
    m.r_out_min_fraction = m.r_out_min_fraction[m.r_out_min_fraction > 0]

    # derive annuity factor from WACC and depreciation duration
    m.process['annuity-factor'] = annuity_factor(
        m.process['depreciation'],
        m.process['wacc'])
    m.transmission['annuity-factor'] = annuity_factor(
        m.transmission['depreciation'],
        m.transmission['wacc'])
    m.storage['annuity-factor'] = annuity_factor(
        m.storage['depreciation'],
        m.storage['wacc'])

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

    # modelled Demand Side Management time steps (downshift):
    # downshift effective in tt to compensate for upshift in t
    m.tt = pyomo.Set(
        within=m.t,
        initialize=m.timesteps[1:],
        ordered=True,
        doc='Set of additional DSM time steps')

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
        initialize=m.transmission.index.get_level_values('Transmission')
                                       .unique(),
        doc='Set of transmission technologies')

    # storage (e.g. hydrogen, pump storage)
    m.sto = pyomo.Set(
        initialize=m.storage.index.get_level_values('Storage').unique(),
        doc='Set of storage technologies')

    # cost_type
    m.cost_type = pyomo.Set(
        initialize=['Invest', 'Fixed', 'Variable', 'Fuel', 'Revenue',
                    'Purchase', 'Startup', 'Environmental'],
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
        doc='Combinations of possible transmissions, e.g. '
            '(South,Mid,hvac,Elec)')
    m.sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com,
        initialize=m.storage.index,
        doc='Combinations of possible storage by site, e.g. (Mid,Bat,Elec)')
    m.dsm_site_tuples = pyomo.Set(
        within=m.sit*m.com,
        initialize=m.dsm.index,
        doc='Combinations of possible dsm by site, e.g. (Mid, Elec)')
    m.dsm_down_tuples = pyomo.Set(
        within=m.tm*m.tm*m.sit*m.com,
        initialize=[(t, tt, site, commodity)
                    for (t, tt, site, commodity)
                    in dsm_down_time_tuples(m.timesteps[1:],
                                            m.dsm_site_tuples,
                                            m)],
        doc='Combinations of possible dsm_down combinations, e.g. '
            '(5001,5003,Mid,Elec)')

    # process tuples for area rule
    m.pro_area_tuples = pyomo.Set(
        within=m.sit*m.pro,
        initialize=m.proc_area.index,
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

    # process tuples for startup & partial feature
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
        initialize=float(8760) / (len(m.tm) * dt),
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
        doc='Use of sell commodity source (MW) per timestep')
    m.e_co_buy = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of buy commodity source (MW) per timestep')

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

    m.cap_online = pyomo.Var(
        m.t, m.pro_partial_tuples,
        within=pyomo.NonNegativeReals,
        doc='Online capacity (MW) of process per timestep')
    m.startup_pro = pyomo.Var(
        m.tm, m.pro_partial_tuples,
        within=pyomo.NonNegativeReals,
        doc='Started capacity (MW) of process per timestep')

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

    # demand side management
    m.dsm_up = pyomo.Var(
        m.tm, m.dsm_site_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM upshift')
    m.dsm_down = pyomo.Var(
        m.dsm_down_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM downshift')

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
        m.tm, m.pro_input_tuples - m.pro_partial_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')
    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples - m.pro_partial_output_tuples,
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
    m.res_process_maxgrad_lower = pyomo.Constraint(
        m.tm, m.pro_maxgrad_tuples,
        rule=res_process_maxgrad_lower_rule,
        doc='throughput may not decrease faster than maximal gradient')
    m.res_process_maxgrad_upper = pyomo.Constraint(
        m.tm, m.pro_maxgrad_tuples,
        rule=res_process_maxgrad_upper_rule,
        doc='throughput may not increase faster than maximal gradient')
    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

    m.res_area = pyomo.Constraint(
        m.sit,
        rule=res_area_rule,
        doc='used process area <= total process area')

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='power connection capacity must be symmetric in both directions')

    m.res_throughput_by_online_capacity_min = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_online_capacity_min_rule,
        doc='cap_online * min-fraction <= tau_pro')
    m.res_throughput_by_online_capacity_max = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_online_capacity_max_rule,
        doc='tau_pro <= cap_online')
    m.def_partial_process_input = pyomo.Constraint(
        m.tm, m.pro_partial_input_tuples,
        rule=def_partial_process_input_rule,
        doc='e_pro_in = '
            ' cap_online * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction)')
    m.def_partial_process_output = pyomo.Constraint(
        m.tm, m.pro_partial_output_tuples,
        rule=def_partial_process_output_rule,
        doc='e_pro_out = '
            ' cap_online * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction)')
    m.res_cap_online_by_cap_pro = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_cap_online_by_cap_pro_rule,
        doc='online capacity <= process capacity')
    m.def_startup_capacity = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=def_startup_capacity_rule,
        doc='startup_capacity[t] >= cap_online[t] - cap_online[t-1]')

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

    # costs
    m.def_costs = pyomo.Constraint(
        m.cost_type,
        rule=def_costs_rule,
        doc='main cost function by cost type')
    m.obj = pyomo.Objective(
        rule=obj_rule,
        sense=pyomo.minimize,
        doc='minimize(cost = sum of all cost types)')

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
            rule=res_global_co2_limit_rule,
            doc='total co2 commodity output <= Global CO2 limit')

    if dual:
        m.dual = pyomo.Suffix(direction=pyomo.Suffix.IMPORT)
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
    # if sit com is a dsm tuple, the power surplus is decreased by the
    # upshifted demand and increased by the downshifted demand.
    if (sit, com) in m.dsm_site_tuples:
        power_surplus -= m.dsm_up[tm, sit, com]
        power_surplus += sum(m.dsm_down[t, tm, sit, com]
                             for t in dsm_time_tuples(
                                 tm, m.timesteps[1:],
                                 m.dsm['delay'].loc[sit, com]))
    return power_surplus == 0

# demand side management (DSM) constraints


# DSMup == DSMdo * efficiency factor n
def def_dsm_variables_rule(m, tm, sit, com):
    dsm_down_sum = 0
    for tt in dsm_time_tuples(tm,
                              m.timesteps[1:],
                              m.dsm['delay'].loc[sit, com]):
        dsm_down_sum += m.dsm_down[tm, tt, sit, com]
    return dsm_down_sum == m.dsm_up[tm, sit, com] * m.dsm.loc[sit, com]['eff']


# DSMup <= Cup (threshold capacity of DSMup)
def res_dsm_upward_rule(m, tm, sit, com):
    return m.dsm_up[tm, sit, com] <= int(m.dsm.loc[sit, com]['cap-max-up'])


# DSMdo <= Cdo (threshold capacity of DSMdo)
def res_dsm_downward_rule(m, tm, sit, com):
    dsm_down_sum = 0
    for t in dsm_time_tuples(tm,
                             m.timesteps[1:],
                             m.dsm['delay'].loc[sit, com]):
        dsm_down_sum += m.dsm_down[t, tm, sit, com]
    return dsm_down_sum <= m.dsm.loc[sit, com]['cap-max-do']


# DSMup + DSMdo <= max(Cup,Cdo)
def res_dsm_maximum_rule(m, tm, sit, com):
    dsm_down_sum = 0
    for t in dsm_time_tuples(tm,
                             m.timesteps[1:],
                             m.dsm['delay'].loc[sit, com]):
        dsm_down_sum += m.dsm_down[t, tm, sit, com]

    max_dsm_limit = max(m.dsm.loc[sit, com]['cap-max-up'],
                        m.dsm.loc[sit, com]['cap-max-do'])
    return m.dsm_up[tm, sit, com] + dsm_down_sum <= max_dsm_limit


# DSMup(t, t + recovery time R) <= Cup * delay time L
def res_dsm_recovery_rule(m, tm, sit, com):
    dsm_up_sum = 0
    for t in dsm_recovery(tm,
                          m.timesteps[1:],
                          m.dsm['recov'].loc[sit, com]):
        dsm_up_sum += m.dsm_up[t, sit, com]
    return dsm_up_sum <= (m.dsm.loc[sit, com]['cap-max-up'] *
                          m.dsm['delay'].loc[sit, com])


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


def res_process_maxgrad_lower_rule(m, t, sit, pro):
    return (m.tau_pro[t-1, sit, pro] -
            m.cap_pro[sit, pro] * m.process.loc[sit, pro]['max-grad'] * m.dt <=
            m.tau_pro[t, sit, pro])


def res_process_maxgrad_upper_rule(m, t, sit, pro):
    return (m.tau_pro[t-1, sit, pro] +
            m.cap_pro[sit, pro] * m.process.loc[sit, pro]['max-grad'] * m.dt >=
            m.tau_pro[t, sit, pro])


def res_throughput_by_online_capacity_min_rule(m, tm, sit, pro):
    return (m.tau_pro[tm, sit, pro] >=
            m.cap_online[tm, sit, pro] *
            m.process.loc[sit, pro]['min-fraction'])


def res_throughput_by_online_capacity_max_rule(m, tm, sit, pro):
    return (m.tau_pro[tm, sit, pro] <= m.cap_online[tm, sit, pro])


def def_partial_process_input_rule(m, tm, sit, pro, coin):
    R = m.r_in.loc[pro, coin]  # input ratio at maximum operation point
    r = m.r_in_min_fraction[pro, coin]  # input ratio at lowest operation point
    min_fraction = m.process.loc[sit, pro]['min-fraction']

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)

    return (m.e_pro_in[tm, sit, pro, coin] ==
            m.cap_online[tm, sit, pro] * online_factor +
            m.tau_pro[tm, sit, pro] * throughput_factor)


def def_partial_process_output_rule(m, tm, sit, pro, coo):
    R = m.r_out.loc[pro, coo]  # input ratio at maximum operation point
    r = m.r_out_min_fraction[pro, coo]  # input ratio at lowest operation point
    min_fraction = m.process.loc[sit, pro]['min-fraction']

    online_factor = min_fraction * (r - R) / (1 - min_fraction)
    throughput_factor = (R - min_fraction * r) / (1 - min_fraction)

    return (m.e_pro_out[tm, sit, pro, coo] ==
            m.cap_online[tm, sit, pro] * online_factor +
            m.tau_pro[tm, sit, pro] * throughput_factor)


def res_cap_online_by_cap_pro_rule(m, tm, sit, pro):
    return m.cap_online[tm, sit, pro] <= m.cap_pro[sit, pro]


def def_startup_capacity_rule(m, tm, sit, pro):
    return (m.startup_pro[tm, sit, pro] >=
            m.cap_online[tm, sit, pro] -
            m.cap_online[tm-1, sit, pro])


# lower bound <= process capacity <= upper bound
def res_process_capacity_rule(m, sit, pro):
    return (m.process.loc[sit, pro]['cap-lo'],
            m.cap_pro[sit, pro],
            m.process.loc[sit, pro]['cap-up'])


# used process area <= maximal process area
def res_area_rule(m, sit):
    if m.site.loc[sit]['area'] >= 0 and sum(
                         m.process.loc[(s, p), 'area-per-cap']
                         for (s, p) in m.pro_area_tuples
                         if s == sit) > 0:
        total_area = sum(m.cap_pro[s, p] *
                         m.process.loc[(s, p), 'area-per-cap']
                         for (s, p) in m.pro_area_tuples
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
            return (m.cap_pro[sit_in, pro_in] == m.cap_pro[sit_in, sell_pro])
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

# storage content in timestep [t] == storage content[t-1] * (1-discharge)
# + newly stored energy * input efficiency
# - retrieved energy / output efficiency
def def_storage_state_rule(m, t, sit, sto, com):
    return (m.e_sto_con[t, sit, sto, com] ==
            m.e_sto_con[t-1, sit, sto, com] *
            (1 - m.storage.loc[sit, sto, com]['discharge']) +
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


# total CO2 output <= Global CO2 limit
def res_global_co2_limit_rule(m):
    if math.isinf(m.global_prop.loc['CO2 limit', 'value']):
        return pyomo.Constraint.Skip
    elif m.global_prop.loc['CO2 limit', 'value'] > 0:
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
    if cost_type == 'Invest':
        return m.costs[cost_type] == \
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

    elif cost_type == 'Fixed':
        return m.costs[cost_type] == \
            sum(m.cap_pro[p] * m.process.loc[p]['fix-cost']
                for p in m.pro_tuples) + \
            sum(m.cap_tra[t] * m.transmission.loc[t]['fix-cost']
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p[s] * m.storage.loc[s]['fix-cost-p'] +
                m.cap_sto_c[s] * m.storage.loc[s]['fix-cost-c']
                for s in m.sto_tuples)

    elif cost_type == 'Variable':
        return m.costs[cost_type] == \
            sum(m.tau_pro[(tm,) + p] * m.dt *
                m.process.loc[p]['var-cost'] *
                m.weight
                for tm in m.tm
                for p in m.pro_tuples) + \
            sum(m.e_tra_in[(tm,) + t] * m.dt *
                m.transmission.loc[t]['var-cost'] *
                m.weight
                for tm in m.tm
                for t in m.tra_tuples) + \
            sum(m.e_sto_con[(tm,) + s] *
                m.storage.loc[s]['var-cost-c'] * m.weight +
                (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) * m.dt *
                m.storage.loc[s]['var-cost-p'] * m.weight
                for tm in m.tm
                for s in m.sto_tuples)

    elif cost_type == 'Fuel':
        return m.costs[cost_type] == sum(
            m.e_co_stock[(tm,) + c] * m.dt *
            m.commodity.loc[c]['price'] *
            m.weight
            for tm in m.tm for c in m.com_tuples
            if c[1] in m.com_stock)

    elif cost_type == 'Revenue':
        sell_tuples = commodity_subset(m.com_tuples, m.com_sell)

        return m.costs[cost_type] == -sum(
            m.e_co_sell[(tm,) + c] *
            m.buy_sell_price.loc[tm][c[1]] *
            m.commodity.loc[c]['price'] *
            m.weight * m.dt
            for tm in m.tm
            for c in sell_tuples)

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)

        return m.costs[cost_type] == sum(
            m.e_co_buy[(tm,) + c] *
            m.buy_sell_price.loc[tm][c[1]] *
            m.commodity.loc[c]['price'] *
            m.weight * m.dt
            for tm in m.tm
            for c in buy_tuples)

    elif cost_type == 'Startup':
        return m.costs[cost_type] == sum(
            m.startup_pro[(tm,) + p] *
            m.process.loc[p]['startup-cost'] *
            m.weight * m.dt
            for tm in m.tm
            for p in m.pro_partial_tuples)

    elif cost_type == 'Environmental':
        return m.costs[cost_type] == sum(
            - commodity_balance(m, tm, sit, com) *
            m.weight * m.dt *
            m.commodity.loc[sit, com, com_type]['price']
            for tm in m.tm
            for sit, com, com_type in m.com_tuples
            if com in m.com_env)

    else:
        raise NotImplementedError("Unknown cost type.")


def obj_rule(m):
    return pyomo.summation(m.costs)
