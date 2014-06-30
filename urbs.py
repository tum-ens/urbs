from datetime import datetime
import coopr.pyomo as pyomo
import pandas as pd


def create_model(filename, timesteps):
    """ Create pyomo ConcreteModel URBS object
    """
    m = pyomo.ConcreteModel()
    m.name = 'URBS'
    m.settings = {
        'dateformat': '%Y%m%dT%H%M%S',
        'timesteps': timesteps,
        }
    m.created = datetime.now().strftime(m.settings['dateformat'])

    # Preparations
    # ============
    # Excel import
    # use Pandas DataFrames instead of Pyomo parameters for entity
    # attributes. Syntax to access a value:
    #
    #     m.process.loc[sit, pro, coin, cout][attribute]
    #
    xls = pd.ExcelFile(filename)
    m.site = xls.parse(
        'Site',
        index_col=['Sit'])
    m.commodity = xls.parse(
        'Commodity',
        index_col=['Sit', 'Co', 'Type'])
    m.process = xls.parse(
        'Process',
        index_col=['Sit', 'Pro', 'CoIn', 'CoOut'])
    m.transmission = xls.parse(
        'Transmission',
        index_col=['SitIn', 'SitOut', 'Co'])
    m.storage = xls.parse(
        'Storage',
        index_col=['Sit', 'Sto', 'Tra', 'Co'])
    m.demand = xls.parse('Demand', index_col=['t'])
    m.supim = xls.parse('SupIm', index_col=['t'])

    # derive annuity factor for process and storage
    m.process['annuity_factor'] = annuity_factor(
        m.process['depreciation'], m.process['wacc'])
    m.transmission['annuity_factor'] = annuity_factor(
        m.transmission['depreciation'], m.transmission['wacc'])
    m.storage['annuity_factor'] = annuity_factor(
        m.storage['depreciation'], m.storage['wacc'])

    # split columns by dots '.', so that 'DE.Elec' becomes the two-level
    # column index ('DE', 'Elec')
    m.demand.columns = split_columns(m.demand.columns, '.')
    m.supim.columns = split_columns(m.supim.columns, '.')

    # Sets
    # ====
    # Syntax: m.{name} = Set({domain}, initialize={values})
    # where name: set name
    #       domain: set domain for tuple sets, a cartesian set product
    #       values: set values, a list or array of element tuples
    m.t = pyomo.Set(
        initialize=m.settings['timesteps'],
        doc='Set of timesteps')
    m.tm = pyomo.Set(
        within=m.t, initialize=m.settings['timesteps'][1:],
        doc='Set of modelled timesteps')
    m.sit = pyomo.Set(
        initialize=m.site.index.levels[0],
        doc='Set of sites')
    m.com = pyomo.Set(
        initialize=m.commodity.index.levels[1],
        doc='Set of commodities')
    m.com_type = pyomo.Set(
        initialize=m.commodity.index.levels[2],
        doc='Set of commodity types')
    m.pro = pyomo.Set(
        initialize=m.process.index.levels[1],
        doc='Set of conversion processes')
    m.tra = pyomo.Set(
        initialize=m.transmission.index.levels[2],
        doc='Set of tranmission technologies')
    m.sto = pyomo.Set(
        initialize=m.storage.index.levels[1],
        doc='Set of storage technologies')
    m.cost_type = pyomo.Set(
        initialize=['Inv', 'Fix', 'Var', 'Fuel'],
        doc='Set of cost types (hard-coded)')

    # sets of existing tuples:
    # co_tuples = [('DE', 'Coal', 'Stock'), ('MA', 'Wind', 'SupIm'), ...]
    # pro_tuples = [('DE', 'pp', 'Coal', 'Elec'), ('NO', 'wt', 'Wind', 'Elec')]
    # sto_tuples = [('DE', 'bat', 'Elec'), ('NO', 'pst', 'Elec')...]
    m.co_tuples = pyomo.Set(within=m.sit*m.com*m.com_type,
                            initialize=m.commodity.index)
    m.pro_tuples = pyomo.Set(within=m.sit*m.pro*m.com*m.com,
                             initialize=m.process.index)
    m.tra_tuples = pyomo.Set(within=m.sit*m.sit*m.tra*m.com,
                             initialize=m.transport.index)
    m.sto_tuples = pyomo.Set(within=m.sit*m.sto*m.com,
                             initialize=m.storage.index)

    # subsets of commodities by type
    # for equations that apply to only one commodity type
    m.com_supim = pyomo.Set(
        within=m.com,
        initialize=(c[1] for c in m.com_tuples if c[2] == 'SupIm'))
    m.com_stock = pyomo.Set(
        within=m.com,
        initialize=(c[1] for c in m.com_tuples if c[2] == 'Stock'))
    m.com_demand = pyomo.Set(
        within=m.com,
        initialize=(c[1] for c in m.com_tuples if c[2] == 'Demand'))

    # Parameters
    # ==========
    # for model entities (commodity, process, transmission, storage) no Pyomo
    # parames are needed, just use the DataFrames m.commodity, m.process,
    # m.storage and m.transmission directly.
    # Syntax: m.{name} = Param({domain}, initialize={values})
    # where name: param name
    #       domain: one or multiple model sets; empty for scalar parameters
    #       values: dict of parameter values, addressed by elements of domains
    # if domain is skipped, defines a scalar parameter with a single value
    m.weight = pyomo.Param(initialize=float(8760) / len(m.t))

    # Variables
    # =========
    # listed alphabetically
    # Syntax: m.{name} = Var({domain}, within={range}, doc={docstring})
    # where name: variable name
    #       domain: variable domain, consisting of one or multiple sets
    #       range: variable values, like Binary, Integer, NonNegativeReals
    #       docstring: a documentation string/short description
    m.cap_pro = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total process capacity (MW)')
    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')
    m.cap_tra = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total transmission capacity (MW)')
    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')
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
    m.co2_pro_out = pyomo.Var(
        m.tm, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='CO2 emissions from process (t) per timestep')
    m.costs = pyomo.Var(
        m.cost_type,
        within=pyomo.NonNegativeReals,
        doc='Costs by type (EUR/a)')
    m.e_co_stock = pyomo.Var(
        m.tm, m.co_tuple,
        within=pyomo.NonNegativeReals,
        doc='Use of stock commodity source (MW) per timestep')
    m.e_pro_in = pyomo.Var(
        m.tm, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into process (MW) per timestep')
    m.e_pro_out = pyomo.Var(
        m.tm, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of process (MW) per timestep')
    m.e_tra_in = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into transmission line (MW) per timestep')
    m.e_tra_out = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of transmission line (MW) per timestep')
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

    # Equation definition
    # ===================
    # listed by topic. All equations except the Objective function are
    # of type Constraint, although there are two semantics for those,
    # indicated by the name prefix (def, res).
    #  - def: definition, usually equations, defining variable values
    #  - res: restriction, usually inequalities, limiting variable values
    # topics
    #  - commodity
    #  - process
    #  - transmission
    #  - storage
    #  - emissions
    #  - costs

    # commodity
    def res_demand_rule(m, tm, sit, com, com_type):
        if com not in m.com_demand:
            return pyomo.Constraint.Skip
        else:
            provided_energy = - commodity_balance(m, tm, sit, com)
            return (provided_energy >=
                    m.demand.loc[tm][sit, com] *
                    m.commodity.loc[sit, com, com_type]['peak'])

    def def_e_co_stock_rule(m, tm, sit, com, com_type):
        if com not in m.com_stock:
            return pyomo.Constraint.Skip
        else:
            return (m.e_co_stock[tm, sit, com, com_type] ==
                    commodity_balance(m, tm, sit, com))

    def res_stock_hour_rule(m, tm, sit, com, com_type):
        if com not in m.com_stock:
            return pyomo.Constraint.Skip
        else:
            return (m.e_co_stock[tm, sit, com, com_type] <=
                    m.commodity.loc[sit, com, com_type]['maxperhour'])

    def res_stock_total_rule(m, sit, com, com_type):
        if com not in m.com_stock:
            return pyomo.Constraint.Skip
        else:
            # calculate total consumption of commodity com
            total_consumption = 0
            for tm in m.tm:
                total_consumption += m.e_co_stock[tm, sit, com, com_type]
            total_consumption *= m.weight
            return (total_consumption <=
                    m.commodity.loc[sit, com, com_type]['max'])

    # process
    def def_process_capacity_rule(m, sit, pro, coin, cout):
        return (m.cap_pro[sit, pro, coin, cout] ==
                m.cap_pro_new[sit, pro, coin, cout] +
                m.process.loc[sit, pro, coin, cout]['inst-cap'])

    def def_process_output_rule(m, tm, sit, pro, coin, cout):
        return (m.e_pro_out[tm, sit, pro, coin, cout] ==
                m.e_pro_in[tm, sit, pro, coin, cout] *
                m.process.loc[sit, pro, coin, cout]['eff'])

    def def_intermittent_supply_rule(m, tm, sit, pro, coin, cout):
        if coin in m.com_supim:
            return (m.e_pro_in[tm, sit, pro, coin, cout] ==
                    m.cap_pro[sit, pro, coin, cout] *
                    m.supim.loc[tm][sit, coin])
        else:
            return pyomo.Constraint.Skip

    def def_co2_emissions_rule(m, tm, sit, pro, coin, cout):
        return (m.co2_pro_out[tm, sit, pro, coin, cout] ==
                m.e_pro_in[tm, sit, pro, coin, cout] *
                m.process.loc[sit, pro, coin, cout]['co2'] *
                m.weight)

    def res_process_output_by_capacity_rule(m, tm, sit, pro, coin, cout):
        return (m.e_pro_out[tm, sit, pro, coin, cout] <=
                m.cap_pro[sit, pro, coin, cout])

    def res_process_capacity_rule(m, sit, pro, coin, cout):
        return (m.process.loc[sit, pro, coin, cout]['cap-lo'],
                m.cap_pro[sit, pro, coin, cout],
                m.process.loc[sit, pro, coin, cout]['cap-up'])

    # transmission
    def def_transmission_capacity_rule(m, sin, sout, tra, com):
        return (m.cap_tra[sin, sout, tra, com] ==
                m.cap_tra_new[sin, sout, tra, com] +
                m.transmission.loc[sin, sout, tra, com]['inst-cap'])

    def def_transmission_output_rule(m, tm, sin, sout, tra, com):
        return (m.e_tra_out[tm, sin, sout, tra, com] ==
                m.e_tra_in[tm, sin, sout, tra, com] *
                m.transmission.loc[sin, sout, tra, com]['eff'])

    def res_transmission_input_by_capacity_rule(m, tm, sin, sout, tra, com):
        return (m.e_tra_in[tm, sin, sout, tra, com] >=
                m.cap_tra[sin, sout, tra, com])

    def res_transmission_capacity_rule(m, sin, sout, tra, com):
        return (m.transmission.loc[sin, sout, tra, com]['cap-lo'],
                m.cap_tra[sin, sout, tra, com],
                m.transmission.loc[sin, sout, tra, com]['cap-up'])

    def res_transmission_symmetry_rule(m, sin, sout, tra, com):
        return m.cap_tra[sin, sout, com] == m.cap_tra[sout, sin, tra, com]

    # storage
    def def_storage_state_rule(m, t, sit, sto, com):
        return (m.e_sto_con[t, sit, sto, com] ==
                m.e_sto_con[t-1, sit, sto, com] +
                m.e_sto_in[t, sit, sto, com] *
                m.storage.loc[sit, sto, com]['eff-in'] -
                m.e_sto_out[t, sit, sto, com] /
                m.storage.loc[sit, sto, com]['eff-out'])

    def def_storage_power_rule(m, sit, sto, com):
        return (m.cap_sto_p[sit, sto, com] ==
                m.cap_sto_p_new[sit, sto, com] +
                m.storage.loc[sit, sto, com]['inst-cap-p'])

    def def_storage_capacity_rule(m, sit, sto, com):
        return (m.cap_sto_c[sit, sto, com] ==
                m.cap_sto_c_new[sit, sto, com] +
                m.storage.loc[sit, sto, com]['inst-cap-p'])

    def res_storage_input_by_power_rule(m, t, sit, sto, com):
        return m.e_sto_in[t, sit, sto, com] <= m.cap_sto_p[sit, sto, com]

    def res_storage_output_by_power_rule(m, t, sit, sto, co):
        return m.e_sto_out[t, sit, sto, co] <= m.cap_sto_p[sit, sto, co]

    def res_storage_state_by_capacity_rule(m, t, sit, sto, com):
        return m.e_sto_con[t, sit, sto, com] <= m.cap_sto_c[sit, sto, com]

    def res_storage_power_rule(m, sit, sto, com):
        return (m.storage.loc[sit, sto, com]['cap-lo-p'],
                m.cap_sto_p[sit, sto, com],
                m.storage.loc[sit, sto, com]['cap-up-p'])

    def res_storage_capacity_rule(m, sit, sto, com):
        return (m.storage.loc[sit, sto, com]['cap-lo-c'],
                m.cap_sto_c[sit, sto, com],
                m.storage.loc[sit, sto, com]['cap-up-c'])

    def res_initial_and_final_storage_state_rule(m, t, sit, sto, com):
        if t == m.t[1]:  # first timestep (Pyomo uses 1-based indexing)
            return (m.e_sto_con[t, sit, sto, com] ==
                    m.cap_sto_c[sit, sto, com] *
                    m.storage.loc[sit, sto, com]['init'])
        elif t == m.t[-1]:  # last timestep
            return (m.e_sto_con[t, sit, sto, com] >=
                    m.cap_sto_c[sit, sto, com] *
                    m.storage.loc[sit, sto, com]['init'])
        else:
            return pyomo.Constraint.Skip

    # emissions
    def res_co2_emission_rule(m):
        return (pyomo.summation(m.co2_pro_out) <=
                m.commodity.loc['Global', 'CO2', 'Env']['max'])

    # costs
    def def_costs_rule(m, cost_type):
        """ calculate total costs by cost type

        This functions sums up process activity and capacity expansions
        and sums them in the cost types that are specified in the set
        m.cost_type. To change or add cost types, add/change entries
        there and modify the if/elif cases in this function accordingly.

        Cost types are

          - Investment costs for process power, storage power and
            storage capacity. They are multiplied by the annuity
            factors, which in turn are derived from the attributes
            'depreciation' and 'wacc'.

          - Fixed costs for process power, storage power and storage
            capacity.

          - Variables costs for usage ofr processes,
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
                    m.storage.loc[s]['annuity_factor']
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
                sum(m.e_pro_out[(tm,) + p] *
                    m.process.loc[p]['var-cost'] *
                    m.weight
                    for tm in m.tm for p in m.pro_tuples) + \
                sum(m.e_tra_in[(tm,) + t] *
                    m.transmission.loc[t]['var-cost'] *
                    m.weight
                    for tm in m.tm for t in m.tra_tuples) + \
                sum(m.e_sto_con[(tm,) + s] *
                    m.storage.loc[s]['var-cost-c'] * m.weight +
                    (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) *
                    m.storage.loc[s]['var-cost-p'] * m.weight
                    for tm in m.tm for s in m.sto_tuples)

        elif cost_type == 'Fuel':
            return m.costs['Fuel'] == sum(
                m.e_co_stock[(tm,) + c] *
                m.commodity[c]['price'] *
                m.weight
                for tm in m.tm for c in m.com_tuples
                if c[0] in m.com_stock)

        else:
            raise NotImplementedError("Unknown cost type!")

    def obj_rule(m):
        return pyomo.summation(m.costs)

    # Equation declaration
    # ====================
    # declarations connect rule functions to the model, specifying
    # the model sets for which the constraints are enforced
    # a constraint with m.{name} automagically binds to the function
    # {name}_rule. If the names don't match, one can link Constraint to
    # function by using the rule keyword. Example:
    # m.every_step = pyomo.Constraint(m.tm, rule=any_function_name)

    # commodity
    m.res_demand = pyomo.Constraint(
        m.tm, m.com_tuples,
        doc='storage + transmission + process + source >= demand')
    m.def_e_co_stock = pyomo.Constraint(
        m.tm, m.com_tuples,
        doc='commodity source term = hourly commodity consumption')
    m.res_stock_hour = pyomo.Constraint(
        m.tm, m.com_tuples,
        doc='hourly commodity source term <= commodity.maxperhour')
    m.res_stock_total = pyomo.Constraint(
        m.com_tuples,
        doc='total commodity source term <= commodity.max')

    # process
    m.def_process_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        doc='total process capacity = inst-cap + new capacity')
    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_tuples,
        doc='process output = process input * efficiency')
    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_tuples,
        doc='process output = process capacity * supim timeseries')
    m.def_co2_emissions = pyomo.Constraint(
        m.tm, m.pro_tuples,
        doc='process co2 output = process input * process.co2 * weight')
    m.res_process_output_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        doc='process output <= total process capacity')
    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

    # transmission
    m.def_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        doc='total transmission capacity = inst-cap + new capacity')
    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        doc='transmission output = transmission input * efficiency')
    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        doc='transmission input <= total transmission capacity')
    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')
    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples,
        doc='total transmission capacity must be symmetric in both directions')

    # storage
    m.def_storage_state = pyomo.Constraint(
        m.tm, m.sto_tuples,
        doc='storage[t] = storage[t-1] + input - output')
    m.def_storage_power = pyomo.Constraint(
        m.sto_tuples,
        doc='storage power = inst-cap + new power')
    m.def_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        doc='storage capacity = inst-cap + new capacity')
    m.res_storage_input_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        doc='storage input <= storage power')
    m.res_storage_output_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        doc='storage output <= storage power')
    m.res_storage_state_by_capacity = pyomo.Constraint(
        m.t, m.sto_tuples,
        doc='storage content <= storage capacity')
    m.res_storage_power = pyomo.Constraint(
        m.sto_tuples,
        doc='storage.cap-lo-p <= storage power <= storage.cap-up-p')
    m.res_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        doc='storage.cap-lo-c <= storage capacity <= storage.cap-up-c')
    m.res_initial_and_final_storage_state = pyomo.Constraint(
        m.t, m.sto_tuples,
        doc='storage content initial == and final >= storage.init * capacity')

    # emissions
    m.res_co2_emission = pyomo.Constraint(
        doc='total CO2 emissions <= commodity.global.co2.max')

    # costs
    m.def_costs = pyomo.Constraint(
        m.cost_type,
        doc='main cost function by cost type')
    m.obj = pyomo.Objective(
        sense=pyomo.minimize,
        doc='minimize(cost = sum of all cost types)')

    return m


def annuity_factor(n, i):
    """ return annuity factor

    Evaluates the annuity factor formula for depreciation duration
    and interest rate. Works also well for equally sized numpy arrays
    of values for n and i.
    Args:
        n: depreciation period (years)
        i: interest rate (percent, e.g. 0.06 means 6 %)

    Returns:
        Value of the expression
            (1+i)**n * i / ((1+i)**n - 1)
            
    Example:
        >>> round(annuity_factor(20, 0.07), 5)
        0.09439

    """
    return (1+i)**n * i / ((1+i)**n - 1)


def commodity_balance(m, tm, sit, com):
    """Calculate commodity balance at given timestep.

    For a given commodity co and timestep tm, calculate the balance of
    consumed (to process/storage/transmission, counts positive) and provided
    (from process/storage/transmission, counts negative) energy. Used as helper
    function in create_model for constraints on demand and stock commodities.

    Args:
        m: the model object
        tm: the timestep
        co: the commodity

    Returns
        balance: net value of consumed (+) or provided (-) energy

    """
    balance = 0
    for p in m.pro_tuples:
        if p[0] == sit and p[1] == com:
            # usage as input for process increases balance
            balance += m.e_pro_in[(tm,)+p]
        if p[0] == sit and p[2] == com:
            # output from processes decreases balance
            balance -= m.e_pro_out[(tm,)+p]
    for s in m.sto_tuples:
        # usage as input for storage increases consumption
        # output from storage decreases consumption
        if s[0] == sit and s[1] == com:
            balance += m.e_sto_in[(tm,)+s]
            balance -= m.e_sto_out[(tm,)+s]
    for t in m.tra_tuples:
        # exports increase balance
        if t[0] == sit and t[3] == com:
            balance += m.e_tra_in[(tm,)+t]
        # imports decrease balance
        if t[1] == sit and t[3] == com:
            balance -= m.e_tra_out[(tm,)+t]
    return balance


def split_columns(columns, sep='.'):
    """Split columns by separator into MultiIndex.

    Given a list of column labels containing a separator string (default: '.'),
    derive a MulitIndex that is split at the separator string.

    Args:
        columns: list of column labels, containing the separator string
        sep: the separator string (default: '.')

    Example:
        >>> split_columns(['DE.Elec', 'MA.Elec', 'NO.Wind'])
        MultiIndex(levels=[[u'DE', u'MA', u'NO'], [u'Elec', u'Wind']],
                   labels=[[0, 1, 2], [0, 0, 1]])

    """
    column_tuples = [tuple(col.split('.')) for col in columns]
    return pd.MultiIndex.from_tuples(column_tuples)
