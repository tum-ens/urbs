Transmission Constraints
^^^^^^^^^^^^^^^^^^^^^^^^

**Transmission Capacity Rule**: The constraint transmission capacity rule
defines the variable total transmission capacity :math:`\kappa_{yaf}`. The
variable total transmission capacity is defined by the constraint as the sum of
the variable transmission capacity installed :math:`K_{yaf}` and the variable
new transmission capacity :math:`\hat{\kappa}_{yaf}`. The mathematical
explanation of this rule is given in :ref:`theory-multinode`.

In script ``transmission.py`` the constraint transmission capacity rule is
defined and calculated by the following code fragment:
::

    m.def_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity = inst-cap + new capacity')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: def_transmission_capacity_rule
   
**Transmission New Capacity Rule**: The constraint transmission new capacity
rule defines the variable new trasmission capacity :math:`\hat{\kappa}_{yaf}`.
This variable is defined by the constraint as the product of the parameter
transmission new capacity block :math:`{K}_{yaf}^\text{block}` and the variable
new transmission capacity units :math:`\beta_{yaf}`. The mathematical explanation
of this rule is given in :ref:`theory-multinode`.

In script ``transmission.py`` the constraint transmission output rule is
defined and calculated by the following code fragment:
::

   m.def_cap_tra_new = pyomo.Constraint(
        m.tra_block_tuples,
        rule=def_cap_tra_new_rule,
        doc='cap_tra_new = tra-block * cap_tra_new')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: def_cap_tra_new_rule
   
**Transmission Output Rule**: The constraint transmission output rule defines
the variable transmission output commodity flow :math:`\pi_{yaft}^\text{out}`.
The variable transmission output commodity flow is defined by the constraint as
the product of the variable transmission input commodity flow
:math:`\pi_{yaft}^\text{in}` and the parameter transmission efficiency
:math:`e_{yaf}`. The mathematical explanation of this rule is given in
:ref:`theory-multinode`.

In script ``transmission.py`` the constraint transmission output rule is
defined and calculated by the following code fragment:
::

    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: def_transmission_output_rule

**Transmission Input By Capacity Rule**: The constraint transmission input by
capacity rule limits the variable transmission input commodity flow
:math:`\pi_{yaft}^\text{in}`. This constraint prevents the transmission power
from exceeding the possible power input capacity of the line. The constraint
states that the variable transmission input commodity flow
:math:`\pi_{yaft}^\text{in}` must be less than or equal to the variable total
transmission capacity :math:`\kappa_{yaf}`, scaled by the size of the time
steps :math: `\Delta t`. The mathematical explanation of this rule is given in
:ref:`theory-multinode`.

In script ``transmission.py`` the constraint transmission input by capacity
rule is defined and calculated by the following code fragment:
::

    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: res_transmission_input_by_capacity_rule

**Transmission Capacity Limit Rule**: The constraint transmission capacity
limit rule limits the variable total transmission capacity
:math:`\kappa_{yaf}`. This constraint restricts a transmission :math:`f`
through an arc :math:`a` in support timeframe :math:`y` from having more total
power output capacity than an upper bound and having less than a lower bound.
The constraint states that the variable total transmission capacity
:math:`\kappa_{yaf}` must be greater than or equal to the parameter
transmission capacity lower bound :math:`\underline{K}_{yaf}` and less than or
equal to the parameter transmission capacity upper bound
:math:`\overline{K}_{yaf}`. The mathematical explanation of this rule is given
in :ref:`theory-multinode`.

In script ``transmission.py`` the constraint transmission capacity limit rule
is defined and calculated by the following code fragment:
::

    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: res_transmission_capacity_rule

**Transmission Symmetry Rule**: The constraint transmission symmetry rule
defines the power capacities of incoming and outgoing arcs :math:`a , a'` of a
transmission :math:`f` in support timeframe :math:`y`. The constraint states
that the power capacities :math:`\kappa_{af}` of the incoming arc :math:`a` and
the complementary outgoing arc :math:`a'` between two sites must be equal. The
mathematical explanation of this rule is given in :ref:`theory-multinode`.

In script ``transmission.py`` the constraint transmission symmetry rule is
defined and calculated by the following code fragment:
::

    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: res_transmission_symmetry_rule

DCPF Transmission Constraints
=============================

The following constraints are included in the model if the optional DC
Power Flow feature is activated.

**DC Power Flow Rule**: The constraint DC Power Flow rule defines the power flow
of transmission lines, which are modelled with DCPF. This constraint states that
the power flow on a transmission line is equal to the product of voltage angle
differences of two connecting sites :math:`v_\text{out}` and :math:`{v_\text{in}}`
and the admittance of the transmission line. This constraint is only applied
to the transmission lines modelled with DCPF. The mathematical explanation of
this rule is given in :ref:`theory-multinode`. In script ``transmission.py``
the constraint DC Power Flow Rule is defined and calculated by the following
code fragment:
::

    m.def_dc_power_flow = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=def_dc_power_flow_rule,
        doc='transmission output = (angle(in)-angle(out))/ 57.2958 '
            '* -1 *(-1/reactance) * (base voltage)^2')

.. literalinclude:: /../urbs/features/transmission.py
    :pyobject: def_dc_power_flow_rule


**DCPF Transmission Input By Capacity Rule**: The constraint DCPF transmission
input by capacity rule expands the constraint transmission input by capacity
rule for transmission lines modelled with DCPF. This constraint limits the
variable transmission input commodity flow :math:`\pi_{yaft}^\text{in}` of
DCPF transmission lines also with a lower bound. This constraint prevents the
absolute value of the transmission power from exceeding the possible power input
capacity of the line especially when the transmission power can be negative.
The constraint states that the additive inverse of variable transmission input
commodity flow :math:`-\pi_{yaft}^\text{in}` must be less than or equal to the
variable total transmission capacity :math:`\kappa_{yaf}`, scaled by the size of
the time steps :math: `\Delta t`. This constraint is only applied to the
tranmission lines modelled with DCPF. The mathematical explanation of this rule
is given in
:ref:`theory-multinode`.

In script ``transmission.py`` the constraint transmission input by capacity
rule is defined and calculated by the following code fragment:
::

    m.res_transmission_dc_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=res_transmission_dc_input_by_capacity_rule,
        doc='-dcpf transmission input <= total transmission capacity')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: res_transmission_dc_input_by_capacity_rule

**Voltage Angle Limit Rule**: The constraint voltage angle limit rule limits the
maximum and minimum difference of voltage angles :math:`\theta_{yvt}` of two sites
:math:`v_\text{out}` and :math:`{v_\text{in}}` connected with a DCPF
transmission line with the parameter voltage angle difference limit
:math:`\overline{dl}_{yaf}`. This constraint is only applied
to the transmission lines modelled with DCPF. The mathematical explanation of
this rule is given in :ref:`theory-multinode`. In script ``transmission.py``
the constraint voltage angle limit rule is defined and given by the following
code fragment:
::

    m.def_angle_limit = pyomo.Constraint(
            m.tm, m.tra_tuples_dc,
            rule=def_angle_limit_rule,
            doc='-angle limit < angle(in) - angle(out) < angle limit')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: def_angle_limit_rule

**Absolute Transmission Flow Constraints**: The two absolute transmission flow
constraints are included in the model to create the variable
absolute value of transmission commodity flow
:math:`{\pi_{yaft}^{\text{in}}}^\prime`. By limiting the negative
:math:`-{\pi_{yaft}^{\text{in}}}^\prime`
and positive :math:`{\pi_{yaft}^{\text{in}}}^\prime` of substitute variable
''e_tra_abs'' with the variable :math:`\pi_{yaft}^\text{in}` and minimizing the
substitute value :math:`{\pi_{yaft}^{\text{in}}}^\prime` the absolute value of
transmission commodity flow is retrieved. These constraints are only applied to
the transmission lines modelled with DCPF. The mathematical explanation of
these rules are given in :ref:`theory-multinode`. In script ``transmission.py``
the constraint Absolute Transmission Flow Constraints are defined and
given by the following
code fragment:
::

    m.e_tra_abs1 = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=e_tra_abs_rule1,
        doc='transmission dc input <= absolute transmission dc input')
    m.e_tra_abs2 = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=e_tra_abs_rule2,
        doc='-transmission dc input <= absolute transmission dc input')

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: e_tra_abs_rule1

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: e_tra_abs_rule2

**Transmission Symmetry Rule**: The above mentioned constraint transmission symmetry rule
is only applied to the transmission lines modelled with transport model if the
DCPF is activated. Since the DCPF transmission lines do not include the complementary
arcs, this constraint is ignored for these transmission lines. For this reason,
the constraint is indexed with the transmission tuple set ``m.tra_tuples_tp`` if
the DCPF is activated.

In script ``transmission.py`` the constraint transmission symmetry rule is
defined as following if the DCPF is activated:
::

    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples_tp,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')
