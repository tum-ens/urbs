import os
# import pyomo.environ as pyomo
from pyomo.environ import SolverFactory
import pyomo.environ as pyomo
from datetime import datetime, date
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *
import urbs
import time as t
import pandas as pd

#from multiprocessing import Process, Pipe, Queue, freeze_support, Pool
import multiprocessing as mp

# from pathos.multiprocessing import ProcessingPool as Pool
import queue
# os.system("taskset -p 0xff %d" % os.getpid())
from math import isnan
from .ADMM_async.run_Worker import run_Worker
from .ADMM_async.urbs_admm_model import urbs_admm_model
import time
import copy
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


def create_pipes(clusters, boundarying_lines):
    edges = np.empty((1, 2))
    for cluster_idx in range(0, len(clusters)):
        edges = np.concatenate((edges, np.stack([boundarying_lines[cluster_idx].cluster_from.to_numpy(),
                                                 boundarying_lines[cluster_idx].cluster_to.to_numpy()], axis=1)))
    edges = np.delete(edges, (0), axis=0)
    edges = np.unique(edges, axis=0)
    edges = np.array(list({tuple(sorted(item)) for item in edges}))

    pipes = {}
    for edge in edges.tolist():
        fend, tend = mp.Pipe()
        if edge[0] not in pipes:
            pipes[edge[0]] = {}
        pipes[edge[0]][edge[1]] = fend
        if edge[1] not in pipes:
            pipes[edge[1]] = {}
        pipes[edge[1]][edge[0]] = tend
    return edges, pipes


def parallel_solve(sub_pro):
    sub_pro.solve(save_results=False, load_solutions=False, warmstart=True)


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
def run_regional(input_files, solver, sub_input_files, timesteps, scenario, result_dir,
                 dt, objective,
                 plot_tuples=None, plot_periods=None, report_tuples=None, clusters=None):
    """ run an urbs model for given input, time steps and scenario
        with ADMM

    Args:
        input_file: filename to an Excel spreadsheet for urbs.read_excel
        timesteps: a list of timesteps, e.g. range(0,8761)
        scenario: a scenario function that modifies the input data dict
        result_dir: directory name for result spreadsheet and plots
        plot_tuples: (opt.) list of plot tuples (c.f. urbs.result_figures)
        plot_periods: (opt.) dict of plot periods (c.f. urbs.result_figures)
        report_tuples: (opt.) list of (sit, com) tuples (c.f. urbs.report)

    Returns:
        the urbs model instances
    """
    parallel = False

    # hard-coded year. ADMM doesn't work with intertemporal models (yet)
    year = date.today().year
    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data_all = read_input(input_files, year)
    data_all = scenario(data_all)
    validate_input(data_all)
    validate_dc_objective(data_all, objective)

    if not data_all['global_prop'].loc[year].loc['CO2 limit', 'value'] == np.inf:
        data_all = add_carbon_supplier(data_all, clusters)
        clusters.append(['Carbon_site'])
        print(clusters)

    # if 'test_timesteps' is stored in data dict, replace the timesteps parameter with that value
    timesteps = data_all.pop('test_timesteps', timesteps)

    # subproblem dataprof
    sub_data = {}
    for item in sub_input_files:
        sub_data[item] = urbs.read_input(sub_input_files[item], year)
        # drop source lines added in Excel
        for key in sub_data[item]:
            sub_data[item][key].drop('Source', axis=0, inplace=True, errors='ignore')
        sub_data[item] = scenario(sub_data[item])
        # if 'test_timesteps' is stored in data dict, replace the timesteps parameter with that value
        timesteps = sub_data[item].pop('test_timesteps', timesteps)

    coup_vars = CouplingVars()
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
                coup_vars.rhos[cluster_idx, j, year, sit_from, sit_to] = 2
                coup_vars.lambdas[cluster_idx, j, year, sit_from, sit_to] = 0
                coup_vars.residdual[cluster_idx, j, year, sit_from, sit_to] = 10**8
                coup_vars.residprim[cluster_idx, j, year, sit_from, sit_to] = 10**8
                coup_vars.flow_global[cluster_idx, j, year, sit_from, sit_to] = 0
    all_boundary_lines = pd.concat(list(boundarying_lines.values()))
    all_boundary_lines = \
        all_boundary_lines[~all_boundary_lines.index.duplicated(keep='first')]

    sub = {}
    prob = create_model(data_all, timesteps, dt, type='normal')
    prob.write('orig.lp', io_options={'symbolic_solver_labels': True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    maxit = 1000

    # setup solver
    solver_name = 'gurobi'
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)

    # define parameters to save results of tests to files
    if 'test' in sce:
        test_file = os.path.join(result_dir, scenario.__name__ + '.txt')

    track_file = os.path.join(result_dir, scenario.__name__ + '-tracking.txt')

    # original problem solution (not necessary for ADMM, just to compare)
    results_prob = optim.solve(prob, tee=False)

    flows_from_original_problem = dict((name, entity.value) for (name, entity) in prob.e_tra_in.items())
    flows_from_original_problem = pd.DataFrame.from_dict(flows_from_original_problem, orient='index',
                                                         columns=['Original'])

    pd.options.display.max_rows = 999
    pd.options.display.max_columns = 999
    problems = []

    for cluster_idx in range(0, len(clusters)):
        print(cluster_idx)
        problem = urbs_admm_model()
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
        problem.flow_global.rename_axis(['t','stf','sit','sit_'],inplace=True)
        problem.flow_global = problem.flow_global.to_frame()

        problem.lamda = {(key[1], key[2], key[3], key[4]): value
                         for (key, value) in coup_vars.lambdas.items() if key[0] == cluster_idx}
        problem.lamda = pd.Series(problem.lamda)
        problem.lamda.rename_axis(['t','stf','sit','sit_'],inplace=True)
        problem.lamda = problem.lamda.to_frame()

        problem.rho = {(key[1], key[2], key[3], key[4]): value
                       for (key, value) in coup_vars.rhos.items() if key[0] == cluster_idx}
        problem.rho = pd.Series(problem.rho)
        problem.rho.rename_axis(['t','stf','sit','sit_'],inplace=True)
        problem.rho = problem.rho.to_frame()
        problem.rho = 2

        problem.resid_dual = {(key[1], key[2], key[3], key[4]): value
                              for (key, value) in coup_vars.residdual.items() if key[0] == cluster_idx}
        problem.resid_dual = pd.Series(problem.resid_dual)
        problem.resid_dual.rename_axis(['t','stf','sit','sit_'],inplace=True)
        problem.resid_dual = problem.resid_dual.to_frame()


        problem.resid_prim = {(key[1], key[2], key[3], key[4]): value
                              for (key, value) in coup_vars.residprim.items() if key[0] == cluster_idx}
        problem.resid_prim = pd.Series(problem.resid_prim)
        problem.resid_prim.rename_axis(['t','stf','sit','sit_'],inplace=True)
        problem.resid_prim = problem.resid_prim.to_frame()

        problem.ID = cluster_idx
        boundarying_lines[cluster_idx]['cluster_from'], boundarying_lines[cluster_idx]['cluster_to'], \
        boundarying_lines[cluster_idx]['neighbor_cluster'] = calculate_neighbor_cluster_per_line(boundarying_lines,
                                                                                                 cluster_idx,
                                                                                                 clusters)
        problem.boundarying_lines = boundarying_lines[cluster_idx]
        problems.append(problem)

    edges, pipes = create_pipes(clusters, boundarying_lines)
    for cluster_idx in range(0, len(clusters)):
        problems[cluster_idx].neighbors = sorted(set(boundarying_lines[cluster_idx].neighbor_cluster.to_list()))
        problems[cluster_idx].nneighbors = len(problems[cluster_idx].neighbors)
        problems[cluster_idx].pipes = pipes[cluster_idx]
        problems[cluster_idx].nwait = ceil(problems[cluster_idx].nneighbors * problems[cluster_idx].admmopt.nwaitPercent)

    output = mp.Manager().Queue()
    procs = []

    #run_Worker(1, problems[0], output) #for test
    for cluster_idx in range(0, len(clusters)):
        procs += [mp.Process(target=run_Worker, args=(cluster_idx + 1, problems[cluster_idx], output))]


    start_time = time.time()
    start_clock = time.clock()
    for proc in procs:
        proc.start()

    liveprocs = list(procs)
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


    ## ------------get results ---------------------------
    ttime = time.time()
    tclock = time.clock()
    totaltime = ttime - start_time
    clocktime = tclock - start_clock

    results = sorted(results, key=lambda x: x[0])

    objTotal = 0
    objCent = results_prob['Problem'][0]['Lower bound']

    for cluster_idx in range(0, len(clusters)):
        if cluster_idx != results[cluster_idx][0]:
            print('Error: Result of worker %d not returned!' % (cluster_idx + 1,))
            break
        objTotal += results[cluster_idx][1]['cost']

    gap = (objTotal - objCent) / objCent * 100
    print('The convergence time is %f' % (totaltime,))
    print('The convergence clock time is %f' % (clocktime,))
    print('The objective function value is %f' % (objTotal,))
    print('The central objective function value is %f' % (objCent,))

    print('The gap in objective function is %f %%' % (gap,))

    ## ------------ plots of convergence -----------------
    fig = plt.figure()
    for cluster_idx in range(0, len(clusters)):
        if cluster_idx != results[cluster_idx][0]:
            print('Error: Result of worker %d not returned!' % (cluster_idx + 1,))
            break
        pgap = results[cluster_idx][1]['primal_residual']
        dgap = results[cluster_idx][1]['dual_residual']
        curfig = fig.add_subplot(1, 3, cluster_idx + 1)
        curfig.plot(pgap, color='red', linewidth=2.5, label='primal residual')
        curfig.plot(dgap, color='blue', linewidth=2.5, label='dual residual')
        curfig.set_yscale('log')
        curfig.legend(loc='upper right')

    plt.show()
    import pdb;pdb.set_trace()


    return sub

