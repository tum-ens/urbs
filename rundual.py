    import coopr.environ
    import urbs
    from coopr.opt.base import SolverFactory
    
    data = urbs.read_excel('mimo-example.xlsx')
    model = urbs.create_model(data, timesteps=range(24), dual=True)
    prob = model.create()
    
    optim = SolverFactory('glpk')
    result = optim.solve(prob, tee=True)
    prob.load(result)
    
    # display all duals
    print "Duals"
    from coopr.pyomo import Constraint
    for c in prob.components(Constraint, active=True):
        print ("   Constraint "+str(c))
        cobject = getattr(prob, str(c))
        for index in cobject:
            print ("      ", index, prob.dual.getValue(cobject[index]))