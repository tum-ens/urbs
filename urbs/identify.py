import pandas as pd

def identify_mode(data):
    """ Identify the urbs mode that is needed for running the current Input

    Args:
        data: input data dictionary

    Features:
        Intertemporal, Transmission, Storage, DSM, Buy Sell (Price), Time
        Variable efficiency, Expansion (4 values for process, transmission,
        storage capacity and storage power expansion)

    Returns:
        mode dictionary; contains bool values that define the urbs mode
        m.mode['exp'] will be initialized with 'True' if the corresponing mode
        (e.g. transmission) is also enabled and later updated through
        identify_expansion(m)

    """

    # create modes
    mode = {
        'int': False,                   # intertemporal
        'tra': False,                   # transmission
        'sto': False,                   # storage
        'dsm': False,                   # demand site management
        'bsp': False,                   # buy sell price
        'tve': False,                   # time variable efficiency
        'dcpf': False,                  # dc power flow
        'acpf': False,                  # ac power flow
        'onoff': False,                 # on/off processes
        'minfraction': False,           # processes with minimum working load
        'chp': False,                   # chp processes
        'exp': {                        # expansion
                'pro': True,
                'tra': False,
                'sto-c': False,
                'sto-p': False},
        'transdist': False              # transmission-distribution interface
        # 'inv_mip':{
        #         'pro': False,
        #         'tra': False,
        #         'sto-c': False,
        #         'sto-p': False}
        }

    # if number of support timeframes > 1
    if len(data['global_prop'].index.levels[0]) > 1:
        mode['int'] = True
    if not data['transmission'].empty:
        mode['tra'] = True
        mode['exp']['tra'] = True
    if not data['storage'].empty:
        mode['sto'] = True
        mode['exp']['sto-c'] = True
        mode['exp']['sto-p'] = True
    if not data['dsm'].empty:
        mode['dsm'] = True
    if not data['buy_sell_price'].empty:
        mode['bsp'] = True
    if not data['eff_factor'].empty:
        mode['tve'] = True
    if 'resistance' in data['transmission'].keys():
        if any(data['transmission']['resistance'] > 0):
            mode['acpf'] = True
    if 'reactance' in data['transmission'].keys():
        if any(data['transmission']['reactance'] > 0):
            mode['dcpf'] = True
    if 'on-off' in data['process'].keys():
        if any(data['process']['on-off'] == 1):
            mode['onoff'] = True
    if 'min-fraction' in data['process'].keys():
        if any(data['process']['min-fraction'] > 0):
            mode['minfraction'] = True
    # checking TransDist input value
    if data['global_prop'].loc[pd.IndexSlice[:,'TransDist'],'value'][0]:
        mode['transdist'] = True
    # if not data['process_commodity'].empty:
    #     if any(data['commodity'] == 'heat'):
    #         mode['chp'] = True

    return mode


def identify_expansion(const_unit_df, inst_cap_df):
    """ Identify if the model will be with expansion. The criterion for which
        no expansion is possible is "inst-cap == cap-up" for all
        support timeframes

        Here the the number of items in dataframe with constant units will be
        compared to the the number of items to which 'inst-cap' is given

    """
    if const_unit_df.count() == inst_cap_df.count():
        return False
    else:
        return True
