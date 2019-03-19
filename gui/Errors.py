# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 18:27:54 2018

@author: aelshaha
"""


NO_SITE = 'NO_SITE'
NO_YEAR = 'NO_YEAR'
NO_TS = 'NO_TS'
TS_LEN = 'TS_LEN'
NO_COMM = 'NO_COMM'
NO_PROC = 'NO_PROC'
NO_SCENARIO = 'NO_SC'
ONE_SITE = 'ONE_SITE_'
NO_SITE_SEL = 'NO_SITE_SEL'

ALREADY_COPIED = 'ALREADY_COPIED_'

ERRORS = {
    NO_SITE: 'Please define at least one site!',
    NO_YEAR: 'Please define at least one year!',
    NO_SCENARIO: 'Please select at least one scenario!',
    NO_COMM: 'No commodities defined for the site: %s',
    NO_TS: 'Time Series is not defined for (site, commodity, year): '
    '(%s, %s, %s)',
    TS_LEN: 'Time Series should be exactly %s (not %s) entries, '
    'for (site, commodity, year): (%s, %s, %s)',
    NO_PROC: 'No processes defined for the site: %s',
    ONE_SITE: 'There is only one site defined.',
    NO_SITE_SEL: 'Please select atleast one site.',

    ALREADY_COPIED: 'This Process/Storage is already copied to the site (%s) '
    'before. Please go to that site and use "Clone" feature.'
}
