Transmission Constraints
^^^^^^^^^^^^^^^^^^^^^^^^

**Transmission Capacity Rule**: The constraint transmission capacity rule defines the variable total transmission capacity :math:`\kappa_{af}`. The variable total transmission capacity is defined by the constraint as the sum of the variable transmission capacity installed :math:`K_{af}` and the variable new transmission capacity :math:`\hat{\kappa}_{af}`. In mathematical notation this is expressed as:

.. math::
    \forall a\in A, f\in F\colon\ \kappa_{af} = K_{af} + \hat{\kappa}_{af}

In script ``model.py`` the constraint transmission capacity rule is defined and calculated by the following code fragment:
::

    m.def_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity = inst-cap + new capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_transmission_capacity_rule

**Transmission Output Rule**: The constraint transmission output rule defines the variable transmission output commodity flow :math:`\pi_{aft}^\text{out}`. The variable transmission output commodity flow is defined by the constraint as the product of the variable transmission input commodity flow :math:`\pi_{aft}^\text{in}` and the parameter transmission efficiency :math:`e_{af}`. In mathematical notation this is expressed as:

.. math::
    \forall a\in A, f\in F, t\in T_m\colon\ \pi^\text{out}_{aft} = \pi^\text{in}_{aft} e_{af}

In script ``model.py`` the constraint transmission output rule is defined and calculated by the following code fragment:
::

    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_transmission_output_rule

**Transmission Input By Capacity Rule**: The constraint transmission input by capacity rule limits the variable transmission input commodity flow :math:`\pi_{aft}^\text{in}`. This constraint prevents the transmission power from exceeding the possible power input capacity of the line. The constraint states that the variable transmission input commodity flow :math:`\pi_{aft}^\text{in}` must be less than or equal to the variable total transmission capacity :math:`\kappa_{af}`, scaled by the size of the time steps :math: `\Delta t`. In mathematical notation this is expressed as:

.. math::
    \forall a\in A, f\in F, t\in T_m\colon\ \pi^\text{in}_{aft} \leq \kappa_{af} \Delta t

In script ``model.py`` the constraint transmission input by capacity rule is defined and calculated by the following code fragment:
::

    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_transmission_input_by_capacity_rule

**Transmission Capacity Limit Rule**: The constraint transmission capacity limit rule limits the variable total transmission capacity :math:`\kappa_{af}`. This constraint restricts a transmission :math:`f` through an arc :math:`a` from having more total power output capacity than an upper bound and having less than a lower bound. The constraint states that the variable total transmission capacity :math:`\kappa_{af}` must be greater than or equal to the parameter transmission capacity lower bound :math:`\underline{K}_{af}` and less than or equal to the parameter transmission capacity upper bound :math:`\overline{K}_{af}`. In mathematical notation this is expressed as:

.. math::
    \forall a\in A, f\in F\colon\ \underline{K}_{af} \leq \kappa_{af} \leq \overline{K}_{af}

In script ``model.py`` the constraint transmission capacity limit rule is defined and calculated by the following code fragment:
::

    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_transmission_capacity_rule

**Transmission Symmetry Rule**: The constraint transmission symmetry rule defines the power capacities of incoming and outgoing arcs :math:`a , a'` of a transmission :math:`f`. The constraint states that the power capacities :math:`\kappa_{af}` of the incoming arc :math:`a` and the complementary outgoing arc :math:`a'` between two sites must be equal. In mathematical notation this is expressed as:

.. math::
    \forall a\in A, f\in F\colon\ \kappa_{af} = \kappa_{a'f}

In script ``model.py`` the constraint transmission symmetry rule is defined and calculated by the following code fragment:
::

    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_transmission_symmetry_rule
