import pandas as pd
import os
import glob
from xlrd import XLRDError
import pyomo.core as pyomo
from .modelhelper import *


def read_intertemporal(folder):
    glob_input = os.path.join(folder, '*.xlsx')
    input_files = sorted(glob.glob(glob_input))
    return input_files


def read_excel(input_files):
    """Read Excel input file and prepare URBS input dict.

    Reads an Excel spreadsheet that adheres to the structure shown in
    mimo-example.xlsx. Two preprocessing steps happen here:
    1. Column titles in 'Demand' and 'SupIm' are split, so that
    'Site.Commodity' becomes the MultiIndex column ('Site', 'Commodity').
    2. The attribute 'annuity-factor' is derived here from the columns 'wacc'
    and 'depreciation' for 'Process', 'Transmission' and 'Storage'.

    Args:
        filename: filename to an Excel spreadsheet with the required sheets
            'Commodity', 'Process', 'Transmission', 'Storage', 'Demand' and
            'SupIm'.

    Returns:
        a dict of 6 DataFrames

    Example:
        >>> data = read_excel('mimo-example.xlsx')
        >>> data['global_prop'].loc['CO2 limit', 'value']
        150000000
    """

    gl = []
    sit = []
    com = []
    pro = []
    pro_com = []
    tra = []
    sto = []
    dem = []
    sup = []
    bsp = []
    ds = []

    for filename in input_files:
        with pd.ExcelFile(filename) as xls:
            global_prop = xls.parse('Global').set_index(['Property'])
            support_timeframe = global_prop.loc['Support timeframe']['value']
            global_prop = (
                global_prop.drop(['Support timeframe'])
                .drop(['description'], axis=1))

            global_prop = pd.concat([global_prop], keys=[support_timeframe],
                                    names=['support_timeframe'])
            gl.append(global_prop)
            site = xls.parse('Site').set_index(['Name'])
            site = pd.concat([site], keys=[support_timeframe],
                             names=['support_timeframe'])
            sit.append(site)
            commodity = (
                xls.parse('Commodity')
                   .set_index(['Site', 'Commodity', 'Type']))
            commodity = pd.concat([commodity], keys=[support_timeframe],
                                  names=['support_timeframe'])
            com.append(commodity)
            process = xls.parse('Process').set_index(['Site', 'Process'])
            process = pd.concat([process], keys=[support_timeframe],
                                names=['support_timeframe'])
            pro.append(process)
            process_commodity = (
                xls.parse('Process-Commodity')
                   .set_index(['Process', 'Commodity', 'Direction']))
            process_commodity = pd.concat([process_commodity],
                                          keys=[support_timeframe],
                                          names=['support_timeframe'])
            pro_com.append(process_commodity)
            transmission = (
                xls.parse('Transmission')
                   .set_index(['Site In', 'Site Out',
                              'Transmission', 'Commodity']))
            transmission = pd.concat([transmission], keys=[support_timeframe],
                                     names=['support_timeframe'])
            tra.append(transmission)
            storage = (
                xls.parse('Storage')
                   .set_index(['Site', 'Storage', 'Commodity']))
            storage = pd.concat([storage], keys=[support_timeframe],
                                names=['support_timeframe'])
            sto.append(storage)
            demand = xls.parse('Demand').set_index(['t'])
            demand = pd.concat([demand], keys=[support_timeframe],
                               names=['support_timeframe'])
            dem.append(demand)
            supim = xls.parse('SupIm').set_index(['t'])
            supim = pd.concat([supim], keys=[support_timeframe],
                              names=['support_timeframe'])
            sup.append(supim)
            buy_sell_price = xls.parse('Buy-Sell-Price').set_index(['t'])
            buy_sell_price = pd.concat([buy_sell_price],
                                       keys=[support_timeframe],
                                       names=['support_timeframe'])
            bsp.append(buy_sell_price)
            dsm = xls.parse('DSM').set_index(['Site', 'Commodity'])
            dsm = pd.concat([dsm], keys=[support_timeframe],
                            names=['support_timeframe'])
            ds.append(dsm)

        # prepare input data
        # split columns by dots '.', so that 'DE.Elec' becomes the two-level
        # column index ('DE', 'Elec')
        demand.columns = split_columns(demand.columns, '.')
        supim.columns = split_columns(supim.columns, '.')
        buy_sell_price.columns = split_columns(buy_sell_price.columns, '.')

    data = {
        'global_prop': pd.concat(gl),
        'site': pd.concat(sit),
        'commodity': pd.concat(com),
        'process': pd.concat(pro),
        'process_commodity': pd.concat(pro_com),
        'transmission': pd.concat(tra),
        'storage': pd.concat(sto),
        'demand': pd.concat(dem),
        'supim': pd.concat(sup),
        'buy_sell_price': pd.concat(bsp),
        'dsm': pd.concat(ds)
        }

    # sort nested indexes to make direct assignments work
    for key in data:
        if isinstance(data[key].index, pd.core.index.MultiIndex):
            data[key].sort_index(inplace=True)
    return data


# preparing the pyomo model
def pyomo_model_prep(data, timesteps):
    m = pyomo.ConcreteModel()

    # Preparations
    # ============
    # Data import. Syntax to access a value within equation definitions looks
    # like this:
    #
    #     m.storage.loc[site, storage, commodity][attribute]
    #
    m.global_prop = data['global_prop']
    m.site = data['site']
    m.commodity = data['commodity']
    m.process = data['process']
    m.process_commodity = data['process_commodity']
    m.transmission = data['transmission']
    m.storage = data['storage']
    m.demand = data['demand']
    m.supim = data['supim']
    m.buy_sell_price = data['buy_sell_price']
    m.timesteps = timesteps
    m.dsm = data['dsm']

    # Create columns of support timeframe values
    m.commodity['support_timeframe'] = (m.commodity.index.
                                        get_level_values('support_timeframe'))
    m.process['support_timeframe'] = (m.process.index.
                                      get_level_values('support_timeframe'))
    m.transmission['support_timeframe'] = (m.transmission.index.
                                           get_level_values
                                           ('support_timeframe'))
    m.storage['support_timeframe'] = (m.storage.index.
                                      get_level_values('support_timeframe'))

    # Converting Data frames to dict
    m.demand_dict = m.demand.to_dict()
    m.supim_dict = m.supim.to_dict()
    m.dsm_dict = m.dsm.to_dict()
    m.buy_sell_price_dict = m.buy_sell_price.to_dict()

    # process input/output ratios
    m.r_in = m.process_commodity.xs('In', level='Direction')['ratio']
    m.r_out = m.process_commodity.xs('Out', level='Direction')['ratio']
    m.r_in_dict = m.r_in.to_dict()
    m.r_out_dict = m.r_out.to_dict()

    # process areas
    m.proc_area = m.process['area-per-cap']
    m.sit_area = m.site['area']
    m.proc_area = m.proc_area[m.proc_area >= 0]
    m.sit_area = m.sit_area[m.sit_area >= 0]

    # installed units for intertemporal planning
    m.inst_pro = m.process['inst-cap']
    m.inst_pro = m.inst_pro[m.inst_pro > 0]
    m.inst_tra = m.transmission['inst-cap']
    m.inst_tra = m.inst_tra[m.inst_tra > 0]
    m.inst_sto = m.storage['inst-cap-p']
    m.inst_sto = m.inst_sto[m.inst_sto > 0]

    # input ratios for partial efficiencies
    # only keep those entries whose values are
    # a) positive and
    # b) numeric (implicitely, as NaN or NV compare false against 0)
    m.r_in_min_fraction = m.process_commodity.xs('In', level='Direction')
    m.r_in_min_fraction = m.r_in_min_fraction['ratio-min']
    m.r_in_min_fraction = m.r_in_min_fraction[m.r_in_min_fraction > 0]

    # output ratios for partial efficiencies
    # only keep those entries whose values are
    # a) positive and
    # b) numeric (implicitely, as NaN or NV compare false against 0)
    m.r_out_min_fraction = m.process_commodity.xs('Out', level='Direction')
    m.r_out_min_fraction = m.r_out_min_fraction['ratio-min']
    m.r_out_min_fraction = m.r_out_min_fraction[m.r_out_min_fraction > 0]

    # derive invest factor from WACC, depreciation and discount untility
    m.process['invcost-factor'] = invcost_factor(
        m,
        m.process['depreciation'],
        m.process['wacc'], m.process['support_timeframe'])
    m.transmission['invcost-factor'] = invcost_factor(
        m,
        m.transmission['depreciation'],
        m.transmission['wacc'], m.transmission['support_timeframe'])
    m.storage['invcost-factor'] = invcost_factor(
        m,
        m.storage['depreciation'],
        m.storage['wacc'], m.storage['support_timeframe'])

    # derive rest value factor from WACC, depreciation and discount untility
    m.process['rv-factor'] = rv_factor(
        m,
        m.process['depreciation'],
        m.process['wacc'], m.process['support_timeframe'])
    m.process.loc[(m.process['rv-factor'] < 0) |
                  (m.process['rv-factor'].isnull()), 'rv-factor'] = 0
    m.transmission['rv-factor'] = rv_factor(
        m,
        m.transmission['depreciation'],
        m.transmission['wacc'], m.transmission['support_timeframe'])
    try:
        m.transmission.loc[(m.transmission['rv-factor'] < 0) |
                           (m.transmission['rv-factor'].isnull()),
                           'rv-factor'] = 0
    except TypeError:
        pass
    m.storage['rv-factor'] = rv_factor(
        m,
        m.storage['depreciation'],
        m.storage['wacc'], m.storage['support_timeframe'])
    try:
        m.storage.loc[(m.storage['rv-factor'] < 0) |
                      (m.storage['rv-factor'].isnull()), 'rv-factor'] = 0
    except TypeError:
        pass

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

    # Converting Data frames to dictionaries
    #
    m.commodity_dict = m.commodity.to_dict()
    m.process_dict = m.process.to_dict()  # Changed
    m.transmission_dict = m.transmission.to_dict()  # Changed
    m.storage_dict = m.storage.to_dict()  # Changed
    return m


def split_columns(columns, sep='.'):
    """Split columns by separator into MultiIndex.

    Given a list of column labels containing a separator string (default: '.'),
    derive a MulitIndex that is split at the separator string.

    Args:
        columns: list of column labels, containing the separator string
        sep: the separator string (default: '.')

    Returns:
        a MultiIndex corresponding to input, with levels split at separator

    Example:
        >>> split_columns(['DE.Elec', 'MA.Elec', 'NO.Wind'])
        MultiIndex(levels=[['DE', 'MA', 'NO'], ['Elec', 'Wind']],
                   labels=[[0, 1, 2], [0, 0, 1]])

    """
    if len(columns) == 0:
        return columns
    column_tuples = [tuple(col.split('.')) for col in columns]
    return pd.MultiIndex.from_tuples(column_tuples)


def get_input(prob, name):
    """Return input DataFrame of given name from urbs instance.

    These are identical to the key names returned by function `read_excel`.
    That means they are lower-case names and use underscores for word
    separation, e.g. 'process_commodity'.

    Args:
        prob: a urbs model instance
        name: an input DataFrame name ('commodity', 'process', ...)

    Returns:
        the corresponding input DataFrame

    """
    if hasattr(prob, name):
        # classic case: input data DataFrames are accessible via named
        # attributes, e.g. `prob.process`.
        return getattr(prob, name)
    elif hasattr(prob, '_data') and name in prob._data:
        # load case: input data is accessible via the input data cache dict
        return prob._data[name]
    else:
        # unknown
        raise ValueError("Unknown input DataFrame name!")
