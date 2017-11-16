import pandas as pd


def validate_input(data):
    """ This function raises errors if inconsistent or illogical inputs are
    made, that might lead to erreneous results."""

    # Avoid negative part-load efficiencies
    for index in data['process_commodity']['ratio'].index:
        if (data['process_commodity'].loc[index]['ratio'] >
            data['process_commodity'].loc[index]['ratio-min']):
            raise ValueError('ratio-min must be larger than ratio for each'
                             ' line in process-commodity input sheet!')

    # Ensure correct formation of vertex rule
    for (sit, pro) in data['process'].index:
        for com in data['commodity'].index.get_level_values('Commodity'):
            simplified_pro_com_index = (
            [(p, c) for p, c, d in data['process_commodity'].index.tolist()])
            simplified_com_index = (
            [(s, c) for s, c, t in data['commodity'].index.tolist()])
            if ((pro, com) in simplified_pro_com_index and
                (sit, com) not in simplified_com_index):
                raise ValueError('Commodities used in a process at a site must'
                                 ' be specified in the commodity input sheet!'
                                 + ' the pair (' + sit + ',' + com + ')'
                                 ' is not in commodity input sheet.')