from coopr.opt.base import SolverFactory
from coopr.pyomo import *
from datetime import datetime
from numpy import arange
import os
import pandas as pd
import pdb


def create_model(filename, timesteps):
    
    m = ConcreteModel()
    m.name = 'URPS'
    m.settings = {
        'dateformat': '%Y%m%dT%H%M%S',
        'basename': os.path.basename(os.path.splitext(filename)[0]),
        'timesteps': timesteps,
        }        
    m.created = datetime.now().strftime(m.settings['dateformat'])
    
    # Preparations
    # ============
    # Excel import
    # use Pandas DataFrames instead of Pyomo parameters for entity
    # attributes. Syntax to access a value:
    #
    #     m.process.loc[pro, coin, cout][attribute]
    #
    xls = pd.ExcelFile(filename)
    m.site = xls.parse('Site', index_col=[0])
    m.commodity = xls.parse('Commodity', index_col=[0,1,2])
    m.process = xls.parse('Process', index_col=[0,1,2])
    m.transmission = xls.parse('Transmission', index_col=[0,1,2])
    m.storage = xls.parse('Storage', index_col=[0,1])
    m.demand = xls.parse('Demand', index_col=[0]) 
    m.supim = xls.parse('SupIm', index_col=[0])
    
    # derive annuity factor for process and storage
    m.process['annuity_factor'] = annuity_factor(m.process['depreciation'], m.process['wacc'])
    m.transmission['annuity_factor'] = annuity_factor(m.transmission['depreciation'], m.transmission['wacc'])
    m.storage['annuity_factor'] = annuity_factor(m.storage['depreciation'], m.storage['wacc'])
      
    # Sets
    # ====
    # Syntax: m.{name} = Set({domain}, initialize={values})
    # where name: set name
    #       domain: set domain for tuple sets, a cartesian set product
    #       values: set values, a list or array of element tuples
    m.t = Set(initialize=m.settings['timesteps'])
    m.tm = Set(within=m.t, initialize=m.settings['timesteps'][1:])
    m.sit = Set(initialize=m.site.index.levels[0])
    m.com = Set(initialize=m.commodity.index.levels[1])
    m.com_type = Set(initialize=m.commodity.index.levels[2])
    m.pro = Set(initialize=m.process.index.levels[0])
    m.sto = Set(initialize=m.storage.index.levels[0])
    m.cost_type = Set(initialize=['Inv', 'Fix', 'Var', 'Fuel'])

    # sets of existing tuples:
    # co_tuples = [('Coal', 'Stock'), ('Wind', 'SupIm'), ('ElecAC', 'Demand')...]
    # pro_tuples = [('pp', 'Coal', 'ElecAC'), ('wt', 'Wind', 'ElecAC')...]
    # sto_tuples = [('bat', 'ElecDC'), ('pst', 'ElecAC')...]
    m.co_tuples = Set(within=m.sit*m.com*m.com_type, initialize=m.commodity.index)  
    m.pro_tuples = Set(within=m.sit*m.pro*m.com*m.com, initialize=m.process.index)
    m.tra_tuples = Set(within=m.sit*m.sit*m.com, initialize=m.transport.index)
    m.sto_tuples = Set(within=m.sit*m.sto*m.com, initialize=m.storage.index)
    
    # subsets of commodities by type
    # for shorter equations that apply to only one commodity type
    m.com_supim = Set(within=m.com, initialize=(c[0] for c in m.com_tuples if c[1] == 'SupIm'))
    m.com_stock = Set(within=m.com, initialize=(c[0] for c in m.com_tuples if c[1] == 'Stock'))
    m.com_demand = Set(within=m.com, initialize=(c[0] for c in m.com_tuples if c[1] == 'Demand'))
    
    # Parameters
    # ==========
    # for model entities (commodity, process, storage) no Pyomo parames
    # are needed, just use the DataFrames m.commodity, m.process and
    # m.storage directly.
    # Syntax: m.{name} = Param({domain}, initialize={values})
    # where name: param name
    #       domain: one or multiple model sets; empty for scalar parameters
    #       values: dict of parameter values, addressed by elements of domain sets
    m.weight = Param(initialize=float(8760) / len(m.t))
 
    # Variables
    # =========
    # listed alphabetically
    # Syntax: m.{name} = Var({domain}, within={range})
    # where name: variable name
    #       domain: variable domain, consisting of one or multiple sets
    #       range: variable values, like Binary, Integer, NonNegativeReals
    m.cap_pro = Var(m.pro_tuples, within=NonNegativeReals)
    m.cap_pro_new = Var(m.pro_tuples, within=NonNegativeReals)
    m.cap_sto_c = Var(m.sto_tuples, within=NonNegativeReals)
    m.cap_sto_c_new = Var(m.sto_tuples, within=NonNegativeReals)
    m.cap_sto_p = Var(m.sto_tuples, within=NonNegativeReals)
    m.cap_sto_p_new = Var(m.sto_tuples, within=NonNegativeReals)
    m.co2_pro_out = Var(m.tm, m.pro_tuples, within=NonNegativeReals)
    m.costs = Var(m.cost_type, within=NonNegativeReals)
    m.e_pro_in = Var(m.tm, m.pro_tuples, within=NonNegativeReals)
    m.e_pro_out = Var(m.tm, m.pro_tuples, within=NonNegativeReals)
    m.e_sto_in = Var(m.tm, m.sto_tuples, within=NonNegativeReals)
    m.e_sto_out = Var(m.tm, m.sto_tuples, within=NonNegativeReals)
    m.e_sto_con = Var(m.t, m.sto_tuples, within=NonNegativeReals)
    
    # Equation definition
    # ===================
    # listed by topic. All equations except the Objective function are 
    # of type Constraint, although there are two semantics for those, 
    # indicated by the name prefix (def, res).
    #  - def: definition, usually equations, defining variable values
    #  - res: restriction, usually inequalities, limiting variable values
    # topics
    #  - commodity
    #  - process
    #  - storage
    #  - emissions
    #  - costs
    
    # commodity
    def res_demand_rule(m, tm, com, com_type):
        if co not in m.com_demand:
            return Constraint.Skip
        else:
            provided_energy = - commodity_balance(m, tm, com)
            return provided_energy >= \
                   m.demand.loc[tm][com] * \
                   m.commodity.loc[com, com_type]['peak']
    
    def res_stock_hour_rule(m, tm, com, com_type):
        if com not in m.com_stock:
            return Constraint.Skip
        else:
            # calculate total consumption of commodity co in timestep tm
            total_consumption = commodity_balance(m, tm, com)                
            return total_consumption <= m.commodity.loc[com, com_type]['maxperhour']
        

    def res_stock_total_rule(m, com, com_type):
        if com not in m.com_stock:
            return Constraint.Skip
        else:
            # calculate total consumption of commodity co
            total_consumption = 0
            for tm in m.tm:
                total_consumption += commodity_balance(m, tm, com)                
             
            return total_consumption <= m.commodity.loc[com, com_type]['max']

            
    # process
    def def_process_capacity_rule(m, tm, pro, coin, cout):
        return m.cap_pro[pro,coin,cout] == \
               m.cap_pro_new[pro,coin,cout] + \
               m.process.loc[pro,coin,cout]['inst-cap']
                                      
    def def_process_output_rule(m, tm, pro, coin, cout):
        return m.e_pro_out[tm, pro, coin, cout] == \
               m.e_pro_in[tm, pro, coin, cout] * \
               m.process.loc[pro, coin, cout]['eff']

    def def_intermittent_supply_rule(m, tm, pro, coin, cout):
        if coin in m.com_supim:
            return m.e_pro_in[tm, pro, coin, cout] == \
                   m.cap_pro[pro, coin, cout] * m.supim.loc[tm][coin]
        else:
            return Constraint.Skip
        
    def def_co2_emissions_rule(m, tm, pro, coin, cout):
        return m.co2_pro_out[tm, pro, coin, cout] == \
               m.e_pro_in[tm, pro, coin, cout] * \
               m.process.loc[pro, coin, cout]['co2'] * \
               m.weight
        
    def res_process_output_by_capacity_rule(m, tm, pro, coin, cout):
        return m.e_pro_out[tm, pro, coin, cout] <= m.cap_pro[pro, coin, cout]
        
    def res_process_capacity_rule(m, pro, coin, cout):
        return (m.process.loc[pro, coin, cout]['cap-lo'],
                m.cap_pro[pro, coin, cout],
                m.process.loc[pro, coin, cout]['cap-up'])
    
    # storage
    def def_storage_state_rule(m, t, sto, com):
        return m.e_sto_con[t, sto, com] == \
               m.e_sto_con[t-1, sto, com] + \
               m.e_sto_in[t, sto, com] * m.storage.loc[sto, com]['eff-in'] - \
               m.e_sto_out[t, sto, com] / m.storage.loc[sto, com]['eff-out']
    
    def def_storage_power_rule(m, sto, com):
        return m.cap_sto_p[sto, com] == \
               m.cap_sto_p_new[sto, com] + \
               m.storage.loc[sto, com]['inst-cap-p']

    def def_storage_capacity_rule(m, sto, com):
        return m.cap_sto_c[sto, com] == \
               m.cap_sto_c_new[sto, com] + \
               m.storage.loc[sto, com]['inst-cap-p']

    def res_storage_input_by_power_rule(m, t, sto, com):
        return m.e_sto_in[t, sto, com] <= m.cap_sto_p[sto, com]
        
    def res_storage_output_by_power_rule(m, t, sto, co):
        return m.e_sto_out[t, sto, co] <= m.cap_sto_p[sto, co]
        
    def res_storage_state_by_capacity_rule(m, t, sto, com):
        return m.e_sto_con[t, sto, com] <= m.cap_sto_c[sto, com]
               
    def res_storage_power_rule(m, sto, com):
        return (m.storage.loc[sto, com]['cap-lo-p'],
                m.cap_sto_p[sto, com],
                m.storage.loc[sto, com]['cap-up-p'])
        
    def res_storage_capacity_rule(m, sto, com):
        return (m.storage.loc[sto, com]['cap-lo-c'],
                m.cap_sto_c[sto, com],
                m.storage.loc[sto, com]['cap-up-c'])
                
    def res_initial_and_final_storage_state_rule(m, t, sto, com):
        if t == m.t[1]: # first timestep (Pyomo uses 1-based indexing)
            return m.e_sto_con[t, sto, com] == \
                   m.cap_sto_c[sto, com] * \
                   m.storage.loc[sto, com]['init']
        elif t == m.t[-1]: # last timestep
            return m.e_sto_con[t, sto, com] >= \
                   m.cap_sto_c[sto, com] * \
                   m.storage.loc[sto, com]['init']
        else:
            return Constraint.Skip
    
    # emissions
    def res_co2_emission_rule(m):
        return summation(m.co2_pro_out) <= m.commodity.loc['CO2','Env']['max']
    
    # costs
    def def_costs_rule(m, cost_type):
        """ calculate total costs by cost type
        
        This functions sums up process activity and capacity expansions
        and sums them in the cost types that are specified in the set
        m.cost_type. To change or add cost types, add/change entries 
        there and modify the if/elif cases in this function accordingly.
        
        Cost types are
        
          - Investment costs for process power, storage power and 
            storage capacity. They are multiplied by the annuity 
            factors, which in turn are derived from the attributes 
            'depreciation' and 'wacc'.
            
          - Fixed costs for process power, storage power and storage
            capacity.
        """
        if cost_type == 'Inv':
            return m.costs['Inv'] == \
                sum(m.cap_pro_new[p] * 
                    m.process.loc[p]['inv-cost'] * 
                    m.process.loc[p]['annuity_factor'] 
                    for p in m.pro_tuples) + \
                sum(m.cap_sto_p_new[s] * 
                    m.storage.loc[s]['inv-cost-p'] * 
                    m.storage.loc[s]['annuity_factor'] +
                    m.cap_sto_c_new[s] * 
                    m.storage.loc[s]['inv-cost-c'] * 
                    m.storage.loc[s]['annuity_factor'] 
                    for s in m.sto_tuples)
                
        elif cost_type == 'Fix':
            return m.costs['Fix'] == \
                sum(m.cap_pro[p] * m.process.loc[p]['fix-cost'] 
                    for p in m.pro_tuples) + \
                sum(m.cap_sto_p[s] * m.storage.loc[s]['fix-cost-p'] +
                    m.cap_sto_c[s] * m.storage.loc[s]['fix-cost-c'] 
                    for s in m.sto_tuples)
                
        elif cost_type == 'Var':
            return m.costs['Var'] == \
                sum(m.e_pro_out[(tm,) + p] * 
                    m.process.loc[p]['var-cost'] * 
                    m.weight 
                    for tm in m.tm for p in m.pro_tuples) + \
                sum(m.e_sto_con[(tm,) + s] * 
                    m.storage.loc[s]['var-cost-c'] * m.weight +
                    (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) * 
                    m.storage.loc[s]['var-cost-p'] * m.weight
                    for tm in m.tm for s in m.sto_tuples)
            
        elif cost_type == 'Fuel':
            return m.costs['Fuel'] == \
                sum(m.e_pro_in[p] * m.commodity[c]['price'] * m.weight 
                    for p in m.pro_tuples 
                    for c in m.com_tuples 
                    if c[1] == p[1])
            
        else:
            raise NotImplementedError("Unknown cost type!")
            
    def obj_rule(m):
        return summation(m.costs)
    
    
    # Equation declaration
    # ====================
    # declarations connect rule functions to the model, specifying
    # the model sets for which the constraints are enforced
    
    # commodity
    m.res_demand = Constraint(m.tm, m.com_tuples)
    m.res_stock_hour = Constraint(m.tm, m.com_tuples)
    m.res_stock_total = Constraint(m.com_tuples)
    
    # process
    m.def_process_capacity = Constraint(m.tm, m.pro_tuples)
    m.def_process_output = Constraint(m.tm, m.pro_tuples)
    m.def_intermittent_supply = Constraint(m.tm, m.pro_tuples)
    m.def_co2_emissions = Constraint(m.tm, m.pro_tuples)
    m.res_process_output_by_capacity = Constraint(m.tm, m.pro_tuples)
    m.res_process_capacity = Constraint(m.pro_tuples)
    
    # storage 
    m.def_storage_state = Constraint(m.tm, m.sto_tuples)
    m.def_storage_power = Constraint(m.sto_tuples)
    m.def_storage_capacity = Constraint(m.sto_tuples)
    m.res_storage_input_by_power = Constraint(m.tm, m.sto_tuples)
    m.res_storage_output_by_power = Constraint(m.tm, m.sto_tuples)
    m.res_storage_state_by_capacity = Constraint(m.t, m.sto_tuples)
    m.res_storage_power = Constraint(m.sto_tuples)
    m.res_storage_capacity = Constraint(m.sto_tuples)    
    m.res_initial_and_final_storage_state = Constraint(m.t, m.sto_tuples)
    
    # emissions
    m.res_co2_emission = Constraint()

    # costs
    m.def_costs = Constraint(m.cost_type)
    m.obj = Objective(sense=minimize)    
    
    return m


    
def annuity_factor(n, i):
    """ return annuity factor
    
    Evaluates the annuity factor formula for depreciation duration
    and interest rate. Works also well for equally sized numpy arrays 
    of values for n and i.
    Args:
        n: depreciation period (years)
        i: interest rate (percent, e.g. 0.06 means 6 %)
        
    Returns:
        Value of the expression 
            (1+i)**n * i / ((1+i)**n - 1)
            
    """
    return (1+i)**n * i / ((1+i)**n - 1)


def commodity_balance(m, tm, com):
    """ calculate commodity balance at given timestep.
    
    For a given commodity co and timestep tm, calculate the balance of
    consumed (to process/storage, counts positive) and provided (from
    process/storage, counts negative) energy. Used as helper function 
    in create_model for constraints on demand and stock commodities.
    
    Args:
        m: the model object
        tm: the timestep
        co: the commodity
        
    Returns
        balance: net value of consumed (+) or provided (-) energy
    
    """
    balance = 0
    for p in m.pro_tuples:
        if p[1] == com:
            # usage as input for process increases balance
            balance += m.e_pro_in[(tm,)+p]
        if p[2] == com:
            # output from processes decreases balance
            balance -= m.e_pro_out[(tm,)+p]
    for s in m.sto_tuples:
        # usage as input for storage increases consumption
        # output from storage decreases consumption
        if s[1] == com:
            balance += m.e_sto_in[(tm,)+s]
            balance -= m.e_sto_out[(tm,)+s]
    return balance
