import numpy as np
import pandas as pd
import urbs
from coopr.opt.base import SolverFactory

# input data
filename = 'data-example.xlsx'

# settings
(offset, length) = (4000, 5*24)  # timestep selection
timesteps = np.arange(offset, offset+length+1)

#
model = urbs.create_model(filename, timesteps)
prob = model.create()
optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
result = optim.solve(prob, tee=True)
prob.load(result)

# read results (only for interactive use)
(costs, cpro, ctra, csto, co2) = urbs.get_constants(prob)
(created, consumed, stored, 
 imported, exported) = urbs.get_timeseries(prob, 'Elec', 'DE')

# write concise report to spreadsheet
urbs.report(prob, 'report.xlsx', ['Elec'], ['DE', 'MA', 'NO'])

# add or change plot colours
for country, colour in {
        'DE': (220, 200, 200), 
        'MA': (200, 220, 200),
        'NO': (200, 200, 220)}.iteritems():
   urbs.COLOURS[country] = colour 

# create timeseries plot
for sit in ['DE', 'MA', 'NO']:
    fig = urbs.plot(prob, 'Elec', sit)
    fig.savefig('plot-{}.png'.format(sit), bbox_inches='tight') 

