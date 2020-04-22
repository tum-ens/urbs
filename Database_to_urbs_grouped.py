# Libraries

import pandas as pd
import numpy as np
from openpyxl import load_workbook
import itertools
import os
import urbs
import time

dict_countries = {"IE": "IEUK",
                  "UK": "IEUK",
                  "FR": "FR",
                  "BE": "BELUNL",
                  "LU": "BELUNL",
                  "NL": "BELUNL",
                  "DE": "DE",
                  "DK": "DKFINOSE",
                  "FI": "DKFINOSE",
                  "NO": "DKFINOSE",
                  "SE": "DKFINOSE",
                  "ES": "ESPT",
                  "PT": "ESPT",
                  "AT": "ATCH",
                  "CH": "ATCH",
                  "IT": "IT",
                  "CZ": "CZPLSK",
                  "PL": "CZPLSK",
                  "SK": "CZPLSK",
                  "EE": "EELTLV",
                  "LT": "EELTLV",
                  "LV": "EELTLV",
                  "HR": "HRHUSI",
                  "HU": "HRHUSI",
                  "SI": "HRHUSI",
                  "BG": "BGELRO",
                  "EL": "BGELRO",
                  "RO": "BGELRO",
                  }


def write_Global(Global, version, model_type, suffix, year, writer):
    print("Global")
    Global_updated = pd.read_excel('Input' + fs + version + model_type + fs + str(year) + suffix + '.xlsx', sheet_name="Global", index_col=0)
    Global_updated.loc['Support timeframe', 'value'] = year
    Global_updated.to_excel(writer, sheet_name='Global', index=True)
    
    
def write_Site(Site, version, suffix, year, writer):
    print("Site")
    Site_year = Site[Site['scenario-year']==year]
    Site_year = Site_year[['Site','area']]
    Site_year = Site_year.rename(columns={'Site':'Name'})
    Site_year = group_sites(Site_year).groupby("Name").sum().reset_index()
    Site_year.to_excel(writer, sheet_name='Site', index=False)
    
    
def write_Commodity(Commodity, version, suffix, year, writer):
    print("Commodity")
    Commodity_year = Commodity[Commodity['scenario-year']==year]
    
    # Save for later
    annual = Commodity_year[['annual']].copy()
    annual.dropna(inplace=True)
    annual.reset_index(inplace=True)
    co2_price = Commodity_year.reset_index().set_index(["Commodity"])
    co2_price = co2_price.loc["CO2", "price"].unique()[0]
    
    # Prepare sheet
    Commodity_year = Commodity_year[['price','max','maxperhour']]
    if year == 2015:
        Commodity_year.drop(("CH", "CO2", "Env"), axis=0, inplace=True)
        Commodity_year.drop("CCS_CO2", axis=0, level="Commodity", inplace=True)
    
    # Remove CSP
    Commodity_year.drop(["Solar_CSP_high", "Solar_CSP_mid", "Solar_CSP_low"], axis=0, level="Commodity", inplace=True)
    
    # Rename Solar_PV to Solar
    Commodity_year.reset_index(inplace=True)
    Commodity_year.loc[Commodity_year["Commodity"] == "Solar_PV_high", "Commodity"] = "Solar_high"
    Commodity_year.loc[Commodity_year["Commodity"] == "Solar_PV_mid", "Commodity"] = "Solar_mid"
    Commodity_year.loc[Commodity_year["Commodity"] == "Solar_PV_low", "Commodity"] = "Solar_low"
    
    # Add Slack
    if year == 2015:
        sites = list(Commodity_year["Site"].unique())
        df = pd.DataFrame(999, index=pd.MultiIndex.from_product([sites, ["Slack"], ["Stock"]], names=["Site", "Commodity", "Type"]), columns=["price", "max", "maxperhour"])
        df["max"] = np.inf
        df["maxperhour"] = np.inf
        Commodity_year = Commodity_year.append(df.reset_index(), ignore_index=True)
        
    # Correct maxperhour for CCS_CO2
    if year > 2015:
        Commodity_year.loc[Commodity_year["Commodity"] == "CCS_CO2", "maxperhour"] = np.inf
        
    Commodity_year = group_sites(Commodity_year).groupby(["Site", "Commodity", "Type"]) \
                                                .agg({"price": np.mean, "max": np.sum, "maxperhour": np.sum}) \
                                                .reset_index()
        
    # Round to 1e-5
    Commodity_year["price"] = round(Commodity_year["price"], 5)
    Commodity_year["max"] = round(Commodity_year["max"], 5)
    
    # Write
    Commodity_year.to_excel(writer, sheet_name='Commodity', index=False)
    
    return annual, co2_price
    
    
def write_Process(Process, Process_prev, EE_limits, co2_price, version, suffix, year, writer):
    print("Process")
    
    # Save for later
    #pro_reserve = Process[['Site','Process','reserve']]
    #pro_reliability = Process[['Site','Process','reliability']]
    #pro_capcredit = Process[['Site','Process','cap-credit']]
    
    # Rename Solar_PV to Solar
    Process.reset_index(inplace=True)
    for proc in Process["Process"].unique():
        if proc.startswith("Solar_PV"):
            Process.loc[Process["Process"] == proc, "Process"] = proc[:5] + proc[8:]
    Process.set_index(["Site", "Process"], inplace=True)
    
    # Filter possible expansion for that year
    Process_year = Process[Process['scenario-year']==year]
    Process_year = Process_year[Process_year['cap-up']!=0]
        
    if year > 2015:
        Process_year["inst-cap"] = 0
        Process_prev = Process_prev.join(Process["lifetime"], how="inner")
        Process_prev['Construction year'] = [int(x[-4:]) for x in Process_prev.index.get_level_values(level='Process')]
        idx_old = Process_prev.loc[(Process_prev['Construction year'] + Process_prev['lifetime']) < year].index
        idx_decommissioned = Process_prev.index.intersection(idx_old)
        Process_prev.loc[idx_decommissioned, "Total"] = 0
        Process_prev.rename(columns={"Total": "inst-cap"}, inplace=True)
        Process_prev["cap-up"] = Process_prev["inst-cap"]
        Process_prev["cap-lo"] = 0
        Process_prev = Process_prev.join(Process[['max-grad','inv-cost','fix-cost','var-cost','depreciation','reliability','cap-credit']], how="left")
        Process_year = pd.concat([Process_year.reset_index(), Process_prev.reset_index()], axis=0, ignore_index=True, sort=True)
        Process_year.set_index(["Site", "Process"], inplace=True)
    
    # Prepare sheet
    Process_year['min-fraction'] = 0
    Process_year['startup-cost'] = 0
    Process_year['area-per-cap'] = 0
    Process_year['wacc'] = WACC
    Process_year = Process_year[['inst-cap','cap-lo','cap-up','max-grad','min-fraction','inv-cost','fix-cost','var-cost','startup-cost','reliability', 'cap-credit','wacc','depreciation','area-per-cap']]
    
    # Correct max-grad, cap-up and depreciation
    Process_year.loc[Process_year['max-grad'] == 0, 'max-grad'] = np.inf
    Process_year.loc[Process_year["depreciation"] == 0, "depreciation"] = 25
    
    # Correct cap-up
    Process_year.loc[Process_year["cap-up"] == -1, "cap-up"] = np.inf
    Process_year.reset_index(inplace=True)
    if (year>2015):
        Process_group = Process_year.copy()
        Process_group["Category"] = [x.split("_")[0]+"_"+x.split("_")[-2] for x in Process_group["Process"]]
        Process_group = Process_group[["Site", "Category","inst-cap"]]
        Process_group = Process_group.groupby(["Site", "Category"]).sum()
        Process_group = Process_group.join(EE_limits["cap-up"], how="right")
        Process_group["rest-cap-up"] = Process_group["cap-up"] - Process_group["inst-cap"]
        
        idx = Process_year[Process_year["cap-up"] == np.inf].index
        idx = [i for i in idx if (Process_year.loc[i, "Process"].startswith("Solar") or Process_year.loc[i, "Process"].startswith("Wind"))]
        Process_capped = Process_year.loc[idx]
        Process_capped["Category"] = [x.split("_")[0]+"_"+x.split("_")[-2] for x in Process_capped["Process"]]
        Process_capped.set_index(["Site", "Category"], inplace=True)
        Process_capped = Process_capped.join(Process_group["rest-cap-up"])
        Process_capped["cap-up"] = Process_group["rest-cap-up"]
        Process_capped = Process_capped.reset_index().drop(columns=["Category", "rest-cap-up"])
        Process_year.drop(index=idx, inplace=True)
        Process_year = Process_year.append(Process_capped, ignore_index=True, sort=False)
        Process_year.loc[Process_year["cap-up"]<0, "cap-up"] = 0
        
        # Update var-cost of Bio_CCS
        idx = [i for i in Process_year.index if Process_year.loc[i, "Process"].startswith("Bio_CCS")]
        Process_year.loc[idx, "var-cost"] = Process_year.loc[idx, "var-cost"] - co2_price * 0.7128
    
    # Add Shunt and Slack
    sites = Process_year["Site"].unique()
    if year == 2015:
        tech = ["Slack", "Shunt"]
    else:
        tech = ["Shunt"]
    df = pd.DataFrame(0, index=pd.MultiIndex.from_product([sites, tech], names=['Site', 'Process']), columns=['inst-cap','cap-lo','cap-up','max-grad','min-fraction','inv-cost','fix-cost','var-cost','startup-cost','reliability', 'cap-credit','wacc','depreciation','area-per-cap'])
    df["inst-cap"] = 999999
    df["cap-up"] = 999999
    df["cap-credit"] = 1
    df["reliability"] = 1
    df["max-grad"] = np.inf
    df["wacc"] = WACC
    df["depreciation"] = 1
    Process_year = Process_year.append(df.reset_index(), ignore_index=True, sort=False)
    
    # Last check
    Process_year = Process_year[Process_year['cap-up']!=0]
    
    Process_year = group_sites(Process_year).groupby(["Site", "Process"]) \
                                            .agg({"inst-cap": np.sum, "cap-lo": np.sum, "cap-up": np.sum,
                                                  "max-grad": np.mean, "min-fraction": np.sum,
                                                  "inv-cost": np.mean, "fix-cost": np.mean, "var-cost": np.mean,
                                                  "startup-cost": np.mean, "reliability": np.mean, "cap-credit": np.mean,
                                                  "wacc": np.mean, "depreciation": np.mean, "area-per-cap": np.mean}) \
                                            .reset_index()
    
    # Round to 1e-5
    Process_year["inst-cap"] = round(Process_year["inst-cap"], 5)
    Process_year["cap-lo"] = round(Process_year["cap-lo"], 5)
    Process_year["cap-up"] = round(Process_year["cap-up"], 5)
    Process_year["var-cost"] = round(Process_year["var-cost"], 5)
    
    # Write
    pro = list(Process_year["Process"].unique())
    Process_year.to_excel(writer, sheet_name='Process', index=False)
    return pro
    
    
def write_ProCom(ProCom, pro, year, writer):
    print("Process-Commodity")
    pro_renamed = []
    for elem in pro:
        if elem.startswith("Solar_"):
            pro_renamed = pro_renamed + [elem[:5] + "_PV" + elem[5:]]
        else:
            pro_renamed = pro_renamed + [elem]
       
    ProCom = ProCom.loc[ProCom.index.isin(pro_renamed)].reset_index()
    ProCom = ProCom.loc[ProCom["ratio"] != 0]
    
    # Prepare sheet
    ProCom = ProCom[['Process','Commodity','Direction','ratio','ratio-min']]
    ProCom.loc[ProCom['Direction'] == 'IN', 'Direction'] = 'In'
    
    # Change direction for negative values
    ProCom.loc[ProCom['ratio'] < 0, 'ratio-min'] = - ProCom.loc[ProCom['ratio'] < 0, 'ratio-min']
    ProCom.loc[ProCom['ratio'] < 0, 'Direction'] = "In"
    ProCom.loc[ProCom['ratio'] < 0, 'ratio'] = - ProCom.loc[ProCom['ratio'] < 0, 'ratio']
    
    # Rename Solar_PV to Solar
    for proc in ProCom["Process"].unique():
        if proc.startswith("Solar_PV"):
            ProCom.loc[ProCom["Process"] == proc, "Process"] = proc[:5] + proc[8:]
    for com in ProCom["Commodity"].unique():
        if com.startswith("Solar_PV"):
            ProCom.loc[ProCom["Commodity"] == com, "Commodity"] = com[:5] + com[8:]
    
    # Add Shunt and Slack
    if year == 2015:
        df = pd.DataFrame([('Slack', 'Slack', 'In', 1, 1), ('Slack', 'Elec', 'Out', 1, 1), ('Shunt', 'Elec', 'In', 1, 1)],
                          columns=['Process','Commodity','Direction','ratio','ratio-min'])
    else:
        df = pd.DataFrame([('Shunt', 'Elec', 'In', 1, 1)],
                          columns=['Process','Commodity','Direction','ratio','ratio-min'])
    ProCom = ProCom.append(df, ignore_index=True)
        
    ProCom.fillna(1, inplace=True)
    
    # Round to 1e-5
    ProCom["ratio"] = round(ProCom["ratio"], 5)
    ProCom["ratio-min"] = round(ProCom["ratio-min"], 5)
    
    # Write
    ProCom.to_excel(writer, sheet_name='Process-Commodity', index=False)
    
    
def write_Storage(Storage, Storage_prev, version, suffix, year, writer):
    print("Storage")
    
    # Rename columns
    Storage = Storage.rename(columns={'inv-cost':'inv-cost-p','fix-cost':'fix-cost-p','var-cost':'var-cost-p', 'e-to-p': 'ep-ratio'})
    
    # Filter possible expansion for that year
    Storage_year = Storage[Storage['scenario-year']==year]
    Storage_year = Storage_year[Storage_year['cap-up-p']!=0]
    
    # Save for later
    # sto_cycles = Storage[['Site','Storage','Commodity','cycles-max']]
    # sto_capcredit = Storage[['Site','Storage','Commodity','cap-credit']]
    # sto_inflow = Storage[['Site','Storage','Commodity','inflow']]
    # sto_etop = Storage[['Site','Storage','Commodity','e-to-p']]
    
    # Correct cap-up-p
    Storage_year.loc[Storage_year["cap-up-p"] == -1, "cap-up-p"] = np.inf
    
    # Prepare sheet
    Storage_year['ep-ratio'] = Storage['ep-ratio'].round(2)
    Storage_year.loc[Storage_year["depreciation"] == 0, "depreciation"] = 10
    Storage_year['inst-cap-c'] = Storage_year['inst-cap-p'] * Storage_year['ep-ratio']
    Storage_year['cap-lo-c'] = Storage_year['cap-lo-p'] * Storage_year['ep-ratio']
    Storage_year['cap-up-c'] = Storage_year['cap-up-p'] * Storage_year['ep-ratio']
    
    if year > 2015:
        Storage_prev = Storage_prev.join(Storage[["lifetime", "ep-ratio"]], how="inner")
        Storage_prev['Construction year'] = [int(x[-4:]) for x in Storage_prev.index.get_level_values(level='Storage')]
        idx_old = Storage_prev.loc[(Storage_prev['Construction year'] + Storage_prev['lifetime']) < year].index
        idx_decommissioned = Storage_prev.index.intersection(idx_old)
        #Storage_prev.loc[idx_decommissioned, "C Total"] = 0
        Storage_prev.loc[idx_decommissioned, "P Total"] = 0
        #Storage_prev.rename(columns={"C Total": "inst-cap-c", "P Total": "inst-cap-p"}, inplace=True)
        Storage_prev.rename(columns={"P Total": "inst-cap-p"}, inplace=True)
        Storage_prev['inst-cap-p'] = Storage_prev['inst-cap-p'].round(2)
        Storage_prev['inst-cap-c'] = Storage_prev['inst-cap-p'] * Storage_prev['ep-ratio']
        Storage_prev["cap-up-c"] = Storage_prev["inst-cap-c"]
        Storage_prev["cap-lo-c"] = 0
        Storage_prev["cap-up-p"] = Storage_prev["inst-cap-p"]
        Storage_prev["cap-lo-p"] = 0
        Storage_prev = Storage_prev.join(Storage[['eff-in','eff-out','inv-cost-p','fix-cost-p','var-cost-p',
                                                  'depreciation','init','discharge','cap-credit','reliability']], how="left")
        Storage_year = pd.concat([Storage_year.reset_index(), Storage_prev.reset_index()], axis=0, ignore_index=True, sort=True)
        Storage_year.set_index(["Site", "Storage", "Commodity"], inplace=True)
        
    Storage_year['wacc'] = WACC
    Storage_year['inv-cost-c'] = 0
    Storage_year['fix-cost-c'] = 0
    Storage_year['var-cost-c'] = 0   
    Storage_year = Storage_year[['inst-cap-c','cap-lo-c','cap-up-c','inst-cap-p','cap-lo-p','cap-up-p',
                                 'eff-in','eff-out','inv-cost-p','inv-cost-c','fix-cost-p','fix-cost-c','var-cost-p','var-cost-c',
                                 'wacc','depreciation','init','reliability','cap-credit','discharge', 'ep-ratio']]
    
    # Last check
    Storage_year = Storage_year[Storage_year['cap-up-p']!=0]
    
    # Round to 1e-5
    Storage_year = round(Storage_year, 5)
    
    # Group sites
    Storage_year = Storage_year.reset_index()
    Storage_year = group_sites(Storage_year).groupby(["Site", "Storage", "Commodity"]) \
                                            .agg({"inst-cap-c": np.sum, "cap-lo-c": np.sum, "cap-up-c": np.sum,
                                                  "inst-cap-p": np.sum, "cap-lo-p": np.sum, "cap-up-p": np.sum,
                                                  "eff-in": np.mean, "eff-out": np.mean,
                                                  "inv-cost-c": np.mean, "inv-cost-p": np.mean, "fix-cost-p": np.mean,
                                                  "fix-cost-c": np.mean, "var-cost-p": np.mean, "var-cost-c": np.mean,
                                                  "wacc": np.mean, "depreciation": np.mean, "init": np.mean, "reliability": np.mean,
                                                  "cap-credit": np.mean, "discharge": np.mean, "ep-ratio": np.mean}) \
                                            .reset_index()
                                            
    if year == 2015:
        Storage_year["ep-ratio"] = (Storage_year["inst-cap-c"] / Storage_year["inst-cap-p"]).round(2)
        Storage_year['inst-cap-c'] = Storage_year['inst-cap-p'] * Storage_year['ep-ratio']
        Storage_year['cap-lo-c'] = Storage_year['cap-lo-p'] * Storage_year['ep-ratio']
        Storage_year['cap-up-c'] = Storage_year['cap-up-p'] * Storage_year['ep-ratio']
    
    # Write
    Storage_year.to_excel(writer, sheet_name='Storage', index=False)
    

def add_weight(df):
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
    df_empty.loc[(t <= 1416) | (t>=8017), "t"] = (df_empty.index[(t <= 1416) | (t>=8017)]-1)%168+1 # winter
    df_empty.loc[0, "t"] = 0
    df_empty.loc[(t <= 3624) & (t>=1417), "t"] = (df_empty.index[(t <= 3624) & (t>=1417)]-1)%168+169 # Spring
    df_empty.loc[(t <= 5832) & (t>=3625), "t"] = (df_empty.index[(t <= 5832) & (t>=3625)]-1)%168+337 # Summer
    df_empty.loc[(t <= 8016) & (t>=5833), "t"] = (df_empty.index[(t <= 8016) & (t>=5833)]-1)%168+505 # Autumn
    
    weights = df_empty["t"].value_counts().reset_index().rename(columns={"t": "weight"}).rename(columns={"index":"t"})
    weights = weights.set_index("t")
    df_new = df.reset_index().join(weights, on="t")
    for col in col_names:
        df_new[col] = df_new[col] * df_new["weight"]
    df_new = df_new.drop(columns="weight").set_index(df.index.names)
    
    return df_new
    
def group_sites(df):
    # Replace site name
    for cl in ["Name", "Site", "Site In", "Site Out"]:
        if cl in df.columns:
            df = df.set_index(cl)
            df["aux"] = ""
            for sit in df.index:
                df.loc[sit, "aux"] = dict_countries[sit]
            df = df.reset_index().drop(cl, axis=1).rename(columns={"aux":cl})
    
    return df
    
    
def Database_to_urbs_grouped(version, model_type, suffix, year, result_folder, time_slices):
    # # Main code
    global fs
    global WACC
    fs = os.path.sep
    
    # Read the database file
    db = pd.read_excel('Input' + fs + '4NEMO_Database_' + version + suffix + '.xlsx', sheet_name=None)
    Global = db['Global'].copy().set_index('Parameter')
    Site = db['Site'].copy()
    Commodity = db['Commodity'].copy().set_index(["Site", "Commodity", "Type"])
    Process = db['Process'].copy().set_index(["Site", "Process"])
    EE_limits = db["Cap-Up"].copy().rename(columns={"Country":"Site", "Technology (sum over all vintages)": "Category"}).set_index(["Site", "Category"])
    ProCom = db['Process-Commodity'].copy().set_index(["Process"])
    Transmission = db['Transmission'].copy()
    Storage = db['Storage'].copy().set_index(["Site", "Storage", "Commodity"])
    db = None
    
    # Read the time series
    ts = pd.read_excel('Input' + fs + '4NEMO_Database_'+version+'_timeseries_allRegs.xlsx', sheet_name=None)
    Demand = ts['Demand'].copy()
    SupIm = ts['SupIm'].copy()
    ts = None
    
    # Eventually read the results of the previous year
    urbs_path = os.path.join("result", result_folder, "scenario_base.h5")
    # while not os.path.exists(urbs_path):
        # print("waiting for the creation of ", urbs_path)
    
    # print(urbs_path, "exists")
    helpdf = urbs.load(urbs_path)
    df_result = helpdf._result
    df_data = helpdf._data
    
    Process_prev = df_data["process"].droplevel(0)[["inst-cap"]].rename(columns={"inst-cap": "Total"})
    Process_prev_new = df_result["cap_pro_new"].droplevel(0).reset_index().rename(columns={"sit":"Site", "pro":"Process", "cap_pro_new":"Total"}).set_index(["Site", "Process"]).fillna(0)
    Process_prev = Process_prev + Process_prev_new
    
    Storage_prev = df_data["storage"].droplevel(0)[["inst-cap-p"]].rename(columns={"inst-cap-p": "P Total"})
    try:
        Storage_prev_new = df_result["cap_sto_p_new"].droplevel(0).reset_index().rename(columns={"sit":"Site", "sto":"Storage", "cap_sto_p_new":"P Total", "com":"Commodity"}).set_index(["Site", "Storage", "Commodity"]).fillna(0)
        Storage_prev = Storage_prev + Storage_prev_new
    except:
        pass
    try:
        Transmission_prev = df_result["cap_tra_new"].droplevel(0).reset_index().rename(columns={"sit": "Site In", "sit_": "Site Out", "tra": "Transmission", "com": "Commodity", "cap_tra_new": "New"}).set_index(["Site In", "Site Out", "Transmission", "Commodity"])
    except:
        pass
    #Process_prev = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Process caps", index_col=[1,2])[["Total"]]
    #Storage_prev = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Storage caps", index_col=[1,2,3])[["C Total", "P Total"]]
    #Transmission_prev = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Transmission caps", index_col=[1,2,3,4])[["New"]]
        
    # Prepare the output
    book = load_workbook('Input' + fs + version + model_type + fs + str(year) + suffix + '.xlsx')
    writer = pd.ExcelWriter('Input' + fs + version + model_type + fs + str(year) + suffix + '.xlsx', engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    
    ### Global
    WACC = Global.loc['WACC','value']
    write_Global(Global, version, model_type, suffix, year, writer)
    
    ### Site
    write_Site(Site, version, suffix, year, writer)
    
    ### Commodity
    annual, co2_price = write_Commodity(Commodity, version, suffix, year, writer)
    
    ### Process
    pro = write_Process(Process, Process_prev, EE_limits, co2_price, version, suffix, year, writer)
    
    ### Process-Commodity
    write_ProCom(ProCom, pro, year, writer)
    
    # ### Transmission
    print("Transmission")
    Transmission = Transmission[Transmission['scenario-year']==year]
    
    # Correct cap-up-p
    Transmission.loc[Transmission["cap-up"] == -1, "cap-up"] = np.inf
        
    # Save for later
    # tra_capcredit = Transmission[['Site In','Site Out','Transmission','Commodity','cap-credit']]
    
    # Prepare sheet
    Transmission['wacc'] = WACC
    Transmission.loc[Transmission["depreciation"] == 0, "depreciation"] = 50
    Transmission = Transmission[['Site In','Site Out','Transmission','Commodity','eff','inv-cost','fix-cost','var-cost','inst-cap','cap-lo','cap-up','cap-credit','wacc','depreciation']]
    
    # Change sites
    Transmission = group_sites(Transmission).groupby(["Site In", "Site Out", "Transmission", "Commodity"]) \
                                            .agg({"eff": np.min, "inv-cost": np.max, "fix-cost": np.max,
                                                  "var-cost": np.max, "inst-cap": np.sum, "cap-lo": np.sum,
                                                  "cap-up": np.sum, "cap-credit": np.mean, "wacc": np.mean,
                                                  "depreciation": np.mean}) \
                                            .reset_index()
    Transmission = Transmission[Transmission['cap-up']>0]
    
    for idx in Transmission.index:
        if Transmission.loc[idx, "Site In"] == Transmission.loc[idx, "Site Out"]:
            Transmission.drop(index=idx, inplace=True)
    
    # Evetually add new capacities from previous year
    if year > 2030:
        Transmission.set_index(['Site In','Site Out','Transmission','Commodity'], inplace=True)
        try:
            Transmission["inst-cap"] = Transmission["inst-cap"] + Transmission_prev["New"]
        except:
            pass
        Transmission.reset_index(inplace=True)
        Transmission = Transmission.fillna(0)
            
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
    write_Storage(Storage, Storage_prev, version, suffix, year, writer)
    
    ### Demand
    print("Demand")
    # Prepare sheet
    Demand_year = Demand.set_index('t')
    Demand_year = Demand_year.loc[time_slices]
    Demand_year.reset_index(inplace=True)
    Demand_year["t"] = Demand_year.index
    Demand_year.set_index('t', inplace=True)
    annual_dem = annual[annual['Commodity']=='Elec']
    annual_dem.set_index('Site', inplace=True)
    annual_dem = annual_dem['annual']
    Demand_year_weighted = add_weight(Demand_year)
    for c in Demand_year.columns:
        Demand_year[c] = (annual_dem[c] * Demand_year[c]) / Demand_year_weighted[c].sum()
        Demand_year = Demand_year.rename(columns={c: dict_countries[c]+'.Elec'})
    Demand_year = Demand_year.transpose().reset_index().groupby("index").sum().transpose()
    
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
    for c in SupIm_year.columns:
        cnew = c.replace('_','.',1)
        if "Solar_PV" in cnew.split(".")[1]:
            cnew = cnew.replace("Solar_PV","Solar",1)
        SupIm_year = SupIm_year.rename(columns={c: cnew})
    
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
                while abs(gap) > 0.1:
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