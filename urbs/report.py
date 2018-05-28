import pandas as pd
from .input import get_input
from .output import get_constants, get_timeseries


def report(instance, filename, report_tuples=None):
    """Write result summary to a spreadsheet file

    Args:
        instance: a urbs model instance
        filename: Excel spreadsheet filename, will be overwritten if exists
        report_tuples: (optional) list of (sit, com) tuples for which to
                       create detailed timeseries sheets

    Returns:
        Nothing
    """
    # default to all demand (sit, com) tuples if none are specified
    if report_tuples is None:
        report_tuples = get_input(instance, 'demand').columns

    costs, cpro, ctra, csto = get_constants(instance)

    # create spreadsheet writer object
    with pd.ExcelWriter(filename) as writer:

        # write constants to spreadsheet
        costs.to_frame().to_excel(writer, 'Costs')
        cpro.to_excel(writer, 'Process caps')
        ctra.to_excel(writer, 'Transmission caps')
        csto.to_excel(writer, 'Storage caps')

        # initialize timeseries tableaus
        energies = []
        timeseries = {}

        # collect timeseries data
        for stf, sit, com in report_tuples:
            (created, consumed, stored, imported, exported,
             dsm) = get_timeseries(instance, stf, com, sit)

            overprod = pd.DataFrame(
                columns=['Overproduction'],
                data=created.sum(axis=1) - consumed.sum(axis=1) +
                imported.sum(axis=1) - exported.sum(axis=1) +
                stored['Retrieved'] - stored['Stored'])

            tableau = pd.concat(
                [created, consumed, stored, imported, exported, overprod,
                 dsm],
                axis=1,
                keys=['Created', 'Consumed', 'Storage', 'Import from',
                      'Export to', 'Balance', 'DSM'])
            timeseries[(stf, sit, com)] = tableau.copy()

            # timeseries sums
            sums = pd.concat([created.sum(), consumed.sum(),
                              stored.sum().drop('Level'),
                              imported.sum(), exported.sum(), overprod.sum(),
                              dsm.sum()],
                             axis=0,
                             keys=['Created', 'Consumed', 'Storage', 'Import',
                                   'Export', 'Balance', 'DSM'])
            energies.append(sums.to_frame("{}.{}".format(stf, sit, com)))

        # write timeseries data (if any)
        if timeseries:
            # concatenate Commodity sums
            energy = pd.concat(energies, axis=1).fillna(0)
            energy.to_excel(writer, 'Commodity sums')

            # write timeseries to individual sheets
            for stf, sit, com in report_tuples:
                # sheet names cannot be longer than 31 characters...
                sheet_name = "{}.{}.{} timeseries".format(stf, sit, com)[:31]
                timeseries[(stf, sit, com)].to_excel(writer, sheet_name)
