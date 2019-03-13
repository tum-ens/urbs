import pandas as pd
from .input import get_input
from .pyomoio import get_entity, get_entities
from .util import is_string


def get_constants(instance):
    """Return summary DataFrames for important variables

    Usage:
        costs, cpro, ctra, csto = get_constants(instance)

    Args:
        instance: an urbs model instance

    Returns:
        (costs, cpro, ctra, csto) tuple

    Example:
        >>> import pyomo.environ
        >>> from pyomo.opt.base import SolverFactory
        >>> data = read_excel('mimo-example.xlsx')
        >>> prob = create_model(data, range(1,25))
        >>> optim = SolverFactory('glpk')
        >>> result = optim.solve(prob)
        >>> cap_pro = get_constants(prob)[1]['Total']
        >>> cap_pro.xs('Wind park', level='Process').apply(int)
        Site
        Mid      13000
        North    23258
        South        0
        Name: Total, dtype: int64
    """
    costs = get_entity(instance, 'costs')
    cpro = get_entities(instance, ['cap_pro', 'cap_pro_new'])
    ctra = get_entities(instance, ['cap_tra', 'cap_tra_new'])
    csto = get_entities(instance, ['cap_sto_c', 'cap_sto_c_new',
                                   'cap_sto_p', 'cap_sto_p_new'])

    # better labels and index names and return sorted
    if not cpro.empty:
        cpro.index.names = ['Stf', 'Site', 'Process']
        cpro.columns = ['Total', 'New']
        cpro.sort_index(inplace=True)
    if not ctra.empty:
        ctra.index.names = (['Stf', 'Site In', 'Site Out',
                             'Transmission', 'Commodity'])
        ctra.columns = ['Total', 'New']
        ctra.sort_index(inplace=True)
    if not csto.empty:
        csto.index.names = ['Stf', 'Site', 'Storage', 'Commodity']
        csto.columns = ['C Total', 'C New', 'P Total', 'P New']
        csto.sort_index(inplace=True)

    return costs, cpro, ctra, csto


def get_timeseries(instance, stf, com, sites, timesteps=None):
    """Return DataFrames of all timeseries referring to given commodity

    Usage:
        created, consumed, stored, imported, exported,
        dsm = get_timeseries(instance, commodity, sites, timesteps)

    Args:
        - instance: a urbs model instance
        - com: a commodity name
        - sites: a site name or list of site names
        - timesteps: optional list of timesteps, default: all modelled
          timesteps

    Returns:
        a tuple of (created, consumed, storage, imported, exported, dsm) with
        DataFrames timeseries. These are:

        - created: timeseries of commodity creation, including stock source
        - consumed: timeseries of commodity consumption, including demand
        - storage: timeseries of commodity storage (level, stored, retrieved)
        - imported: timeseries of commodity import
        - exported: timeseries of commodity export
        - dsm: timeseries of demand-side management
    """
    if timesteps is None:
        # default to all simulated timesteps
        timesteps = sorted(get_entity(instance, 'tm').index)
    else:
        timesteps = sorted(timesteps)  # implicit: convert range to list

    if is_string(sites):
        # wrap single site name into list
        sites = [sites]

    # DEMAND
    # default to zeros if commodity has no demand, get timeseries
    try:
        # select relevant timesteps (=rows)
        # select commodity (xs), then the sites from remaining simple columns
        # and sum all together to form a Series
        demand = (
            pd.DataFrame.from_dict(
                get_input(
                    instance,
                    'demand_dict')).loc[stf] .loc[timesteps].xs(
                com,
                axis=1,
                level=1)[sites].sum(
                    axis=1))
    except KeyError:
        demand = pd.Series(0, index=timesteps)
    demand.name = 'Demand'

    # STOCK
    eco = get_entity(instance, 'e_co_stock')
    try:
        eco = eco.xs([stf, com, 'Stock'], level=['stf', 'com', 'com_type'])
        stock = eco.unstack()[sites].sum(axis=1)
    except KeyError:
        stock = pd.Series(0, index=timesteps)
    stock.name = 'Stock'

    # PROCESS
    created = get_entity(instance, 'e_pro_out')
    created = created.xs([stf, com], level=['stf', 'com']).loc[timesteps]
    try:
        created = created.unstack(level='sit')[sites].fillna(0).sum(axis=1)
        created = created.unstack(level='pro')
        created = drop_all_zero_columns(created)
    except KeyError:
        created = pd.DataFrame(index=timesteps)

    consumed = get_entity(instance, 'e_pro_in')
    try:
        consumed = consumed.xs([stf, com], level=['stf', 'com']).loc[timesteps]
        consumed = consumed.unstack(level='sit')[sites].fillna(0).sum(axis=1)
        consumed = consumed.unstack(level='pro')
        consumed = drop_all_zero_columns(consumed)
    except KeyError:
        consumed = pd.DataFrame(index=timesteps[1:])

    # TRANSMISSION
    other_sites = (get_input(instance, 'site')
                   .xs(stf, level='support_timeframe').index.difference(sites))

    # if commodity is transportable
    try:
        df_transmission = get_input(instance, 'transmission')
        if com in set(df_transmission.index.get_level_values('Commodity')):
            imported = get_entity(instance, 'e_tra_out')
            imported = imported.loc[timesteps].xs(
                [stf, com], level=['stf', 'com'])
            imported = imported.unstack(level='tra').sum(axis=1)
            imported = imported.unstack(
                level='sit_')[sites].fillna(0).sum(
                axis=1)
            imported = imported.unstack(level='sit')

            internal_import = imported[sites].sum(axis=1)  # ...from sites
            imported = imported[other_sites]  # ...from other_sites
            imported = drop_all_zero_columns(imported)

            exported = get_entity(instance, 'e_tra_in')
            exported = exported.loc[timesteps].xs(
                [stf, com], level=['stf', 'com'])
            exported = exported.unstack(level='tra').sum(axis=1)
            exported = exported.unstack(
                level='sit')[sites].fillna(0).sum(
                axis=1)
            exported = exported.unstack(level='sit_')

            internal_export = exported[sites].sum(
                axis=1)  # ...to sites (internal)
            exported = exported[other_sites]  # ...to other_sites
            exported = drop_all_zero_columns(exported)
        else:
            imported = pd.DataFrame(index=timesteps)
            exported = pd.DataFrame(index=timesteps)
            internal_export = pd.Series(0, index=timesteps)
            internal_import = pd.Series(0, index=timesteps)

        # to be discussed: increase demand by internal transmission losses
        internal_transmission_losses = internal_export - internal_import
        demand = demand + internal_transmission_losses
    except KeyError:
        # imported and exported are empty
        imported = exported = pd.DataFrame(index=timesteps)

    # STORAGE
    # group storage energies by commodity
    # select all entries with desired commodity co
    stored = get_entities(instance, ['e_sto_con', 'e_sto_in', 'e_sto_out'])
    try:
        stored = stored.loc[timesteps].xs([stf, com], level=['stf', 'com'])
        stored = stored.groupby(level=['t', 'sit']).sum()
        stored = stored.loc[(slice(None), sites), :].sum(level='t')
        stored.columns = ['Level', 'Stored', 'Retrieved']
    except (KeyError, ValueError):
        stored = pd.DataFrame(0, index=timesteps,
                              columns=['Level', 'Stored', 'Retrieved'])

    # DEMAND SIDE MANAGEMENT (load shifting)
    dsmup = get_entity(instance, 'dsm_up')
    dsmdo = get_entity(instance, 'dsm_down')

    if dsmup.empty:
        # if no DSM happened, the demand is not modified (delta = 0)
        delta = pd.Series(0, index=timesteps)

    else:
        # DSM happened (dsmup implies that dsmdo must be non-zero, too)
        # so the demand will be modified by the difference of DSM up and
        # DSM down uses
        # for sit in m.dsm_site_tuples:
        try:
            # select commodity
            dsmup = dsmup.xs([stf, com], level=['stf', 'com'])
            dsmdo = dsmdo.xs([stf, com], level=['stf', 'com'])

            # select sites
            dsmup = dsmup.unstack()[sites].sum(axis=1)
            dsmdo = dsmdo.unstack()[sites].sum(axis=1)

            # convert dsmdo to Series by summing over the first time level
            dsmdo = dsmdo.unstack().sum(axis=0)
            dsmdo.index.names = ['t']

            # derive secondary timeseries
            delta = dsmup - dsmdo
        except KeyError:
            delta = pd.Series(0, index=timesteps)

    shifted = demand + delta

    shifted.name = 'Shifted'
    demand.name = 'Unshifted'
    delta.name = 'Delta'

    dsm = pd.concat((shifted, demand, delta), axis=1)

    # JOINS
    created = created.join(stock)  # show stock as created
    consumed = consumed.join(shifted.rename('Demand'))

    return created, consumed, stored, imported, exported, dsm


def drop_all_zero_columns(df):
    """ Drop columns from DataFrame if they contain only zeros.

    Args:
        df: a DataFrame

    Returns:
        the DataFrame without columns that only contain zeros
    """
    return df.loc[:, (df != 0).any(axis=0)]
