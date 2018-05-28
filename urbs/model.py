import math
import pyomo.core as pyomo
from datetime import datetime
from .modelhelper import *
from .input import *


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

    # Optional
    if not timesteps:
        timesteps = data['demand'].index.tolist()

    m = pyomo_model_prep(data, timesteps)  # preparing pyomo model
    m.name = 'urbs'
    m.created = datetime.now().strftime('%Y%m%dT%H%M')
    m._data = data

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
        doc='Set of modelled timesteps within each stf')

    # modelled Demand Side Management time steps (downshift):
    # downshift effective in tt to compensate for upshift in t
    m.tt = pyomo.Set(
        within=m.t,
        initialize=m.timesteps[1:],
        ordered=True,
        doc='Set of additional DSM time steps')

    # support timeframes (e.g. 2020, 2030...)
    m.stf = pyomo.Set(
        initialize=(m.commodity.index.get_level_values('support_timeframe')
                    .unique()),
        doc='Set of modeled support timeframes (e.g. years)')

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
                    'Purchase', 'Environmental'],
        doc='Set of cost types (hard-coded)')

    # tuple sets
    m.sit_tuples = pyomo.Set(
        within=m.stf*m.sit,
        initialize=m.site.index,
        doc='Combinations of support imeframes and sites')
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
        m.sit_tuples,
        rule=res_area_rule,
        doc='used process area <= total process area')

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='power connection capacity must be symmetric in both directions')

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

    # costs
    m.def_costs = pyomo.Constraint(
        m.cost_type,
        rule=def_costs_rule,
        doc='main cost function by cost type')
    m.obj = pyomo.Objective(
        rule=obj_rule,
        sense=pyomo.minimize,
        doc='minimize(cost = sum of all cost types)')

    if dual:
        m.dual = pyomo.Suffix(direction=pyomo.Suffix.IMPORT)
    return m


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


# Objective
def def_costs_rule(m, cost_type):
    """Calculate total costs by cost type.

    Sums up process activity and capacity expansions
    and sums them in the cost types that are specified in the set
    m.cost_type. To change or add cost types, add/change entries
    there and modify the if/elif cases in this function accordingly.

    Cost types are
      - Investment costs for process power, storage power and
        storage capacity. They are multiplied by the investment
        factors. Rest values of units are subtracted.
      - Fixed costs for process power, storage power and storage
        capacity.
      - Variables costs for usage of processes, storage and transmission.
      - Fuel costs for stock commodity purchase.

    """
    if cost_type == 'Invest':
        return m.costs[cost_type] == \
            sum(m.cap_pro_new[p] *
                m.process_dict['inv-cost'][p] *
                m.process_dict['invcost-factor'][p]
                for p in m.pro_tuples) + \
            sum(m.cap_tra_new[t] *
                m.transmission_dict['inv-cost'][t] *
                m.transmission_dict['invcost-factor'][t]
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p_new[s] *
                m.storage_dict['inv-cost-p'][s] *
                m.storage_dict['invcost-factor'][s] +
                m.cap_sto_c_new[s] *
                m.storage_dict['inv-cost-c'][s] *
                m.storage_dict['invcost-factor'][s]
                for s in m.sto_tuples) - \
            sum(m.process_dict['inv-cost'][p] *
                m.process_dict['rv-factor'][p]
                for p in m.pro_tuples) + \
            sum(m.cap_tra_new[t] *
                m.transmission_dict['inv-cost'][t] *
                m.transmission_dict['rv-factor'][t]
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p_new[s] *
                m.storage_dict['inv-cost-p'][s] *
                m.storage_dict['rv-factor'][s] +
                m.cap_sto_c_new[s] *
                m.storage_dict['inv-cost-c'][s] *
                m.storage_dict['rv-factor'][s]
                for s in m.sto_tuples)

    elif cost_type == 'Fixed':
        return m.costs[cost_type] == \
            sum(m.cap_pro[p] * m.process_dict['fix-cost'][p] *
                m.process_dict['cost_factor'][p]
                for p in m.pro_tuples) + \
            sum(m.cap_tra[t] * m.transmission_dict['fix-cost'][t] *
                m.transmission_dict['cost_factor'][t]
                for t in m.tra_tuples) + \
            sum((m.cap_sto_p[s] * m.storage_dict['fix-cost-p'][s] +
                m.cap_sto_c[s] * m.storage_dict['fix-cost-c'][s]) *
                m.storage_dict['cost_factor'][s]
                for s in m.sto_tuples)

    elif cost_type == 'Variable':
        return m.costs[cost_type] == \
            sum(m.tau_pro[(tm,) + p] * m.dt * m.weight *
                m.process_dict['var-cost'][p] *
                m.process_dict['cost_factor'][p]
                for tm in m.tm
                for p in m.pro_tuples) + \
            sum(m.e_tra_in[(tm,) + t] * m.dt * m.weight *
                m.transmission_dict['var-cost'][t] *
                m.transmission_dict['cost_factor'][t]
                for tm in m.tm
                for t in m.tra_tuples) + \
            sum(m.e_sto_con[(tm,) + s] * m.weight *
                m.storage_dict['var-cost-c'][s] *
                m.storage_dict['cost_factor'][s] +
                (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) * m.dt *
                m.weight * m.storage_dict['var-cost-p'][s] *
                m.storage_dict['cost_factor'][s]
                for tm in m.tm
                for s in m.sto_tuples)

    elif cost_type == 'Fuel':
        return m.costs[cost_type] == sum(
            m.e_co_stock[(tm,) + c] * m.dt * m.weight *
            m.commodity_dict['price'][c] *
            m.commodity_dict['cost_factor'][c]
            for tm in m.tm for c in m.com_tuples
            if c[2] in m.com_stock)

    elif cost_type == 'Revenue':
        sell_tuples = commodity_subset(m.com_tuples, m.com_sell)

        return m.costs[cost_type] == -sum(
            m.e_co_sell[(tm,) + c] *
            m.buy_sell_price_dict[c[2]][(c[0], tm)] * m.weight * m.dt *
            m.commodity_dict['price'][c] *
            m.commodity_dict['cost_factor'][c]
            for tm in m.tm
            for c in sell_tuples)

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)

        return m.costs[cost_type] == sum(
            m.e_co_buy[(tm,) + c] *
            m.buy_sell_price_dict[c[2]][(c[0], tm)] * m.weight * m.dt *
            m.commodity_dict['price'][c] *
            m.commodity_dict['cost_factor'][c]
            for tm in m.tm
            for c in buy_tuples)

    elif cost_type == 'Environmental':
        return m.costs[cost_type] == sum(
            - commodity_balance(m, tm, stf, sit, com) * m.weight * m.dt *
            m.commodity_dict['price'][(stf, sit, com, com_type)] *
            m.commodity_dict['cost_factor'][(stf, sit, com, com_type)]
            for tm in m.tm
            for stf, sit, com, com_type in m.com_tuples
            if com in m.com_env)

    else:
        raise NotImplementedError("Unknown cost type.")


def obj_rule(m):
    return pyomo.summation(m.costs)
