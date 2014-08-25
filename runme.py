import coopr.environ
import os
import pandas as pd
import urbs
from coopr.opt.base import SolverFactory

# INIT
filename = 'data-example.xlsx'
(offset, length) = (4000, 5*24)  # timestep selection
timesteps = range(offset, offset+length+1)


# SCENARIOS
def scenario_base(data):
    # don't change data file
    pass


def scenario_stock_prices(data):
    # change stock commodity prices
    co = data['commodity']
    stock_commodities_only = (co.index.get_level_values('Type') == 'Stock')
    co.loc[stock_commodities_only, 'price'] *= 1.0


def scenario_co2_limit(data):
    # change CO2 limit
    co = data['commodity']
    co.loc[('Global', 'CO2', 'Env'), 'max'] *= 0.05


def scenario_north_process_caps(data):
    # change maximum installable capacity
    pro = data['process']
    pro.loc[('North', 'turb', 'Hydro', 'Elec'), 'cap-up'] *= 0.5
    pro.loc[('North', 'pp', 'Biomass', 'Elec'), 'cap-up'] *= 0.25


def scenario_all_together(data):
    # combine all other scenarios
    scenario_stock_prices(data)
    scenario_co2_limit(data)
    scenario_north_process_caps(data)


# select scenarios to be run
scenarios = [
    scenario_base,
    scenario_stock_prices,
    scenario_co2_limit,
    scenario_north_process_caps,
    scenario_all_together]


# MAIN

for scenario in scenarios:
    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = urbs.read_excel(filename)
    scenario(data)

    # create model, solve it, read results
    model = urbs.create_model(data, timesteps)
    prob = model.create()
    optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
    result = optim.solve(prob, tee=True)
    prob.load(result)

    # write report to spreadsheet
    urbs.report(
        prob,
        os.path.join('results', '{}.xlsx').format(sce),
        ['Elec'], ['South', 'Mid', 'North'])

    # add or change plot colours
    my_colors = {
        'South': (230, 200, 200),
        'Mid': (200, 230, 200),
        'North': (200, 200, 230)}
    for country, color in my_colors.iteritems():
        urbs.COLORS[country] = color

    # create timeseries plot for each demand (site, commodity) timeseries
    for sit, com in prob.demand.columns:
        fig = urbs.plot(prob, com, sit)
        ax0 = fig.get_axes()[0]
        new_title = ax0.get_title().replace('Energy balance of ',
                                            '{}: '.format(sce))
        ax0.set_title(new_title)
        for ext in ['png', 'pdf']:
            fig_filename = os.path.join(
                'results', '{}-{}-{}.{}').format(sce, com, sit, ext)
            fig.savefig(fig_filename, bbox_inches='tight')
