import pandas as pd


def validate_input(data):
    """ This function raises errors if inconsistent or illogical inputs are
    made, that might lead to erreneous results."""

    # Avoid negative part-load efficiencies
    for index in data['process_commodity']['ratio'].index:
        if (data['process_commodity'].loc[index]['ratio'] >
            data['process_commodity'].loc[index]['ratio-min']):
            raise ValueError('ratio-min must be larger than ratio!')

    # Ensure correct formation of vertex rule
