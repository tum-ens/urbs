import pandas as pd
import os
import glob
from xlrd import XLRDError
import pyomo.core as pyomo
from .modelhelper import *
from .identi import identify_mode
from .int_modelhelper import *



def read_input(input_files):
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
    glob_input = os.path.join(input_files, '*.xlsx')
    input_files = sorted(glob.glob(glob_input))
    
    tra_mod,sto_mod,dsm_mod,int_mod = identify_mode(input_files)
    
    if int_mod:
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
            
            site = xls.parse('Site').set_index(['Name'])           
            
            commodity = (
                xls.parse('Commodity')
                   .set_index(['Site', 'Commodity', 'Type']))
            
            process = xls.parse('Process').set_index(['Site', 'Process'])
            
            process_commodity = (
                xls.parse('Process-Commodity')
                   .set_index(['Process', 'Commodity', 'Direction']))

            demand = xls.parse('Demand').set_index(['t'])

            supim = xls.parse('SupIm').set_index(['t'])

            buy_sell_price = xls.parse('Buy-Sell-Price').set_index(['t'])
            
            if tra_mod:
                transmission = (
                    xls.parse('Transmission')
                       .set_index(['Site In', 'Site Out',
                                  'Transmission', 'Commodity']))
            if sto_mod:
                storage = (
                    xls.parse('Storage')
                       .set_index(['Site', 'Storage', 'Commodity']))            

            if dsm_mod:               
                dsm = xls.parse('DSM').set_index(['Site', 'Commodity'])

            if int_mod:
                support_timeframe = global_prop.loc['Support timeframe']['value']
                global_prop = (
                    global_prop.drop(['Support timeframe'])
                    .drop(['description'], axis=1))

                global_prop = pd.concat([global_prop], keys=[support_timeframe],
                                        names=['support_timeframe'])
                gl.append(global_prop)
                site = pd.concat([site], keys=[support_timeframe],
                                 names=['support_timeframe'])
                sit.append(site)
                commodity = pd.concat([commodity], keys=[support_timeframe],
                                      names=['support_timeframe'])
                com.append(commodity)
                process = pd.concat([process], keys=[support_timeframe],
                                    names=['support_timeframe'])
                pro.append(process)
                process_commodity = pd.concat([process_commodity],
                                              keys=[support_timeframe],
                                              names=['support_timeframe'])
                pro_com.append(process_commodity)
                transmission = pd.concat([transmission], keys=[support_timeframe],
                                         names=['support_timeframe'])
                tra.append(transmission)         
                storage = pd.concat([storage], keys=[support_timeframe],
                                    names=['support_timeframe'])
                sto.append(storage)
                demand = pd.concat([demand], keys=[support_timeframe],
                                   names=['support_timeframe'])
                dem.append(demand)    
                supim = pd.concat([supim], keys=[support_timeframe],
                                  names=['support_timeframe'])
                sup.append(supim)   
                buy_sell_price = pd.concat([buy_sell_price],
                                           keys=[support_timeframe],
                                           names=['support_timeframe'])
                bsp.append(buy_sell_price)   
                dsm = pd.concat([dsm], keys=[support_timeframe],
                                names=['support_timeframe'])
                ds.append(dsm)     

                
        # prepare input data
        # split columns by dots '.', so that 'DE.Elec' becomes the two-level
        # column index ('DE', 'Elec')
        demand.columns = split_columns(demand.columns, '.')
        supim.columns = split_columns(supim.columns, '.')
        buy_sell_price.columns = split_columns(buy_sell_price.columns, '.')
    
    if int_mod:
        data = {
            'global_prop': pd.concat(gl),
            'site': pd.concat(sit),
            'commodity': pd.concat(com),
            'process': pd.concat(pro),
            'process_commodity': pd.concat(pro_com),
            'demand': pd.concat(dem),
            'supim': pd.concat(sup),
            'buy_sell_price': pd.concat(bsp)
            }
        if tra_mod:
            data['transmission'] = pd.concat(tra)
        if sto_mod:
            data['storage'] = pd.concat(sto)
        if dsm_mod:
            data['dsm'] = pd.concat(ds)
    else:
        data = {
            'global_prop': global_prop,
            'site': site,
            'commodity': commodity,
            'process': process,
            'process_commodity': process_commodity,
            'demand': demand,
            'supim': supim,
            'buy_sell_price': buy_sell_price
            }
        if tra_mod:
            data['transmission'] = transmission
        if sto_mod:
            data['storage'] = storage
        if dsm_mod:
            data['dsm'] = dsm

    mode = {
        'tra': tra_mod,
        'sto': sto_mod,
        'dsm': dsm_mod,
        'int': int_mod
        }
    
    # sort nested indexes to make direct assignments work
    for key in data:
        if isinstance(data[key].index, pd.core.index.MultiIndex):
            data[key].sort_index(inplace=True)

    return data,mode


# preparing the pyomo model
def pyomo_model_prep(data, mode, timesteps):
    m = pyomo.ConcreteModel()
    #create mode
    m.mode = mode
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
    m.demand = data['demand']
    m.supim = data['supim']
    m.buy_sell_price = data['buy_sell_price']
    m.timesteps = timesteps
    
    #Create expandable and const processes
    m.process_exp = m.process[m.process['inst-cap'] < m.process['cap-up']]
    m.process_const = m.process[m.process['inst-cap'] >= m.process['cap-up']]
    
    # Data for optional modes
    # Transmission
    if m.mode['tra']:
        m.transmission = data['transmission']  
        # expandable and const transmission
        m.transmission_exp = m.transmission[m.transmission['inst-cap'] < m.transmission['cap-up']]
        m.transmission_const = m.transmission[m.transmission['inst-cap'] >= m.transmission['cap-up']]
    # Storage
    if m.mode['sto']:
        m.storage = data['storage']
        # expandable and const storage
        m.storage_exp_c = m.storage[m.storage['inst-cap-c'] < m.storage['cap-up-c']]
        m.storage_const_c = m.storage[m.storage['inst-cap-c'] >= m.storage['cap-up-c']]
        m.storage_exp_p = m.storage[m.storage['inst-cap-p'] < m.storage['cap-up-p']]
        m.storage_const_p = m.storage[m.storage['inst-cap-p'] >= m.storage['cap-up-p']]
    # DSM
    if m.mode['dsm']:
        m.dsm = data['dsm']
        
        
    # Create columns of support timeframe values
    if m.mode['int']:
        m.commodity['support_timeframe'] = (m.commodity.index.
                                            get_level_values('support_timeframe'))
        m.process['support_timeframe'] = (m.process.index.
                                          get_level_values('support_timeframe'))
        m.transmission['support_timeframe'] = (m.transmission.index.
                                               get_level_values
                                               ('support_timeframe'))
        m.storage['support_timeframe'] = (m.storage.index.
                                          get_level_values('support_timeframe'))

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

    #create expandable and const process areas
    m.proc_area_exp = m.proc_area[m.process['inst-cap'] < m.process['cap-up']] 
    m.proc_area_const = m.proc_area[m.process['inst-cap'] >= m.process['cap-up']]
    
    if m.mode['int']:
        # installed units for intertemporal planning
        m.inst_pro = m.process['inst-cap']
        m.inst_pro = m.inst_pro[m.inst_pro > 0]
        if m.mode['tra']:
            m.inst_tra = m.transmission['inst-cap']
            m.inst_tra = m.inst_tra[m.inst_tra > 0]
        if m.mode['sto']:
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

    if m.mode['int']:
        # derive invest factor from WACC, depreciation and discount untility
        m.process['invcost-factor'] = invcost_factor(
            m,
            m.process['depreciation'],
            m.process['wacc'], m.process['support_timeframe'])
        # derive rest value factor from WACC, depreciation and discount untility
        m.process['rv-factor'] = rv_factor(
            m,
            m.process['depreciation'],
            m.process['wacc'], m.process['support_timeframe'])
        m.process.loc[(m.process['rv-factor'] < 0) |
                    (m.process['rv-factor'].isnull()), 'rv-factor'] = 0
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
        
        if m.mode['tra']:
            m.transmission['invcost-factor'] = invcost_factor(
                m,
                m.transmission['depreciation'],
                m.transmission['wacc'], m.transmission['support_timeframe'])
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
            m.transmission['stf_dist'] = (m.transmission['support_timeframe'].
                                          apply(stf_dist, m=m))
            m.transmission['c_helper'] = (m.transmission['support_timeframe'].
                                          apply(cost_helper, m=m))
            m.transmission['c_helper2'] = (m.transmission['stf_dist'].
                                           apply(cost_helper2, m=m))
            m.transmission['cost_factor'] = (m.transmission['c_helper'] *
                                             m.transmission['c_helper2'])
        if m.mode['sto']:
            m.storage['invcost-factor'] = invcost_factor(
                m,
                m.storage['depreciation'],
                m.storage['wacc'], m.storage['support_timeframe'])

            m.storage['rv-factor'] = rv_factor(
                m,
                m.storage['depreciation'],
                m.storage['wacc'], m.storage['support_timeframe'])
            try:
                m.storage.loc[(m.storage['rv-factor'] < 0) |
                            (m.storage['rv-factor'].isnull()), 'rv-factor'] = 0
            except TypeError:
                pass
            m.storage['stf_dist'] = m.storage['support_timeframe'].apply(stf_dist, m=m)
            m.storage['c_helper'] = (m.storage['support_timeframe']
                                     .apply(cost_helper, m=m))
            m.storage['c_helper2'] = m.storage['stf_dist'].apply(cost_helper2, m=m)
            m.storage['cost_factor'] = m.storage['c_helper'] * m.storage['c_helper2']

    else:
        # derive annuity factor from WACC and depreciation duration
        m.process['annuity-factor'] = annuity_factor(
            m.process['depreciation'],
            m.process['wacc'])
        if m.mode['tra']:
            m.transmission['annuity-factor'] = annuity_factor(
                m.transmission['depreciation'],
                m.transmission['wacc'])
        if m.mode['sto']:
            m.storage['annuity-factor'] = annuity_factor(
                m.storage['depreciation'],
                m.storage['wacc'])

    # Converting Data frames to dictionaries
    m.commodity_dict = m.commodity.to_dict()
    m.process_dict = m.process.to_dict()
    m.exp_process_dict = m.process_exp.to_dict()
    m.const_process_dict = m.process_const.to_dict()
    m.demand_dict = m.demand.to_dict()
    m.supim_dict = m.supim.to_dict()
    m.buy_sell_price_dict = m.buy_sell_price.to_dict()
    if m.mode['tra']:
        m.transmission_dict = m.transmission.to_dict()
    if m.mode['sto']:
        m.storage_dict = m.storage.to_dict() 
    if m.mode['dsm']:
        m.dsm_dict = m.dsm.to_dict()
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
