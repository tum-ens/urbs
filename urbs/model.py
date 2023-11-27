import math
from datetime import datetime
from .features import *
from .features.transmission import *
from .input import *
import pyomo.environ as pyomo
import numpy as np
import math
import sys
import pdb

class ForkedPdb(pdb.Pdb):
    """A Pdb subclass that may be used
    from a forked multiprocessing child

    """
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

def create_model(data, dt=1, timesteps=None, objective='cost', hoursPerPeriod=None, weighting_order=None,
                 assumelowq=True, dual=True, grid_plan_model=False, bui_react_model=False, flexible_heat=True):
    """Create a pyomo ConcreteModel urbs object from given input data.

    Args:
        - data: a dict of up to 12
        - dt: timestep duration in hours (default: 1)m.gri
        - timesteps: optional list of timesteps, default: demand timeseries
        - objective: Either "cost" or "CO2" for choice of objective function,
          default: "cost"
        - dual: set True to add dual variables to model output
          (marginally slower), default: True

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
    m.grid_plan_model = grid_plan_model
    # Parameters

    # weight = length of year (hours) / length of simulation (hours)
    # weight scales costs and emissions from length of simulation to a full
    # year, making comparisons among cost types (invest is annualized, fixed
    # costs are annual by default, variable costs are scaled by weight) and
    # among different simulation durations meaningful.
    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.timesteps) - 1 * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')

    # dt = spacing between timesteps. Required for storage equation that
    # converts between energy (storage content, e_sto_con) and power (all other
    # quantities that start with "e_")
    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')

    # import objective function information
    m.obj = pyomo.Param(
        initialize=objective,
        within=pyomo.Any,
        doc='Specification of minimized quantity, default: "cost"')

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
    if m.mode['evu_sperre']:
        m.day = pyomo.Set(
            initialize=range(1, int(len(m.timesteps[1:]) / 24 + 1)),
            ordered=True,
            doc='Set of days')
        m.tm_sperrzeit = pyomo.Set(
            within=m.t,
            initialize=m.timesteps[1:-2],
            ordered=True,
            doc='Set of timesteps where the sperrzeit constraint is defined ')

    # support timeframes (e.g. 2020, 2030...)
    indexlist = set()
    for key in m.commodity_dict["price"]:
        indexlist.add(tuple(key)[0])
    m.stf = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of modeled support timeframes (e.g. years)')

    # site (e.g. north, middle, south...)
    indexlist = set()
    for key in m.commodity_dict["price"]:
        indexlist.add(tuple(key)[1])
    m.sit = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of sites')

    # commodity (e.g. solar, wind, coal...)
    indexlist = set()
    for key in m.commodity_dict["price"]:
        indexlist.add(tuple(key)[2])
    m.com = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of commodities')

    # commodity type (i.e. SupIm, Demand, Stock, Env)
    indexlist = set()
    for key in m.commodity_dict["price"]:
        indexlist.add(tuple(key)[3])
    m.com_type = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of commodity types')

    # process (e.g. Wind turbine, Gas plant, Photovoltaics...)
    indexlist = set()
    for key in m.process_dict["inv-cost"]:
        indexlist.add(tuple(key)[2])
    m.pro = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of conversion processes')

    # cost_type
    m.cost_type = pyomo.Set(
        initialize=m.cost_type_list,
        doc='Set of cost types (hard-coded)')

    # tuple sets
    m.sit_tuples = pyomo.Set(
        within=m.stf * m.sit,
        initialize=tuple(m.site_dict["area"].keys()),
        doc='Combinations of support timeframes and sites')

    # tuple sets relevant for ac rules
    m.sit_tuples_ac = pyomo.Set(
        within=m.stf * m.sit,
        initialize=[(stf, site)
                    for (stf, site) in m.sit_tuples
                    if m.site_dict['min-voltage'][(stf, site)] > 0],
        doc='Combinations of support timeframes and sites with ac characteristics')
    m.sit_slackbus = pyomo.Set(
        within=m.stf * m.sit,
        initialize=[(stf, site)
                    for (stf, site) in m.sit_tuples
                    if m.site_dict['ref-node'][(stf, site)] == 1],
        doc='Set of all reference nodes in defined microgrids')
    if m.mode['power_price']:
        m.sit_power_price_tuples = pyomo.Set(
            within=m.stf * m.sit,
            initialize=[(stf, site)
                        for (stf, site) in m.sit_tuples
                        if m.site_dict['power_price_kw'][(stf, site)] > 0],
            doc='Combinations of support timeframes and sites with retail power price')

    if m.mode['uhp']:
        m.sit_temperature_tuples = pyomo.Set(
            within=m.stf * m.sit,
            initialize=[(stf, site)
                        for (stf, site) in m.sit_tuples
                        if not math.isnan(m.site_dict['U'][(stf, site)])],
            doc='Combinations of support timeframes and sites with U, V, C values')

    m.com_tuples = pyomo.Set(
        within=m.stf * m.sit * m.com * m.com_type,
        initialize=tuple(m.commodity_dict["price"].keys()),
        doc='Combinations of defined commodities, e.g. (2018,Mid,Elec,Demand)')
    m.pro_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=tuple(m.process_dict["inv-cost"].keys()),
        doc='Combinations of possible processes, e.g. (2018,North,Coal plant)')
    m.com_stock = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Stock'),
        ordered=False,
        doc='Commodities that can be purchased at some site(s)')

    if m.mode['int']:
        # tuples for operational status of technologies
        m.operational_pro_tuples = pyomo.Set(
            within=m.sit * m.pro * m.stf * m.stf,
            initialize=[(sit, pro, stf, stf_later)
                        for (sit, pro, stf, stf_later)
                        in op_pro_tuples(m.pro_tuples, m)],
            doc='Processes that are still operational through stf_later'
                '(and the relevant years following), if built in stf'
                'in stf.')

        # tuples for rest lifetime of installed capacities of technologies
        m.inst_pro_tuples = pyomo.Set(
            within=m.sit * m.pro * m.stf,
            initialize=[(sit, pro, stf)
                        for (sit, pro, stf)
                        in inst_pro_tuples(m)],
            doc='Installed processes that are still operational through stf')

    # commodity type subsets
    m.com_supim = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'SupIm'),
        ordered=False,
        doc='Commodities that have intermittent (timeseries) input')
    m.com_demand = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Demand'),
        ordered=False,
        doc='Commodities that have a demand (implies timeseries)')
    m.com_env = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Env'),
        ordered=False,
        doc='Commodities that (might) have a maximum creation limit')

    # process tuples for area rule
    m.pro_area_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=tuple(m.proc_area_dict.keys()),
        doc='Processes and Sites with area Restriction')
    # process tuples for building in blocks rule
    m.pro_cap_new_block_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=[(stf, site, process)
                    for (stf, site, process) in m.pro_tuples
                    for (s, si, pro) in tuple(m.cap_block_dict.keys())
                    if process == pro and si == site and s == stf],
        doc='Processes with new capacities built in blocks')
    m.pro_inv_cost_fix_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=[(stf, site, process)
                    for (stf, site, process) in m.pro_tuples
                    for (s, si, pro) in tuple(m.pro_inv_cost_fix_dict.keys())
                    if process == pro and si == site and s == stf],
        doc='Processes with fixed investment cost portions')
    # process input/output
    m.pro_input_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro * m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in tuple(m.r_in_dict.keys())
                    if process == pro and s == stf],
        doc='Commodities consumed by process by site,'
            'e.g. (2020,Mid,PV,Solar)')

    m.pro_output_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro * m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in tuple(m.r_out_dict.keys())
                    if process == pro and s == stf],
        doc='Commodities produced by process by site, e.g. (2020,Mid,PV,Elec)')

    m.pro_output_tuples_reactive = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=[(stf, site, process)
                    for (stf, site, process) in m.pro_tuples
                    if m.process_dict['pf-min'][(stf, site, process)] > 0],
        doc='Elec-Reactive produced by process by site, e.g. (2020, node1, PV_private, Elec-Reactive)')

    # process tuples for maximum gradient feature
    m.pro_rampupgrad_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=[(stf, sit, pro)
                    for (stf, sit, pro) in m.pro_tuples
                    if m.process_dict['ramp-up-grad'][stf, sit, pro] < 1.0 / dt],
        doc='Processes with maximum ramp up gradient smaller than timestep length')
    m.pro_rampdowngrad_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=[(stf, sit, pro)
                    for (stf, sit, pro) in m.pro_tuples
                    if m.process_dict['ramp-down-grad'][stf, sit, pro] < 1.0 / dt],
        doc='Processes with maximum ramp down gradient smaller than timestep length')

    # process tuples for decommissioning feature
    m.pro_decommissionable_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=[(stf, sit, pro)
                    for (stf, sit, pro) in m.pro_tuples
                    if m.process_dict['decommissionable'][stf, sit, pro] == 1],
        doc='Processes which can be decommissioned')

    if m.mode['evu_sperre']:
        m.hp_lock_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            initialize=[(stf, sit, pro)
                        for (stf, sit, pro) in m.pro_tuples
                        if 'hp_lock' in pro],
            doc='Heat pump processes which compensate for heatpump_air_heizstrom whenever the sperrzeit is applied')

        m.sit_multi_heatpump_tuples = pyomo.Set(
            within=m.stf * m.sit,
            initialize=[(stf, sit) for (stf, sit) in m.sit_tuples
                        if len([pro for (st, si, pro) in m.pro_tuples
                               if pro.startswith('heatpump') and st == stf and si == sit]) > 1],
            doc='Sites where multiple heat pumps are defined (required for the rule "res_single_heatpump", only if '
                'evu_sperre)')

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

    # site
    if m.mode['power_price']:
        m.peak_injection = pyomo.Var(m.sit_power_price_tuples,
                                     within=pyomo.NonNegativeReals,
                                     doc='Peak injection/feed-in in site')
        m.abs_injection = pyomo.Var(m.tm, m.sit_power_price_tuples,
                                    within=pyomo.NonNegativeReals,
                                    doc='Absolute injection/feed-in in site')

    if m.mode['uhp']:
        m.temperature = pyomo.Var(m.t, m.sit_temperature_tuples,
                                     within=pyomo.Reals,
                                     doc='Temperature in building')

        m.temperature_slack = pyomo.Var(m.t, m.sit_temperature_tuples,
                                         within=pyomo.NonNegativeReals,
                                         doc='Temperature slack in building')
    # process
    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')
    m.cap_decommissioned = pyomo.Var(
        m.pro_decommissionable_tuples,
        within=pyomo.NonNegativeReals,
        doc='Decommissioned process capacity (MW)')
    # process capacity as expression object
    # (variable if expansion is possible, else static)
    m.cap_pro = pyomo.Expression(
        m.pro_tuples,
        rule=def_process_capacity_rule,
        doc='total process capacity')

    m.tau_pro = pyomo.Var(
        m.t, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow (MW) through process')
    m.e_pro_in = pyomo.Var(
        m.tm, m.pro_input_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow of commodity into process (MW) per timestep')
    m.e_pro_out = pyomo.Var(
        m.tm, m.pro_output_tuples,
        within=pyomo.Reals,
        doc='Power flow out of process (MW) per timestep')

    # process new capacity expansion unit
    m.pro_cap_unit = pyomo.Var(
        m.pro_cap_new_block_tuples,
        within=pyomo.NonNegativeIntegers,
        doc='Number of newly installed capacity units')

    # process new capacity expansion boolean
    m.pro_cap_expands = pyomo.Var(
        m.pro_inv_cost_fix_tuples,
        within=pyomo.Boolean,
        doc='Boolean variable whether a process is expanded')
    # debug

    # Add additional features
    # called features are declared in distinct files in features folder
    if m.mode['tra']:
        if m.mode['acpf']:
            m = add_transmission_ac(m, assumelowq)
        elif m.mode['dcpf']:
            m = add_transmission_dc(m)
        else:
            m = add_transmission(m)
    if m.mode['sto']:
        m = add_storage(m)
    if m.mode['dsm']:
        m = add_dsm(m)
    if m.mode['bsp']:
        m = add_buy_sell_price(m)
    if m.mode['tdy']:
        if m.mode['tsam']:
            store_typeperiod_parameter(m, hoursPerPeriod, weighting_order)

        m = add_typeperiod(m, hoursPerPeriod)

    if (m.mode['tve'] or m.mode['onoff'] or  m.mode['ava'] or m.mode['minfraction']):
        m = add_advanced_processes(m)
    else:
        m.pro_timevar_output_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro * m.com,
            doc='empty set needed for (partial) process output')
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
        m.pro_start_up_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc='Processes with fix start up costs')
        m.pro_rampup_start_tuples = pyomo.Set(
            within=m.stf * m.sit * m.pro,
            doc='Processes with different starting ramp up gradient')
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
    m.res_env_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_env_step_rule,
        doc='environmental output per step <= commodity.maxperstep')
    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

    # process
    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples - m.pro_partial_input_tuples -
              m.pro_on_off_input_tuples - m.pro_partial_on_off_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')
    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples - m.pro_partial_output_tuples -
              m.pro_on_off_output_tuples - m.pro_partial_on_off_output_tuples -
              m.pro_timevar_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

    # upper reactive power generation limit
    m.def_process_output_reactive1 = pyomo.Constraint(
        m.tm, m.pro_output_tuples_reactive,
        rule=def_process_output_reactive_rule1,
        doc='Q <= P * tan(phi_min)')

    # lower reactive power generation limit
    m.def_process_output_reactive2 = pyomo.Constraint(
        m.tm, m.pro_output_tuples_reactive,
        rule=def_process_output_reactive_rule2,
        doc='Q >= -tan(phi_min)')

    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')
    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples - m.pro_on_off_tuples - m.pro_partial_on_off_tuples - m.pro_availability_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')

    m.res_process_rampdown = pyomo.Constraint(
        m.tm, m.pro_rampdowngrad_tuples,
        rule=res_process_rampdown_rule,
        doc='throughput may not decrease faster than maximal ramp down gradient')
    m.res_process_ramp_up = pyomo.Constraint(
        m.tm, m.pro_rampupgrad_tuples,  # - m.pro_rampup_start_tuples,
        rule=res_process_rampup_rule,
        doc='throughput may not increase faster than maximal ramp up gradient')

    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

    # capacity limitation for the fix investment cost processes
    m.res_process_capacity_fixed_inv_cost_lower = pyomo.Constraint(
        m.pro_inv_cost_fix_tuples,
        rule=res_process_capacity_fixed_inv_cost_lower_rule,
        doc='pro_cap_expands * process.cap-lo <= new process capacity')
    m.res_process_capacity_fixed_inv_cost_upper = pyomo.Constraint(
        m.pro_inv_cost_fix_tuples,
        rule=res_process_capacity_fixed_inv_cost_upper_rule,
        doc='new process capacity <= pro_cap_expands * process.cap-up')

    m.res_area = pyomo.Constraint(
        m.sit_tuples,
        rule=res_area_rule,
        doc='used process area <= total process area')

    # build new capacities in blocks
    m.def_new_capacity_units = pyomo.Constraint(
        m.pro_cap_new_block_tuples,
        rule=def_new_capacity_units_rule,
        doc='cap_pro_new = pro_cap_unit * cap-block')

    if m.mode['power_price']:
        if not grid_plan_model:
            m.def_abs_injection_1 = pyomo.Constraint(
                m.tm, m.sit_power_price_tuples,
                rule=def_abs_injection_1_rule,
                doc='injection <= abs(injection)')
            m.def_abs_injection_2 = pyomo.Constraint(
                m.tm, m.sit_power_price_tuples,
                rule=def_abs_injection_2_rule,
                doc='-injection <= abs(injection)')
            m.def_peak_injection = pyomo.Constraint(
                m.tm, m.sit_power_price_tuples,
                rule=def_peak_injection_rule,
                doc='-abs(injection) <= peak(injection)')

    if m.mode['evu_sperre']:
        if grid_plan_model:
            m.def_evu_sperre_daily_limit = pyomo.Constraint(m.day, m.hp_lock_tuples,
                                                           rule=def_evu_sperre_hourly_limit_rule,
                                                           doc='Sperrzeit not more than 6 hours per day')
            m.def_evu_sperre_hourly_limit = pyomo.Constraint(m.tm_sperrzeit, m.hp_lock_tuples,
                                                            rule=def_evu_sperre_hourly_limit_rule,
                                                            doc='Sperrzeit not more than 2 hour per time, and pause after')

        m.res_single_heatpump = pyomo.Constraint(m.sit_multi_heatpump_tuples, rule=res_single_heatpump_rule,
                                                 doc='Only one type of heatpump in each building')

    if m.mode['uhp']:
        if bui_react_model:
            m.res_temperature_min = pyomo.Constraint(
                m.tm, m.sit_temperature_tuples,
                rule=res_temperature_min_slack_rule,
                doc='building temperature >= set temperature - slack')
        else:
            m.res_temperature_min = pyomo.Constraint(
                m.tm, m.sit_temperature_tuples,
                rule=res_temperature_min_rule,
                doc='building temperature >= set temperature')
        if flexible_heat:
            m.res_temperature_max = pyomo.Constraint(
                m.tm, m.sit_temperature_tuples,
                rule=res_temperature_max_rule,
            doc='building temperature <= max temperature')
        else:
            m.res_temperature_fix = pyomo.Constraint(
                m.tm, m.sit_temperature_tuples,
                rule=res_temperature_fix_rule,
                doc='building temperature <= min temperature')
        m.def_initial_temperature = pyomo.Constraint(m.sit_temperature_tuples,
                                                     rule=def_initial_temperature_rule)
        #if m.mode['tsam']:
        #    m.def_startofperiod_temperature = pyomo.Constraint(m.t_startofperiod, m.sit_temperature_tuples,
        #                                                 rule=def_startofperiod_temperature_rule)

    # if m.mode['int']:
    #     m.res_global_co2_limit = pyomo.Constraint(
    #         m.stf,
    #         rule=res_global_co2_limit_rule,
    #         doc='total co2 commodity output <= global.prop CO2 limit')

    # costs
    m.def_costs = pyomo.Constraint(
        m.cost_type,
        rule=def_costs_rule,
        doc='main cost function by cost type')

    # objective and global constraints
    if m.obj.value == 'cost':
        m.res_global_co2_limit = pyomo.Constraint(
            m.stf,
            rule=res_global_co2_limit_rule,
            doc='total co2 commodity output <= Global CO2 limit')

        if m.mode['int']:
            m.res_global_co2_budget = pyomo.Constraint(
                rule=res_global_co2_budget_rule,
                doc='total co2 commodity output <= global.prop CO2 budget')

            m.res_global_cost_limit = pyomo.Constraint(
                m.stf,
                rule=res_global_cost_limit_rule,
                doc='total costs <= Global cost limit')

        m.objective_function = pyomo.Objective(
            rule=cost_rule,
            sense=pyomo.minimize,
            doc='minimize(cost = sum of all cost types)')

    elif m.obj.value == 'CO2':

        m.res_global_cost_limit = pyomo.Constraint(
            m.stf,
            rule=res_global_cost_limit_rule,
            doc='total costs <= Global cost limit')
        if m.mode['int']:
            m.res_global_cost_budget = pyomo.Constraint(
                rule=res_global_cost_budget_rule,
                doc='total costs <= global.prop Cost budget')
            m.res_global_co2_limit = pyomo.Constraint(
                m.stf,
                rule=res_global_co2_limit_rule,
                doc='total co2 commodity output <= Global CO2 limit')

        m.objective_function = pyomo.Objective(
            rule=co2_rule,
            sense=pyomo.minimize,
            doc='minimize total CO2 emissions')

    else:
        raise NotImplementedError("Non-implemented objective quantity. Set "
                                  "either 'cost' or 'CO2' as the objective in "
                                  "run_ms.py!")

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
    if (com in m.com_stock) or (com in m.com_demand):
        power_surplus += m.e_co_stock[tm, stf, sit, com, com_type]

    # if Buy and sell prices are enabled
    if m.mode['bsp']:
        power_surplus += bsp_surplus(m, tm, stf, sit, com, com_type)

    # if com is a demand commodity, the power_surplus is reduced by the
    # demand value; no scaling by m.dt or m.weight is needed here, as this
    # constraint is about power (MW), not energy (MWh)
    if com in m.com_demand:
        try:
            power_surplus -= m.demand_dict[(sit, com)][(stf, tm)]
        except KeyError:
            pass

    if m.mode['dsm']:
        power_surplus += dsm_surplus(m, tm, stf, sit, com)

    if m.mode['uhp'] and com == 'space_heat':
        if (stf, sit) in m.sit_temperature_tuples:
            if m.mode['tsam'] and tm in m.t_startofperiod:
                return m.temperature[(tm, stf, sit)] == (m.uhp_dict[(sit, 'Tmin')][(stf, tm)])# +
                                                          #m.uhp_dict[(sit, 'Tmax')][(stf, tm)]) / 2
            else:
                try:
                    power_surplus +=   (m.uhp_dict[(sit, 'sol_gains')][(stf, tm)]
                                    + m.uhp_dict[(sit, 'int_gains')][(stf, tm)]
                                    - m.site_dict['C'][(stf, sit)] / (m.dt * 3600) * (m.temperature[tm, stf, sit] - m.temperature[tm-1, stf, sit])
                                    - ((m.site_dict['U'][(stf, sit)] + m.site_dict['V'][(stf, sit)])
                                       * (m.temperature[tm, stf, sit] - m.uhp_dict[('ambient', 'Tamb')][(stf, tm)] )) * m.dt
                                    )
                except:
                    import pdb;pdb.set_trace()
    return power_surplus == 0


# stock commodity purchase == commodity consumption, according to
# commodity_balance of current (time step, site, commodity);
# limit stock commodity use per time step


def res_stock_step_rule(m, tm, stf, sit, com, com_type):
    if (com not in m.com_stock) and (com not in m.com_demand):
        return pyomo.Constraint.Skip
    else:
        return (m.e_co_stock[tm, stf, sit, com, com_type] <=
                m.dt * m.commodity_dict['maxperhour']
                [(stf, sit, com, com_type)])


# limit stock commodity use in total (scaled to annual consumption, thanks
# to m.weight)
def res_stock_total_rule(m, stf, sit, com, com_type):
    if (com not in m.com_stock) and (com not in m.com_demand):
        return pyomo.Constraint.Skip
    else:
        # calculate total consumption of commodity com
        total_consumption = 0
        for tm in m.tm:
            total_consumption += (
                    m.e_co_stock[tm, stf, sit, com, com_type] * m.typeperiod['weight_typeperiod'][(stf, tm)])
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
                m.dt * m.commodity_dict['maxperhour']
                [(stf, sit, com, com_type)])


# limit environmental commodity output in total (scaled to annual
# emissions, thanks to m.weight)
def res_env_total_rule(m, stf, sit, com, com_type):
    if com not in m.com_env:
        return pyomo.Constraint.Skip
    else:
        # calculate total creation of environmental commodity com
        env_output_sum = 0
        for tm in m.tm:
            env_output_sum += (- commodity_balance(m, tm, stf, sit, com) * m.typeperiod['weight_typeperiod'][(stf, tm)])
        env_output_sum *= m.weight
        return (env_output_sum <=
                m.commodity_dict['max'][(stf, sit, com, com_type)])


# process
# process capacity (for m.cap_pro Expression)
def def_process_capacity_rule(m, stf, sit, pro):
    if m.mode['int']:  # operational mode of function
        if (sit, pro, stf) in m.inst_pro_tuples:  # if this is an existing process
            # if (sit, pro, min(m.stf)) in m.pro_const_cap_dict:  # if no expansion is possible/allowed -> cap=initial cap
            if 0:  # if no expansion is possible/allowed -> cap=initial cap
                cap_pro = m.process_dict['inst-cap'][(stf, sit, pro)]
            else:  # expansion is possible
                cap_pro = \
                    (sum
                     (m.cap_pro_new[stf_built, sit, pro]
                      for stf_built in m.stf if
                      (sit, pro, stf_built, stf) in m.operational_pro_tuples)  # sum over all that still exist
                     + m.process_dict['inst-cap'][(min(m.stf), sit, pro)]  # + initial value
                     ) \
                    - sum(m.cap_decommissioned[stf_dec, sit, pro] for stf_dec in m.stf if stf_dec <= stf if
                          stf_dec > min(m.stf) if
                          (stf_dec, sit, pro) in m.pro_decom_cap_dict)  # - sum of decommissioned
                # decomissioning is only allowed for processes within m.pro_decom_cap_dict, also process cannot be decommissioned in min(m.stf)
        else:  # if process has to be built
            cap_pro = sum(
                m.cap_pro_new[stf_built, sit, pro]
                for stf_built in m.stf
                if (sit, pro, stf_built, stf) in m.operational_pro_tuples)
            - sum(m.cap_decommissioned[stf_dec, sit, pro] for stf_dec in m.stf if stf_dec <= stf if stf_dec > min(m.stf)
                  if (stf_dec, sit, pro) in m.pro_decom_cap_dict)
    else:  # operational mode of function
        if 0:  # (sit, pro, stf) in m.pro_const_cap_dict:
            cap_pro = m.process_dict['inst-cap'][(stf, sit, pro)]
        else:
            cap_pro = (m.cap_pro_new[stf, sit, pro] +
                       m.process_dict['inst-cap'][(stf, sit, pro)]
                       - sum(m.cap_decommissioned[stf_dec, sit, pro]
                             for stf_dec in m.stf
                             if stf_dec <= stf
                             if (stf_dec, sit, pro) in m.pro_decom_cap_dict))
    return cap_pro


# process input power == process throughput * input ratio
def def_process_input_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_in[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m.r_in_dict[(stf, pro, com)])


# process output power = process throughput * output ratio
def def_process_output_rule(m, tm, stf, sit, pro, com):
    if com == 'electricity-reactive' and (stf, sit, pro) in m.pro_output_tuples_reactive:
        return pyomo.Constraint.Skip
    else:
        return (m.e_pro_out[tm, stf, sit, pro, com] ==
                m.tau_pro[tm, stf, sit, pro] * m.r_out_dict[(stf, pro, com)])


# rules relating reactive to active power generation with predefined power factors
def def_process_output_reactive_rule1(m, tm, stf, sit, pro):
    #elec_co = [co for (st, si, pr, co) in m.pro_output_tuples
    #           if st == stf and si == sit and pr == pro and co!= 'electricity-reactive'][0]
    return (m.e_pro_out[tm, stf, sit, pro, 'electricity-reactive'] <=
            m.e_pro_out[tm, stf, sit, pro, 'electricity'] * math.tan(
                math.acos(m.process_dict['pf-min'][(stf, sit, pro)])))


def def_process_output_reactive_rule2(m, tm, stf, sit, pro):
    return (m.e_pro_out[tm, stf, sit, pro, 'electricity-reactive'] >=
            -m.e_pro_out[tm, stf, sit, pro, 'electricity'] * math.tan(
                math.acos(m.process_dict['pf-min'][(stf, sit, pro)])))


# process input (for supim commodity) = process capacity * timeseries
def def_intermittent_supply_rule(m, tm, stf, sit, pro, coin):
    if coin in m.com_supim:
        return (m.e_pro_in[tm, stf, sit, pro, coin] ==
                m.cap_pro[stf, sit, pro] * m.supim_dict[(sit, coin)]
                [(stf, tm)] * m.dt)
    else:
        return pyomo.Constraint.Skip


# process throughput <= process capacity
def res_process_throughput_by_capacity_rule(m, tm, stf, sit, pro):
    return (m.tau_pro[tm, stf, sit, pro] <= m.dt * m.cap_pro[stf, sit, pro])


def res_process_rampdown_rule(m, t, stf, sit, pro):
    return (m.tau_pro[t - 1, stf, sit, pro] -
            m.cap_pro[stf, sit, pro] *
            m.process_dict['ramp-down-grad'][(stf, sit, pro)] * m.dt <=
            m.tau_pro[t, stf, sit, pro])


def res_process_rampup_rule(m, t, stf, sit, pro):
    return (m.tau_pro[t - 1, stf, sit, pro] +
            m.cap_pro[stf, sit, pro] *
            m.process_dict['ramp-up-grad'][(stf, sit, pro)] * m.dt >=
            m.tau_pro[t, stf, sit, pro])


# lower bound <= process capacity <= upper bound
def res_process_capacity_rule(m, stf, sit, pro):
    return (m.process_dict['cap-lo'][stf, sit, pro],
            m.cap_pro[stf, sit, pro],
            m.process_dict['cap-up'][stf, sit, pro])


def res_process_capacity_fixed_inv_cost_lower_rule(m, stf, sit, pro):
    return m.pro_cap_expands[stf, sit, pro] * m.process_dict['cap-lo'][stf, sit, pro] <= m.cap_pro_new[stf, sit, pro]


def res_process_capacity_fixed_inv_cost_upper_rule(m, stf, sit, pro):
    return m.cap_pro_new[stf, sit, pro] <= m.pro_cap_expands[stf, sit, pro] * m.process_dict['cap-up'][stf, sit, pro]


# used process area <= maximal process area
def res_area_rule(m, stf, sit):
    if m.site_dict['area'][stf, sit] >= 0 and sum(
            m.process_dict['area-per-cap'][st, s, p]
            for (st, s, p) in m.pro_area_tuples
            if s == sit and st == stf) > 0:
        total_area = sum(m.cap_pro[st, s, p] *
                         m.process_dict['area-per-cap'][st, s, p]
                         for (st, s, p) in m.pro_area_tuples
                         if s == sit and st == stf)
        return total_area <= m.site_dict['area'][stf, sit]
    else:
        # Skip constraint, if area is not numeric
        return pyomo.Constraint.Skip


def def_abs_injection_1_rule(m, tm, stf, sit):
    return calculate_injection(m, tm, stf, sit) <= m.abs_injection[(tm, stf, sit)]


def def_abs_injection_2_rule(m, tm, stf, sit):
    return -calculate_injection(m, tm, stf, sit) <= m.abs_injection[(tm, stf, sit)]


def def_peak_injection_rule(m, tm, stf, sit):
    return m.abs_injection[(tm, stf, sit)] <= m.peak_injection[(stf, sit)]


def def_evu_sperre_hourly_limit_rule(m, tm, stf, sit, pro):
    return m.on_off[(tm - 1, stf, sit, pro)] + 2 * m.on_off[(tm, stf, sit, pro)] + \
           m.on_off[(tm + 1, stf, sit, pro)] + m.on_off[(tm + 2, stf, sit, pro)] <= 3

def def_evu_sperre_daily_limit_rule(m, day, stf, sit, pro):
    return sum(m.on_off[(t, stf, sit, pro)] for t in range(1 + 24 * (day - 1), 24 + 24 * (day - 1) + 1)) <= 6

def res_single_heatpump_rule(m, stf, sit):
    return  sum(m.pro_cap_expands[(st, si, pr)]
            for (st, si, pr) in m.pro_inv_cost_fix_tuples
            if si == sit and st == stf and pr.startswith('heatpump')) <= 1 # new capacity blocks

def def_new_capacity_units_rule(m, stf, sit, pro):
    return (m.cap_pro[stf, sit, pro] == m.pro_cap_unit[stf, sit, pro] *
            m.cap_block_dict[stf, sit, pro])

def res_temperature_min_rule(m, tm, stf, sit):
    return m.temperature[(tm, stf, sit)] >= m.uhp_dict[(sit, 'Tmin')][(stf, tm)]

def res_temperature_min_slack_rule(m, tm, stf, sit):
    return m.temperature[(tm, stf, sit)] >= m.uhp_dict[(sit, 'Tmin')][(stf, tm)] - m.temperature_slack[(tm, stf, sit)]

def res_temperature_max_rule(m, tm, stf, sit):
    return m.temperature[(tm, stf, sit)] <= m.uhp_dict[(sit, 'Tmax')][(stf, tm)]

def res_temperature_fix_rule(m, tm, stf, sit):
    if m.uhp_dict[(sit, 'Tmin')][(stf, tm)] == 18: #night temperature, dont force
        return m.temperature[(tm, stf, sit)] <= m.uhp_dict[(sit, 'Tmax')][(stf, tm)]
    else:
        return m.temperature[(tm, stf, sit)] == m.uhp_dict[(sit, 'Tmin')][(stf, tm)] #force set temperature during day

def def_initial_temperature_rule(m, stf, sit):
    return m.temperature[(0, stf, sit)] == m.uhp_dict[(sit, 'Tmin')][(stf, 0)]

def def_startofperiod_temperature_rule(m, t_startofperiod, stf, sit):
    return m.temperature[(t_startofperiod, stf, sit)] == (m.uhp_dict[(sit, 'Tmin')][(stf, t_startofperiod)])# +
                                                          #m.uhp_dict[(sit, 'Tmax')][(stf, t_startofperiod)]) / 2

# total CO2 output <= Global CO2 limit
def res_global_co2_limit_rule(m, stf):
    if len(m.com_env) == 0:
        return pyomo.Constraint.Skip
    if math.isinf(m.global_prop_dict['value'][stf, 'CO2 limit']):
        return pyomo.Constraint.Skip
    elif m.global_prop_dict['value'][stf, 'CO2 limit'] >= 0:
        co2_output_sum = 0
        for tm in m.tm:
            for sit in m.sit:
                # minus because negative commodity_balance represents creation
                # of that commodity.
                co2_output_sum += (
                        - commodity_balance(m, tm, stf, sit, 'CO2') * m.typeperiod['weight_typeperiod'][(stf, tm)])

        # scaling to annual output (cf. definition of m.weight)
        co2_output_sum *= m.weight
        return (co2_output_sum <= m.global_prop_dict['value']
        [stf, 'CO2 limit'])
    else:
        return pyomo.Constraint.Skip


# CO2 output in entire period <= Global CO2 budget
def res_global_co2_budget_rule(m):
    if math.isinf(m.global_prop_dict['value'][min(m.stf_list), 'CO2 budget']):
        return pyomo.Constraint.Skip
    elif (m.global_prop_dict['value'][min(m.stf_list), 'CO2 budget']) >= 0:
        co2_output_sum = 0
        for stf in m.stf:
            for tm in m.tm:
                for sit in m.sit:
                    # minus because negative commodity_balance represents
                    # creation of that commodity.
                    co2_output_sum += (- commodity_balance
                    (m, tm, stf, sit, 'CO2') *
                                       m.typeperiod['weight_typeperiod'][(stf, tm)] *
                                       m.weight *
                                       stf_dist(stf, m))

        return (co2_output_sum <=
                m.global_prop_dict['value'][min(m.stf), 'CO2 budget'])
    else:
        return pyomo.Constraint.Skip


# total cost of one year <= Global cost limit
def res_global_cost_limit_rule(m, stf):
    if math.isinf(m.global_prop_dict["value"][stf, "Cost limit"]):
        return pyomo.Constraint.Skip
    elif m.global_prop_dict["value"][stf, "Cost limit"] >= 0:
        return (pyomo.summation(m.costs) <= m.global_prop_dict["value"]
        [stf, "Cost limit"])
    else:
        return pyomo.Constraint.Skip


# total cost in entire period <= Global cost budget
def res_global_cost_budget_rule(m):
    if math.isinf(m.global_prop_dict["value"][min(m.stf), "Cost budget"]):
        return pyomo.Constraint.Skip
    elif m.global_prop_dict["value"][min(m.stf), "Cost budget"] >= 0:
        return (pyomo.summation(m.costs) <= m.global_prop_dict["value"]
        [min(m.stf), "Cost budget"])
    else:
        return pyomo.Constraint.Skip


# Costs and emissions
def def_costs_rule(m, cost_type):
    # Calculate total costs by cost type.
    # Sums up process activity and capacity expansions
    # and sums them in the cost types that are specified in the set
    # m.cost_type. To change or add cost types, add/change entries
    # there and modify the if/elif cases in this function accordingly.
    # Cost types are
    #  - Investment costs for process power, storage power and
    #    storage capacity. They are multiplied by the investment
    #    factors. Rest values of units are subtracted.
    #  - Fixed costs for process power, storage power and storage
    #    capacity.
    #  - Variables costs for usage of processes, storage and transmission.
    #  - Fuel costs for stock commodity purchase.

    if cost_type == 'Invest':
        cost = \
            (sum(m.cap_pro_new[p] *
                 m.process_dict['inv-cost'][p] *
                 m.process_dict['invcost-factor'][p]
                 for p in m.pro_tuples)
             - sum(m.cap_decommissioned[p] *
                   m.process_dict['decom-saving'][p] *
                   m.process_dict['invcost-factor'][p]
                   for p in m.pro_decom_cap_dict)
             + sum(m.pro_cap_expands[p] *
                   m.process_dict['inv-cost-fix'][p] *
                   m.process_dict['invcost-factor'][p]
                   for p in m.pro_inv_cost_fix_tuples))
        if m.mode['int']:
            cost -= \
                sum(m.cap_pro_new[p] *
                    m.process_dict['inv-cost'][p] *
                    m.process_dict['overpay-factor'][p]
                    for p in m.pro_tuples)
            cost += sum(
                m.cap_decommissioned[p] * m.process_dict['decom-saving'][p] * m.process_dict['overpay-factor'][p] for p
                in m.pro_decom_cap_dict)
            cost -= sum(m.pro_cap_expands[p] *
                        m.process_dict['inv-cost-fix'][p] *
                        m.process_dict['overpay-factor'][p]
                        for p in m.pro_inv_cost_fix_tuples)
        if m.mode['tra']:
            # transmission_cost is defined in transmission.py
            cost += transmission_cost(m, cost_type)
        if m.mode['sto']:
            # storage_cost is defined in storage.py
            cost += storage_cost(m, cost_type)
        return m.costs[cost_type] == cost

    elif cost_type == 'Fixed':
        cost = \
            sum(m.cap_pro[p] * m.process_dict['fix-cost'][p] *
                m.process_dict['cost_factor'][p]
                for p in m.pro_tuples)
        if m.mode['tra']:
            cost += transmission_cost(m, cost_type)
        if m.mode['sto']:
            cost += storage_cost(m, cost_type)
        return m.costs[cost_type] == cost

    elif cost_type == 'Variable':
        cost = \
            sum(m.tau_pro[(tm,) + p] * m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)] *
                m.process_dict['var-cost'][p] *
                m.process_dict['cost_factor'][p]
                for tm in m.tm
                for p in m.pro_tuples)
        if m.mode['tra']:
            cost += transmission_cost(m, cost_type)
        if m.mode['sto']:
            cost += storage_cost(m, cost_type)
        return m.costs[cost_type] == cost

    elif cost_type == 'Fuel':
        return m.costs[cost_type] == sum(
            m.e_co_stock[(tm,) + c] * m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)] *
            m.commodity_dict['price'][c] *
            m.commodity_dict['cost_factor'][c]
            for tm in m.tm for c in m.com_tuples
            if c[2] in m.com_stock)

    elif cost_type == 'Start-up':
        if m.mode['onoff']:
            cost = sum(m.start_up[(tm,) + p] * m.weight *
                       m.start_price_dict[p] * m.cap_pro[p] *
                       m.process_dict['cost_factor'][p]
                       for tm in m.tm
                       for p in m.pro_start_up_tuples)
            return m.costs[cost_type] == cost
        else:
            return m.costs[cost_type] == 0

    elif cost_type == 'Environmental':
        return m.costs[cost_type] == sum(
            - commodity_balance(m, tm, stf, sit, com) * m.weight * m.typeperiod['weight_typeperiod'][
                (m.stf_list[0], tm)] *
            m.commodity_dict['price'][(stf, sit, com, com_type)] *
            m.commodity_dict['cost_factor'][(stf, sit, com, com_type)]
            for tm in m.tm
            for stf, sit, com, com_type in m.com_tuples
            if com in m.com_env)

    # Revenue and Purchase costs defined in BuySellPrice.py
    elif cost_type == 'Revenue':
        return m.costs[cost_type] == revenue_costs(m)

    elif cost_type == 'Purchase':
        return m.costs[cost_type] == purchase_costs(m)
    elif cost_type == 'Power price':
        return m.costs[cost_type] == sum(m.site_dict['power_price_kw'][sit]
                                         * m.site_dict['cost_factor'][sit]
                                         * m.peak_injection[sit]
                                         for sit in m.sit_power_price_tuples)
    elif cost_type == 'Temperature slack':
        return m.costs[cost_type] == sum(m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)]
                                         * m.temperature_slack[tm, sit] * 200
                                         for tm in m.tm
                                         for sit in m.sit_temperature_tuples)
    else:
        raise NotImplementedError("Unknown cost type.")


def cost_rule(m):
    return pyomo.summation(m.costs)


# CO2 output in entire period <= Global CO2 budget
def co2_rule(m):
    co2_output_sum = 0
    for stf in m.stf:
        for tm in m.tm:
            for sit in m.sit:
                # minus because negative commodity_balance represents
                # creation of that commodity.
                if m.mode['int']:
                    co2_output_sum += (- commodity_balance(m, tm, stf, sit, 'CO2') *
                                       m.typeperiod['weight_typeperiod'][(stf, tm)] *
                                       m.weight * stf_dist(stf, m))
                else:
                    co2_output_sum += (- commodity_balance(m, tm, stf, sit, 'CO2') *
                                       m.weight)

    return (co2_output_sum)
