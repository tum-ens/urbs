import pandas as pd
from .input_nopt import get_input
from .output_nopt import get_constants, get_timeseries
from .util_nopt import is_string


def report(instance, filename, report_tuples=None, report_sites_name={}):  # prob is given as instance
    """Write result summary to a spreadsheet file

    Args:
        :param instance: a urbs model instance;
        :param filename: Excel spreadsheet filename, will be overwritten if exists;
        :param report_tuples: (optional) list of (sit, com) tuples for which to
          create detailed timeseries sheets;
        :param report_sites_name: (optional) dict of names for created timeseries
          sheets
    """

    # default to all demand (sit, com) tuples if none are specified
    if len(report_tuples)==0:
        report_tuples = get_input(instance, 'dsm').index


    # Report new  optimized capacities:


    # create spreadsheet writer object
    with pd.ExcelWriter(filename) as writer:
        if 'cost' in instance.objective_dict.keys() or 'CO2' in instance.objective_dict.keys():
            if len(report_tuples) is None:
                report_tuples = get_input(instance, 'demand').index
            costs, cpro, ctra, csto = get_constants(instance)  # finds these values from model instance prob
            costs = costs.to_frame(name='Costs')
            costs = pd.concat([costs],keys=[str(list(instance.objective_dict.items())).replace("'", "").strip("[]")],
                                 names=['Objective'])
            cpro = pd.concat([cpro],keys=[str(list(instance.objective_dict.items())).replace("'", "").strip("[]")],
                                 names=['Objective'])
            cpro.to_excel(writer, 'Process caps')
            ctra.to_excel(writer, 'Transmission caps')
            csto.to_excel(writer, 'Storage caps')
            costs.to_excel(writer, 'Costs')
            # initialize timeseries tableaus
            energies = []
            timeseries = {}
            help_ts = {}

            # collect timeseries data
            for stf, sit, com in report_tuples:

                # wrap single site name in 1-element list for consistent behavior
                if is_string(sit):
                    help_sit = [sit]
                else:
                    help_sit = sit
                    sit = tuple(sit)

                # check existence of predefined names, else define them
                try:
                    report_sites_name[sit]
                except BaseException:
                    report_sites_name[sit] = str(sit)

                for lv in help_sit:
                    (created, consumed, stored, imported, exported,
                     dsm, voltage_angle) = get_timeseries(instance, stf, com, lv)

                    overprod = pd.DataFrame(
                        columns=['Overproduction'],
                        data=created.sum(axis=1) - consumed.sum(axis=1) +
                             imported.sum(axis=1) - exported.sum(axis=1) +
                             stored['Retrieved'] - stored['Stored'])

                    tableau = pd.concat(
                        [created, consumed, stored, imported, exported, overprod,
                         dsm, voltage_angle],
                        axis=1,
                        keys=['Created', 'Consumed', 'Storage', 'Import from',
                              'Export to', 'Balance', 'DSM', 'Voltage Angle'])
                    help_ts[(stf, lv, com)] = tableau.copy()

                    # timeseries sums
                    help_sums = pd.concat([created.sum(), consumed.sum(),
                                           stored.sum().drop('Level'),
                                           imported.sum(), exported.sum(),
                                           overprod.sum(), dsm.sum()],
                                          axis=0,
                                          keys=['Created', 'Consumed', 'Storage',
                                                'Import', 'Export', 'Balance',
                                                'DSM'])
                    try:
                        timeseries[(stf, report_sites_name[sit], com)] = \
                            timeseries[(stf, report_sites_name[sit], com)].add(
                                help_ts[(stf, lv, com)], axis=1, fill_value=0)
                        sums = sums.add(help_sums, fill_value=0)
                    except BaseException:
                        timeseries[(stf, report_sites_name[sit], com)] = help_ts[
                            (stf, lv, com)]
                        sums = help_sums

                # timeseries sums
                sums = pd.concat([created.sum(), consumed.sum(),
                                  stored.sum().drop('Level'),
                                  imported.sum(), exported.sum(), overprod.sum(),
                                  dsm.sum()],
                                 axis=0,
                                 keys=['Created', 'Consumed', 'Storage', 'Import',
                                       'Export', 'Balance', 'DSM'])
                energies.append(sums.to_frame("{}.{}.{}".format(stf, sit, com)))

            # write timeseries data (if any)
            if timeseries:
                # concatenate Commodity sums
                energy = pd.concat(energies, axis=1).fillna(0)
                energy.to_excel(writer, 'Commodity sums')

                # write timeseries to individual sheets
                for stf, sit, com in report_tuples:
                    if isinstance(sit, list):
                        sit = tuple(sit)

                    # sheet names cannot be longer than 31 characters...
                    sheet_name = "{}.{}.{} timeseries".format(
                        stf, report_sites_name[sit], com)[:31]
                    timeseries[(stf, report_sites_name[sit], com)].to_excel(
                        writer, sheet_name)

        else:
            costs = pd.concat([instance.near_optimal_cost],keys=[str(list(instance.objective_dict.items())).replace("'", "").strip("[]")],
                                 names=['Objective'])
            pro_cap = pd.concat([instance.near_optimal_capacities],
                                 keys=[str(list(instance.objective_dict.items())).replace("'", "").strip("[]")],
                                 names=['Objective'])
            sto_cap = pd.concat([instance.near_optimal_storage],
                                 keys=[str(list(instance.objective_dict.items())).replace("'", "").strip("[]")],
                                 names=['Objective'])
            costs.to_excel(writer, 'Costs')
            pro_cap.to_excel(writer, 'Near-Optimal Process Capacities')
            sto_cap.to_excel(writer, 'Near-Optimal Storage Capacities')

            #Min cost solution commodity report sheets
            ts_name = 'Min_Cost'
            energy_cost = instance.timeseries_data[ts_name][0]
            timeseries_cost = instance.timeseries_data[ts_name][1]
            if timeseries_cost:
                energy_cost.to_excel(writer, 'Commodity sums_' + ts_name)
            for stf, sit, com in report_tuples:
                if isinstance(sit, list):
                    sit = tuple(sit)
                try:
                    report_sites_name[sit]
                except BaseException:
                    report_sites_name[sit] = str(sit)
                # sheet names cannot be longer than 31 characters...
                sheet_name = "{}.{}.{}.{} timeseries".format(
                    ts_name, stf, report_sites_name[sit], com)[:31]
                timeseries_cost[(stf, report_sites_name[sit], com)].to_excel(
                    writer, sheet_name)

            instance.slack_list.sort()
            for slack in instance.slack_list:
                ts_name_1 = str(slack) + '_Min'
                ts_name_2 = str(slack) + '_Max'
                energy_min=instance.timeseries_data[ts_name_1][0]
                timeseries_min = instance.timeseries_data[ts_name_1][1]
                if timeseries_min:
                    energy_min.to_excel(writer, 'Commodity sums'+ts_name_1)
                for stf, sit, com in report_tuples:
                    if isinstance(sit, list):
                        sit = tuple(sit)
                    try:
                        report_sites_name[sit]
                    except BaseException:
                        report_sites_name[sit] = str(sit)
                    # sheet names cannot be longer than 31 characters...
                    sheet_name = "{}.{}.{}.{} timeseries".format(
                        ts_name_1,stf, report_sites_name[sit], com)[:31]
                    timeseries_min[(stf, report_sites_name[sit], com)].to_excel(
                        writer, sheet_name)

                energy_max=instance.timeseries_data[ts_name_2][0]
                timeseries_max = instance.timeseries_data[ts_name_2][1]
                if timeseries_max:
                    energy_max.to_excel(writer, 'Commodity sums'+ts_name_2)
                for stf, sit, com in report_tuples:
                    if isinstance(sit, list):
                        sit = tuple(sit)
                    try:
                        report_sites_name[sit]
                    except BaseException:
                        report_sites_name[sit] = str(sit)
                    # sheet names cannot be longer than 31 characters...
                    sheet_name = "{}.{}.{}.{} timeseries".format(
                        ts_name_2,stf, report_sites_name[sit], com)[:31]
                    timeseries_max[(stf, report_sites_name[sit], com)].to_excel(
                        writer, sheet_name)

def read_generation(instance, report_tuples=None, report_sites_name={}):

    if len(report_tuples)==0:
        report_tuples = get_input(instance, 'dsm').index
    # initialize timeseries tableaus
    energies = []
    timeseries = {}
    help_ts = {}

    # collect timeseries data
    for stf, sit, com in report_tuples:

        # wrap single site name in 1-element list for consistent behavior
        if is_string(sit):
            help_sit = [sit]
        else:
            help_sit = sit
            sit = tuple(sit)

        # check existence of predefined names, else define them
        try:
            report_sites_name[sit]
        except BaseException:
            report_sites_name[sit] = str(sit)

        for lv in help_sit:
            (created, consumed, stored, imported, exported,
             dsm, voltage_angle) = get_timeseries(instance, stf, com, lv)

            overprod = pd.DataFrame(
                columns=['Overproduction'],
                data=created.sum(axis=1) - consumed.sum(axis=1) +
                     imported.sum(axis=1) - exported.sum(axis=1) +
                     stored['Retrieved'] - stored['Stored'])

            tableau = pd.concat(
                [created, consumed, stored, imported, exported, overprod,
                 dsm, voltage_angle],
                axis=1,
                keys=['Created', 'Consumed', 'Storage', 'Import from',
                      'Export to', 'Balance', 'DSM', 'Voltage Angle'])
            help_ts[(stf, lv, com)] = tableau.copy()

            # timeseries sums
            help_sums = pd.concat([created.sum(), consumed.sum(),
                                   stored.sum().drop('Level'),
                                   imported.sum(), exported.sum(),
                                   overprod.sum(), dsm.sum()],
                                  axis=0,
                                  keys=['Created', 'Consumed', 'Storage',
                                        'Import', 'Export', 'Balance',
                                        'DSM'])
            try:
                timeseries[(stf, report_sites_name[sit], com)] = \
                    timeseries[(stf, report_sites_name[sit], com)].add(
                        help_ts[(stf, lv, com)], axis=1, fill_value=0)
                sums = sums.add(help_sums, fill_value=0)
            except BaseException:
                timeseries[(stf, report_sites_name[sit], com)] = help_ts[
                    (stf, lv, com)]
                sums = help_sums

        # timeseries sums
        sums = pd.concat([created.sum(), consumed.sum(),
                          stored.sum().drop('Level'),
                          imported.sum(), exported.sum(), overprod.sum(),
                          dsm.sum()],
                         axis=0,
                         keys=['Created', 'Consumed', 'Storage', 'Import',
                               'Export', 'Balance', 'DSM'])
        energies.append(sums.to_frame("{}.{}.{}".format(stf, sit, com)))

    # write timeseries data (if any)
    if timeseries:
        # concatenate Commodity sums
        com_sums = pd.concat(energies, axis=1).fillna(0)
    else:
        com_sums= None
        timeseries= None
    return com_sums,timeseries