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

# modify here to create scenarios, e.g.
data['commodity']['price'] *= 2

# create model, solve it, read results
model = urbs.create_model(data, timesteps)
prob = model.create()
optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
result = optim.solve(prob, tee=True)
prob.load(result)

# read results (only for interactive use)
(costs, cpro, ctra, csto, co2) = urbs.get_constants(prob)
(created, consumed, stored, 
 imported, exported) = urbs.get_timeseries(prob, 'Elec', 'DE')

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
    fig.savefig('plot-{}-{}.png'.format(com, sit), bbox_inches='tight') 

