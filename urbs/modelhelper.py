import pandas as pd


def annuity_factor(n, i):
    """Annuity factor formula.

    Evaluates the annuity factor formula for depreciation duration
    and interest rate. Works also well for equally sized numpy arrays
    of values for n and i.

    Args:
        n: depreciation period (years)
        i: interest rate (e.g. 0.06 means 6 %)

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
    balance = (sum(m.e_pro_in[(tm, site, process, com)]
                   # usage as input for process increases balance
                   for site, process in m.pro_tuples
                   if site == sit and (process, com) in m.r_in_dict)
               - sum(m.e_pro_out[(tm, site, process, com)]
                     # output from processes decreases balance
                     for site, process in m.pro_tuples
                     if site == sit and (process, com) in m.r_out_dict)
               + sum(m.e_tra_in[(tm, site_in, site_out, transmission, com)]
                     # exports increase balance
                     for site_in, site_out, transmission, commodity
                     in m.tra_tuples
                     if site_in == sit and commodity == com)
               - sum(m.e_tra_out[(tm, site_in, site_out, transmission, com)]
                     # imports decrease balance
                     for site_in, site_out, transmission, commodity
                     in m.tra_tuples
                     if site_out == sit and commodity == com)
               + sum(m.e_sto_in[(tm, site, storage, com)] -
                     m.e_sto_out[(tm, site, storage, com)]
                     # usage as input for storage increases consumption
                     # output from storage decreases consumption
                     for site, storage, commodity in m.sto_tuples
                     if site == sit and commodity == com))
    return balance


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

    for (site, commodity) in sit_com_tuple:
        for step1 in time:
            for step2 in range(step1 - delay[site, commodity],
                               step1 + delay[site, commodity] + 1):
                if lb <= step2 <= ub:
                    time_list.append((step1, step2, site, commodity))

    return time_list


def dsm_time_tuples(timestep, time, delay):
    """ Tuples for the two time instances of DSM_down

    Args:
        timestep: current timestep
        time: list with time indices
        delay: allowed dsm delay in particular site and commodity

    Returns:
        A list of possible time tuples of a current time step in a specific
        site and commodity
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
        type_name: a commodity type or a ist of a commodity types

    Returns:
        The set (unique elements/list) of commodity names of the desired type
    """
    if type(type_name) is str:
        # type_name: ('Stock', 'SupIm', 'Env' or 'Demand')
        return set(com for sit, com, com_type in com_tuples
                   if com_type == type_name)
    else:
        # type(type_name) is a class 'pyomo.base.sets.SimpleSet'
        # type_name: ('Buy')=>('Elec buy', 'Heat buy')
        return set((sit, com, com_type) for sit, com, com_type in com_tuples
                   if com in type_name)


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
    buy_out = set([(x[0], x[2])
                   for x in pro_output_tuples
                   if x[1] == pro_in])
    # search the sell process for the output_commodity from the buy process
    sell_output_tuple = ([x
                          for x in pro_output_tuples
                          if x[2] in instance.com_sell])
    for k in range(len(sell_output_tuple)):
        sell_pro = sell_output_tuple[k][1]
        sell_in = set([(x[0], x[2])
                       for x in pro_input_tuples
                       if x[1] == sell_pro])
        # check: buy - commodity == commodity - sell; for a site
        if not(sell_in.isdisjoint(buy_out)):
            return sell_pro
    return None
