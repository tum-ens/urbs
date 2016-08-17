import pyomo.environ
import urbs
from pyomo.core import Constraint
from pyomo.opt.base import SolverFactory

data = urbs.read_excel('mimo-example.xlsx')
prob = urbs.create_model(data, timesteps=range(1,8), dual=True)

optim = SolverFactory('glpk')
result = optim.solve(prob, tee=True)

# display all duals
print("Duals")
for c in prob.component_objects(Constraint, active=True):
    print("   Constraint "+str(c))
    cobject = getattr(prob, str(c))
    for index in cobject:
        try:
            dual_value = prob.dual[cobject[index]]
            print("      ", index, dual_value)
        except KeyError:
            print("      !KeyError ", index)