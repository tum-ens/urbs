############################################################################
# This file builds the opf_admm_model class that represents a subproblem 
# ADMM algorithm parameters should be defined in admmoption
# Package Pypower 5.1.3 is used in this application
#############################################################################

import numpy as np
import pandas as pd
import pyomo.environ as pyomo
from copy import deepcopy
from numpy import maximum


class urbsADMMmodel(object):
    """This class encapsulates the local urbs subproblem and implements admm steps
    including x-update(solving subproblem), send data to neighbors, receive data
    from neighbors, z-update (global flows) and y-update (lambdas)
    """

    def __init__(self):
        # initialize all the fields
        self.boundarying_lines = None
        self.flows_all = None
        self.flows_with_neighbor = None
        self.flow_global = None
        self.sub_pyomo = None
        self.sub_persistent = None
        self.neighbors = None
        self.nneighbors = None
        self.nwait = None
        self.var = {'flow_global': None, 'rho': None}
        self.ID = None
        self.nbor = {}
        self.pipes = None
        self.queues = None
        self.admmopt = admmoption()
        self.recvmsg = {}
        self.primalgap = [9999]
        self.dualgap = [9999]
        self.gapAll = None
        self.rho = None
        self.lamda = None

    def solve_problem(self):
        self.sub_persistent.solve(save_results=False, load_solutions=False, warmstart=True)

    def fix_flow_global(self):
        for key in self.flow_global.index:
            if not isinstance(self.flow_global.loc[key], pd.core.series.Series):
                self.sub_pyomo.flow_global[key].fix(self.flow_global.loc[key])
                self.sub_persistent.update_var(
                    self.sub_pyomo.flow_global[key])
            else:
                self.sub_pyomo.flow_global[key].fix(self.flow_global.loc[key, 0])
                self.sub_persistent.update_var(
                    self.sub_pyomo.flow_global[key])

    def fix_lambda(self):
        for key in self.lamda.index:
            if not isinstance(self.lamda.loc[key], pd.core.series.Series):
                self.sub_pyomo.lamda[key].fix(self.lamda.loc[key])
                self.sub_persistent.update_var(self.sub_pyomo.lamda[key])
            else:
                self.sub_pyomo.lamda[key].fix(self.lamda.loc[key, 0])
                self.sub_persistent.update_var(self.sub_pyomo.lamda[key])

    def set_quad_cost(self, rhos_old):
        quadratic_penalty_change = 0
        # Hard coded transmission name: 'hvac', commodity 'Elec' for performance.
        # Caution, as these need to be adjusted if the transmission of other commodities exists!
        for key in self.flow_global.index:
            if (key[2] == 'Carbon_site') or (key[3] == 'Carbon_site'):
                quadratic_penalty_change += 0.5 * (
                        self.rho - rhos_old) * \
                                            (self.sub_pyomo.e_tra_in[
                                                 key, 'CO2_line', 'Carbon'] -
                                             self.sub_pyomo.flow_global[key]) ** 2
            else:
                quadratic_penalty_change += 0.5 * (
                        self.rho - rhos_old) * \
                                            (self.sub_pyomo.e_tra_in[key, 'hvac', 'Elec'] -
                                             self.sub_pyomo.flow_global[key]) ** 2

        old_expression = self.sub_persistent._pyomo_model.objective_function.expr
        self.sub_persistent._pyomo_model.del_component('objective_function')
        self.sub_persistent._pyomo_model.add_component('objective_function',
                                                       pyomo.Objective(expr = old_expression + quadratic_penalty_change,
                                                                       sense=pyomo.minimize))
        self.sub_persistent.set_objective(
            self.sub_persistent._pyomo_model.objective_function)
        self.sub_persistent._solver_model.update()


    def send(self):
        dest = self.queues[self.ID].keys()
        for k in dest:
            # prepare the message to be sent to neighbor k
            msg = message()
            msg.config(self.ID, k, self.flows_with_neighbor[k], self.rho,
                       self.lamda[self.lamda.index.isin(self.flows_with_neighbor[k].index)],
                       self.gapAll)
            self.queues[self.ID][k].put(msg)

    def recv(self, pollrounds=5):
        twait = self.admmopt.pollWaitingtime
        dest = list(self.queues[self.ID].keys())
        recv_flag = [0] * self.nneighbors
        arrived = 0  # number of arrived neighbors
        pollround = 0

        # keep receiving from nbor 1 to nbor K in round until nwait neighbors arrived
        while arrived < self.nwait and pollround < pollrounds:
            for i in range(len(dest)):
                k = dest[i]
                while not self.queues[k][self.ID].empty():  # read from queue until get the last message
                    self.recvmsg[k] = self.queues[k][self.ID].get(timeout=twait)
                    recv_flag[i] = 1
                    # print("Message received at %d from %d" % (self.ID, k))
            arrived = sum(recv_flag)
            pollround += 1

    def update_z(self):
        srcs = self.queues[self.ID].keys()
        flow_global_old = deepcopy(self.flow_global)
        for k in srcs:
            if k in self.recvmsg and self.recvmsg[k].tID == self.ID:  # target is this Cluster
                nborvar = self.recvmsg[k].fields  # nborvar['flow'], nborvar['convergeTable']
                self.flow_global.loc[self.flow_global.index.isin(self.flows_with_neighbor[k].index)] = \
                    (self.lamda.loc[self.lamda.index.isin(self.flows_with_neighbor[k].index)] +
                     nborvar['lambda'] + self.flows_with_neighbor[k] * self.rho + nborvar['flow'] * nborvar['rho']) \
                    / (self.rho + nborvar['rho'])
        self.dualgap += [self.rho * (np.sqrt(np.square(self.flow_global - flow_global_old).sum(axis=0)[0]))]

    def update_y(self):
        self.lamda = self.lamda + self.rho * (self.flows_all.loc[:, [0]] - self.flow_global)

    # update rho and primal gap locally
    def update_rho(self, nu):
        self.primalgap += [np.sqrt(np.square(self.flows_all - self.flow_global).sum(axis=0)[0])]
        # update rho (only in the first rho_iter_nu iterations)
        if nu <= self.admmopt.rho_update_nu:
            if self.primalgap[-1] > self.admmopt.mu * self.dualgap[-1]:
                self.rho = min(self.admmopt.rho_max, self.rho * self.admmopt.tau)
            elif self.dualgap[-1] > self.admmopt.mu * self.primalgap[-1]:
                self.rho = min(self.rho / self.admmopt.tau, self.admmopt.rho_max)
        # update local converge table
        self.gapAll[self.ID] = self.primalgap[-1]

    #   # use the maximum rho among neighbors for local update
    def choose_max_rho(self):
        srcs = self.recvmsg.keys()
        for k in srcs:
            rho_nbor = self.recvmsg[k].fields['rho']
            self.rho = maximum(self.rho, rho_nbor)  # pick the maximum one

    #
    def converge(self):
        # first update local converge table using received converge tables
        if self.recvmsg is not None:
            for k in self.recvmsg:
                table = self.recvmsg[k].fields['convergeTable']
                self.gapAll = list(map(min, zip(self.gapAll, table)))
        # check if all local primal gaps < tolerance
        if max(self.gapAll) < self.convergetol:
            return True
        else:
            return False

    def retrieve_boundary_flows(self):
        e_tra_in_per_neighbor = {}

        self.sub_persistent.load_vars(self.sub_pyomo.e_tra_in[:, :, :, :, :, :])
        boundary_lines_pairs = self.boundarying_lines.reset_index().set_index(['Site In', 'Site Out']).index
        e_tra_in_dict = {(tm, stf, sit_in, sit_out): v.value for (tm, stf, sit_in, sit_out, tra, com), v in
                         self.sub_pyomo.e_tra_in.items() if ((sit_in, sit_out) in boundary_lines_pairs)}

        e_tra_in_dict = pd.DataFrame(list(e_tra_in_dict.values()),
                                     index=pd.MultiIndex.from_tuples(e_tra_in_dict.keys())).rename_axis(
            ['t', 'stf', 'sit', 'sit_'])

        for (tm, stf, sit_in, sit_out) in e_tra_in_dict.index:
            e_tra_in_dict.loc[(tm, stf, sit_in, sit_out), 'neighbor_cluster'] = self.boundarying_lines.reset_index(). \
                set_index(['support_timeframe', 'Site In', 'Site Out']).loc[(stf, sit_in, sit_out), 'neighbor_cluster']

        for neighbor in self.neighbors:
            e_tra_in_per_neighbor[neighbor] = e_tra_in_dict.loc[e_tra_in_dict['neighbor_cluster'] == neighbor]
            e_tra_in_per_neighbor[neighbor].reset_index().set_index(['t', 'stf', 'sit', 'sit_'], inplace=True)
            e_tra_in_per_neighbor[neighbor].drop('neighbor_cluster', axis=1, inplace=True)

        return e_tra_in_dict, e_tra_in_per_neighbor


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


class message(object):
    """ This class defines the message region i sends to/receives from j """

    def __init__(self):
        self.fID = 0  # source region ID
        self.tID = 0  # destination region ID
        self.fields = {
            'flow': None,
            'rho': None,
            'lambda': None,
            'convergeTable': None}

    def config(self, f, t, var_flow, var_rho, var_lambda, gapall):  # AVall and var are local variables of f region
        self.fID = f
        self.tID = t

        self.fields['flow'] = var_flow
        self.fields['rho'] = var_rho
        self.fields['lambda'] = var_lambda
        self.fields['convergeTable'] = gapall
