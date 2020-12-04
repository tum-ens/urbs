import pandas as pd
import os
import glob
from xlrd import XLRDError
import pyomo.core as pyomo #from pyomo.environ import ConcreteModel #todo nachfragen
from .features.modelhelper import *
from .identify import *
import copy

#Später nicht genutzte packages aussortieren

def create_transdist_data(data, microgrid_data_initial):
    mg_set_list = build_set_list(data)
    for set_number, set in enumerate(mg_set_list):  # Bundesland microgrid setting
        connected_trans = data['site'].index.get_level_values(1)[set_number]
        for type_nr, quantity_nr in enumerate(set):  # Auflistung des settings
            microgrid_entries = microgrid_data_initial[type_nr]['site'].index.get_level_values(1)
            n = 0
            while n < quantity_nr:
                microgrid_data_input = copy.deepcopy(microgrid_data_initial[type_nr])
                for entry in microgrid_entries:
                    microgrid_data_input['site'].rename(index={entry: entry + str(n + 1) + '_' + connected_trans},
                                                        level=1, inplace=True)
                n += 1
                concatenate_with_micros(data, microgrid_data_input)
    return data

def build_set_list(data):
    transdist_dict = data['site'].drop('area', axis=1).to_dict()
    mg_set = transdist_dict['microgrid setting']
    mg_set_list = []
    for item in mg_set:
        mg_set_list.append(list(map(int, mg_set[item].split(','))))
    return mg_set_list

def concatenate_with_micros(data, microgrid_data):
    data['global_prop'] = pd.concat([data['global_prop'], microgrid_data['global_prop']]) #todo: assign props to each objective function?
    data['site'] = pd.concat([data['site'], microgrid_data['site']])
    data['commodity'] = pd.concat([data['commodity'], microgrid_data['commodity']])
    data['process'] = pd.concat([data['process'], microgrid_data['process']])
    data['process_commodity'] = pd.concat([data['process_commodity'], microgrid_data['process_commodity']]) # for different ratios from different systems, the processes need adapted names
    data['process_commodity'] = data['process_commodity'][~data['process_commodity'].index.duplicated(keep='first')]
    data['demand'] = pd.concat([data['demand'], microgrid_data['demand']], axis=1)
    data['supim'] = pd.concat([data['supim'], microgrid_data['supim']], axis=1)
    data['transmission'] = pd.concat([data['transmission'], microgrid_data['transmission']])
    data['storage'] = pd.concat([data['storage'], microgrid_data['storage']])
    data['dsm'] = pd.concat([data['dsm'], microgrid_data['dsm']])
    data['buy_sell_price'] = pd.concat([data['buy_sell_price'], microgrid_data['buy_sell_price']], axis=1) #todo: problem - buy sell price not site specific so far
    data['eff_factor'] = pd.concat([data['eff_factor'], microgrid_data['eff_factor']], axis=1)
    return data