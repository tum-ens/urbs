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
'v2.00_2015_eu-20200123T0827',
'v2.00_2020_eu-20200123T1216',
'v2.00_2025_eu-20200125T1840',
'v2.00_2020_gas-20200123T1556',
'v2.00_2020_nation-20200125T1337',
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
    
    prices = df_result["res_vertex"].xs(('Elec', 'Demand'), level=('com', 'com_type')).reorder_levels(['sit', 'stf', 't']).sort_index()
    prices = prices.reset_index().rename(columns={"sit": "Site", "stf": "scenario-year"})
    prices["season"] = [dict_season[x] for x in prices["t"]]
    demand = df_data["demand"].droplevel(1, axis=1).stack().reorder_levels([2, 0, 1])
    demand = demand.reset_index().rename(columns={"level_0": "Site", "support_timeframe": "scenario-year"})
    demand["season"] = [dict_season[x] for x in demand["t"]]
    prices_weighted = prices.set_index(["Site", "scenario-year", "t"])["res_vertex"]
    prices_weighted = demand.set_index(["Site", "scenario-year", "t"]).loc[prices_weighted.index][0] * prices_weighted
    prices_weighted = prices_weighted.reset_index()
    prices_weighted["season"] = [dict_season[x] for x in prices_weighted["t"]]
    
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
    
    # Repeat for groups of countries
    dem_regions = demand.drop(columns=["t"])
    dem_regions["Site"] = [dict_countries[x] for x in dem_regions["Site"]]
    dem_winter_regions = dem_regions.loc[dem_regions["season"]=="winter"].groupby(["Site", "scenario-year"]).sum()
    dem_summer_regions = dem_regions.loc[dem_regions["season"]=="summer"].groupby(["Site", "scenario-year"]).sum()
    dem_midseason_regions = dem_regions.loc[dem_regions["season"]=="midseason"].groupby(["Site", "scenario-year"]).sum()
    dem_regions = dem_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"])
    prices_weighted_regions = prices_weighted.copy()
    prices_weighted_regions["Site"] = [dict_countries[x] for x in prices_weighted_regions["Site"]]
    prices_weighted_regions = prices_weighted_regions.groupby(["Site", "scenario-year", "season", "t"]).sum(axis=0)
    prices_weighted_regions = prices_weighted_regions.droplevel(level=3).reset_index()
    
    # Averages
    import pdb; pdb.set_trace()
    prices_weighted_avg = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).sum()
    electricity.loc[prices_weighted_avg.index, "price-avg"] = prices_weighted_avg[0] / dem_regions[0]
    prices_weighted_winter = prices_weighted_regions.loc[prices_weighted_regions["season"]=="winter", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).sum()
    electricity.loc[prices_weighted_winter.index, "price-avg-winter"] = prices_weighted_winter[0] / dem_winter_regions[0]
    prices_weighted_summer = prices_weighted_regions.loc[prices_weighted_regions["season"]=="summer", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).sum()
    electricity.loc[prices_weighted_summer.index, "price-avg-summer"] = prices_weighted_summer[0] / dem_summer_regions[0]
    prices_weighted_midseason = prices_weighted_regions.loc[prices_weighted_regions["season"]=="midseason", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).sum()
    electricity.loc[prices_weighted_midseason.index, "price-avg-midseason"] = prices_weighted_midseason[0] / dem_midseason_regions[0]
    # Median
    prices_weighted_median = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).median()
    electricity.loc[prices_weighted_median.index, "price-median"] = prices_weighted_median[0] / dem_regions[0]
    # Max
    prices_weighted_max = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).max()
    electricity.loc[prices_weighted_max.index, "price-max"] = prices_weighted_max[0] / dem_regions[0]
    # Min
    prices_weighted_min = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).min()
    electricity.loc[prices_weighted_min.index, "price-min"] = prices_weighted_min[0] / dem_regions[0]
    # Demand
    electricity.loc[dem_regions.index, "elec-demand"] = dem_regions[0]
    
    # Save results
    electricity.reset_index().to_excel(writer, sheet_name='Electricity', index=False)
    

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
    
    print(scen, year, ": Getting CO2 data")
    get_emissions_data(reader, writer)
    
    print(scen, year, ": Getting electricity prices")
    get_electricity_data(reader, writer)
    
    print(scen, year, ": Getting electricity generation data")
    get_generation_data(reader, writer)
    
    
    
    
    # Save results
    # writer.to_excel(writer_path, sep=",", delimiter=";")
    writer.save()
    
    
    
    # # Filter results
    # urbs_results[scen] = helpdf['e_pro_out'].unstack()
    
    # # Get Elec data
    # urbs_elec[scen] = urbs_results[scen]['Elec'].reorder_levels(['sit', 'pro', 't']).sort_index()
    # urbs_elec_ts[scen] = urbs_elec[scen].unstack(level=0).unstack(level=0)
    # urbs_elec_ts_ger[scen] = urbs_elec[scen].unstack(level=1).unstack(level=1).sum(axis=0).unstack().T.sum(axis=0)
    
    # # Get CO2 data
    # urbs_co2[scen] = urbs_results[scen]['CO2'].reorder_levels(['sit', 'pro', 't']).sort_index()
    # urbs_co2_ts[scen] = urbs_co2[scen].unstack(level=0).unstack(level=0)
    # urbs_co2_ts_ger[scen] = urbs_co2[scen].unstack(level=1).unstack(level=1).sum(axis=0).unstack().T.sum(axis=0)
    
    # # Get Transmission data
    # urbs_tra[scen] = helpdf['cap_tra'].unstack()
    # urbs_tra_new[scen] = helpdf['cap_tra_new'].unstack()
    # urbs_tra_e_in[scen] = helpdf['e_tra_in']
    # urbs_tra_e_out[scen] = helpdf['e_tra_out']
    
    # # Get process capacities
    # urbs_cap[scen] = helpdf['cap_pro'].unstack()
    # urbs_cap_new[scen] = helpdf['cap_pro_new'].unstack()
    
    # # Get curtailment data
    # urbs_curt[scen] = helpdf['e_pro_in'].unstack(level=3)['Elec'].unstack(level=2)['Curtailment'].unstack(level=1)

    # # Get storage data
    # urbs_sto_in[scen] = helpdf['e_sto_in']
    # urbs_sto_out[scen] = helpdf['e_sto_out']
    
    # # Get scenario costs
    # urbs_cost[scen] = helpdf['costs']
