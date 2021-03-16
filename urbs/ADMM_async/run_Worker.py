from time import time
from ..saveload import *
from pyomo.environ import SolverFactory
import numpy as np
import os


def run_worker(ID, s, output):
    """

    Args:
        ID: the ordinality of the subproblem
        s: the urbsADMMmodel instance corresponding to the subproblem
        output: the Queue() object where the results are delivered to

    """
    s.sub_persistent = SolverFactory('gurobi_persistent')
    s.sub_persistent.set_instance(s.sub_pyomo, symbolic_solver_labels=False)
    s.sub_persistent.set_gurobi_param('Method', 2)
    s.sub_persistent.set_gurobi_param('Threads', 1)
    s.neighbor_clusters = s.boundarying_lines.neighbor_cluster.unique()

    print("Worker %d initialized successfully!" % (ID,))
    nu = 0  # iteration count
    maxit = s.admmopt.iterMaxlocal  # get maximum iteration
    s.flag = False
    s.gapAll = [10 ** 8] * s.na
    cost_history = np.zeros(maxit)
    s.convergetol = s.admmopt.conv_rel * (len(s.flow_global)+1) #  # convergence criteria for maximum primal gap

    while nu <= maxit-1 and not s.flag:
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
            print('Subproblem %d at iteration %d solved!. Local cost at %d is: %d. Residprim is: %d'
                  % (ID, nu, ID, cost_history[nu - 1], s.primalgap[-1]))
        print("Time for solving subproblem %d: %ssecs to %ssecs" % (ID, start_time, end_time))

        # check convergence
        s.flag = s.converge()
        s.recvmsg = {}  # clear the received messages
        if s.flag:
            print("Worker %d converged!" % (ID,))

        s.send()
        s.recv(pollrounds=5)
        nu += 1

    print("Local iteration of worker %d is %d" % (ID, nu))
    # save(s.sub_pyomo, os.path.join(s.result_dir, '_{}_'.format(ID),'{}.h5'.format(s.sce)))
    output_package = {'cost': cost_history[nu - 1], 'coupling_flows': s.flow_global,
                      'primal_residual': s.primalgap, 'dual_residual': s.dualgap}
    output.put((ID - 1, output_package))
