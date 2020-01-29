# Libraries

import pandas as pd
import numpy as np
from openpyxl import load_workbook
import itertools
import os
import urbs
import time


def write_Global(Global, version, suffix, year, writer):
    print("Global")
    Global_updated = pd.read_excel(os.path.join('Input', version + suffix, str(year) + '.xlsx'), sheet_name="Global", index_col=0)
    Global_updated.loc['Support timeframe', 'value'] = year
    Global_updated.to_excel(writer, sheet_name='Global', index=True)
    
    
def write_Site(Site, version, suffix, year, writer):
    print("Site")
    Site_year = Site[Site['scenario-year']==year]
    Site_year = Site_year[['Site','area']]
    Site_year = Site_year.rename(columns={'Site':'Name'})
    Site_year.to_excel(writer, sheet_name='Site', index=False)
    
    
def write_Commodity(Commodity, version, suffix, year, writer):
    print("Commodity")
    Commodity_year = Commodity[Commodity['scenario-year']==year]
    
    # Save for later
    annual = Commodity_year[['annual']].copy()
    annual.dropna(inplace=True)
    annual.reset_index(inplace=True)
    
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
    
    # Write
    Commodity_year.to_excel(writer, sheet_name='Commodity', index=False)
    
    return annual
    
    
def write_Process(Process, EE_limits, version, suffix, year, writer):
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
        
    if year == 2015:
        Process_year['Construction year'] = [int(x[-4:]) for x in Process_year.index.get_level_values(level='Process')]
        Process_year['lifetime'] = Process_year['lifetime'] - (year - Process_year['Construction year'])
        Process_year.loc[Process_year['lifetime']<0, "lifetime"] = 0
        Process_year.drop(columns=["Construction year"], inplace=True)
    
    # Prepare sheet
    Process_year['min-fraction'] = 0
    Process_year['startup-cost'] = 0
    Process_year['area-per-cap'] = 0
    Process_year['wacc'] = WACC
    Process_year = Process_year[['lifetime','inst-cap','cap-lo','cap-up','max-grad','min-fraction','inv-cost','fix-cost','var-cost','startup-cost','wacc','depreciation','area-per-cap']]
    
    # Correct max-grad, cap-up and depreciation
    Process_year.loc[Process_year['max-grad'] == 0, 'max-grad'] = np.inf
    Process_year.loc[Process_year["depreciation"] == 0, "depreciation"] = 25
    
    # Correct cap-up
    Process_year.loc[Process_year["cap-up"] == -1, "cap-up"] = np.inf
    Process_year.reset_index(inplace=True)
    # if (suffix in ["_eu", "_nation"]) and (year>2015):
        # Process_group = Process_year.copy()
        # Process_group["Category"] = [x.split("_")[0]+"_"+x.split("_")[-2] for x in Process_group["Process"]]
        # Process_group = Process_group[["Site", "Category","inst-cap"]]
        # Process_group = Process_group.groupby(["Site", "Category"]).sum()
        # Process_group = Process_group.join(EE_limits["cap-up"], how="right")
        # Process_group["rest-cap-up"] = Process_group["cap-up"] - Process_group["inst-cap"]
        
        # idx = Process_year[Process_year["cap-up"] == np.inf].index
        # idx = [i for i in idx if (Process_year.loc[i, "Process"].startswith("Solar") or Process_year.loc[i, "Process"].startswith("Wind"))]
        # Process_capped = Process_year.loc[idx]
        # Process_capped["Category"] = [x.split("_")[0]+"_"+x.split("_")[-2] for x in Process_capped["Process"]]
        # Process_capped.set_index(["Site", "Category"], inplace=True)
        # Process_capped = Process_capped.join(Process_group["rest-cap-up"])
        # Process_capped["cap-up"] = Process_group["rest-cap-up"]
        # Process_capped = Process_capped.reset_index().drop(columns=["Category", "rest-cap-up"])
        # Process_year.drop(index=idx, inplace=True)
        # Process_year = Process_year.append(Process_capped, ignore_index=True, sort=False)
    
    # Add Shunt and Slack
    sites = Process_year["Site"].unique()
    if year == 2015:
        tech = ["Slack", "Shunt"]
    else:
        tech = ["Shunt"]
    df = pd.DataFrame(0, index=pd.MultiIndex.from_product([sites, tech], names=['Site', 'Process']), columns=['inst-cap','lifetime','cap-lo','cap-up','max-grad','min-fraction','inv-cost','fix-cost','var-cost','startup-cost','wacc','depreciation','area-per-cap'])
    df["inst-cap"] = 999999
    df["cap-up"] = 999999
    df["max-grad"] = np.inf
    df["wacc"] = WACC
    df["depreciation"] = 1
    Process_year = Process_year.append(df.reset_index(), ignore_index=True, sort=False)
    
    # Write
    pro = list(Process_year["Process"].unique())
    if year > 2015:
        Process_year.drop(columns=["inst-cap", "lifetime"], inplace=True)
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
    
    # Write
    ProCom.to_excel(writer, sheet_name='Process-Commodity', index=False)
    
    
def write_Storage(Storage, version, suffix, year, writer):
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
    
    if year == 2015:
        Storage_year['Construction year'] = [int(x[-4:]) for x in Storage_year.index.get_level_values(level='Storage')]
        Storage_year['lifetime'] = Storage_year['lifetime'] - (year - Storage_year['Construction year']) + 20
        Storage_year.loc[Storage_year['lifetime']<0, "lifetime"] = 0
        Storage_year.drop(columns=["Construction year"], inplace=True)
        
    Storage_year['wacc'] = WACC
    Storage_year['inv-cost-c'] = 0
    Storage_year['fix-cost-c'] = 0
    Storage_year['var-cost-c'] = 0   
    Storage_year = Storage_year[['lifetime','inst-cap-c','cap-lo-c','cap-up-c','inst-cap-p','cap-lo-p','cap-up-p',
                                 'eff-in','eff-out','inv-cost-p','inv-cost-c','fix-cost-p','fix-cost-c','var-cost-p','var-cost-c',
                                 'wacc','depreciation','init','discharge', 'ep-ratio']]
    
    # Write
    Storage_year.reset_index(inplace=True)
    if year > 2015:
        Storage_year.drop(columns=["lifetime", "inst-cap-p", "inst-cap-c"], inplace=True)
    Storage_year.to_excel(writer, sheet_name='Storage', index=False)
    
    
def Database_to_urbs(version, suffix, time_slices):
    # Main code
    global WACC
    
    # Read the database file
    db = pd.read_excel(os.path.join('Input', '4NEMO_Database_' + version + suffix + '.xlsx'), sheet_name=None)
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
    ts = pd.read_excel(os.path.join('Input', '4NEMO_Database_'+version+'_timeseries.xlsx'), sheet_name=None)
    Demand = ts['Demand'].copy()
    SupIm = ts['SupIm'].copy()
    ts = None
    
    for year in range(2015,2026,5):
        # Prepare the output
        writer_path = os.path.join("Input", version + suffix, str(year) + ".xlsx")
        book = load_workbook(writer_path)
        writer = pd.ExcelWriter(writer_path, engine='openpyxl') 
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        
        ### Global
        WACC = Global.loc['WACC','value']
        write_Global(Global, version, suffix, year, writer)
        
        ### Site
        write_Site(Site, version, suffix, year, writer)
        
        ### Commodity
        annual = write_Commodity(Commodity, version, suffix, year, writer)
        
        ### Process
        pro = write_Process(Process, EE_limits, version, suffix, year, writer)
        
        ### Process-Commodity
        write_ProCom(ProCom, pro, year, writer)
        
        ### Transmission
        print("Transmission")
        Transmission_year = Transmission.loc[Transmission['scenario-year']==year]
        Transmission_year = Transmission_year.loc[Transmission_year['cap-up']>0]
        
        # Save for later
        # tra_capcredit = Transmission[['Site In','Site Out','Transmission','Commodity','cap-credit']]
        
        # Prepare sheet
        Transmission_year['wacc'] = WACC
        Transmission_year.loc[Transmission_year["depreciation"] == 0, "depreciation"] = 50
        Transmission_year["lifetime"] = 50
        Transmission_year = Transmission_year[['Site In','Site Out','Transmission','Commodity','lifetime','eff','inv-cost','fix-cost','var-cost','inst-cap','cap-lo','cap-up','wacc','depreciation']]
        if year > 2015:
            Transmission_year.drop(columns=["inst-cap", "lifetime"], inplace=True)
                
        # Write
        Transmission_year.to_excel(writer, sheet_name='Transmission', index=False)
        Transmission_year = None
        
        ### Storage
        write_Storage(Storage, version, suffix, year, writer)
        
        ### Demand
        print("Demand")
        # Prepare sheet
        Demand_year = Demand.set_index('t')
        Demand_year = Demand_year.loc[time_slices]
        annual_dem = annual[annual['Commodity']=='Elec']
        annual_dem.set_index('Site', inplace=True)
        annual_dem = annual_dem['annual']
        for c in Demand_year.columns:
            Demand_year[c] = (annual_dem[c] * Demand_year[c]) / Demand_year[c].sum() * len(time_slices) / 8760
            Demand_year = Demand_year.rename(columns={c: c+'.Elec'})
        
        Demand_year.reset_index(inplace=True)
        Demand_year["t"] = Demand_year.index
        Demand_year.set_index('t', inplace=True)
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
            if cnew[3:11] == "Solar_PV":
                cnew = cnew.replace("Solar_PV","Solar",1)
            SupIm_year = SupIm_year.rename(columns={c: cnew})
          
        FLH_should = SupIm_year.sum(axis=0) * len(time_slices) / 8760
        SupIm_year = SupIm_year.loc[time_slices]
        correction = FLH_should / SupIm_year.sum(axis=0)
        for cf in correction.dropna().index:
            if correction[cf] < 1:
                SupIm_year[cf] = correction[cf] * SupIm_year[cf]
            if correction[cf] > 1:
                x_min = SupIm_year[cf].min()
                x_max = SupIm_year[cf].max()
                N = len(time_slices)
                Sigma = SupIm_year[cf].sum()
                A = (Sigma/correction[cf] -N*x_min) *(x_max -x_min) / (Sigma - N*x_min)
                if (A <= 1) and (A > 0):
                    SupIm_year[cf] = (SupIm_year[cf]-x_min)/(x_max-x_min)*A+x_min
                else:
                    import pdb; pdb.set_trace()  
        
        SupIm_year.reset_index(inplace=True)
        SupIm_year["t"] = SupIm_year.index
        SupIm_year.set_index('t', inplace=True)
        # Write
        SupIm_year.to_excel(writer, sheet_name='SupIm', index=True)
        SupIm_year = None
        
        
        ### Output
        writer.save()
        print("Model file updated!")