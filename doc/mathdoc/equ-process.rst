.. module urbs

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

.. literalinclude:: /../urbs.py
   :pyobject: def_process_capacity_rule

**Process Input Rule**: The constraint process input rule defines the variable process input commodity flow :math:`\epsilon_{vcpt}^\text{in}`. The variable process input commodity flow is defined by the constraint as the product of the variable process throughput :math:`\tau_{vpt}` and the parameter process input ratio :math:`r_{pc}^\text{in}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \epsilon^\text{in}_{vcpt} &= \tau_{vpt} r^\text{in}_{pc}

In script ``urbs.py`` the constraint process input rule is defined and calculated by the following code fragment:
::

    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples - m.pro_partial_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')

.. literalinclude:: /../urbs.py
   :pyobject: def_process_input_rule

**Process Output Rule**: The constraint process output rule defines the variable process output commodity flow :math:`\epsilon_{vcpt}^\text{out}`. The variable process output commodity flow is defined by the constraint as the product of the variable process throughput :math:`\tau_{vpt}` and the parameter process output ratio :math:`r_{pc}^\text{out}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \epsilon^\text{out}_{vpct} &= \tau_{vpt} r^\text{out}_{pc}

In script ``urbs.py`` the constraint process output rule is defined and calculated by the following code fragment:
::

    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

.. literalinclude:: /../urbs.py
   :pyobject: def_process_output_rule

**Intermittent Supply Rule**: The constraint intermittent supply rule defines the variable process input commodity flow :math:`\epsilon_{vcpt}^\text{in}` for processes :math:`p` that use a supply intermittent commodity :math:`c \in C_\text{sup}` as input. Therefore this constraint only applies if a commodity is an intermittent supply commodity :math:`c \in C_\text{sup}`. The variable process input commodity flow is defined by the constraint as the product of the variable total process capacity :math:`\kappa_{vp}` and the parameter intermittent supply capacity factor :math:`s_{vct}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, c\in C_\text{sup}, t\in T_m\colon \qquad & \qquad \epsilon^\text{in}_{vpct} &= \kappa_{vp} s_{vct}

In script ``urbs.py`` the constraint intermittent supply rule is defined and calculated by the following code fragment:
::

    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')

.. literalinclude:: /../urbs.py
   :pyobject: def_intermittent_supply_rule

**Process Throughput By Capacity Rule**: The constraint process throughput by capacity rule limits the variable process throughput :math:`\tau_{vpt}`. This constraint prevents processes from exceeding their capacity. The constraint states that the variable process throughput must be less than or equal to the variable total process capacity :math:`\kappa_{vp}`. In mathematical notation this is expressed as:

.. math::

    \forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \tau_{vpt} &\leq \kappa_{vp}

In script ``urbs.py`` the constraint process throughput by capacity rule is defined and calculated by the following code fragment:
::

    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')

.. literalinclude:: /../urbs.py
   :pyobject: res_process_throughput_by_capacity_rule

**Process Throughput Gradient Rule**: The constraint process throughput gradient rule limits the process power gradient :math:`\left| \tau_{vpt} - \tau_{vp(t-1)} \right|`. This constraint prevents processes from exceeding their maximal possible change in activity from one time step to the next. The constraint states that absolute power gradient must be less than or equal to the maximal power gradient :math:`\overline{PG}_{vp}` parameter (scaled to capacity and by time step duration). In mathematical notation this is expressed as:

.. math::

    \forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \left| \tau_{vpt} - \tau_{vp(t-1)} \right| &\leq  \kappa_{vp} \overline{PG}_{vp} \Delta t

In script ``urbs.py`` the constraint process throughput gradient rule is defined and calculated by the following code fragment:
::

    m.res_process_throughput_gradient = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_gradient_rule,
        doc='process throughput gradient <= maximal gradient')

.. literalinclude:: /../urbs.py
   :pyobject: res_process_throughput_gradient_rule

**Process Capacity Limit Rule**: The constraint process capacity limit rule limits the variable total process capacity :math:`\kappa_{vp}`. This constraint restricts a process :math:`p` in a site :math:`v` from having more total capacity than an upper bound and having less than a lower bound. The constraint states that the variable total process capacity :math:`\kappa_{vp}` must be greater than or equal to the parameter process capacity lower bound :math:`\underline{K}_{vp}` and less than or equal to the parameter process capacity upper bound :math:`\overline{K}_{vp}`. In mathematical notation this is expressed as:

.. math::

    \forall v\in V, p\in P\colon \qquad & \qquad  \underline{K}_{vp} \leq \kappa_{vp} \leq \overline{K}_{vp}

In script ``urbs.py`` the constraint process capacity limit rule is defined and calculated by the following code fragment:
::

    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

.. literalinclude:: /../urbs.py
   :pyobject: res_process_capacity_rule

**Sell Buy Symmetry Rule**: The constraint sell buy symmetry rule defines the total process capacity :math:`\kappa_{vp}` of a process :math:`p` in a site :math:`v` that uses either sell or buy commodities ( :math:`c \in C_\text{sell} \vee C_\text{buy}`), therefore this constraint only applies to processes that use sell or buy commodities. The constraint states that the total process capacities :math:`\kappa_{vp}` of processes that use complementary buy and sell commodities must be equal. Buy and sell commodities are complementary, when a commodity :math:`c` is an output of a process where the buy commodity is an input, and at the same time the commodity :math:`c` is an input commodity of a process where the sell commodity is an output.

In script ``urbs.py`` the constraint sell buy symmetry rule is defined and calculated by the following code fragment:
::

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='total power connection capacity must be symmetric in both directions')

.. literalinclude:: /../urbs.py
   :pyobject: res_sell_buy_symmetry_rule


.. _sec-partial-startup-constr:

Partial & Startup Process Constraints
-------------------------------------

Start

**Throughput by Online Capacity Min Rule**


.. math::
    \forall

::

    m.res_throughput_by_online_capacity_min = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_online_capacity_min_rule,
        doc='cap_online * min-fraction <= tau_pro')
        
.. literalinclude:: /../urbs.py
   :pyobject: res_throughput_by_online_capacity_min_rule


**Throughput by Online Capacity Max Rule**
   
::

    m.res_throughput_by_online_capacity_max = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_online_capacity_max_rule,
        doc='tau_pro <= cap_online')
        
.. literalinclude:: /../urbs.py
   :pyobject: res_throughput_by_online_capacity_max_rule

   

**Partial Process Input Rule**
   
::

    m.def_partial_process_input = pyomo.Constraint(
        m.tm, m.pro_partial_input_tuples,
        rule=def_partial_process_input_rule,
        doc='e_pro_in = cap_online * min_fraction * (r - R) / (1 - min_fraction)'
                        '+ tau_pro * (R - min_fraction * r) / (1 - min_fraction)')

.. literalinclude:: /../urbs.py
   :pyobject: def_partial_process_input_rule


**Online Capacity By Process Capacity** limits the value of the online capacity :math:`\omega_{vpt}` by the total installed process capacity :math:`\kappa_{vp}`:


.. math::

	\forall \left.v\in V, p\in P\right|_{(v,p)\in PP},t\in T_m\colon\quad 
	\omega_{vpt} \leq \kappa_{vp}
   
::

    m.res_cap_online_by_cap_pro = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_cap_online_by_cap_pro_rule,
        doc='online capacity <= process capacity')

.. literalinclude:: /../urbs.py
   :pyobject: res_cap_online_by_cap_pro_rule 

::

    m.def_startup_capacity = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=def_startup_capacity_rule,
        doc='startup_capacity[t] >= cap_online[t] - cap_online[t-1]')

.. literalinclude:: /../urbs.py
   :pyobject: def_startup_capacity_rule
        