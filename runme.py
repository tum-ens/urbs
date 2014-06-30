import numpy as np
import pandas as pd
import urbs
from coopr.opt.base import SolverFactory

filename = 'data-example.xlsx'
timesteps = np.arange(0, 24+1)

model = urbs.create_model(filename, timesteps)
prob = model.create()
optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
result = optim.solve(prob, tee=True)
prob.load(result)

# read results to DataFrames for quick analyses
(costs, cpro, ctra, csto, co2) = urbs.get_constants(prob)
(created, consumed, stored, 
 imported, exported) = urbs.get_timeseries(prob, 'Elec', 'DE')

# write concise report to spreadsheet
urbs.report(prob, 'report.xlsx', ['Elec'], ['DE', 'MA', 'NO'])

# create timeseries plot
urbs.plot(prob, 'Elec', 'DE')
