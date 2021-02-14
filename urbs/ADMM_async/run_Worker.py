from time import time

from pyomo.environ import SolverFactory
import matplotlib.pyplot as plt
import numpy as np

def run_Worker(ID, s, output):

    s.sub_persistent = SolverFactory('gurobi_persistent')
    s.sub_persistent.set_instance(s.sub_pyomo, symbolic_solver_labels=False)
    s.sub_persistent.set_options("method=2")

    s.neighbor_clusters = s.boundarying_lines.neighbor_cluster.unique()

    # pack necessary structures into the problem object

    print("Worker %d initialized successfully!" % (ID,))
    nu = 0  # iteration count
    maxit = s.iterMaxlocal  # get maximum iteration
    flag = False
    # while not s.pb['converge']:
    cost_history = np.zeros(maxit)
    #while nu <= itermax and not flag:

    while nu <= maxit and not flag:
        print('Subproblem %d is at iteration %d right now.' % (ID, nu))
        if s.recvmsg:
            s.update_z() # update global flows
        #    s.choose_max_rho() # update choose max rho (not needed?)

        s.fix_flow_global()
        s.fix_lambda()

        rhos_old = s.rho
        s.set_quad_cost(rhos_old)
        start_time = time()
        s.result = s.solve_problem()
        end_time = time()
        #retrieve
        s.flows_all, s.flows_with_neighbor = s.retrieve_boundary_flows()

        if nu % 20 == 0:
            print('Subproblem %d at iteration %d solved!' % (ID, nu))
        print("Time for solving subproblem %d: %ssecs to %ssecs" % (ID, start_time, end_time))

        #s.update_x()
        if s.recvmsg:  # not the initialization
            s.update_y() # update lambda
            #s.update_rho()

        # check convergence
        #flag = s.converge() ADD THIS!!
        s.recvmsg = {}  # clear the received messages

        s.send()
        s.recv()
        cost_history[nu - 1] = s.sub_persistent._solver_model.objval
        if nu == 50 or nu == 100:
            plt.plot(cost_history[1:nu-1])
            plt.figure();
            #flow_global_history.plot(legend=False)
            plt.pause(0.001)
            plt.show()
        nu += 1

    # record results
    # print("Worker %d finished!" % (ID,))
    # print("Local iteration of worker %d is %d" % (ID, nu))
    # # calculate local generation cost
    # gencost = s.region['gencost']
    # pg = s.var['Pg']
    # objValue = dot(gencost[:, COST], pg ** 2) + dot(gencost[:, COST + 1], pg) + sum(gencost[:, COST + 2])
    #
    # varDual = {'ymd': s.var['ymd'], 'yad': s.var['yad'], 'yms': s.var['yms'],
    #            'yas': s.var['yas']}
    # varPrimal = {'Vm': s.var['Vm'], 'Va': s.var['Va'],
    #              'Pg': s.var['Pg'], 'Qg': s.var['Qg']}
    # Result = {'objValue': objValue, 'varPrimal': varPrimal, 'varDual': varDual, 'localiter': nu,
    #           'primalgap': s.pb['primalgap'], 'dualgap': s.pb['dualgap']}
    # output.put((ID - 1, Result))