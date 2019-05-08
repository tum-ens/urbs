.. module urbs

Commodity Constraints
^^^^^^^^^^^^^^^^^^^^^

**Commodity Balance** The function commodity balance calculates the in- and
outflows into all processes, storages and transmission of a commodity :math:`c`
in a site :math:`v` in support timeframe :math:`y` at a timestep :math:`t`. The
value of the function :math:`\mathrm{CB}` being greater than zero
:math:`\mathrm{CB} > 0` means that the presence of the commodity :math:`c` in
the site :math:`v` in support timeframe :math:`y` at the timestep :math:`t` is
getting by the interaction with the technologies given above. Correspondingly,
the value of the function being less than zero means that the presence of the
commodity in the site at the timestep is getting more than before by the
technologies given above. The mathematical explanation of this rule for general
problems is explained in :ref:`theory-storage`.

In script ``modelhelper.py`` the value of the commodity balance function
:math:`\mathrm{CB}(y,v,c,t)` is calculated by the following code fragment: 

.. literalinclude:: /../urbs/features/modelhelper.py
   :pyobject: commodity_balance

where the two functions introducing the partly balances for transmissions and
storages, respectively, are given by:

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: transmission_balance
.. literalinclude:: /../urbs/features/storage.py
   :pyobject: storage_balance

**Vertex Rule**: The vertex rule is the main constraint that has to be
satisfied for every commodity. It represents a version of
"Kirchhoff's current law" or local energy conservation. This constraint is
defined differently for each commodity type. The inequality requires, that any
imbalance (CB>0, CB<0) of a commodity :math:`c` in a site :math:`v` and support
timeframe :math:`y` at a timestep :math:`t` to be balanced by a corresponding
source term or demand. The rule is not defined for environmental or SupIm
commodities. The mathematical explanation of this rule is given in
:ref:`theory-min`.

In script ``model.py`` the constraint vertex rule is defined and calculated by
the following code fragments:

::

        m.res_vertex = pyomo.Constraint(
            m.tm, m.com_tuples,
            rule=res_vertex_rule,
            doc='storage + transmission + process + source + buy - sell == demand')


.. literalinclude:: /../urbs/model.py
   :pyobject: res_vertex_rule

where the two functions introducing the effects of Buy/Sell or DSM events,
respectively, are given by:

.. literalinclude:: /../urbs/features/BuySellPrice.py
   :pyobject: bsp_surplus
.. literalinclude:: /../urbs/features/dsm.py
   :pyobject: dsm_surplus


**Stock Per Step Rule**: The constraint stock per step rule applies only for
commodities of type "Stock" (:math:`c \in C_\text{st}`). This constraint limits
the amount of stock commodity :math:`c \in C_\text{st}`, that can be used by
the energy system in the site :math:`v` in support timeframe :math:`y` at the
timestep :math:`t`. This amount is limited by the product of the parameter
maximum stock supply limit per hour :math:`\overline{l}_{yvc}` and the timestep
length :math:`\Delta t`. The mathematical explanation of this rule is given in
:ref:`theory-min`.

In script ``model.py`` the constraint stock per step rule is defined and
calculated by the following code fragment:

::

    m.res_stock_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_stock_step_rule,
        doc='stock commodity input per step <= commodity.maxperstep')


.. literalinclude:: /../urbs/model.py
   :pyobject: res_stock_step_rule


**Total Stock Rule**: The constraint total stock rule applies only for
commodities of type "Stock" (:math:`c \in C_\text{st}`). This constraint limits
the amount of stock commodity :math:`c \in C_\text{st}`, that can be used
annually by the energy system in the site :math:`v` and support timeframe
:math:`y`. This amount is limited by the parameter maximum annual stock supply
limit per vertex :math:`\overline{L}_{yvc}`. The annual usage of stock
commodity is calculated by the sum of the products of the parameter weight
:math:`w` and the parameter stock commodity source term :math:`\rho_{yvct}`,
summed over all timesteps :math:`t \in T_m`. The mathematical explanation of
this rule is given in :ref:`theory-min`.

In script ``model.py`` the constraint total stock rule is defined and
calculated by the following code fragment:

::

    m.res_stock_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_stock_total_rule,
        doc='total stock commodity input <= commodity.max')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_stock_total_rule


**Sell Per Step Rule**: The constraint sell per step rule applies only for
commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint
limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be
sold by the energy system in the site :math:`v` in support timeframe :math:`y`
at the timestep :math:`t`. The limit is defined by the parameter maximum sell
supply limit per hour :math:`\overline{g}_{yvc}`. To satisfy this constraint,
the value of the variable sell commodity source term :math:`\varrho_{yvct}`
must be less than or equal to the value of the parameter maximum sell supply
limit per hour :math:`\overline{g}_{vc}` multiplied with the length of the
time steps :math:`\Delta t`. The mathematical explanation of this rule is given
in :ref:`theory-buysell`.

In script ``BuySellPrice.py`` the constraint sell per step rule is defined and
calculated by the following code fragment:
::

    m.res_sell_step = pyomo.Constraint(
       m.tm, m.com_tuples,
       rule=res_sell_step_rule,
       doc='sell commodity output per step <= commodity.maxperstep')

.. literalinclude:: /../urbs/features/BuySellPrice.py
   :pyobject: res_sell_step_rule

**Total Sell Rule**: The constraint total sell rule applies only for
commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint
limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be
sold annually by the energy system in the site :math:`v` and support timeframe
:math:`y`. The limit is defined by the parameter maximum annual sell supply
limit per vertex :math:`\overline{G}_{yvc}`. The annual usage of sell commodity
is calculated by the sum of the products of the parameter weight :math:`w` and
the parameter sell commodity source term :math:`\varrho_{yvct}`, summed over
all timesteps :math:`t \in T_m`. The mathematical explanation of this rule is
given in :ref:`theory-buysell`.

In script ``BuySellPrice.py`` the constraint total sell rule is defined and
calculated by the following code fragment:
::

    m.res_sell_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_sell_total_rule,
        doc='total sell commodity output <= commodity.max')

.. literalinclude:: /../urbs/features/BuySellPrice.py
   :pyobject: res_sell_total_rule

**Buy Per Step Rule**: The constraint buy per step rule applies only for
commodities of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits
the amount of buy commodity :math:`c \in C_\text{buy}`, that can be bought by
the energy system in the site :math:`v` in support timeframe :math:`y` at the
timestep :math:`t`. The limit is defined by the parameter maximum buy
supply limit per time step :math:`\overline{b}_{yvc}`. To satisfy this
constraint, the value of the variable buy commodity source term
:math:`\psi_{yvct}` must be less than or equal to the value of the parameter
maximum buy supply limit per time step :math:`\overline{b}_{vc}`, multiplied by
the length of the time steps :math:`\Delta t`. The mathematical explanation of
this rule is given in :ref:`theory-buysell`.

In script ``BuySellPrice.py`` the constraint buy per step rule is defined and
calculated by the following code fragment:
::

    m.res_buy_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_buy_step_rule,
        doc='buy commodity output per step <= commodity.maxperstep')

.. literalinclude:: /../urbs/features/BuySellPrice.py
   :pyobject: res_buy_step_rule

**Total Buy Rule**: The constraint total buy rule applies only for commodities
of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits the amount
of buy commodity :math:`c \in C_\text{buy}`, that can be bought annually by the
energy system in the site :math:`v` in support timeframe :math:`y`. The limit
is defined by the parameter maximum annual buy supply limit per vertex
:math:`\overline{B}_{yvc}`. To satisfy this constraint, the annual usage of buy
commodity must be less than or equal to the value of the parameter buy supply
limit per vertex :math:`\overline{B}_{vc}`. The annual usage of buy commodity
is calculated by the sum of the products of the parameter weight :math:`w` and
the parameter buy commodity source term :math:`\psi_{yvct}`, summed over all
modeled timesteps :math:`t \in T_m`. The mathematical explanation of this rule
is given in :ref:`theory-buysell`.

In script ``BuySellPrice.py`` the constraint total buy rule is defined and
calculated by the following code fragment:
::

    m.res_buy_total = pyomo.Constraint(
       m.com_tuples,
       rule=res_buy_total_rule,
       doc='total buy commodity output <= commodity.max')

.. literalinclude:: /../urbs/features/BuySellPrice.py
   :pyobject: res_buy_total_rule


**Environmental Output Per Step Rule**: The constraint environmental output per
step rule applies only for commodities of type "Env"
(:math:`c \in C_\text{env}`). This constraint limits the amount of
environmental commodity :math:`c \in C_\text{env}`, that can be released to
environment by the energy system in the site :math:`v` in support timeframe
:math:`y` at the timestep :math:`t`. The limit is defined by the parameter
maximum environmental output per time step :math:`\overline{m}_{yvc}`. To
satisfy this constraint, the negative value of the commodity balance for the
given environmental commodity :math:`c \in C_\text{env}` must be less than or
equal to the value of the parameter maximum environmental output per time step
:math:`\overline{m}_{vc}`, multiplied by the length of the time steps
:math:`\Delta t`. The mathematical explanation of this rule is given
in :ref:`theory-min`.

In script ``model.py`` the constraint environmental output per step rule is
defined and calculated by the following code fragment:
::

    m.res_env_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_env_step_rule,
        doc='environmental output per step <= commodity.maxperstep')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_env_step_rule


**Total Environmental Output Rule**: The constraint total environmental output
rule applies only for commodities of type "Env" ( :math:`c \in C_\text{env}`).
This constraint limits the amount of environmental commodity
:math:`c \in C_\text{env}`, that can be released to environment annually by the
energy system in the site :math:`v` in support timeframe :math:`y`. The limit
is defined by the parameter maximum annual environmental output limit per
vertex :math:`\overline{M}_{yvc}`. To satisfy this constraint, the annual
release of environmental commodity must be less than or equal to the value of
the parameter maximum annual environmental output :math:`\overline{M}_{vc}`.
The annual release of environmental commodity is calculated by the sum of the
products of the parameter weight :math:`w` and the negative value of commodity
balance function, summed over all modeled time steps :math:`t \in T_m`. The
mathematical explanation of this rule is given in :ref:`theory-min`.

In script ``model.py`` the constraint total environmental output rule is
defined and calculated by the following code fragment:
::

    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_env_total_rule

   
.. _sec-dsm-constr:

Demand Side Management Constraints
----------------------------------

The DSM equations are taken from the Paper of Zerrahn and Schill "On the
representation of demand-side management in power system models",
DOI: `10.1016/j.energy.2015.03.037 <http://dx.doi.org/10.1016/j.energy.2015.03.037>`_.


**DSM Variables Rule**: The DSM variables rule defines the relation between the
up- and downshifted DSM commodities. An upshift :math:`\delta_{yvct}^\text{up}`
in site :math:`v` and support timeframe :math:`y` of demand commodity :math:`c`
in time step :math:`t` can be compensated during a certain time step interval
:math:`[t-y_{yvc}/{\Delta t}, t+y_{yvc}/{\Delta t}]` by multiple downshifts
:math:`\delta_{t,tt,yvc}^\text{down}`. Here, :math:`y_{yvc}` represents the
allowable delay time of downshifts in hours, which is scaled into time steps by
dividing by the timestep length :math:`{\Delta t}`. Depending on the DSM
efficiency :math:`e_{yvc}`, an upshift in a DSM commodity may correspond to
multiple downshifts which sum to less than the original upshift. The
mathematical explanation of this rule is given in :ref:`theory-dsm`.
    
In script ``dsm.py`` the constraint DSM variables rule is defined by the
following code fragment:

::

    m.def_dsm_variables = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=def_dsm_variables_rule,
        doc='DSMup * efficiency factor n == DSMdo (summed)')	

.. literalinclude:: /../urbs/features/dsm.py
   :pyobject: def_dsm_variables_rule
        
        
**DSM Upward Rule**: The DSM upshift :math:`\delta_{yvct}^\text{up}` in site
:math:`v` and support timeframe :math:`y` of demand commodity :math:`c` in time
step :math:`t` is limited by the DSM maximal upshift per hour
:math:`\overline{K}_{yvc}^\text{up}`, multiplied by the length of the time
steps :math:`\Delta t`. The mathematical explanation of this rule is given in
:ref:`theory-dsm`.
    
In script ``dsm.py`` the constraint DSM upward rule is defined by the
following code fragment:

::

    m.res_dsm_upward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_upward_rule,
        doc='DSMup <= Cup (threshold capacity of DSMup)')

.. literalinclude:: /../urbs/features/dsm.py
   :pyobject: res_dsm_upward_rule
        
**DSM Downward Rule**: The total DSM downshift
:math:`\delta_{t,tt,yvc}^\text{down}` in site :math:`v` and support timeframe
:math:`y` of demand commodity :math:`c` in time step :math:`t` is limited by
the DSM maximal downshift per hour :math:`\overline{K}_{yvc}^\text{down}`,
multiplied by the length of the time steps :math:`\Delta t`. The mathematical
explanation of this rule is given in :ref:`theory-dsm`.
    
In script ``dsm.py`` the constraint DSM downward rule is defined by the
following code fragment:

::

    m.res_dsm_downward = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_downward_rule,
        doc='DSMdo (summed) <= Cdo (threshold capacity of DSMdo)')

.. literalinclude:: /../urbs/features/dsm.py
   :pyobject: res_dsm_downward_rule
        

**DSM Maximum Rule**: The DSM maximum rule limits the shift of one DSM unit in
site :math:`v` in support timeframe :math:`y` of demand commodity :math:`c` in
time step :math:`t`. The mathematical explanation of this rule is given in
:ref:`theory-dsm`.
   
In script ``dsm.py`` the constraint DSM maximum rule is defined by the
following code fragment:

::

    m.res_dsm_maximum = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_maximum_rule,
        doc='DSMup + DSMdo (summed) <= max(Cup,Cdo)')

.. literalinclude:: /../urbs/features/dsm.py
   :pyobject: res_dsm_maximum_rule

**DSM Recovery Rule**: The DSM recovery rule limits the upshift in site
:math:`v` and support timeframe :math:`y` of demand commodity :math:`c` during
a set recovery period :math:`o_{yvc}`. Since the recovery period
:math:`o_{yvc}` is input as hours, it is scaled into time steps by dividing it
by the length of the time steps :math:`\Delta t`. The mathematical explanation
of this rule is given in :ref:`theory-dsm`.
    
In script ``dsm.py`` the constraint DSM Recovery rule is defined by the
following code fragment:

::

    m.res_dsm_recovery = pyomo.Constraint(
        m.tm, m.dsm_site_tuples, 
        rule=res_dsm_recovery_rule,
        doc='DSMup(t, t + recovery time R) <= Cup * delay time L')

.. literalinclude:: /../urbs/features/dsm.py
   :pyobject: res_dsm_recovery_rule     
  
        
            
Global Environmental Constraint
-------------------------------

**Global CO2 Limit Rule**: The constraint global CO2 limit rule applies to the
whole energy system in one support timeframe :math:`y`, that is to say it
applies to every site and timestep. This constraints restricts the total amount
of CO2 to environment. The constraint states that the sum of released CO2
across all sites :math:`v\in V` and timesteps :math:`t \in t_m` must be less
than or equal to the parameter maximum global annual CO2 emission limit
:math:`\overline{L}_{CO_{2},y}`, where the amount of released CO2 in a single
site :math:`v` at a single timestep :math:`t` is calculated by the product of
commodity balance of environmental commodities :math:`\mathrm{CB}(y,v,CO_{2},t)`
and the parameter weight :math:`w`. This constraint is skipped if the value of
the parameter :math:`\overline{L}_{CO_{2}}` is set to ``inf``. The mathematical
explanation of this rule is given in :ref:`theory-min`.

In script ``model.py`` the constraint annual global CO2 limit rule is defined
and calculated by the following code fragment:

.. literalinclude:: /../urbs/model.py
   :pyobject: res_global_co2_limit_rule

**Global CO2 Budget Rule**: The constraint global CO2 budget rule applies to
the whole energy system over the entire modeling horizon, that is to say it
applies to every support timeframe, site and timestep. This constraints
restricts the total amount of CO2 to environment. The constraint states that
the sum of released CO2 across all support timeframe :math:`y\in Y`, sites
:math:`v\in V` and timesteps :math:`t \in t_m` must be less than or equal to
the parameter maximum global CO2 emission budget
:math:`\overline{\overline{L}}_{CO_{2},y}`, where the amount of released CO2 in
a single support timeframe :math:`y` in a single site :math:`v` and at a single
timestep :math:`t` is calculated by the product of the commodity balance of
environmental commodities :math:`\mathrm{CB}(y,v,CO_{2},t)` and the parameter
weight :math:`w`. This constraint is skipped if the value of the parameter
:math:`\overline{\overline{L}}_{CO_{2}}` is set to ``inf``. The mathematical
explanation of this rule is given in :ref:`theory-intertemp`.

In script ``model.py`` the constraint global CO2 budget is defined and
calculated by the following code fragment:

.. literalinclude:: /../urbs/model.py
   :pyobject: res_global_co2_budget_rule
