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
time step to the next. The constraint states that the absolute power gradient must
be less than or equal to the maximal power ramp up gradient 
:math:`overline{PG}_{yvp}^\text{up}` parameter when increasing power or to the
maximal power ramp down gradient :math:`\overline{PG}_{yvp}^\text{up}` parameter
(both scaled to capacity and by time step duration). The mathematical
explanation of this rule is given in :ref:`theory-min`.

In script ``model.py`` the constraint process throughput gradient rule is split
into 2 parts and defined and calculated by the following code fragments:
::

    m.res_process_rampdown = pyomo.Constraint(
        m.tm, m.pro_rampdowngrad_tuples,
        rule=res_process_rampdown_rule,
        doc='throughput may not decrease faster than maximal ramp down gradient')
    m.res_process_rampup = pyomo.Constraint(
        m.tm, m.pro_rampupgrad_tuples,
        rule=res_process_rampup_rule,
        doc='throughput may not increase faster than maximal ramp up gradient')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_rampdown_rule
.. literalinclude:: /../urbs/model.py
   :pyobject: res_process_rampup_rule

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
mathematical explanation of this rule is given in :ref:`theory-AP`.

In script ``TimeVarEff.py`` the constraint process time variable output rule is
defined and calculated by the following code fragment:

::

    m.def_process_timevar_output = pyomo.Constraint(
        m.tm, m.pro_timevar_output_tuples,
        rule=def_pro_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_pro_timevar_output_rule

.. _sec-partial-startup-constr:


Process Constraints for partial operation
-----------------------------------------
The process constraints for partial operation described in the following are
only activated if in the input file there is a value set in the column
**ratio-min** for an **input commodity** or for an **output commodity** in the
**process-commodity** sheet for the process in question.

It is important to understand that this partial load formulation
can only work if its accompanied by a non-zero value for the minimum partial
load fraction :math:`\underline{P}_{yvp}`.

Without activating the on/off feature in the **process** sheet, the partial load
feature can only be used for processes that are never meant to be shut down and
are always operating only between a given part load state and full load. Please
see the next chapter for the combined on/off and partial operation features.

**Throughput by Min fraction Rule**: This constraint limits the minimal
operational state of a process downward, making sure that the minimal part load
fraction is honored. The mathematical explanation of this rule is given in
:ref:`theory-AP`.

In script ``AdvancedProcesses.py`` this constraint is defined and calculated by the
following code fragment:

::

    m.res_throughput_by_capacity_min = pyomo.Constraint(
        m.tm, m.pro_partial_tuples,
        rule=res_throughput_by_capacity_min_rule,
        doc='cap_pro * min-fraction <= tau_pro')
        
.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_throughput_by_capacity_min_rule

**Partial Process Input Rule**: The link between operational state
:math:`tau_{yvpt}` and commodity in/outputs is changed from a simple
linear behavior to a more complex one. Instead of constant in- and output
ratios these are now interpolated linearly between the value for full operation
:math:`r^{\text{in/out}}_{yvp}` at full load and the minimum in/output ratios
:math:`\underline{r}^{\text{in/out}}_{yvp}` at the minimum operation point. The
mathematical explanation of this rule is given in :ref:`theory-AP`.   

In script `model.py` this expression is written in the following way for the
input ratio (and analogous for the output ratios):
::

    m.def_partial_process_input = pyomo.Constraint(
        m.tm, m.pro_partial_input_tuples,
        rule=def_partial_process_input_rule,
        doc='e_pro_in = cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
                     '+ tau_pro * (R - min_fraction * r) / (1 - min_fraction)')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_partial_process_input_rule

In case of a process where also a time variable output efficiency is given the
code for the output changes to.
::

    m.def_process_partial_timevar_output = pyomo.Constraint(
        m.tm, m.pro_partial_output_tuples & m.pro_timevar_output_tuples,
        rule=def_pro_partial_timevar_output_rule,
        doc='e_pro_out = tau_pro * r_out * eff_factor')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_pro_partial_timevar_output_rule
 
 
Process Constraints for the on/off feature
------------------------------------------
The process constraints for the on/off feature described in this chapter are
only activated if, in the input file, the value „1” is set is set in the 
column **on-off** for a process in the **process** sheet.

**Process Throughput and On/Off Coupling Rule**: These two constraints couple
the variables process throughput :math:`\tau_{yvpt}` and process on/off marker
:math:`\omicron_{yvpt}`. This is done by turning the marker on (boolean value 1)
when the throughput is greater than the minimum load of the process.The
mathematical explanation of this rule is given in :ref:`theory-AP`.

In script ``AdvancedProcesses.py`` this constraint is defined and calculated by the
following code fragment:
::

    m.res_throughput_by_on_off_lower = pyomo.Constraint(
        m.tm, m.pro_on_off_tuples | m.pro_partial_on_off_tuples,
        rule=res_throughput_by_on_off_lower_rule,
        doc='tau_pro >= min-fraction * cap_pro * on_off')
    m.res_throughput_by_on_off_upper = pyomo.Constraint(
        m.tm, m.pro_on_off_tuples | m.pro_partial_on_off_tuples,
        rule=res_throughput_by_on_off_upper_rule,
        doc='tau_pro <='
            'cap_pro * on_off + min-fraction * cap_pro * (1 - on_off)')
            
.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_throughput_by_on_off_lower
.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_throughput_by_on_off_upper

**Process On/Off Output Rule**: This constraint modifies the process output 
commodity flow :math:`\epsilon_{yvcpt}^\text{out}` when compared to the 
original version without the on/off feature in two ways by differentiating 
between the output **commodity type** :math:`q`. When the **commodity type**
is ``Env``, the output remains the same as without the on/off feature. Otherwise, 
the original output equation is multiplied with the variable process on/off 
marker :math:`\omicron_{yvpt}`. The mathematical explanation of this rule
is given in :ref:`theory-AP`.

In script ``AdvancedProcesses.py`` the constraint process on/off output rule 
is defined and calculated by the following code fragment:
::

    m.def_process_on_off_output = pyomo.Constraint(
        m.tm, m.pro_on_off_output_tuples - m.pro_timevar_output_tuples -
              m.pro_partial_on_off_output_tuples,
        rule=def_process_on_off_output_rule,
        doc='e_pro_out = tau_pro * r_out * on_off')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_process_on_off_output_rule
   
In the case of a process where also a time variable output efficiency is given the
code for the output changes to:
::

    m.def_process_on_off_timevar_output = pyomo.Constraint(
        m.tm, m.pro_timevar_output_tuples & m.pro_on_off_output_tuples -
              m.pro_partial_on_off_output_tuples,
        rule=def_process_on_off_timevar_output_rule,
        doc='e_pro_out == tau_pro * r_out * on_off * eff_factor')
        
.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_process_on_off_timevar_output_rule
   
**Process On/Off Partial Input Rule**: This constraint modifies the process input 
commodity flow :math:`\epsilon_{yvcpt}^\text{in}` when compared to the 
original partial operation version without the on/off feature in by differentiating 
between two possible input functions, depending on the process on/off marker
:math:`\omicron_{yvpt}`. When the marker is on, the input function is the same as
in the case of simple partial operation. When the marker is off, the input function
becomes the product of the variable process throughput :math:`\tau_{yvpt}` and the 
parameter process partial input ratio :math:`\underline{r}_{ypc}^\text{in}`.
the output **commodity type** :math:`q`. When the **commodity type**. The mathematical
explanation of this rule is given in :ref:`theory-AP`.

In script ``AdvancedProcesses.py`` the constraint process on/off output rule 
is defined and calculated by the following code fragment:
::

    m.def_partial_process_on_off_input = pyomo.Constraint(
        m.tm, m.pro_partial_on_off_input_tuples,
        rule=def_partial_process_on_off_input_rule,
        doc='e_pro_in = '
            ' (cap_pro * min_fraction * (r - R) / (1 - min_fraction)'
            ' + tau_pro * (R - min_fraction * r) / (1 - min_fraction))')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_partial_process_on_off_input_rule
   
**Process On/Off Partial Output Rule**: This constraint modifies the process output 
commodity flow :math:`\epsilon_{yvcpt}^\text{out}` when compared to the 
original partial operation version without the on/off feature in two ways by differentiating 
between the output **commodity type** :math:`q`. When the **commodity type**
is not ``Env``, the output remains the same as for the partial operation without the on/off 
feature. Otherwise, the original output equation is changes depending on the variable process on/off 
marker :math:`\omicron_{yvpt}`. When the marker is off, the output function
becomes the product of the variable process throughput :math:`\tau_{yvpt}` and the 
parameter process partial output ratio :math:`\underline{r}_{ypc}^\text{out}`. When the marker is on,
the output function for ``Env`` type commodities remains the same as for the partial operation 
without the on/off feature. The mathematical explanation of this rule is given in :ref:`theory-AP`.
::

    m.def_partial_process_on_off_output = pyomo.Constraint(
        m.tm, m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=def_partial_process_on_off_output_rule,
        doc='e_pro_out = on_off *'
            ' (cap_pro * min_fraction * (r - R) / (1 - min_fraction) '
            '+ tau_pro * (R - min_fraction * r) / (1 - min_fraction)) ')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_partial_process_on_off_output_rule

In the case of a process where also a time variable output efficiency is given the
code for the output changes to:
::

    m.def_process_partial_on_off_timevar_output = pyomo.Constraint(
        m.tm, m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=def_pro_partial_on_off_timevar_output_rule,
        doc='e_pro_out == tau_pro * r_out * on_off * eff_factor')
        
.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: def_partial_process_on_off_output_rule
   
**Process Starting Ramp-up Rule**: This constraint replaces the process
throughput ramping rule when the parameter process starting time 
:math:`\overline{ST}_{yvp}^\text{start}` is defined in the input 
**process** sheet. This is done only until the variable process throughput 
:math:`\tau_{yvpt}` reaches the minimum load value and only while increasing
the process throughput :math:`\tau_{yvpt}`. The mathematical explanation of 
this rule is given in :ref:`theory-AP`.

In script ``AdvancedProcesses.py`` the constraint process starting ramp-up rule
is defined and calculated by the following code fragment:
::

    m.res_starting_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_start_tuples,
        rule=res_starting_rampup_rule,
        doc='throughput may not increase faster than maximal starting ramp up '
            'gradient until reaching minimum capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_starting_rampup_rule
   
**Process Output Ramping Rule**: These constraints act as a limiter for the
process output :math:`\epsilon_{yvcpt}^\text{out}` with the on/off feature 
because the process on/off marker :math:`\omicron_{yvpt}` can be both on and off
in the minimum load point. There are three possible cases, as follows, defined in
the script ``AdvanceProcesses.py``. The mathematical explanation of this rule is 
given in :ref:`theory-AP`

Case I: The parameter process minimum load fraction :math:`\underline{P}_{yvp}`
is greater than the parameter process maximum power ramp up gradient 
:math:`\overline{PG}_{yvp}^\text{up}` and is divisible with it. It is defined
and calculated by the following code fragment:
::

    m.res_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples -
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')
        
.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_output_minfraction_rampup_rule        
   
If the process has partial operation, the code changes to:
::

    m.res_partial_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_partial_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_partial_output_minfraction_rampup_rule
   
If the process has time variable efficiency, the code changes to:
::

    m.res_timevar_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples &
              m.pro_timevar_output_tuples - m.pro_partial_on_off_output_tuples,
        rule=res_timevar_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_timevar_output_minfraction_rampup_rule
   
If the process has both partial operation and time variable efficiency, the code changes to:
::

    m.res_partial_timevar_output_minfraction_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=res_partial_timevar_output_minfraction_rampup_rule,
        doc='Output may not increase faster than the minimal working capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_partial_timevar_output_minfraction_rampup_rule
   
Case II: The parameter process minimum load fraction :math:`\underline{P}_{yvp}`
is greater than the parameter process maximum power ramp up gradient 
:math:`\overline{PG}_{yvp}^\text{up}`, but is not divisible with it. It is defined
and calculated by the following code fragment:
::

    m.res_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples -
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_output_minfraction_rampup_rampup_rule
   
If the process has partial operation, the code changes to:
::

    m.res_partial_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_partial_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_partial_output_minfraction_rampup_rampup_rule
   
If the process has time variable efficiency, the code changes to:
::

    m.res_timevar_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples &
              m.pro_timevar_output_tuples - m.pro_partial_on_off_output_tuples,
        rule=res_timevar_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_timevar_output_minfraction_rampup_rampup_rule
   
If the process has both partial operation and time variable efficiency, the code changes to:
::

    m.res_partial_timevar_output_minfraction_rampup_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_not_divides_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=res_partial_timevar_output_minfraction_rampup_rampup_rule,
        doc='Output may not increase faster than the first multiple of the'
            'ramping up gradient greater than the minimal working capacity')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_partial_timevar_output_minfraction_rampup_rampup_rule
   
Case III: The parameter process minimum load fraction :math:`\underline{P}_{yvp}`
is smaller than the parameter process maximum power ramp up gradient 
:math:`\overline{PG}_{yvp}^\text{up}`. It is defined and calculated by the following 
code fragment:
::

    m.res_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples -
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_output_rampup_rule
   
If the process has partial operation, the code changes to:
::

    m.res_partial_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples - m.pro_timevar_output_tuples,
        rule=res_partial_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_partial_output_rampup_rule
   
If the process has time variable efficiency, the code changes to:
::

    m.res_timevar_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples &
              m.pro_timevar_output_tuples - m.pro_partial_on_off_output_tuples,
        rule=res_timevar_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_timevar_output_rampup_rule
   
If the process has both partial operation and time variable efficiency, the code changes to:
::

    m.res_partial_timevar_output_rampup = pyomo.Constraint(
        m.tm, m.pro_rampup_bigger_minfraction_output_tuples &
              m.pro_partial_on_off_output_tuples & m.pro_timevar_output_tuples,
        rule=res_partial_timevar_output_rampup_rule,
        doc='Output may not increase faster than the ramping up gradient')

.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_partial_timevar_output_rampup_rule
   
**Process Start-Up Rule**: The constraint process start-up rule marks in the
variable process start marker :math:`\sigma_{yvpt}` whether a process :math:`p`
started in timestep :math:`t` or not. The mathematical explanation of 
this rule is given in :ref:`theory-AP`.

In script ``AdvancedProcesses.py`` the constraint process start ups rule
is defined and calculated by the following code fragment:
::

    m.res_start_ups = pyomo.Constraint(
        m.tm, m.pro_start_up_tuples,
        rule=res_start_ups_rule,
        doc='start >= on_off(t) - on_off(t-1)')
        
.. literalinclude:: /../urbs/features/AdvancedProcesses.py
   :pyobject: res_start_ups_rule
