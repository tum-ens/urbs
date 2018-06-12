import math
import pyomo.core as pyomo
from .modelhelper import*

# Objective
def def_costs_rule(m, mode, cost_type):
    """Calculate total costs by cost type.

    Sums up process activity and capacity expansions
    and sums them in the cost types that are specified in the set
    m.cost_type. To change or add cost types, add/change entries
    there and modify the if/elif cases in this function accordingly.

    Cost types are
      - Investment costs for process power, storage power and
        storage capacity. They are multiplied by the annuity
        factors.
      - Fixed costs for process power, storage power and storage
        capacity.
      - Variables costs for usage of processes, storage and transmission.
      - Fuel costs for stock commodity purchase.

    """                                   
    
    tra,sto,dsm,Int = mode
    
    if cost_type == 'Invest':
        m.costs[cost_type] == \
            sum(m.cap_pro_new[p] *
                m.process_dict['inv-cost'][p] *
                m.process_dict['annuity-factor'][p]
				for p in m.pro_tuples_exp)
        if tra:
            """m.costs[cost_type] += \
				sum(m.cap_tra_new[t] *
					m.transmission_dict['inv-cost'][t] *
					m.transmission_dict['annuity-factor'][t]
					for t in m.tra_tuples_expansion)"""
        if sto:
            """m.costs[cost_type] += \
            	sum(m.cap_sto_p_new[s] *
					m.storage_dict['inv-cost-p'][s] *
					m.storage_dict['annuity-factor'][s] +
					m.cap_sto_c_new[s] *
					m.storage_dict['inv-cost-c'][s] *
					m.storage_dict['annuity-factor'][s]
					for s in m.sto_tuples_c_expansion.intersection(m.sto_tuples_p_expansion)) +\
				sum(m.cap_sto_p_new[s] *
					m.storage_dict['inv-cost-p'][s] *
					m.storage_dict['annuity-factor'][s] +
					m.storage_dict['inst-cap-c'][(s)] *
					m.storage_dict['inv-cost-c'][s] *
					m.storage_dict['annuity-factor'][s]
					for s in m.sto_tuples_p_expansion.difference(m.sto_tuples_c_expansion)) +\
				sum(m.storage_dict['inst-cap-p'][(s)] *
					m.storage_dict['inv-cost-p'][s] *
					m.storage_dict['annuity-factor'][s] +
					m.cap_sto_c_new[s] *
					m.storage_dict['inv-cost-c'][s] *
					m.storage_dict['annuity-factor'][s]
					for s in m.sto_tuples_c_expansion.difference(m.sto_tuples_p_expansion)) """
        return m.costs[cost_type]

    elif cost_type == 'Fixed':
        m.costs[cost_type] == \
            sum(m.cap_pro[p] * m.process_dict['fix-cost'][p]
                for p in m.pro_tuples_exp) + \
            sum(m.process_dict['inst-cap'][(p)] * m.process_dict['fix-cost'][p]
                for p in (m.pro_tuples-m.pro_tuples_expansion))
        if tra:
                    """sum(m.cap_tra[t] * m.transmission_dict['fix-cost'][t]
                        for t in m.tra_tuples) + \ """
        if sto:
                    """sum(m.cap_sto_p[s] * m.storage_dict['fix-cost-p'][s] +
                        m.cap_sto_c[s] * m.storage_dict['fix-cost-c'][s]
                        for s in m.sto_tuples_p_expansion.intersection(m.sto_tuples_c_expansion)) + \
                    sum(m.cap_sto_p[s] * m.storage_dict['fix-cost-p'][s] +
                        m.storage_dict['inst-cap-c'][(s)] * m.storage_dict['fix-cost-c'][s]
                        for s in m.sto_tuples_p_expansion.difference(m.sto_tuples_c_expansion)) + \
                    sum(m.storage_dict['inst-cap-p'][(s)] * m.storage_dict['fix-cost-p'][s] +
                        m.cap_sto_c[s] * m.storage_dict['fix-cost-c'][s]
                        for s in m.sto_tuples_c_expansion.difference(m.sto_tuples_p_expansion)) + \
                    sum(m.storage_dict['inst-cap-p'][(s)] * m.storage_dict['fix-cost-p'][s] +
                        m.storage_dict['inst-cap-c'][(s)] * m.storage_dict['fix-cost-c'][s]
                        for s in m.sto_tuples-m.sto_tuples_c_expansion-m.sto_tuples_p_expansion) """
        return m.costs[cost_type]

    elif cost_type == 'Variable':
        m.costs[cost_type] == \
            sum(m.tau_pro[(tm,) + p] * m.dt * m.weight *
                m.process_dict['var-cost'][p]
                for tm in m.tm
                for p in m.pro_tuples)
        if tra:
                   """ sum(m.e_tra_in[(tm,) + t] * m.dt * m.weight *
                        m.transmission_dict['var-cost'][t]
                        for tm in m.tm
                        for t in m.tra_tuples) """
        if sto:               
                    """sum(m.e_sto_con[(tm,) + s] * m.weight *
                        m.storage_dict['var-cost-c'][s] +
                        m.dt * m.weight *
                        (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) *
                        m.storage_dict['var-cost-p'][s]
                        for tm in m.tm
                        for s in m.sto_tuples) """

        return m.costs[cost_type]

    elif cost_type == 'Fuel':
        return m.costs[cost_type] == sum(
            m.e_co_stock[(tm,) + c] * m.dt * m.weight *
            m.commodity_dict['price'][c]
            for tm in m.tm for c in m.com_tuples
            if c[1] in m.com_stock)

    elif cost_type == 'Revenue':
        sell_tuples = commodity_subset(m.com_tuples, m.com_sell)

        try:
            return m.costs[cost_type] == -sum(
                m.e_co_sell[(tm,) + c] * m.weight * m.dt *
                m.buy_sell_price_dict[c[1], ][tm] *
                m.commodity_dict['price'][c]
                for tm in m.tm
                for c in sell_tuples)
        except KeyError:
            return m.costs[cost_type] == -sum(
                m.e_co_sell[(tm,) + c] * m.weight * m.dt *
                m.buy_sell_price_dict[c[1]][tm] *
                m.commodity_dict['price'][c]
                for tm in m.tm
                for c in sell_tuples)

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)

        try:
            return m.costs[cost_type] == sum(
                m.e_co_buy[(tm,) + c] * m.weight * m.dt *
                m.buy_sell_price_dict[c[1], ][tm] *
                m.commodity_dict['price'][c]
                for tm in m.tm
                for c in buy_tuples)
        except KeyError:
            return m.costs[cost_type] == sum(
                m.e_co_buy[(tm,) + c] * m.weight * m.dt *
                m.buy_sell_price_dict[c[1]][tm] *
                m.commodity_dict['price'][c]
                for tm in m.tm
                for c in buy_tuples)

    elif cost_type == 'Environmental':
        return m.costs[cost_type] == sum(
            - commodity_balance(m, tm, sit, com) *
            m.weight * m.dt *
            m.commodity_dict['price'][(sit, com, com_type)]
            for tm in m.tm
            for sit, com, com_type in m.com_tuples
            if com in m.com_env)

    else:
        raise NotImplementedError("Unknown cost type.")


def obj_rule(m):
    return pyomo.summation(m.costs)
