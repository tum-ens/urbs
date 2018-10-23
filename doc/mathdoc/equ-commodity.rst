.. module urbs

Commodity Constraints
^^^^^^^^^^^^^^^^^^^^^

**Commodity Balance** The function commodity balance calculates the balance of a commodity :math:`c` in a site :math:`v` at a timestep :math:`t`. Commodity balance function facilitates the formulation of commodity constraints. The formula for commodity balance is expressed in mathematical notation as:

.. math::

	\mathrm{CB}(v,c,t) = 
          \sum_{p|c \in C_{vp}^\text{in}} \epsilon_{vcpt}^\text{in}
        - \sum_{p|c \in C_{vp}^\text{out}} \epsilon_{vcpt}^\text{out}
        + \sum_{{s\in S_{vc}}} \left( \epsilon_{vst}^\text{in} - \epsilon_{vst}^\text{out} \right)
        + \sum_{{\substack{a\in A_v^\text{s}\\ f \in F_{vc}^\text{exp}}}} \pi_{aft}^\text{in}
        - \sum_{{\substack{a\in A_v^\text{p}\\ f \in F_{vc}^\text{imp}}}} \pi_{aft}^\text{out}

This function sums up for a given commodity :math:`c`, site :math:`v` and timestep :math:`t`;

* the consumption: Process input commodity flow :math:`\epsilon_{vcpt}^\text{in}` of all process tuples using the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.
* the export: Transmission input commodity flow :math:`\pi_{aft}^\text{in}` of all transmission tuples exporting the commodity :math:`c` from the origin site :math:`v` at the timestep :math:`t`.
* the storage input: Storage input commodity flow :math:`\epsilon_{vst}^\text{in}` of all storage tuples storing the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.

and subtracts for the same given commodity :math:`c`, site :math:`v` and timestep :math:`t`;

* the creation: Process output commodity flow :math:`\epsilon_{vcpt}^\text{out}` of all process tuples using the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.
* the import: Transmission output commodity flow  :math:`\pi_{aft}^\text{out}` of all transmission tuples importing the commodity math:`c` to the destination site :math:`v` at the timestep :math:`t`.
* the storage output: Storage output commodity flow  :math:`\epsilon_{vst}^\text{out}` of all storage tuples storing the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.

The value of the function :math:`\mathrm{CB}` being greater than zero :math:`\mathrm{CB} > 0` means that the presence of the commodity :math:`c` in the site :math:`v` at the timestep :math:`t` is getting less than before by the technologies given above. Correspondingly, the value of the function being less than zero means that the presence of the commodity in the site at the timestep is getting more than before by the technologies given above.

In script ``model.py`` the value of the commodity balance function :math:`\mathrm{CB}(v,c,t)` is calculated by the following code fragment: 

.. literalinclude:: /../urbs/modelhelper.py
   :pyobject: commodity_balance



**Vertex Rule**: Vertex rule is the main constraint that has to be satisfied for every commodity. This constraint is defined differently for each commodity type. The inequality requires, that any imbalance (CB>0, CB<0) of a commodity :math:`c` in a site :math:`v` at a timestep :math:`t` to be balanced by a corresponding source term or demand.

* Environmental commodities :math:`C_\text{env}`: this constraint is not defined for environmental commodities.
* Suppy intermittent commodities :math:`C_\text{sup}`: this constraint is not defined for supply intermittent commodities.
* Stock commodities :math:`C_\text{st}`: For stock commodities, the possible imbalance of the commodity must be supplied by the stock commodity purchases. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from the variable stock commodity source term :math:`\rho_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{st}, t\in T_m\colon\ - \mathrm{CB}(v,c,t) + \rho_{vct} \geq 0


* Sell commodities :math:`C_\text{sell}`: For sell commodities, the possible imbalance of the commodity must be supplied by the sell commodity trades. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from minus the variable sell commodity source term :math:`\varrho_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{sell}, t\in T_m\colon\ - \mathrm{CB}(v,c,t) - \varrho_{vct} \geq 0

* Buy commodities :math:`C_\text{buy}`: For buy commodities, the possible imbalance of the commodity must be supplied by the buy commodity purchases. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from the variable buy commodity source term :math:`\psi_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{buy}, t\in T_m\colon\ - \mathrm{CB}(v,c,t) + \psi_{vct} \geq 0

* Demand commodities :math:`C_\text{dem}`: For demand commodities, the possible imbalance of the commodity must supply the demand :math:`d_{vct}` of demand commodities :math:`c \in C_\text{dem}`. In other words, the parameter demand for commodity subtracted :math:`d_{vct}` from the minus commodity balance :math:`-\mathrm{CB}(v,c,t)` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as: 

.. math::
	\forall v\in V, c\in C_\text{dem}, t\in T_m\colon\ - \mathrm{CB}(v,c,t) - d_{vct} \geq 0
    
* Demand Side Management commodities and sites: For any combination of commodity and site for which demand side management is defined, the upshift is substracted and the downshift added to the negative commodity balance :math:`-\mathrm{CB}(v,c,t)`.

.. math::
	\forall (v,c) \in D_{vc}, t\in T_m\colon\ - \mathrm{CB}(v,c,t) - \delta_{vct}^\text{up}` + \sum_{tt \in D_{vct,tt}^\text{down}} \delta_{vct,tt}^\text{down}` \geq 0

In script ``model.py`` the constraint vertex rule is defined and calculated by the following code fragments:

::

		m.res_vertex = pyomo.Constraint(
			m.tm, m.com_tuples,
			rule=res_vertex_rule,
			doc='storage + transmission + process + source + buy - sell == demand')
		

.. literalinclude:: /../urbs/model.py
   :pyobject: res_vertex_rule

**Stock Per Step Rule**: The constraint stock per step rule applies only for commodities of type "Stock" ( :math:`c \in C_\text{st}`). This constraint limits the amount of stock commodity :math:`c \in C_\text{st}`, that can be used by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum stock supply limit per hour :math:`\overline{l}_{vc}`. To satisfy this constraint, the value of the variable stock commodity source term :math:`\rho_{vct}` each time step must be less than or equal to the value of the parameter maximum stock supply limit per hour :math:`\overline{l}_{vc}`, multiplied by the size of the time steps :math:`\Delta t`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{st}, t\in T_m\colon\ \rho_{vct} \leq \overline{l}_{vc} \Delta t

In script ``model.py`` the constraint stock per step rule is defined and calculated by the following code fragment:

::

    m.res_stock_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_stock_step_rule,
        doc='stock commodity input per step <= commodity.maxperstep')


.. literalinclude:: /../urbs/model.py
   :pyobject: res_stock_step_rule


**Total Stock Rule**: The constraint total stock rule applies only for commodities of type "Stock" (:math:`c \in C_\text{st}`). This constraint limits the amount of stock commodity :math:`c \in C_\text{st}`, that can be used annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual stock supply limit per vertex :math:`\overline{L}_{vc}`. To satisfy this constraint, the annual usage of stock commodity must be less than or equal to the value of the parameter stock supply limit per vertex :math:`\overline{L}_{vc}`. The annual usage of stock commodity is calculated by the sum of the products of the parameter weight :math:`w` and the parameter stock commodity source term :math:`\rho_{vct}`, summed over the whole modeled time horizon :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{st}\colon\ w \sum_{t\in T_m} \rho_{vct} \leq \overline{L}_{vc}

In script ``model.py`` the constraint total stock rule is defined and calculated by the following code fragment:

::

    m.res_stock_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_stock_total_rule,
        doc='total stock commodity input <= commodity.max')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_stock_total_rule


**Sell Per Step Rule**: The constraint sell per step rule applies only for commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be sold by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum sell supply limit per hour :math:`\overline{g}_{vc}`. To satisfy this constraint, the value of the variable sell commodity source term :math:`\varrho_{vct}` must be less than or equal to the value of the parameter maximum sell supply limit per hour :math:`\overline{g}_{vc}`, multiplied by the size of the time steps :math:`\Delta t`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{sell}, t\in T_m\colon\  \varrho_{vct} \leq \overline{g}_{vc} \Delta t

In script ``model.py`` the constraint sell per step rule is defined and calculated by the following code fragment:
::

    m.res_sell_step = pyomo.Constraint(
       m.tm, m.com_tuples,
       rule=res_sell_step_rule,
       doc='sell commodity output per step <= commodity.maxperstep')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_sell_step_rule

**Total Sell Rule**: The constraint total sell rule applies only for commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be sold annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual sell supply limit per vertex :math:`\overline{G}_{vc}`. To satisfy this constraint, the annual usage of sell commodity must be less than or equal to the value of the parameter sell supply limit per vertex :math:`\overline{G}_{vc}`. The annual usage of sell commodity is calculated by the sum of the products of the parameter weight :math:`w` and the parameter sell commodity source term :math:`\varrho_{vct}`, summed over the whole modeled time horizon :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{sell}\colon\ w \sum_{t\in T_m} \varrho_{vct} \leq \overline{G}_{vc}

In script ``model.py`` the constraint total sell rule is defined and calculated by the following code fragment:
::

    m.res_sell_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_sell_total_rule,
        doc='total sell commodity output <= commodity.max')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_sell_total_rule

**Buy Per Step Rule**: The constraint buy per step rule applies only for commodities of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits the amount of buy commodity :math:`c \in C_\text{buy}`, that can be bought by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum buy supply limit per time step :math:`\overline{b}_{vc}`. To satisfy this constraint, the value of the variable buy commodity source term :math:`\psi_{vct}` must be less than or equal to the value of the parameter maximum buy supply limit per time step :math:`\overline{b}_{vc}`, multiplied by the size of the time steps :math:`\Delta t`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{buy}, t\in T_m\colon\  \psi_{vct} \leq \overline{b}_{vc} \Delta t

In script ``model.py`` the constraint buy per step rule is defined and calculated by the following code fragment:
::

    m.res_buy_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_buy_step_rule,
        doc='buy commodity output per step <= commodity.maxperstep')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_buy_step_rule

**Total Buy Rule**: The constraint total buy rule applies only for commodities of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits the amount of buy commodity :math:`c \in C_\text{buy}`, that can be bought annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual buy supply limit per vertex :math:`\overline{B}_{vc}`. To satisfy this constraint, the annual usage of buy commodity must be less than or equal to the value of the parameter buy supply limit per vertex :math:`\overline{B}_{vc}`. The annual usage of buy commodity is calculated by the sum of the products of the parameter weight :math:`w` and the parameter buy commodity source term :math:`\psi_{vct}`, summed over the whole modeled time horizon :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{buy}\colon\ w \sum_{t\in T_m} \psi_{vct} \leq \overline{B}_{vc}

In script ``model.py`` the constraint total buy rule is defined and calculated by the following code fragment:
::

    m.res_buy_total = pyomo.Constraint(
       m.com_tuples,
       rule=res_buy_total_rule,
       doc='total buy commodity output <= commodity.max')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_buy_total_rule


**Environmental Output Per Step Rule**: The constraint environmental output per step rule applies only for commodities of type "Env" ( :math:`c \in C_\text{env}`). This constraint limits the amount of environmental commodity :math:`c \in C_\text{env}`, that can be released to environment by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum environmental output per time step :math:`\overline{m}_{vc}`. To satisfy this constraint, the negative value of the commodity balance for the given environmental commodity :math:`c \in C_\text{env}` must be less than or equal to the value of the parameter maximum environmental output per time step :math:`\overline{m}_{vc}`, multiplied by the size of the time steps :math:`\Delta t`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{env}, t\in T_m\colon\  -\mathrm{CB}(v,c,t) \leq \overline{m}_{vc} \Delta t

In script ``model.py`` the constraint environmental output per step rule is defined and calculated by the following code fragment:
::

    m.res_env_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_env_step_rule,
        doc='environmental output per step <= commodity.maxperstep')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_env_step_rule


**Total Environmental Output Rule**: The constraint total environmental output rule applies only for commodities of type "Env" ( :math:`c \in C_\text{env}`). This constraint limits the amount of environmental commodity :math:`c \in C_\text{env}`, that can be released to environment annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual environmental output limit per vertex :math:`\overline{M}_{vc}`. To satisfy this constraint, the annual release of environmental commodity must be less than or equal to the value of the parameter maximum annual environmental output :math:`\overline{M}_{vc}`. The annual release of environmental commodity is calculated by the sum of the products of the parameter weight :math:`w` and the negative value of commodity balance function, summed over the whole modeled time horizon :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{env}\colon\ - w \sum_{t\in T_m} \mathrm{CB}(v,c,t) \leq \overline{M}_{vc}

In script ``model.py`` the constraint total environmental output rule is defined and calculated by the following code fragment:
::

    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

In script ``model.py`` the constraint total environmental output rule is defined and calculated by the following code fragment:

.. literalinclude:: /../urbs/model.py
   :pyobject: res_env_total_rule


   
.. _sec-dsm-constr:

Demand Side Management Constraints
----------------------------------

The DSM equations are taken from the Paper of Zerrahn and Schill "On the representation of demand-side management in power system models", DOI: `10.1016/j.energy.2015.03.037 <http://dx.doi.org/10.1016/j.energy.2015.03.037>`_.


**DSM Variables Rule**: The DSM variables rule defines the relation between the up- and downshifted DSM commodities. An upshift :math:`\delta_{vct}^\text{up}` in site :math:`v` of commodity :math:`c` in time step :math:`t` can be compensated during a certain time step interval :math:`[t-y_{vc}/{\Delta t}, t+y_{vc}/{\Delta t}]` by multiple downshifts :math:`\delta_{vct,tt}^\text{down}`. Here, :math:`y_{vc}` represents the allowable delay time of downshifts in hours, which is scaled into time steps by dividing by :math:`{\Delta t}`. Depending on the DSM efficiency :math:`e_{vc}`, an upshift in a DSM commodity may correspond to multiple downshifts which sum to less than the original upshift. In mathematical terms, this constraint is expressed as:
.. math:: 
	
	\forall (v,c) \in D_{vc}, t\in T\colon\  \delta_{vct}^\text{up} e_{vc} = \sum_{tt = t-y_{vc}/{\Delta t}}^{t+y_{vc}/{\Delta t}} \delta_{vct,tt}^\text{down}
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.def_dsm_variables = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=def_dsm_variables_rule,
        doc='DSMup * efficiency factor n == DSMdo (summed)')	

.. literalinclude:: /../urbs/model.py
   :pyobject: def_dsm_variables_rule
        
        
**DSM Upward Rule**: The DSM upshift :math:`\delta_{vct}^\text{up}` in site :math:`v` of commodity :math:`c` in time step :math:`t` is limited by the DSM maximal upshift per hour :math:`\overline{K}_{vc}^\text{up}`, multiplied by the size of the time steps :math:`\Delta t`. In mathematical terms, this constraint is expressed as:

.. math::
    \forall (v,c) \in D_{vc}, t\in T \colon\  \delta_{vct}^\text{up} \leq \overline{K}_{vc}^\text{up} \Delta t
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_upward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_upward_rule,
        doc='DSMup <= Cup (threshold capacity of DSMup)')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_dsm_upward_rule
        
**DSM Downward Rule**: The total DSM downshift :math:`\delta_{vct}^\text{down}` in site :math:`v` of commodity :math:`c` in time step :math:`t` is limited by the DSM maximal downshift per hour :math:`\overline{K}_{vc}^\text{down}`, multiplied by the size of the time steps :math:`\Delta t`. In mathematical terms, this constraint is expressed as:

.. math::
    \forall (v,c) \in D_{vc}, tt\in T \colon\  \sum_{t = tt-y/{\Delta t}}^{tt+y/{\Delta t}} \delta_{vct,tt}^\text{down} \leq \overline{K}_{vc}^\text{down} \Delta t
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_downward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_downward_rule,
        doc='DSMdo (summed) <= Cdo (threshold capacity of DSMdo)')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_dsm_downward_rule
        

**DSM Maximum Rule**: The DSM maximum rule limits the shift of one DSM unit in site :math:`v` of commodity :math:`c` in time step :math:`t`. In mathematical terms, this constraint is expressed as:

.. math::
    \forall (v,c) \in D_{vc}, tt\in T \colon\  \delta_{vct}^\text{up} + \sum_{t = tt-y/{\Delta t}}^{tt+y/{\Delta t}} \delta_{vct,tt}^\text{down} \leq \max \left\lbrace \overline{K}_{vc}^\text{up}, \overline{K}_{vc}^\text{down} \right\rbrace \Delta t
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_maximum = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_maximum_rule,
        doc='DSMup + DSMdo (summed) <= max(Cup,Cdo)')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_dsm_maximum_rule

**DSM Recovery Rule**: The DSM recovery rule limits the upshift in site :math:`v` of commodity :math:`c` during a set recovery period :math:`o_{vc}`. Since the recovery period :math:`o_{vc}` is input as hours, it is scaled into time steps by dividing by the size of the time steps :math:`\Delta t`. In mathematical terms, this constraint is expressed as:

.. math::
    \forall (v,c) \in D_{vc}, t\in T \colon\  \sum_{tt = t}^{t+o_{vc}/{\Delta t}-1} \delta_{vctt}^\text{up} \leq (\overline{K}_{vc}^\text{up} \Delta t) (y /{\Delta t})
    
The definition of the constraint and its corresponding rule is defined by the following code:

::

    m.res_dsm_recovery = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_recovery_rule,
        doc='DSMup(t, t + recovery time R) <= Cup * delay time L')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_dsm_recovery_rule     
  
        
            
Global Environmental Constraint
-------------------------------

**Global CO2 Limit Rule**: The constraint global CO2 limit rule applies to the whole energy system, that is to say it applies to every site and timestep in general. This constraints restricts the energy model from releasing more environmental commodities, namely CO2 to environment than allowed. The constraint states that the sum of released environmental commodities for every site :math:`v` and every timestep :math:`t` must be less than or equal to the parameter maximum global annual CO2 emission limit :math:`\overline{L}_{CO_{2}}`, where the amount of released enviromental commodites in a single site :math:`v` at a single timestep :math:`t` is calculated by the product of commodity balance of enviromental commodities :math:`\mathrm{CB}(v,CO_{2},t)` and the parameter weight :math:`w`. This constraint is skipped if the value of the parameter :math:`\overline{L}_{CO_{2}}` is set to ``inf``. In mathematical notation this constraint is expressed as:

.. math::

	w \sum_{t\in T_\text{m}} \sum_{v \in V} \mathrm{-CB}(v,CO_{2},t) \leq \overline{L}_{CO_{2}}

In script ``model.py`` the constraint global CO2 limit rule is defined and calculated by the following code fragment:

.. literalinclude:: /../urbs/model.py
   :pyobject: res_global_co2_limit_rule
