import pandas as pd
import json

import os
import glob
from datetime import date
import time


def convert_to_json(input_files, year=date.today().year, json_filename='unnamed_simulation.json'):
    """
    Read the input files and arrange the information in a way that the URBS GUI can read it.
    Then, convert the dictionary to a json file.

    Args:
        - input_files: file path of the excel sheets or 'Input' (for the input folder within the urbs folder)
        - year: used, if there is no 'Support timeframe' within the 'Global' sheet
        - json_filename: name of the json file that is supposed to be created
    """

    # get the input files
    if input_files == 'Input':
        glob_input = os.path.join("..", input_files, '*.xlsx')
        input_files = sorted(glob.glob(glob_input))
#####################################################
# removed packaging of filepath into list 
# so that multiple filepaths can be selected in gui which are already stored in a list
    elif type(input_files).__name__ == 'string':
        input_files = [input_files]
#####################################################

    # read all the excel sheets and store them in a list
    sheet_list = []
    for sheet in input_files:
        sheet_list.append(pd.ExcelFile(sheet))

    # create the dict that stores all relevant information
    data_dict = {'_years': read_year_and_budget(sheet_list, year),
                 '_sites': read_site(sheet_list),
                 '_periods': {},
                 '_models': {},
                 '_transmissions': read_transmission(sheet_list, year),
                 '_trnsmCommodities': {},
                 '_gl': read_settings(sheet_list, json_filename),
                 '_scenarios': ["scenario_base"]
                 }

    # '_models' & '_trnsmCommodities' need the information from '_years' and '_sites' in data_dict
    data_dict['_models'] = read_models(sheet_list, data_dict)
    data_dict['_trnsmCommodities'] = read_transmission_commodities(sheet_list, data_dict)

    # make sure that json_filename is valid
    #####################################################
    if os.path.splitext(json_filename)[1] != '.json': 
    #####################################################
    #if json_filename[-5:] is not '.json':
        json_filename += '.json'

    # create json file
    json_file = json.dumps(data_dict, indent=2)
    f = open(json_filename, 'w')
    f.write(json_file)
    f.close()


def read_year_and_budget(input_list, year):
    """
    Read the year and the CO2 budget of the respective years.
    Save these information in a dictionary with the structure:
    "2019": {"selected": "", "CO2-limit": CO2 budget}

    Args:
        - input_list: list with the Excel spreadsheets
        - year: current year for non-intertemporal problems

    Returns:
        a dict with all the data regarding the year and CO2 budget
    """

    # lists for the years and the CO2 budget that will later be converted to years_dict
    years = []
    co2 = []
    years_dict = {}

    # read the 'Global' files in all the input sheets
    for xls in input_list:
        if 'Global' in xls.sheet_names:  # TODO how to handle errors?
            global_sheet = xls.parse('Global').set_index('Property')
            if 'Support timeframe' in global_sheet.value:
                support_timeframe = (int(global_sheet.loc['Support timeframe']['value']))
            else:
                support_timeframe = year
            years.append(support_timeframe)
            if 'CO2 limit' in global_sheet.value:
                limit = (global_sheet.loc['CO2 limit']['value'])
            else:
                limit = 'inf'
            co2.append(limit)
        else:
            print("No global sheet in the input sheet!")
    index = 0
    for items in years:
        # difference if CO2-budget is 'inf' or an integer
        """if isinstance(co2[index], str):
            years_dict[str(items)] = {"selected": "", "CO2 limit": co2[index]}
        else:
            years_dict[str(items)] = {"selected": "", "CO2 limit": co2[index].item()}"""
        # the String format has resulted in an error in combination withe .item() function; now, it somehow works
        years_dict[str(items)] = {"selected": "", "CO2 limit": co2[index].item()}
        index = index + 1

    return years_dict


def read_site(input_list):
    """
    Read all the sites and their respective areas.
    Information saved in a dict of the form:
    "Site name": {"selected" = "", "area" = size}

    Args:
        - input_list: list with the Excel spreadsheets

    Returns:
        a dict with the information regarding the sites
    """

    areas = []
    site_dict = {}

    # read the 'Site' sheets
    for xls in input_list:
        if 'Site' in xls.sheet_names:  # TODO error handling
            site_sheet = xls.parse('Site')
            site_sheet_indexed = site_sheet.set_index('Name')
            # throw out duplicated entries
            areas = list(set(areas).union(set(site_sheet['Name'].tolist())))
            for keys in areas:
                site_dict[str(keys)] = {"selected": "", "area": (site_sheet_indexed.loc[str(keys)]['area']).item()}
        else:
            print("No 'Site' sheet in the input sheet!")

    return site_dict


def read_settings(input_list, json_filename):
    """
    Read the settings of the simulation
    Store the information in a dict of the form seen in the first assignment of gl_dict

    Args:
        - input_list: list with the Excel spreadsheets
        - json_filename: name of the resulting json-file; used to name the result of the simulation

    Returns:
        - a dict with the information regarding the settings
    """
    # get the name of the result (= name of the json file without .json)
    result_name = json_filename[:-5]
    # dict with standard values (some of the values are not found in the sheets)
    gl_dict = {
        "Discount rate": {"value": 0.03},
        "CO2 budget": {"value": "inf"},
        "Cost budget": {"value": "inf"},
        "Weight": {"value": 1},
        "Solver": {"value": "glpk"},
        "Objective": {"value": "cost"},
        "TSOffset": {"value": 3500},
        "TSLen": {"value": 168},
        "DT": {"value": 1},
        "RsltName": {"value": result_name}
    }
    for xls in input_list:
        if 'Global' in xls.sheet_names:  # TODO how to handle errors?
            global_sheet = xls.parse('Global').set_index('Property')
            for keys in gl_dict:
                if str(keys) in global_sheet.value:
                    gl_dict[str(keys)] = {"value": global_sheet.loc[str(keys)]["value"].item()}
        else:
            print("No global sheet in the input sheet!")

    return gl_dict


def read_commodities(site, years_list, input_list):
    """
    Read all commodities, i.e. commodities, storage, processes and connections.

    Args:
        - site: Current site that is looked at
        - years_list: list containing all the years that are relevant for the model
        - input_list: list with the Excel spreadsheets

    Returns:
        - a list containing dicts for the commodities (including the storage), the processes and the connections
    """

    # dicts for the return values
    comm_dict = {}
    process_dict = {}
    connections_dict = {}

    # necessary variables: "types" because the types are sorted in groups (0,1,2),
    # number_of_comms: number of commodities that has been accounted for,
    # number_of_processes: number of processes that has been accounted for
    types = {"SupIm": 0, "Demand": 2, "Stock": 1, "Env": 2, "Buy": 0, "Sell": 2}
    number_of_comms = 1
    number_of_processes = 1

    # lists for storing commodities, processes & storage that already have been accounted for and just need
    # to get the new information that may come with new years (i.e. new Excel sheets)
    comms_in_site = []
    process_list = []
    storage_list = []
    sheet_number = 0
    # create a variable for the sheet of the commodities of the processes; necessary because it is used in different
    # for-loops (check if it's None)
    process_comms_sheet = None

    for xls in input_list:
        # get the current year
        if 'Global' in xls.sheet_names:
            try:
                current_year = str(int(xls.parse("Global").set_index("Property").loc["Support timeframe"]["value"]))
            except KeyError:
                current_year = years_list[sheet_number]
        else:
            current_year = years_list[sheet_number]
        sheet_number += 1

        # First, get all the information regarding the commodities

        if 'Commodity' in xls.sheet_names:
            comm_sheet = xls.parse("Commodity")

            if 'DSM' in xls.sheet_names:
                dsm_sheet = xls.parse("DSM")
                dsm_df = dsm_sheet.loc[dsm_sheet["Site"] == site].set_index("Commodity").drop(["Site"], axis=1)

                for keys in types:
                    # check for every type
                    comm_df = comm_sheet.loc[comm_sheet["Site"] == site][comm_sheet["Type"] == keys].set_index(
                        "Commodity").drop(["Site", "Type"], axis=1)  # TODO handle the warning

                    for items in comm_df.T:
                        # check every occurrence of the type; creates a new entry if it's not already been accounted for
                        if str(items) not in comms_in_site:
                            comms_in_site.append(str(items))
                            if number_of_comms < 10:
                                comm_id = str(types[keys]) + "-1_0" + str(number_of_comms) + "_" + str(keys)
                            else:
                                comm_id = str(types[keys]) + "-1_" + str(number_of_comms) + "_" + str(keys)
                            number_of_comms += 1
                            comm_dict[comm_id] = {
                                "Years": dict.fromkeys(years_list, {}),
                                "Id": comm_id,
                                "Name": str(items),
                                "Type": keys,
                                "Group": types[keys],
                                "Color": "rgb(255, 128, 0)",
                                "DSM": False  # TODO DSM
                            }
                        # add the information that may come with a new year (= excel sheet)
                        for comm_id in comm_dict:
                            # go through every existing commodity; if the current commodity is found: add the
                            # information, then break out of the for loop
                            if comm_dict[str(comm_id)]["Name"] == str(items):
                                new_comm = comm_dict[str(comm_id)]["Years"]
                                new_comm[current_year] = {
                                    "timeSer": "",
                                    "price": comm_df.T.loc["price"][items].item(),
                                    "max": comm_df.T.loc["max"][items].item(),
                                    "maxperhour": comm_df.T.loc["maxperhour"][items].item(),
                                    "Action": "...",
                                    "delay": 0.0,
                                    "eff": 0.0,
                                    "plot": False,
                                    "report": False,
                                    "recov": 0.0,
                                    "cap-max-do": 0.0,
                                    "cap-max-up": 0.0
                                }
                                df_time_ser = None
                                time_ser = ""
                                # for the time series, check the sheets that correspond to the commodity's type
                                if str(keys) == "SupIm":
                                    if "SupIm" in xls.sheet_names:  # TODO error handling
                                        sup_im_sheet = xls.parse("SupIm")
                                        if str(site) + "." + str(items) in sup_im_sheet:
                                            df_time_ser = sup_im_sheet.T.loc[str(site) + "." + str(items)]
                                    else:
                                        print("No SupIm sheet!")
                                        return

                                elif str(keys) == "Buy" or str(keys) == "Sell":
                                    if "Buy-Sell-Price" in xls.sheet_names:  # TODO error handling
                                        buy_sell_sheet = xls.parse("Buy-Sell-Price")
                                        if str(items) in buy_sell_sheet:
                                            df_time_ser = buy_sell_sheet.T.loc[str(items)]
                                    else:
                                        print("No 'Buy-Sell-Price' sheet!")
                                        return

                                elif str(keys) == "Demand":
                                    if "Demand" in xls.sheet_names:  # TODO error handling
                                        demand_sheet = xls.parse("Demand")
                                        if str(site) + "." + str(items) in demand_sheet:
                                            df_time_ser = demand_sheet.T.loc[str(site) + "." + str(items)]
                                    else:
                                        print("No Demand sheet!")
                                        return

                                # create the time series
                                if df_time_ser is not None:
                                    for row in df_time_ser:
                                        time_ser = time_ser + "|" + str(row)
                                new_comm[current_year]["timeSer"] = time_ser[1:]
                                for values in dsm_df.T:
                                    if str(values) == str(items):
                                        new_comm[current_year]["delay"] = dsm_df.loc[str(values)]["delay"]
                                        new_comm[current_year]["eff"] = dsm_df.loc[str(values)]["eff"]
                                        new_comm[current_year]["recov"] = dsm_df.loc[str(values)]["recov"]
                                        new_comm[current_year]["cap-max-do"] = dsm_df.loc[str(values)]["cap-max-do"]
                                        new_comm[current_year]["cap-max-up"] = dsm_df.loc[str(values)]["cap-max-up"]
                                        comm_dict[str(comm_id)]["DSM"] = True
                                break
            else:
                print("No 'DSM' sheet in the input sheet!")
        else:
            print("No 'Commodity' sheet in the input sheet!")

        # Secondly, check all the processes

        if 'Process' in xls.sheet_names:  # TODO how to handle errors?
            process_sheet = xls.parse("Process")
            process_df = process_sheet.loc[process_sheet["Site"] == site].set_index("Process").drop(["Site"], axis=1)
            # check every process in the sheet; if it's not already accounted for: create a new entry,
            # otherwise: find the matching process
            for processes in process_df.T:
                if str(processes) not in process_list:
                    process_list.append(str(processes))
                    current_process = "NewProcess#"+str(number_of_processes)
                    process_dict[current_process] = {
                        "IN": [],
                        "OUT": [],
                        "Years": {},
                        "Id": current_process,
                        "Name": str(processes),
                        "Type": "Process",
                        "PlotColor": ""
                    }
                    number_of_processes += 1
                else:
                    i = 1
                    while process_dict["NewProcess#" + str(i)]["Name"] != str(processes):
                        i += 1
                    current_process = "NewProcess#" + str(i)

                process_dict[current_process]["Years"][current_year] = {
                    "inst-cap": 0.0,
                    "Action": "...",
                    "timeEff": "",
                    "lifetime": 0.0,
                    "cap-lo": process_df.loc[processes]["cap-lo"].item(),
                    "cap-up": process_df.loc[processes]["cap-up"].item(),
                    "inv-cost": process_df.loc[processes]["inv-cost"].item(),
                    "fix-cost": process_df.loc[processes]["fix-cost"].item(),
                    "var-cost": process_df.loc[processes]["var-cost"].item(),
                    "startup-cost": 0.0,
                    "wacc": process_df.loc[processes]["wacc"].item(),
                    "max-grad": process_df.loc[processes]["max-grad"].item(),
                    "min-fraction": process_df.loc[processes]["min-fraction"].item(),
                    "depreciation": process_df.loc[processes]["depreciation"].item(),
                    "area-per-cap": 0.0
                }
                # 'inst-cap' is only provided in the first year of the analysis,
                # it stays the same for all the following years;
                # if the information is found in one sheet, the value should be assigned to every other year as well
                if "inst-cap" in process_df:  # TODO: what's the warning?
                    process_dict[current_process]["Years"][current_year]["inst-cap"] = process_df.loc[processes][
                        "inst-cap"].item()
                for registered_years in process_dict[current_process]["Years"]:
                    if process_dict[current_process]["Years"][registered_years]["inst-cap"] != 0:
                        process_dict[current_process]["Years"][current_year][
                            "inst-cap"] = process_dict[current_process]["Years"][registered_years]["inst-cap"]
                        break
                # same procedure for 'lifetime' as for 'inst-cap'
                if "lifetime" in process_df:
                    process_dict[current_process]["Years"][current_year]["lifetime"] = process_df.loc[processes][
                        "lifetime"].item()
                for registered_years in process_dict[current_process]["Years"]:
                    if process_dict[current_process]["Years"][registered_years]["lifetime"] != 0:
                        process_dict[current_process]["Years"][current_year][
                            "lifetime"] = process_dict[current_process]["Years"][registered_years]["lifetime"]
                        break
                # again, the same procedure for 'startup-cost'
                if "startup-cost" in process_df:
                    process_dict[current_process]["Years"][current_year]["startup-cost"] = process_df.loc[processes][
                        "startup-cost"].item()
                for registered_years in process_dict[current_process]["Years"]:
                    if process_dict[current_process]["Years"][registered_years]["startup-cost"] != 0:
                        process_dict[current_process]["Years"][current_year][
                            "startup-cost"] = process_dict[current_process]["Years"][registered_years]["startup-cost"]
                        break
                # again, the same procedure for 'area-per-cap'
                if "area-per-cap" in process_df:
                    process_dict[current_process]["Years"][current_year]["area-per-cap"] = process_df.loc[processes][
                        "area-per-cap"].item()
                for registered_years in process_dict[current_process]["Years"]:
                    if process_dict[current_process]["Years"][registered_years]["area-per-cap"] != 0:
                        process_dict[current_process]["Years"][current_year][
                            "area-per-cap"] = process_dict[current_process]["Years"][registered_years]["area-per-cap"]
                        break
                # create the time series for the efficiency
                eff = ""
                if "TimeVarEff" in xls.sheet_names:  # TODO error handling
                    time_var_eff_sheet = xls.parse("TimeVarEff").set_index("t")
                else:
                    time_var_eff_sheet = None
                    print("No 'TimeVarEff' sheet")

                if time_var_eff_sheet is not None:
                    if str(site) + "." + str(processes) in time_var_eff_sheet:
                        time_var_eff_df = time_var_eff_sheet.T.loc[str(site) + "." + str(processes)]
                        for rows in time_var_eff_df:
                            eff = eff + "|" + str(rows)
                        process_dict[current_process]["Years"][current_year]["timeEff"] = eff[1:]  # TODO what's the warning?

                # IN and OUT commodities of one process
                if 'Process-Commodity' in xls.sheet_names:  # TODO error handling
                    process_comms_sheet = xls.parse("Process-Commodity")
                    process_comms_df = process_comms_sheet.loc[process_comms_sheet["Process"] == processes] \
                        .set_index("Commodity")
                    for entries in comm_dict:
                        for process_comm in process_comms_df.T:
                            if comm_dict[str(entries)]["Name"] == str(process_comm):
                                if process_comms_df.loc[str(process_comm)]["Direction"] == "In" and \
                                        comm_dict[str(entries)]["Id"] not in process_dict[current_process]["IN"]:
                                    process_dict[current_process]["IN"].append(comm_dict[str(entries)]["Id"])
                                elif process_comms_df.loc[str(process_comm)]["Direction"] == "Out" and \
                                        comm_dict[str(entries)]["Id"] not in process_dict[current_process]["OUT"]:
                                    process_dict[current_process]["OUT"].append(comm_dict[str(entries)]["Id"])
                else:
                    print("No sheet for the process commodities found.")
        else:
            print("No process sheet in the input!")

        # Thirdly, check all the storage facilities and and them to the process dict

        if 'Storage' in xls.sheet_names:  # TODO how to handle errors?
            storage_sheet = xls.parse("Storage")
            storage_df = storage_sheet.loc[storage_sheet["Site"] == site].set_index("Storage")
            # create a new variable for the number of processes; new variable is necessary because the type storage
            # requires different information than the processes, but the storage is also part of the process_dict;
            # otherwise: go through every saved storage type, select the correct one that is being updated
            number_of_storages = number_of_processes
            for storage_types in storage_df.T:
                # go through every storage type; if it has not already been accounted for, create a new entry
                if str(storage_types) not in storage_list:
                    storage_list.append(str(storage_types))
                    current_storage = "NewStorage#" + str(number_of_storages)
                    number_of_storages += 1
                    process_dict[current_storage] = {
                        "IN": [],
                        "OUT": [],
                        "Years": {},
                        "Id": current_storage,
                        "Name": str(storage_types),
                        "Type": "Storage",
                        "PlotColor": ""
                    }
                else:
                    i = number_of_processes
                    while process_dict["NewStorage#" + str(i)]["Name"] != str(storage_types):
                        i += 1
                    current_storage = "NewStorage#" + str(i)
                # all the information provided by the input sheet for the current process and the current year
                process_dict[current_storage]["Years"][current_year] = {
                    "inst-cap-c": 0.0,
                    "cap-lo-c": storage_df.loc[storage_types]["cap-lo-c"].item(),
                    "cap-up-c": storage_df.loc[storage_types]["cap-up-c"].item(),
                    "inst-cap-p": 0.0,
                    "cap-lo-p": storage_df.loc[storage_types]["cap-lo-p"].item(),
                    "cap-up-p": storage_df.loc[storage_types]["cap-up-p"].item(),
                    "eff-in": storage_df.loc[storage_types]["eff-in"].item(),
                    "eff-out": storage_df.loc[storage_types]["eff-out"].item(),
                    "inv-cost-p": storage_df.loc[storage_types]["inv-cost-p"].item(),
                    "inv-cost-c": storage_df.loc[storage_types]["inv-cost-c"].item(),
                    "fix-cost-p": storage_df.loc[storage_types]["fix-cost-p"].item(),
                    "fix-cost-c": storage_df.loc[storage_types]["fix-cost-c"].item(),
                    "var-cost-p": storage_df.loc[storage_types]["var-cost-p"].item(),
                    "var-cost-c": storage_df.loc[storage_types]["var-cost-c"].item(),
                    "lifetime": 0.0,
                    "depreciation": storage_df.loc[storage_types]["depreciation"].item(),
                    "wacc": storage_df.loc[storage_types]["wacc"].item(),
                    "init": storage_df.loc[storage_types]["init"].item(),
                    "discharge": storage_df.loc[storage_types]["discharge"].item()
                    # "ep-ratio": ""  # TODO: it's in the excel sheets, not in the json files..
                }
                # 'inst-cap-c', 'inst-cap-p' and 'lifetime' only occur in the first observed year / the storage's first
                # appearance in the simulation; after that they remain unchanged for the rest of the years
                if "inst-cap-c" in storage_df:  # TODO: what's the warning?
                    process_dict[current_storage]["Years"][current_year]["inst-cap-c"] = storage_df.loc[storage_types][
                        "inst-cap-c"].item()
                for registered_years in process_dict[current_storage]["Years"]:
                    if process_dict[current_storage]["Years"][registered_years]["inst-cap-c"] != 0:
                        process_dict[current_storage]["Years"][current_year][
                            "inst-cap-c"] = process_dict[current_storage]["Years"][registered_years][
                            "inst-cap-c"]
                        break
                if "inst-cap-p" in storage_df:  # TODO: what's the warning?
                    process_dict[current_storage]["Years"][current_year]["inst-cap-p"] = storage_df.loc[storage_types][
                        "inst-cap-p"].item()
                for registered_years in process_dict[current_storage]["Years"]:
                    if process_dict[current_storage]["Years"][registered_years]["inst-cap-p"] != 0:
                        process_dict[current_storage]["Years"][current_year][
                            "inst-cap-p"] = process_dict[current_storage]["Years"][registered_years][
                            "inst-cap-p"].item()
                        break
                if "lifetime" in storage_df:
                    process_dict[current_storage]["Years"][current_year]["lifetime"] = storage_df.loc[storage_types][
                        "lifetime"].item()
                for registered_years in process_dict[current_storage]["Years"]:
                    if process_dict[current_storage]["Years"][registered_years]["lifetime"] != 0:
                        process_dict[current_storage]["Years"][current_year][
                            "lifetime"] = process_dict[current_storage]["Years"][registered_years]["lifetime"]
                        break
                # the commodities that go 'IN' the storage
                for entries in comm_dict:
                    if comm_dict[entries]["Name"] == storage_df.loc[storage_types]["Commodity"] and \
                            comm_dict[entries]["Id"] not in process_dict[current_storage]["IN"]:
                        process_dict[current_storage]["IN"].append(comm_dict[entries]["Id"])
                        break
        else:
            print("No 'Storage' sheet in the input!")

        # lastly, create a dict for the connections (of the processes; IN-OUT-relation)

        for process in process_dict:
            # establish the connections for every process
            if process_comms_sheet is not None:  # TODO how to handle errors?
                connections_df = process_comms_sheet.loc[process_comms_sheet["Process"] == process_dict[
                    process]["Name"]].set_index("Commodity")
            else:
                print("No process commodities specified!")
                break
            # create a new entry if the connection has not been accounted for, otherwise just update the information for
            # the years
            for inputs in connections_df.T:
                id_comm = ""
                for comms in comm_dict:
                    if comm_dict[comms]["Name"] == inputs:
                        id_comm = comm_dict[comms]["Id"]
                        break
                direction = str(connections_df.loc[inputs]["Direction"]).upper()
                current_connection = process + "$" + id_comm + "$" + direction
                if current_connection not in connections_dict:
                    connections_dict[current_connection] = {
                        "Dir": direction,
                        "Proc": process,
                        "Comm": id_comm,
                        "Years": {}
                    }
                connections_dict[current_connection]["Years"][current_year] = {
                    "ratio": connections_df.loc[inputs]["ratio"],
                    "ratio-min": connections_df.loc[inputs]["ratio-min"]
                }

    return [comm_dict, process_dict, connections_dict]


def read_models(input_list, data_dict):
    """
    prepares the already obtained data (sites, years) and calls the function 'read_commodities' to get all the necessary
    information to run the model(commodities, processes, connections)

    Args:
        - input_list: list with the Excel spreadsheets
        - data_dict: dictionary that contains the already obtained data for the sites and the years

    Returns:
        a dict with the information regarding the model
    """
    models_dict = {}
    years_list = []
    for year in data_dict["_years"]:
        years_list.append(year)

    for site in data_dict["_sites"]:
        [comms, processes, connections] = read_commodities(site, years_list, input_list)
        models_dict[str(site)] = {
            "_name": site,
            "_years": years_list,
            "_commodities": comms,
            "_processes": processes,
            "_connections": connections
        }

    return models_dict


def read_transmission(sheets_list, year):
    """
    Read the transmission between the sites.

    Args:
        - sheets_list: list with the Excel spreadsheets
        - year: used if the excel sheet does not provide a year (i.e. 'Support timeframe' in 'Global' does not exist)

    Returns:
        a dict with the information regarding the transmissions
    """
    trsm_dict = {}
    number_of_transmissions = 1
    new_transmission = False
    trsm_id = ""

    lifetime_cap_dict = {}

    trsms_in_model = []
    for xls in sheets_list:
        # get the current year
        if 'Global' in xls.sheet_names:
            try:
                current_year = str(int(xls.parse("Global").set_index("Property").loc["Support timeframe"]["value"]))
            except KeyError:
                current_year = year
        else:
            current_year = year
        if 'Transmission' in xls.sheet_names:
            trsm_sheet = xls.parse("Transmission")

            for row in trsm_sheet.itertuples(index=False, name="CurrentRow"):
                # go through every row of the sheet (= every transmission)
                # two rows necessary: the information 'lifetime' & 'inst-cap' are not included in every year
                # --> these information are only stored in the original data frame; for the other information,
                # the modified list is used
                modified_row = list(row)
                if "lifetime" in trsm_sheet:
                    del modified_row[5]
                if "inst-cap" in trsm_sheet:
                    del modified_row[9]
                # the current transmission is specified by: SiteIn, SiteOut, Type and the name of the commodity
                current_trsm_id = [row[0], row[1], row[2], row[3]]
                # if the transmission is new: create a new entry;
                if current_trsm_id not in trsms_in_model:
                    trsms_in_model.append(current_trsm_id)  # add transmission to the list
                    new_transmission = True
                    trsm_id = "NewTrsms#" + str(number_of_transmissions)  # create new transmission id
                    lifetime_cap_dict[trsm_id] = {"lifetime": 0, "inst-cap": 0}

                    """if modified_row[3] == "Elec":
                        modified_row[3] = "Electricity"
                        """
                    trsm_dict[trsm_id] = {
                        "SiteIn": modified_row[0],
                        "SiteOut": modified_row[1],
                        "CommName": modified_row[3],
                        "Years": {},
                        "Id": trsm_id,
                        "Name": "Power Line" + str(number_of_transmissions),
                        "Type": modified_row[2],
                        "IN": [str(modified_row[0] + "." + modified_row[3])],
                        "OUT": [str(modified_row[1] + "." + modified_row[3])]
                    }
                    number_of_transmissions += 1
                # if the transmission is new: create the Id; otherwise: find the Id
                if new_transmission:
                    new_transmission = False
                    trsm_id = "NewTrsms#" + str(number_of_transmissions - 1)
                else:
                    for transmissions in trsm_dict:
                        current_trsm = trsm_dict[transmissions]
                        if row[0] == current_trsm["SiteIn"] and row[1] == current_trsm["SiteOut"] and row[2] == \
                                current_trsm["Type"] and row[3] == current_trsm["CommName"]:
                            trsm_id = current_trsm["Id"]

                # add the information for 'lifetime' & 'inst-cap' (check for every year)
                if "lifetime" in trsm_sheet:
                    for registered_years in trsm_dict[trsm_id]["Years"]:
                        trsm_dict[trsm_id]["Years"][registered_years]["lifetime"] = row[5]
                    lifetime_cap_dict[trsm_id]["lifetime"] = row[5]
                if "inst-cap" in trsm_sheet:
                    for registered_years in trsm_dict[trsm_id]["Years"]:
                        trsm_dict[trsm_id]["Years"][registered_years]["inst-cap"] = row[9]
                    lifetime_cap_dict[trsm_id]["inst-cap"] = row[9]
                # add the information for the current year
                trsm_dict[trsm_id]["Years"][current_year] = {
                    "eff": modified_row[4],
                    "inv-cost": modified_row[5],
                    "fix-cost": modified_row[6],
                    "var-cost": modified_row[7],
                    "inst-cap": lifetime_cap_dict[trsm_id]["inst-cap"],
                    "lifetime": lifetime_cap_dict[trsm_id]["lifetime"],
                    "cap-lo": modified_row[8],
                    "cap-up": modified_row[9],
                    "wacc": modified_row[10],
                    "depreciation": modified_row[11]
                }
        else:
            print("No information provided for the transmissions.")

    return trsm_dict


def read_transmission_commodities(input_list, data_dict):
    """
    Reads all the commodities corresponding to the transmissions
    Args:
        - input_list: list with the Excel spreadsheets
        - data_dict: dictionary that contains the already obtained data for the sites and the years

    Returns:
        a dict with the information regarding the transmission commodities
    """
    trsm_comm_dict = {}
    trsm_comm_list = []
    years_list = []
    number_of_sheets = 0

    # create a list for all the years
    for years in data_dict["_years"]:
        years_list.append(str(years))

    for xls in input_list:
        # get the current year
        if 'Global' in xls.sheet_names:
            try:
                current_year = str(int(xls.parse("Global").set_index("Property").loc["Support timeframe"]["value"]))
            except KeyError:
                current_year = years_list[number_of_sheets]
        else:
            current_year = years_list[number_of_sheets]
        number_of_sheets += 1

        if 'Demand' in xls.sheet_names:
            demand_sheet = xls.parse("Demand").set_index("t")

            for key in demand_sheet:
                # check every commodity in every site for which information is provided
                [site, comm] = str(key).split(".")
                # create a new entry if the commodity has not been accounted for
                if str(key) not in trsm_comm_list:
                    trsm_comm_list.append(str(key))
                    trsm_comm_dict[str(key)] = {
                        "Years": dict.fromkeys(years_list, {}),
                        "Id": "",
                        "Name": str(comm),
                        "Type": "",
                        "Group": "",
                        "Color": "rgb(128, 128, 0)",  # TODO choose the right color
                        "DSM": False
                    }

                    for commodities in data_dict["_models"][str(site)]["_commodities"]:
                        # go through every registered commodity and check if information for its demand is provided
                        current_commodity = data_dict["_models"][str(site)]["_commodities"][str(commodities)]
                        if current_commodity["Name"] == str(comm):
                            trsm_comm_dict[str(key)]["Id"] = current_commodity["Id"]
                            trsm_comm_dict[str(key)]["Type"] = current_commodity["Type"]
                            trsm_comm_dict[str(key)]["Group"] = current_commodity["Group"]
                            trsm_comm_dict[str(key)]["Color"] = current_commodity["Color"]
                            trsm_comm_dict[str(key)]["DSM"] = current_commodity["DSM"]
                            break
                # update the information that may change every year
                for commodities in data_dict["_models"][str(site)]["_commodities"]:
                    current_commodity = data_dict["_models"][str(site)]["_commodities"][str(commodities)]
                    if current_commodity["Name"] == str(comm):
                        trsm_comm_dict[str(key)]["Years"][current_year] = {
                            "timeSer": "",
                            "price": current_commodity["Years"][current_year]["price"],
                            "max": current_commodity["Years"][current_year]["max"],
                            "maxperhour": current_commodity["Years"][current_year]["maxperhour"],
                            "Action": "...",
                            "delay": current_commodity["Years"][current_year]["delay"],
                            "eff": current_commodity["Years"][current_year]["eff"],
                            "plot": False,
                            "report": False,
                            "recov": current_commodity["Years"][current_year]["recov"],
                            "cap-max-do": current_commodity["Years"][current_year]["cap-max-do"],
                            "cap-max-up": current_commodity["Years"][current_year]["cap-max-up"]
                        }
                    # add the time series
                    df = demand_sheet.T.loc[str(key)]
                    time_ser = ""
                    for row in df:
                        time_ser = time_ser + "|" + str(row)
                    trsm_comm_dict[str(key)]["Years"][current_year]["timeSer"] = time_ser[1:]
        else:
            print("No 'Demand' sheet provided.")

    return trsm_comm_dict

if __name__ == "__main__":
    start_time = time.time()
    convert_to_json('Input', json_filename='test5')
    print("--- %s seconds ---" % (time.time() - start_time))
