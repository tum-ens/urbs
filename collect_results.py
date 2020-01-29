import os
import shutil
import urbs
import pandas as pd
import numpy as np
from openpyxl import load_workbook
import itertools

global dict_tech
global dict_countries
global dict_season

# User preferences
result_folders = [
# 'v2.00_2015_eu-20200123T0827',
'v2.00_2020_eu-20200123T1216',
# 'v2.00_2025_eu-20200125T1840',
# 'v2.00_2020_gas-20200123T1556',
# 'v2.00_2020_nation-20200125T1337',
]

dict_tech = {"Bio_CCS": "Bio-CCS",
             "Bioenergy": "Bioenergy",
             "Coal": "Coal",
             "Coal_CCS": "Coal-CCS",
             "Gas_CCGT": "Gas-CCGT",
             "Gas_CCS": "Gas-CCS",
             "Gas_OCGT": "Gas-OCGT",
             "Gas_ST": "Gas-ST",
             "Geothermal": "Geothermal",
             "Hydro": "Hydro",
             "Lignite": "Lignite",
             "Nuclear": "Nuclear",
             "OilOther": "OilOther",
             "Solar_high": "Solar",
             "Solar_low": "Solar",
             "Solar_mid": "Solar",
             "WindOff_100m_high": "WindOff",
             "WindOff_100m_low": "WindOff",
             "WindOff_100m_mid": "WindOff",
             "WindOff_120m_high": "WindOff",
             "WindOff_120m_low": "WindOff",
             "WindOff_120m_mid": "WindOff",
             "WindOff_80m_high": "WindOff",
             "WindOff_80m_low": "WindOff",
             "WindOff_80m_mid": "WindOff",
             "WindOn_100m_high": "WindOn",
             "WindOn_100m_low": "WindOn",
             "WindOn_100m_mid": "WindOn",
             "WindOn_120m_high": "WindOn",
             "WindOn_120m_low": "WindOn",
             "WindOn_120m_mid": "WindOn",
             "WindOn_80m_high": "WindOn",
             "WindOn_80m_low": "WindOn",
             "WindOn_80m_mid": "WindOn",
             "Slack": "OilOther",
             "Shunt": "Curtailment",
             }
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
dict_season = {}
for t in range(0, 8761):
    if (t <= 2184) or (t>=7897):
        dict_season[t] = "winter"
    elif (t <= 6552) and (t>=3529):
        dict_season[t] = "summer"
    else:
        dict_season[t] = "midseason"

   
def get_emissions_data(reader, writer):
    emissions = reader["Emissions"].set_index(["Site", "scenario-year"])
    emissions_by_fuel = reader["Emissions by fuel"].set_index(["Site", "scenario-year"])
    
    co2 = df_result["e_pro_out"].unstack()['CO2'].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
    co2 = co2.unstack(level=3).sum(axis=1)
    co2 = co2.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"})
    co2["Technology"] = co2["pro"]
    for pro in co2["pro"].index:
        if len(co2["pro"][pro]) > 5:
            co2.loc[pro, "Technology"] = dict_tech[co2.loc[pro, "Technology"][:-5]]
        else:
            co2.loc[pro, "Technology"] = dict_tech[co2.loc[pro, "Technology"]]
    co2 = co2.drop(columns=["pro"])
    co2 = co2.groupby(["Site", "scenario-year", "Technology"]).sum()
    co2 = co2.unstack(level=2).droplevel(0, axis=1).fillna(0)
    emissions.loc[co2.index, "CO2-emissions-elec"] = co2.sum(axis=1)
    
    emissions_by_fuel.loc[co2.index, "CO2-emissions-bioenergy"] = co2["Bioenergy"]
    emissions_by_fuel.loc[co2.index, "CO2-emissions-coal"] = co2["Coal"]
    emissions_by_fuel.loc[co2.index, "CO2-emissions-gas"] = co2["Gas-CCGT"] + co2["Gas-OCGT"] + co2["Gas-ST"]
    emissions_by_fuel.loc[co2.index, "CO2-emissions-lignite"] = co2["Lignite"]
    emissions_by_fuel.loc[co2.index, "CO2-emissions-oil/other"] = co2["OilOther"]
    
    co2_regions = co2.reset_index()
    co2_regions["Site"] = [dict_countries[x] for x in co2_regions["Site"]]
    co2_regions = co2_regions.groupby(["Site", "scenario-year"]).sum(axis=0)
    emissions.loc[co2_regions.index, "CO2-emissions-elec"] = co2_regions.sum(axis=1)
    
    emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-bioenergy"] = co2_regions["Bioenergy"]
    emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-coal"] = co2_regions["Coal"]
    emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-gas"] = co2_regions["Gas-CCGT"] + co2_regions["Gas-OCGT"] + co2_regions["Gas-ST"]
    emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-lignite"] = co2_regions["Lignite"]
    emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-oil/other"] = co2_regions["OilOther"]
    
    # CCS_CO2
    if year == "2015":
        emissions.loc[co2.index, "CO2-captured"] = 0
        emissions.loc[co2_regions.index, "CO2-captured"] = 0
    else:
        ccs_co2 = df_result["e_pro_out"].unstack()['CCS_CO2'].droplevel([0,3]).reorder_levels(['sit', 'stf']).sort_index().fillna(0)
        ccs_co2 = ccs_co2.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"}).groupby(["Site", "scenario-year"]).sum()
        emissions.loc[ccs_co2.index, "CO2-captured"] = ccs_co2["CCS_CO2"]
        
        ccs_co2_regions = ccs_co2.reset_index()
        ccs_co2_regions["Site"] = [dict_countries[x] for x in ccs_co2_regions["Site"]]
        ccs_co2_regions = ccs_co2_regions.groupby(["Site", "scenario-year"]).sum(axis=0)
        emissions.loc[ccs_co2_regions.index, "CO2-captured"] = ccs_co2_regions["CCS_CO2"]
        
    # Save results
    emissions.reset_index().to_excel(writer, sheet_name='Emissions', index=False)
    emissions_by_fuel.reset_index().to_excel(writer, sheet_name='Emissions by fuel', index=False)
    
    
def get_electricity_data(reader, writer):
    electricity = reader["Electricity"].set_index(["Site", "scenario-year"])
    hourly_prices = reader["Hourly prices"].set_index(["Hours", "Year"])
    
    prices = df_result["res_vertex"].xs(('Elec', 'Demand'), level=('com', 'com_type')).reorder_levels(['sit', 'stf', 't']).sort_index()
    prices = prices.reset_index().rename(columns={"sit": "Site", "stf": "scenario-year"})
    prices["season"] = [dict_season[x] for x in prices["t"]]
    demand = df_data["demand"].droplevel(1, axis=1).stack().reorder_levels([2, 0, 1])
    demand = demand.reset_index().rename(columns={"level_0": "Site", "support_timeframe": "scenario-year"})
    demand["season"] = [dict_season[x] for x in demand["t"]]
    
    # Averages
    prices_avg = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg.index, "price-avg"] = prices_avg["res_vertex"]
    prices_avg_winter = prices.loc[prices["season"]=="winter", ["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg_winter.index, "price-avg-winter"] = prices_avg_winter["res_vertex"]
    prices_avg_summer = prices.loc[prices["season"]=="summer", ["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg_summer.index, "price-avg-summer"] = prices_avg_summer["res_vertex"]
    prices_avg_midseason = prices.loc[prices["season"]=="midseason", ["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg_midseason.index, "price-avg-midseason"] = prices_avg_midseason["res_vertex"]
    # Median
    prices_median = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).median()
    electricity.loc[prices_median.index, "price-median"] = prices_median["res_vertex"]
    # Max
    prices_max = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).max()
    electricity.loc[prices_max.index, "price-max"] = prices_max["res_vertex"]
    # Min
    prices_min = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).min()
    electricity.loc[prices_min.index, "price-min"] = prices_min["res_vertex"]
    # Demand
    dem = demand[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).sum()
    electricity.loc[dem.index, "elec-demand"] = dem[0]
    # Hourly prices
    prices_h = prices.rename(columns={"scenario-year":"Year", "t":"Hours"}).drop(columns=["season"]).set_index(["Hours", "Year", "Site"]).unstack()["res_vertex"]
    hourly_prices.loc[prices_h.index, prices_h.columns] = prices_h
    
    # Repeat for groups of countries
    prices_weighted = prices.set_index(["Site", "scenario-year", "t"])["res_vertex"]
    prices_weighted = demand.set_index(["Site", "scenario-year", "t"]).loc[prices_weighted.index][0] * prices_weighted
    prices_weighted_regions = prices_weighted.reset_index()
    prices_weighted_regions["Site"] = [dict_countries[x] for x in prices_weighted_regions["Site"]]
    prices_weighted_regions = prices_weighted_regions.groupby(["Site", "scenario-year", "t"]).sum(axis=0)
    
    dem_regions = demand.drop(columns=["season"])
    dem_regions["Site"] = [dict_countries[x] for x in dem_regions["Site"]]
    dem_regions = dem_regions.groupby(["Site", "scenario-year","t"]).sum()
    
    prices_weighted_regions = prices_weighted_regions / dem_regions.loc[prices_weighted_regions.index]
    prices_weighted_regions = prices_weighted_regions.reset_index()
    prices_weighted_regions["season"] = [dict_season[x] for x in prices_weighted_regions["t"]]
    
    # Averages
    prices_weighted_avg = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_weighted_avg.index, "price-avg"] = prices_weighted_avg[0]
    prices_weighted_winter = prices_weighted_regions.loc[prices_weighted_regions["season"]=="winter", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_weighted_winter.index, "price-avg-winter"] = prices_weighted_winter[0]
    prices_weighted_summer = prices_weighted_regions.loc[prices_weighted_regions["season"]=="summer", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_weighted_summer.index, "price-avg-summer"] = prices_weighted_summer[0]
    prices_weighted_midseason = prices_weighted_regions.loc[prices_weighted_regions["season"]=="midseason", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_weighted_midseason.index, "price-avg-midseason"] = prices_weighted_midseason[0]
    # Median
    prices_weighted_median = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).median()
    electricity.loc[prices_weighted_median.index, "price-median"] = prices_weighted_median[0]
    # Max
    prices_weighted_max = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).max()
    electricity.loc[prices_weighted_max.index, "price-max"] = prices_weighted_max[0]
    # Min
    prices_weighted_min = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).min()
    electricity.loc[prices_weighted_min.index, "price-min"] = prices_weighted_min[0]
    # Demand
    dem_regions = dem_regions.unstack().sum(axis=1)
    electricity.loc[dem_regions.index, "elec-demand"] = dem_regions
    # Hourly prices
    prices_h_regions = prices_weighted_regions.rename(columns={"scenario-year":"Year", "t":"Hours"}).drop(columns=["season"]).set_index(["Hours", "Year", "Site"]).unstack()[0]
    hourly_prices.loc[prices_h_regions.index, prices_h_regions.columns] = prices_h_regions
    
    # Save results
    electricity.reset_index().to_excel(writer, sheet_name='Electricity', index=False)
    hourly_prices.reset_index().to_excel(writer, sheet_name='Hourly prices', index=False)
    

def get_generation_data(reader, writer):
    generation = reader["Electricity generation"].set_index(["Site", "scenario-year"])
    
    prod = df_result["e_pro_out"].unstack()['Elec'].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
    prod = prod.unstack(level=3).sum(axis=1)
    prod = prod.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"})
    prod["Technology"] = prod["pro"]
    for pro in prod["pro"].index:
        if len(prod["pro"][pro]) > 5:
            prod.loc[pro, "Technology"] = dict_tech[prod.loc[pro, "Technology"][:-5]]
        else:
            prod.loc[pro, "Technology"] = dict_tech[prod.loc[pro, "Technology"]]
    
    prod = prod.drop(columns=["pro"]).groupby(["Site", "scenario-year", "Technology"]).sum().unstack()[0].fillna(0)
    generation.loc[prod.index, prod.columns] = prod
    generation.loc[prod.index] = generation.loc[prod.index].fillna(0)
    
    prod_regions = prod.reset_index()
    prod_regions["Site"] = [dict_countries[x] for x in prod_regions["Site"]]
    prod_regions = prod_regions.groupby(["Site", "scenario-year"]).sum(axis=0)
    generation.loc[prod_regions.index, prod_regions.columns] = prod_regions
    generation.loc[prod_regions.index] = generation.loc[prod_regions.index].fillna(0)
    
    generation.reset_index().to_excel(writer, sheet_name='Electricity generation', index=False)


def get_capacities_data(reader, writer):
    capacities_total = reader["Installed capacities"].set_index(["Site", "scenario-year"])
    capacities_new = reader["Added capacities"].set_index(["Site", "scenario-year"])
    capacities_retired = reader["Capacities retired"].set_index(["Site", "scenario-year"])
    
    # New capacities
    cap_new = df_result["cap_pro_new"].reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "pro":"Process", "cap_pro_new":"inst-cap"})
    cap_new["Technology"] = cap_new["Process"]
    for pro in cap_new["Process"].index:
        if cap_new["Process"][pro] in ["Slack", "Shunt"]:
            cap_new.drop(index=pro, inplace=True)
            continue
        if len(cap_new["Process"][pro]) > 5:
            cap_new.loc[pro, "Technology"] = dict_tech[cap_new.loc[pro, "Technology"][:-5]]
        else:
            cap_new.loc[pro, "Technology"] = dict_tech[cap_new.loc[pro, "Technology"]]
    cap_new = cap_new.drop(columns=["Process"]).groupby(["Site", "scenario-year", "Technology"]).sum()
    cap_new_regions = cap_new.reset_index()
    cap_new_regions["Site"] = [dict_countries[x] for x in cap_new_regions["Site"]]
    cap_new_regions = cap_new_regions.groupby(["Site", "scenario-year", "Technology"]).sum()
    
    # Total capacity, Retired capacity
    cap_total = df_data["process"][["inst-cap"]].reset_index().rename(columns={"support_timeframe": "scenario-year"})
    cap_total["Technology"] = cap_total["Process"]
    for pro in cap_total["Process"].index:
        if cap_total["Process"][pro] in ["Slack", "Shunt"]:
            cap_total.drop(index=pro, inplace=True)
            continue
        if len(cap_total["Process"][pro]) > 5:
            cap_total.loc[pro, "Technology"] = dict_tech[cap_total.loc[pro, "Technology"][:-5]]
        else:
            cap_total.loc[pro, "Technology"] = dict_tech[cap_total.loc[pro, "Technology"]]
    year_now = cap_total["scenario-year"].unique()[0]
    cap_total = cap_total.drop(columns=["Process"]).groupby(["Site", "scenario-year", "Technology"]).sum()
    cap_retired = - cap_total.copy()
    cap_total = cap_total + cap_new
    cap_total_regions = cap_total.reset_index()
    cap_total_regions["Site"] = [dict_countries[x] for x in cap_total_regions["Site"]]
    cap_total_regions = cap_total_regions.groupby(["Site", "scenario-year", "Technology"]).sum()
    
    # Save results
    cap_new = cap_new.unstack()["inst-cap"].fillna(0)
    capacities_new.loc[cap_new.index, cap_new.columns] = cap_new
    cap_total = cap_total.unstack()["inst-cap"].fillna(0)
    capacities_total.loc[cap_total.index, cap_total.columns] = cap_total
    
    # Repeat for groups of regions
    cap_new_regions = cap_new_regions.unstack()["inst-cap"].fillna(0)
    capacities_new.loc[cap_new_regions.index, cap_new_regions.columns] = cap_new_regions
    cap_total_regions = cap_total_regions.unstack()["inst-cap"].fillna(0)
    capacities_total.loc[cap_total_regions.index, cap_total_regions.columns] = cap_total_regions
    
    # Retired capacity (continued)
    if year_now == 2015:
        capacities_retired.loc[cap_total.index, :] = 0
        capacities_retired.loc[cap_total_regions.index, :] = 0
    else:
        index_past = pd.MultiIndex.from_product([[*dict_countries], [year_now-5]], names=["Site", "scenario-year"])
        cap_total_past = capacities_total.loc[index_past].stack().reset_index().rename(columns={"level_2": "Technology", 0:"inst-cap-past"})
        cap_total_past["scenario-year"] = year_now
        cap_total_past = cap_total_past.set_index(["Site", "scenario-year", "Technology"])
        cap_retired = cap_retired.join(cap_total_past).fillna(0)
        cap_retired["inst-cap"] = cap_retired["inst-cap"] + cap_retired["inst-cap-past"]
        cap_retired.loc[abs(cap_retired["inst-cap"])<0.00001, "inst-cap"] = 0

        cap_retired = cap_retired.drop(columns=["inst-cap-past"])
        cap_retired_regions = cap_retired.reset_index()
        cap_retired_regions["Site"] = [dict_countries[x] for x in cap_retired_regions["Site"]]
        cap_retired_regions = cap_retired_regions.groupby(["Site", "scenario-year", "Technology"]).sum()
    
        cap_retired = cap_retired.unstack()["inst-cap"].fillna(0)
        capacities_retired.loc[cap_retired.index, cap_retired.columns] = cap_retired
        cap_retired_regions = cap_retired_regions.unstack()["inst-cap"].fillna(0)
        capacities_retired.loc[cap_retired_regions.index, cap_retired_regions.columns] = cap_retired_regions
    
    capacities_total.reset_index().to_excel(writer, sheet_name='Installed capacities', index=False)
    capacities_new.reset_index().to_excel(writer, sheet_name='Added capacities', index=False)
    capacities_retired.reset_index().to_excel(writer, sheet_name='Capacities retired', index=False)
    return cap_pro

def get_storage_data(reader, writer):
    storage = reader["Storage"].set_index(["Site", "Storage type", "scenario-year"])
    
    # New capacities
    cap_p_new = df_result["cap_sto_p_new"].droplevel(3).reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage type", "cap_sto_p_new":"new-inst-cap-p"}).fillna(0)
    cap_p_new = cap_p_new.set_index(["Site", "Storage type", "scenario-year"])
    cap_c_new = df_result["cap_sto_c_new"].droplevel(3).reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage type", "cap_sto_c_new":"new-inst-cap-c"}).fillna(0)
    cap_c_new = cap_c_new.set_index(["Site", "Storage type", "scenario-year"])
    
    
    # Old capacity
    cap_p_old = df_data["storage"][["inst-cap-p"]].droplevel(3).reset_index().rename(columns={"support_timeframe": "scenario-year", "Storage": "Storage type"})
    year_now = cap_p_old["scenario-year"].unique()[0]
    cap_p_old = cap_p_old.set_index(["Site", "Storage type", "scenario-year"])
    cap_c_old = df_data["storage"][["inst-cap-c"]].droplevel(3).reset_index().rename(columns={"support_timeframe": "scenario-year", "Storage": "Storage type"})
    cap_c_old = cap_c_old.set_index(["Site", "Storage type", "scenario-year"])
    
    # Retired capacity
    cap_p_retired = - cap_p_old.rename(columns={"inst-cap-p": "retired-cap-p"})
    cap_c_retired = - cap_c_old.rename(columns={"inst-cap-c": "retired-cap-c"})
    
    storage_cap = cap_p_old.join([cap_c_old, cap_p_new, cap_c_new, cap_p_retired, cap_c_retired])
    storage_cap["inst-cap-p"] = storage_cap["inst-cap-p"] + storage_cap["new-inst-cap-p"]
    storage_cap["inst-cap-c"] = storage_cap["inst-cap-c"] + storage_cap["new-inst-cap-c"]
    
    # Rename storage types
    storage_cap = storage_cap.reset_index()
    for idx in storage_cap.index:
        if storage_cap.loc[idx, "Storage type"].startswith("Storage_"):
            storage_cap.loc[idx, "Storage type"] = storage_cap.loc[idx, "Storage type"][:-5]
    storage_types = storage_cap["Storage type"].unique()
    storage_cap = storage_cap.set_index(["Site", "Storage type", "scenario-year"])
            
    # Retired capacity (continued)
    if year_now == 2015:
        storage_cap["retired-cap-p"] = 0
        storage_cap["retired-cap-c"] = 0
    else:
        index_past = pd.MultiIndex.from_product([[*dict_countries], storage_types, [year_now-5]], names=["Site", "Storage type", "scenario-year"])
        cap_p_past = storage.loc[index_past, "inst-cap-p"].fillna(0).reset_index().rename(columns={"inst-cap-p": "retired-cap-p"})
        cap_c_past = storage.loc[index_past, "inst-cap-c"].fillna(0).reset_index().rename(columns={"inst-cap-c": "retired-cap-c"})
        cap_p_past["scenario-year"] = year_now
        cap_c_past["scenario-year"] = year_now
        cap_p_past = cap_p_past.set_index(["Site", "Storage type", "scenario-year"])
        cap_c_past = cap_c_past.set_index(["Site", "Storage type", "scenario-year"])
        storage_cap["retired-cap-p"] = storage_cap["retired-cap-p"] + cap_p_past.T.squeeze()
        storage_cap["retired-cap-c"] = storage_cap["retired-cap-c"] + cap_c_past.T.squeeze()
        storage_cap = storage_cap.fillna(0)
        
    storage_cap_regions = storage_cap.reset_index()
    storage_cap_regions["Site"] = [dict_countries[x] for x in storage_cap_regions["Site"]]
    storage_cap_regions = storage_cap_regions.groupby(["Site", "Storage type", "scenario-year"]).sum()
        
    storage_con = df_result["e_sto_con"].droplevel([4]).reset_index().rename(columns={"stf":"scenario-year", "sit":"Site", "sto": "Storage type", "e_sto_con":"avg-state-of-charge"})
    storage_con_regions = storage_con.copy()
    storage_con_regions["Site"] = [dict_countries[x] for x in storage_con_regions["Site"]]
    storage_con_regions = storage_con_regions.groupby(["Site", "Storage type", "scenario-year", "t"]).sum().droplevel(3).reset_index()
    storage_con = storage_con.groupby(["Site", "Storage type", "scenario-year"]).mean().drop(columns=["t"])
    storage_con_regions = storage_con_regions.groupby(["Site", "Storage type", "scenario-year"]).mean()
    
    # Correct storage type
    storage_con = storage_con.reset_index()
    for idx in storage_con.index:
        if storage_con.loc[idx, "Storage type"].startswith("Storage_"):
            storage_con.loc[idx, "Storage type"] = storage_con.loc[idx, "Storage type"][:-5]
    storage_con = storage_con.set_index(["Site", "Storage type", "scenario-year"])
    storage_con_regions = storage_con_regions.reset_index()
    for idx in storage_con_regions.index:
        if storage_con_regions.loc[idx, "Storage type"].startswith("Storage_"):
            storage_con_regions.loc[idx, "Storage type"] = storage_con_regions.loc[idx, "Storage type"][:-5]
    storage_con_regions = storage_con_regions.set_index(["Site", "Storage type", "scenario-year"])
    
    # Save results
    storage.loc[storage_cap.index, storage_cap.columns] = storage_cap.fillna(0)
    storage.loc[storage_cap_regions.index, storage_cap_regions.columns] = storage_cap_regions.fillna(0)
    storage.loc[storage_con.index, storage_con.columns] = storage_con
    storage.loc[storage_con_regions.index, storage_con_regions.columns] = storage_con_regions

    storage.reset_index().to_excel(writer, sheet_name='Storage', index=False)
    
    

def get_curtailment_data(reader, writer):
    curtailment = reader["Curtailment"]
    
    curtailed = df_result["e_pro_in"].unstack()["Elec"].dropna().droplevel(3).reorder_levels(['sit', 'stf', 't']).sort_index()
    curtailed = curtailed.reset_index().rename(columns={"sit": "Site", "stf": "scenario-year"})
    year_now = curtailed["scenario-year"].unique()[0]
    curtailed = curtailed.set_index(["Site", "scenario-year", "t"])
    
    prod = df_result["e_pro_out"].unstack()['Elec'].unstack().reorder_levels(['sit', 'stf', 't']).sort_index().fillna(0)
    for pro in prod.columns:
        if (len(pro) > 5) and (dict_tech[pro[:-5]] in ["Solar", "WindOn", "WindOff", "Hydro"]):
            prod = prod.rename(columns={pro: dict_tech[pro[:-5]]})
        else:
            prod = prod.drop(columns=pro)
    
    prod = prod.stack().reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"}).groupby(["Site", "scenario-year", "t", "pro"]).sum()
    prod = prod.unstack().fillna(0)[0]
    
    curtailed = curtailed.join(prod[["Solar", "WindOn", "WindOff", "Hydro"]])
    curtailed = curtailed.loc[curtailed["Elec"]>0]
    
    # Order of curtailment: Solar, WindOn, WindOff, Hydro
    for idx in curtailed.index:
        for pp in ["Solar", "WindOn", "WindOff", "Hydro"]:
            curtailed.loc[idx, pp] = min(curtailed.loc[idx, "Elec"], curtailed.loc[idx, pp])
            curtailed.loc[idx, "Elec"] = curtailed.loc[idx, "Elec"] - curtailed.loc[idx, pp]

    curtailed = curtailed.drop(columns=["Elec"]).droplevel(2).reset_index().groupby(["Site", "scenario-year"]).sum()
    curtailed_regions = curtailed.reset_index()
    curtailed_regions["Site"] = [dict_countries[x] for x in curtailed_regions["Site"]]
    curtailed_regions = curtailed_regions.groupby(["Site", "scenario-year"]).sum()
    
    # Save results
    curtailment.loc[curtailment["scenario-year"]==year_now] = curtailment.loc[curtailment["scenario-year"]==year_now].fillna(0)
    curtailment = curtailment.set_index(["Site", "scenario-year"])
    curtailment.loc[curtailed.index, curtailed.columns] = curtailed
    curtailment.loc[curtailed_regions.index, curtailed_regions.columns] = curtailed_regions
    curtailment.reset_index().to_excel(writer, sheet_name='Curtailment', index=False)
    

def get_transfer_data(reader, writer):
    transfers = reader["Transfers"].set_index(["Site", "scenario-year"])
    
    tra_out = df_result["e_tra_out"].droplevel([0,4,5]).reset_index().rename(columns={"stf": "scenario-year", "sit": "Site", "sit_": "Site Out"})
    tra_out = tra_out.groupby(["Site", "scenario-year", "Site Out"]).sum().reset_index()
    
    tra_out_regions = tra_out.copy()
    tra_out_regions["Site"] = [dict_countries[x] for x in tra_out_regions["Site"]]
    tra_out_regions["Site Out"] = [dict_countries[x] for x in tra_out_regions["Site Out"]]
    
    idx_drop = []
    for idx in tra_out_regions.index:
        if tra_out_regions.loc[idx, "Site"] == tra_out_regions.loc[idx, "Site Out"]:
            idx_drop = idx_drop + [idx]
    tra_out_regions = tra_out_regions.drop(index=idx_drop)
    
    tra_out = tra_out.set_index(["Site", "scenario-year", "Site Out"]).unstack()["e_tra_out"]
    tra_out_regions = tra_out_regions.groupby(["Site", "scenario-year", "Site Out"]).sum().unstack()["e_tra_out"]
    
    transfers.loc[tra_out.index, tra_out.columns] = tra_out
    transfers.loc[tra_out_regions.index, tra_out_regions.columns] = tra_out_regions
    transfers.reset_index().to_excel(writer, sheet_name='Transfers', index=False)
    
    
def get_NTC_data(reader, writer):
    NTC = reader["NTC"].set_index(["Site", "scenario-year"])
    
    ntc_inst = df_data["transmission"]["inst-cap"].reset_index().rename(columns={"support_timeframe": "scenario-year", "Site In": "Site"})
    ntc_inst = ntc_inst.set_index(["Site", "scenario-year", "Transmission", "Commodity", "Site Out"])
    ntc_new = df_result["cap_tra_new"].reset_index().rename(columns={"stf": "scenario-year", "sit": "Site", "sit_": "Site Out", "tra": "Transmission", "com": "Commodity", "cap_tra_new": "inst-cap"})
    ntc_new = ntc_new.set_index(["Site", "scenario-year", "Transmission", "Commodity", "Site Out"])
    ntc_inst = ntc_inst + ntc_new
    ntc_inst = ntc_inst.droplevel([2,3]).reset_index().groupby(["Site", "scenario-year", "Site Out"]).sum().unstack()["inst-cap"]
    
    ntc_inst_regions = ntc_inst.stack().reset_index()
    ntc_inst_regions["Site"] = [dict_countries[x] for x in ntc_inst_regions["Site"]]
    ntc_inst_regions["Site Out"] = [dict_countries[x] for x in ntc_inst_regions["Site Out"]]
    
    idx_drop = []
    for idx in ntc_inst_regions.index:
        if ntc_inst_regions.loc[idx, "Site"] == ntc_inst_regions.loc[idx, "Site Out"]:
            idx_drop = idx_drop + [idx]
    ntc_inst_regions = ntc_inst_regions.drop(index=idx_drop)
    
    ntc_inst_regions = ntc_inst_regions.groupby(["Site", "scenario-year", "Site Out"]).sum().unstack()[0]
    
    NTC.loc[ntc_inst.index, ntc_inst.columns] = ntc_inst
    NTC.loc[ntc_inst_regions.index, ntc_inst_regions.columns] = ntc_inst_regions
    NTC.reset_index().to_excel(writer, sheet_name='NTC', index=False)
    
    
def get_NTC_rents_data(reader, writer):
    NTC_rents = reader["NTC rents"].set_index(["Site", "scenario-year"])
    hourly_prices = reader["Hourly prices"].rename(columns={"Hours":"t", "Year":"scenario-year"}).dropna()
    hourly_prices = hourly_prices.set_index(["t", "scenario-year"]).stack().reset_index()
    
    prices_site = hourly_prices.rename(columns={"level_2": "Site"}).set_index(["t", "scenario-year", "Site"])
    prices_siteout = hourly_prices.rename(columns={"level_2": "Site Out"}).set_index(["t", "scenario-year", "Site Out"])
    
    tra_out = df_result["e_tra_out"].droplevel([4,5]).reset_index().rename(columns={"stf": "scenario-year", "sit": "Site", "sit_": "Site Out"})
    tra_out_regions = tra_out.copy()
    tra_out_regions["Site"] = [dict_countries[x] for x in tra_out_regions["Site"]]
    tra_out_regions["Site Out"] = [dict_countries[x] for x in tra_out_regions["Site Out"]]
    tra_out_regions = tra_out_regions.groupby(["t", "Site", "scenario-year", "Site Out"]).sum().reset_index()
    tra_out = tra_out.append(tra_out_regions, sort=True, ignore_index=True)
    
    tra_out = tra_out.set_index(["t", "scenario-year", "Site"]).join(prices_site).rename(columns={0: "price Site"}).reset_index()
    tra_out = tra_out.set_index(["t", "scenario-year", "Site Out"]).join(prices_siteout).rename(columns={0: "price Site Out"}).reset_index()
    tra_out["rent"] = (tra_out["price Site Out"] - tra_out["price Site"]) * tra_out["e_tra_out"]
    
    tra_out = tra_out.drop(columns=["e_tra_out", "t", "price Site", "price Site Out"]).groupby(["Site", "scenario-year", "Site Out"]).sum().reset_index()
    idx_drop = []
    for idx in tra_out.index:
        if tra_out.loc[idx, "rent"] == 0:
            idx_drop = idx_drop + [idx]
        if tra_out.loc[idx, "rent"] < 0:
            aux = tra_out.loc[idx, "Site"]
            tra_out.loc[idx, "Site"] = tra_out.loc[idx, "Site Out"]
            tra_out.loc[idx, "Site Out"] = aux
            tra_out.loc[idx, "rent"] = - tra_out.loc[idx, "rent"]
    tra_out = tra_out.drop(index=idx_drop).groupby(["Site", "scenario-year", "Site Out"]).sum().unstack()["rent"]
    
    NTC_rents.loc[tra_out.index, tra_out.columns] = tra_out
    NTC_rents.reset_index().to_excel(writer, sheet_name='NTC rents', index=False)


def get_cost_data(reader, writer, discount):
    costs = reader["Total system costs"].set_index(["Site", "scenario-year"])
    
    process = df_data["process"].drop(columns="support_timeframe").reset_index().rename(columns={"support_timeframe": "scenario-year"}).set_index(["Site", "scenario-year", "Process"])
    storage = df_data["storage"].reset_index().rename(columns={"support_timeframe": "scenario-year"}).set_index(["Site", "scenario-year", "Storage", "Commodity"])
    transmission = df_data["transmission"].reset_index().rename(columns={"support_timeframe": "scenario-year"}).set_index(["Site In", "scenario-year", "Transmission", "Commodity", "Site Out"])
    
    # Get helping factors
    discount = df_data["global_prop"].droplevel(0).loc["Discount rate", "value"]
    storage["invcost-factor"] = (storage["depreciation"] * ((1 + storage["wacc"]) ** storage["depreciation"] * storage["wacc"]) / ((1 + storage["wacc"]) ** storage["depreciation"] - 1))
    transmission["invcost-factor"] = (transmission["depreciation"] * ((1 + transmission["wacc"]) ** transmission["depreciation"] * transmission["wacc"]) / ((1 + transmission["wacc"]) ** transmission["depreciation"] - 1))
    
    # Get newly installed capacities
    cap_pro_new = df_result["cap_pro_new"].reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "pro":"Process"}).set_index(["Site", "scenario-year", "Process"])
    cap_sto_p_new = df_result["cap_sto_p_new"].reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage", "com":"Commodity"}).fillna(0)
    cap_sto_p_new = cap_sto_p_new.set_index(["Site", "scenario-year", "Storage", "Commodity"])
    cap_sto_c_new = df_result["cap_sto_c_new"].reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage", "com":"Commodity"}).fillna(0)
    cap_sto_c_new = cap_sto_c_new.set_index(["Site", "scenario-year", "Storage", "Commodity"])
    cap_tra_new = df_result["cap_tra_new"].reset_index().rename(columns={"stf": "scenario-year", "sit": "Site In", "sit_": "Site Out", "tra": "Transmission", "com": "Commodity"})
    cap_tra_new = cap_tra_new.set_index(["Site In", "scenario-year", "Transmission", "Commodity", "Site Out"])
    process = process.join(cap_pro_new)
    storage = storage.join([cap_sto_p_new, cap_sto_c_new])
    transmission = transmission.join(cap_tra_new)
    
    # Correct total installed capacity
    process["inst-cap"] = process["inst-cap"] + process["cap_pro_new"]
    storage["inst-cap-p"] = storage["inst-cap-p"] + storage["cap_sto_p_new"]
    storage["inst-cap-c"] = storage["inst-cap-c"] + storage["cap_sto_c_new"]
    transmission["inst-cap"] = transmission["inst-cap"] + transmission["cap_tra_new"]
    
    # Get produced energy
    prod = df_result["e_pro_out"].unstack()['Elec'].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
    prod = prod.unstack(level=3).sum(axis=1).reset_index().rename(columns={"sit":"Site", "stf": "scenario-year", "pro": "Process", 0: "prod"}).set_index(["Site", "scenario-year", "Process"])
    process = process.join(prod)
    
    # Get consumed fuels
    fuel = df_result["e_pro_in"].droplevel(0).reset_index().rename(columns={"sit":"Site", "stf": "scenario-year", "pro": "Process", "com": "Commodity"})
    fuel = fuel.groupby(["Site", "scenario-year", "Process", "Commodity"]).sum().reset_index().set_index(["Site", "scenario-year", "Commodity"])
    fuel_price = df_data["commodity"]["price"].reset_index().rename(columns={"support_timeframe": "scenario-year"}).drop(columns="Type").set_index(["Site", "scenario-year", "Commodity"])
    fuel = fuel.join(fuel_price).reset_index().set_index(["Site", "scenario-year", "Process"]).fillna(0).drop(columns=["Commodity"])
    process = process.join(fuel)
    
    # Get emissions
    emissions = df_result["e_pro_out"].unstack()[['CO2', "CCS_CO2"]].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
    emissions = emissions.stack().reset_index().rename(columns={"sit":"Site", "stf": "scenario-year", "pro": "Process", "com": "Commodity", 0: "emissions"}).groupby(["Site", "scenario-year", "Process", "Commodity"]).sum()
    emissions = emissions.reset_index().set_index(["Site", "scenario-year", "Commodity"]).join(fuel_price.rename(columns={"price": "emissions_price"}))
    emissions = emissions.reset_index().set_index(["Site", "scenario-year", "Process"]).drop(columns=["Commodity", "t"])
    
    # Investment costs
    process["costs_inv"] = process["cap_pro_new"] * process["inv-cost"] * process["invcost-factor"] # alt for intertemporal: 'overpay-factor'
    storage["costs_inv"] = (storage["cap_sto_p_new"] * storage["inv-cost-p"] + storage["cap_sto_c_new"] * storage["inv-cost-c"]) * storage["invcost-factor"] # alt for intertemporal: 'overpay-factor'
    transmission["costs_inv"] = transmission["cap_tra_new"] * transmission["inv-cost"] * transmission["invcost-factor"] # alt for intertemporal: 'overpay-factor'
    import pdb; pdb.set_trace()
    
    # Fix costs
    
    
        
    # Fix costs
    if cost_type == 'Fixed':
        cost = \
            sum(m.cap_pro[p] * m.process_dict['fix-cost'][p] *
                m.process_dict['cost_factor'][p]
                for p in m.pro_tuples)
        
        return sum(m.cap_tra[t] * m.transmission_dict['fix-cost'][t] *
                   m.transmission_dict['cost_factor'][t]
                   for t in m.tra_tuples)
                   
        return sum((m.cap_sto_p[s] * m.storage_dict['fix-cost-p'][s] +
                    m.cap_sto_c[s] * m.storage_dict['fix-cost-c'][s]) *
                   m.storage_dict['cost_factor'][s]
                   for s in m.sto_tuples)
        
    # Variable costs
    elif cost_type == 'Variable':
        cost = \
            sum(m.tau_pro[(tm,) + p] * m.weight *
                m.process_dict['var-cost'][p] *
                m.process_dict['cost_factor'][p]
                for tm in m.tm
                for p in m.pro_tuples)
        if m.mode['tra']:
            cost += transmission_cost(m, cost_type)
        if m.mode['sto']:
            cost += storage_cost(m, cost_type)
        return m.costs[cost_type] == cost
        
        return sum(m.e_tra_in[(tm,) + t] * m.weight *
                   m.transmission_dict['var-cost'][t] *
                   m.transmission_dict['cost_factor'][t]
                   for tm in m.tm
                   for t in m.tra_tuples)
                   
        return sum(m.e_sto_con[(tm,) + s] * m.weight *
                   m.storage_dict['var-cost-c'][s] *
                   m.storage_dict['cost_factor'][s] +
                   (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) *
                   m.weight * m.storage_dict['var-cost-p'][s] *
                   m.storage_dict['cost_factor'][s]
                   for tm in m.tm
                   for s in m.sto_tuples)

    elif cost_type == 'Fuel':
        return m.costs[cost_type] == sum(
            m.e_co_stock[(tm,) + c] * m.weight *
            m.commodity_dict['price'][c] *
            m.commodity_dict['cost_factor'][c]
            for tm in m.tm for c in m.com_tuples
            if c[2] in m.com_stock)

    elif cost_type == 'Environmental':
        return m.costs[cost_type] == sum(
            - commodity_balance(m, tm, stf, sit, com) * m.weight *
            m.commodity_dict['price'][(stf, sit, com, com_type)] *
            m.commodity_dict['cost_factor'][(stf, sit, com, com_type)]
            for tm in m.tm
            for stf, sit, com, com_type in m.com_tuples
            if com in m.com_env)


def get_FLH_data(reader, writer):
    # Generation
    capacities_total = reader["Installed capacities"].set_index(["Site", "scenario-year"]).dropna()
    generation = reader["Electricity generation"].set_index(["Site", "scenario-year"]).loc[capacities_total.index]
    FLH_generation = reader["Full-load hours generation"].set_index(["Site", "scenario-year"])
    
    FLH_generation.loc[capacities_total.index] = generation / capacities_total
    FLH_generation.reset_index().to_excel(writer, sheet_name='Full-load hours generation', index=False)
    
    # Transmission
    NTC = reader["NTC"].set_index(["Site", "scenario-year"]).dropna(how="all")
    transfers = reader["Transfers"].set_index(["Site", "scenario-year"]).loc[NTC.index]
    FLH_transmission = reader["Full-load hours transmission"].set_index(["Site", "scenario-year"])
    
    FLH_transmission.loc[NTC.index] = transfers / NTC
    FLH_transmission.reset_index().to_excel(writer, sheet_name='Full-load hours transmission', index=False)

# Read in data for all scenarios
for folder in result_folders:
    version = folder.split("-")[0].split("_")[0]
    year = folder.split("-")[0].split("_")[1]
    suffix = folder.split("-")[0].split("_")[2]
    scen = suffix.upper()
    
    # Read output file
    writer_path = os.path.join("result", "TUM_" + scen + ".xlsx")
    book = load_workbook(writer_path)
    reader = pd.read_excel(writer_path, sheet_name=None)
    writer = pd.ExcelWriter(writer_path, engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    
    # Read in results
    urbs_path = os.path.join("result", folder, "scenario_base.h5")
    helpdf = urbs.load(urbs_path)
    df_result = helpdf._result
    df_data = helpdf._data
    
    # print(scen, year, ": Getting CO2 data")
    # get_emissions_data(reader, writer)
    
    # print(scen, year, ": Getting electricity prices")
    # get_electricity_data(reader, writer)
    
    # print(scen, year, ": Getting electricity generation data")
    # get_generation_data(reader, writer)
    
    # print(scen, year, ": Getting total, new and retired capacities data")
    # cap_pro = get_capacities_data(reader, writer)
    
    # print(scen, year, ": Getting storage data")
    # cap_sto = get_storage_data(reader, writer)
    
    # print(scen, year, ": Getting curtailment data")
    # get_curtailment_data(reader, writer)
    
    # print(scen, year, ": Getting transfer data")
    # get_transfer_data(reader, writer)
    
    # print(scen, year, ": Getting NTC data")
    # cap_tra = get_NTC_data(reader, writer)
    
    # print(scen, year, ": Getting NTC rents data")
    # get_NTC_rents_data(reader, writer)
    
    print(scen, year, ": Getting system cost data")
    get_cost_data(reader, writer)
    
    # Save results
    writer.save()
    
# for scen in ["EU", "NATION", "GREEN", "GAS"]:

    # # Read output file
    # writer_path = os.path.join("result", "TUM_" + scen + ".xlsx")
    # book = load_workbook(writer_path)
    # reader = pd.read_excel(writer_path, sheet_name=None)
    # writer = pd.ExcelWriter(writer_path, engine='openpyxl') 
    # writer.book = book
    # writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    # print(scen, ": Getting FLH data")
    # get_FLH_data(reader, writer)
    
    # # Save results
    # writer.save()
    
    
    
    # # Filter results
    # urbs_results[scen] = helpdf['e_pro_out'].unstack()
    
    # # Get storage data
    # urbs_sto_in[scen] = helpdf['e_sto_in']
    # urbs_sto_out[scen] = helpdf['e_sto_out']
    
    # # Get scenario costs
    # urbs_cost[scen] = helpdf['costs']
