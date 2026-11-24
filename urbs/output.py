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


def get_transmission_neighbors(instance, stf, com, sites):
    """Sites connected by transmission links for import/export columns."""
    import_sources = set()
    export_destinations = set()
    sites_set = set(sites)
    try:
        df_transmission = get_input(instance, 'transmission')
        tra = df_transmission.xs(stf, level='support_timeframe')
        for idx in tra.index:
            site_in, site_out, commodity = idx[0], idx[1], idx[3]
            if commodity != com:
                continue
            if site_out in sites_set and site_in not in sites_set:
                import_sources.add(site_in)
            if site_in in sites_set and site_out not in sites_set:
                export_destinations.add(site_out)
    except (KeyError, AttributeError, IndexError):
        pass
    return sorted(import_sources), sorted(export_destinations)


def _flow_timesteps(instance, timesteps):
    """Return timesteps that carry process/transmission flows (tm, not storage init)."""
    timesteps = sorted(timesteps)
    try:
        tm = set(get_entity(instance, 'tm').index)
    except (KeyError, AttributeError):
        tm = set(timesteps[1:]) if len(timesteps) > 1 else set(timesteps)
    flow = [t for t in timesteps if t in tm]
    return flow if flow else sorted(tm)


def ensure_neighbor_columns(df, neighbors, timesteps):
    """Keep configured transmission neighbors as columns even when flow is zero."""
    df = df.reindex(index=timesteps, fill_value=0)
    if not neighbors:
        return df.fillna(0)
    for neighbor in neighbors:
        if neighbor not in df.columns:
            df[neighbor] = 0.0
    return df[sorted(neighbors)].fillna(0)


def _co_market_series(instance, entity_name, stf, com, com_type, sites, timesteps):
    """Extract e_co_sell / e_co_buy for one commodity as a site-summed series."""
    zeros = pd.Series(0, index=timesteps)
    data = get_entity(instance, entity_name)
    if data is None or getattr(data, 'empty', True):
        return zeros
    if getattr(data.index, 'nlevels', 1) < 2:
        return zeros
    try:
        data = data.xs((stf, com, com_type), level=['stf', 'com', 'com_type'])
        if 'sit' in (data.index.names or []):
            data = data.unstack(level='sit')
        else:
            data = data.unstack()
        data = data.reindex(columns=sites).fillna(0).sum(axis=1)
        return data.reindex(timesteps, fill_value=0)
    except (KeyError, TypeError, ValueError, IndexError):
        return zeros


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

    # Process and transmission variables are indexed on tm (excludes t=0).
    flow_timesteps = _flow_timesteps(instance, timesteps)

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
        demand = pd.Series(0, index=flow_timesteps)
    demand = demand.reindex(flow_timesteps, fill_value=0)
    demand.name = 'Demand'

    # STOCK
    eco = get_entity(instance, 'e_co_stock')
    try:
        eco = eco.xs((stf, com, 'Stock'), level=['stf', 'com', 'com_type'])
        stock = eco.unstack()[sites].sum(axis=1)
        stock = stock.reindex(flow_timesteps, fill_value=0)
    except KeyError:
        stock = pd.Series(0, index=flow_timesteps)
    stock.name = 'Stock'

    # BUY / SELL commodity exchange with the market
    sell = _co_market_series(
        instance, 'e_co_sell', stf, com, 'Sell', sites, flow_timesteps
    )
    sell.name = 'Sell'
    buy = _co_market_series(
        instance, 'e_co_buy', stf, com, 'Buy', sites, flow_timesteps
    )
    buy.name = 'Buy'

    # PROCESS
    created = get_entity(instance, 'e_pro_out')
    try:
        created = created.xs((stf, com), level=['stf', 'com']).loc[flow_timesteps]
        created = created.unstack(level='sit')[sites].fillna(0).sum(axis=1)
        created = created.unstack(level='pro')
        created = drop_all_zero_columns(created)
    except KeyError:
        created = pd.DataFrame(index=flow_timesteps)

    consumed = get_entity(instance, 'e_pro_in')
    try:
        consumed = consumed.xs((stf, com), level=['stf', 'com']).loc[flow_timesteps]
        consumed = consumed.unstack(level='sit')[sites].fillna(0).sum(axis=1)
        consumed = consumed.unstack(level='pro')
        consumed = drop_all_zero_columns(consumed)
    except KeyError:
        consumed = pd.DataFrame(index=flow_timesteps)

    # TRANSMISSION
    other_sites = (get_input(instance, 'site')
                   .xs(stf, level='support_timeframe').index.difference(sites))
    import_sources, export_destinations = get_transmission_neighbors(
        instance, stf, com, sites)

    # if commodity is transportable
    try:
        df_transmission = get_input(instance, 'transmission')
        if com in set(df_transmission.index.get_level_values('Commodity')):
            imported = get_entity(instance, 'e_tra_out')
            # avoid negative value import for DCPF transmissions
            if instance.mode['dpf']:
                # -0.01 to avoid numerical errors such as -0
                minus_imported = imported[(imported < -0.01)]
                minus_imported = -1 * minus_imported.swaplevel('sit', 'sit_')
                imported = imported[imported >= 0]
                imported = pd.concat([imported, minus_imported])
            imported = imported.loc[flow_timesteps].xs(
                (stf, com), level=['stf', 'com'])
            imported = imported.unstack(level='tra').sum(axis=1)
            imported = imported.unstack(
                level='sit_').reindex(columns=sites).fillna(0).sum(
                axis=1)
            imported = imported.unstack(level='sit')

            # A single site never imports from itself, and a one-directional
            # line means the queried site may be absent from the columns.
            # reindex tolerates missing columns instead of raising KeyError
            # (which previously zeroed out all transmission flows).
            internal_import = imported.reindex(
                columns=sites).fillna(0).sum(axis=1)  # ...from sites
            if instance.mode['dpf']:
                imported = imported[[x for x in other_sites if x in imported.keys()]]  # ...to existing other_sites
            else:
                imported = imported.reindex(columns=other_sites, fill_value=0)
            imported = ensure_neighbor_columns(
                imported.fillna(0), import_sources, flow_timesteps)

            exported = get_entity(instance, 'e_tra_in')
            # avoid negative value export for DCPF transmissions
            if instance.mode['dpf']:
                # -0.01 to avoid numerical errors such as -0
                minus_exported = exported[(exported < -0.01)]
                minus_exported = -1 * minus_exported.swaplevel('sit', 'sit_')
                exported = exported[exported >= 0]
                exported = pd.concat([exported, minus_exported])
            exported = exported.loc[flow_timesteps].xs(
                (stf, com), level=['stf', 'com'])
            exported = exported.unstack(level='tra').sum(axis=1)
            exported = exported.unstack(
                level='sit').reindex(columns=sites).fillna(0).sum(
                axis=1)
            exported = exported.unstack(level='sit_')

            # A single site never exports to itself, and a one-directional
            # line means the queried site may be absent from the columns.
            # reindex tolerates missing columns instead of raising KeyError
            # (which previously zeroed out all transmission flows).
            internal_export = exported.reindex(
                columns=sites).fillna(0).sum(axis=1)  # ...to sites (internal)
            if instance.mode['dpf']:
                exported = exported[[x for x in other_sites if x in exported.keys()]]  # ...to existing other_sites
            else:
                exported = exported.reindex(columns=other_sites, fill_value=0)
            exported = ensure_neighbor_columns(
                exported.fillna(0), export_destinations, flow_timesteps)
        else:
            imported = ensure_neighbor_columns(
                pd.DataFrame(index=flow_timesteps), import_sources, flow_timesteps)
            exported = ensure_neighbor_columns(
                pd.DataFrame(index=flow_timesteps), export_destinations, flow_timesteps)
            internal_export = pd.Series(0, index=flow_timesteps)
            internal_import = pd.Series(0, index=flow_timesteps)

        # to be discussed: increase demand by internal transmission losses
        internal_transmission_losses = internal_export - internal_import
        demand = demand + internal_transmission_losses.reindex(demand.index, fill_value=0)
    except KeyError:
        imported = ensure_neighbor_columns(
            pd.DataFrame(index=flow_timesteps), import_sources, flow_timesteps)
        exported = ensure_neighbor_columns(
            pd.DataFrame(index=flow_timesteps), export_destinations, flow_timesteps)

    # STORAGE
    # group storage energies by commodity
    # select all entries with desired commodity co
    stored = get_entities(instance, ['e_sto_con', 'e_sto_in', 'e_sto_out'])
    try:
        stored = stored.loc[flow_timesteps].xs((stf, com), level=['stf', 'com'])
        stored = stored.groupby(level=['t', 'sit']).sum()
        stored = stored.loc[(slice(None), sites), :].groupby('t').sum()
        stored.columns = ['Level', 'Stored', 'Retrieved']
        stored = stored.reindex(flow_timesteps, fill_value=0)
    except (KeyError, ValueError):
        stored = pd.DataFrame(0, index=flow_timesteps,
                              columns=['Level', 'Stored', 'Retrieved'])

    # DEMAND SIDE MANAGEMENT (load shifting)
    dsmup = get_entity(instance, 'dsm_up')
    dsmdo = get_entity(instance, 'dsm_down')

    if dsmup.empty:
        # if no DSM happened, the demand is not modified (delta = 0)
        delta = pd.Series(0, index=flow_timesteps)

    else:
        # DSM happened (dsmup implies that dsmdo must be non-zero, too)
        # so the demand will be modified by the difference of DSM up and
        # DSM down uses
        # for sit in m.dsm_site_tuples:
        try:
            # select commodity
            dsmup = dsmup.xs((stf, com), level=['stf', 'com'])
            dsmdo = dsmdo.xs((stf, com), level=['stf', 'com'])

            # select sites
            dsmup = dsmup.unstack()[sites].sum(axis=1)
            dsmdo = dsmdo.unstack()[sites].sum(axis=1)

            # convert dsmdo to Series by summing over the first time level
            dsmdo = dsmdo.unstack().sum(axis=0)
            dsmdo.index.names = ['t']

            # derive secondary timeseries
            delta = dsmup - dsmdo
            delta = delta.reindex(flow_timesteps, fill_value=0)
        except KeyError:
            delta = pd.Series(0, index=flow_timesteps)

    shifted = demand + delta

    shifted.name = 'Shifted'
    demand.name = 'Unshifted'
    delta.name = 'Delta'

    dsm = pd.concat((shifted, demand, delta), axis=1)

    # JOINS
    created = created.join(stock)  # show stock as created
    created = created.join(buy)  # purchased Buy commodity
    consumed = consumed.join(shifted.rename('Demand'))
    consumed = consumed.join(sell)  # sold Sell commodity

    # VOLTAGE ANGLE of sites

    try:
        voltage_angle = get_entity(instance, 'voltage_angle')
        voltage_angle = voltage_angle.xs(stf, level=['stf']).loc[flow_timesteps]
        voltage_angle = voltage_angle.unstack(level='sit')[sites]
    except (KeyError, AttributeError, TypeError):
        voltage_angle = pd.DataFrame(index=flow_timesteps)
    voltage_angle.name = 'Voltage Angle'

    return created, consumed, stored, imported, exported, dsm, voltage_angle


def drop_all_zero_columns(df):
    """ Drop columns from DataFrame if they contain only zeros.

    Args:
        df: a DataFrame

    Returns:
        the DataFrame without columns that only contain zeros
    """
    return df.loc[:, (df != 0).any(axis=0)]
