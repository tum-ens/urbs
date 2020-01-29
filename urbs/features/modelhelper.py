from .transmission import transmission_balance
from .storage import storage_balance


def invcost_factor(dep_prd, interest, discount=None, year_built=None,
                   stf_min=None):
    """Investment cost factor formula.
    Evaluates the factor multiplied to the invest costs
    for depreciation duration and interest rate.
    Args:
        dep_prd: depreciation period (years)
        interest: interest rate (e.g. 0.06 means 6 %)
        year_built: year utility is built
        discount: discount rate for intertmeporal planning
    """
    # invcost factor for non intertemporal planning
    if discount is None:
        if interest == 0:
            return 1 / dep_prd
        else:
            return ((1 + interest) ** dep_prd * interest /
                    ((1 + interest) ** dep_prd - 1))
    # invcost factor for intertemporal planning
    elif discount == 0:
        if interest == 0:
            return 1
        else:
            return (dep_prd * ((1 + interest) ** dep_prd * interest) /
                    ((1 + interest) ** dep_prd - 1))
    else:
        if interest == 0:
            return ((1 + discount) ** (1 - (year_built-stf_min)) *
                    ((1 + discount) ** dep_prd - 1) /
                    (dep_prd * discount * (1 + discount) ** dep_prd))
        else:
            return ((1 + discount) ** (1 - (year_built-stf_min)) *
                    (interest * (1 + interest) ** dep_prd *
                    ((1 + discount) ** dep_prd - 1)) /
                    (discount * (1 + discount) ** dep_prd *
                    ((1+interest) ** dep_prd - 1)))


def overpay_factor(dep_prd, interest, discount, year_built, stf_min, stf_end):
    """Overpay value factor formula.
    Evaluates the factor multiplied to the invest costs
    for all annuity payments of a unit after the end of the
    optimization period.
    Args:
        dep_prd: depreciation period (years)
        interest: interest rate (e.g. 0.06 means 6 %)
        year_built: year utility is built
        discount: discount rate for intertemporal planning
        k: operational time after simulation horizon
    """

    op_time = (year_built + dep_prd) - stf_end - 1

    if discount == 0:
        if interest == 0:
            return op_time / dep_prd
        else:
            return (op_time * ((1 + interest) ** dep_prd * interest) /
                    ((1 + interest) ** dep_prd - 1))
    else:
        if interest == 0:
            return ((1 + discount) ** (1 - (year_built - stf_min)) *
                    ((1 + discount) ** op_time - 1) /
                    (dep_prd * discount * (1 + discount) ** dep_prd))
        else:
            return ((1 + discount) ** (1 - (year_built - stf_min)) *
                    (interest * (1 + interest) ** dep_prd *
                    ((1 + discount) ** op_time - 1)) /
                    (discount * (1 + discount) ** dep_prd *
                    ((1 + interest) ** dep_prd - 1)))


# Energy related costs
def stf_dist(stf, m):
    """Calculates the distance between the modeled support timeframes.
    """
    sorted_stf = sorted(m.stf_list)
    dist = []

    for s in sorted_stf:
        if s == max(sorted_stf):
            dist.append(m.global_prop.loc[(s, 'Weight')]['value'])
        else:
            dist.append(sorted_stf[sorted_stf.index(s) + 1] - s)

    return dist[sorted_stf.index(stf)]


def discount_factor(stf, m):
    """Discount for any payment made in the year stf
    """
    discount = (m.global_prop.xs('Discount rate', level=1)
                .loc[m.global_prop.index.min()[0]]['value'])

    return (1 + discount) ** (1 - (stf - m.global_prop.index.min()[0]))


def effective_distance(dist, m):
    """Factor for variable, fuel, purchase, sell, and fix costs.
    Calculated by repetition of modeled stfs and discount utility.
    """
    discount = (m.global_prop.xs('Discount rate', level=1)
                .loc[m.global_prop.index.min()[0]]['value'])

    if discount == 0:
        return dist
    else:
        return (1 - (1 + discount) ** (-dist)) / discount


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
                   (stframe, process, com) in m.r_in_dict) -
               sum(m.e_pro_out[(tm, stframe, site, process, com)]
                   # output from processes decreases balance
                   for stframe, site, process in m.pro_tuples
                   if site == sit and stframe == stf and
                   (stframe, process, com) in m.r_out_dict))
    if m.mode['tra']:
        balance += transmission_balance(m, tm, stf, sit, com)
    if m.mode['sto']:
        balance += storage_balance(m, tm, stf, sit, com)

    return balance


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
                if (stf_later +
                    m.global_prop.loc[(max(sorted_stf), 'Weight'), 'value'] -
                    1 <= stf + m.process_dict['depreciation'][
                                              (stf, sit, pro)]):
                    op_pro.append((sit, pro, stf, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  stf + m.process_dict['depreciation'][(stf, sit, pro)] and
                  stf <= stf_later):
                op_pro.append((sit, pro, stf, stf_later))
            else:
                pass

    return op_pro


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
                if (stf_later +
                   m.global_prop.loc[(max(sorted_stf), 'Weight'), 'value'] -
                   1 < min(m.stf) + m.process_dict['lifetime'][
                                                   (stf, sit, pro)]):
                    inst_pro.append((sit, pro, stf_later))
            elif (sorted_stf[index_helper+1] <=
                  min(m.stf) + m.process_dict['lifetime'][(stf, sit, pro)]):
                inst_pro.append((sit, pro, stf_later))

    return inst_pro
