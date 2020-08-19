import pandas as pd

# SCENARIO GENERATORS
# In this script a variety of scenario generator functions are defined to
# facilitate scenario definitions.


def scenario_base(data):
    # do nothing
    return data


def scenario_stock_prices(data):
    # change stock commodity prices
    co = data['commodity']
    stock_commodities_only = (co.index.get_level_values('Type') == 'Stock')
    co.loc[stock_commodities_only, 'price'] *= 1.5
    return data


def scenario_co2_limit(data) :
    # change global CO2 limit
    global_prop = data['global_prop']
    for stf in global_prop.index.levels[0].tolist():
        global_prop.loc[(stf, 'CO2 limit'), 'value'] *= 0.2
    return data



def scenario_co2_tax_mid(data):

    # change CO2 price in Mid
    co = data['commodity']
    for stf in data['global_prop'].index.levels[0].tolist():
        co.loc[(stf, 'Mid', 'CO2', 'Env'), 'price'] = 50
    return data


def scenario_north_process_caps(data):
    # change maximum installable capacity
    pro = data['process']
    for stf in data['global_prop'].index.levels[0].tolist():
        pro.loc[(stf, 'North', 'Hydro plant'), 'cap-up'] *= 0.5
        pro.loc[(stf, 'North', 'Biomass plant'), 'cap-up'] *= 0.25
    return data


def scenario_no_dsm(data):
    # empty the DSM dataframe completely
    data['dsm'] = pd.DataFrame()
    return data


def scenario_all_together(data):
    # combine all other scenarios
    data = scenario_stock_prices(data)
    data = scenario_co2_limit(data)
    data = scenario_north_process_caps(data)
    return data

#nopt scenarios

def scenario_RF(data) :

    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    budget= ((305+177+124+104)*10)*1000000 #Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice
    demand.loc[idx[2020, :], ('Germany', 'Elec')]*=1
    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1
    #turn CCS off
    #pro = data['process']
    #for stf in data['global_prop'].index.levels[0].tolist():
     #   pro.loc[(stf, 'Germany', 'CCS PC'), 'cap-up']=0
     #   pro.loc[(stf, 'Germany', 'CCS Oxyfuel'), 'cap-up']=0
     #   pro.loc[(stf, 'Germany', 'CCS NGCC'), 'cap-up']=0
     #   pro.loc[(stf, 'Germany', 'CCS IGCC'), 'cap-up']=0

    return data

def scenario_TM80(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    #80  40% 55% 70% 80%
    budget = (((308/841)*(1-0.4)+(144/561)*(1-0.55)+(58/374)*(1-0.70) + (4/250)*(1-0.80)) * 10) *emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.17
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.27
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.35
    # turn CCS off
    #pro = data['process']
   # for stf in data['global_prop'].index.levels[0].tolist():
   #     pro.loc[(stf, 'Germany', 'CCS PC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS Oxyfuel'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS NGCC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS IGCC'), 'cap-up']=0
    return data

def scenario_TM95(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    #80  40% 55% 75% 95%
    budget = (((308/841)*(1-0.4)+(144/561)*(1-0.55)+(35/305)*(1-0.75) + (0/64)*(1-0.95)) * 10) *emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.19
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.32
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.38
    # turn CCS off
   # pro = data['process']
   # for stf in data['global_prop'].index.levels[0].tolist():
   #     pro.loc[(stf, 'Germany', 'CCS PC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS Oxyfuel'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS NGCC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS IGCC'), 'cap-up']=0
    return data

def scenario_EL80(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    #80  40% 55% 70% 80%
    budget = (((319/838)*(1-0.4)+(209/561)*(1-0.55)+(132/374)*(1-0.70)+ (76/250)*(1-0.80)) * 10 ) *emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.34
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.64
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.83
    # turn CCS off
   # pro = data['process']
   # for stf in data['global_prop'].index.levels[0].tolist():
   #     pro.loc[(stf, 'Germany', 'CCS PC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS Oxyfuel'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS NGCC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS IGCC'), 'cap-up']=0
    return data

def scenario_EL95(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    # 80  40% 55% 75% 95%
    budget = (((319/838)*(1-0.4)+(209/561)*(1-0.55) + (114 / 305) * (1 - 0.75) + (0 / 64) * (1 - 0.95)) * 10) * emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.34
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.63
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.82
    # turn CCS off
   # pro = data['process']
   # for stf in data['global_prop'].index.levels[0].tolist():
   #     pro.loc[(stf, 'Germany', 'CCS PC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS Oxyfuel'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS NGCC'), 'cap-up']=0
   #     pro.loc[(stf, 'Germany', 'CCS IGCC'), 'cap-up']=0
    return data


def scenario_RF_ccs(data) :

    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    budget= ((305+177+124+104)*10)*1000000 #Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice
    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1
    return data

def scenario_TM80_ccs(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    #80  40% 55% 70% 80%
    budget = (((308/841)*(1-0.4)+(144/561)*(1-0.55)+(58/374)*(1-0.70)+ (4/250)*(1-0.80)) * 10 ) *emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.17
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.27
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.35

    return data

def scenario_TM95_ccs(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    #80  40% 55% 75% 95%
    budget = (((308/841)*(1-0.4)+(144/561)*(1-0.55)+(35/305)*(1-0.75)+ (0/64)*(1-0.95)) * 10 ) *emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.19
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.32
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.38
    # turn CCS off

    return data

def scenario_EL80_ccs(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    #80  40% 55% 70% 80%
    budget = (((319/838)*(1-0.4)+(209/561)*(1-0.55)+(132/374)*(1-0.70)+ (76/250)*(1-0.80)) * 10 ) *emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.34
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.64
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.83
    # turn CCS off

    return data

def scenario_EL95_ccs(data) :
    emm1990_total = 1248000000  # Tonnes of CO2 equivalent
    # change global CO2 budget for reference scenario
    global_prop = data['global_prop']
    # 80  40% 55% 75% 95%
    budget = (((319/838)*(1-0.4)+(209/561)*(1-0.55) + (114 / 305) * (1 - 0.75)+ (0 / 64) * ( 1 - 0.95)) * 10 ) * emm1990_total  # Tonnes of CO2 eq
    global_prop.loc[(2020, 'CO2 budget'), 'value'] = budget
    # change demand for scenario
    demand = data['demand']
    idx = pd.IndexSlice

    demand.loc[idx[2030, :], ('Germany', 'Elec')] *= 1.34
    demand.loc[idx[2040, :], ('Germany', 'Elec')] *= 1.63
    demand.loc[idx[2050, :], ('Germany', 'Elec')] *= 1.82

    return data