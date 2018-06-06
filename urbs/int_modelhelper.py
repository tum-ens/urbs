import pandas as pd


def invcost_factor(m, n, i, year_built):
    """Investment cost factor formula.

    Evaluates the factor multiplied to the invest costs
    for depreciation duration and interest rate.

    Args:
        n: depreciation period (years)
        i: interest rate (e.g. 0.06 means 6 %)
        year_built: year utility is built
        j: discount rate for intertmeporal planning
    """
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])
    if j == 0:
        return n * ((1+i) ** n * i)/((1+i) ** n - 1)
    else:
        return ((1+j) ** (-(year_built-m.global_prop.index.min()[0])) *
                (i * (1+i) ** n * ((1+j) ** n - 1)) /
                (j * (1+j) ** n * ((1+i) ** n - 1)))


def rv_factor(m, n, i, year_built):
    """Rest value factor formula.

    Evaluates the factor multiplied to the invest costs
    for the rest value of a unit after the end of the
    optimization period.

    Args:
        n: depreciation period (years)
        i: interest rate (e.g. 0.06 means 6 %)
        year_built: year utility is built
        j: discount rate for intertmeporal planning
        k: operational time after simulation horizon
    """
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])
    k = (year_built + n) - m.global_prop.index.max()[0] - 1

    if j == 0:
        return k * ((1+i) ** n * i)/((1+i) ** n - 1)
    else:
        return ((1+j) ** (-(year_built-m.global_prop.index.min()[0])) *
                (i * (1+i)** n * ((1+j) ** k - 1)) /
                (j * (1+j) ** n * ((1+i) ** n - 1)))


# Energy related costs
def stf_dist(stf, m):
    """Calculates the distance between the modeled support timeframes.
    """
    sorted_stf = sorted(list(m.commodity.index.
                             get_level_values('support_timeframe').unique()))
    dist = []

    for s in sorted_stf:
        if s == max(sorted_stf):
            dist.append(1)
        else:
            dist.append(sorted_stf[sorted_stf.index(s) + 1] - s)

    return dist[sorted_stf.index(stf)]


def cost_helper(stf, m):
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])

    return (1+j) ** (1-(stf-m.global_prop.index.min()[0]))


def cost_helper2(dist, m):
    """Factor for variable, fuel, purchase, sell, and fix costs.
    Calculated by repetition of modeled stfs and discount utility.
    """
    j = (m.global_prop.xs('Discount rate', level=1)
         .loc[m.global_prop.index.min()[0]]['value'])

    if j == 0:
        return dist
    else:
        return (1-(1+j) ** (-dist)) / j


def commodity_balance(m, tm, stf, sit, com):
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
    balance = (sum(m.e_pro_in[(tm, stframe, site, process, com)]
                   # usage as input for process increases balance
                   for stframe, site, process in m.pro_tuples
                   if site == sit and stframe == stf and (stframe, process, com) in m.r_in_dict)
               - sum(m.e_pro_out[(tm, stframe, site, process, com)]
                     # output from processes decreases balance
                     for stframe, site, process in m.pro_tuples
                     if site == sit and stframe == stf and (stframe, process, com) in m.r_out_dict)
               + sum(m.e_tra_in[(tm, stframe, site_in, site_out, transmission, com)]
                     # exports increase balance
                     for stframe, site_in, site_out, transmission, commodity
                     in m.tra_tuples
                     if site_in == sit and stframe == stf and commodity == com)
               - sum(m.e_tra_out[(tm, stframe, site_in, site_out, transmission, com)]
                     # imports decrease balance
                     for stframe, site_in, site_out, transmission, commodity
                     in m.tra_tuples
                     if site_out == sit and stframe == stf and commodity == com)
               + sum(m.e_sto_in[(tm, stframe, site, storage, com)] -
                     m.e_sto_out[(tm, stframe, site, storage, com)]
                     # usage as input for storage increases consumption
                     # output from storage decreases consumption
                     for stframe, site, storage, commodity in m.sto_tuples
                     if site == sit and stframe == stf and commodity == com))
    return balance


def op_pro_tuples(pro_tuple, m):
    """ Tuples for operational status of units (processes, transmissions,
    storages) for intertemporal planning.

    Only such tuples where the unit is still operational until the next
    support time frame are valid.
    """
    op_pro = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, pro) in pro_tuple:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(sorted_stf):
                if stf_later <= stf + m.process.loc[(stf, sit, pro),
                                                    'depreciation']:
                    op_pro.append((sit, pro, stf, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  stf + m.process.loc[(stf, sit, pro), 'depreciation'] and
                  stf <= stf_later):
                op_pro.append((sit, pro, stf, stf_later))
            else:
                pass

    return op_pro


def op_tra_tuples(tra_tuple, m):
    """ s.a. op_pro_tuples
    """
    op_tra = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit1, sit2, tra, com) in tra_tuple:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(sorted_stf):
                if (stf_later <=
                    stf + m.transmission.loc[(stf, sit1, sit2, tra, com),
                                             'depreciation']):
                    op_tra.append((sit1, sit2, tra, com, stf, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  stf + m.transmission.loc[(stf, sit1, sit2, tra, com),
                                           'depreciation'] and
                  stf <= stf_later):
                op_tra.append((sit1, sit2, tra, com, stf, stf_later))
            else:
                pass

    return op_tra


def op_sto_tuples(sto_tuple, m):
    """ s.a. op_pro_tuples
    """
    op_sto = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, sto, com) in sto_tuple:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(sorted_stf):
                if stf_later <= stf + m.storage.loc[(stf, sit, sto, com),
                                                    'depreciation']:
                    op_sto.append((sit, sto, com, stf, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  stf +
                  m.storage.loc[(stf, sit, sto, com), 'depreciation'] and
                  stf <= stf_later):
                op_sto.append((sit, sto, com, stf, stf_later))
            else:
                pass

    return op_sto


def rest_val_pro_tuples(pro_tuple, m):
    """ Tuples for rest value determination of units.

        The last entry represents the remaining life time after the end of the
        modeled time frame.
    """
    rv_pro = []

    for (stf, sit, pro) in pro_tuple:
        if stf + m.process.loc[(stf, sit, pro), 'depreciation'] > max(m.stf):
            rv_pro.append((sit, pro, stf))

    return rv_pro


def rest_val_tra_tuples(tra_tuple, m):
    """ s.a. rest_val_pro_tuples
    """
    rv_tra = []

    for (stf, sit1, sit2, tra, com) in tra_tuple:
        if (stf +
            m.transmission.loc[(stf, sit1, sit2, tra, com), 'depreciation'] >
            max(m.stf)):
            rv_tra.append((sit1, sit2, tra, com, stf))

    return rv_tra


def rest_val_sto_tuples(sto_tuple, m):
    """ s.a. rest_val_pro_tuples
    """
    rv_sto = []

    for (stf, sit, sto, com) in sto_tuple:
        if (stf + m.storage.loc[(stf, sit, sto, com), 'depreciation'] >
            max(m.stf)):
            rv_sto.append((sit, sto, com, stf))

    return rv_sto


def inst_pro_tuples(m):
    """ Tuples for operational status of already installed units
    (processes, transmissions, storages) for intertemporal planning.

    Only such tuples where the unit is still operational until the next
    support time frame are valid.
    """
    inst_pro = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, pro) in m.inst_pro.index:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(m.stf):
                if (stf_later <
                    min(m.stf) + m.process.loc[(stf, sit, pro),
                                               'lifetime']):
                    inst_pro.append((sit, pro, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  min(m.stf) + m.process.loc[(stf, sit, pro),
                                             'lifetime']):
                inst_pro.append((sit, pro, stf_later))

    return inst_pro


def inst_tra_tuples(m):
    """ s.a. inst_pro_tuples
    """
    inst_tra = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit1, sit2, tra, com) in m.inst_tra.index:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(m.stf):
                if (stf_later <
                    min(m.stf) +
                    m.transmission.loc[(stf, sit1, sit2, tra, com),
                                       'lifetime']):
                    inst_tra.append((sit1, sit2, tra, com, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  min(m.stf) + m.transmission.loc[(stf, sit1, sit2, tra, com),
                                                  'lifetime']):
                inst_tra.append((sit1, sit2, tra, com, stf_later))

    return inst_tra


def inst_sto_tuples(m):
    """ s.a. inst_pro_tuples
    """
    inst_sto = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit, sto, com) in m.inst_sto.index:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(m.stf):
                if (stf_later <
                    min(m.stf) + m.storage.loc[(stf, sit, sto, com),
                                               'lifetime']):
                    inst_sto.append((sit, sto, com, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  min(m.stf) + m.storage.loc[(stf, sit, sto, com),
                                             'lifetime']):
                inst_sto.append((sit, sto, com, stf_later))

    return inst_sto


def dsm_down_time_tuples(time, sit_com_tuple, m):
    """ Dictionary for the two time instances of DSM_down


    Args:
        time: list with time indices
        sit_com_tuple: a list of (site, commodity) tuples
        m: model instance

    Returns:
        A list of possible time tuples depending on site and commodity
    """
    if m.dsm.empty:
        return []

    delay = m.dsm['delay']
    ub = max(time)
    lb = min(time)
    time_list = []

    for (stf, site, commodity) in sit_com_tuple:
        for step1 in time:
            for step2 in range(step1 - delay[stf, site, commodity],
                               step1 + delay[stf, site, commodity] + 1):
                if lb <= step2 <= ub:
                    time_list.append((step1, step2, stf, site, commodity))

    return time_list


def dsm_time_tuples(timestep, time, delay):
    """ Tuples for the two time instances of DSM_down

    Args:
        timestep: current timestep
        time: list with time indices
        delay: allowed dsm delay in particular site and commodity

    Returns:
        A list of possible time tuples of a current time step in a specific
        stf, site and commodity
    """

    ub = max(time)
    lb = min(time)

    time_list = list()

    for step in range(timestep - delay, timestep + delay + 1):
        if step >= lb and step <= ub:
            time_list.append(step)

    return time_list


def dsm_recovery(timestep, time, recov):
    """ Time frame for the allowed time indices in case of recovery

    Args:
        timestep: current timestep
        time: list with time indices
        recov: allowed dsm recovery in particular site and commodity

    Returns:
        A list of possible time indices which are within the modelled time
        area
    """

    ub = max(time)

    time_list = list()

    for step in range(timestep, timestep+recov):
        if step <= ub:
            time_list.append(step)

    return time_list


def commodity_subset(com_tuples, type_name):
    """ Unique list of commodity names for given type.

    Args:
        com_tuples: a list of (site, commodity, commodity type) tuples
        type_name: a commodity type or a list of a commodity types

    Returns:
        The set (unique elements/list) of commodity names of the desired type
    """
    if type(type_name) is str:
        # type_name: ('Stock', 'SupIm', 'Env' or 'Demand')
        return set(com for stf, sit, com, com_type in com_tuples
                   if com_type == type_name)
    else:
        # type(type_name) is a class 'pyomo.base.sets.SimpleSet'
        # type_name: ('Buy')=>('Elec buy', 'Heat buy')
        return set((stf, sit, com, com_type) for stf, sit, com, com_type
                   in com_tuples if com in type_name)


def search_sell_buy_tuple(instance, stf, sit_in, pro_in, coin):
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
    # buy_out = (stf, site, output_commodity)
    buy_out = set([(x[0], x[1], x[3])
                   for x in pro_output_tuples
                   if x[2] == pro_in])
    # search the sell process for the output_commodity from the buy process
    sell_output_tuple = ([x
                          for x in pro_output_tuples
                          if x[3] in instance.com_sell])
    for k in range(len(sell_output_tuple)):
        sell_pro = sell_output_tuple[k][2]
        sell_in = set([(x[0], x[1], x[3])
                       for x in pro_input_tuples
                       if x[2] == sell_pro])
        # check: buy - commodity == commodity - sell; for a site
        if not(sell_in.isdisjoint(buy_out)):
            return sell_pro
    return None
