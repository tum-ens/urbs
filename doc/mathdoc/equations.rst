.. module:: urbs

Equations
=========

Cost Function
^^^^^^^^^^^^^

The variable total system cost :math:`\zeta` is calculated by the cost function. The cost function is the objective function of the optimization  model. Minimizing the value of the variable total system cost would give the most reasonable solution for the modelled energy system  The formula of the cost function expressed in mathematical notation is as following:

.. math::

	\zeta = \zeta_\text{inv} + \zeta_\text{fix} + \zeta_\text{var} + \zeta_\text{fuel} + \zeta_\text{rev} + \zeta_\text{pur} + \zeta_\text{startup}

The calculation of the variable total system cost is given in ``urbs.py`` by the following code fragment.  

::

	def obj_rule(m):
		return pyomo.summation(m.costs)

The variable total system cost :math:`\zeta` is basically calculated by the summation of every type of total costs. As previously mentioned on `Cost Types`_ these cost types are : ``Investment``, ``Fix``, ``Variable``, ``Fuel``, ``Revenue``, ``Purchase``. The calculation of each single cost types are listed below.

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

1. The first summand of the formula calculates the required annual investment expenses to install the additional process capacity for every member of the set process tuples :math:`\forall p_v \in P_v`. Total process investment cost for all process tuples is defined by the sum of all possible annual process investment costs, which are calculated seperately for each process tuple ( :math:`p_v`, ``m.pro_tuples``) consisting of process :math:`p` in site :math:`v`. Annual process investment cost for a given process tuple :math:`p_v` is calculated by the product of the variable new process capacity ( :math:`\hat{\kappa}_{vp}`,``m.cap_pro_new``) and the parameter annualised process capacity investment cost ( :math:`k_{vp}^\text{inv}`, ``m.process.loc[p]['inv-cost'] * m.process.loc[p]['annuity-factor']``). In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ p \in P}} \hat{\kappa}_{vp} k_p^\text{inv}

2. The second summand of the formula calculates the required investment expenses to install additional power output capacity and storage content capacity to storage technologies for every member of the set storage tuples ( :math:`\forall s_{vc} \in S_{vc}`). This summand consists of two products:
	* The first product calculates the required annual investment expenses to install an additional storage content capacity to a given storage tuple . This is calculated by the product of the variable new storage size ( :math:`\hat{\kappa}_{vs}^\text{c}`, ``cap_sto_c_new``) and the parameter annualised storage size investment costs ( :math:`k_{vs}^\text{c,inv}`, ``m.storage.loc[s]['inv-cost-c'] * m.storage.loc[s]['annuity-factor']``).
	* The second product calculates the required annual investment expenses to install an additional power output capacity to a given storage tuple. This is calculated by the product of the variable new storage power ( :math:`\hat{\kappa}_{vs}^\text{p}`, ``cap_sto_p_new``) and the parameter annualised storage power investment costs ( :math:`k_{vs}^\text{p,inv}`, ``m.storage.loc[s]['inv-cost-p'] * m.storage.loc[s]['annuity-factor']``).

   These two products for a given storage tuple are than added up. The calculation of investment costs for a given storage tuple is than repeated for every single storage tuple and summed up to calculate the total investment costs for storage technologies. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ s \in S}} ( \hat{\kappa}_{vs}^\text{c} k_{vs}^\text{c,inv} + \hat{\kappa}_{vs}^\text{p} k_{vs}^\text{p,inv})

3. The third and the last summand of the formula calculates the required investment expenses to install additional power capacity to transmission technologies for every member of the set transmission tuples :math:`\forall f_{ca} \in F_{ca}`. Total transmission investment cost for all transmission tuples is defined by the sum of all possible annual transmission investment costs, which are calculated seperately for each transmission tuple ( :math:`f_{ca}`). Annual transmission investment cost for a given transmission tuple is calculated by the product of the variable new transmission capacity ( :math:`\hat{\kappa}_{af}`, ``cap_tra_new``) and the parameter annualised transmission capacity investment costs ( :math:`k_{af}^\text{inv}`, ``m.transmission.loc[t]['inv-cost'] * m.transmission.loc[t]['annuity-factor']``) for the given transmission tuple. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{a \in A\\ f \in F}} \hat{\kappa}_{af} k_{af}^\text{inv}

As mentioned above the variable investment costs :math:`\zeta_\text{inv}` is calculated by the sum of these 3 summands.

In script ``urbs.py`` the value of the total investment cost is calculated by the following code fragment:

::

    if cost_type == 'Inv':
        return m.costs['Inv'] == \
            sum(m.cap_pro_new[p] *
                m.process.loc[p]['inv-cost'] *
                m.process.loc[p]['annuity-factor']
                for p in m.pro_tuples) + \
            sum(m.cap_tra_new[t] *
                m.transmission.loc[t]['inv-cost'] *
                m.transmission.loc[t]['annuity-factor']
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p_new[s] *
                m.storage.loc[s]['inv-cost-p'] *
                m.storage.loc[s]['annuity-factor'] +
                m.cap_sto_c_new[s] *
                m.storage.loc[s]['inv-cost-c'] *
                m.storage.loc[s]['annuity-factor']
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

1. The first summand of the formula calculates the required annual fix cost to keep all the process technologies maintained. This is calculated for every member of the set process tuples :math:`\forall p_v \in P_v`. Total process fix cost for all process tuples is defined by the sum of all possible annual process fix costs, which are calculated seperately for each process tuple ( :math:`p_v`, ``m.pro_tuples``) consisting of process :math:`p` in site :math:`v`. Annual process fix cost for a given process tuple is calculated by the product of the variable total process capacity ( :math:`\kappa_{vp}`, ``cap_pro``) and process capacity fixed cost ( :math:`k_{vp}^\text{fix}`, ``m.process.loc[p]['fix-cost']``). In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ p \in P}} \kappa_{vp} k_{vp}^\text{fix}

2. The second summand of the formula calculates the required fix expenses to keep the power capacity and storage content capacity of storage technologies maintained. The present storage technologies comprise the members of the set storage tuples :math:`\forall s_{vc} \in S_{vc}`. This summand consists of two products:
	* The first product calculates the required annual fix expenses to keep the storage content capacity of a given storage tuple maintained.  This is calculated by the product of the variable total storage size ( :math:`\kappa_{vs}^\text{c}`, ``cap_sto_c``) and the parameter annual storage size fixed costs ( :math:`k_{vs}^\text{c,fix}`, ``m.storage.loc[s]['fix-cost-c']``).
	* The second product calculates the required annual fix expenses to keep the power capacity of a given storage tuple maintained. This is calculated by the product of the variable total storage power ( :math:`\kappa_{vs}^\text{p}`, ``cap_sto_p``) and the parameter annual storage power fixed costs (:math:`k_{vs}^\text{p,fix}`, ``m.storage.loc[s]['fix-cost-p']``).

   These two products for a given storage tuple are than added up. The calculation of fix costs for a storage tuple is then repeated for every single storage tuple and summed up to calculate the total fix costs for storage technologies. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ s \in S}} (\kappa_{vs}^\text{c} k_{vs}^\text{c,fix} + \kappa_{vs}^\text{p} k_{vs}^\text{p,fix})

3. The third and the last summand of the formula calculates the required fix expenses to keep the power capacity of transmission technologies maintained. The transmission technologies comprise the members of the set transmission tuples :math:`\forall f_{ca} \in F_{ca}`. Total transmission fix cost for all transmission tuples is defined by the sum of all possible annual transmission fix costs, which are calculated seperately for each transmission tuple :math:`f_{ca}`. Annual transmission fix cost for a given transmission tuple is calculated by the product of the variable total transmission capacity ( :math:`\kappa_{af}`, ``cap_tra``) and the parameter annual transmission capacity fixed costs ( :math:`k_{af}^\text{fix}`, ``m.transmission.loc[t]['fix-cost']``) for the given transmission tuple :math:`f_{ca}`. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{a \in A\\ f \in F}} \kappa_{af} k_{af}^\text{fix}

As mentioned above the variable fix costs :math:`\zeta_\text{fix}` is calculated by the sum of these 3 summands.

In script ``urbs.py`` the value of the total fix cost is calculated by the following code fragment:

::

    elif cost_type == 'Fix':
        return m.costs['Fix'] == \
            sum(m.cap_pro[p] * m.process.loc[p]['fix-cost']
                for p in m.pro_tuples) + \
            sum(m.cap_tra[t] * m.transmission.loc[t]['fix-cost']
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p[s] * m.storage.loc[s]['fix-cost-p'] +
                m.cap_sto_c[s] * m.storage.loc[s]['fix-cost-c']
                for s in m.sto_tuples)


Variable Costs
--------------

.. math::

	\zeta_\text{var} =  w \sum_{t \in T_\text{m}} &\left( \sum_{\substack{v \in V\\ p \in P}} \tau_{vpt} k_{vp}^\text{var} \Delta t + 
	\sum_{\substack{a \in a\\ f \in F}} \pi_{af}^\text{in} k_{af}^\text{var} \Delta t +  
	\right.\nonumber \\
	&\left.\phantom{\Big(} % invisible left parenthesis for horizontal alignment
	\sum_{\substack{v \in V\\ s \in S}} \left[ 
	\epsilon_{vst}^\text{con} k_{vs}^\text{c,var} + \left(
	\epsilon_{vst}^\text{in} + \epsilon_{vst}^\text{out} 
	\right) k_{vs}^\text{p,var} \Delta t 
	\right] 
	\right)

::

    elif cost_type == 'Var':
        return m.costs['Var'] == \
            sum(m.tau_pro[(tm,) + p] * m.dt *
                m.process.loc[p]['var-cost'] *
                m.weight
                for tm in m.tm for p in m.pro_tuples) + \
            sum(m.e_tra_in[(tm,) + t] * m.dt *
                m.transmission.loc[t]['var-cost'] *
                m.weight
                for tm in m.tm for t in m.tra_tuples) + \
            sum(m.e_sto_con[(tm,) + s] *
                m.storage.loc[s]['var-cost-c'] * m.weight +
                (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) * m.dt *
                m.storage.loc[s]['var-cost-p'] * m.weight
                for tm in m.tm for s in m.sto_tuples)


Fuel Costs
----------

The variable fuel costs :math:`\zeta_\text{fuel}` represents the total annual expenses that are required to be made to buy stock commodities :math:`c \in C_\text{stock}`. The calculation of the variable total annual fuel cost :math:`\zeta_\text{fuel}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{fuel} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{stock}}} \rho_{vct} k_{vc}^\text{fuel} \Delta t

The variable :math:`\zeta_\text{fuel}` is calculated by the sum of all possible annual fuel costs, defined by the combinations of commodity tuples of commodity type 'Stock'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Stock'}`) and timesteps( :math:`\forall t \in T_m`). These annual fuel costs are calculated by the product of the following elements:

	* The parameter stock commodity fuel cost for a given stock commodity :math:`c` in a site :math:`v`.( :math:`k_{vc}^\text{fuel}`, ``m.commodity.loc[c]['price']``)
	* The variable stock commodity source term for a given stock commodity :math:`c` in a site :math:`v` at a timestep :math:`t`.( :math:`\rho_{vct}`, ``e_co_stock``)
	* The variable timestep duration.( :math:`\Delta t`, ``dt``)
	* The variable weight.( :math:`w`, ``weight``)

In script ``urbs.py`` the value of the total fuel cost is calculated by the following code fragment:
::

    elif cost_type == 'Fuel':
        return m.costs['Fuel'] == sum(
            m.e_co_stock[(tm,) + c] * m.dt *
            m.commodity.loc[c]['price'] *
            m.weight
            for tm in m.tm for c in m.com_tuples
            if c[1] in m.com_stock)


Revenue Costs
-------------

The variable revenue costs :math:`\zeta_\text{rev}` represents the total annual expenses that are required to be made to sell sell commodities :math:`c \in C_\text{sell}`. The calculation of the variable total annual revenue cost :math:`\zeta_\text{rev}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{rev} = 
	-w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{sell}}} \varrho_{vct} k_{vct}^\text{bs} \Delta t

The variable :math:`\zeta_\text{rev}` is calculated by the sum of all possible annual revenue costs, defined by the combinations of commodity tuples of commodity type 'Sell'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Sell'}`) and timesteps (:math:`\forall t \in T_m`). These annual revenue costs are calculated by the product of the following elements:

	* The parameter sell commodity sell cost for given sell commodity :math:`c` in a site :math:`v`.( :math:`k_{vct}^\text{bs}`, ``com_prices[c].loc[tm]`` )
	* The variable sell commodity source term for a given sell commodity :math:`c` in a site :math:`v` at a timestep :math:`t`.( :math:`\varrho_{vct}`, ``e_co_sell``)
	* The variable timestep duration.( :math:`\Delta t`, ``dt``)
	* The variable weight.( :math:`w`, ``weight``)
	* Coefficient [-1].

Since this variable is an income for the energy system, it is multiplied by the value -1 to be able to express it in the cost function as a summand.
In script ``urbs.py`` the value of the total revenue cost is calculated by the following code fragment:
::

    elif cost_type == 'Revenue':
        sell_tuples = commodity_subset(m.com_tuples, m.com_sell)
        com_prices = get_com_price(m, sell_tuples)

        return m.costs['Revenue'] == -sum(
            m.e_co_sell[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in sell_tuples)


Purchase Costs
--------------

The variable purchase costs :math:`\zeta_\text{pur}` represents the total annual expenses that are required to be made to purchase buy commodities :math:`c \in C_\text{buy}`. The calculation of the variable total annual purchase cost :math:`\zeta_\text{pur}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{pur} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{buy}}} \psi_{vct} k_{vct}^\text{bs} \Delta t

The variable :math:`\zeta_\text{pur}` is calculated by the sum of all possible annual purchase costs, defined by the combinations of commodity tuples of commodity type 'Buy'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Buy'}`) and timesteps (:math:`\forall t \in T_m`). These annual purchase costs are calculated by the product of the following elements:

	* The parameter buy commodity buy cost for a given buy commodity :math:`c` in a site :math:`v`. ( :math:`k_{vct}^\text{bs}`, ``com_prices[c].loc[tm]`` )
	* The variable buy commodity source term for a given buy commodity :math:`c` in a site :math:`v` at a timestep :math:`t`.( :math:`\psi_{vct}`, ``e_co_buy``)
	* The variable timestep duration.( :math:`\Delta t`, ``dt``)
	* The variable weight.( :math:`w`, ``weight``)

In script ``urbs.py`` the value of the total purchase cost is calculated by the following code fragment:
::

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)
        com_prices = get_com_price(m, buy_tuples)

        return m.costs['Purchase'] == sum(
            m.e_co_buy[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in buy_tuples)


Startup Costs
--------------

The variable startup costs :math:`\zeta_\text{startup}` represents the total annual expenses that are required for the startup occurences of processes :math:`p \in P`. The calculation of the variable total annual startup cost :math:`\zeta_\text{startup}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{startup} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{ p \in P}} \chi_{vpt}^\text{startup} k_{vp}^\text{st} \Delta t


In script ``urbs.py`` the value of the total startup cost is calculated by the following code fragment:
::

    elif cost_type == 'Startup':

        return m.costs['Startup'] == sum(
            m.startupcostfactor[(tm,)+p] * m.process.loc[p]['startup'] * 
            m.weight for tm in m.tm for p in m.pro_tuples)


Commodity Balance
^^^^^^^^^^^^^^^^^

The function commodity balance calculates the balance of a commodity :math:`c` in a site :math:`v` at a timestep :math:`t`. Commodity balance function facilitates the formulation of commodity constraints. The formula for commodity balance is expressed in mathematical notation as:

.. math::

	\mathrm{CB}(v,c,t) = 
          \sum_{{p|c \in C_{vp}^\text{in}}} \epsilon_{vcpt}^\text{in}
        - \sum_{{p|c \in C_{vp}^\text{out}}} \epsilon_{vcpt}^\text{out}
        + \sum_{{s\in S_{vc}}} \left( \epsilon_{vst}^\text{in} - \epsilon_{vst}^\text{out} \right)
        + \sum_{{\substack{a\in A_v^\text{s}\\ f \in F_{vc}^\text{exp}}}} \pi_{aft}^\text{in}
        - \sum_{{\substack{a\in A_v^\text{p}\\ f \in F_{vc}^\text{imp}}}} \pi_{aft}^\text{out}

This function sums up for a given commodity :math:`c`, site :math:`v` and timestep :math:`t`;

	* the consumption: Process input commodity flow  :math:`\epsilon_{vcpt}^\text{in}` of all process tuples using the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.
	* the export: Input transmission power flow :math:`\pi_{aft}^\text{in}` of all transmission tuples exporting the commodity :math:`c` from the origin site :math:`v` at the timestep :math:`t`.
	* the storage input: Input power flow :math:`\epsilon_{vst}^\text{in}` of all storage tuples storing the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.

and subtracts for the same given commodity :math:`c`, site :math:`v` and timestep :math:`t`;
	* the creation: Process output commodity flow :math:`\epsilon_{vcpt}^\text{out}` of all process tuples using the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.
	* the import: Output transmission power flow :math:`\pi_{aft}^\text{out}` of all transmission tuples importing the commodity math:`c` to the destination site :math:`v` at the timestep :math:`t`.
	* the storage output: Output power flow :math:`\epsilon_{vst}^\text{out}` of all storage tuples storing the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.

The value of the function :math:`\mathrm{CB}` being greater than zero :math:`\mathrm{CB} > 0` means that the presence of the commodity :math:`c` in the site :math:`v` at the timestep :math:`t` is getting less than before by the technologies given above. Correspondingly, the value of the function being less than zero means that the presence of the commodity in the site at the timestep is getting more than before by the technologies given above.

In script ``urbs.py`` the value of the commodity balance function :math:`\mathrm{CB}(v,c,t)` is calculated by the following code fragment: 

::

	def commodity_balance(m, tm, sit, com):
		balance = 0
		for site, process in m.pro_tuples:
			if site == sit and com in m.r_in.loc[process].index:
				# usage as input for process increases balance
				balance += m.e_pro_in[(tm, site, process, com)]
			if site == sit and com in m.r_out.loc[process].index:
				# output from processes decreases balance
				balance -= m.e_pro_out[(tm, site, process, com)]
		for site_in, site_out, transmission, commodity in m.tra_tuples:
			# exports increase balance
			if site_in == sit and commodity == com:
				balance += m.e_tra_in[(tm, site_in, site_out, transmission, com)]
			# imports decrease balance
			if site_out == sit and commodity == com:
				balance -= m.e_tra_out[(tm, site_in, site_out, transmission, com)]
		for site, storage, commodity in m.sto_tuples:
			# usage as input for storage increases consumption
			# output from storage decreases consumption
			if site == sit and commodity == com:
				balance += m.e_sto_in[(tm, site, storage, com)]
				balance -= m.e_sto_out[(tm, site, storage, com)]
		return balance

Further information on this function can be found in Helper function section. :func:`commodity_balance(m, tm, sit, com)`

Constraints
===========

Commodity Constraints
^^^^^^^^^^^^^^^^^^^^^

**Vertex Rule**: Vertex rule is the main constraint that has to be satisfied for every commodity. This constraint is defined differently for each commodity type. The inequality requires, that any imbalance (CB>0, CB<0) of a commodity :math:`c` in a site :math:`v` at a timestep :math:`t` to be balanced by a corresponding source term or demand.

* Environmental commodities :math:`C_\text{env}`: this constraint is not defined for environmental commodities.
* Suppy intermittent commodities :math:`C_\text{sup}`: this constraint is not defined for supply intermittent commodities.
* Stock commodities :math:`C_\text{st}`: For stock commodities, the possible imbalance of the commodity must be supplied by the stock commodity purchases. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from the variable stock commodity source term :math:`\rho_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{st}, t\in T_m\colon \qquad & \qquad - \mathrm{CB}(v,c,t) + \rho_{vct} &\geq 0


* Sell commodities :math:`C_\text{sell}`: For sell commodities, the possible imbalance of the commodity must be supplied by the sell commodity trades. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from minus the variable sell commodity source term :math:`\varrho_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{sell}, t\in T_m\colon \qquad & \qquad  - \mathrm{CB}(v,c,t) - \varrho_{vct} &\geq 0

* Buy commodities :math:`C_\text{buy}`: For buy commodities, the possible imbalance of the commodity must be supplied by the buy commodity purchases. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from the variable buy commodity source term :math:`\psi_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{buy}, t\in T_m\colon \qquad & \qquad  - \mathrm{CB}(v,c,t) + \psi_{vct} &\geq 0

* Demand commodities :math:`C_\text{dem}`: For demand commodities, the possible imbalance of the commodity must supply the demand :math:`d_{vct}` of demand commodities :math:`c \in C_\text{dem}`. In other words, the parameter demand for commodity subtracted :math:`d_{vct}` from the minus commodity balance :math:`-\mathrm{CB}(v,c,t)` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as: 

.. math::
	\forall v\in V, c\in C_\text{dem}, t\in T_m\colon \qquad & \qquad  - \mathrm{CB}(v,c,t) - d_{vct} &\geq 0
    
* Demand Side Management commodities and sites: For any combination of commodity and site for which demand side management is defined, the upshift is substracted and the downshift added to the negative commodity balance :math:`-\mathrm{CB}(v,c,t)`.

.. math::
	\forall (v,c) in D_{vc}, t\in T_m\colon \qquad & \qquad  - \mathrm{CB}(v,c,t) - \delta_{vct}^\text{up}` + \sum_{tt \in D_{vct,tt}^\text{down}} \delta_{vct,tt}^\text{down}` &\geq 0

In script ``urbs.py`` the constraint vertex rule is defined and calculated by the following code fragments:

::

		m.res_vertex = pyomo.Constraint(
			m.tm, m.com_tuples,
			rule=res_vertex_rule,
			doc='storage + transmission + process + source + buy - sell == demand')
		

::

	def res_vertex_rule(m, tm, sit, com, com_type):
		# environmental or supim commodities don't have this constraint (yet)
		if com in m.com_env:
			return pyomo.Constraint.Skip
		if com in m.com_supim:
			return pyomo.Constraint.Skip
	
		# helper function commodity_balance calculates balance from input to
		# and output from processes, storage and transmission.
		# if power_surplus > 0: production/storage/imports create net positive
		#                       amount of commodity com
		# if power_surplus < 0: production/storage/exports consume a net
		#                       amount of the commodity com
		power_surplus = - commodity_balance(m, tm, sit, com)
	
		# if com is a stock commodity, the commodity source term e_co_stock
		# can supply a possibly negative power_surplus
		if com in m.com_stock:
			power_surplus += m.e_co_stock[tm, sit, com, com_type]
	
		# if com is a sell commodity, the commodity source term e_co_sell
		# can supply a possibly positive power_surplus
		if com in m.com_sell:
			power_surplus -= m.e_co_sell[tm, sit, com, com_type]
	
		# if com is a buy commodity, the commodity source term e_co_buy
		# can supply a possibly negative power_surplus
		if com in m.com_buy:
			power_surplus += m.e_co_buy[tm, sit, com, com_type]
	
		# if com is a demand commodity, the power_surplus is reduced by the
		# demand value; no scaling by m.dt or m.weight is needed here, as this
		# constraint is about power (MW), not energy (MWh)
		if com in m.com_demand:
			try:
				power_surplus -= m.demand.loc[tm][sit, com]
			except KeyError:
				pass
        # if sit com is a dsm tuple, the power surplus is decreased by the
        # upshifted demand and increased by the downshifted demand.
        if (sit, com) in m.dsm_site_tuples:
            power_surplus -= m.dsm_up[tm,sit,com]
            power_surplus += sum(m.dsm_down[t,tm,sit,com] for t in dsm_time_tuples(tm, m.timesteps[1:], m.dsm.loc[sit,com]['delay']))
		return power_surplus == 0

**Stock Per Step Rule**: The constraint stock per step rule applies only for commodities of type "Stock" ( :math:`c \in C_\text{st}`). This constraint limits the amount of stock commodity :math:`c \in C_\text{st}`, that can be used by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum stock supply limit per time step :math:`\overline{l}_{vc}`. To satisfy this constraint, the value of the variable stock commodity source term :math:`\rho_{vct}` must be less than or equal to the value of the parameter maximum stock supply limit per time step :math:`\overline{l}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{st}, t\in T_m\colon \qquad & \qquad \rho_{vct} &\leq \overline{l}_{vc}

In script ``urbs.py`` the constraint stock per step rule is defined and calculated by the following code fragment:

::

    m.res_stock_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_stock_step_rule,
        doc='stock commodity input per step <= commodity.maxperstep')

::

	def res_stock_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_stock:
			return pyomo.Constraint.Skip
		else:
			return (m.e_co_stock[tm, sit, com, com_type] <=
					m.commodity.loc[sit, com, com_type]['maxperstep'])

**Total Stock Rule**: The constraint total stock rule applies only for commodities of type "Stock" (:math:`c \in C_\text{st}`). This constraint limits the amount of stock commodity :math:`c \in C_\text{st}`, that can be used annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual stock supply limit per vertex :math:`\overline{L}_{vc}`. To satisfy this constraint, the annual usage of stock commodity must be less than or equal to the value of the parameter stock supply limit per vertex :math:`\overline{L}_{vc}`. The annual usage of stock commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the parameter stock commodity source term :math:`\rho_{vct}` for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{st}\colon \qquad & \qquad  w \sum_{t\in T_m} \Delta t\, \rho_{vct} &\leq \overline{L}_{vc}

In script ``urbs.py`` the constraint total stock rule is defined and calculated by the following code fragment:

::

    m.res_stock_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_stock_total_rule,
        doc='total stock commodity input <= commodity.max')

::

	def res_stock_total_rule(m, sit, com, com_type):
		if com not in m.com_stock:
			return pyomo.Constraint.Skip
		else:
			# calculate total consumption of commodity com
			total_consumption = 0
			for tm in m.tm:
				total_consumption += (
					m.e_co_stock[tm, sit, com, com_type] * m.dt)
			total_consumption *= m.weight
			return (total_consumption <=
					m.commodity.loc[sit, com, com_type]['max'])


**Sell Per Step Rule**: The constraint sell per step rule applies only for commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be sold by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum sell supply limit per time step :math:`\overline{g}_{vc}`. To satisfy this constraint, the value of the variable sell commodity source term :math:`\varrho_{vct}` must be less than or equal to the value of the parameter maximum sell supply limit per time step :math:`\overline{g}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{sell}, t\in T_m\colon \qquad & \qquad \varrho_{vct} &\leq \overline{g}_{vc}

In script ``urbs.py`` the constraint sell per step rule is defined and calculated by the following code fragment:
::

    m.res_sell_step = pyomo.Constraint(
       m.tm, m.com_tuples,
       rule=res_sell_step_rule,
       doc='sell commodity output per step <= commodity.maxperstep')

::

	def res_sell_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_sell:
			return pyomo.Constraint.Skip
		else:
			return (m.e_co_sell[tm, sit, com, com_type] <=
					   m.commodity.loc[sit, com, com_type]['maxperstep'])


**Total Sell Rule**: The constraint total sell rule applies only for commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be sold annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual sell supply limit per vertex :math:`\overline{G}_{vc}`. To satisfy this constraint, the annual usage of sell commodity must be less than or equal to the value of the parameter sell supply limit per vertex :math:`\overline{G}_{vc}`. The annual usage of sell commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the parameter sell commodity source term :math:`\varrho_{vct}` for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{sell}\colon \qquad & \qquad  w \sum_{t\in T_m} \Delta t\, \varrho_{vct} &\leq \overline{G}_{vc}

In script ``urbs.py`` the constraint total sell rule is defined and calculated by the following code fragment:
::

    m.res_sell_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_sell_total_rule,
        doc='total sell commodity output <= commodity.max')

::

	def res_sell_total_rule(m, sit, com, com_type):
		if com not in m.com_sell:
			return pyomo.Constraint.Skip
		else:
			# calculate total sale of commodity com
			total_consumption = 0
			for tm in m.tm:
				total_consumption += (
					m.e_co_sell[tm, sit, com, com_type] * m.dt)
			total_consumption *= m.weight
			return (total_consumption <=
					  m.commodity.loc[sit, com, com_type]['max'])

**Buy Per Step Rule**: The constraint buy per step rule applies only for commodities of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits the amount of buy commodity :math:`c \in C_\text{buy}`, that can be bought by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum buy supply limit per time step :math:`\overline{b}_{vc}`. To satisfy this constraint, the value of the variable buy commodity source term :math:`\psi_{vct}` must be less than or equal to the value of the parameter maximum buy supply limit per time step :math:`\overline{b}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{buy}, t\in T_m\colon \qquad & \qquad \psi_{vct} &\leq \overline{b}_{vc}

In script ``urbs.py`` the constraint buy per step rule is defined and calculated by the following code fragment:
::

    m.res_buy_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_buy_step_rule,
        doc='buy commodity output per step <= commodity.maxperstep')

::

	def res_buy_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_buy:
			return pyomo.Constraint.Skip
		else:
			return (m.e_co_buy[tm, sit, com, com_type] <=
					   m.commodity.loc[sit, com, com_type]['maxperstep'])

**Total Buy Rule**: The constraint total buy rule applies only for commodities of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits the amount of buy commodity :math:`c \in C_\text{buy}`, that can be bought annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual buy supply limit per vertex :math:`\overline{B}_{vc}`. To satisfy this constraint, the annual usage of buy commodity must be less than or equal to the value of the parameter buy supply limit per vertex :math:`\overline{B}_{vc}`. The annual usage of buy commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the parameter buy commodity source term :math:`\psi_{vct}` for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{buy}\colon \qquad & \qquad  w \sum_{t\in T_m} \Delta t\, \psi_{vct} &\leq \overline{B}_{vc}

In script ``urbs.py`` the constraint total buy rule is defined and calculated by the following code fragment:
::

    m.res_buy_total = pyomo.Constraint(
       m.com_tuples,
       rule=res_buy_total_rule,
       doc='total buy commodity output <= commodity.max')

::

	def res_buy_total_rule(m, sit, com, com_type):
		if com not in m.com_buy:
			return pyomo.Constraint.Skip
		else:
			# calculate total sale of commodity com
			total_consumption = 0
			for tm in m.tm:
				total_consumption += (
					m.e_co_buy[tm, sit, com, com_type] * m.dt)
			total_consumption *= m.weight
			return (total_consumption <=
					  m.commodity.loc[sit, com, com_type]['max'])

**Environmental Output Per Step Rule**: The constraint environmental output per step rule applies only for commodities of type "Env" ( :math:`c \in C_\text{env}`). This constraint limits the amount of environmental commodity :math:`c \in C_\text{env}`, that can be released to environment by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum environmental output per time step :math:`\overline{m}_{vc}`. To satisfy this constraint, the negative value of the commodity balance for the given environmental commodity :math:`c \in C_\text{env}` must be less than or equal to the value of the parameter maximum environmental output per time step :math:`\overline{m}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{env}, t\in T_m\colon \qquad & \qquad -\mathrm{CB}(v,c,t) &\leq \overline{m}_{vc}

In script ``urbs.py`` the constraint environmental output per step rule is defined and calculated by the following code fragment:
::

    m.res_env_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_env_step_rule,
        doc='environmental output per step <= commodity.maxperstep')

::

	def res_env_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_env:
			return pyomo.Constraint.Skip
		else:
			environmental_output = - commodity_balance(m, tm, sit, com)
			return (environmental_output <=
					m.commodity.loc[sit, com, com_type]['maxperstep'])

**Total Environmental Output Rule**: The constraint total environmental output rule applies only for commodities of type "Env" ( :math:`c \in C_\text{env}`). This constraint limits the amount of environmental commodity :math:`c \in C_\text{env}`, that can be released to environment annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual environmental output limit per vertex :math:`\overline{M}_{vc}`. To satisfy this constraint, the annual release of environmental commodity must be less than or equal to the value of the parameter maximum annual environmental output :math:`\overline{M}_{vc}`. The annual release of environmental commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the negative value of commodity balance function, for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{env}\colon \qquad & \qquad  - w \sum_{t\in T_m} \Delta t\, \mathrm{CB}(v,c,t) &\leq \overline{M}_{vc}

In script ``urbs.py`` the constraint total environmental output rule is defined and calculated by the following code fragment:
::

    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

In script ``urbs.py`` the constraint total environmental output rule is defined and calculated by the following code fragment:
::

	def res_env_total_rule(m, sit, com, com_type):
		if com not in m.com_env:
			return pyomo.Constraint.Skip
		else:
			# calculate total creation of environmental commodity com
			env_output_sum = 0
			for tm in m.tm:
				env_output_sum += (- commodity_balance(m, tm, sit, com) * m.dt)
			env_output_sum *= m.weight
			return (env_output_sum <=
					m.commodity.loc[sit, com, com_type]['max'])

Process Constraints
^^^^^^^^^^^^^^^^^^^

**Process Capacity Rule**: The constraint process capacity rule defines the variable total process capacity :math:`\kappa_{vp}`. The variable total process capacity is defined by the constraint as the sum of the parameter process capacity installed :math:`K_{vp}` and the variable new process capacity :math:`\hat{\kappa}_{vp}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P\colon \qquad & \qquad \kappa_{vp} = K_{vp} + \hat{\kappa}_{vp}

In script ``urbs.py`` the constraint process capacity rule is defined and calculated by the following code fragment:
::

    m.def_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=def_process_capacity_rule,
        doc='total process capacity = inst-cap + new capacity')

::

	def def_process_capacity_rule(m, sit, pro):
		return (m.cap_pro[sit, pro] ==
				m.cap_pro_new[sit, pro] +
				m.process.loc[sit, pro]['inst-cap'])

**Process Input Rule**: The constraint process input rule defines the variable process input commodity flow :math:`\epsilon_{vcpt}^\text{in}`. The variable process input commodity flow is defined by the constraint as the product of the variable process throughput :math:`\tau_{vpt}` and the parameter process input ratio :math:`r_{pc}^\text{in}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \epsilon^\text{in}_{vcpt} &= \tau_{vpt} r^\text{in}_{pc}

In script ``urbs.py`` the constraint process input rule is defined and calculated by the following code fragment:
::

    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')

::

	def def_process_input_rule(m, tm, sit, pro, co):
		return (m.e_pro_in[tm, sit, pro, co] ==
				m.tau_pro[tm, sit, pro] * m.r_in.loc[pro, co])

**Process Output Rule**: The constraint process output rule defines the variable process output commodity flow :math:`\epsilon_{vcpt}^\text{out}`. The variable process output commodity flow is defined by the constraint as the product of the variable process throughput :math:`\tau_{vpt}` and the parameter process output ratio :math:`r_{pc}^\text{out}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \epsilon^\text{out}_{vpct} &= \tau_{vpt} r^\text{out}_{pc}

In script ``urbs.py`` the constraint process output rule is defined and calculated by the following code fragment:
::

    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

::

	def def_process_output_rule(m, tm, sit, pro, co):
		return (m.e_pro_out[tm, sit, pro, co] ==
				m.tau_pro[tm, sit, pro] * m.r_out.loc[pro, co])

**Intermittent Supply Rule**: The constraint intermittent supply rule defines the variable process input commodity flow :math:`\epsilon_{vcpt}^\text{in}` for processes :math:`p` that use a supply intermittent commodity :math:`c \in C_\text{sup}` as input. Therefore this constraint only applies if a commodity is an intermittent supply commodity :math:`c \in C_\text{sup}`. The variable process input commodity flow is defined by the constraint as the product of the variable total process capacity :math:`\kappa_{vp}` and the parameter intermittent supply capacity factor :math:`s_{vct}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, c\in C_\text{sup}, t\in T_m\colon \qquad & \qquad \epsilon^\text{in}_{vpct} &\leq \kappa_{vp} s_{vct}

In script ``urbs.py`` the constraint intermittent supply rule is defined and calculated by the following code fragment:
::

    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')

::

	def def_intermittent_supply_rule(m, tm, sit, pro, coin):
		if coin in m.com_supim:
			return (m.e_pro_in[tm, sit, pro, coin] <=
					m.cap_pro[sit, pro] * m.supim.loc[tm][sit, coin])
		else:
			return pyomo.Constraint.Skip

**Process Throughput By Capacity Rule**: The constraint process throughput by capacity rule limits the variable process throughput :math:`\tau_{vpt}`. This constraint prevents processes from exceeding their capacity. The constraint states that the variable process throughput must be less than or equal to the variable total process capacity :math:`\kappa_{vp}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \tau_{vpt} &\leq \kappa_{vp}

In script ``urbs.py`` the constraint process throughput by capacity rule is defined and calculated by the following code fragment:
::

    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')

::

	def res_process_throughput_by_capacity_rule(m, tm, sit, pro):
		return (m.tau_pro[tm, sit, pro] <= m.cap_pro[sit, pro])

**Process Throughput Gradient Rule**: The constraint process throughput gradient rule limits the process power gradient :math:`\left| \tau_{vpt} - \tau_{vp(t-1)} \right|`. This constraint prevents processes from exceeding their maximal possible change in activity from one time step to the next. The constraint states that absolute power gradient must be less than or equal to the maximal power gradient :math:`\overline{PG}_{vp}` parameter (scaled to capacity and by time step duration). In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \left| \tau_{vpt} - \tau_{vp(t-1)} \right| &\leq  \kappa_{vp} \overline{PG}_{vp} \Delta t

In script ``urbs.py`` the constraint process throughput gradient rule is defined and calculated by the following code fragment:
::

    m.res_process_throughput_gradient = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_gradient_rule,
        doc='process throughput gradient <= maximal gradient')

::

    def res_process_throughput_gradient_rule(m, t, sit, pro):
        if m.process.loc[sit, pro]['max-grad'] < 1/m.dt.value:
            if m.cap_pro[sit, pro].value is None:
                return pyomo.Constraint.Skip
            else:
                return (m.tau_pro[t-1, sit, pro] - m.cap_pro[sit, pro] *
                            m.process.loc[sit, pro]['max-grad'] * m.dt,
                        m.tau_pro[t, sit, pro],
                        m.tau_pro[t-1, sit, pro] + m.cap_pro[sit, pro] *
                            m.process.loc[sit, pro]['max-grad'] * m.dt)
        else:
            return pyomo.Constraint.Skip

**Process Capacity Limit Rule**: The constraint process capacity limit rule limits the variable total process capacity :math:`\kappa_{vp}`. This constraint restricts a process :math:`p` in a site :math:`v` from having more total capacity than an upper bound and having less than a lower bound. The constraint states that the variable total process capacity :math:`\kappa_{vp}` must be greater than or equal to the parameter process capacity lower bound :math:`\underline{K}_{vp}` and less than or equal to the parameter process capacity upper bound :math:`\overline{K}_{vp}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P\colon \qquad & \qquad  \underline{K}_{vp} \leq \kappa_{vp} \leq \overline{K}_{vp}

In script ``urbs.py`` the constraint process capacity limit rule is defined and calculated by the following code fragment:
::

    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

::

	def res_process_capacity_rule(m, sit, pro):
		return (m.process.loc[sit, pro]['cap-lo'],
				m.cap_pro[sit, pro],
				m.process.loc[sit, pro]['cap-up'])

**Sell Buy Symmetry Rule**: The constraint sell buy symmetry rule defines the total process capacity :math:`\kappa_{vp}` of a process :math:`p` in a site :math:`v` that uses either sell or buy commodities ( :math:`c \in C_\text{sell} \vee C_\text{buy}`), therefore this constraint only applies to processes that use sell or buy commodities. The constraint states that the total process capacities :math:`\kappa_{vp}` of processes that use complementary buy and sell commodities must be equal. Buy and sell commodities are complementary, when a commodity :math:`c` is an output of a process where the buy commodity is an input, and at the same time the commodity :math:`c` is an input commodity of a process where the sell commodity is an output.

In script ``urbs.py`` the constraint sell buy symmetry rule is defined and calculated by the following code fragment:
::

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='total power connection capacity must be symmetric in both directions')

::

	def res_sell_buy_symmetry_rule(m, sit_in, pro_in, coin):
	# constraint only for sell and buy processes
	# and the processes must be in the same site
		if coin in m.com_buy:
			sell_pro = search_sell_buy_tuple(m, sit_in, pro_in, coin)
			if sell_pro is None:
				return pyomo.Constraint.Skip
			else:
				return (m.cap_pro[sit_in, pro_in] ==
							m.cap_pro[sit_in, sell_pro])
		else:
			return pyomo.Constraint.Skip

**Process Throughput by Partial Rules**: These constraint process throughput by partial rules constrict the process throughput :math:`\tau_{vpt}` either between the total process capacity :math:`\kappa_{vp}` and its minimum allowable partial load (:math:`\kappa_{vp}` * :math:`\underline{P}_{vp}`), else sets it to zero. 

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \underline{P}_{vp} \kappa'_{vp} \leq \tau_{vpt} \leq \kappa'_{vp}

In script ``urbs.py`` the constraint process throughput by partial rules are defined and calculated by the following code fragment:
::

    m.res_process_throughput_by_partial_1 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_partial_1_rule,
        doc='partial * (process_capacity or 0) <= process throughput ')
    m.res_process_throughput_by_partial_2 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_partial_2_rule,
        doc='process throughput <= (process_capacity or 0) ') 

::

	def res_process_throughput_by_partial_1_rule(m, tm, sit, pro):
    		return (m.process.loc[sit,pro]['partial']*m.cap_pro_piecewise[tm,sit,pro] <=
            		m.tau_pro[tm,sit,pro])
	def res_process_throughput_by_partial_2_rule(m, tm, sit, pro):
    		return (m.tau_pro[tm,sit,pro] <=
            		m.cap_pro_piecewise[tm,sit,pro])

**Piecewise Process Capacity Rules**: These constraint piecewise process capacity rules introduce the necessary inequalities to define the piecewise process capacity :math:`\kappa'_{vpt}` such that it assumes the intended values of 0 (for zero process throughput :math:`\tau_{vpt}`) and the value of total process capacity :math:`\kappa_{vp}` (for non-zero process throughput :math:`\tau_{vpt}`). 

.. math::

	\forall v\in V, p\in P, t\in T_m\colon 
	
	\kappa'_{vpt} \leq \kappa_{vp}

	\kappa'_{vpt} \leq \overline{K}_{vp} \omicron_{vpt}

	\kappa'_{vpt} \geq \kappa_{vp} - \overline{K}_{vp} (1 - \omicron_{vpt})

These inequalities together ensure :math:`\kappa'_{vpt} = \kappa_{vp}` if :math:`\tau_{vpt} \neq 0` and :math:`\kappa'_{vpt} = 0` if :math:`\tau_{vpt} = 0`

In script ``urbs.py`` the constraint piecewise process capacity rules are defined and calculated by the following code fragment:
::

    m.def_cap_pro_piecewise_1 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=def_cap_pro_piecewise_1_rule,
        doc='process piecewise capacity <= process capacity')
    m.def_cap_pro_piecewise_2 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=def_cap_pro_piecewise_2_rule,
        doc='process piecewise capacity <= process.cap-up * online status')
    m.def_cap_pro_piecewise_3 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=def_cap_pro_piecewise_3_rule,
        doc='process piecewise capacity >= process capacity - \
        process.cap-up * (1 - online status)')

::

	def def_cap_pro_piecewise_1_rule(m, tm, sit, pro):
    		return (m.cap_pro_piecewise[tm, sit, pro] <= m.cap_pro[sit,pro])
	def def_cap_pro_piecewise_2_rule(m, tm, sit, pro):
    		return (m.cap_pro_piecewise[tm, sit, pro] <= 
            		m.process.loc[sit,pro]['cap-up'] * m.onlinestatus[tm, sit, pro])
	def def_cap_pro_piecewise_3_rule(m, tm, sit, pro):
    		return (m.cap_pro_piecewise[tm, sit, pro] >=
            		m.cap_pro[sit,pro] - m.process.loc[sit,pro]['cap-up'] *
                	(1 - m.onlinestatus[tm, sit, pro]))

**Process Startup Cost Factor Rules**: These constraint process startup cost factor rules introduce the necessary inequalities to define the process startup cost factor :math:`\chi_{vpt}^\text{startup}` such that it assumes the intended values of 1 for a startup occurence of a process :math:`p` in a site :math:`v` and 0 otherwise.

.. math::

	\forall v\in V, p\in P, t\in T_m\colon 
	
	\chi_{vpt}^\text{startup} \leq \omicron_{vpt}(t)

	\chi_{vpt}^\text{startup} \geq \omicron_{vpt}(t) - 2* \omicron_{vpt}(t-1)

	\chi_{vpt}^\text{startup} \leq \frac{3*\omicron_{vpt}(t) - \omicron_{vpt}(t-1) + 1}{4}

These inequalities together ensure :math:`\chi_{vpt}^\text{startup} = 1` if :math:`\omicron_{vpt}(t-1) = 0 \ \& \  \omicron_{vpt}(t) = 1` and :math:`\chi_{vpt}^\text{startup} = 0` otherwise.

In script ``urbs.py`` the constraint process startup cost factor rules are defined and calculated by the following code fragment:
::

    m.def_startupcostfactor_1 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=def_startupcostfactor_1_rule,
        doc='rule 1 for startupcostfactor')
    m.def_startupcostfactor_2 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=def_startupcostfactor_2_rule,
        doc='rule 2 for startupcostfactor')
    m.def_startupcostfactor_3 = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=def_startupcostfactor_3_rule,
        doc='rule 3 for startupcostfactor')  

::

	def def_startupcostfactor_1_rule(m, tm, sit, pro):
   		return (m.startupcostfactor[tm, sit, pro] <= m.onlinestatus[tm, sit, pro])
	def def_startupcostfactor_2_rule(m, tm, sit, pro):
   		return (m.startupcostfactor[tm, sit, pro] >= m.onlinestatus[tm, sit, pro]-
           		2 * m.onlinestatus[(tm-1), sit, pro])
	def def_startupcostfactor_3_rule(m, tm, sit, pro):
    		return (m.startupcostfactor[tm, sit, pro] <= 
            		(3 * m.onlinestatus[tm, sit, pro] - 
                	m.onlinestatus[(tm-1), sit, pro] +1) / 4)

Transmission Constraints
^^^^^^^^^^^^^^^^^^^^^^^^

**Transmission Capacity Rule**: The constraint transmission capacity rule defines the variable total transmission capacity :math:`\kappa_{af}`. The variable total transmission capacity is defined by the constraint as the sum of the variable transmission capacity installed :math:`K_{af}` and the variable new transmission capacity :math:`\hat{\kappa}_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \kappa_{af} &= K_{af} + \hat{\kappa}_{af}

In script ``urbs.py`` the constraint transmission capacity rule is defined and calculated by the following code fragment:
::

    m.def_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity = inst-cap + new capacity')

::

	def def_transmission_capacity_rule(m, sin, sout, tra, com):
		return (m.cap_tra[sin, sout, tra, com] ==
				m.cap_tra_new[sin, sout, tra, com] +
				m.transmission.loc[sin, sout, tra, com]['inst-cap'])

**Transmission Output Rule**: The constraint transmission output rule defines the variable transmission power flow (output) :math:`\pi_{aft}^\text{out}`. The variable transmission power flow (output) is defined by the constraint as the product of the variable transmission power flow (input) :math:`\pi_{aft}^\text{in}` and the parameter transmission efficiency :math:`e_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F, t\in T_m\colon \qquad & \qquad \pi^\text{out}_{aft} &= \pi^\text{in}_{aft} e_{af}

In script ``urbs.py`` the constraint transmission output rule is defined and calculated by the following code fragment:
::

    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')

::

	def def_transmission_output_rule(m, tm, sin, sout, tra, com):
		return (m.e_tra_out[tm, sin, sout, tra, com] ==
				m.e_tra_in[tm, sin, sout, tra, com] *
				m.transmission.loc[sin, sout, tra, com]['eff'])

**Transmission Input By Capacity Rule**: The constraint transmission input by capacity rule limits the variable transmission power flow (input) :math:`\pi_{aft}^\text{in}`. This constraint prevents  transmissions from exceeding their possible power input capacity. The constraint states that the variable transmission power flow (input) :math:`\pi_{aft}^\text{in}` must be less than or equal to the variable total transmission capacity :math:`\kappa_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F, t\in T_m\colon \qquad & \qquad \pi^\text{in}_{aft} &\leq \kappa_{af}

In script ``urbs.py`` the constraint transmission input by capacity rule is defined and calculated by the following code fragment:
::

    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')

::

	def res_transmission_input_by_capacity_rule(m, tm, sin, sout, tra, com):
		return (m.e_tra_in[tm, sin, sout, tra, com] <=
				m.cap_tra[sin, sout, tra, com])

**Transmission Capacity Limit Rule**: The constraint transmission capacity limit rule limits the variable total transmission capacity :math:`\kappa_{af}`. This constraint restricts a transmission :math:`f` through an arc :math:`a` from having more total power output capacity than an upper bound and having less than a lower bound. The constraint states that the variable total transmission capacity :math:`\kappa_{af}` must be greater than or equal to the parameter transmission capacity lower bound :math:`\underline{K}_{af}` and less than or equal to the parameter transmission capacity upper bound :math:`\overline{K}_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \underline{K}_{af} &\leq \kappa_{af} \leq \overline{K}_{af}

In script ``urbs.py`` the constraint transmission capacity limit rule is defined and calculated by the following code fragment:
::

    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')

::

	def res_transmission_capacity_rule(m, sin, sout, tra, com):
		return (m.transmission.loc[sin, sout, tra, com]['cap-lo'],
				m.cap_tra[sin, sout, tra, com],
				m.transmission.loc[sin, sout, tra, com]['cap-up'])

**Transmission Symmetry Rule**: The constraint transmission symmetry rule defines the power output capacities of incoming and outgoing arcs :math:`a , a'` of a transmission :math:`f`. The constraint states that the power output capacities :math:`\kappa_{af}` of the incoming arc :math:`a` and the complementary outgoing arc :math:`a'` between two sites must be equal. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \kappa_{af} &= \kappa_{a'f}

In script ``urbs.py`` the constraint transmission symmetry rule is defined and calculated by the following code fragment:
::

    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

::

	def res_transmission_symmetry_rule(m, sin, sout, tra, com):
		return m.cap_tra[sin, sout, tra, com] == m.cap_tra[sout, sin, tra, com]

Storage Constraints
^^^^^^^^^^^^^^^^^^^

**Storage State Rule**: The constraint storage state rule is the main storage constraint and it defines the storage energy content of a storage :math:`s` in a site :math:`v` at a timestep :math:`t`. This constraint calculates the storage energy content at a timestep :math:`t` by adding or subtracting differences, such as ingoing and outgoing energy, to/from a storage energy content at a previous timestep :math:`t-1`. Here ingoing energy is given by the product of the variable input storage power flow :math:`\epsilon_{vst}^\text{in}`, the parameter timestep duration :math:`\Delta t` and the parameter storage efficiency during charge :math:`e_{vs}^\text{in}`. Outgoing energy is given by the product of the variable output storage power flow :math:`\epsilon_{vst}^\text{out}` and the parameter timestep duration :math:`\Delta t` divided by the parameter storage efficiency during discharge :math:`e_{vs}^\text{out}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, \forall s\in S, t\in T_\text{m}\colon \qquad & \qquad \epsilon_{vst}^\text{con} = \epsilon_{vs(t-1)}^\text{con}  + \epsilon_{vst}^\text{in} \cdot e_{vs}^\text{in} - \epsilon_{vst}^\text{out} / e_{vs}^\text{out}

In script ``urbs.py`` the constraint storage state rule is defined and calculated by the following code fragment:

::

    m.def_storage_state = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=def_storage_state_rule,
        doc='storage[t] = storage[t-1] + input - output')

::

	def def_storage_state_rule(m, t, sit, sto, com):
		return (m.e_sto_con[t, sit, sto, com] ==
				m.e_sto_con[t-1, sit, sto, com] +
				m.e_sto_in[t, sit, sto, com] *
				m.storage.loc[sit, sto, com]['eff-in'] * m.dt -
				m.e_sto_out[t, sit, sto, com] /
				m.storage.loc[sit, sto, com]['eff-out'] * m.dt)

**Storage Power Rule**: The constraint storage power rule defines the variable total storage power :math:`\kappa_{vs}^\text{p}`. The variable total storage power is defined by the constraint as the sum of the parameter storage power installed :math:`K_{vs}^\text{p}` and the variable new storage power :math:`\hat{\kappa}_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \kappa_{vs}^\text{p} = K_{vs}^\text{p} + \hat{\kappa}_{vs}^\text{p}

In script ``urbs.py`` the constraint storage power rule is defined and calculated by the following code fragment:
::

    m.def_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_power_rule,
        doc='storage power = inst-cap + new power')

::

	def def_storage_power_rule(m, sit, sto, com):
		return (m.cap_sto_p[sit, sto, com] ==
				m.cap_sto_p_new[sit, sto, com] +
				m.storage.loc[sit, sto, com]['inst-cap-p'])

**Storage Capacity Rule**: The constraint storage capacity rule defines the variable total storage size :math:`\kappa_{vs}^\text{c}`. The variable total storage size is defined by the constraint as the sum of the parameter storage content installed :math:`K_{vs}^\text{c}` and the variable new storage size :math:`\hat{\kappa}_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \kappa_{vs}^\text{c} = K_{vs}^\text{c} + \hat{\kappa}_{vs}^\text{c}

In script ``urbs.py`` the constraint storage capacity rule is defined and calculated by the following code fragment:
::

    m.def_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_capacity_rule,
        doc='storage capacity = inst-cap + new capacity')

::

	def def_storage_capacity_rule(m, sit, sto, com):
		return (m.cap_sto_c[sit, sto, com] ==
				m.cap_sto_c_new[sit, sto, com] +
				m.storage.loc[sit, sto, com]['inst-cap-c'])

**Storage Input By Power Rule**: The constraint storage input by power rule limits the variable storage input power flow :math:`\epsilon_{vst}^\text{in}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more input power than the storage power capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{in}` must be less than or equal to the variable total storage power :math:`\kappa_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S, t\in T_m\colon \qquad & \qquad \epsilon_{vst}^\text{in} \leq \kappa_{vs}^\text{p}

In script ``urbs.py`` the constraint storage input by power rule is defined and calculated by the following code fragment:
::

    m.res_storage_input_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_input_by_power_rule,
        doc='storage input <= storage power')

::

	def res_storage_input_by_power_rule(m, t, sit, sto, com):
		return m.e_sto_in[t, sit, sto, com] <= m.cap_sto_p[sit, sto, com]

**Storage Output By Power Rule**: The constraint storage output by power rule limits the variable storage output power flow :math:`\epsilon_{vst}^\text{out}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more output power than the storage power capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{out}` must be less than or equal to the variable total storage power :math:`\kappa_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	 \forall v\in V, s\in S, t\in T\colon \qquad & \qquad \epsilon_{vst}^\text{out} \leq \kappa_{vs}^\text{p}

In script ``urbs.py`` the constraint storage output by power rule is defined and calculated by the following code fragment:
::

    m.res_storage_output_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_output_by_power_rule,
        doc='storage output <= storage power')

::

	def res_storage_output_by_power_rule(m, t, sit, sto, co):
		return m.e_sto_out[t, sit, sto, co] <= m.cap_sto_p[sit, sto, co]

**Storage State By Capacity Rule**: The constraint storage state by capacity rule limits the variable storage energy content :math:`\epsilon_{vst}^\text{con}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more storage content than the storage content capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{con}` must be less than or equal to the variable total storage size :math:`\kappa_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S, t\in T\colon \qquad & \qquad \epsilon_{vst}^\text{con} \leq \kappa_{vs}^\text{c}

In script ``urbs.py`` the constraint storage state by capacity rule is defined and calculated by the following code fragment.
::

    m.res_storage_state_by_capacity = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_storage_state_by_capacity_rule,
        doc='storage content <= storage capacity')

::

	def res_storage_state_by_capacity_rule(m, t, sit, sto, com):
		return m.e_sto_con[t, sit, sto, com] <= m.cap_sto_c[sit, sto, com]

**Storage Power Limit Rule**: The constraint storage power limit rule limits the variable total storage power :math:`\kappa_{vs}^\text{p}`. This contraint restricts a storage :math:`s` in a site :math:`v` from having more total power output capacity than an upper bound and having less than a lower bound. The constraint states that the variable total storage power :math:`\kappa_{vs}^\text{p}` must be greater than or equal to the parameter storage power lower bound :math:`\underline{K}_{vs}^\text{p}` and less than or equal to the parameter storage power upper bound :math:`\overline{K}_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \underline{K}_{vs}^\text{p} \leq \kappa_{vs}^\text{p} \leq \overline{K}_{vs}^\text{p}

In script ``urbs.py`` the constraint storage power limit rule is defined and calculated by the following code fragment: 
::

    m.res_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_power_rule,
        doc='storage.cap-lo-p <= storage power <= storage.cap-up-p')

::

	def res_storage_power_rule(m, sit, sto, com):
		return (m.storage.loc[sit, sto, com]['cap-lo-p'],
				m.cap_sto_p[sit, sto, com],
				m.storage.loc[sit, sto, com]['cap-up-p'])

**Storage Capacity Limit Rule**: The constraint storage capacity limit rule limits the variable total storage size :math:`\kappa_{vs}^\text{c}`. This contraint restricts a storage :math:`s` in a site :math:`v` from having more total storage content capacity than an upper bound and having less than a lower bound. The constraint states that the variable total storage size :math:`\kappa_{vs}^\text{c}` must be greater than or equal to the parameter storage content lower bound :math:`\underline{K}_{vs}^\text{c}` and less than or equal to the parameter storage content upper bound :math:`\overline{K}_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \underline{K}_{vs}^\text{c} \leq \kappa_{vs}^\text{c} \leq \overline{K}_{vs}^\text{c}

In script ``urbs.py`` the constraint storage capacity limit rule is defined and calculated by the following code fragment:
::

    m.res_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_capacity_rule,
        doc='storage.cap-lo-c <= storage capacity <= storage.cap-up-c')

::

	def res_storage_capacity_rule(m, sit, sto, com):
		return (m.storage.loc[sit, sto, com]['cap-lo-c'],
				m.cap_sto_c[sit, sto, com],
				m.storage.loc[sit, sto, com]['cap-up-c'])

**Initial And Final Storage State Rule**: The constraint initial and final storage state rule defines and restricts the variable storage energy content :math:`\epsilon_{vst}^\text{con}` of a storage :math:`s` in a site :math:`v` at the initial timestep :math:`t_1` and at the final timestep :math:`t_N`.  

Initial Storage:  Initial storage represents how much energy is installed in a storage at the beginning of the simulation. The variable storage energy content :math:`\epsilon_{vst}^\text{con}` at the initial timestep :math:`t_1` is defined by this constraint. The constraint states that the variable :math:`\epsilon_{vst_1}^\text{con}` must be equal to the product of the parameters storage content installed :math:`K_{vs}^\text{c}` and  initial and final state of charge :math:`I_{vs}`. In mathematical notation this is expressed as: 

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \epsilon_{vst_1}^\text{con} = \kappa_{vs}^\text{c} I_{vs}

Final Storage: Final storage represents how much energy is installed in a storage at the end of the simulation. The variable storage energy content :math:`\epsilon_{vst}^\text{con}` at the final timestep :math:`t_N` is restricted by this constraint. The constraint states that the variable :math:`\epsilon_{vst_N}^\text{con}` must be greater than or equal to the product of the parameters storage content installed :math:`K_{vs}^\text{c}` and  initial and final state of charge :math:`I_{vs}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \epsilon_{vst_N}^\text{con} \geq \kappa_{vs}^\text{c} I_{vs}

In script ``urbs.py`` the constraint initial and final storage state rule is defined and calculated by the following code fragment:
::

    m.res_initial_and_final_storage_state = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_initial_and_final_storage_state_rule,
        doc='storage content initial == and final >= storage.init * capacity')

::

	def res_initial_and_final_storage_state_rule(m, t, sit, sto, com):
		if t == m.t[1]:  # first timestep (Pyomo uses 1-based indexing)
			return (m.e_sto_con[t, sit, sto, com] ==
					m.cap_sto_c[sit, sto, com] *
					m.storage.loc[sit, sto, com]['init'])
		elif t == m.t[len(m.t)]:  # last timestep
			return (m.e_sto_con[t, sit, sto, com] >=
					m.cap_sto_c[sit, sto, com] *
					m.storage.loc[sit, sto, com]['init'])
		else:
			return pyomo.Constraint.Skip

Demand Side Management Constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The DSM equations are taken from the Paper of Zerrahn and Schill "On the representation of demand-side management in power system models", DOI: `10.1016/j.energy.2015.03.037 <http://dx.doi.org/10.1016/j.energy.2015.03.037>`_.

**DSM Variables Rule**: The DSM variables rule defines the relation between upshift and downshift. An upshift :math:`\delta_{vct}^\text{up}` in site :math:`v` of commodity :math:`c` in time step :math:`t` can be compensated during a certain time interval :math:`[t-y_{vc}, t+y_{vc}]` by multiple downshifts :math:`\delta_{vct,tt}^\text{down}`. Depending on the efficiency :math:`e_{vc}`, less downshifts have to be made. This is given by:

.. math::
    \forall (v,c) \in D_{vc}, t\in T\colon \qquad & \qquad \delta_{vct}^\text{up} e_{vc} = \sum_{tt = t-y_{vc}}^{t+y_{vc}} \delta_{vct,tt}^\text{down}
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.def_dsm_variables = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=def_dsm_variables_rule,
        doc='DSMup == DSMdo * efficiency factor n')	

::

    def def_dsm_variables_rule(m, tm, sit, com):
        dsm_down_sum = 0
        for tt in dsm_time_tuples(tm, m.timesteps[1:], m.dsm.loc[sit,com]['delay']):
            dsm_down_sum += m.dsm_down[tm,tt,sit,com]
        return dsm_down_sum == m.dsm_up[tm,sit,com] * m.dsm.loc[sit,com]['eff']
        
        
**DSM Upward Rule**: The DSM upshift :math:`\delta_{vct}^\text{up}` in site :math:`v` of commodity :math:`c` in time step :math:`t` is limited by the maximal upshift capacity :math:`\overline{K}_{vc}^\text{up}`. In mathematical terms, this is written as:

.. math::
    \forall (v,c) \in D_{vc}, t\in T \colon \qquad & \qquad \delta_{vct}^\text{up} \leq \overline{K}_{vc}^\text{up}
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_upward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_upward_rule,
        doc='DSMup <= Cup (threshold capacity of DSMup)')

::

    def res_dsm_upward_rule(m, tm, sit, com):
        return m.dsm_up[tm,sit,com] <= int(m.dsm.loc[sit,com]['cap-max-up'])
        
**DSM Downward Rule**: The DSM downshift :math:`\delta_{vct}^\text{up}` in site :math:`v` of commodity :math:`c` in time step :math:`t` is limited by the maximal upshift capacity :math:`\overline{K}_{vc}^\text{up}`. In mathematical terms, this is written as:

.. math::
    \forall (v,c) \in D_{vc}, tt\in T \colon \qquad & \qquad \sum_{t = tt-y}^{tt+y} \delta_{vct,tt}^\text{down} \leq \overline{K}_{vc}^\text{down}
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_downward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_downward_rule,
        doc='DSMdo <= Cdo (threshold capacity of DSMdo)')

::

    def res_dsm_downward_rule(m, tm, sit, com):
        dsm_down_sum = 0
        for t in dsm_time_tuples(tm, m.timesteps[1:], m.dsm.loc[sit,com]['delay']):
            dsm_down_sum += m.dsm_down[t,tm,sit,com]
        return dsm_down_sum <= m.dsm.loc[sit,com]['cap-max-do']
        

**DSM Maximum Rule**: The DSM maximum rule limits the shift of one DSM unit in site :math:`v` of commodity :math:`c` in time step :math:`t`. In mathematical terms, this is written as:

.. math::
    \forall (v,c) \in D_{vc}, tt\in T \colon \qquad & \qquad \delta_{vct}^\text{up} + \sum_{t = tt-y}^{tt+y} \delta_{vct,tt}^\text{down} \leq \max \left\lbrace \overline{K}_{vc}^\text{up}, \overline{K}_{vc}^\text{down} \right\rbrace
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_maximum = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_maximum_rule,
        doc='DSMup + DSMdo <= max(Cup,Cdo)')

::

    def res_dsm_maximum_rule(m, tm, sit, com):
        dsm_down_sum = 0
        for t in dsm_time_tuples(tm, m.timesteps[1:], m.dsm.loc[sit,com]['delay']):
            dsm_down_sum += m.dsm_down[t,tm,sit,com]

        max_dsm_limit = max(m.dsm.loc[sit,com]['cap-max-up'], 
                              m.dsm.loc[sit,com]['cap-max-do'])
        return m.dsm_up[tm,sit,com] + dsm_down_sum <= max_dsm_limit

**DSM Recovery Rule**: The DSM recovery rule limits the upshift in site :math:`v` of commodity :math:`c` during a set recovery period :math:`o_{vc}`. In mathematical terms, this is written as:

.. math::
    \forall (v,c) \in D_{vc}, t\in T \colon \qquad & \qquad \sum_{tt = t}^{t+o_{vc}-1} \delta_{vctt}^\text{up} \leq \overline{K}_{vc}^\text{up} y
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_recovery = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_recovery_rule,
        doc='DSMup(t, t + recovery time R) <= Cup * delay time L')

::

    def res_dsm_recovery_rule(m, tm, sit, com):
        dsm_up_sum = 0
        for t in range(tm, tm+m.dsm.loc[sit,com]['recov']):
            dsm_up_sum += m.dsm_up[t,sit,com]
        return dsm_up_sum <= m.dsm.loc[sit,com]['cap-max-up'] * m.dsm.loc[sit,com]['delay']       
  
        
            
Environmental Constraints
^^^^^^^^^^^^^^^^^^^^^^^^^

**Global CO2 Limit Rule**: The constraint global CO2 limit rule applies to the whole energy system, that is to say it applies to every site and timestep in general. This constraints restricts the energy model from releasing more environmental commodities, namely CO2 to environment than allowed. The constraint states that the sum of released environmental commodities for every site :math:`v` and every timestep :math:`t` must be less than or equal to the parameter maximum global annual CO2 emission limit :math:`\overline{L}_{CO_{2}}`, where the amount of released enviromental commodites in a single site :math:`v` at a single timestep :math:`t` is calculated by the product of commodity balance of enviromental commodities :math:`\mathrm{CB}(v,CO_{2},t)` and the parameter weight :math:`w`. This constraint is skipped if the value of the parameter :math:`\overline{L}_{CO_{2}}` is set to ``inf``. In mathematical notation this constraint is expressed as:

.. math::

	w \sum_{t\in T_\text{m}} \sum_{v \in V} \mathrm{-CB}(v,CO_{2},t) \leq \overline{L}_{CO_{2}}

In script ``urbs.py`` the constraint global CO2 limit rule is defined and calculated by the following code fragment:
::

	def add_hacks(model, hacks):
		""" add hackish features to model object

		This function is reserved for corner cases/features that still lack a
		satisfyingly general solution that could become part of create_model.
		Use hack features sparingly and think about how to incorporate into main
		model function before adding here. Otherwise, these features might become
		a maintenance burden.

		"""

		# Store hack data
		model.hacks = hacks

		# Global CO2 limit
		try:
			global_co2_limit = hacks.loc['Global CO2 limit', 'Value']
		except KeyError:
			global_co2_limit = float('inf')

		# only add constraint if limit is finite
		if not math.isinf(global_co2_limit):
			model.res_global_co2_limit = pyomo.Constraint(
				rule=res_global_co2_limit_rule,
				doc='total co2 commodity output <= hacks.Glocal CO2 limit')

		return model

::

	def res_global_co2_limit_rule(m):
		co2_output_sum = 0
		for tm in m.tm:
			for sit in m.sit:
				# minus because negative commodity_balance represents creation of 
				# that commodity.
				co2_output_sum += (- commodity_balance(m, tm, sit, 'CO2') * m.dt)

		# scaling to annual output (cf. definition of m.weight)
		co2_output_sum *= m.weight
		return (co2_output_sum <= m.hacks.loc['Global CO2 limit', 'Value'])

