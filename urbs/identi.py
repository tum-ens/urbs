import pandas as pd


def identify_mode(input_files):
    """ Identify the urbs mode that is needed for running the current xslx file
    
    Minimum mode: only one site, no transmission, no storage, no DSM, no expansion
    optional features:
    Transmission
    Storage
    DSM
    Intertemporal
    Expansion
    
    Args:
        data: a dict of 6 DataFrames with the keys 'commodity', 'process',
            'transmission', 'storage', 'demand' and 'supim'.
    
    Returns:
        result: a bool vector which defines the urbs mode"""
    
    # Set minimal mode as default
    tra = sto = dsm = Int = False
    
    # Intertemporal mode 
    if len(input_files)>1:
        Int = True
    
    for filename in input_files:
        with pd.ExcelFile(filename) as xls:
        # Transmission mode
            if 'Transmission' in xls.sheet_names \
                and not xls.parse('Transmission').set_index(['Site In', 'Site Out',
                                'Transmission', 'Commodity']).empty:
                tra = True
            # Storage mode
            if 'Storage' in xls.sheet_names \
            and not xls.parse('Storage').set_index(['Site', 'Storage', 'Commodity']).empty:
                sto = True
            # Demand side management mode
            if 'DSM' in xls.sheet_names \
            and not xls.parse('DSM').set_index(['Site', 'Commodity']).empty:
                dsm = True
    
    return tra,sto,dsm,Int
        
    
    
        
    