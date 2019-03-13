.. module urbs

Process Constraints
^^^^^^^^^^^^^^^^^^^

**Process Capacity Rule**: The constraint process capacity rule defines the 
variable total process capacity :math:`\kappa_{yvp}`. The variable total
process  capacity is defined by the constraint as the sum of the parameter
process  capacity installed :math:`K_{vp}` and the variable new process
capacity  :math:`\hat{\kappa}_{yvp}`. The mathematical explanation of this rule
is given in :ref:`theory-min`.

In script ``model.py`` the constraint process capacity rule is defined and
calculated by the following code fragment:

::

    m.def_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=def_process_capacity_rule,
        doc='total process capacity = inst-cap + new capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_process_capacity_rule

**Process Input Rule**: The constraint process input rule defines the variable
process input commodity flow :math:`\epsilon_{yvcpt}^\text{in}`. The variable
process input commodity flow is defined by the constraint as the product of the
variable process throughput :math:`\tau_{yvpt}` and the parameter process input
ratio :math:`r_{ypc}^\text{in}`.The mathematical explanation of this rule is
given in :ref:`theory-min`.

In script ``model.py`` the constraint process input rule is defined and
calculated by the following code fragment:

::

    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples - m.pro_partial_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_process_input_rule

**Process Output Rule**: The constraint process output rule defines the variable
process output commodity flow :math:`\epsilon_{yvcpt}^\text{out}`. The variable
process output commodity flow is defined by the constraint as the product of
the variable process throughput :math:`\tau_{yvpt}` and the parameter process
output ratio :math:`r_{ypc}^\text{out}`. The mathematical explanation of this
rule is given in :ref:`theory-min`.

In script ``model.py`` the constraint process output rule is defined and
calculated by the following code fragment:

::

    m.def_process_output = pyomo.Constraint(
        m.tm, (m.pro_output_tuples - m.pro_partial_output_tuples -
               m.pro_timevar_output_tuples),
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_process_output_rule

**Intermittent Supply Rule**: The constraint intermittent supply rule defines
the variable process input commodity flow :math:`\epsilon_{yvcpt}^\text{in}`
for processes :math:`p` that use a supply intermittent commodity
:math:`c \in C_\text{sup}` as input. Therefore this constraint only applies if
a commodity is an intermittent supply commodity :math:`c \in C_\text{sup}`. The
variable process input commodity flow is defined by the constraint as the
product of the variable total process capacity :math:`\kappa_{yvp}` and the
parameter intermittent supply capacity factor :math:`s_{yvct}`, scaled by the 
size of the time steps :math: `\Delta t`. The mathematical explanation of this
rule is given in :ref:`theory-min`.

In script ``model.py`` the constraint intermittent supply rule is defined and
calculated by the following code fragment:

::

    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_intermittent_supply_rule

**Process Throughput By Capacity Rule**: The constraint process throughput by
capacity rule limits the variable process throughput :math:`\tau_{yvpt}`. This
constraint prevents processes from exceeding their capacity. The constraint
states that the variable process throughput must be less than or equal to the
variable total process capacity :math:`\kappa_{yvp}`, scaled by the size
of the time steps :math: `\Delta t`. The mathematical explanation of this rule
is given in :ref:`theory-min`.

In script ``model.py`` the constraint process throughput by capacity rule is
defined and calculated by the following code fragment:

::

    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_throughput_by_capacity_rule

**Process Throughput Gradient Rule**: The constraint process throughput
gradient rule limits the process power gradient
:math:`\left| \tau_{yvpt} - \tau_{yvp(t-1)} \right|`. This constraint prevents
processes from exceeding their maximal possible change in activity from one
time step to the next. The constraint states that absolute power gradient must
be less than or equal to the maximal power gradient :math:`\overline{PG}_{yvp}`
parameter (scaled to capacity and by time step duration). The mathematical
explanation of this rule is given in :ref:`theory-min`.

In script ``model.py`` the constraint process throughput gradient rule is split
into 2 parts and defined and calculated by the following code fragments:
::

    m.res_process_maxgrad_lower = pyomo.Constraint(
        m.tm, m.pro_maxgrad_tuples,
        rule=res_process_maxgrad_lower_rule,
        doc='throughput may not decrease faster than maximal gradient')
    m.res_process_maxgrad_upper = pyomo.Constraint(
        m.tm, m.pro_maxgrad_tuples,
        rule=res_process_maxgrad_upper_rule,
        doc='throughput may not increase faster than maximal gradient')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_maxgrad_lower_rule
.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_maxgrad_upper_rule

**Process Capacity Limit Rule**: The constraint process capacity limit rule
limits the variable total process capacity :math:`\kappa_{yvp}`. This
constraint restricts a process :math:`p` in a site :math:`v` and support
timeframe :math:`y` from having more total capacity than an upper bound and
having less than a lower bound. The constraint states that the variable total
process capacity :math:`\kappa_{yvp}` must be greater than or equal to the
parameter process capacity lower bound :math:`\underline{K}_{yvp}` and less
than or equal to the parameter process capacity upper bound
:math:`\overline{K}_{yvp}`. The mathematical explanation of this rule is given
in :ref:`theory-min`.

In script ``model.py`` the constraint process capacity limit rule is defined
and calculated by the following code fragment:

::

    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_capacity_rule


**Sell Buy Symmetry Rule**: The constraint sell buy symmetry rule defines the
total process capacity :math:`\kappa_{yvp}` of a process :math:`p` in a site
:math:`v` and support timeframe :math:`y` that uses either sell or buy
commodities ( :math:`c \in C_\text{sell} \vee C_\text{buy}`), therefore this
constraint only applies to processes that use sell or buy commodities. The
constraint states that the total process capacities :math:`\kappa_{yvp}` of
processes that use complementary buy and sell commodities must be equal. Buy
and sell commodities are complementary, when a commodity :math:`c` is an output
of a process where the buy commodity is an input, and at the same time the
commodity :math:`c` is an input commodity of a process where the sell commodity
is an output. The mathematical explanation of this rule is given in
:ref:`theory-buysell`.

In script ``BuySellPrice.py`` the constraint sell buy symmetry rule is defined
and calculated by the following code fragment:

::

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='total power connection capacity must be symmetric in both '
            'directions')

.. literalinclude:: /../urbs/features/BuySellPrice.py
   :pyobject: res_sell_buy_symmetry_rule


**Process time variable output rule**: This constraint multiplies the process
efficiency with the parameter time series :math:`f_{yvpt}^\text{out}`. The
process output for all commodities is thus manipulated depending on time. This
constraint is not valid for environmental commodities since these are typically
linked to an input commodity flow rather than an output commodity flow. The
mathematical explanation of this rule is given in :ref:`theory-TVE`.

In script ``TimeVarEff.py`` the constraint process time variable output rule is
defined and calculated by the following code fragment:

::

    m.def_process_timevar_output = pyomo.Constraint(
        m.tm, m.pro_timevar_output_tuples,
        rule=def_pro_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')

.. literalinclude:: /../urbs/features/TimeVarEff.py
   :pyobject: def_pro_timevar_output_rule

.. _sec-partial-startup-constr:


Process Constraints for partial operation
-----------------------------------------
The process constraints for partial operation described in the following are
only activated if in the input file there is a value set in the column
**ratio-min** for an **input commodity** in the **process-commodity** sheet for
the process in question. Values for **output commodities** in the **ratio_min**
column do not have any effect.

The partial load feature can only be used for processes that are never meant
to be shut down and are always operating only between a given part load state
and full load. It is important to understand that this partial load formulation
can only work if its accompanied by a non-zero value for the minimum partial
load fraction :math:`\underline{P}_{yvp}`.

**Throughput by Min fraction Rule**: This constraint limits the minimal
operational state of a process downward, making sure that the minimal part load
fraction is honored. The mathematical explanation of this rule is given in
:ref:`theory-min`.

In script ``model.py`` this constraint is defined and calculated by the
following code fragment:

::

    m.res_throughput_by_capacity_min = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_capacity_min_rule,
        doc='cap_pro * min-fraction <= tau_pro')
        
.. literalinclude:: /../urbs/model.py
   :pyobject: res_throughput_by_capacity_min_rule

**Partial Process Input Rule**: The link between operational state
:math:`tau_{yvpt}` and commodity in/outputs is changed from a simple
linear behavior to a more complex one. Instead of constant in- and output
ratios these are now interpolated linearly between the value for full operation
:math:`r^{\text{in/out}}_{yvp}` at full load and the minimum in/output ratios
:math:`\underline{r}^{\text{in/out}}_{yvp}` at the minimum operation point. The
mathematical explanation of this rule is given in :ref:`theory-min`.   

In script `model.py` this expression is written in the following way for the
input ratio (and analogous for the output ratios):
::

    m.def_partial_process_input = pyomo.Constraint(
        m.tm, m.pro_partial_input_tuples,
        rule=def_partial_process_input_rule,
        doc='e_pro_in = cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
                     '+ tau_pro * (R - min_fraction * r) / (1 - min_fraction)')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_partial_process_input_rule

In case of a process where also a time variable output efficiency is given the
code for the output changes to.
::

    m.def_process_partial_timevar_output = pyomo.Constraint(
        m.tm, m.pro_partial_output_tuples & m.pro_timevar_output_tuples,
        rule=def_pro_partial_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')

.. literalinclude:: /../urbs/features/TimeVarEff.py
   :pyobject: def_pro_partial_timevar_output_rule