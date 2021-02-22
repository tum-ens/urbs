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
    maxit = s.admmopt.iterMaxlocal  # get maximum iteration
    s.flag = False
    s.gapAll = [10 ** 8] * s.na
    # while not s.pb['converge']:
    cost_history = np.zeros(maxit)
    # while nu <= itermax and not flag:

    while nu <= maxit and not s.flag:
        print('Subproblem %d is at iteration %d right now.' % (ID, nu))
        if s.recvmsg:
            s.update_z()  # update global flows
            s.choose_max_rho()  # update choose max rho (not needed?)

        s.fix_flow_global()
        s.fix_lambda()

        if nu > 0:
            s.set_quad_cost(rhos_old)

        start_time = time()
        s.result = s.solve_problem()
        end_time = time()

        # retrieve
        s.flows_all, s.flows_with_neighbor = s.retrieve_boundary_flows()

        cost_history[nu] = s.sub_persistent._solver_model.objval

        rhos_old = s.rho
        if s.recvmsg:  # not the initialization
            s.update_y()  # update lambda
            s.update_rho(nu)

        if nu % 1 == 0:
            print('Subproblem %d at iteration %d solved!. Local cost at %d is: %d. Residprim is: %d' % (ID, nu, ID, cost_history[nu - 1], s.primalgap[-1]))
        print("Time for solving subproblem %d: %ssecs to %ssecs" % (ID, start_time, end_time))

        # check convergence
        s.flag = s.converge()
        s.recvmsg = {}  # clear the received messages
        if s.flag:
            print("Worker %d converged!" % (ID,))
        s.send()
        if not s.flag:
            s.recv(pollrounds=5)

        #if nu % 50 == 0:
            #plt.plot(s.primalgap[1:nu])
            #plt.figure()
            ## flow_global_history.plot(legend=False)
            #plt.pause(0.001)
            #plt.show()
        nu += 1

    #close pipe connections
    #dest = s.pipes.keys()
    #for k in dest:
    #    s.pipes[k].close()

    # record results

    print("Local iteration of worker %d is %d" % (ID, nu))
    output_package = {'cost': cost_history[nu - 1], 'coupling_flows': s.flow_global,
                      'primal_residual': s.primalgap, 'dual_residual': s.dualgap}
    output.put((ID - 1, output_package))
