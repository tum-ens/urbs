import numpy as np
import pandas as pd
import urbs
from coopr.opt.base import SolverFactory

filename = 'data-example.xlsx'
timesteps = np.arange(0, 24+1)

model = urbs.create_model(filename, timesteps)
prob = model.create()
optim = SolverFactory('gurobi')  # 'cplex', 'gurobi', ...
result = optim.solve(prob, tee=True)
prob.load(result)

urbs.report(prob, 'report.xlsx', ['Elec'], ['DE', 'MA', 'NO'])
# urbs.get_constants
# urbs.get_timeseries
# urbs.plot
# urbs.report
