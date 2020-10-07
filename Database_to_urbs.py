# Libraries

import pandas as pd
import numpy as np
from openpyxl import load_workbook
import itertools
import os
import urbs
import time
import shutil


def write_Global(Global, year, writer):
    print("Global")
    Global.loc['Support timeframe', 'value'] = year
    if year == 2020:
        Global.loc['CO2 limit', 'value'] = 84825000 *1.070367
    elif year == 2025:
        Global.loc['CO2 limit', 'value'] = 88021000 *1.070367
    elif year == 2030:
        Global.loc['CO2 limit', 'value'] = 98743000 *1.070367
    elif year == 2035:
        Global.loc['CO2 limit', 'value'] = 102717000 *1.070367
    elif year == 2037:
        Global.loc['CO2 limit', 'value'] = 103845000 *1.070367
    Global.to_excel(writer, sheet_name='Global', index=True)
    
    
def write_Site(Site, year, writer):
    print("Site")
    Site.to_excel(writer, sheet_name='Site', index=False)
    
    
def write_Commodity(Commodity, year, writer):
    print("Commodity")
    Commodity_year = Commodity[Commodity['scenario-year']==year]
    
    # Prepare sheet
    Commodity_year = Commodity_year[['price','max','maxperhour']]
        
    # Round to 1e-5
    Commodity_year["price"] = round(Commodity_year["price"], 5)
    Commodity_year["max"] = round(Commodity_year["max"], 5)
    
    # Write
    Commodity_year.reset_index().to_excel(writer, sheet_name='Commodity', index=False)
    
    
def write_Process(Process, Process_prev, EE_limits, suffix, year, writer):
    print("Process")
    
    # Filter possible expansion for that year
    Process_year = Process[Process['scenario-year']==year]
        
    if year > 2016:
        Process_year["inst-cap"] = 0
        Process_prev = Process_prev.join(Process["lifetime"], how="inner")
        Process_prev['Construction year'] = [int(x[-4:]) for x in Process_prev.index.get_level_values(level='Process')]
        idx_old = Process_prev.loc[(Process_prev['Construction year'] + Process_prev['lifetime']) < year].index
        idx_decommissioned = Process_prev.index.intersection(idx_old)
        Process_prev.loc[idx_decommissioned, "Total"] = 0
        Process_prev.rename(columns={"Total": "inst-cap"}, inplace=True)
        Process_prev["cap-up"] = Process_prev["inst-cap"]
        Process_prev["cap-lo"] = 0
        Process_prev = Process_prev.join(Process[['max-grad','inv-cost','fix-cost','var-cost','min-fraction', 'startup-cost','depreciation','reliability','cap-credit','wacc']], how="left")
        Process_year = pd.concat([Process_year.reset_index(), Process_prev.reset_index()], axis=0, ignore_index=True, sort=True)
        Process_year.set_index(["Site", "Process"], inplace=True)
    
    # Prepare sheet
    if (year>2016):
        Process_year = Process_year.reset_index().drop(columns=["lifetime", "scenario-year", "Construction year", "Source"])
    else:
        Process_year = Process_year.reset_index()
    Process_year = Process_year.groupby(['Site','Process']).agg({'max-grad':np.mean, 'min-fraction':np.sum, 'inv-cost':np.mean, 'fix-cost':np.mean, 'var-cost':np.mean, 'startup-cost':np.mean, 'reliability':np.mean, 'cap-credit':np.mean, 'wacc':np.mean, 'depreciation':np.mean, 'area-per-cap':np.mean, 'inst-cap':np.sum, 'cap-lo':np.sum, 'cap-up':np.sum})
    
    # Correct cap-up
    Process_year.reset_index(inplace=True)
    if (year>2016):
        Process_group = Process_year.copy()
        Process_group["Category"] = [x.split("_")[0] for x in Process_group["Process"]]
        Process_group = Process_group[["Site", "Category","inst-cap"]]
        Process_group = Process_group.groupby(["Site", "Category"]).sum()
        EE_limits_year = EE_limits.loc[(EE_limits["scenario-year"]=="all") | ((EE_limits["scenario-year"]==year) & (EE_limits["scenario"]==suffix[1:]))]
        Process_group = Process_group.join(EE_limits_year["cap-up"], how="right")
        Process_group["rest-cap-up"] = Process_group["cap-up"] - Process_group["inst-cap"]
        
        idx = Process_year[Process_year["cap-up"] == np.inf].index
        idx = [i for i in idx if (Process_year.loc[i, "Process"].startswith("Solar") or Process_year.loc[i, "Process"].startswith("Wind") or Process_year.loc[i, "Process"].startswith("Hydro"))]
        Process_capped = Process_year.loc[idx]
        Process_capped["Category"] = [x.split("_")[0] for x in Process_capped["Process"]]
        Process_capped.set_index(["Site", "Category"], inplace=True)
        Process_capped = Process_capped.join(Process_group["rest-cap-up"])
        Process_capped["cap-up"] = Process_group["rest-cap-up"]
        Process_capped = Process_capped.reset_index().drop(columns=["Category", "rest-cap-up"])
        Process_year.drop(index=idx, inplace=True)
        Process_year = Process_year.append(Process_capped, ignore_index=True, sort=False)
        Process_year.loc[Process_year["cap-up"]<0, "cap-up"] = 0
    
    # Round to 1e-5
    Process_year["inst-cap"] = round(Process_year["inst-cap"], 5)
    Process_year["cap-lo"] = round(Process_year["cap-lo"], 5)
    Process_year["cap-up"] = round(Process_year["cap-up"], 5)
    #Process_year["cap-up"] = 0
    Process_year["var-cost"] = round(Process_year["var-cost"], 5)
    Process_year = Process_year.loc[Process_year['cap-up']!=0]
    
    # Write
    pro = list(Process_year["Process"].unique())
    Process_year = Process_year[["Site", "Process", "inst-cap", "cap-lo", "cap-up", "max-grad", "min-fraction", "inv-cost", "fix-cost", "var-cost", "startup-cost", "reliability", "cap-credit", "wacc", "depreciation", "area-per-cap"]]
    Process_year.to_excel(writer, sheet_name='Process', index=False)
    return pro
    
    
def write_ProCom(ProCom, pro, year, writer):
    print("Process-Commodity")
    ProCom = ProCom[ProCom['scenario-year']<=year]
    ProCom = ProCom.loc[ProCom.index.isin(pro)].reset_index()
    
    # Prepare sheet
    ProCom = ProCom[['Process','Commodity','Direction','ratio','ratio-min']]
    
    # Round to 1e-5
    ProCom["ratio"] = round(ProCom["ratio"], 5)
    ProCom["ratio-min"] = round(ProCom["ratio-min"], 5)
    
    # Write
    ProCom.to_excel(writer, sheet_name='Process-Commodity', index=False)
    
    
def write_Storage(Storage, Storage_prev, year, writer):
    print("Storage")
    
    # Rename columns
    Storage = Storage.rename(columns={'inv-cost':'inv-cost-p','fix-cost':'fix-cost-p','var-cost':'var-cost-p', 'e-to-p': 'ep-ratio'})
    
    # Filter possible expansion for that year
    Storage_year = Storage[Storage['scenario-year']==year]
    Storage_year = Storage_year[Storage_year['cap-up-p']!=0]
    
    if (year > 2016) and len(Storage_prev):
        Storage_prev = Storage_prev.join(Storage[["lifetime", "ep-ratio"]], how="inner")
        Storage_prev['Construction year'] = [int(x[-4:]) for x in Storage_prev.index.get_level_values(level='Storage')]
        idx_old = Storage_prev.loc[(Storage_prev['Construction year'] + Storage_prev['lifetime']) < year].index
        idx_decommissioned = Storage_prev.index.intersection(idx_old)
        Storage_prev.loc[idx_decommissioned, "C Total"] = 0
        Storage_prev.loc[idx_decommissioned, "P Total"] = 0
        Storage_prev.rename(columns={"C Total": "inst-cap-c", "P Total": "inst-cap-p"}, inplace=True)
        Storage_prev['inst-cap-p'] = Storage_prev['inst-cap-p'].round(2)
        Storage_prev['inst-cap-c'] = Storage_prev['inst-cap-c'].round(2)
        Storage_prev["cap-up-c"] = Storage_prev["inst-cap-c"]
        Storage_prev["cap-lo-c"] = 0
        Storage_prev["cap-up-p"] = Storage_prev["inst-cap-p"]
        Storage_prev["cap-lo-p"] = 0
        Storage_prev = Storage_prev.join(Storage[['eff-in','eff-out','inv-cost-p','fix-cost-p','var-cost-p',
                                                  'depreciation','init','discharge','cap-credit','reliability']], how="left")
        Storage_year = pd.concat([Storage_year.reset_index(), Storage_prev.reset_index()], axis=0, ignore_index=True, sort=True)
        Storage_year.set_index(["Site", "Storage", "Commodity"], inplace=True)
          
    Storage_year = Storage_year[['inst-cap-c','cap-lo-c','cap-up-c','inst-cap-p','cap-lo-p','cap-up-p',
                                 'eff-in','eff-out','inv-cost-p','inv-cost-c','fix-cost-p','fix-cost-c','var-cost-p','var-cost-c',
                                 'wacc','depreciation','init','reliability','cap-credit','discharge', 'ep-ratio']]
    
    # Last check
    Storage_year = Storage_year[Storage_year['cap-up-p']!=0]
    
    # Round to 1e-5
    Storage_year = round(Storage_year, 5)
    
    # Write
    Storage_year.reset_index(inplace=True)
    Storage_year.to_excel(writer, sheet_name='Storage', index=False)
    

def add_weight(df, time_slices):
    # Get column names
    if isinstance(df, pd.DataFrame):
        col_names = df.columns
    elif isinstance(df, pd.Series):
        col_names = [df.name]
    
    # Prepare dataframe
    index_new = pd.Index(range(0,8761), name="t_new")
    df_empty = pd.DataFrame(0, index=index_new, columns=["t"])
    df_empty = df_empty.reset_index().set_index("t_new")
    
    t = df_empty.index
    len_ts = len(time_slices) - 1
    if len_ts == 8760:
        df_empty.loc[(t <= 1416) | (t>=8017), "t"] = df_empty.index[(t <= 1416) | (t>=8017)] # winter
        df_empty.loc[0, "t"] = 0
        df_empty.loc[(t <= 3624) & (t>=1417), "t"] = df_empty.index[(t <= 3624) & (t>=1417)] # Spring
        df_empty.loc[(t <= 5832) & (t>=3625), "t"] = df_empty.index[(t <= 5832) & (t>=3625)] # Summer
        df_empty.loc[(t <= 8016) & (t>=5833), "t"] = df_empty.index[(t <= 8016) & (t>=5833)] # Autumn
    else:
        df_empty.loc[(t <= 1416) | (t>=8017), "t"] = (df_empty.index[(t <= 1416) | (t>=8017)]-1)%(len_ts/4)+1 # winter
        df_empty.loc[0, "t"] = 0
        df_empty.loc[(t <= 3624) & (t>=1417), "t"] = (df_empty.index[(t <= 3624) & (t>=1417)]-1)%(len_ts/4)+(len_ts/4)+1 # Spring
        df_empty.loc[(t <= 5832) & (t>=3625), "t"] = (df_empty.index[(t <= 5832) & (t>=3625)]-1)%(len_ts/4)+2*(len_ts/4)+1 # Summer
        df_empty.loc[(t <= 8016) & (t>=5833), "t"] = (df_empty.index[(t <= 8016) & (t>=5833)]-1)%(len_ts/4)+3*(len_ts/4)+1 # Autumn
    
    weights = df_empty["t"].value_counts().reset_index().rename(columns={"t": "weight"}).rename(columns={"index":"t"})
    weights = weights.set_index("t")
    df_new = df.reset_index().join(weights, on="t")
    for col in col_names:
        df_new[col] = df_new[col] * df_new["weight"]
    df_new = df_new.drop(columns="weight").set_index(df.index.names)
    
    return df_new
    
    
def Database_to_urbs(model_type, suffix, year, result_folder, time_slices):
    # # Main code
    global fs
    global WACC
    fs = os.path.sep
    
    # Read the database file
    db = pd.read_excel('Input' + fs + 'Mekong' + fs + 'ASEAN_Mekong_provinces_DB.xlsx', sheet_name=None)
    Global = db['Global'].copy().set_index('Property')
    Site = db['Site'].copy()
    Commodity = db['Commodity'].copy().set_index(["Site", "Commodity", "Type"])
    Process = db['Process'].copy().set_index(["Site", "Process"])
    EE_limits = db["Cap-Up"].copy().rename(columns={"Country":"Site", "Technology (sum over all vintages)": "Category"}).set_index(["Site", "Category"])
    ProCom = db['Process-Commodity'].copy().set_index(["Process"])
    Transmission = db['Transmission'].copy()
    Storage = db['Storage'].copy().set_index(["Site", "Storage", "Commodity"])
    Demand = db['Demand'].copy()
    try:
        SupIm = db['SupIm'+suffix].copy()
        Hydro = pd.read_csv('Input' + fs + 'Mekong' + fs + 'hydro' + suffix + '_' + str(year) + '.csv', sep=';', decimal=',', index_col=0)
    except:
        SupIm = db['SupIm_average'].copy()
        Hydro = pd.read_csv('Input' + fs + 'Mekong' + fs + 'hydro_average_' + str(year) + '.csv', sep=';', decimal=',', index_col=0)
    db = None
    
    # Eventually read the results of the previous year
    urbs_path = os.path.join("result", result_folder, "scenario_base.h5")

    helpdf = urbs.load(urbs_path)
    df_result = helpdf._result
    df_data = helpdf._data
    
    Process_prev = df_data["process"].droplevel(0)[["inst-cap"]].rename(columns={"inst-cap": "Total"})
    Process_prev_new = df_result["cap_pro_new"].droplevel(0).reset_index().rename(columns={"sit":"Site", "pro":"Process", "cap_pro_new":"Total"}).set_index(["Site", "Process"]).fillna(0)
    Process_prev = Process_prev + Process_prev_new
    
    try:
        Storage_prev = df_data["storage"].droplevel(0)[["inst-cap-p"]].rename(columns={"inst-cap-p": "P Total"})
        Storage_prev_new = df_result["cap_sto_p_new"].droplevel(0).reset_index().rename(columns={"sit":"Site", "sto":"Storage", "cap_sto_p_new":"P Total", "com":"Commodity"}).set_index(["Site", "Storage", "Commodity"]).fillna(0)
        Storage_prev = Storage_prev + Storage_prev_new
    except:
        Storage_prev = pd.DataFrame()
    try:
        Transmission_prev = df_result["cap_tra_new"].droplevel(0).reset_index().rename(columns={"sit": "Site In", "sit_": "Site Out", "tra": "Transmission", "com": "Commodity", "cap_tra_new": "New"}).set_index(["Site In", "Site Out", "Transmission", "Commodity"])
    except:
        pass
    #Process_prev = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Process caps", index_col=[1,2])[["Total"]]
    #Storage_prev = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Storage caps", index_col=[1,2,3])[["C Total", "P Total"]]
    #Transmission_prev = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Transmission caps", index_col=[1,2,3,4])[["New"]]
        
    # Prepare the output
    layout_path = 'Input' + fs + 'Mekong' + fs + model_type[1:] + fs + '2016.xlsx'
    output_path = 'Input' + fs + 'Mekong' + fs + model_type[1:] + fs + str(year) + suffix + '.xlsx'
    shutil.copyfile(layout_path, output_path)
    book = load_workbook(output_path)
    writer = pd.ExcelWriter(output_path, engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    
    ### Global
    write_Global(Global, year, writer)
    
    ### Site
    write_Site(Site, year, writer)
    
    ### Commodity
    annual = write_Commodity(Commodity, year, writer)
    
    ### Process
    pro = write_Process(Process, Process_prev, EE_limits, suffix, year, writer)
    
    ### Process-Commodity
    write_ProCom(ProCom, pro, year, writer)
    
    # ### Transmission
    print("Transmission")
    
    # Prepare sheet
    Transmission = Transmission[['Site In','Site Out','Transmission','Commodity','eff','inv-cost','fix-cost','var-cost','inst-cap','cap-lo','cap-up','cap-credit','reliability','wacc','depreciation']]
    
    # Evetually add new capacities from previous year
    if year > 2016:
        Transmission.set_index(['Site In','Site Out','Transmission','Commodity'], inplace=True)
        try:
            Transmission["inst-cap"] = Transmission["inst-cap"] + Transmission_prev["New"]
        except:
            pass
        Transmission.reset_index(inplace=True)
        Transmission = Transmission.fillna(0)
    else:
        Transmission['cap-up'] = Transmission["inst-cap"]
            
    # Round to 1e-5
    Transmission["eff"] = round(Transmission["eff"], 5)
    Transmission["inv-cost"] = round(Transmission["inv-cost"], 5)
    Transmission["fix-cost"] = round(Transmission["fix-cost"], 5)
    Transmission["inst-cap"] = round(Transmission["inst-cap"], 5)
    Transmission["cap-lo"] = round(Transmission["cap-lo"], 5)
    Transmission["cap-up"] = round(Transmission["cap-up"], 5)
    
    # Write
    Transmission.to_excel(writer, sheet_name='Transmission', index=False)
    Transmission = None
    
    ### Storage
    write_Storage(Storage, Storage_prev, year, writer)
    
    ### Demand
    print("Demand")
    # Prepare sheet
    Demand = Demand.set_index('t')
    Demand_year = Demand.loc[time_slices]
    Demand_year.reset_index(inplace=True)
    Demand_year["t"] = Demand_year.index
    Demand_year.set_index('t', inplace=True)
    annual_dem = (0.043494 * (year-2016) + 1) * Demand.sum(axis=0)
    for reg in annual_dem.index:
        if reg[:3] == "KHM":
            annual_dem.loc[reg] = (0.088 * (year-2016) + 1) * Demand[reg].sum(axis=0)
        if reg[:3] == "LAO":
            annual_dem.loc[reg] = (0.095 * (year-2016) + 1) * Demand[reg].sum(axis=0)
    Demand_year_weighted = add_weight(Demand_year, time_slices)
    for c in Demand_year.columns:
        Demand_year[c] = (annual_dem[c] * Demand_year[c]) / Demand_year_weighted[c].sum()
    
    # Round to 1e-5
    Demand_year = round(Demand_year, 5)
    
    # Write
    Demand_year.to_excel(writer, sheet_name='Demand', index=True)
    Demand_year = None
    
    
    ### SupIm
    print("SupIm")
    # Prepare sheet
    SupIm_year = SupIm.set_index('t')
    SupIm_year.loc[0] = 0
    SupIm_year.sort_index(inplace=True)
    SupIm_year = pd.concat([Hydro, SupIm_year], axis=1)
      
    FLH_should = SupIm_year.sum(axis=0) * (len(time_slices)-1) / 8760
    SupIm_year = SupIm_year.loc[time_slices]
    correction = FLH_should / SupIm_year.sum(axis=0)
    for cf in correction.dropna().index:
        if correction[cf] < 1:
            SupIm_year[cf] = correction[cf] * SupIm_year[cf]
        if correction[cf] > 1:
            x_min = SupIm_year[cf].min()
            x_max = SupIm_year[cf].max()
            N = len(time_slices) - 1
            Sigma = SupIm_year[cf].sum()
            A = (correction[cf] * Sigma - N*x_min)/(Sigma - N * x_min) * (x_max - x_min)
            if (A <= 1) and (A > 0):
                SupIm_year[cf] = (SupIm_year[cf]-x_min)/(x_max-x_min)*A+x_min
            else:
                gap = FLH_should[cf] - Sigma
                nz = sum(SupIm_year[cf]>0)
                offset = gap / nz * 1.5
                SupIm_year_new = SupIm_year[cf]
                
                while abs(gap) > 5:
                    print(cf, gap)
                    SupIm_year_new = SupIm_year_new + (SupIm_year[cf]>0)*offset
                    SupIm_year_new.loc[SupIm_year_new>1] = 1
                    gap = FLH_should[cf] - SupIm_year_new.sum()
                    offset = gap / nz * 1.5
                SupIm_year[cf] = SupIm_year_new  
    
    SupIm_year.reset_index(inplace=True)
    SupIm_year["t"] = SupIm_year.index
    SupIm_year.set_index('t', inplace=True)
    
    # Round to 1e-5
    SupIm_year = round(SupIm_year, 5)
    
    # Write
    SupIm_year.to_excel(writer, sheet_name='SupIm', index=True)
    SupIm_year = None
    
    
    ### Output
    writer.save()
    print("Model file updated!")