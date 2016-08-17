import pyomo.environ
import urbs
from pyomo.core import Constraint
from pyomo.opt.base import SolverFactory

data = urbs.read_excel('mimo-example.xlsx')
prob = urbs.create_model(data, timesteps=range(1,8), dual=True)

optim = SolverFactory('glpk')
result = optim.solve(prob, tee=True)

res_vertex_duals = urbs.get_entity(prob, 'res_vertex')
marg_costs = res_vertex_duals.xs(('Elec', 'Demand'), level=('com', 'com_type'))
print(marg_costs)