.. _guide_for_admm:

ADMM user guide
===============

This section serves as a guide for those who would like to use the regional decomposition module by ADMM.

Setting the modelled time steps
-------------------------------

As with the usual urbs, the modelled time steps has to be set on ``runme_admm.py`` in the corresponding :ref:`line <time-step-section>`

Clustering scheme for the regional decomposition
------------------------------------------------

Regional decomposition only makes sense if the energy system model contains multiple sites. These sites then need to be assigned to different subproblems in "clusters", whose scheme has to be input on ``runme_admm.py`` within the variable ``clusters`` in the corresponding :ref:`line <cluster-section>`:


::

    clusters = [[('site 1 of cluster 1'),('site 2 of cluster 1'),('site 3 of cluster 1'')],
                [('site 1 of cluster 2'),('site 2 of cluster 2')]]

Any number of clusters is possible, from two to the total number of sites (each site forming its own cluster). For the trivial case of having only a single cluster, the regional decomposition is obviously not necessary.

The input of ADMM parameters
----------------------------

**The initialized values of global ** can be set in the following :ref:`line <init-vals-section>` on the ``runfunctions_admm.py`` script:

::

    for j in timesteps[1:]:
        coup_vars.lambdas[cluster_idx, j, year, sit_from, sit_to] = 0
        coup_vars.rhos[cluster_idx, j, year, sit_from, sit_to] = 5
        coup_vars.flow_global[cluster_idx, j, year, sit_from, sit_to] = 0

as well as :ref:`here <init-vals-section2>` again for the quadratic penalty parameter:

::

       problem.rho = 5

ADMM settings (``admmoption``)
------------------------------

Lastly, the ADMM settings, which are input as attributes of the class ``admmoption`` of ``urbsADMMmodel`` can be fine tuned depending on the problem type. These settings can be found in the :ref:`corresponding section <admmoption>` of ``ADMM_async/urbs_admm_model.py``:

::

    # ##--------ADMM parameters specification -------------------------------------
    class admmoption(object):
        """ This class defines all the parameters to use in admm """

        def __init__(self):
            self.rho_max = 10  # upper bound for penalty rho
            self.tau_max = 1.5  # parameter for residual balancing of rho
            self.tau = 1.05  # multiplier for increasing rho
            self.zeta = 1  # parameter for residual balancing of rho
            self.theta = 0.99  # multiplier for determining whether to update rho
            self.mu = 10  # multiplier for determining whether to update rho
            self.pollWaitingtime = 0.001  # waiting time of receiving from one pipe
            self.nwaitPercent = 0.2  # waiting percentage of neighbors (0, 1]
            self.iterMaxlocal = 20  # local maximum iteration
            #self.convergetol = 365 * 10 ** 1#  convergence criteria for maximum primal gap
            self.rho_update_nu = 50 # rho is updated only for the first 50 iterations
            self.conv_rel = 0.1 # the relative convergece tolerance, to be multiplied with len(s.flow_global)



Commenting out the original problem solution
--------------------------------------------

The ``runfunctions_admm.py`` includes the routines for building and solution of the original, undecomposed model for testing purposes. When the problem is solved in a decomposed way, the original problem doesn't need to be solved. Therefore, the :ref:`following code section <orig-solve-section>` has to be commented out in actual operation:

::

    # (optional) create the central problem to compare results
    prob = create_model(data_all, timesteps, dt, type='normal')

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # setup solver
    solver_name = 'gurobi'
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)

    # original problem solution (not necessary for ADMM, to compare results)
    orig_time_before_solve = time.time()
    results_prob = optim.solve(prob, tee=False)
    orig_time_after_solve = time.time()
    orig_duration = orig_time_after_solve - orig_time_before_solve
    flows_from_original_problem = dict((name, entity.value) for (name, entity) in prob.e_tra_in.items())
    flows_from_original_problem = pd.DataFrame.from_dict(flows_from_original_problem, orient='index',
                                                         columns=['Original'])

as well as the :ref:`test procedure <test-section>` at the end of ``runfunctions_admm.py``::

    # ------------get results ---------------------------
    ttime = time.time()
    tclock = time.clock()
    totaltime = ttime - start_time
    clocktime = tclock - start_clock

    results = sorted(results, key=lambda x: x[0])

    obj_total = 0
    obj_cent = results_prob['Problem'][0]['Lower bound']

    for cluster_idx in range(0, len(clusters)):
        if cluster_idx != results[cluster_idx][0]:
            print('Error: Result of worker %d not returned!' % (cluster_idx + 1,))
            break
        obj_total += results[cluster_idx][1]['cost']

    gap = (obj_total - obj_cent) / obj_cent * 100
    print('The convergence time for original problem is %f' % (orig_duration,))
    print('The convergence time for ADMM is %f' % (totaltime,))
    print('The convergence clock time is %f' % (clocktime,))
    print('The objective function value is %f' % (obj_total,))
    print('The central objective function value is %f' % (obj_cent,))
    print('The gap in objective function is %f %%' % (gap,))
