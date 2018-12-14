import pandas as pd
from .input import get_input
from .pyomoio import get_entity, get_entities
from .util import is_string


def get_constants(h5):
    """Return summary DataFrames for important variables

    Usage:
        costs, cpro, ctra, csto = get_constants(instance)

    Args:
        instance: a urbs model instance

    Returns:
        (costs, cpro, ctra, csto) tuple
    """
    costs = h5._result["costs"].copy()
    cpro = get_entities(h5._result, ['cap_pro', 'cap_pro_new']).copy()
    ctra = get_entities(h5._result, ['cap_tra', 'cap_tra_new']).copy()
    csto = get_entities(h5._result, ['cap_sto_c', 'cap_sto_c_new',
                                     'cap_sto_p', 'cap_sto_p_new']).copy()

    # better labels and index names and return sorted
    if not cpro.empty:
        cpro.index.names = ['Site', 'Process']
        cpro.columns = ['Total', 'New']
        cpro.sort_index(inplace=True)
    if not ctra.empty:
        ctra.index.names = ['Site In', 'Site Out', 'Transmission', 'Commodity']
        ctra.columns = ['Total', 'New']
        ctra.sort_index(inplace=True)
    if not csto.empty:
        csto.columns = ['C Total', 'C New', 'P Total', 'P New']
        csto.sort_index(inplace=True)

    return costs, cpro, ctra, csto


def get_timeseries(h5, com, sites, timesteps=None):
    """Return DataFrames of all timeseries referring to given commodity

    Usage:
        (created, consumed, stored, imported, exported,
         dsm) = get_timeseries(instance, commodity, sites, timesteps)

    Args:
        h5: loaded h5 file in form of data frame containing model
        com: a commodity name
        sites: a site name or list of site names
        timesteps: optional list of timesteps, default: all modelled timesteps

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
        timesteps = sorted(h5._result['tm'].index)
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
        # and sum all together to form a Series.
        # get_input will use h5._data["demand"]
        demand = (get_input(h5, 'demand').loc[timesteps]
                  .xs(com, axis=1, level=1)[sites].sum(axis=1))
    except KeyError:
        demand = pd.Series(0, index=timesteps)
    demand.name = 'Demand'

    # STOCK
    eco = h5._result['e_co_stock']
    eco = eco.xs([com, 'Stock'], level=['com', 'com_type'])
    try:
        stock = eco.unstack()[sites].sum(axis=1)
    except KeyError:
        stock = pd.Series(0, index=timesteps)
    stock.name = 'Stock'

    # PROCESS
    created = h5._result['e_pro_out']
    created = created.xs(com, level='com').loc[timesteps]
    try:
        created = created.unstack(level='sit')[sites].fillna(0).sum(axis=1)
        created = created.unstack(level='pro')
        created = drop_all_zero_columns(created)
    except KeyError:
        created = pd.DataFrame(index=timesteps)

    consumed = h5._result['e_pro_in']
    consumed = consumed.xs(com, level='com').loc[timesteps]
    try:
        consumed = consumed.unstack(level='sit')[sites].fillna(0).sum(axis=1)
        consumed = consumed.unstack(level='pro')
        consumed = drop_all_zero_columns(consumed)
    except KeyError:
        consumed = pd.DataFrame(index=timesteps)

    # TRANSMISSION
    other_sites = get_input(h5, 'site').index.difference(sites)

    # if commodity is transportable
    df_transmission = get_input(h5, 'transmission')
    if com in tuple(df_transmission.index)[0]:
        imported = h5._result['e_tra_out']
        imported = imported.loc[timesteps].xs(com, level='com')
        imported = imported.unstack(level='tra').sum(axis=1)
        imported = imported.unstack(level='sit_')[sites].fillna(0).sum(axis=1)
        imported = imported.unstack(level='sit')

        internal_import = imported[sites].sum(axis=1)  # ...from sites
        other_sites_im = list(other_sites & imported.columns)
        imported = imported[other_sites_im]  # ...from other_sites
        imported = drop_all_zero_columns(imported)

        exported = h5._result['e_tra_in']
        exported = exported.loc[timesteps].xs(com, level='com')
        exported = exported.unstack(level='tra').sum(axis=1)
        exported = exported.unstack(level='sit')[sites].fillna(0).sum(axis=1)
        exported = exported.unstack(level='sit_')

        internal_export = exported[sites].sum(axis=1)  # ...to sites (internal)
        other_sites_ex = list(other_sites & exported.columns)
        exported = exported[other_sites_ex]  # ...to other_sites
        exported = drop_all_zero_columns(exported)
    else:
        imported = pd.DataFrame(index=timesteps)
        exported = pd.DataFrame(index=timesteps)
        internal_export = pd.Series(0, index=timesteps)
        internal_import = pd.Series(0, index=timesteps)

    # to be discussed: increase demand by internal transmission losses
    internal_transmission_losses = internal_export - internal_import
    demand = demand + internal_transmission_losses

    # STORAGE
    # group storage energies by commodity
    # select all entries with desired commodity co
    stored = pd.DataFrame(h5._result['e_sto_con']).join(pd.DataFrame(
                          h5._result['e_sto_in']).join(pd.DataFrame(
                          h5._result['e_sto_out']), how='outer'), how='outer')
    try:
        stored = stored.loc[timesteps].xs(com, level='com')
        stored = stored.groupby(level=['t', 'sit']).sum()
        stored = stored.loc[(slice(None), sites), :].sum(level='t')
        stored.columns = ['Level', 'Stored', 'Retrieved']
    except (KeyError, ValueError):
        stored = pd.DataFrame(0, index=timesteps,
                              columns=['Level', 'Stored', 'Retrieved'])

    # DEMAND SIDE MANAGEMENT (load shifting)
    dsmup = h5._result['dsm_up']
    dsmdo = h5._result['dsm_down']

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
            dsmup = dsmup.xs(com, level='com')
            dsmdo = dsmdo.xs(com, level='com')

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
