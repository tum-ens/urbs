############################################################################
# This file builds the opf_admm_model class that represents a subproblem 
# ADMM algorithm parameters should be defined in admmoption
# Package Pypower 5.1.3 is used in this application
#############################################################################

import numpy as np
import pandas as pd
import pyomo.environ as pyomo
from copy import deepcopy
from numpy import Inf, maximum


class urbs_admm_model(object):
    """This class encapsulates the local urbs subproblem and implements admm steps
    including x-update(solving subproblem), send data to neighbors, receive data
    from neighbors, z-update (global flows) and y-update (lambdas)
    """

    def __init__(self):
        # initialize all the fields
        self.var = {'flow_global': None, 'rho': None}
        self.ID = None
        self.nbor = {}
        self.pipes = None
        self.admmopt = admmoption()
        self.recvmsg = {}
        #self.na = 17
        self.primalgap = [9999]
        self.dualgap = [9999]

    def solve_problem(self):
        self.sub_persistent.solve(save_results=False, load_solutions=False, warmstart=True)

    def fix_lambda(self):
        for key in self.lamda.index:
            if not isinstance(self.lamda.loc[key], pd.core.series.Series):
                self.sub_pyomo.lamda[key].fix(self.lamda.loc[key])
                self.sub_persistent.update_var(self.sub_pyomo.lamda[key])
            else:
                self.sub_pyomo.lamda[key].fix(self.lamda.loc[key,0])
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
                                                       pyomo.Objective(expr=old_expression + quadratic_penalty_change,
                                                                       sense=pyomo.minimize))
        # self.sub_persistent._pyomo_model.objective_function = pyomo.Objective(expr=self.sub_persistent._pyomo_model.objective_function.expr + quadratic_penalty_change,
        #                                                                                        sense=pyomo.minimize)
        self.sub_persistent.set_objective(
            self.sub_persistent._pyomo_model.objective_function)
        self.sub_persistent._solver_model.update()

    def fix_flow_global(self):
        for key in self.flow_global.index:
            if not isinstance(self.flow_global.loc[key], pd.core.series.Series):
                self.sub_pyomo.flow_global[key].fix(self.flow_global.loc[key])
                self.sub_persistent.update_var(
                    self.sub_pyomo.flow_global[key])
            else:
                self.sub_pyomo.flow_global[key].fix(self.flow_global.loc[key,0])
                self.sub_persistent.update_var(
                    self.sub_pyomo.flow_global[key])

    def send(self):
        dest = self.pipes.keys()
        for k in dest:
            # prepare the message to be sent to neighbor k
            msg = message()
            msg.config(self.ID, k, self.flows_with_neighbor[k], self.rho,
                       self.lamda[self.lamda.index.isin(self.flows_with_neighbor[k].index)],
                       self.gapAll)
            print('stuck at sending to %d' % k)
            self.pipes[k].send(msg)
            print('sent to %d' % k)

    def recv(self, pollrounds=5):
        twait = self.admmopt.pollWaitingtime
        dest = list(self.pipes.keys())
        recvFlag = [0] * self.nneighbors
        arrived = 0  # number of arrived neighbors
        pollround = 0

        # keep receiving from nbor 1 to nbor K in round until nwait neighbors arrived
        while arrived < self.nwait and pollround < pollrounds:
            for i in range(len(dest)):
                k = dest[i]
                print('stuck at recv before poll abfrage')
                #if self.pipes[k].poll(0):
                print('stuck at recv after poll abfrage')
                while self.pipes[k].poll(twait):  # read from pipe until get the last message
                    self.recvmsg[k] = self.pipes[k].recv()
                    recvFlag[i] = 1
                    # print("Message received at %d from %d" % (self.ID, k))
            arrived = sum(recvFlag)
            pollround += 1

    def update_z(self):
        srcs = self.pipes.keys()
        flow_global_old = deepcopy(self.flow_global)
        for k in srcs:
            if k in self.recvmsg:
                if self.recvmsg[k].tID == self.ID:  # target is this Cluster
                    nborvar = self.recvmsg[k].fields  # nborvar['flow'], nborvar['convergeTable']
                    self.flow_global.loc[self.flow_global.index.isin(self.flows_with_neighbor[k].index)] = \
                        (self.lamda.loc[self.lamda.index.isin(self.flows_with_neighbor[k].index)] +
                         nborvar['lambda'] + self.flows_with_neighbor[k] * self.rho + nborvar['flow'] * nborvar['rho']) \
                        / (self.rho + nborvar['rho'])
                    print('z updated at %d using messages received from %d !' % (self.ID + 1, k + 1))
        # self.dualgap += [((self.flow_global - flow_global_old).abs()).max()[0]]
        self.dualgap += [self.rho * (np.sqrt(np.square(self.flow_global - flow_global_old).sum(axis=0)[0]))]
        # if np.sqrt(np.square(self.lamda).sum(axis=0)[0]) == 0:
        #     self.dualgap += [1]
        # else:
        #     self.dualgap += [self.rho * (np.sqrt(np.square(self.flow_global - flow_global_old).sum(axis=0)[0])) \
        #                     / (np.sqrt(np.square(self.lamda).sum(axis=0)[0]))]

    def update_y(self):
        self.lamda = self.lamda + self.rho * (self.flows_all.loc[:, [0]] - self.flow_global)

        #   # update rho and primal gap locally

    def update_rho(self,nu):
        # calculate and update primal gap first
        # primalgap_old = deepcopy(self.primalgap[-1])
        #self.primalgap += [((self.flows_all - self.flow_global).abs()).max()[0]]
        self.primalgap += [np.sqrt(np.square(self.flows_all - self.flow_global).sum(axis=0)[0])]
        # self.primalgap += [np.sqrt(np.square(self.flows_all - self.flow_global).sum(axis=0)[0]) \
        #                   / maximum(np.sqrt(np.square(self.flows_all).sum(axis=0)[0]),
        #                             np.sqrt(np.square(self.flow_global).sum(axis=0)[0]))]
        # (for residual balancing: https://arxiv.org/pdf/1704.06209.pdf) update tau
        # if 1 <= np.sqrt(self.admmopt.zeta ** -1 * self.primalgap[-1] / self.dualgap[-1]) < self.admmopt.tau_max:
        #     self.admmopt.tau = np.sqrt(self.admmopt.zeta ** -1 * self.primalgap[-1] / self.dualgap[-1])
        # elif self.admmopt.tau_max ** -1 < np.sqrt(self.admmopt.zeta ** -1 * self.primalgap[-1] / self.dualgap[-1]) < 1:
        #     self.admmopt.tau = np.sqrt(self.admmopt.zeta * self.dualgap[-1] / self.primalgap[-1])
        # else:
        #     self.admmopt.tau = self.admmopt.tau_max
        # update rho if necessary
        # if self.primalgap[-1] > self.admmopt.theta * primalgap_old:
        # if self.primalgap[-1] > self.admmopt.zeta * self.dualgap[-1]:
        #     self.rho = min(self.admmopt.rho_max, self.rho * self.admmopt.tau)
        # elif self.dualgap[-1] > self.admmopt.zeta ** -1 * self.primalgap[-1]:
        #     self.rho = self.rho / self.admmopt.tau
            # self.rho = minimum(self.rho, self.admmopt.rho_max)
        # if self.primalgap[-1] > self.admmopt.theta * primalgap_old:
        if nu <= 50:
            if self.primalgap[-1] > self.admmopt.mu * self.dualgap[-1]:
                self.rho = min(self.admmopt.rho_max, self.rho * self.admmopt.tau)
            elif self.dualgap[-1] > self.admmopt.mu * self.primalgap[-1]:
                self.rho = min(self.rho / self.admmopt.tau, self.admmopt.rho_max)
        # update local converge table
        self.ID
        len(self.gapAll)
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
        print(self.gapAll)
        if self.recvmsg is not None:
            for k in self.recvmsg:
                table = self.recvmsg[k].fields['convergeTable']
                print('table: '+str(table))
                self.gapAll = list(map(min, zip(self.gapAll, table)))
        # check if all local primal gaps < tolerance
        if max(self.gapAll) < self.admmopt.convergetol:
            dest = self.pipes.keys()
            for k in dest:
                self.pipes[k].close()
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
        self.beta_diff = 2  # weight for (Vi - Vj) of tie line
        self.beta_sum = 0.5  # weight for (Vi + Vj) of tie line
        self.rho_0 = 1 * 10 ** 4  # initial value for penalty rho, at the same order of initial cost function
        self.rho_max = 10  # upper bound for penalty rho
        self.tau_max = 1.5  # parameter for residual balancing of rho
        self.tau = 1.05  # multiplier for increasing rho
        self.zeta = 1  # parameter for residual balancing of rho
        self.theta = 0.99  # multiplier for determining whether to update rho
        self.mu = 10  # multiplier for determining whether to update rho
        self.init = 'flat'  # starting point
        self.ymax = 10 ** 16  # maximum y
        self.ymin = -10 ** 16  # minimum y
        self.pollWaitingtime = 0.001  # waiting time of receiving from one pipe
        self.nwaitPercent = 0.1  # waiting percentage of neighbors (0, 1]
        self.iterMaxlocal = 1000  # local maximum iteration
        self.convergetol = 5* 10 ** 2  # convergence criteria for maximum primal gap


#
class message(object):
    """ This class defines the message region i sends to/receives from j """

    def __init__(self):
        self.fID = 0  # source region ID
        self.tID = 0  # destination region ID
        self.fields = {
            'flow': None,
            'rho': None,
            'convergeTable': None}

    def config(self, f, t, var_flow, var_rho, var_lambda, gapAll):  # AVall and var are local variables of f region
        self.fID = f
        self.tID = t

        self.fields['flow'] = var_flow
        self.fields['rho'] = var_rho
        self.fields['lambda'] = var_lambda
        self.fields['convergeTable'] = gapAll
