import pandas as pd
from .pyomoio import get_entity, list_entities

def rename_duplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df

def create_result_cache(prob):
    entity_types = ['set', 'par', 'var', 'exp']
    if hasattr(prob, 'dual'):
        entity_types.append('con')

    entities = []
    for entity_type in entity_types:
        entities.extend(list_entities(prob, entity_type).index.tolist())

    result_cache = {}
    for entity in entities:
        result_cache[entity] = get_entity(prob, entity)
    return result_cache


def save(prob, filename, manyprob=False):
    """Save urbs model input and result cache to a HDF5 store file.

    Args:
        - prob: a urbs model instance containing a solution
        - filename: HDF5 store file to be written
        - manyprob: if prob is defined as a dictionary of Pyomo.ConcreteModel instances instead of a single one
    Returns:
        Nothing
    """
    import warnings
    import tables
    warnings.filterwarnings('ignore',
                            category=pd.io.pytables.PerformanceWarning)
    warnings.filterwarnings('ignore',
                            category=tables.NaturalNameWarning)

    if not manyprob: # normal save operation
        prob._result = create_result_cache(prob)

        with pd.HDFStore(filename, mode='w') as store:
            for name in prob._data.keys():
                if name not in ['trafo_node', 'mainbusbar_node']:
                    store['data/'+name] = prob._data[name]
            for name in prob._result.keys():
                store['result/'+name] = prob._result[name]
    else: #LVDS: prob is a dictionary of pyomo models (for prosumer clusters) ,
          # so iterate over each one to generate a single h5 file
        for prob_ in prob.values():
            prob_._result = create_result_cache(prob_)

        data_all    = dict.fromkeys(prob[0]._data.keys(),   pd.DataFrame()) # initialize datasets with empty dataframes
        results_all = dict.fromkeys(prob[0]._result.keys(), pd.DataFrame()) # initialzie results with empty dataframes

        for prob_ in prob.values():
            for name in prob_._data.keys():
                if name not in ['trafo_node', 'mainbusbar_node']:
                    if name in ['global_prop', 'process_commodity', 'type period','buy_sell_price']:
                        data_all[name] = prob_._data[name]
                    elif name in ['demand', 'supim', 'eff_factor', 'availability', 'uhp']:
                        data_all[name] = pd.concat([data_all[name], prob_._data[name]], axis = 1)
                    else:
                        data_all[name] = pd.concat([data_all[name], prob_._data[name]], axis = 0)
            for name in prob_._result.keys():
                if (name == 'costs') and (len(prob_._result[name])!= 0) : #costs result frame already has some costs inserted
                    results_all[name] += prob_._result[name] # if costs, add them, not concat.
                else:
                    if results_all[name].empty:
                        results_all[name] = prob_._result[name]
                    else:
                        results_all[name]  = pd.concat([results_all[name], prob_._result[name]])

        with pd.HDFStore(filename, mode='w') as store:
            for name in data_all.keys():
                try:
                    data_all[name] = data_all[~data_all.index.duplicated(keep='first')]
                except:
                    pass
                if name not in ['trafo_node', 'mainbusbar_node']:
                    if name == 'uhp':
                        data_all[name].columns = [';'.join(col).strip() for col in data_all[name].columns.values]
                        data_all[name] = rename_duplicate_columns(data_all[name])
                        data_all[name].columns = pd.MultiIndex.from_tuples([tuple(c.split(';')) for c in data_all[name].columns])
                    store['data/'+name] = data_all[name]
            for name in results_all.keys():
                try:
                    results_all[name] = results_all[~results_all.index.duplicated(keep='first')]
                except:
                    pass

                store['result/'+name] = results_all[name]

class ResultContainer(object):
    """ Result/input data container for reporting functions. """
    def __init__(self, data, result):
        self._data = data
        self._result = result


def load(filename):
    """Load a urbs model result container from a HDF5 store file.

    Args:
        filename: an existing HDF5 store file

    Returns:
        prob: the modified instance containing the result cache
    """
    with pd.HDFStore(filename, mode='r') as store:
        data_cache = {}
        for group in store.get_node('data'):
            data_cache[group._v_name] = store[group._v_pathname]

        result_cache = {}
        for group in store.get_node('result'):
            result_cache[group._v_name] = store[group._v_pathname]

    return ResultContainer(data_cache, result_cache)
