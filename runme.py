import numpy as np
import pandas as pd
import urbs
from coopr.opt.base import SolverFactory

# settings
filename = 'data-example.xlsx'
(offset, length) = (4000, 5*24)  # timestep selection
timesteps = np.arange(offset, offset+length+1)

# prepare input data
data = urbs.read_input(filename)

# modify data here to create scenarios

# EXAMPLE 1 - change stock commodity prices
co = data['commodity']
co.sortlevel(inplace=True)  # lexsort to make indexing work
stock_commodities_only = (co.index.get_level_values('Type') == 'Stock')
co.loc[stock_commodities_only, 'price'] *= 1.0
# EXAMPLE 2 - change CO2 limit
co.loc[('Global', 'CO2', 'Env'), 'max'] *= 0.05

# create model, solve it, read results
model = urbs.create_model(data, timesteps)
prob = model.create()
optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
result = optim.solve(prob, tee=True)
prob.load(result)

# write report to spreadsheet
urbs.report(prob, 'report.xlsx', ['Elec'], ['DE', 'MA', 'NO'])

# add or change plot colours
for country, colour in {
        'DE': (220, 200, 200), 
        'MA': (200, 220, 200),
        'NO': (200, 200, 220)}.iteritems():
   urbs.COLOURS[country] = colour 

# create timeseries plot for each demand (site, commodity) timeseries
for sit, com in prob.demand.columns:                          
    fig = urbs.plot(prob, com, sit)
    for ext in ['png', 'pdf']:
        fig.savefig('plot-{}-{}.{}'.format(com, sit, ext), bbox_inches='tight')

constants = urbs.get_constants(prob)
