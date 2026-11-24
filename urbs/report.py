import pandas as pd
from .input import get_input
from .output import get_constants, get_timeseries
from .util import is_string


_EXCEL_SHEET_INVALID = str.maketrans({c: '-' for c in r'[]:*?/\\'})


def _excel_sheet_name(sit, com, com_type, used):
    """Readable unique Excel sheet name (max 31 characters, no invalid chars)."""
    label = f"{com} - {com_type}" if com_type else str(com)
    raw = f"{label} ({sit})" if sit else label
    raw = raw.translate(_EXCEL_SHEET_INVALID).strip(' -') or 'timeseries'
    name = raw[:31]
    if name not in used:
        used.add(name)
        return name
    i = 2
    while True:
        suffix = f" {i}"
        name = raw[: 31 - len(suffix)] + suffix
        if name not in used:
            used.add(name)
            return name
        i += 1


def _unpack_report_tuple(item):
    if len(item) >= 4:
        return item[0], item[1], item[2], item[3]
    return item[0], item[1], item[2], ''


def report(instance, filename, report_tuples, report_sites_name={}):
    """Write result summary to a spreadsheet file

    Args:
        - instance: a urbs model instance;
        - filename: Excel spreadsheet filename, will be overwritten if exists;
        - report_tuples: (optional) list of (sit, com) tuples for which to
          create detailed timeseries sheets;
        - report_sites_name: (optional) dict of names for created timeseries
          sheets
    """

    costs, cpro, ctra, csto = get_constants(instance)

    # create spreadsheet writer object
    with pd.ExcelWriter(filename) as writer:

        # write constants to spreadsheet
        costs.to_frame().to_excel(writer, sheet_name='Costs')
        cpro.to_excel(writer, sheet_name='Process caps')
        ctra.to_excel(writer, sheet_name='Transmission caps')
        csto.to_excel(writer, sheet_name='Storage caps')

        # initialize timeseries tableaus
        energies = []
        timeseries = {}
        help_ts = {}

        # collect timeseries data
        for item in report_tuples:
            stf, sit, com, com_type = _unpack_report_tuple(item)

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

            extracted = False
            for lv in help_sit:
                try:
                    (created, consumed, stored, imported, exported,
                     dsm, voltage_angle) = get_timeseries(instance, stf, com, lv)
                except Exception as exc:
                    print(f'get_timeseries failed for {sit}/{com}: {exc}')
                    continue
                extracted = True

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

            if not extracted:
                continue

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
            energy.to_excel(writer, sheet_name='Commodity sums')

            index_rows = []
            used_names = set()
            for item in report_tuples:
                stf, sit, com, com_type = _unpack_report_tuple(item)
                if isinstance(sit, list):
                    sit = tuple(sit)
                site_label = report_sites_name[sit]
                key = (stf, site_label, com)
                if key not in timeseries:
                    continue
                sheet_name = _excel_sheet_name(
                    site_label, com, com_type, used_names
                )
                index_rows.append({
                    'Sheet': sheet_name,
                    'Year': stf,
                    'Site': site_label,
                    'Commodity': com,
                    'Type': com_type,
                })
                timeseries[key].to_excel(writer, sheet_name=sheet_name)

            if index_rows:
                pd.DataFrame(index_rows).to_excel(
                    writer, sheet_name='Timeseries list', index=False
                )
