from .model import *
from .input import split_columns
from .data import timeseries_number

'''
These Scenarios don´t built up a whole new model. Instead they save time by
using an existing base model and by manipulating the dictionaries containing
the data and updating the affected constraints afterwards.
It is important to rebuilt the base scenario once the problem is solved.
This is done by handing reverse=True to the scenario function.

If you want to create your own scenarios either manipulate the functions below
or do the following steps:
1) Build an Excel file where the data is similar to the one the scenario
    funtion should produce
2) Create a model instance of this scenario using prob = urbs.create_model()
3) Write the model to an .lp file using prob.write(filename,
                                io_options={"symbolic_solver_labels":True})
4) Write a function with similar structure as the scenario functions below that
    changes the data in the dictionaries as you wish
5) Do step 2 (using the standard Excel input file, not the modified version),
    call your scenario function to manipulate the model, then do step 3.
    This creates an .lp file of your current scenario model.
6) Compare the .lp  file of your model to the .lp file you created before
    (Notepad++ Plugin 'Compare' is very useful)
7) Spot the constraints that need to be updated, delete these constraints and
    recreate them in your scenario function. Sometimes indices have to be
    deleted, too. Do this both for the reverse=False part and the reverse=True
    part
8) Repeat starting from step 5 until there are no more differences between the
    two .lp files
9) Do step 2 and 3 using the standard input file,
10) Do step 2 (using the standard Excel input file), call your scenario
    function to manipulate the model twice: One time with reverse=False and
    afterwards with reverse=True, then do step 3. This .lp file should match
    the .lp file of the base model. Compare them!
11) Congratulations! You created your own scenario function!
'''


def scenario_base(prob, reverse, not_used):
    # do nothing
    return prob


def scenario_stock_prices(prob, reverse, not_used):
    # change stock commodity prices
    if not reverse:
        for x in tuple(prob.commodity_dict["price"].keys()):
            if x[2] == "Stock":
                prob.commodity_dict["price"][x] *= 1.5
        update_cost(prob)
        return prob
    if reverse:
        for x in tuple(prob.commodity_dict["price"].keys()):
            if x[2] == "Stock":
                prob.commodity_dict["price"][x] *= 1/1.5
        update_cost(prob)
        return prob


def scenario_co2_limit(prob, reverse, not_used):
    # change global CO2 limit
    if not reverse:
        prob.global_prop_dict["value"]["CO2 limit"] *= 0.05
        update_co2_limit(prob)
        return prob
    if reverse:
        prob.global_prop_dict["value"]["CO2 limit"] *= 1/0.05
        update_co2_limit(prob)
        return prob


def scenario_co2_tax_mid(prob, reverse, not_used):
    # change CO2 price in Mid
    if not reverse:
        prob.commodity_dict["price"][('Mid', 'CO2', 'Env')] = 50
        update_cost(prob)
        return prob
    if reverse:
        prob.commodity_dict["price"][('Mid', 'CO2', 'Env')] = (
            prob._data["commodity"]["price"][('Mid', 'CO2', 'Env')])
        update_cost(prob)
        return prob


def scenario_north_process_caps(prob, reverse, not_used):
    # change maximum installable capacity
    if not reverse:
        prob.process_dict["cap-up"][('North', 'Hydro plant')] *= 0.5
        prob.process_dict["cap-up"][('North', 'Biomass plant')] *= 0.25
        update_process_capacity(prob)
        return prob
    if reverse:
        prob.process_dict["cap-up"][('North', 'Hydro plant')] *= 2
        prob.process_dict["cap-up"][('North', 'Biomass plant')] *= 4
        update_process_capacity(prob)
        return prob


def scenario_no_dsm(prob, reverse, not_used):
    if not reverse:
        del_dsm(prob)
        return prob
    if reverse:
        recreate_dsm(prob)
        return prob


def scenario_all_together(prob, reverse, not_used):
    # combine all other scenarios
    if not reverse:
        prob = scenario_stock_prices(prob, 0, not_used)
        prob = scenario_co2_limit(prob, 0, not_used)
        prob = scenario_north_process_caps(prob, 0, not_used)
        return prob
    if reverse:
        prob = scenario_stock_prices(prob, 1, not_used)
        prob = scenario_co2_limit(prob, 1, not_used)
        prob = scenario_north_process_caps(prob, 1, not_used)
        return prob


# Usage: In main the scenarios are function handles. In order to hand further
# information to the scenario function it is necessary to define an external
# data structure to store the additional information in. This function should
# be called like this:
# scenario_new_timeseries(timeseries_number, <value>)
# value specifies the path/file extension in order to locate the excel file.
# value will be appended to input\\scenario_new_timeseries_
def scenario_new_timeseries(timeseries_number, number):
    timeseries_number.insert(0, number)  # Is this an issue (memory not allocated)?
    return scenario_new_timeseries_


def scenario_new_timeseries_(prob, reverse,
                             filename="input\\scenario_new_timeseries.xlsx"):
    if not reverse:
        sheetnames = load_timeseries(prob, reverse, filename)
        if "Demand" in sheetnames:
            update_res_vertex(prob)
        if "SupIm" in sheetnames:
            update_supim(prob)
        if "Buy-Sell-Price" in sheetnames:
            update_cost(prob)
        if 'TimeVarEff' in sheetnames:
            update_TimeVarEff(prob)
    if reverse:
        sheetnames = load_timeseries(prob, reverse, filename)
        if "Demand" in sheetnames:
            update_res_vertex(prob)
        if "SupIm" in sheetnames:
            update_supim(prob)
        if "Buy-Sell-Price" in sheetnames:
            update_cost(prob)
        if 'TimeVarEff' in sheetnames:
            update_TimeVarEff(prob)
    return prob


# Constraint updating funtions:
def del_dsm(prob):
    # empty the DSM dataframe completely
    prob.dsm_dict = pd.DataFrame().to_dict()

    prob.del_component(prob.dsm_site_tuples)
    prob.del_component(prob.dsm_down_tuples)
    prob.dsm_site_tuples = pyomo.Set()
    prob.dsm_down_tuples = pyomo.Set()

    prob.del_component(prob.dsm_down)
    prob.del_component(prob.dsm_up)
    prob.dsm_down = pyomo.Var()
    prob.dsm_up = pyomo.Var()

    prob.del_component(prob.def_dsm_variables)
    prob.del_component(prob.res_dsm_upward)
    prob.del_component(prob.res_dsm_downward)
    prob.del_component(prob.res_dsm_maximum)
    prob.del_component(prob.res_dsm_recovery)

    prob.def_dsm_variables = pyomo.Constraint.Skip
    prob.res_dsm_upward = pyomo.Constraint.Skip
    prob.res_dsm_downward = pyomo.Constraint.Skip
    prob.res_dsm_maximum = pyomo.Constraint.Skip
    prob.res_dsm_recovery = pyomo.Constraint.Skip

    # The following lines cause 99% of work for the formation of this scenario
    update_res_vertex(prob)


def recreate_dsm(prob):
    # dsm_variables & vertex rule
    prob.dsm_dict = prob._data["dsm"].to_dict()
    try:
        myset = tuple(prob.dsm_dict["delay"].keys())
    except KeyError:
        raise NotImplementedError("Could not rebuild base modell!")

    prob.del_component(prob.dsm_site_tuples_domain)
    prob.del_component(prob.dsm_site_tuples)
    prob.dsm_site_tuples = pyomo.Set(
        within=prob.sit*prob.com,
        initialize=myset,
        doc='Combinations of possible dsm by site, e.g.(Mid, Elec)')

    prob.del_component(prob.dsm_down_tuples_domain)
    prob.del_component(prob.dsm_down_tuples_domain_index_0)
    prob.del_component(prob.dsm_down_tuples_domain_index_0_index_0)
    prob.del_component(prob.dsm_down_tuples)
    prob.dsm_down_tuples = pyomo.Set(
        within=prob.tm*prob.tm*prob.sit*prob.com,
        initialize=[(t, tt, site, commodity)
                    for (t, tt, site, commodity)
                    in dsm_down_time_tuples(prob.timesteps[1:],
                                            prob.dsm_site_tuples,
                                            prob)],
        doc='Combinations of possible dsm_down combinations, e.g. '
            '(5001,5003,Mid,Elec)')

    prob.del_component(prob.dsm_up_index)
    prob.del_component(prob.dsm_up)
    prob.dsm_up = pyomo.Var(
        prob.tm, prob.dsm_site_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM upshift')

    prob.del_component(prob.dsm_down)
    prob.dsm_down = pyomo.Var(
        prob.dsm_down_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM downshift')

    prob.del_component(prob.def_dsm_variables_index)
    prob.del_component(prob.def_dsm_variables)
    del prob.def_dsm_variables
    prob.def_dsm_variables = pyomo.Constraint(
        prob.tm, prob.dsm_site_tuples,
        rule=def_dsm_variables_rule,
        doc='DSMup * efficiency factor n == DSMdo (summed)')

    prob.del_component(prob.res_dsm_upward_index)
    prob.del_component(prob.res_dsm_upward)
    del prob.res_dsm_upward
    prob.res_dsm_upward = pyomo.Constraint(
        prob.tm, prob.dsm_site_tuples,
        rule=res_dsm_upward_rule,
        doc='DSMup <= Cup (threshold capacity of DSMup)')

    prob.del_component(prob.res_dsm_downward_index)
    prob.del_component(prob.res_dsm_downward)
    del prob.res_dsm_downward
    prob.res_dsm_downward = pyomo.Constraint(
        prob.tm, prob.dsm_site_tuples,
        rule=res_dsm_downward_rule,
        doc='DSMdo (summed) <= Cdo (threshold capacity of DSMdo)')

    prob.del_component(prob.res_dsm_maximum)
    prob.del_component(prob.res_dsm_maximum_index)
    del prob.res_dsm_maximum
    prob.res_dsm_maximum = pyomo.Constraint(
        prob.tm, prob.dsm_site_tuples,
        rule=res_dsm_maximum_rule,
        doc='DSMup + DSMdo (summed) <= max(Cup,Cdo)')

    prob.del_component(prob.res_dsm_recovery)
    prob.del_component(prob.res_dsm_recovery_index)
    del prob.res_dsm_recovery
    prob.res_dsm_recovery = pyomo.Constraint(
        prob.tm, prob.dsm_site_tuples,
        rule=res_dsm_recovery_rule,
        doc='DSMup(t, t + recovery time R) <= Cup * delay time L')

    # The following lines cause 50% of rebuilding work
    update_res_vertex(prob)


def change_dsm(prob):
    # not implemented yet
    return prob


def upd_dsm_constraints(prob):
    # not implemented yet
    return prob


def load_timeseries(prob, reverse, filename):
    with pd.ExcelFile(filename) as xls:
        try:
            sheetnames = xls.sheet_names
        except KeyError:
            print("Could not find file for new timeseries scenario")
        if not reverse:
            for temp in sheetnames:
                temp2 = xls.parse(temp).set_index(["t"])
                temp2.columns = split_columns(temp2.columns, '.')
                if str(temp) == "Demand":
                    prob.demand_dict = temp2.to_dict()
                if str(temp) == "SupIm":
                    prob.supim_dict = temp2.to_dict()
                if str(temp) == "Buy-Sell-Price":
                    prob.buy_sell_price_dict = temp2.to_dict()
                if str(temp) == "TimeVarEff":
                    prob.eff_factor_dict = temp2.to_dict()
        if reverse:
            for temp in sheetnames:
                if str(temp) == "demand":
                    prob.demand_dict = prob._data["demand"].to_dict()
                if str(temp) == "SupIm":
                    prob.supim_dict = prob._data["supim"].to_dict()
                if str(temp) == "Buy-Sell-Price":
                    prob.buy_sell_price_dict = (prob._data["buy_sell_price"]
                                                .to_dict())
                if str(temp) == "TimeVarEff":
                    prob.eff_factor_dict = prob._data["eff_factor"].to_dict()
        return sheetnames


def update_TimeVarEff(prob):
    prob.del_component(prob.pro_timevar_output_tuples)
    prob.del_component(prob.pro_timevar_output_tuples_domain)
    prob.del_component(prob.pro_timevar_output_tuples_domain_index_0)
    prob.pro_timevar_output_tuples = pyomo.Set(
        within=prob.sit*prob.pro*prob.com,
        initialize=[(site, process, commodity)
                    for (site, process) in tuple(prob.eff_factor_dict.keys())
                    for (pro, commodity) in tuple(prob.r_out_dict.keys())
                    if process == pro],
        doc='Outputs of processes with time dependent efficiency')

    prob.del_component(prob.def_process_output)
    prob.del_component(prob.def_process_output_index)
    prob.del_component(prob.def_process_output_index_1)
    prob.del_component(prob.def_process_output_index_1_index_0)
    prob.def_process_output = pyomo.Constraint(
        prob.tm, (prob.pro_output_tuples - prob.pro_partial_output_tuples -
                  prob.pro_timevar_output_tuples),
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

    prob.del_component(prob.def_process_timevar_output)
    prob.del_component(prob.def_process_timevar_output_index)
    prob.del_component(prob.def_process_timevar_output_index_1)
    prob.del_component(prob.def_process_timevar_output_index_1_index_1)
    prob.def_process_timevar_output = (
        pyomo.Constraint(prob.tm, (prob.pro_timevar_output_tuples -
                         (prob.pro_partial_output_tuples &
                          prob.pro_timevar_output_tuples)),
                         rule=def_pro_timevar_output_rule,
                         doc='e_pro_out = tau_pro * r_out * eff_factor'))

    prob.del_component(prob.def_process_partial_timevar_output)
    prob.del_component(prob.def_process_partial_timevar_output_index)
    prob.del_component(prob.def_process_partial_timevar_output_index_1)
    prob.def_process_partial_timevar_output = pyomo.Constraint(
        prob.tm,
        prob.pro_partial_output_tuples & prob.pro_timevar_output_tuples,
        rule=def_pro_partial_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')


def update_cost(prob):
    prob.del_component(prob.def_costs)
    prob.def_costs = pyomo.Constraint(
        prob.cost_type,
        rule=def_costs_rule,
        doc='main cost function by cost type')


def update_supim(prob):
    prob.del_component(prob.def_intermittent_supply)
    prob.del_component(prob.def_intermittent_supply_index)
    prob.def_intermittent_supply = pyomo.Constraint(
        prob.tm, prob.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')


def update_res_vertex(prob):
    prob.del_component(prob.res_vertex)
    prob.del_component(prob.res_vertex_index)
    prob.res_vertex = pyomo.Constraint(
        prob.tm, prob.com_tuples,
        rule=res_vertex_rule,
        doc='storage + transmission + process + source + buy - sell == demand')


def update_process_capacity(prob):
    prob.del_component(prob.def_process_capacity)
    prob.def_process_capacity = pyomo.Constraint(
        prob.pro_tuples,
        rule=def_process_capacity_rule,
        doc='total process capacity = inst-cap + new capacity')
    prob.del_component(prob.res_process_capacity)
    prob.res_process_capacity = pyomo.Constraint(
        prob.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')


def update_co2_limit(prob):
    prob.del_component(prob.res_global_co2_limit)
    prob.res_global_co2_limit = pyomo.Constraint(
        rule=res_global_co2_limit_rule,
        doc='total co2 commodity output <= Global CO2 limit')
