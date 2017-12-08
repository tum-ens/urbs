import pandas as pd


def validate_input(data):
    """ Input validation function

    This function raises errors if inconsistent or illogical inputs are
    made, that might lead to erreneous results.

    Args:
        data: Input data frames as read in by input.read_excel

    Returns:
        Customized error messages.

    """

    # Ensure correct formation of vertex rule
    for (sit, pro) in data['process'].index:
        for com in data['commodity'].index.get_level_values('Commodity'):
            simplified_pro_com_index = ([(p, c) for p, c, d in
                                        data['process_commodity'].index
                                        .tolist()])
            simplified_com_index = ([(s, c) for s, c, t in data['commodity']
                                    .index.tolist()])
            if ((pro, com) in simplified_pro_com_index and
                (sit, com) not in simplified_com_index):
                raise ValueError('Commodities used in a process at a site must'
                                 ' be specified in the commodity input sheet'
                                 '! The pair (' + sit + ',' + com + ')'
                                 ' is not in commodity input sheet.')
