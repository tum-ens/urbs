from pyomo.environ import SolverFactory
from .model import create_model
from .plot import *
from .input import *
from .validation import *
import urbs
import pandas as pd
import multiprocessing as mp

import queue
from .ADMM_async.run_Worker import run_worker
from .ADMM_async.urbs_admm_model import urbsADMMmodel
import time
import numpy as np
from math import ceil


def calculate_neighbor_cluster_per_line(boundarying_lines, cluster_idx, clusters):
    neighbor_cluster = 99 * np.ones((len(boundarying_lines[cluster_idx]), 2))
    row_number = 0
    for (year, site_in, site_out, tra, com) in boundarying_lines[cluster_idx].index:
        for cluster in clusters:
            if site_in in cluster:
                neighbor_cluster[row_number, 0] = clusters.index(cluster)
            if site_out in cluster:
                neighbor_cluster[row_number, 1] = clusters.index(cluster)
        row_number = row_number + 1
    cluster_from = neighbor_cluster[:, 0]
    cluster_to = neighbor_cluster[:, 1]
    neighbor_cluster = np.sum(neighbor_cluster, 1) - cluster_idx
    return cluster_from, cluster_to, neighbor_cluster


def create_queues(clusters, boundarying_lines):
    edges = np.empty((1, 2))
    for cluster_idx in range(0, len(clusters)):
        edges = np.concatenate((edges, np.stack([boundarying_lines[cluster_idx].cluster_from.to_numpy(),
                                                 boundarying_lines[cluster_idx].cluster_to.to_numpy()], axis=1)))
    edges = np.delete(edges, 0, axis=0)
    edges = np.unique(edges, axis=0)
    edges = np.array(list({tuple(sorted(item)) for item in edges}))

    queues = {}
    for edge in edges.tolist():
        fend = mp.Manager().Queue()
        tend = mp.Manager().Queue()
        if edge[0] not in queues:
            queues[edge[0]] = {}
        queues[edge[0]][edge[1]] = fend
        if edge[1] not in queues:
            queues[edge[1]] = {}
        queues[edge[1]][edge[0]] = tend
    return edges, queues


class CouplingVars:
    flow_global = {}
    rhos = {}
    lambdas = {}
    cap_global = {}
    residdual = {}
    residprim = {}


def prepare_result_directory(result_name):
    """ create a time stamped directory within the result folder.

    Args:
        result_name: user specified result name

    Returns:
        a subfolder in the result folder 
    
    """
    # timestamp for result directory
    now = datetime.now().strftime('%Y%m%dT%H%M')

    # create result directory if not existent
    result_dir = os.path.join('result', '{}-{}'.format(result_name, now))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    return result_dir


def setup_solver(optim, logfile='solver.log'):
    """ """
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        optim.set_options("method=2")
        # optim.set_options("timelimit=7200")  # seconds
        # optim.set_options("mipgap=5e-4")  # default = 1e-4
    elif optim.name == 'glpk':
        # reference with list of options
        # execute 'glpsol --help'
        optim.set_options("log={}".format(logfile))
        # optim.set_options("tmlim=7200")  # seconds
        # optim.set_options("mipgap=.0005")
    elif optim.name == 'cplex':
        optim.set_options("log={}".format(logfile))
    else:
        print("Warning from setup_solver: no options set for solver "
              "'{}'!".format(optim.name))
    return optim


# @profile
def run_regional(input_file, timesteps, scenario, result_dir,
                 dt, objective, clusters=None):
    """ run an urbs model for given input, time steps and scenario with regional decomposition using ADMM

    Args:
        input_file: filename to an Excel spreadsheet for urbs.read_excel
        timesteps: a list of timesteps, e.g. range(0,8761)
        scenario: a scenario function that modifies the input data dict
        result_dir: directory name for result spreadsheet and plots
        dt: width of a time step in hours(default: 1)
        objective: the entity which is optimized ('cost' of 'co2')
        clusters: user-defined region clusters for regional decomposition (list of tuple lists)

    Returns:
        the urbs model instances
    """
    # hard-coded year. ADMM doesn't work with intertemporal models (yet)
    year = date.today().year

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data_all = read_input(input_file, year)
    data_all = scenario(data_all)
    validate_input(data_all)
    validate_dc_objective(data_all, objective)

    if not data_all['global_prop'].loc[year].loc['CO2 limit', 'value'] == np.inf:
        data_all = add_carbon_supplier(data_all, clusters)
        clusters.append(['Carbon_site'])

    # if 'test_timesteps' is stored in data dict, replace the timesteps parameter with that value
    timesteps = data_all.pop('test_timesteps', timesteps)

    # initiate a coupling-variables Class
    coup_vars = CouplingVars()

    # identify the boundarying and internal lines
    boundarying_lines = {}
    internal_lines = {}

    boundarying_lines_logic = np.zeros((len(clusters),
                                        data_all['transmission'].shape[0]),
                                       dtype=bool)
    internal_lines_logic = np.zeros((len(clusters),
                                     data_all['transmission'].shape[0]),
                                    dtype=bool)

    for cluster_idx in range(0, len(clusters)):
        for j in range(0, data_all['transmission'].shape[0]):
            boundarying_lines_logic[cluster_idx, j] = (
                    (data_all['transmission'].index.get_level_values('Site In')[j]
                     in clusters[cluster_idx])
                    ^ (data_all['transmission'].index.get_level_values('Site Out')[j]
                       in clusters[cluster_idx]))
            internal_lines_logic[cluster_idx, j] = (
                    (data_all['transmission'].index.get_level_values('Site In')[j]
                     in clusters[cluster_idx])
                    and (data_all['transmission'].index.get_level_values('Site Out')[j]
                         in clusters[cluster_idx]))

        boundarying_lines[cluster_idx] = \
            data_all['transmission'].loc[boundarying_lines_logic[cluster_idx, :]]
        internal_lines[cluster_idx] = \
            data_all['transmission'].loc[internal_lines_logic[cluster_idx, :]]

        for i in range(0, boundarying_lines[cluster_idx].shape[0]):
            sit_from = boundarying_lines[cluster_idx].iloc[i].name[1]
            sit_to = boundarying_lines[cluster_idx].iloc[i].name[2]

            for j in timesteps[1:]:
                coup_vars.lambdas[cluster_idx, j, year, sit_from, sit_to] = 0
                coup_vars.rhos[cluster_idx, j, year, sit_from, sit_to] = 5
                coup_vars.flow_global[cluster_idx, j, year, sit_from, sit_to] = 0


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

    pd.options.display.max_rows = 999
    pd.options.display.max_columns = 999

    problems = []
    sub = {}

    # initiate urbs_admm_model Classes for each subproblem
    for cluster_idx in range(0, len(clusters)):
        problem = urbsADMMmodel()
        sub[cluster_idx] = urbs.create_model(data_all, timesteps, type='sub',
                                             sites=clusters[cluster_idx],
                                             coup_vars=coup_vars,
                                             data_transmission_boun=boundarying_lines[cluster_idx],
                                             data_transmission_int=internal_lines[cluster_idx],
                                             cluster=cluster_idx)
        problem.sub_pyomo = sub[cluster_idx]
        problem.flow_global = {(key[1], key[2], key[3], key[4]): value
                               for (key, value) in coup_vars.flow_global.items() if key[0] == cluster_idx}
        problem.flow_global = pd.Series(problem.flow_global)
        problem.flow_global.rename_axis(['t', 'stf', 'sit', 'sit_'], inplace=True)
        problem.flow_global = problem.flow_global.to_frame()

        problem.lamda = {(key[1], key[2], key[3], key[4]): value
                         for (key, value) in coup_vars.lambdas.items() if key[0] == cluster_idx}
        problem.lamda = pd.Series(problem.lamda)
        problem.lamda.rename_axis(['t', 'stf', 'sit', 'sit_'], inplace=True)
        problem.lamda = problem.lamda.to_frame()

        problem.rho = 5

        problem.ID = cluster_idx
        problem.result_dir = result_dir
        problem.sce = sce
        boundarying_lines[cluster_idx]['cluster_from'], boundarying_lines[cluster_idx]['cluster_to'], \
            boundarying_lines[cluster_idx]['neighbor_cluster'] = calculate_neighbor_cluster_per_line(boundarying_lines,
                                                                                                     cluster_idx,
                                                                                                     clusters)
        problem.boundarying_lines = boundarying_lines[cluster_idx]
        problem.na = len(clusters)
        problems.append(problem)

    # create Queues for each communication channel
    edges, queues = create_queues(clusters, boundarying_lines)

    # define further necessary fields for the subproblems
    for cluster_idx in range(0, len(clusters)):
        problems[cluster_idx].neighbors = sorted(set(boundarying_lines[cluster_idx].neighbor_cluster.to_list()))
        problems[cluster_idx].nneighbors = len(problems[cluster_idx].neighbors)

        problems[cluster_idx].queues = dict((key, value) for (key, value) in queues.items() if key == cluster_idx)
        problems[cluster_idx].queues.update(dict(
            (key0, {key: value}) for (key0, n) in queues.items() for (key, value) in n.items() if
            key == cluster_idx).items())
        problems[cluster_idx].nwait = ceil(
            problems[cluster_idx].nneighbors * problems[cluster_idx].admmopt.nwaitPercent)

    # define a Queue class for collecting the results from each subproblem after convergence
    output = mp.Manager().Queue()

    # define the asynchronous jobs for ADMM routines
    procs = []
    for cluster_idx in range(0, len(clusters)):
        procs += [mp.Process(target=run_worker, args=(cluster_idx + 1, problems[cluster_idx], output))]

    start_time = time.time()
    start_clock = time.clock()
    for proc in procs:
        proc.start()

    liveprocs = list(procs)

    # collect results as the subproblems converge
    results = []
    while liveprocs:
        try:
            while 1:
                results.append(output.get(False))
        except queue.Empty:
            pass

        time.sleep(0.5)
        if not output.empty():
            continue

        liveprocs = [p for p in liveprocs if p.is_alive()]

    for proc in procs:
        proc.join()

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

    #testlog
    file_object = open('log_for_test.txt', 'a')
    file_object.write('Timesteps for this test is %f' % (len(timesteps),))
    file_object.write('The convergence time for original problem is %f' % (orig_duration,))
    file_object.write('The convergence time for ADMM is %f' % (totaltime,))
    file_object.write('The gap in objective function is %f %%' % (gap,))
    file_object.close()
    # ------------ plots of convergence -----------------
    fig = plt.figure()
    for cluster_idx in range(0, len(clusters)):
        if cluster_idx != results[cluster_idx][0]:
            print('Error: Result of worker %d not returned!' % (cluster_idx + 1,))
            break
        pgap = results[cluster_idx][1]['primal_residual']
        dgap = results[cluster_idx][1]['dual_residual']
        curfig = fig.add_subplot(1, len(clusters), cluster_idx + 1)
        curfig.plot(pgap, color='red', linewidth=2.5, label='primal residual')
        curfig.plot(dgap, color='blue', linewidth=2.5, label='dual residual')
        curfig.set_yscale('log')
        curfig.legend(loc='upper right')

    #plt.show()

    return sub
