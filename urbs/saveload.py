import pandas as pd
from .pyomoio import get_entity, list_entities


def create_result_cache(prob):
    entity_types = ['set', 'par', 'var']
    if hasattr(prob, 'dual'):
        entity_types.append('con')

    entities = []
    for entity_type in entity_types:
        entities.extend(list_entities(prob, entity_type).index.tolist())

    result_cache = {}
    for entity in entities:
        result_cache[entity] = get_entity(prob, entity)
    return result_cache


def save(prob, filename):
    """Save urbs model input and result cache to a HDF5 store file.

    Args:
        - prob: a urbs model instance containing a solution
        - filename: HDF5 store file to be written

    Returns:
        Nothing
    """
    import warnings
    warnings.filterwarnings('ignore',
                            category=pd.io.pytables.PerformanceWarning)

    if not hasattr(prob, '_result'):
        prob._result = create_result_cache(prob)

    with pd.HDFStore(filename, mode='w') as store:
        for name in prob._data.keys():
            store['data/'+name] = prob._data[name]
        for name in prob._result.keys():
            store['result/'+name] = prob._result[name]


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
