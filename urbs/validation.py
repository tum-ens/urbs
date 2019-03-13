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
                                 '! The tuple (' + str(stf) + ',' + sit + ',' +
                                 com + ') is not in commodity input sheet.'
                                 '! The pair (' + sit + ',' + com + ')'
                                 ' is not in commodity input sheet.')

    # Find ducplicate index
    for key in data:
        if not data[key].index[data[key].index.duplicated()].unique().empty:
            if key == 'global_prop':
                raise ValueError('Some support time frames are duplicated in '
                                 'sheet "Global"')
            else:
                raise ValueError('The following indices are duplicated ' +
                                 str(data[key].index[data[key]
                                     .index.duplicated()].unique()))

    # Identify infeasible process, transmission and storage capacity
    # constraints before solving
    for index in data['process'].index:
        if not (data['process'].loc[index]['cap-lo'] <=
                data['process'].loc[index]['cap-up'] and
                data['process'].fillna(0).loc[index]['inst-cap'] <=
                data['process'].loc[index]['cap-up']):
            raise ValueError('Ensure cap_lo <= cap_up and inst_cap <= cap_up'
                             ' for all processes.')

    if not data['transmission'].empty:
        for index in data['transmission'].index:
            if not (data['transmission'].loc[index]['cap-lo'] <=
                    data['transmission'].loc[index]['cap-up'] and
                    data['transmission'].fillna(0).loc[index]['inst-cap'] <=
                    data['transmission'].loc[index]['cap-up']):
                raise ValueError('Ensure cap_lo <= cap_up and'
                                 'inst_cap <= cap_up for all transmissions.')

    if not data['storage'].empty:
        for index in data['storage'].index:
            if not (data['storage'].loc[index]['cap-lo-p'] <=
                    data['storage'].loc[index]['cap-up-p'] and
                    data['storage'].fillna(0).loc[index]['inst-cap-p'] <=
                    data['storage'].loc[index]['cap-up-p']):
                raise ValueError('Ensure cap_lo <= cap_up and'
                                 'inst_cap <= cap_up for all storage powers.')

            elif not (data['storage'].loc[index]['cap-lo-c'] <=
                      data['storage'].loc[index]['cap-up-c'] and
                      data['storage'].fillna(0).loc[index]['inst-cap-c'] <=
                      data['storage'].loc[index]['cap-up-c']):
                raise ValueError('Ensure cap_lo <= cap_up and inst_cap <= '
                                 'cap_up for all storage capacities.')

    # Identify SupIm values larger than 1, which lead to an infeasible model
    if (data['supim'] > 1).sum().sum() > 0:
        raise ValueError('All values in Sheet SupIm must be <= 1.')

    # Identify non sensible values for inputs
    if not data['storage'].empty:
        if (data['storage']['init'] > 1).any():
            raise ValueError("In worksheet 'storage' all values in column "
                             "'init' must be either in [0,1] (for a fixed "
                             "initial storage level) or 'nan' for a variable "
                             "initial storage level")

    # Identify outdated column label 'maxperstep' on the commodity tab and
    # suggest a rename to 'maxperhour'
    if 'maxperstep' in list(data['commodity']):
        raise KeyError("Maximum allowable commodities are defined by per "
                       "hour. Please change the column name 'maxperstep' "
                       "in the commodity worksheet to 'maxperhour' and "
                       "ensure that the input values are adjusted "
                       "correspondingly.")

    # Identify inconsistencies in site names throughout worksheets
    for site in data['commodity'].index.levels[1].tolist():
        if site not in data['site'].index.levels[1].tolist():
            raise KeyError("All names in the column 'Site' in input worksheet "
                           "'Commodity' must be from the list of site names "
                           "specified in the worksheet 'Site'.")

    for site in data['process'].index.levels[1].tolist():
        if site not in data['site'].index.levels[1].tolist():
            raise KeyError("All names in the column 'Site' in input worksheet "
                           "'Process' must be from the list of site names "
                           "specified in the worksheet 'Site'.")

    if not data['storage'].empty:
        for site in data['storage'].index.levels[1].tolist():
            if site not in data['site'].index.levels[1].tolist():
                raise KeyError("All names in the column 'Site' in input "
                               "worksheet 'Storage' must be from the list of "
                               "site names specified in the worksheet 'Site'.")

    if not data['dsm'].empty:
        for site in data['dsm'].index.levels[1].tolist():
            if site not in data['site'].index.levels[1].tolist():
                raise KeyError("All names in the column 'Site' in input "
                               "worksheet 'DSM' must be from the list of site "
                               "names specified in the worksheet 'Site'.")
