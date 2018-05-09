.. module urbs


.. _eq-cost-func:

Objective function
^^^^^^^^^^^^^^^^^^

The variable total system cost :math:`\zeta` is calculated by the cost function. The cost function is the objective function of the optimization  model. Minimizing the value of the variable total system cost would give the most reasonable solution for the modelled energy system  The formula of the cost function expressed in mathematical notation is as following:

.. math::
    \zeta = \zeta_\text{inv} + \zeta_\text{fix} + \zeta_\text{var} + \zeta_\text{fuel} + \zeta_\text{rev} + \zeta_\text{pur} + \zeta_\text{startup}

The calculation of the variable total system cost is given in ``model.py`` by the following code fragment.  

.. literalinclude:: /../urbs/model.py
   :pyobject: obj_rule

The variable total system cost :math:`\zeta` is basically calculated by the summation of every type of total costs. As previously mentioned in section :ref:`sec-cost-types`, these cost types are : ``Investment``, ``Fix``, ``Variable``, ``Fuel``, ``Revenue``, ``Purchase``. The calculation of each single cost types are listed below.

Investment Costs
----------------

The variable investment costs :math:`\zeta_\text{inv}` represent the required annual expenses made, in the hope of future benefits. These expenses are made on every new investment. The possible investments of an energy system in this model are:

1. Additional throughput capacity for process technologies.
2. Additional power capacity for storage technologies and additional storage content capacity for storage technologies.
3. Additional power capacity for transmission technologies.

The calculation of total annual investment cost :math:`\zeta_\text{inv}` is expressed by the formula: 

.. math::

    \zeta_\text{inv} = 
    \sum_{\substack{v \in V\\ p \in P}} \hat{\kappa}_{vp} k_p^\text{inv} +
    \sum_{\substack{v \in V\\ s \in S}} \left( \hat{\kappa}_{vs}^\text{c} k_{vs}^\text{c,inv} + \hat{\kappa}_{vs}^\text{p} k_{vs}^\text{p,inv}\right) +
    \sum_{\substack{a \in A\\ f \in F}} \hat{\kappa}_{af} k_{af}^\text{inv}


Total annual investment cost is calculated by the sum of three main summands, these are the investment costs for processes, storages, and transmissions. 

1. The first summand of the formula calculates the required annual investment expenses to install the additional process capacity for every member of the set process tuples :math:`\forall p_v \in P_v`. Total process investment cost for all process tuples is defined by the sum of all possible annual process investment costs, which are calculated seperately for each process tuple ( :math:`p_v`, ``m.pro_tuples``) consisting of process :math:`p` in site :math:`v`. Annual process investment cost for a given process tuple :math:`p_v` is calculated by the product of the variable new process capacity ( :math:`\hat{\kappa}_{vp}`,``m.cap_pro_new``) and the parameter annualised process capacity investment cost ( :math:`k_{vp}^\text{inv}`, ``m.process_dict['inv-cost'][p] * m.process_dict['annuity-factor'][p]``). In mathematical notation this summand is expressed as:

.. math::
    \sum_{\substack{v \in V\\ p \in P}} \hat{\kappa}_{vp} k_p^\text{inv}

2. The second summand of the formula calculates the required investment expenses to install additional power output capacity and storage content capacity to storage technologies for every member of the set storage tuples ( :math:`\forall s_{vc} \in S_{vc}`). This summand consists of two products:
 * The first product calculates the required annual investment expenses to install an additional storage content capacity to a given storage tuple . This is calculated by the product of the variable new storage size ( :math:`\hat{\kappa}_{vs}^\text{c}`, ``cap_sto_c_new``) and the parameter annualised storage size investment costs ( :math:`k_{vs}^\text{c,inv}`, ``m.storage_dict['inv-cost-c'][s] * m.storage_dict['annuity-factor'][s]``).
 * The second product calculates the required annual investment expenses to install an additional power output capacity to a given storage tuple. This is calculated by the product of the variable new storage power ( :math:`\hat{\kappa}_{vs}^\text{p}`, ``cap_sto_p_new``) and the parameter annualised storage power investment costs ( :math:`k_{vs}^\text{p,inv}`, ``m.storage_dict['inv-cost-p'][s] * m.storage_dict['annuity-factor'][s]``).
 These two products for a given storage tuple are then added up. The calculation of investment costs for a given storage tuple is than repeated for every single storage tuple and summed up to calculate the total investment costs for storage technologies. In mathematical notation this summand is expressed as:

.. math::
    \sum_{\substack{v \in V\\ s \in S}} ( 
        \hat{\kappa}_{vs}^\text{c} k_{vs}^\text{c,inv} +
        \hat{\kappa}_{vs}^\text{p} k_{vs}^\text{p,inv})

3. The third and the last summand of the formula calculates the required investment expenses to install additional power capacity to transmission technologies for every member of the set transmission tuples :math:`\forall f_{ca} \in F_{ca}`. Total transmission investment cost for all transmission tuples is defined by the sum of all possible annual transmission investment costs, which are calculated seperately for each transmission tuple ( :math:`f_{ca}`). Annual transmission investment cost for a given transmission tuple is calculated by the product of the variable new transmission capacity ( :math:`\hat{\kappa}_{af}`, ``cap_tra_new``) and the parameter annualised transmission capacity investment costs ( :math:`k_{af}^\text{inv}`, ``m.transmission_dict['inv-cost'][t] * m.transmission_dict['annuity-factor'][t]``) for the given transmission tuple. In mathematical notation this summand is expressed as:

.. math:: 
    \sum_{\substack{a \in A\\ f \in F}} \hat{\kappa}_{af} k_{af}^\text{inv}

As mentioned above the variable investment costs :math:`\zeta_\text{inv}` is calculated by the sum of these 3 summands.

In script ``model.py`` the value of the total investment cost is calculated by the following code fragment:

::

    if cost_type == 'Invest':
        return m.costs[cost_type] == \
            sum(m.cap_pro_new[p] *
                m.process_dict['inv-cost'][p] *
                m.process_dict['annuity-factor'][p]
                for p in m.pro_tuples) + \
            sum(m.cap_tra_new[t] *
                m.transmission_dict['inv-cost'][t] *
                m.transmission_dict['annuity-factor'][t]
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p_new[s] *
                m.storage_dict['inv-cost-p'][s] *
                m.storage_dict['annuity-factor'][s] +
                m.cap_sto_c_new[s] *
                m.storage_dict['inv-cost-c'][s] *
                m.storage_dict['annuity-factor'][s]
                for s in m.sto_tuples)

Fix Costs
---------

The variable fix costs :math:`\zeta_\text{fix}` represents the total annual fixed costs for all used storage, process and transmission technologies. The possible fix costs of an energy system in this model can be divided into sections, these are:

1. Fix costs for process technologies
2. Fix costs for storage technologies
3. Fix costs for transmission technologies.

The calculation of total annual fix cost :math:`\zeta_\text{fix}` is expressed by the formula:

.. math::

	\zeta_\text{fix} = 
	\sum_{\substack{v \in V\\ p \in P}} \kappa_{vp} k_{vp}^\text{fix} +
	\sum_{\substack{v \in V\\ s \in S}} \left( \kappa_{vs}^\text{c} k_{vs}^\text{c,fix} + \kappa_{vs}^\text{p} k_{vs}^\text{p,fix} \right) +
	\sum_{\substack{a \in A\\ f \in F}} \kappa_{af} k_{af}^\text{fix}

Total annual fix cost :math:`\zeta_\text{fix}` is calculated by the sum of three main summands, these are the fix costs for process, storage and transmission technologies.

1. The first summand of the formula calculates the required annual fix cost to keep all the process technologies maintained. This is calculated for every member of the set process tuples :math:`\forall p_v \in P_v`. Total process fix cost for all process tuples is defined by the sum of all possible annual process fix costs, which are calculated seperately for each process tuple ( :math:`p_v`, ``m.pro_tuples``) consisting of process :math:`p` in site :math:`v`. Annual process fix cost for a given process tuple is calculated by the product of the variable total process capacity ( :math:`\kappa_{vp}`, ``cap_pro``) and process capacity fixed cost ( :math:`k_{vp}^\text{fix}`, ``m.process_dict['fix-cost'][p]``). In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ p \in P}} \kappa_{vp} k_{vp}^\text{fix}

2. The second summand of the formula calculates the required fix expenses to keep the power capacity and storage content capacity of storage technologies maintained. The present storage technologies comprise the members of the set storage tuples :math:`\forall s_{vc} \in S_{vc}`. This summand consists of two products:
 * The first product calculates the required annual fix expenses to keep the storage content capacity of a given storage tuple maintained.  This is calculated by the product of the variable total storage size ( :math:`\kappa_{vs}^\text{c}`, ``cap_sto_c``) and the parameter annual storage size fixed costs ( :math:`k_{vs}^\text{c,fix}`, ``m.storage_dict[s]['fix-cost-c']``).
 * The second product calculates the required annual fix expenses to keep the power capacity of a given storage tuple maintained. This is calculated by the product of the variable total storage power ( :math:`\kappa_{vs}^\text{p}`, ``cap_sto_p``) and the parameter annual storage power fixed costs (:math:`k_{vs}^\text{p,fix}`, ``m.storage_dict[s]['fix-cost-p']``).
 These two products for a given storage tuple are than added up. The calculation of fix costs for a storage tuple is then repeated for every single storage tuple and summed up to calculate the total fix costs for storage technologies. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ s \in S}} (\kappa_{vs}^\text{c} k_{vs}^\text{c,fix} + \kappa_{vs}^\text{p} k_{vs}^\text{p,fix})

3. The third and the last summand of the formula calculates the required fix expenses to keep the power capacity of transmission technologies maintained. The transmission technologies comprise the members of the set transmission tuples :math:`\forall f_{ca} \in F_{ca}`. Total transmission fix cost for all transmission tuples is defined by the sum of all possible annual transmission fix costs, which are calculated seperately for each transmission tuple :math:`f_{ca}`. Annual transmission fix cost for a given transmission tuple is calculated by the product of the variable total transmission capacity ( :math:`\kappa_{af}`, ``cap_tra``) and the parameter annual transmission capacity fixed costs ( :math:`k_{af}^\text{fix}`, ``m.transmission_dict[t]['fix-cost']``) for the given transmission tuple :math:`f_{ca}`. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{a \in A\\ f \in F}} \kappa_{af} k_{af}^\text{fix}

As mentioned above, the fix costs :math:`\zeta_\text{fix}` are calculated by the sum of these 3 summands.

In script ``model.py`` the value of the total fix cost is calculated by the following code fragment:

::

    elif cost_type == 'Fixed':
        return m.costs[cost_type] == \
            sum(m.cap_pro[p] * m.process_dict['fix-cost'][p]
                for p in m.pro_tuples) + \
            sum(m.cap_tra[t] * m.transmission_dict['fix-cost'][t]
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p[s] * m.storage_dict['fix-cost-p'][s] +
                m.cap_sto_c[s] * m.storage_dict['fix-cost-c'][s]
                for s in m.sto_tuples)


Variable Costs
--------------

.. math::

	\zeta_\text{var} =  w \sum_{t \in T_\text{m}} &\left( \sum_{\substack{v \in V\\ p \in P}} \tau_{vpt} k_{vp}^\text{var} + 
	\sum_{\substack{a \in a\\ f \in F}} \pi_{af}^\text{in} k_{af}^\text{var} +  
	\right.\nonumber \\
	&\left.\phantom{\Big(} % invisible left parenthesis for horizontal alignment
	\sum_{\substack{v \in V\\ s \in S}} \left[ 
	\epsilon_{vst}^\text{con} k_{vs}^\text{c,var} + \left(
	\epsilon_{vst}^\text{in} + \epsilon_{vst}^\text{out} 
	\right) k_{vs}^\text{p,var}
	\right] 
	\right)

::

    elif cost_type == 'Variable':
        return m.costs[cost_type] == \
            sum(m.tau_pro[(tm,) + p] * m.weight *
                m.process_dict['var-cost'][p]
                for tm in m.tm
                for p in m.pro_tuples) + \
            sum(m.e_tra_in[(tm,) + t] * m.weight *
                m.transmission_dict['var-cost'][t]
                for tm in m.tm
                for t in m.tra_tuples) + \
            sum(m.e_sto_con[(tm,) + s] * m.weight *
                m.storage_dict['var-cost-c'][s] +
                m.weight *
                (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) *
                m.storage_dict['var-cost-p'][s]
                for tm in m.tm
                for s in m.sto_tuples)

Fuel Costs
----------

The variable fuel costs :math:`\zeta_\text{fuel}` represents the total annual expenses that are required to be made to buy stock commodities :math:`c \in C_\text{stock}`. The calculation of the variable total annual fuel cost :math:`\zeta_\text{fuel}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{fuel} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{c \in C_\text{stock}} \rho_{vct} k_{vc}^\text{fuel}

The variable :math:`\zeta_\text{fuel}` is calculated by the sum of all possible annual fuel costs, defined by the combinations of commodity tuples of commodity type 'Stock'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Stock'}`) and timesteps ( :math:`\forall t \in T_m`). These annual fuel costs are calculated by the product of the following elements:

	* The parameter stock commodity fuel cost for a given stock commodity :math:`c` in a site :math:`v`.(:math:`k_{vc}^\text{fuel}`, ``m.commodity_dict['price'][c]``)
	* The variable stock commodity source term for a given stock commodity :math:`c` in a site :math:`v` at a timestep :math:`t` (:math:`\rho_{vct}`, ``e_co_stock``).
	* The variable weight (:math:`w`, ``weight``). 

In script ``model.py`` the value of the total fuel cost is calculated by the following code fragment:
::

    elif cost_type == 'Fuel':
        return m.costs[cost_type] == sum(
            m.e_co_stock[(tm,) + c] * m.weight *
            m.commodity_dict['price'][c]
            for tm in m.tm for c in m.com_tuples
            if c[1] in m.com_stock)


Revenue Costs
-------------

The variable revenue costs :math:`\zeta_\text{rev}` represents the total annual expenses that are required to be made to sell sell commodities :math:`c \in C_\text{sell}`. The calculation of the variable total annual revenue cost :math:`\zeta_\text{rev}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{rev} = 
	-w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{c \in C_\text{sell}} \varrho_{vct} k_{vct}^\text{bs}

The variable :math:`\zeta_\text{rev}` is calculated by the sum of all possible annual revenue costs, defined by the combinations of commodity tuples of commodity type 'Sell'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Sell'}`) and timesteps (:math:`\forall t \in T_m`). These annual revenue costs are calculated by the product of the following elements:

	* The parameter sell commodity sell cost for given sell commodity :math:`c` in a site :math:`v` (:math:`k_{vct}^\text{bs}`, ``buy_sell_price_dict[c[1], ][tm]``).
	* The variable sell commodity source term for a given sell commodity :math:`c` in a site :math:`v` at a timestep :math:`t` (:math:`\varrho_{vct}`, ``e_co_sell``).
	* The variable weight (:math:`w`, ``weight``).
	* Coefficient [-1].

Since this variable is an income for the energy system, it is multiplied by the value -1 to be able to express it in the cost function as a summand.
In script ``model.py`` the value of the total revenue cost is calculated by the following code fragment:
::
    elif cost_type == 'Revenue':
		sell_tuples = commodity_subset(m.com_tuples, m.com_sell)

		try:
			return m.costs[cost_type] == -sum(
				m.e_co_sell[(tm,) + c] * m.weight *
				m.buy_sell_price_dict[c[1], ][tm] *
				m.commodity_dict['price'][c]
				for tm in m.tm
				for c in sell_tuples)
		except KeyError:
			return m.costs[cost_type] == -sum(
				m.e_co_sell[(tm,) + c] * m.weight *
				m.buy_sell_price_dict[c[1]][tm] *
				m.commodity_dict['price'][c]
				for tm in m.tm
				for c in sell_tuples)


Purchase Costs
--------------

The variable purchase costs :math:`\zeta_\text{pur}` represents the total annual expenses that are required to be made to purchase buy commodities :math:`c \in C_\text{buy}`. The calculation of the variable total annual purchase cost :math:`\zeta_\text{pur}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{pur} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{c \in C_\text{buy}} \psi_{vct} k_{vct}^\text{bs}

The variable :math:`\zeta_\text{pur}` is calculated by the sum of all possible annual purchase costs, defined by the combinations of commodity tuples of commodity type 'Buy'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Buy'}`) and timesteps (:math:`\forall t \in T_m`). These annual purchase costs are calculated by the product of the following elements:

	* The parameter buy commodity buy cost for a given buy commodity :math:`c` in a site :math:`v` (:math:`k_{vct}^\text{bs}`, ``buy_sell_price_dict[c[1], ][tm]``).
	* The variable buy commodity source term for a given buy commodity :math:`c` in a site :math:`v` at a timestep :math:`t` ( :math:`\psi_{vct}`, ``e_co_buy``).
	* The variable weight ( :math:`w`, ``weight``).

In script ``model.py`` the value of the total purchase cost is calculated by the following code fragment:
::

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)

        try:
            return m.costs[cost_type] == sum(
                m.e_co_buy[(tm,) + c] * m.weight *
                m.buy_sell_price_dict[c[1], ][tm] *
                m.commodity_dict['price'][c]
                for tm in m.tm
                for c in buy_tuples)
        except KeyError:
            return m.costs[cost_type] == sum(
                m.e_co_buy[(tm,) + c] * m.weight *
                m.buy_sell_price_dict[c[1]][tm] *
                m.commodity_dict['price'][c]
                for tm in m.tm
                for c in buy_tuples)


Environmental Costs
-------------------

Environmental costs :math:`\zeta_\text{env}` represent the total annual taxes for created emissions/pollutions in form of environmental commodities. The total annual costs are calculated by summing the negative commodity balance :math:`\textrm{CB}` of all environmental commodities, multiplied by their respective price

.. math::

    \zeta_\text{env} = - 
    w \sum_{t\in T_\text{m}} \sum_{v\in V} \sum_{c \in C_\text{env}}
    \textrm{CB}(v,c,t)
    
In script ``model.py`` the value of the total environmental cost is calculated by the following code fragment:
::

    elif cost_type == 'Environmental':
        return m.costs[cost_type] == sum(
            - commodity_balance(m, tm, sit, com) *
            m.weight *
            m.commodity_dict['price'][(sit, com, com_type)]
            for tm in m.tm
            for sit, com, com_type in m.com_tuples
            if com in m.com_env)
