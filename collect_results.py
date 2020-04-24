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
    'v1.00_2016_base+PV-20200424T0610',
]

dict_tech = {"Bioenergy": "Bioenergy",
             "Hydro_2016": "Hydro",
             "Lignite": "Lignite",
             "Import": "Import",
             "Solar_2016": "Solar",
             "Slack": "Slack",
             "Shunt": "Curtailment",
             }
dict_countries = {
                  "Attapu": "Southern",
                  "Bokeo": "Northern",
                  "Bolikhamxai": "Central2",
                  "Champasak": "Southern",
                  "Houaphan": "Central1",
                  "Khammouan": "Central2",
                  "LouangNamtha": "Northern",
                  "Louangphrabang": "Northern",
                  "Oudomxai": "Northern",
                  "Phongsali": "Northern",
                  "Saravan": "Southern", 
                  "Savannakhet": "Central2",
                  "VientianeProvince": "Central1",
                  "VientianePrefecture": "Central1",
                  "Xaignabouri": "Northern",
                  "Xaisomboun": "Central1",
                  "Xiangkhoang": "Central1",
                  "Xekong": "Southern",
                  "China": "China",
                  "Thailand": "Thailand",
                  "Vietnam": "Vietnam",
                  "Cambodia": "Cambodia",
                  }

dict_season = {}
for t in range(0, 8761):
    if (t <= 2184) or (t>=7897):
        dict_season[t] = "winter"
    elif (t <= 6552) and (t>=3529):
        dict_season[t] = "summer"
    else:
        dict_season[t] = "midseason"
# for t in range(0, 673):
    # if (t <= 168):
        # dict_season[t] = "winter"
    # elif (t <= 504) and (t>=337):
        # dict_season[t] = "summer"
    # else:
        # dict_season[t] = "midseason"
        
def extend_to_year(df):
    # Get column names
    if isinstance(df, pd.DataFrame):
        col_names = df.columns
    elif isinstance(df, pd.Series):
        col_names = [df.name]
    
    # Get new multiindices (for all hours)
    total_list = []
    total_names = []
    for idx_name in df.index.names:
        if idx_name != "t":
            partial_list = list(set([x for x in df.index.get_level_values(level=idx_name)]))
            total_names = total_names + [idx_name]
            total_list = total_list + [partial_list]
    # Add t_new at the end
    total_list = total_list + [[x for x in range(0,8761)]]
    total_names = total_names + ["t_new"]
    
    index_new = pd.MultiIndex.from_product(total_list, names=total_names)
    
    # Prepare dataframe
    df_empty = pd.DataFrame(0, index=index_new, columns=["t"])
    df_empty = df_empty.reset_index().set_index("t_new")
    
    t = df_empty.index
    # df_empty.loc[(t <= 1416) | (t>=8017), "t"] = (df_empty.index[(t <= 1416) | (t>=8017)]-1)%96+1 # winter
    # df_empty.loc[0, "t"] = 0
    # df_empty.loc[(t <= 3624) & (t>=1417), "t"] = (df_empty.index[(t <= 3624) & (t>=1417)]-1)%96+97 # Spring
    # df_empty.loc[(t <= 5832) & (t>=3625), "t"] = (df_empty.index[(t <= 5832) & (t>=3625)]-1)%96+193 # Summer
    # df_empty.loc[(t <= 8016) & (t>=5833), "t"] = (df_empty.index[(t <= 8016) & (t>=5833)]-1)%96+289 # Autumn
    df_empty.loc[(t <= 1416) | (t>=8017), "t"] = (df_empty.index[(t <= 1416) | (t>=8017)]) # winter
    df_empty.loc[0, "t"] = 0
    df_empty.loc[(t <= 3624) & (t>=1417), "t"] = (df_empty.index[(t <= 3624) & (t>=1417)]) # Spring
    df_empty.loc[(t <= 5832) & (t>=3625), "t"] = (df_empty.index[(t <= 5832) & (t>=3625)])# Summer
    df_empty.loc[(t <= 8016) & (t>=5833), "t"] = (df_empty.index[(t <= 8016) & (t>=5833)]) # Autumn
    
    df_empty = df_empty.reset_index().set_index(df.index.names)
    df_new = df_empty.join(df).dropna(axis=0).reset_index().drop(columns="t").rename(columns={"t_new":"t"})
    df_new = df_new.set_index(df.index.names).sort_index()
    
    return df_new
    
    
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
    # df_empty.loc[(t <= 1416) | (t>=8017), "t"] = (df_empty.index[(t <= 1416) | (t>=8017)]-1)%168+1 # winter
    # df_empty.loc[0, "t"] = 0
    # df_empty.loc[(t <= 3624) & (t>=1417), "t"] = (df_empty.index[(t <= 3624) & (t>=1417)]-1)%168+169 # Spring
    # df_empty.loc[(t <= 5832) & (t>=3625), "t"] = (df_empty.index[(t <= 5832) & (t>=3625)]-1)%168+337 # Summer
    # df_empty.loc[(t <= 8016) & (t>=5833), "t"] = (df_empty.index[(t <= 8016) & (t>=5833)]-1)%168+505 # Autumn
    df_empty.loc[(t <= 1416) | (t>=8017), "t"] = (df_empty.index[(t <= 1416) | (t>=8017)]) # winter
    df_empty.loc[0, "t"] = 0
    df_empty.loc[(t <= 3624) & (t>=1417), "t"] = (df_empty.index[(t <= 3624) & (t>=1417)]) # Spring
    df_empty.loc[(t <= 5832) & (t>=3625), "t"] = (df_empty.index[(t <= 5832) & (t>=3625)])# Summer
    df_empty.loc[(t <= 8016) & (t>=5833), "t"] = (df_empty.index[(t <= 8016) & (t>=5833)]) # Autumn
    
    weights = df_empty["t"].value_counts().reset_index().rename(columns={"t": "weight"}).rename(columns={"index":"t"})
    weights = weights.set_index("t")
    df_new = df.reset_index().join(weights, on="t")
    for col in col_names:
        df_new[col] = df_new[col] * df_new["weight"]
    df_new = df_new.drop(columns="weight").set_index(df.index.names)
    
    return df_new

   
def get_emissions_data(reader, writer):
    emissions = reader["Emissions"].set_index(["Site", "scenario-year"])
    emissions_by_fuel = reader["Emissions by fuel"].set_index(["Site", "scenario-year"])
    
    co2 = df_result["e_pro_out"].unstack()['CO2'].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
    co2 = add_weight(co2)
    co2 = co2.unstack(level=3).sum(axis=1)
    co2 = co2.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"})
    co2["Technology"] = co2["pro"]
    for pro in co2["pro"].index:
        co2.loc[pro, "Technology"] = dict_tech[co2.loc[pro, "Technology"]]
    co2 = co2.drop(columns=["pro"])
    co2 = co2.groupby(["Site", "scenario-year", "Technology"]).sum()
    co2 = co2.unstack(level=2).droplevel(0, axis=1).fillna(0) / 10**6 # unit: Mt_CO2
    emissions.loc[co2.index, "CO2-emissions-elec"] = co2.sum(axis=1)
    
    try:
        #emissions_by_fuel.loc[co2.index, "CO2-emissions-coal"] = co2["Coal"] + co2["Coal-CCS"]
        #emissions_by_fuel.loc[co2.index, "CO2-emissions-gas"] = co2["Gas-CCGT"] + co2["Gas-OCGT"] + co2["Gas-ST"] + co2["Gas-CCS"]
        emissions_by_fuel.loc[co2.index, "CO2-emissions-lignite"] = co2["Lignite"]
        #emissions_by_fuel.loc[co2.index, "CO2-emissions-oil/other"] = co2["OilOther"]
    except KeyError:
        try: # No CCS
            emissions_by_fuel.loc[co2.index, "CO2-emissions-coal"] = co2["Coal"]
            emissions_by_fuel.loc[co2.index, "CO2-emissions-gas"] = co2["Gas-CCGT"] + co2["Gas-OCGT"] + co2["Gas-ST"]
            emissions_by_fuel.loc[co2.index, "CO2-emissions-lignite"] = co2["Lignite"]
            emissions_by_fuel.loc[co2.index, "CO2-emissions-oil/other"] = co2["OilOther"]
        except KeyError: # Aggregated technologies
            emissions_by_fuel.loc[co2.index, "CO2-emissions-gas"] = co2["Gas-CCGT"]
    
    try: # Bio_CCS negative
        co2_neg = df_result["e_pro_in"].unstack()['CO2'].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
        co2_neg = add_weight(co2_neg)
        co2_neg = co2_neg.unstack(level=3).sum(axis=1)
        co2_neg = co2_neg.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"})
        co2_neg["Technology"] = co2_neg["pro"]
        for pro in co2_neg["pro"].index:
            if len(co2_neg["pro"][pro]) > 5:
                co2_neg.loc[pro, "Technology"] = dict_tech[co2_neg.loc[pro, "Technology"][:-5]]
            else:
                co2_neg.loc[pro, "Technology"] = dict_tech[co2_neg.loc[pro, "Technology"]]
        co2_neg = co2_neg.drop(columns=["pro"])
        co2_neg = co2_neg.groupby(["Site", "scenario-year", "Technology"]).sum()
        co2_neg = co2_neg.unstack(level=2).droplevel(0, axis=1).fillna(0) / 10**6 # unit: Mt_CO2
        emissions.loc[co2_neg.index, "CO2-emissions-elec"] = emissions.loc[co2_neg.index, "CO2-emissions-elec"] - co2_neg.sum(axis=1)
    
        emissions_by_fuel.loc[co2_neg.index, "CO2-emissions-bioenergy"] = - co2_neg["Bio-CCS"]
    except KeyError:
        pass
    
    co2_regions = co2.reset_index()
    co2_regions["Site"] = [dict_countries[x] for x in co2_regions["Site"]]
    co2_regions = co2_regions.groupby(["Site", "scenario-year"]).sum(axis=0)
    emissions.loc[co2_regions.index, "CO2-emissions-elec"] = co2_regions.sum(axis=1)
    
    try:
        #emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-coal"] = co2_regions["Coal"] + co2_regions["Coal-CCS"]
        #emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-gas"] = co2_regions["Gas-CCGT"] + co2_regions["Gas-OCGT"] + co2_regions["Gas-ST"] + co2_regions["Gas-CCS"]
        emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-lignite"] = co2_regions["Lignite"]
        #emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-oil/other"] = co2_regions["OilOther"]
    except KeyError:
        try: # No CCS
            emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-coal"] = co2_regions["Coal"]
            emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-gas"] = co2_regions["Gas-CCGT"] + co2_regions["Gas-OCGT"] + co2_regions["Gas-ST"]
            emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-lignite"] = co2_regions["Lignite"]
            emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-oil/other"] = co2_regions["OilOther"]
        except KeyError: # Aggregated technologies
            emissions_by_fuel.loc[co2_regions.index, "CO2-emissions-gas"] = co2_regions["Gas-CCGT"]
        
    try: # Bio_CCS negative
        co2_neg_regions = co2_neg.reset_index()
        co2_neg_regions["Site"] = [dict_countries[x] for x in co2_neg_regions["Site"]]
        co2_neg_regions = co2_neg_regions.groupby(["Site", "scenario-year"]).sum(axis=0)
        emissions.loc[co2_neg_regions.index.difference(co2_neg.index), "CO2-emissions-elec"] = emissions.loc[co2_neg_regions.index.difference(co2_neg.index), "CO2-emissions-elec"] - co2_neg_regions.sum(axis=1)
    
        emissions_by_fuel.loc[co2_neg_regions.index, "CO2-emissions-bioenergy"] = - co2_neg_regions["Bio-CCS"]
    except:
        pass
    
    # # CCS_CO2
    # if year == "2016":
        # emissions.loc[co2.index, "CO2-captured"] = 0
        # emissions.loc[co2_regions.index, "CO2-captured"] = 0
    # else:
        # try:
            # ccs_co2 = df_result["e_pro_out"].unstack()['CCS_CO2'].fillna(0)
            # ccs_co2 = add_weight(ccs_co2)
            # ccs_co2 = ccs_co2.droplevel([0,3]).reorder_levels(['sit', 'stf']).sort_index()
            # ccs_co2 = ccs_co2.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"}).groupby(["Site", "scenario-year"]).sum() / 10**6 # unit: Mt_CO2
            # emissions.loc[ccs_co2.index, "CO2-captured"] = ccs_co2["CCS_CO2"]
            
            # ccs_co2_regions = ccs_co2.reset_index()
            # ccs_co2_regions["Site"] = [dict_countries[x] for x in ccs_co2_regions["Site"]]
            # ccs_co2_regions = ccs_co2_regions.groupby(["Site", "scenario-year"]).sum(axis=0)
            # emissions.loc[ccs_co2_regions.index, "CO2-captured"] = ccs_co2_regions["CCS_CO2"]
        # except KeyError:
            # pass
            
    # Save results
    emissions.round(2).reset_index().to_excel(writer, sheet_name='Emissions', index=False)
    emissions_by_fuel.round(2).reset_index().to_excel(writer, sheet_name='Emissions by fuel', index=False)
    
    
def get_electricity_data(reader, writer, year_built):
    electricity = reader["Electricity"].set_index(["Site", "scenario-year"])
    hourly_prices = reader["Hourly prices"].set_index(["Hours", "Year"])
    
    # Get helping factors
    stf_min = 2016
    if year_built > 2016:
        discount = 0 #df_data["global_prop"].droplevel(0).loc["Discount rate", "value"]
    else:
        discount = 0
    cost_factor = (1 + discount) ** (stf_min - year_built)
    
    prices = df_result["res_vertex"].xs(('Elec', 'Demand'), level=('com', 'com_type')).reorder_levels(['sit', 'stf', 't']).sort_index()
    prices = extend_to_year(prices)/df_result["weight"][0]
    prices = prices.reset_index().rename(columns={"sit": "Site", "stf": "scenario-year"})
    prices["season"] = [dict_season[x] for x in prices["t"]]
    demand = df_data["demand"].droplevel(1, axis=1).stack().reorder_levels([2, 0, 1])
    demand = demand.reset_index().rename(columns={"level_0": "Site", "support_timeframe": "scenario-year"}).set_index(["Site", "scenario-year", "t"])
    demand = extend_to_year(demand)
    demand = demand.reset_index()
    demand["season"] = [dict_season[x] for x in demand["t"]]
    
    # Averages
    prices_avg = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg.index, "price-avg"] = prices_avg["res_vertex"] * cost_factor
    prices_avg_winter = prices.loc[prices["season"]=="winter", ["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg_winter.index, "price-avg-winter"] = prices_avg_winter["res_vertex"] * cost_factor
    prices_avg_summer = prices.loc[prices["season"]=="summer", ["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg_summer.index, "price-avg-summer"] = prices_avg_summer["res_vertex"] * cost_factor
    prices_avg_midseason = prices.loc[prices["season"]=="midseason", ["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_avg_midseason.index, "price-avg-midseason"] = prices_avg_midseason["res_vertex"] * cost_factor
    # Median
    prices_median = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).median()
    electricity.loc[prices_median.index, "price-median"] = prices_median["res_vertex"] * cost_factor
    # Max
    prices_max = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).max()
    electricity.loc[prices_max.index, "price-max"] = prices_max["res_vertex"] * cost_factor
    # Min
    prices_min = prices[["Site", "scenario-year", "res_vertex"]].groupby(["Site", "scenario-year"]).min()
    electricity.loc[prices_min.index, "price-min"] = prices_min["res_vertex"] * cost_factor
    # Demand
    dem = demand[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).sum()
    electricity.loc[dem.index, "elec-demand"] = dem[0]
    # Hourly prices
    prices_h = prices.rename(columns={"scenario-year":"Year", "t":"Hours"}).drop(columns=["season"]).set_index(["Hours", "Year", "Site"]).unstack()["res_vertex"]
    hourly_prices.loc[prices_h.index, prices_h.columns] = prices_h * cost_factor
    
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
    electricity.loc[prices_weighted_avg.index, "price-avg"] = prices_weighted_avg[0] * cost_factor
    prices_weighted_winter = prices_weighted_regions.loc[prices_weighted_regions["season"]=="winter", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_weighted_winter.index, "price-avg-winter"] = prices_weighted_winter[0] * cost_factor
    prices_weighted_summer = prices_weighted_regions.loc[prices_weighted_regions["season"]=="summer", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_weighted_summer.index, "price-avg-summer"] = prices_weighted_summer[0] * cost_factor
    prices_weighted_midseason = prices_weighted_regions.loc[prices_weighted_regions["season"]=="midseason", ["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).mean()
    electricity.loc[prices_weighted_midseason.index, "price-avg-midseason"] = prices_weighted_midseason[0] * cost_factor
    # Median
    prices_weighted_median = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).median()
    electricity.loc[prices_weighted_median.index, "price-median"] = prices_weighted_median[0] * cost_factor
    # Max
    prices_weighted_max = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).max()
    electricity.loc[prices_weighted_max.index, "price-max"] = prices_weighted_max[0] * cost_factor
    # Min
    prices_weighted_min = prices_weighted_regions[["Site", "scenario-year", 0]].groupby(["Site", "scenario-year"]).min()
    electricity.loc[prices_weighted_min.index, "price-min"] = prices_weighted_min[0] * cost_factor
    # Demand
    dem_regions = dem_regions.unstack().sum(axis=1)
    electricity.loc[dem_regions.index, "elec-demand"] = dem_regions
    # Hourly prices
    prices_h_regions = prices_weighted_regions.rename(columns={"scenario-year":"Year", "t":"Hours"}).drop(columns=["season"]).set_index(["Hours", "Year", "Site"]).unstack()[0]
    hourly_prices.loc[prices_h_regions.index, prices_h_regions.columns] = prices_h_regions * cost_factor
    
    # Save results
    electricity.round(2).reset_index().to_excel(writer, sheet_name='Electricity', index=False)
    hourly_prices.round(2).reset_index().to_excel(writer, sheet_name='Hourly prices', index=False)
    

def get_generation_data(reader, writer):
    generation = reader["Electricity generation"].set_index(["Site", "scenario-year"])
    prod = df_result["e_pro_out"].unstack()['Elec'].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
    prod = add_weight(prod)
    prod = prod.fillna(0).unstack(level=3).sum(axis=1)
    prod = prod.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year"})
    prod["Technology"] = prod["pro"]
    for pro in prod["pro"].index:
        prod.loc[pro, "Technology"] = dict_tech[prod.loc[pro, "Technology"]]

    #prod = prod.drop(index= prod.loc[prod["Technology"]=="Slack"].index)
    prod = prod.drop(columns=["pro"]).groupby(["Site", "scenario-year", "Technology"]).sum().unstack()[0].fillna(0)
    generation.loc[prod.index, prod.columns] = prod
    generation.loc[prod.index] = generation.loc[prod.index].fillna(0)
    
    prod_regions = prod.reset_index()
    prod_regions["Site"] = [dict_countries[x] for x in prod_regions["Site"]]
    prod_regions = prod_regions.groupby(["Site", "scenario-year"]).sum(axis=0)
    generation.loc[prod_regions.index, prod_regions.columns] = prod_regions
    generation.loc[prod_regions.index] = generation.loc[prod_regions.index].fillna(0)
    
    generation.round(2).reset_index().to_excel(writer, sheet_name='Electricity generation', index=False)


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
    if year_now == 2016:
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
    
    capacities_total.round(2).reset_index().to_excel(writer, sheet_name='Installed capacities', index=False)
    capacities_new.round(2).reset_index().to_excel(writer, sheet_name='Added capacities', index=False)
    capacities_retired.round(2).reset_index().to_excel(writer, sheet_name='Capacities retired', index=False)


def get_storage_data(reader, writer):
    try:
        storage = reader["Storage"].set_index(["Site", "Storage type", "scenario-year"])
    
        # New capacities
        cap_p_new = df_result["cap_sto_p_new"].droplevel(3).reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage type", "cap_sto_p_new":"new-inst-cap-p"}).fillna(0)
        cap_p_new = cap_p_new.set_index(["Site", "Storage type", "scenario-year"])
        cap_c_new = df_result["cap_sto_c_new"].droplevel(3).reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage type", "cap_sto_c_new":"new-inst-cap-c"}).fillna(0)
        cap_c_new = cap_c_new.set_index(["Site", "Storage type", "scenario-year"])
    except KeyError:
        return
    
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
    storage_cap = storage_cap.groupby(["Site", "Storage type", "scenario-year"]).sum()
            
    # Retired capacity (continued)
    if year_now == 2016:
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
        storage_cap["retired-cap-p"] = (storage_cap["retired-cap-p"] + cap_p_past.T.squeeze()).dropna()
        storage_cap["retired-cap-c"] = (storage_cap["retired-cap-c"] + cap_c_past.T.squeeze()).dropna()
        storage_cap = storage_cap.fillna(0)
        
    storage_cap_regions = storage_cap.reset_index()
    storage_cap_regions["Site"] = [dict_countries[x] for x in storage_cap_regions["Site"]]
    storage_cap_regions = storage_cap_regions.groupby(["Site", "Storage type", "scenario-year"]).sum()
        
    storage_con = df_result["e_sto_con"].droplevel([4])
    storage_con = storage_con.reset_index().rename(columns={"stf":"scenario-year", "sit":"Site", "sto": "Storage type", "e_sto_con":"avg-state-of-charge"})
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
    
    # SOC in %
    storage_con["avg-state-of-charge"] = storage_con["avg-state-of-charge"]/storage_cap["inst-cap-c"]*100
    storage_con_regions["avg-state-of-charge"] = storage_con_regions["avg-state-of-charge"] / storage_cap_regions["inst-cap-c"] * 100
    
    # Get stored in energy
    storage_in = add_weight(df_result["e_sto_in"]).droplevel([0,4]).reset_index().rename(columns={"stf":"scenario-year", "sit":"Site", "e_sto_in":"stored-energy", "sto": "Storage type"})
    storage_in = storage_in.groupby(["Site", "Storage type", "scenario-year"]).sum()
    
    # Correct storage type
    storage_in = storage_in.reset_index()
    for idx in storage_in.index:
        if storage_in.loc[idx, "Storage type"].startswith("Storage_"):
            storage_in.loc[idx, "Storage type"] = storage_in.loc[idx, "Storage type"][:-5]
    storage_in = storage_in.set_index(["Site", "Storage type", "scenario-year"])
    
    storage_in_regions = storage_in.reset_index()
    storage_in_regions["Site"] = [dict_countries[x] for x in storage_in_regions["Site"]]
    storage_in_regions = storage_in_regions.groupby(["Site", "Storage type", "scenario-year"]).sum()
    
    # Save results
    storage.loc[storage_cap.index, storage_cap.columns] = storage_cap.fillna(0)
    storage.loc[storage_cap_regions.index, storage_cap_regions.columns] = storage_cap_regions.fillna(0)
    storage.loc[storage_con.index, storage_con.columns] = storage_con
    storage.loc[storage_con_regions.index, storage_con_regions.columns] = storage_con_regions
    storage.loc[storage_in.index, storage_in.columns] = storage_in
    storage.loc[storage_in_regions.index, storage_in_regions.columns] = storage_in_regions

    storage.round(2).reset_index().to_excel(writer, sheet_name='Storage', index=False)
    
    
def get_curtailment_data(reader, writer):
    curtailment = reader["Curtailment"]
    
    curtailed = df_result["e_pro_in"].unstack()["Elec"].dropna().droplevel(3).reorder_levels(['sit', 'stf', 't']).sort_index()
    curtailed = add_weight(curtailed)
    curtailed = curtailed.reset_index().rename(columns={"sit": "Site", "stf": "scenario-year"})
    year_now = curtailed["scenario-year"].unique()[0]
    curtailed = curtailed.set_index(["Site", "scenario-year", "t"])
    
    prod = df_result["e_pro_out"].unstack()['Elec'].unstack().reorder_levels(['sit', 'stf', 't']).sort_index().fillna(0)
    prod = add_weight(prod)
    # for pro in prod.columns:
        # prod = prod.drop(columns=pro)
    for pro in prod.columns:
        prod = prod.rename(columns={pro: dict_tech[pro]})
    try:
        prod = prod.stack().reset_index().rename(columns={"sit":"Site", "stf": "scenario-year", "level_3": "pro"}).groupby(["Site", "scenario-year", "t", "pro"]).sum()
        prod = prod.unstack().fillna(0)[0]
    except IndexError:
        return
    
    try:
        curtailed = curtailed.join(prod[["Solar", "Hydro", "Lignite", "Bioenergy"]])
    except KeyError:
        curtailed = curtailed.join(prod[["Hydro", "Lignite", "Bioenergy"]])
    curtailed = curtailed.loc[curtailed["Elec"]>0]
    
    # Order of curtailment: Solar, WindOn, WindOff, Hydro
    for idx in curtailed.index:
        for pp in ["Lignite", "Bioenergy", "Hydro", "Solar"]:
            try:
                curtailed.loc[idx, pp] = min(curtailed.loc[idx, "Elec"], curtailed.loc[idx, pp])
                curtailed.loc[idx, "Elec"] = curtailed.loc[idx, "Elec"] - curtailed.loc[idx, pp]
            except KeyError:
                pass
            
    curtailed = curtailed.drop(columns=["Elec"]).droplevel(2).reset_index().groupby(["Site", "scenario-year"]).sum()
    curtailed_regions = curtailed.reset_index()
    curtailed_regions["Site"] = [dict_countries[x] for x in curtailed_regions["Site"]]
    curtailed_regions = curtailed_regions.groupby(["Site", "scenario-year"]).sum()
    
    # Save results
    curtailment.loc[curtailment["scenario-year"]==year_now] = curtailment.loc[curtailment["scenario-year"]==year_now].fillna(0)
    curtailment = curtailment.set_index(["Site", "scenario-year"])
    curtailment.loc[curtailed.index, curtailed.columns] = curtailed
    curtailment.loc[curtailed_regions.index, curtailed_regions.columns] = curtailed_regions
    curtailment.round(2).reset_index().to_excel(writer, sheet_name='Curtailment', index=False)
    

def get_transfer_data(reader, writer):
    transfers = reader["Transfers"].set_index(["Site", "scenario-year"])
    
    try:
        tra_out = df_result["e_tra_out"]
    except KeyError:
        return
    tra_out = add_weight(tra_out)
    tra_out = tra_out.droplevel([0,4,5]).reset_index().rename(columns={"stf": "scenario-year", "sit": "Site", "sit_": "Site Out"})
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
    transfers.round(2).reset_index().to_excel(writer, sheet_name='Transfers', index=False)
    
    
def get_NTC_data(reader, writer):
    NTC = reader["NTC"].set_index(["Site", "scenario-year"])
    
    ntc_inst = df_data["transmission"]["inst-cap"].reset_index().rename(columns={"support_timeframe": "scenario-year", "Site In": "Site"})
    ntc_inst = ntc_inst.set_index(["Site", "scenario-year", "Transmission", "Commodity", "Site Out"])
    try:
        ntc_new = df_result["cap_tra_new"].reset_index().rename(columns={"stf": "scenario-year", "sit": "Site", "sit_": "Site Out", "tra": "Transmission", "com": "Commodity", "cap_tra_new": "inst-cap"})
        ntc_new = ntc_new.set_index(["Site", "scenario-year", "Transmission", "Commodity", "Site Out"])
        ntc_inst = ntc_inst + ntc_new
    except KeyError:
        return
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
    NTC.round(2).reset_index().to_excel(writer, sheet_name='NTC', index=False)
    
    
def get_NTC_rents_data(reader, writer):
    NTC_rents = reader["NTC rents"].set_index(["Site", "scenario-year"])
    hourly_prices = reader["Hourly prices"].rename(columns={"Hours":"t", "Year":"scenario-year"}).fillna(0)
    hourly_prices = hourly_prices.set_index(["t", "scenario-year"]).stack().reset_index()
    
    prices_site = hourly_prices.rename(columns={"level_2": "Site"}).set_index(["t", "scenario-year", "Site"])
    prices_siteout = hourly_prices.rename(columns={"level_2": "Site Out"}).set_index(["t", "scenario-year", "Site Out"])
    
    try:
        tra_out = df_result["e_tra_out"].droplevel([4,5]).reset_index().rename(columns={"stf": "scenario-year", "sit": "Site", "sit_": "Site Out"}).set_index(["Site", "Site Out", "scenario-year", "t"])
    except KeyError:
        return
    tra_out = tra_out.reset_index()
    # tra_out = add_weight(tra_out)
    # tra_out_regions = tra_out.reset_index()
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
    try:
        tra_out = tra_out.drop(index=idx_drop).groupby(["Site", "scenario-year", "Site Out"]).sum().unstack()["rent"]
    except:
        import pdb; pdb.set_trace()
    NTC_rents.loc[tra_out.index, tra_out.columns] = tra_out
    NTC_rents.round(2).reset_index().to_excel(writer, sheet_name='NTC rents', index=False)


def invcost_factor(dep_prd, interest, discount=None, year_built=None,
                   stf_min=None):
    """Investment cost factor formula.
    Evaluates the factor multiplied to the invest costs
    for depreciation duration and interest rate.
    Args:
        dep_prd: depreciation period (years)
        interest: interest rate (e.g. 0.06 means 6 %)
        year_built: year utility is built
        discount: discount rate for intertmeporal planning
    """
    # invcost factor for non intertemporal planning
    if (discount is None) or (discount == 0):
        return ((1 + interest) ** dep_prd * interest /
               ((1 + interest) ** dep_prd - 1))
    # invcost factor for intertemporal planning
    else:
        return ((1 + discount) ** (1 - (year_built-stf_min)) *
               (interest * (1 + interest) ** dep_prd *
               ((1 + discount) ** dep_prd - 1)) /
               (discount * (1 + discount) ** dep_prd *
               ((1+interest) ** dep_prd - 1)))
                    
                    
def get_cost_data(reader, writer, year_built):
    costs = reader["Total system costs"].set_index(["Site", "scenario-year"])
    abatement = reader["Abatement"].set_index(["scenario-year"])
    
    process = df_data["process"].drop(columns="support_timeframe").reset_index().rename(columns={"support_timeframe": "scenario-year"}).set_index(["Site", "scenario-year", "Process"])
    #storage = df_data["storage"].reset_index().rename(columns={"support_timeframe": "scenario-year"}).set_index(["Site", "scenario-year", "Storage", "Commodity"])
    transmission = df_data["transmission"].reset_index().rename(columns={"support_timeframe": "scenario-year"}).set_index(["Site In", "scenario-year", "Transmission", "Commodity", "Site Out"])
    
    # Get helping factors
    stf_min = 2016
    if year_built > 2016:
        discount = 0 #df_data["global_prop"].droplevel(0).loc["Discount rate", "value"]
    else:
        discount = 0
    cost_factor = (1 + discount) ** (stf_min - year_built)
    process["invcost-factor"] = invcost_factor(process["depreciation"], process["wacc"], 0, year_built, stf_min) * cost_factor
    #storage["invcost-factor"] = invcost_factor(storage["depreciation"], storage["wacc"], 0, year_built, stf_min) * cost_factor
    transmission["invcost-factor"] = invcost_factor(transmission["depreciation"], transmission["wacc"], 0, year_built, stf_min) * cost_factor
    
    #storage["invcost-factor"] = (storage["depreciation"] * ((1 + storage["wacc"]) ** storage["depreciation"] * storage["wacc"]) / ((1 + storage["wacc"]) ** storage["depreciation"] - 1))
    #transmission["invcost-factor"] = (transmission["depreciation"] * ((1 + transmission["wacc"]) ** transmission["depreciation"] * transmission["wacc"]) / ((1 + transmission["wacc"]) ** transmission["depreciation"] - 1))
    
    # Get newly installed capacities
    cap_pro_new = df_result["cap_pro_new"].reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "pro":"Process"}).set_index(["Site", "scenario-year", "Process"])
    process = process.join(cap_pro_new)
    
    # try:
        # cap_sto_p_new = df_result["cap_sto_p_new"].reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage", "com":"Commodity"}).fillna(0)
        # cap_sto_p_new = cap_sto_p_new.set_index(["Site", "scenario-year", "Storage", "Commodity"])
        # cap_sto_c_new = df_result["cap_sto_c_new"].reset_index().rename(columns={"stf": "scenario-year", "sit":"Site", "sto":"Storage", "com":"Commodity"}).fillna(0)
        # cap_sto_c_new = cap_sto_c_new.set_index(["Site", "scenario-year", "Storage", "Commodity"])
        # storage = storage.join([cap_sto_p_new, cap_sto_c_new])
    # except KeyError:
        # storage["cap_sto_p_new"] = 0
        # storage["cap_sto_c_new"] = 0
        
    try:
        cap_tra_new = df_result["cap_tra_new"].reset_index().rename(columns={"stf": "scenario-year", "sit": "Site In", "sit_": "Site Out", "tra": "Transmission", "com": "Commodity"})
        cap_tra_new = cap_tra_new.set_index(["Site In", "scenario-year", "Transmission", "Commodity", "Site Out"])
        transmission = transmission.join(cap_tra_new)
    except:
        transmission["cap_tra_new"] = 0
    
    # Correct total installed capacity
    process["inst-cap"] = process["inst-cap"] + process["cap_pro_new"]
    # storage["inst-cap-p"] = storage["inst-cap-p"] + storage["cap_sto_p_new"]
    # storage["inst-cap-c"] = storage["inst-cap-c"] + storage["cap_sto_c_new"]
    transmission["inst-cap"] = transmission["inst-cap"] + transmission["cap_tra_new"]
    
    # Get produced energy
    prod = df_result["e_pro_out"].unstack()['Elec'].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0)
    prod = add_weight(prod)
    prod = prod.unstack(level=3).sum(axis=1).reset_index().rename(columns={"sit":"Site", "stf": "scenario-year", "pro": "Process", 0: "prod"}).set_index(["Site", "scenario-year", "Process"])
    process = process.join(prod)
    
    # Get consumed fuels
    fuel = df_result["e_pro_in"]
    fuel = add_weight(fuel)
    fuel = fuel.droplevel(0).reset_index().rename(columns={"sit":"Site", "stf": "scenario-year", "pro": "Process", "com": "Commodity"})
    fuel = fuel.groupby(["Site", "scenario-year", "Process", "Commodity"]).sum().reset_index().set_index(["Site", "scenario-year", "Commodity"])
    fuel_price = df_data["commodity"]["price"].reset_index().rename(columns={"support_timeframe": "scenario-year"}).drop(columns="Type").set_index(["Site", "scenario-year", "Commodity"])
    fuel = fuel.join(fuel_price).reset_index().set_index(["Site", "scenario-year", "Process"]).fillna(0).drop(columns=["Commodity"])
    process = process.join(fuel)
    
    # Get emissions
    try:
        emissions = df_result["e_pro_out"].unstack()[['CO2', "CCS_CO2"]].reorder_levels(['sit', 'stf', 'pro', 't']).sort_index().fillna(0).stack().rename("emissions")
    except KeyError:
        emissions = df_result["e_pro_out"].unstack()[['CO2']].stack().reorder_levels(['sit', 'stf', 'pro', 'com', 't']).sort_index().fillna(0).rename("emissions")
    emissions = add_weight(emissions)
    emissions = emissions.reset_index().rename(columns={"sit":"Site", "stf": "scenario-year", "pro": "Process", "com": "Commodity", 0: "emissions"}).groupby(["Site", "scenario-year", "Process", "Commodity"]).sum()
    emissions = emissions.reset_index().set_index(["Site", "scenario-year", "Commodity"]).join(fuel_price.rename(columns={"price": "emissions_price"}))
    emissions["costs_env"] = emissions["emissions"] * emissions["emissions_price"]
    emissions = emissions.reset_index().drop(columns=["Commodity", "t", "emissions", "emissions_price"]).groupby(["Site", "scenario-year", "Process"]).sum()
    process = process.join(emissions)
    
    # Get storage flow
    # try:
        # storage_in = add_weight(df_result["e_sto_in"]).droplevel(0).reset_index().rename(columns={"stf":"scenario-year", "sit":"Site", "sto": "Storage", "com":"Commodity"})
        # storage_in = storage_in.groupby(["Site", "scenario-year", "Storage", "Commodity"]).sum()
        # storage_out = add_weight(df_result["e_sto_out"]).droplevel(0).reset_index().rename(columns={"stf":"scenario-year", "sit":"Site", "sto": "Storage", "com":"Commodity"})
        # storage_out = storage_out.groupby(["Site", "scenario-year", "Storage", "Commodity"]).sum()
        # storage = storage.join([storage_in, storage_out])
    # except KeyError:
        # storage["e_sto_in"] = 0
        # storage["e_sto_out"] = 0
    
    # Fill nan
    process = process.fillna(0)
    #storage = storage.fillna(0)
    transmission = transmission.fillna(0)
    
    # Find investment that have not completed their depreciation period
    process['active'] = 0
    #storage['active'] = 0
    if year_built > 2016:
        process['Construction year'] = 2016
        for ind in process.index:
            if "Shunt" not in ind:
                process.loc[ind, "Construction year"] = int(ind[2][-4:])
        process.loc[process['Construction year']<=2016, 'Construction year'] = 1900
        process['active'] = (process['Construction year'] + process['depreciation'] + 5) >= year_built
        process["active"] = [int(x) for x in process["active"]]
        
        # storage['Construction year'] = [int(x[-4:]) for x in storage.index.get_level_values(level='Storage')]
        # storage.loc[storage['Construction year']<=2016, 'Construction year'] = 1900
        # storage['active'] = (storage['Construction year'] + storage['depreciation'] + 5 - year_built) / 5
        # storage.loc[storage["active"] > 1, "active"] = 1
    
    # Investment costs
    process["costs_inv"] = process["cap_pro_new"] * process["inv-cost"] * process["invcost-factor"] # alt for intertemporal: 'overpay-factor'
    process["horizon"] = (2055 - year_built) / (process["depreciation"] + 5)
    process.loc[process["horizon"]>1, "horizon"] = 1
    process["costs_inv_abs"] = process["cap_pro_new"] * process["inv-cost"]
    process["costs_inv_abs_horizon"] = process["cap_pro_new"] * process["inv-cost"] * process["horizon"]
    process["capital_inv"] = process["inst-cap"] * process["inv-cost"] * process["active"]
    # try:
        # storage["costs_inv"] = (storage["cap_sto_p_new"] * storage["inv-cost-p"] + storage["cap_sto_c_new"] * storage["inv-cost-c"]) * storage["invcost-factor"] # alt for intertemporal: 'overpay-factor'
        # storage["horizon"] = (2055 - year_built) / (storage["depreciation"] + 5)
        # storage.loc[storage["horizon"]>1, "horizon"] = 1
        # storage["costs_inv_abs"] = (storage["cap_sto_p_new"] * storage["inv-cost-p"] + storage["cap_sto_c_new"] * storage["inv-cost-c"])
        # storage["costs_inv_abs_horizon"] = storage["costs_inv_abs"] * storage["horizon"]
        # storage["capital_inv"] = (storage["inst-cap-p"] * storage["inv-cost-p"] + storage["inst-cap-c"] * storage["inv-cost-c"]) * storage["active"]
    # except KeyError:
        # storage["costs_inv"] = 0
        
    transmission["costs_inv"] = transmission["cap_tra_new"] * transmission["inv-cost"] * transmission["invcost-factor"] # alt for intertemporal: 'overpay-factor'
    transmission["horizon"] = (2055 - year_built) / (transmission["depreciation"] + 5)
    transmission.loc[transmission["horizon"]>1, "horizon"] = 1
    transmission["costs_inv_abs"] = transmission["cap_tra_new"] * transmission["inv-cost"]
    transmission["costs_inv_abs_horizon"] = transmission["costs_inv_abs"] * transmission["horizon"]
    
    transmission_1 = transmission["costs_inv"].droplevel([2,3,4]).reset_index().rename(columns={"Site In": "Site"}).groupby(["Site", "scenario-year"]).sum()/2
    transmission_2 = transmission["costs_inv"].droplevel([0,2,3]).reset_index().rename(columns={"Site Out": "Site"}).groupby(["Site", "scenario-year"]).sum()/2
    costs_inv = process["costs_inv"].droplevel(2).reset_index().groupby(["Site", "scenario-year"]).sum()
    # try:
        # costs_inv.loc[storage.index.droplevel([2,3]), "costs_inv"] = costs_inv.loc[storage.index.droplevel([2,3]), "costs_inv"] + storage["costs_inv"].droplevel([2,3]).reset_index().groupby(["Site", "scenario-year"]).sum()["costs_inv"]
    # except KeyError:
        # pass
    try:
        costs_inv.loc[transmission_1.index, "costs_inv"] = costs_inv.loc[transmission_1.index, "costs_inv"] + transmission_1["costs_inv"]
        costs_inv.loc[transmission_2.index, "costs_inv"] = costs_inv.loc[transmission_2.index, "costs_inv"] + transmission_2["costs_inv"]
    except KeyError:
        pass
        
    costs_inv_abs = process["costs_inv_abs"].sum() + transmission["costs_inv_abs"].sum()# + storage["costs_inv_abs"].sum()
    costs_inv_abs_horizon = process["costs_inv_abs_horizon"].sum() + transmission["costs_inv_abs_horizon"].sum()# + storage["costs_inv_abs_horizon"].sum()
    abatement.loc[year_built, "inv-costs-abs"] = costs_inv_abs / 10**6
    abatement.loc[year_built, "inv-costs-abs-horizon"] = costs_inv_abs_horizon / 10**6
    abatement.loc[year_built, "inv-capital-pro"] = process["capital_inv"].sum() / 10**6
    if year_built > 2016:
        abatement.loc[year_built, "inv-capital-tra"] = abatement.loc[year_built-5, "inv-capital-tra"] + transmission["costs_inv"].sum() / 10**6
    else:
        abatement.loc[year_built, "inv-capital-tra"] = 0
    #abatement.loc[year_built, "inv-capital-sto"] = storage["capital_inv"].sum() / 10**6
    
    # Fix costs
    process["costs_fix"] = process["inst-cap"] * process["fix-cost"] * cost_factor
    #storage["costs_fix"] = (storage["inst-cap-p"] * storage["fix-cost-p"] + storage["inst-cap-c"] * storage["fix-cost-c"]) * cost_factor
    transmission["costs_fix"] = transmission["inst-cap"] * transmission["fix-cost"] * cost_factor
    transmission_1 = transmission["costs_fix"].droplevel([2,3,4]).reset_index().rename(columns={"Site In": "Site"}).groupby(["Site", "scenario-year"]).sum()/2
    transmission_2 = transmission["costs_fix"].droplevel([0,2,3]).reset_index().rename(columns={"Site Out": "Site"}).groupby(["Site", "scenario-year"]).sum()/2
    costs_fix = process["costs_fix"].droplevel(2).reset_index().groupby(["Site", "scenario-year"]).sum()
    # try:
        # costs_fix.loc[storage.index.droplevel([2,3]), "costs_fix"] = costs_fix.loc[storage.index.droplevel([2,3]), "costs_fix"] + storage["costs_fix"].droplevel([2,3]).reset_index().groupby(["Site", "scenario-year"]).sum()["costs_fix"]
    # except KeyError:
        # pass
    try:
        costs_fix.loc[transmission_1.index, "costs_fix"] = costs_fix.loc[transmission_1.index, "costs_fix"] + transmission_1["costs_fix"]
        costs_fix.loc[transmission_2.index, "costs_fix"] = costs_fix.loc[transmission_2.index, "costs_fix"] + transmission_2["costs_fix"]
    except KeyError:
        pass
    abatement.loc[year_built, "fix-costs"] = costs_fix["costs_fix"].sum() / 10**6

    # Variable costs
    process["costs_var"] = (process["prod"] * process["var-cost"] + process["e_pro_in"] * process["price"] + process["costs_env"])* cost_factor
    #storage["costs_var"] = (storage["e_sto_in"] + storage["e_sto_out"]) * storage["var-cost-p"] * cost_factor
    costs_var = process["costs_var"].droplevel(2).reset_index().groupby(["Site", "scenario-year"]).sum()
    # try:
        # costs_var.loc[storage.index.droplevel([2,3]), "costs_var"] = costs_var.loc[storage.index.droplevel([2,3]), "costs_var"] + storage["costs_var"].droplevel([2,3]).reset_index().groupby(["Site", "scenario-year"]).sum()["costs_var"]
    # except KeyError:
        # pass
    abatement.loc[year_built, "var-costs"] = costs_var["costs_var"].sum() / 10**6
    
    # Repeat for regions
    costs_inv_regions = costs_inv.reset_index()
    costs_inv_regions["Site"] = [dict_countries[x] for x in costs_inv_regions["Site"]]
    costs_inv_regions = costs_inv_regions.groupby(["Site", "scenario-year"]).sum()
    costs_fix_regions = costs_fix.reset_index()
    costs_fix_regions["Site"] = [dict_countries[x] for x in costs_fix_regions["Site"]]
    costs_fix_regions = costs_fix_regions.groupby(["Site", "scenario-year"]).sum()
    costs_var_regions = costs_var.reset_index()
    costs_var_regions["Site"] = [dict_countries[x] for x in costs_var_regions["Site"]]
    costs_var_regions = costs_var_regions.groupby(["Site", "scenario-year"]).sum()
    
    # Save results
    costs.loc[costs_inv.index, "System costs"] = (costs_fix["costs_fix"] + costs_inv["costs_inv"] + costs_var["costs_var"]) / 10**6
    costs.loc[costs_fix.index, "System fixed costs"] = costs_fix["costs_fix"] / 10**6
    costs.loc[costs_var.index, "System variable costs"] = costs_var["costs_var"] / 10**6
    costs.loc[costs_inv_regions.index, "System costs"] = (costs_fix_regions["costs_fix"] + costs_inv_regions["costs_inv"] + costs_var_regions["costs_var"]) / 10**6
    costs.loc[costs_fix_regions.index, "System fixed costs"] = costs_fix_regions["costs_fix"] / 10**6
    costs.loc[costs_var_regions.index, "System variable costs"] = costs_var_regions["costs_var"] / 10**6
    costs.round(2).reset_index().to_excel(writer, sheet_name='Total system costs', index=False)
    abatement.round(2).reset_index().to_excel(writer, sheet_name='Abatement', index=False)


def get_marginal_generation_data(reader, writer):
    # import pdb; pdb.set_trace()
    # marginal = reader["Marg. elec. generation process"].set_index(["Site", "scenario-year"])
    pass
    

def get_FLH_data(reader, writer):
    # Generation
    capacities_total = reader["Installed capacities"].set_index(["Site", "scenario-year"]).dropna(axis=0, how="all")
    generation = reader["Electricity generation"].set_index(["Site", "scenario-year"]).loc[capacities_total.index]
    FLH_generation = reader["Full-load hours generation"].set_index(["Site", "scenario-year"])
    
    FLH_generation.loc[capacities_total.index] = generation / capacities_total
    FLH_generation.round(2).reset_index().to_excel(writer, sheet_name='Full-load hours generation', index=False)
    
    # Transmission
    NTC = reader["NTC"].set_index(["Site", "scenario-year"]).dropna(axis=0, how="all")
    transfers = reader["Transfers"].set_index(["Site", "scenario-year"]).loc[NTC.index]
    FLH_transmission = reader["Full-load hours transmission"].set_index(["Site", "scenario-year"])
    
    FLH_transmission.loc[NTC.index] = transfers / NTC
    FLH_transmission.round(2).reset_index().to_excel(writer, sheet_name='Full-load hours transmission', index=False)
    
def get_abatement(reader, writer):
    # Emissions
    emissions = reader["Emissions by fuel"].set_index(["Site"])
    emissions = emissions.loc[dict_countries.keys()].reset_index()
    emissions = emissions.drop(columns=["Site"]).set_index(["scenario-year"]).sum(axis=1).reset_index().groupby("scenario-year").sum()
    
    # Electricity demand
    electricity = reader["Electricity"].set_index(["Site"])
    for ind in electricity.index:
        if ind not in dict_countries.keys():
            electricity.loc[ind, "elec-demand"] = 0
            
    electricity = electricity.reset_index()[["scenario-year", "elec-demand"]].groupby(["scenario-year"]).sum()

    # Fill Abatement sheet
    abatement = reader["Abatement"].set_index(["scenario-year"])
    abatement.loc[emissions.index, "CO2-emissions-elec"] = emissions[0]
    abatement["Total costs (no model horizon)"] = abatement["fix-costs"] + abatement["var-costs"] + abatement["inv-costs-abs"]
    abatement["Total costs (model horizon)"] = abatement["fix-costs"] + abatement["var-costs"] + abatement["inv-costs-abs-horizon"]
    abatement["Capital costs"] = abatement["fix-costs"] + abatement["var-costs"] + (abatement["inv-capital-pro"] + abatement["inv-capital-tra"] + abatement["inv-capital-sto"])*0.07
    abatement.loc[electricity.index, "elec-demand-TWh"] = electricity["elec-demand"] / 10**6
    #abatement.loc["total"] = abatement.loc[emissions.index].sum() * 5 - 4 * abatement.loc[2016]
    
    abatement.round(2).reset_index().to_excel(writer, sheet_name='Abatement', index=False)

# Read in data for all scenarios
for folder in result_folders:
    version = folder.split("-")[0].split("_")[0]
    year = folder.split("-")[0].split("_")[1]
    suffix = folder.split("-")[0].split("_")[2]
    scen = suffix#.upper()
    
    # Read output file
    writer_path = os.path.join("result", "Laos", "URBS_" + scen + ".xlsx")
    book = load_workbook(writer_path)
    reader = pd.read_excel(writer_path, sheet_name=None)
    writer = pd.ExcelWriter(writer_path, engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    
    # Read in results
    urbs_path = os.path.join("result", "Laos", folder, "scenario_base.h5")
    helpdf = urbs.load(urbs_path)
    df_result = helpdf._result
    df_data = helpdf._data
    
    print(scen, year, ": Getting CO2 data")
    get_emissions_data(reader, writer)
    
    print(scen, year, ": Getting marginal electricity generation data")
    get_marginal_generation_data(reader, writer)
    
    print(scen, year, ": Getting electricity prices")
    get_electricity_data(reader, writer, int(year))
    
    print(scen, year, ": Getting electricity generation data")
    get_generation_data(reader, writer)
    
    print(scen, year, ": Getting total, new and retired capacities data")
    get_capacities_data(reader, writer)
    
    # print(scen, year, ": Getting storage data")
    # get_storage_data(reader, writer)
    
    print(scen, year, ": Getting curtailment data")
    get_curtailment_data(reader, writer)
    
    print(scen, year, ": Getting transfer data")
    get_transfer_data(reader, writer)
    
    print(scen, year, ": Getting NTC data")
    get_NTC_data(reader, writer)
    
    print(scen, year, ": Getting system cost data")
    get_cost_data(reader, writer, int(year))
    
    # Save results
    writer.save()
    
for folder in result_folders:
    version = folder.split("-")[0].split("_")[0]
    year = folder.split("-")[0].split("_")[1]
    suffix = folder.split("-")[0].split("_")[2]
    scen = suffix#.upper()
    
    # Read output file
    writer_path = os.path.join("result", "Laos", "URBS_" + scen + ".xlsx")
    book = load_workbook(writer_path)
    reader = pd.read_excel(writer_path, sheet_name=None)
    writer = pd.ExcelWriter(writer_path, engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    
    # Read in results
    urbs_path = os.path.join("result", "Laos", folder, "scenario_base.h5")
    helpdf = urbs.load(urbs_path)
    df_result = helpdf._result
    df_data = helpdf._data
    
    print(scen, year, ": Getting NTC rents data")
    get_NTC_rents_data(reader, writer)
    
    # Save results
    writer.save()
    
for scen in ["base+PV"]:#, "base+CO2", "baseCO2", "base+NTC"]: #["v1", "v3", "v4", "v13", "v134", "v34"]: #

    # Read output file
    writer_path = os.path.join("result", "Laos", "URBS_" + scen + ".xlsx")
    book = load_workbook(writer_path)
    reader = pd.read_excel(writer_path, sheet_name=None)
    writer = pd.ExcelWriter(writer_path, engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    # print(scen, ": Getting FLH data")
    # get_FLH_data(reader, writer)
    
    print(scen, ": Getting abatement data")
    get_abatement(reader, writer)
    
    # Save results
    writer.save()