.. module urbs

Process Constraints
^^^^^^^^^^^^^^^^^^^

**Process Capacity Rule**: The constraint process capacity rule defines the 
variable total process capacity :math:`\kappa_{vp}`. The variable total process 
capacity is defined by the constraint as the sum of the parameter process 
capacity installed :math:`K_{vp}` and the variable new process capacity 
:math:`\hat{\kappa}_{vp}`. In mathematical notation this is expressed as: 

.. math::

	\forall v\in V, p\in P\colon\ \kappa_{vp} = K_{vp} + \hat{\kappa}_{vp}

In script ``model.py`` the constraint process capacity rule is defined and calculated by the following code fragment:

::

    m.def_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=def_process_capacity_rule,
        doc='total process capacity = inst-cap + new capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_process_capacity_rule

**Process Input Rule**: The constraint process input rule defines the variable
process input commodity flow :math:`\epsilon_{vcpt}^\text{in}`. The variable
process input commodity flow is defined by the constraint as the product of the
variable process throughput :math:`\tau_{vpt}` and the parameter process input
ratio :math:`r_{pc}^\text{in}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon\ \epsilon^\text{in}_{vcpt} =
    \tau_{vpt} r^\text{in}_{pc}


In script ``model.py`` the constraint process input rule is defined and calculated by the following code fragment:

::

    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples - m.pro_partial_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_process_input_rule

**Process Output Rule**: The constraint process output rule defines the variable
process output commodity flow :math:`\epsilon_{vcpt}^\text{out}`. The variable
process output commodity flow is defined by the constraint as the product of the
variable process throughput :math:`\tau_{vpt}` and the parameter process output
ratio :math:`r_{pc}^\text{out}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon\ \epsilon^\text{out}_{vpct} =
    \tau_{vpt} r^\text{out}_{pc}

In script ``model.py`` the constraint process output rule is defined and calculated by the following code fragment:

::

    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_process_output_rule

**Intermittent Supply Rule**: The constraint intermittent supply rule defines
the variable process input commodity flow :math:`\epsilon_{vcpt}^\text{in}` for
processes :math:`p` that use a supply intermittent commodity
:math:`c \in C_\text{sup}` as input. Therefore this constraint only applies if a
commodity is an intermittent supply commodity :math:`c \in C_\text{sup}`. The
variable process input commodity flow is defined by the constraint as the
product of the variable total process capacity :math:`\kappa_{vp}` and the
parameter intermittent supply capacity factor :math:`s_{vct}`, scaled by the 
size of the time steps :math: `\Delta t`. In mathematical notation this is expressed 
as:

.. math::

	\forall v\in V, p\in P, c\in C_\text{sup}, t\in T_m\colon\
    \epsilon^\text{in}_{vpct} = \kappa_{vp} s_{vct} \Delta t


In script ``model.py`` the constraint intermittent supply rule is defined and calculated by the following code fragment:

::

    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_intermittent_supply_rule

**Process Throughput By Capacity Rule**: The constraint process throughput by
capacity rule limits the variable process throughput :math:`\tau_{vpt}`. This
constraint prevents processes from exceeding their capacity. The constraint
states that the variable process throughput must be less than or equal to the
variable total process capacity :math:`\kappa_{vp}`, scaled by the size
of the time steps :math: `\Delta t`. In mathematical notation this is expressed as:

.. math::

    \forall v\in V, p\in P, t\in T_m\colon\ \tau_{vpt} \leq \kappa_{vp} \Delta t

In script ``model.py`` the constraint process throughput by capacity rule is defined and calculated by the following code fragment:

::

    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_throughput_by_capacity_rule

**Process Throughput Gradient Rule**: The constraint process throughput gradient
rule limits the process power gradient
:math:`\left| \tau_{vpt} - \tau_{vp(t-1)} \right|`. This constraint prevents
processes from exceeding their maximal possible change in activity from one time
step to the next. The constraint states that absolute power gradient must be
less than or equal to the maximal power gradient :math:`\overline{PG}_{vp}`
parameter (scaled to capacity and by time step duration). In mathematical
notation this is expressed as:

.. math::

    \forall v\in V, p\in P, t\in T_m\colon\ \left| \tau_{vpt} - \tau_{vp(t-1)}
    \right| \leq  \kappa_{vp} \overline{PG}_{vp} \Delta t

In script ``model.py`` the constraint process throughput gradient rule is split
into 2 parts and defined and calculated by the following code fragment:
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
limits the variable total process capacity :math:`\kappa_{vp}`. This constraint
restricts a process :math:`p` in a site :math:`v` from having more total
capacity than an upper bound and having less than a lower bound. The constraint
states that the variable total process capacity :math:`\kappa_{vp}` must be
greater than or equal to the parameter process capacity lower bound
:math:`\underline{K}_{vp}` and less than or equal to the parameter process
capacity upper bound :math:`\overline{K}_{vp}`. In mathematical notation this
is expressed as:


.. math::

    \forall v\in V, p\in P\colon\  \underline{K}_{vp} \leq \kappa_{vp} \leq
    \overline{K}_{vp}

In script ``model.py`` the constraint process capacity limit rule is defined and calculated by the following code fragment:

::

    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_capacity_rule


**Sell Buy Symmetry Rule**: The constraint sell buy symmetry rule defines the
total process capacity :math:`\kappa_{vp}` of a process :math:`p` in a site
:math:`v` that uses either sell or buy commodities ( :math:`c \in C_\text{sell}
\vee C_\text{buy}`), therefore this constraint only applies to processes that
use sell or buy commodities. The constraint states that the total process
capacities :math:`\kappa_{vp}` of processes that use complementary buy and sell
commodities must be equal. Buy and sell commodities are complementary, when a
commodity :math:`c` is an output of a process where the buy commodity is an
input, and at the same time the commodity :math:`c` is an input commodity of a
process where the sell commodity is an output.

In script ``model.py`` the constraint sell buy symmetry rule is defined and
calculated by the following code fragment:

::

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='total power connection capacity must be symmetric in both directions')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_sell_buy_symmetry_rule


.. _sec-partial-startup-constr:

Process Constraints for partial operation
-----------------------------------------
The process constraints for partial operation described in the following are
only activated if in the input file there is a value set in the column
**ratio-min** for an **input commodity** in the **process-commodity** sheet for
the process in question. Values for the **output commodities** do not have any
effect.

The partial load feature can only be used for processes that are never meant
to be shut down and are always operating only between a given part load state
and full load. It is important to understand that this partial load formulation
can only work if its accompanied by a sensible value for both the minimum
partial load fraction :math:`\underline{P}_{vp}`.

**Throughput by Min fraction Rule**: This constraint limits the minimal
operational state of a process downward, making sure that the minimal part load
fraction is honored.

.. math::
    \forall t\in T_\text{m}, (v, p)\in P_v^\text{partial}\colon\ 
    \tau_{vpt} \geq \underline{P}_{vp} (\kappa_{vp} \Delta t)

    
And here as code:
::

    m.res_throughput_by_capacity_min = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_capacity_min_rule,
        doc='cap_pro * min-fraction <= tau_pro')
        
.. literalinclude:: /../urbs/model.py
   :pyobject: res_throughput_by_capacity_min_rule

**Partial Process Input Rule**: In energy system modelling, the simplest way to
represent an energy conversion process is to assume a linear input-output
relationship with a flat efficiency parameter :math:`\eta`:

.. math::
       \epsilon_{out} = \epsilon_{in} \cdot \eta


Which means there is only one efficiency :math:`\eta` during the whole process,
i.e. it remains constant during the electricity production. But in fact, most
of the powerplants do not operate at a certain efficiency and the operation
load varies along time. Therefore the regular single efficiency :math:`\eta`
is replaced by a set of input ratios (:math:`r^\text{in}`) and output
ratios (:math:`r^\text{out}`) in urbs. And both ratios relate to the process
throughput :math:`\tau`:

.. math::
       \epsilon_{vpct}^\text{in} &= \tau_{vpt} r_{pc}^\text{in}
       
       \epsilon_{vpct}^\text{out} &= \tau_{vpt} r_{pc}^\text{out}
       
If input or output ratios are set to 1 the process input or output
(:math:`\epsilon_{vpct}^\text{in, out}`) is equal to the process throughput
(:math:`\tau_{vpt}`). The process efficiency :math:`\eta` can be represented as
follows:

.. math::
    \eta = \frac{\epsilon_{vpct}^\text{out}}{\epsilon_{vpct}^\text{in}} =
    \frac{\tau_{vpt}}{\epsilon_{vpct}^\text{in}}

For a part load case the input ratio and, if specified, the output ratio of the
process is a function of :math:`\tau_{vpt}`:

.. math::
    \forall t\in T_\text{m}, (v, p, c)\in C_{vp}^\text{in,partial}\colon\  
    \epsilon_{vpct}^\text{in} = 
      (\kappa_{vp} \Delta t) \cdot \frac{
          \underline{r}_{pc}^\text{in} - r_{pc}^\text{in}}{
          1 - \underline{P}_{vp}} \cdot \underline{P}_{vp} 
    + \tau_{vpt} \cdot \frac{
        r_{pc}^\text{in} - 
          \underline{P}_{vp} 
          \underline{r}_{pc}^\text{in}}{
        1 - \underline{P}_{vp}}

In the program code this expression is written in the following way for the
input ratio:
::

    m.def_partial_process_input = pyomo.Constraint(
        m.tm, m.pro_partial_input_tuples,
        rule=def_partial_process_input_rule,
        doc='e_pro_in = cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
                     '+ tau_pro * (R - min_fraction * r) / (1 - min_fraction)')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_partial_process_input_rule

For a given process capacity :math:`\kappa_{vp}` the efficiency of the process
is then only dependent on the process throughput :math:`\tau_{vpt}`. The
input (or output) ratio varies then linearly between :math:`r^{in}_{pc}` and
:math:`r^{in}_{pc}` for throughputs in the desired operational region, i.e.,
between full load :math:`\kappa_{vp} \Delta t` and the minimal part load state
:math:`\underline P_{vp}(\kappa_{vp} \Delta t)`. The efficiency is then of the form:

.. math::
    \eta = \frac{\epsilon_{vpct}^\text{out}}{\epsilon_{vpct}^\text{in}} =
    \frac{a + b \tau_{vpt}}{c + d \tau_{vpt}}
