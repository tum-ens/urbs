#!/usr/bin/env python
# coding: utf-8

# # Description

# This code reads the database file in Excel and updates the urbs input file based on it.
# 
# ### Inputs
# - 4NEMO_Database_vx.xx.xlsx
# - urbs_model_vx.xx_yyyy.xlsx
# 
# ### Outputs
# - updated file urbs_model_vx.xx_yyyy.xlsx




# # Libraries

import pandas as pd
import numpy as np
from openpyxl import load_workbook
import itertools
import os

def urbs_to_Database(version, suffix, year, result_folder):
    # # Main code
    fs = os.path.sep
    
    # Read the urbs result files
    Costs = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Costs", index_col=[0])
    Process = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Process caps", index_col=[1,2])
    Transmission = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Transmission caps", index_col=[1,2,3,4])
    Storage = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Storage caps", index_col=[1,2,3])
    Commodity = pd.read_excel('result' + fs + result_folder + fs + 'scenario_base.xlsx', sheet_name="Commodity sums", index_col=[0,1])
    
        
    # Prepare the output
    book = load_workbook('result' + fs + 'TUM' + suffix + '.xlsx')
    writer = pd.ExcelWriter('Input' + fs + 'TUM' + suffix + '.xlsx', engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    
    # ### Global
    
    Global = Global.set_index('Parameter')
    WACC = Global.loc['WACC','value']
    print("Global")
    Global2 = pd.read_excel('Input' + fs + 'urbs_model_v' + version + suffix + '_' + str(year) + '.xlsx', sheet_name="Global", index_col=0)
    Global2.loc['Support timeframe', 'value'] = year
    Global2.to_excel(writer, sheet_name='Global', index=True)
    
    # ### Site
    print("Site")
    Site = Site[Site['scenario-year']==year]
    
    # Prepare sheet
    Site = Site[['Site','area']]
    Site = Site.rename(columns={'Site':'Name'})
    
    # Write
    Site.to_excel(writer, sheet_name='Site', index=False)
    Site = None
    
    # ### Commodity
    print("Commodity")
    Commodity = Commodity[Commodity['scenario-year']==year]
    
    # Save for later
    annual = Commodity[['Site','Commodity','annual']].copy()
    annual.dropna(inplace=True)
    
    # Prepare sheet
    Commodity = Commodity[['Site','Commodity','Type','price','max','maxperhour']]
    if year == 2015:
        ind = Commodity.loc[(Commodity["Site"] == "CH") & (Commodity["Commodity"] == "CO2")].index
        Commodity.drop(index=ind, inplace=True)
        ind = Commodity.loc[Commodity["Commodity"] == "CCS_CO2"].index
        Commodity.drop(index=ind, inplace=True)
    
    # Remove CSP
    ind = Commodity.loc[(Commodity["Commodity"] == "Solar_CSP_high") | (Commodity["Commodity"] == "Solar_CSP_mid") | (Commodity["Commodity"] == "Solar_CSP_low")].index
    Commodity.drop(index=ind, inplace=True)
    
    # Rename Solar_PV to Solar
    Commodity.loc[Commodity["Commodity"] == "Solar_PV_high", "Commodity"] = "Solar_high"
    Commodity.loc[Commodity["Commodity"] == "Solar_PV_mid", "Commodity"] = "Solar_mid"
    Commodity.loc[Commodity["Commodity"] == "Solar_PV_low", "Commodity"] = "Solar_low"
    
    # Add Slack
    if year == 2015:
        sites = list(Commodity["Site"].unique())
        coms = ["Slack"]
        df = pd.DataFrame(list(itertools.product(sites, coms, ["Stock"], [0], ['inf'], ['inf'])),
                          columns=["Site", "Commodity", "Type", "price", 'max', 'maxperhour'])
        Commodity = Commodity.append(df, ignore_index=True)
        Commodity.loc[Commodity["Commodity"]=="Slack", "price"] = 999
        
    # Correct maxperhour for CCS_CO2
    Commodity.loc[Commodity["Commodity"] == "CCS_CO2", "maxperhour"] = np.inf
    
    # Write
    Commodity.to_excel(writer, sheet_name='Commodity', index=False)
    Commodity = None
    
    
    # ### Process
    print("Process")
    
    # Save for later
    pro_lifetime = Process[['Site','Process','lifetime']]
    pro_reserve = Process[['Site','Process','reserve']]
    pro_reliability = Process[['Site','Process','reliability']]
    pro_capcredit = Process[['Site','Process','cap-credit']]
    
    # Filter
    Process = Process[Process['scenario-year']==year]
    Process = Process[Process['cap-up']!=0]
    pro = Process['Process'].unique()

    
    # Prepare sheet
    Process['min-fraction'] = 0
    Process['startup-cost'] = 0
    Process['area-per-cap'] = 0
    Process['wacc'] = WACC
    Process = Process[['Site','Process','inst-cap','cap-lo','cap-up','max-grad','min-fraction','inv-cost','fix-cost','var-cost','startup-cost','wacc','depreciation','area-per-cap']]
    
    # Correct max-grad, cap-up and depreciation
    Process.loc[Process["cap-up"] == -1, "cap-up"] = np.inf
    Process.loc[Process['max-grad'] == 0, 'max-grad'] = np.inf
    Process.loc[Process["depreciation"] == 0, "depreciation"] = 25
    
    # Rename Solar_PV to Solar
    for proc in Process["Process"].unique():
        if proc.startswith("Solar_PV"):
            Process.loc[Process["Process"] == proc, "Process"] = proc[:5] + proc[8:]
    
    # Add Shunt and Slack
    if year == 2015:
        sites = list(Process["Site"].unique())
        pros = ["Slack", "Shunt"]
        df = pd.DataFrame(list(itertools.product(sites, pros, [999999], [0], [999999], [0], [0], [0], [0], [0], [0], [WACC], [1], [0])),
                          columns=['Site','Process','inst-cap','cap-lo','cap-up','max-grad','min-fraction','inv-cost','fix-cost','var-cost','startup-cost','wacc','depreciation','area-per-cap'])
        Process = Process.append(df, ignore_index=True)
    
    # Write
    Process.to_excel(writer, sheet_name='Process', index=False)
    Process = None
    
    # Remove decommissioned power plants
    if year > 2015:
        Process = pd.read_excel('Input' + fs + 'urbs_model_v' + version + suffix + '_' + str(year) + '.xlsx', sheet_name="Process", index_col=[0,1])
        pro_lifetime['Construction year'] = [int(x[-4:]) for x in pro_lifetime['Process']]
        pro_lifetime.set_index(["Site", "Process"], inplace=True)
        #idx = pro_lifetime.loc[(pro_lifetime['Construction year'] + pro_lifetime['lifetime']) > year].index
        idx_old = pro_lifetime.loc[(pro_lifetime['Construction year'] + pro_lifetime['lifetime']) <= year].index
        idx_decommissioned = Process.index.intersection(idx_old)
        Process.loc[idx_decommissioned, "inst-cap"] = 0
        # Evetually add new capacities from previous year
        if year > 2020:
            Process["inst-cap"] = Process["inst-cap"] + Process_added["New"]
        Process.reset_index(inplace=True)
        Process.to_excel(writer, sheet_name='Process', index=False)
        Process = None
    
    # ### Process-Commodity
    print("Process-Commodity")
    #ProCom = ProCom[ProCom['scenario-year']==year]
    ProCom.set_index('Process', inplace=True)
    ProCom = ProCom.loc[ProCom.index.isin(pro)].reset_index()
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
        ProCom = ProCom.append(df, ignore_index=True)
    
    # Write
    ProCom.to_excel(writer, sheet_name='Process-Commodity', index=False)
    ProCom = None
    
    # ### Transmission
    print("Transmission")
    Transmission = Transmission[Transmission['scenario-year']==year]
    Transmission = Transmission[Transmission['cap-up']>0]
    
    # Save for later
    tra_capcredit = Transmission[['Site In','Site Out','Transmission','Commodity','cap-credit']]
    
    # Prepare sheet
    Transmission['wacc'] = WACC
    Transmission.loc[Transmission["depreciation"] == 0, "depreciation"] = 50
    Transmission = Transmission[['Site In','Site Out','Transmission','Commodity','eff','inv-cost','fix-cost','var-cost','inst-cap','cap-lo','cap-up','wacc','depreciation']]
    
    # Evetually add new capacities from previous year
    if year > 2030:
        Transmission.set_index(['Site In','Site Out','Transmission','Commodity'], inplace=True)
        Transmission["inst-cap"] = Transmission["inst-cap"] + Transmission_added["New"]
        Transmission.reset_index(inplace=True)
            
    # Write
    Transmission.to_excel(writer, sheet_name='Transmission', index=False)
    Transmission = None
    
    # ### Storage
    print("Storage")
    
    # Save for later
    sto_lifetime = Storage[['Site','Storage','Commodity','lifetime']]
    
    Storage = Storage[Storage['scenario-year']==year]
    Storage = Storage[Storage['cap-up-p']!=0]
    
    # Save for later
    sto_cycles = Storage[['Site','Storage','Commodity','cycles-max']]
    sto_capcredit = Storage[['Site','Storage','Commodity','cap-credit']]
    sto_inflow = Storage[['Site','Storage','Commodity','inflow']]
    sto_etop = Storage[['Site','Storage','Commodity','e-to-p']]
    
    # Correct cap-up-p
    Storage.loc[Storage["cap-up-p"] == -1, "cap-up-p"] = np.inf
    
    # Prepare sheet
    Storage['e-to-p'] = Storage['e-to-p'].round(2)
    Storage.loc[Storage["depreciation"] == 0, "depreciation"] = 10
    #import pdb; pdb.set_trace()
    #Storage.loc[Storage["Storage"] == "PumpStorage_*", 'e-to-p'] = np.nan
    Storage['inst-cap-c'] = Storage['inst-cap-p'] * Storage['e-to-p']
    Storage['cap-lo-c'] = Storage['cap-lo-p'] * Storage['e-to-p']
    Storage['cap-up-c'] = Storage['cap-up-p'] * Storage['e-to-p']
    Storage['wacc'] = WACC
    Storage['inv-cost-c'] = 0
    Storage['fix-cost-c'] = 0
    Storage['var-cost-c'] = 0
    Storage = Storage[['Site','Storage','Commodity','inst-cap-c','cap-lo-c','cap-up-c','inst-cap-p','cap-lo-p','cap-up-p',
                       'eff-in','eff-out','inv-cost','inv-cost-c','fix-cost','fix-cost-c','var-cost','var-cost-c',
                       'wacc','depreciation','init','discharge', 'e-to-p']]
    Storage = Storage.rename(columns={'inv-cost':'inv-cost-p','fix-cost':'fix-cost-p','var-cost':'var-cost-p', 'e-to-p': 'ep-ratio'})
    
    # Write
    Storage.to_excel(writer, sheet_name='Storage', index=False)
    Storage = None
    
    # Remove decommissioned storage
    if year > 2015:
        Storage = pd.read_excel('Input' + fs + 'urbs_model_v' + version + suffix + '_' + str(year) + '.xlsx', sheet_name="Storage", index_col=[0,1])
        sto_lifetime['Construction year'] = [int(x[-4:]) for x in sto_lifetime['Storage']]
        sto_lifetime.set_index(["Site", "Storage"], inplace=True)
        idx_old = sto_lifetime.loc[(sto_lifetime['Construction year'] + sto_lifetime['lifetime']) <= year].index
        idx_decommissioned = Storage.index.intersection(idx_old)
        Storage.loc[idx_decommissioned, "inst-cap-c"] = 0
        Storage.loc[idx_decommissioned, "inst-cap-p"] = 0
        # Evetually add new capacities from previous year
        if year > 2020:
            Storage["inst-cap-c"] = Storage["inst-cap-c"] + Storage_added["C New"]
            Storage["inst-cap-p"] = Storage["inst-cap-p"] + Storage_added["P New"]
        Storage.reset_index(inplace=True)
        Storage.to_excel(writer, sheet_name='Storage', index=False)
        Storage = None
    
    
    # ### Demand
    print("Demand")
    # Prepare sheet
    Demand.set_index('t', inplace=True)
    annual_dem = annual[annual['Commodity']=='Elec']
    annual_dem.set_index('Site', inplace=True)
    annual_dem = annual_dem['annual']
    for c in Demand.columns:
        Demand[c] = annual_dem[c] * Demand[c]
        Demand = Demand.rename(columns={c: c+'.Elec'})
    
    # Write
    Demand.to_excel(writer, sheet_name='Demand', index=True)
    Demand = None
    
    
    # ### SupIm
    print("SupIm")
    # Prepare sheet
    SupIm.set_index('t', inplace=True)
    SupIm.loc[0] = 0
    SupIm.sort_index(inplace=True)
    #annual_hydro = annual[annual['Commodity']=='Hydro']
    #annual_hydro.set_index('Site', inplace=True)
    #annual_hydro = annual_hydro['annual']
    for c in SupIm.columns:
        # if c[-5:]=='Hydro':
            # SupIm[c] = annual_hydro[c[:2]] * SupIm[c]
        cnew = c.replace('_','.',1)
        if cnew[3:11] == "Solar_PV":
            cnew = cnew.replace("Solar_PV","Solar",1)
        SupIm = SupIm.rename(columns={c: cnew})
    
    # Write
    SupIm.to_excel(writer, sheet_name='SupIm', index=True)
    SupIm = None
    
    
    # # Output
    
    writer.save()
    print("Model file updated!")