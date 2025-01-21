import pandas as pd
import numpy as np

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
                                 com + ') is in process-commodity input sheet.'
                                 '! The pair (' + sit + ',' + com + ')'
                                 ' is not in commodity input sheet.')


    # Add global parameters if necessary
    for stf in data['global_prop'].index.get_level_values(0):
        if 'Cost limit' not in data['global_prop'].loc[stf].index:
            data['global_prop'].loc[(stf, 'Cost limit'), :] = np.inf
            print('Added a global Cost limit for ' + str(stf) + ' with the value: inf.')
        if 'CO2 limit' not in data['global_prop'].loc[stf].index:
            data['global_prop'].loc[(stf, 'CO2 limit'), :] = np.inf
            print('Added a global CO2 limit for ' + str(stf) + ' with the value: inf.')
        if stf == min(data['global_prop'].index.get_level_values(0)):
            if 'Cost budget' not in data['global_prop'].loc[stf].index:
                data['global_prop'].loc[(stf, 'Cost budget'), :] = np.inf
                print('Added a global Cost budget for the entire period with the value: inf.')
            if 'CO2 budget' not in data['global_prop'].loc[stf].index:
                data['global_prop'].loc[(stf, 'CO2 budget'), :] = np.inf
                print('Added a global CO2 budget for the entire period with the value: inf.')


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
        # Validate input for DCPF
        if 'reactance' in data['transmission'].keys():
            for index in data['transmission'].index:
                if data['transmission'].loc[index]['reactance'] < 0:
                    raise ValueError('Ensure for DCPF transmission lines: reactance > 0 ')
                if data['transmission'].loc[index]['reactance'] > 0:
                    if data['transmission'].loc[index]['eff'] != 1:
                        raise ValueError('Ensure efficiency of DCPF Transmission Lines are 1')
                    if not data['transmission'].loc[index]['base_voltage'] > 0:
                        raise ValueError('Ensure base voltage of DCPF transmission lines are '
                                         'greater than 0')
                    if not (0 < data['transmission'].loc[index]['difflimit'] <= 90):
                        raise ValueError('Ensure angle difference of DCPF transmission lines '
                                         'are between 90 and 0 '
                                         'degrees')

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

# report that variable costs may have error if used with CO2 minimization and DCPF
def validate_dc_objective(data, objective):
    if not data['transmission'].empty:
        if 'reactance' in data['transmission'].keys():
            if any(data['transmission']['reactance'] > 0) and (objective == 'CO2') \
                    and any(data['transmission']['var-cost'] > 0):
                print("\nif the C02 is selected as objective function while modelling "
                      "DC transmission lines, variable costs may be incorrect \n")