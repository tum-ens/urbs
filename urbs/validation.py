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
    for (stf, sit, pro) in data['process'].index:
        for com in data['commodity'].index.get_level_values('Commodity'):
            simplified_pro_com_index = ([(st, p, c) for st, p, c, d in
                                        data['process_commodity'].index
                                        .tolist()])
            simplified_com_index = ([(st, s, c) for st, s, c, t in
                                    data['commodity'].index.tolist()])
            if ((stf, pro, com) in simplified_pro_com_index and
                (stf, sit, com) not in simplified_com_index):
                raise ValueError('Commodities used in a process at a site must'
                                 ' be specified in the commodity input sheet'
                                 '! The tuple (' + stf + ',' + sit + ',' + com
                                 + ') is not in commodity input sheet.'
                                 '! The pair (' + sit + ',' + com + ')'
                                 ' is not in commodity input sheet.')

    # Identify infeasible process, transmission and storage capacity
    # constraints before solving
    # for index in data['process'].index:
        # if not (data['process'].loc[index]['cap-lo'] <=
                # data['process'].loc[index]['cap-up'] and
                # data['process'].loc[index]['inst-cap'] <=
                # data['process'].loc[index]['cap-up']):
            # raise ValueError('Ensure cap_lo <= cap_up and inst_cap <= cap_up'
                             # ' for all processes.')

    # for index in data['transmission'].index:
        # if not (data['transmission'].loc[index]['cap-lo'] <=
                # data['transmission'].loc[index]['cap-up'] and
                # data['transmission'].loc[index]['inst-cap'] <=
                # data['transmission'].loc[index]['cap-up']):
            # raise ValueError('Ensure cap_lo <= cap_up and inst_cap <= cap_up'
                             # ' for all transmissions.')

    # for index in data['storage'].index:
        # if not (data['storage'].loc[index]['cap-lo-p'] <=
                # data['storage'].loc[index]['cap-up-p'] and
                # data['storage'].loc[index]['inst-cap-p'] <=
                # data['storage'].loc[index]['cap-up-p']):
            # raise ValueError('Ensure cap_lo <= cap_up and inst_cap <= cap_up'
                             # ' for all storage powers.')

        # elif not (data['storage'].loc[index]['cap-lo-c'] <=
                  # data['storage'].loc[index]['cap-up-c'] and
                  # data['storage'].loc[index]['inst-cap-c'] <=
                  # data['storage'].loc[index]['cap-up-c']):
            # raise ValueError('Ensure cap_lo <= cap_up and inst_cap <= cap_up'
                             # ' for all storage capacities.')

    # Identify SupIm values larger than 1, which lead to an infeasible model
    # if (data['supim'] > 1).sum().sum() >= 0:
        # raise ValueError('All values in Sheet SupIm must be <= 1.')
