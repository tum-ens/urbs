import pyomo.environ as pyo
import pyomo.core as pyomo
from datetime import datetime # just used once to create a timestamp
import math # just to use isinf as a test
import numpy as np # just to be able to use np.inf
import itertools # to create tuples with all the different list combinations

#####################
# Model preparation #
#####################

def pyomo_model_prep(data):
    '''Performs calculations on the dictionary "data" for
    further usage by the model.

    Args:
        - data: input data dictionary
        - timesteps: range of modeled timesteps

    Returns:
        a rudimentary pyomo.ConcreteModel instance
    '''

    m = pyomo.ConcreteModel()
    m.name = 'urbs'
    m.created = datetime.now().strftime('%Y%m%dT%H%M')
    
    # Parameter-like data
    # ===================
    # We cannot use pyomo.Param for these ones because we will use a math function on them later
    
    # CO2 limit (relevant in case of cost-minimization)
    m.co2_limit = data["CO2 limit"]
    
    # cost limit (relevant in case of CO2-minimization)
    m.cost_limit = data["Cost limit"]
    
    # Dictionaries
    # ============
    
    # Today, we are assuming that there are no existing power plants (green field), so all power plants can be built
    # and none remain constant --> empty set
    m.pro_const_cap_dict = {}
    
    # Helping functions
    # =================
    def invcost_factor(dep_prd, interest):
        """Investment cost factor formula.
        Evaluates the factor multiplied to the invest costs
        for depreciation duration and interest rate.
        Args:
            dep_prd: depreciation period (years)
            interest: interest rate (e.g. 0.06 means 6 %)
        """
        # invcost factor for non intertemporal planning
        return ((1 + interest) ** dep_prd * interest /
                    ((1 + interest) ** dep_prd - 1))
    
    m.process_dict = {}
    m.process_dict['invcost-factor'] = {p: invcost_factor(data["pro_depreciation"][p], data["pro_wacc"][p]) for p in data["pro_wacc"].keys()}
    
    m._data = data
    return m
    
    
#########
# Model #
#########

def create_model(data, dt=1, objective='cost', dual=True):
    """Create a pyomo ConcreteModel urbs object from given input data.

    Args:
        - data: a dict of up to 12 keys
        - dt: timestep duration in hours (default: 1)
        - objective: Either "cost" or "CO2" for choice of objective function,
          default: "cost"
        - dual: set True to add dual variables to model output
          (marginally slower), default: True

    Returns:
        a pyomo ConcreteModel object
    """
    
    m = pyomo_model_prep(data) # Check this function

    # Parameters
    # ==========

    # dt = spacing between timesteps.
    m.dt = pyomo.Param(
        initialize=data["dt"],
        doc='Time step duration (in hours), default: 1')

    # import objective function information (a switch to reflect user preferences)
    m.obj = pyomo.Param(
        initialize=data["objective"],
        doc='Specification of minimized quantity, default: "cost"')
    
    # weight = length of year (hours) / length of simulation (hours)
    # weight scales costs and emissions from length of simulation to a full
    # year, making comparisons among cost types (invest is annualized, fixed
    # costs are annual by default, variable costs are scaled by weight) and
    # among different simulation durations meaningful.
    m.weight = pyomo.Param(
        initialize=float(8760) / ((len(data["timesteps"]) - 1) * data["dt"]),
        doc='Pre-factor for variable costs and emissions for an annual result')

    # Sets
    # ====
    # Syntax: m.{name} = Set({domain}, initialize={values})
    # where name: set name
    #       domain: set domain for tuple sets, a cartesian set product
    #       values: set values, a list or array of element tuples

    # generate ordered time step sets
    m.t = pyomo.Set(
        initialize=data["timesteps"],
        ordered=True,
        doc='Set of timesteps')

    # modeled time steps
    # It is common to have a fictive first time step to initialize some processes that depend on a previous state,
    # like storage devices.
    m.tm = pyomo.Set(
        within=m.t,
        initialize=data["timesteps"][1:],
        ordered=True,
        doc='Set of modeled timesteps')

    # support timeframes (e.g. 2020, 2030...)
    m.stf = pyomo.Set(
        initialize=set(data["support_timeframes"]),
        doc='Set of modeled support timeframes (e.g. years)')

    # site
    m.sit = pyomo.Set(
        initialize=set(data["sites"]),
        doc='Set of sites')

    # commodity (e.g. solar, wind, coal...)
    m.com = pyomo.Set(
        initialize=set(data["commodities"]),
        doc='Set of commodities')

    # commodity type (i.e. SupIm, Demand, Stock, Env)
    m.com_type = pyomo.Set(
        initialize=set(data["com_type"]),
        doc='Set of commodity types')

    # process (e.g. Wind turbine, Gas plant, Photovoltaics...)
    m.pro = pyomo.Set(
        initialize=set(data["process"]),
        doc='Set of conversion processes')

    # cost_type
    m.cost_type = pyomo.Set(
        initialize=data["cost_type"],
        doc='Set of cost types')

    # tuple sets
    m.sit_tuples = pyomo.Set(
        within=m.stf * m.sit,
        initialize=itertools.product(data["support_timeframes"], data["sites"]),
        doc='Combinations of support timeframes and sites')
    m.com_tuples = pyomo.Set(
        within=m.stf * m.sit * m.com * m.com_type,
        initialize=data["com_prices"].keys(),
        doc='Combinations of defined commodities, e.g. (2018,Mid,Elec,Demand)')
    m.pro_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro,
        initialize=data["pro_invcost"].keys(),
        doc='Combinations of possible processes, e.g. (2018,North,Coal plant)')
    

    # commodity type subsets
    m.com_stock = pyomo.Set(
        within=m.com,
        initialize=set(com for stf, sit, com, com_type in m.com_tuples if com_type == 'Stock'),
        doc='Commodities that can be purchased at some site(s)')
    m.com_supim = pyomo.Set(
        within=m.com,
        initialize=set(com for stf, sit, com, com_type in m.com_tuples if com_type == 'SupIm'),
        doc='Commodities that have intermittent (time series) input')
    m.com_demand = pyomo.Set(
        within=m.com,
        initialize=set(com for stf, sit, com, com_type in m.com_tuples if com_type == 'Demand'),
        doc='Commodities that have a demand (implies time series)')
    m.com_env = pyomo.Set(
        within=m.com,
        initialize=set(com for stf, sit, com, com_type in m.com_tuples if com_type == 'Env'),
        doc='Commodities that (might) have a maximum creation limit')

    # process input/output
    m.pro_input_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro * m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in tuple(data["ratio_in"].keys())
                    if process == pro and s == stf],
        doc='Commodities consumed by process by site,'
            'e.g. (2020,Mid,PV,Solar)')
    m.pro_output_tuples = pyomo.Set(
        within=m.stf * m.sit * m.pro * m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in tuple(data["ratio_out"].keys())
                    if process == pro and s == stf],
        doc='Commodities produced by process by site, e.g. (2020,Mid,PV,Elec)')


    # Variables
    # =========

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

    # process
    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')

    # process capacity as expression object
    # (variable if expansion is possible, else static)
    m.cap_pro = pyomo.Expression(
        m.pro_tuples,
        rule=def_process_capacity_rule,
        doc='Total process capacity (MW)')

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
        within=pyomo.NonNegativeReals,
        doc='Power flow out of process (MW) per timestep')
    
    
    # Equations
    # =========

    # equation bodies are defined in separate functions, referred to here by
    # their name in the "rule" keyword.

    # commodity
    m.res_vertex = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_vertex_rule,
        doc='process + source == demand')
    m.res_stock_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_stock_total_rule,
        doc='total stock commodity input <= commodity.max')
    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

    # process
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

        m.objective_function = pyomo.Objective(
            rule=cost_rule,
            sense=pyomo.minimize,
            doc='minimize(cost = sum of all cost types)')

    elif m.obj.value == 'CO2':

        m.res_global_cost_limit = pyomo.Constraint(
            m.stf,
            rule=res_global_cost_limit_rule,
            doc='total costs <= Global cost limit')

        m.objective_function = pyomo.Objective(
            rule=co2_rule,
            sense=pyomo.minimize,
            doc='minimize total CO2 emissions')

    if dual:
        m.dual = pyomo.Suffix(direction=pyomo.Suffix.IMPORT)

    return m
    
# Helper function

def commodity_balance(m, tm, stf, sit, com):
    """Calculate commodity balance at given timestep.
    For a given commodity co and timestep tm, calculate the balance of
    consumed (to process/storage/transmission, counts positive) and provided
    (from process/storage/transmission, counts negative) commodity flow. Used
    as helper function in create_model for constraints on demand and stock
    commodities.
    Args:
        m: the model object
        tm: the timestep
        site: the site
        com: the commodity
    Returns
        balance: net value of consumed (positive) or provided (negative) power
    """
    balance = (sum(m.e_pro_in[(tm, stframe, site, process, com)]
                # usage as input for process increases balance
                for stframe, site, process in m.pro_tuples
                if site == sit and stframe == stf and
                (stframe, process, com) in m._data["ratio_in"].keys()) -
            sum(m.e_pro_out[(tm, stframe, site, process, com)]
                # output from processes decreases balance
                for stframe, site, process in m.pro_tuples
                if site == sit and stframe == stf and
                (stframe, process, com) in m._data["ratio_out"].keys()))
    return balance

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

    # if com is a demand commodity, the power_surplus is reduced by the
    # demand value; no scaling by m.dt or m.weight is needed here, as this
    # constraint is about power (MW), not energy (MWh)
    if com in m.com_demand:
        try:
            power_surplus -= m._data["demand"][(stf, sit, com, tm)]
        except KeyError:
            pass

    return power_surplus == 0


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
                m.e_co_stock[tm, stf, sit, com, com_type])
        total_consumption *= m.weight
        return (total_consumption <=
                m._data['com_max'][(stf, sit, com, com_type)])


# limit environmental commodity output in total (scaled to annual
# emissions, thanks to m.weight)
def res_env_total_rule(m, stf, sit, com, com_type):
    if com not in m.com_env:
        return pyomo.Constraint.Skip
    else:
        # calculate total creation of environmental commodity com
        env_output_sum = 0
        for tm in m.tm:
            env_output_sum += (- commodity_balance(m, tm, stf, sit, com))
        env_output_sum *= m.weight
        return (env_output_sum <=
                m._data['com_max'][(stf, sit, com, com_type)])


# process

# process capacity (for m.cap_pro Expression)
def def_process_capacity_rule(m, stf, sit, pro):
    if (sit, pro, stf) in m.pro_const_cap_dict:
        cap_pro = m._data['pro_instcap'][(stf, sit, pro)]
    else:
        cap_pro = (m.cap_pro_new[stf, sit, pro] +
                   m._data['pro_instcap'][(stf, sit, pro)])
    return cap_pro

# process input power == process throughput * input ratio
def def_process_input_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_in[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m._data['ratio_in'][(stf, pro, com)])


# process output power = process throughput * output ratio
def def_process_output_rule(m, tm, stf, sit, pro, com):
    return (m.e_pro_out[tm, stf, sit, pro, com] ==
            m.tau_pro[tm, stf, sit, pro] * m._data['ratio_out'][(stf, pro, com)])


# process input (for supim commodity) = process capacity * timeseries
def def_intermittent_supply_rule(m, tm, stf, sit, pro, coin):
    if coin in m.com_supim:
        return (m.e_pro_in[tm, stf, sit, pro, coin] ==
                m.cap_pro[stf, sit, pro] * m._data['supim'][(stf, sit, coin, tm)] * m.dt)
    else:
        return pyomo.Constraint.Skip


# process throughput <= process capacity
def res_process_throughput_by_capacity_rule(m, tm, stf, sit, pro):
    return (m.tau_pro[tm, stf, sit, pro] <= m.dt * m.cap_pro[stf, sit, pro])


# lower bound <= process capacity <= upper bound
def res_process_capacity_rule(m, stf, sit, pro):
    return (m._data['pro_caplo'][stf, sit, pro],
            m.cap_pro[stf, sit, pro],
            m._data['pro_capup'][stf, sit, pro])


# total CO2 output <= Global CO2 limit
def res_global_co2_limit_rule(m, stf):
    if math.isinf(m.co2_limit):
        return pyomo.Constraint.Skip
    elif m.co2_limit >= 0:
        co2_output_sum = 0
        for tm in m.tm:
            for sit in m.sit:
                # minus because negative commodity_balance represents creation
                # of that commodity.
                co2_output_sum += (- commodity_balance(m, tm, stf, sit, "CO2"))

        # scaling to annual output (cf. definition of m.weight)
        co2_output_sum *= m.weight
        return (co2_output_sum <= m.co2_limit)
    else:
        return pyomo.Constraint.Skip


# total cost of one year <= Global cost limit
def res_global_cost_limit_rule(m, stf):
    if math.isinf(m.cost_limit):
        return pyomo.Constraint.Skip
    elif m.cost_limit >= 0:
        return(pyomo.summation(m.costs) <= m.cost_limit)
    else:
        return pyomo.Constraint.Skip


# Costs and emissions
def def_costs_rule(m, cost_type):
    #Calculate total costs by cost type.
    #Sums up process activity and capacity expansions
    #and sums them in the cost types that are specified in the set
    #m.cost_type. To change or add cost types, add/change entries
    #there and modify the if/elif cases in this function accordingly.
    #Cost types are
    #  - Investment costs for process power, storage power and
    #    storage capacity. They are multiplied by the investment
    #    factors. Rest values of units are subtracted.
    #  - Fixed costs for process power, storage power and storage
    #    capacity.
    #  - Variables costs for usage of processes, storage and transmission.
    #  - Fuel costs for stock commodity purchase.

    if cost_type == 'Invest':
        cost = \
            sum(m.cap_pro_new[p] *
                m._data['pro_invcost'][p] *
                m.process_dict['invcost-factor'][p]
                for p in m.pro_tuples)
        return m.costs[cost_type] == cost

    elif cost_type == 'Fixed':
        cost = \
            sum(m.cap_pro[p] * m._data['pro_fixcost'][p]
                for p in m.pro_tuples)
        return m.costs[cost_type] == cost

    elif cost_type == 'Variable':
        cost = \
            sum(m.tau_pro[(tm,) + p] * m.weight *
                m._data['pro_varcost'][p]
                for tm in m.tm
                for p in m.pro_tuples)
        return m.costs[cost_type] == cost

    elif cost_type == 'Fuel':
        return m.costs[cost_type] == sum(
            m.e_co_stock[(tm,) + c] * m.weight *
            m._data['com_prices'][c]
            for tm in m.tm for c in m.com_tuples
            if c[2] in m.com_stock)

    elif cost_type == 'Environmental':
        return m.costs[cost_type] == sum(
            - commodity_balance(m, tm, stf, sit, com) * m.weight *
            m._data['com_prices'][(stf, sit, com, com_type)]
            for tm in m.tm
            for stf, sit, com, com_type in m.com_tuples
            if com in m.com_env)

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
                co2_output_sum += (- commodity_balance(m, tm, stf, sit, "CO2") * m.weight)
    return (co2_output_sum)