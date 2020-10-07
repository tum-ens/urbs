import os
import pyomo.environ
from pyomo.opt.base import SolverFactory
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


def run_scenario(input_files, Solver, timesteps, scenario, result_dir, dt,
                 objective, plot_tuples=None,  plot_sites_name=None,
                 plot_periods=None, report_tuples=None,
                 report_sites_name=None):
    """ run an urbs model for given input, time steps and scenario

    Args:
        - input_files: filenames of input Excel spreadsheets
        - Solver: the user specified solver
        - timesteps: a list of timesteps, e.g. range(0,8761)
        - scenario: a scenario function that modifies the input data dict
        - result_dir: directory name for result spreadsheet and plots
        - dt: length of each time step (unit: hours)
        - objective: objective function chosen (either "cost" or "CO2")
        - plot_tuples: (optional) list of plot tuples (c.f. urbs.result_figures)
        - plot_sites_name: (optional) dict of names for sites in plot_tuples
        - plot_periods: (optional) dict of plot periods
          (c.f. urbs.result_figures)
        - report_tuples: (optional) list of (sit, com) tuples
          (c.f. urbs.report)
        - report_sites_name: (optional) dict of names for sites in
          report_tuples

    Returns:
        the urbs model instance
    """

    # sets a modeled year for non-intertemporal problems
    # (necessary for consitency)
    year = date.today().year

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = read_input(input_files, year)
    data = scenario(data)
    validate_input(data)
    validate_dc_objective(data, objective)

    # create model
    prob = create_model(data, dt, timesteps, objective)
    prob.write('model.lp', io_options={'symbolic_solver_labels':True})

    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory(Solver)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(prob, tee=True)
    assert str(result.solver.termination_condition) == 'optimal'

    # save problem solution (and input data) to HDF5 file
    # save(prob, os.path.join(result_dir, '{}.h5'.format(sce)))

    # write report to spreadsheet
    report(
        prob,
        os.path.join(result_dir, '{}.xlsx').format(sce),
        report_tuples=report_tuples,
        report_sites_name=report_sites_name)

    # result plots
    result_figures(
        prob,
        os.path.join(result_dir, '{}'.format(sce)),
        timesteps,
        plot_title_prefix=sce.replace('_', ' '),
        plot_tuples=plot_tuples,
        plot_sites_name=plot_sites_name,
        periods=plot_periods,
        figure_size=(24, 9))

    return prob

def run_regional(input_files, solver, sub_input_files, timesteps, scenario, result_dir,
                 dt, objective, 
                 plot_tuples=None, plot_periods=None, report_tuples=None, clusters=None):
    """ run an urbs model for given input, time steps and scenario
        with Benders Decomposition

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
    caps_coupling = False
    
    year = date.today().year
    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = read_input(input_files, year)
    data = scenario(data)
    validate_input(data)
    validate_dc_objective(data, objective)

    if not data['global_prop'].loc[year].loc['CO2 limit','value'] == np.inf:
        data = add_carbon_supplier(data, clusters)
        clusters.append('Carbon_site')
        print(clusters)
    
    # if 'test_timesteps' is stored in data dict, replace the timesteps parameter with that value
    timesteps = data.pop('test_timesteps', timesteps)

    # subproblem data
    sub_data = {}
    for item in sub_input_files:
        sub_data[item] = urbs.read_input(sub_input_files[item],year)
        # drop source lines added in Excel
        for key in sub_data[item]:
            sub_data[item][key].drop('Source', axis=0, inplace=True, errors='ignore')
        sub_data[item] = scenario(sub_data[item])
        # if 'test_timesteps' is stored in data dict, replace the timesteps parameter with that value
        timesteps = sub_data[item].pop('test_timesteps', timesteps)

    # init parameters for ADMM
    class CouplingVars:
        flow_global= {}
        rhos= {}
        lambdas = {}  
        cap_global= {}
        rhos_cap = {}
        lambdas_cap = {}
        residdual = {}
        residprim = {}  
        caps_coupling = False
        residdual_cap = {}
        residprim_cap = {}  
        
    coup_vars = CouplingVars() 
    coup_vars.caps_coupling = caps_coupling
    boundarying_lines = {}
    internal_lines = {}
    
    boundarying_lines_logic = np.zeros((len(clusters), 
                                       data['transmission'].shape[0]), 
                                       dtype=bool)
    internal_lines_logic = np.zeros((len(clusters),
                                    data['transmission'].shape[0]), 
                                    dtype=bool)
               
    for cluster_idx in range(0,len(clusters)):
        for j in range(0,data['transmission'].shape[0]):
            boundarying_lines_logic[cluster_idx,j] = (
                    (data['transmission'].index.get_level_values('Site In')[j] 
                    in clusters[cluster_idx]) 
                    ^ (data['transmission'].index.get_level_values('Site Out')[j] 
                    in clusters[cluster_idx]))
            internal_lines_logic[cluster_idx,j]=(
                    (data['transmission'].index.get_level_values('Site In')[j] 
                    in clusters[cluster_idx]) 
                    and (data['transmission'].index.get_level_values('Site Out')[j]
                    in clusters[cluster_idx]))

        boundarying_lines[cluster_idx] = \
            data['transmission'].loc[boundarying_lines_logic[cluster_idx,:]]
        internal_lines[cluster_idx] = \
            data['transmission'].loc[internal_lines_logic[cluster_idx,:]]
        
        for i in range(0,boundarying_lines[cluster_idx].shape[0]):
            sit_from=boundarying_lines[cluster_idx].iloc[i].name[1]
            sit_to=boundarying_lines[cluster_idx].iloc[i].name[2]
            
            if caps_coupling:            
                coup_vars.rhos_cap[cluster_idx, year, sit_from, sit_to]=2           
                coup_vars.lambdas_cap[cluster_idx, year, sit_from, sit_to]=0   
            
            for j in timesteps[1:]:
                coup_vars.rhos[cluster_idx, year, j, sit_from, sit_to]=2           
                coup_vars.lambdas[cluster_idx, year, j, sit_from, sit_to]=1
                coup_vars.residdual[cluster_idx, year, j, sit_from, sit_to]=0        
                coup_vars.residprim[cluster_idx, year, j, sit_from, sit_to]=0    
                
    all_boundary_lines = pd.concat(list(boundarying_lines.values()))
    all_boundary_lines = \
        all_boundary_lines[~all_boundary_lines.index.duplicated(keep='first')]

    for i in range(0,all_boundary_lines.shape[0]):
        sit_from=all_boundary_lines.iloc[i].name[1]
        sit_to=all_boundary_lines.iloc[i].name[2]
        if caps_coupling:                    
            coup_vars.cap_global[year,sit_from,sit_to]=0   
            
        for j in timesteps[1:]:
            coup_vars.flow_global[year,j,sit_from,sit_to]=0            

       
    sub = {}         
    prob = create_model(data, timesteps, dt, type='normal')
    prob.write('orig.lp', io_options={'symbolic_solver_labels':True})
    # refresh time stamp string and create filename for logfile
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    maxit = 501
    mu = 10;
    tau = 0.1;
 
    # setup solver
    
    solver_name = 'gurobi'
    optim = SolverFactory(solver_name)  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    # optim.options['OptimalityTol'] = 1e-9
    # optim.options['FeasibilityTol'] = 1e-9
    # optim.options['NumericFocus'] = 3
    # optim.options['Method'] = 4

    # define parameters to save results of tests to files
    if 'test' in sce:
        test_file = os.path.join(result_dir, scenario.__name__+'.txt')

    track_file = os.path.join(result_dir, scenario.__name__+'-tracking.txt')

    # original problem solution
    results_prob = optim.solve(prob, tee=False)
    flows_from_original_problem = urbs.get_entity(prob, 'e_tra_in')
    flows_from_original_problem.columns = 'Original'    
    if caps_coupling:            
        caps_from_original_problem = urbs.get_entity(prob, 'cap_tra')
        caps_from_original_problem.columns = 'Original' 
        
    pd.options.display.max_rows = 999
    pd.options.display.max_columns = 999
    for cluster_idx in range(0,len(clusters)):
        data = read_input(input_files, year)
        data = scenario(data)
        validate_input(data)
        validate_dc_objective(data, objective)

        if not data['global_prop'].loc[year].loc['CO2 limit','value'] == np.inf:
            data = add_carbon_supplier(data, clusters)
        sub[cluster_idx] = urbs.create_model(data, timesteps, type='sub',
                                    sites=clusters[cluster_idx],
                                    coup_vars=coup_vars,
                                    data_transmission_boun=boundarying_lines[cluster_idx],
                                    data_transmission_int=internal_lines[cluster_idx],
                                    cluster=cluster_idx)   
        sub[cluster_idx].write(str(cluster_idx) +' sub.lp',
                               io_options={'symbolic_solver_labels':True})

    if parallel:
        jobs = []
        manager = mp.Manager()
        return_dict = manager.dict()
        
    t1 = t.time()
    
    cost_history= np.zeros(maxit)
    flow_global_history = pd.DataFrame()
    
    if caps_coupling:
        cap_global_history = pd.DataFrame()
             
    # ADMM loop
    for iteration in range(1, maxit):
        for cluster_idx in range(0,len(clusters)):
            #adjust the global flows as mutable parameters            
            for key in coup_vars.flow_global:
                sub[cluster_idx].flow_global[key] = coup_vars.flow_global[key]
                
            #adjsut the global capacities as mutable parameters (if enabled)    
            if caps_coupling:                            
                for key in coup_vars.cap_global:
                    sub[cluster_idx].cap_global[key] = coup_vars.cap_global[key]      
                    
            lambdas_temp = dict((key[1:],value) for key, value 
                                in coup_vars.lambdas.items() 
                                if key[0] == cluster_idx)   
            rhos_temp = dict((key[1:],value) for key, value 
                             in coup_vars.rhos.items() 
                             if key[0] == cluster_idx)   
            
            for key in lambdas_temp:            
                sub[cluster_idx].lamda[key] = lambdas_temp[key]
            for key in rhos_temp:            
                sub[cluster_idx].rho[key] = rhos_temp[key]
                
            if caps_coupling:                            
                lambdas_temp = dict((key[1:],value) for key, value 
                                    in coup_vars.lambdas_cap.items() 
                                    if key[0] == cluster_idx)   
                rhos_temp = dict((key[1:],value) for key, value
                                 in coup_vars.rhos_cap.items()
                                 if key[0] == cluster_idx)              
                for key in lambdas_temp:            
                    sub[cluster_idx].lamda_cap[key] = lambdas_temp[key]
                for key in rhos_temp:            
                    sub[cluster_idx].rho_cap[key] = rhos_temp[key]        
 
        flows_from_subs_in = []
        caps_from_subs = []
        result_sub = {}

        if parallel:
            #### Parallel solution
            for inst in sub:
                p = mp.Process(target=optim_solve_tee_false, 
                               args=(sub[inst],inst,return_dict,log_filename))
                jobs.append(p)
                p.start()
        
            for proc in jobs:
                proc.join()
        
            for key in return_dict.keys():
                sub[key] = return_dict[key]
        
        else:
            for inst in sub:
                result_sub[inst] = optim.solve(sub[inst], tee=False)         
        
        for inst in sub:                          
            flows_from_a_sub_in = urbs.get_entity(sub[inst], 'e_tra_in')            
            flows_from_a_sub_in.columns = 'Sub ' + str(inst)
            flows_from_subs_in.append(flows_from_a_sub_in)
            if caps_coupling:            
                caps_from_a_sub = urbs.get_entity(sub[inst], 'cap_tra')
                caps_from_a_sub.columns = 'Sub ' + str(inst)
                caps_from_subs.append(caps_from_a_sub)

        flows_from_subs_in0 = pd.concat(flows_from_subs_in,axis=1)
        flows_from_subs_in = pd.concat(flows_from_subs_in)

        if caps_coupling:            
            caps_from_subs0 = pd.concat(caps_from_subs,axis=1)
            caps_from_subs = pd.concat(caps_from_subs)

        flows_from_subs_in = flows_from_subs_in.groupby(
                ['stf','t','sit','sit_','tra','com']).mean()
        flows_from_subs_in = flows_from_subs_in.reset_index(
                level=['com','tra'], drop=True)
        
        flow_global_history[iteration]=flows_from_subs_in
           
        if caps_coupling:           
           cap_global_history[iteration]=caps_from_subs
       
        if caps_coupling:                       
            caps_from_subs = caps_from_subs.groupby(
                    ['stf','sit','sit_','tra','com']).mean()
            caps_from_subs = caps_from_subs.reset_index(
                    level=['com','tra'], drop=True)
        
        for i in range(0,all_boundary_lines.shape[0]):
            sit_from=all_boundary_lines.iloc[i].name[1]
            sit_to=all_boundary_lines.iloc[i].name[2]
            if caps_coupling:                        
                coup_vars.cap_global[(year,sit_from,sit_to)] = \
                    caps_from_subs[(year,sit_from,sit_to)]            
            for j in timesteps[1:]:
                coup_vars.flow_global[(year,j,sit_from,sit_to)] = \
                    flows_from_subs_in[(year,j,sit_from,sit_to)]
                
        #adjusting rho and lambda
        for cluster_idx in range(0,len(clusters)):
            for i in range(0,boundarying_lines[cluster_idx].shape[0]):
                sit_from=boundarying_lines[cluster_idx].iloc[i].name[1]
                sit_to=boundarying_lines[cluster_idx].iloc[i].name[2]
             
                if (caps_coupling and iteration >1):
                    coup_vars.residprim_cap[cluster_idx,year,sit_from,sit_to]= \
                          (urbs.get_entity(sub[cluster_idx], 'cap_tra')[year,sit_from,sit_to].values[0] - caps_from_subs[year,sit_from,sit_to])**2                        
                    coup_vars.residdual_cap[cluster_idx,year,sit_from,sit_to]= \
                        coup_vars.rhos_cap[cluster_idx,year,sit_from,sit_to]**2 * \
                        (cap_global_history[iteration].loc[year,sit_from,sit_to].values[0] -
                         cap_global_history[iteration-1].loc[year,sit_from,sit_to].values[0])**2
                          
                    if iteration >= 2: 
                        if coup_vars.residprim_cap[cluster_idx,year,sit_from,sit_to] \
                        >= mu * coup_vars.residdual_cap[cluster_idx,year,sit_from,sit_to]:
                            coup_vars.rhos_cap[cluster_idx,year,sit_from,sit_to] = \
                            coup_vars.rhos_cap[cluster_idx,year,sit_from,sit_to] * (1 + tau)
                        else:
                            coup_vars.rhos_cap[cluster_idx,year,sit_from,sit_to] = \
                            coup_vars.rhos_cap[cluster_idx,year,sit_from,sit_to] / (1 + tau)             
                            
                for j in timesteps[1:]: 
                    if iteration >1:
                        coup_vars.residprim[cluster_idx,year,j,sit_from,sit_to]= \
                            (urbs.get_entity(sub[cluster_idx], 'e_tra_in')[j,year,sit_from,sit_to].values[0] -
                             flows_from_subs_in[year,j,sit_from,sit_to])**2  
                        #import pdb;pdb.set_trace()     
                        coup_vars.residdual[cluster_idx,year,j,sit_from,sit_to]= \
                             coup_vars.rhos[cluster_idx,year,j,sit_from,sit_to]**2 * \
                             (flow_global_history[iteration].loc[year,j,sit_from,sit_to].values[0] -
                              flow_global_history[iteration-1].loc[year,j,sit_from,sit_to].values[0])**2    
                           
                    if iteration >= 2:
                        if coup_vars.residprim[cluster_idx,year,j,sit_from,sit_to] \
                        >= mu * coup_vars.residdual[cluster_idx,year,j,sit_from,sit_to]:
                            coup_vars.rhos[cluster_idx,year,j,sit_from,sit_to] = \
                            coup_vars.rhos[cluster_idx,year,j,sit_from,sit_to] * (1 + tau)
                        else:
                            coup_vars.rhos[cluster_idx,year,j,sit_from,sit_to] = \
                            coup_vars.rhos[cluster_idx,year,j,sit_from,sit_to] / (1 + tau)                          
                                
                    coup_vars.lambdas[cluster_idx,year,j,sit_from,sit_to] = \
                    coup_vars.lambdas[cluster_idx,year,j,sit_from,sit_to] + \
                        coup_vars.rhos[cluster_idx,year,j,sit_from,sit_to] * \
                        (urbs.get_entity(sub[cluster_idx], 'e_tra_in')[j,year,sit_from,sit_to].values[0] - flows_from_subs_in[year,j,sit_from,sit_to])        
                        
                if caps_coupling:                            
                    coup_vars.lambdas_cap[cluster_idx,year,sit_from,sit_to] = \
                    coup_vars.lambdas_cap[cluster_idx,year,sit_from,sit_to] + \
                        coup_vars.rhos_cap[cluster_idx,year,sit_from,sit_to] * \
                        (urbs.get_entity(sub[cluster_idx], 'cap_tra')[year,sit_from,sit_to].values[0] - caps_from_subs[year,sit_from,sit_to])                       
        print(coup_vars.lambdas[0,2020,1,'Carbon_site','Mid'])                
        #import pdb;pdb.set_trace()
        pd.set_option('display.float_format', lambda x: '%.0f' % x)
        
        #print(pd.concat([flows_from_subs_in0,flows_from_original_problem],axis=1))
        aaa=pd.concat([flows_from_subs_in0,flows_from_original_problem],axis=1)
        aaa=aaa.reset_index(level=0).loc[all_boundary_lines.index]
        print(sum(prob.costs[ct]() for ct in prob.cost_type))
        print(sum(sum(sub[i].costs[ct]() for ct in sub[inst].cost_type) for i in sub))
        cost_history[iteration-1]= sum(sum(sub[i].costs[ct]() for ct in sub[inst].cost_type) for i in sub)
        if iteration >= 2:
            plt.plot(cost_history[1:iteration-1])
            plt.figure();
            flow_global_history.T.plot(legend=False)
            plt.pause(0.01)
            plt.show()
        if abs(sum(prob.costs[ct]() for ct in prob.cost_type)-sum(sum(sub[i].costs[ct]() for ct in sub[inst].cost_type) for i in sub)) <= 0.1:
            print(str(iteration)+' iterations to solve '+ '(parallel '+str(parallel)+')'+ '(capacities coupled '+str(caps_coupling)+')')
        #import pdb;pdb.set_trace()   
        amko=[(b,a,c,d) for a,b,c,d,e,f in flows_from_subs_in0.index.tolist()]
        truth_list=np.zeros(len(amko), dtype=bool)
        for j in range(0,len(amko)):
            truth_list[j] = amko[j] in list(coup_vars.flow_global.keys())
        flows_from_subs_in0=flows_from_subs_in0[truth_list]  

        if caps_coupling:
            amko=[(a,b,c) for a,b,c,d,e in caps_from_subs0.index.tolist()]
            truth_list=np.zeros(len(amko), dtype=bool)
            for j in range(0,len(amko)):
                truth_list[j] = amko[j] in list(coup_vars.cap_global.keys())
            caps_from_subs0=caps_from_subs0[truth_list]            
            pd.set_option('display.max_columns', 500)

        t2 = t.time()                
        print(str(t2-t1)+' seconds elapsed, '+str(iteration)+' iterations')
        if iteration % 100== 0:
            t2 = t.time()         
            print(str(t2-t1)+' seconds to solve '+ '(parallel '+str(parallel)+')'+ '(capacities coupled '+str(caps_coupling)+')')            
            import pdb;pdb.set_trace()                      
  
    return sub
#
#    # save problem solution (and input data) to HDF5 file
#    urbs.save(prob, os.path.join(result_dir, 'original-{}.h5'.format(sce)))
#    urbs.save(master, os.path.join(result_dir, 'master-{}.h5'.format(sce)))
