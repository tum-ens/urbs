
Storage Constraints
^^^^^^^^^^^^^^^^^^^

**Storage State Rule**: The constraint storage state rule is the main storage constraint and it defines the storage energy content of a storage :math:`s` in a site :math:`v` at a timestep :math:`t`. This constraint calculates the storage energy content at a timestep :math:`t` by adding or subtracting differences, such as ingoing and outgoing energy, to/from a storage energy content at a previous timestep :math:`t-1` multiplied by 1 minus the self-discharge rate :math:`d_{vs}` (which is scaled exponentially with the timestep size :math:`\delta t`). Here ingoing energy is given by the product of the variable storage input commodity flow :math:`\epsilon_{vst}^\text{in}` and the parameter storage efficiency during charge :math:`e_{vs}^\text{in}`. Outgoing energy is given by the variable storage output commodity flow :math:`\epsilon_{vst}^\text{out}` divided by the parameter storage efficiency during discharge :math:`e_{vs}^\text{out}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, \forall s\in S, t\in T_\text{m}\colon\ \epsilon_{vst}^\text{con} = \epsilon_{vs(t-1)}^\text{con} \cdot (1-d_{vs})^{\delta t} + \epsilon_{vst}^\text{in} \cdot e_{vs}^\text{in} - \epsilon_{vst}^\text{out} / e_{vs}^\text{out}

In script ``model.py`` the constraint storage state rule is defined and calculated by the following code fragment:

::

    m.def_storage_state = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=def_storage_state_rule,
        doc='storage[t] = (1 - selfdischarge) * storage[t-1] + input * eff_in - output / eff_out')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_storage_state_rule

**Storage Power Rule**: The constraint storage power rule defines the variable total storage power :math:`\kappa_{vs}^\text{p}`. The variable total storage power is defined by the constraint as the sum of the parameter storage power installed :math:`K_{vs}^\text{p}` and the variable new storage power :math:`\hat{\kappa}_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon\ \kappa_{vs}^\text{p} = K_{vs}^\text{p} + \hat{\kappa}_{vs}^\text{p}

In script ``model.py`` the constraint storage power rule is defined and calculated by the following code fragment:
::

    m.def_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_power_rule,
        doc='storage power = inst-cap + new power')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_storage_power_rule

**Storage Capacity Rule**: The constraint storage capacity rule defines the variable total storage size :math:`\kappa_{vs}^\text{c}`. The variable total storage size is defined by the constraint as the sum of the parameter storage content installed :math:`K_{vs}^\text{c}` and the variable new storage size :math:`\hat{\kappa}_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon\ \kappa_{vs}^\text{c} = K_{vs}^\text{c} + \hat{\kappa}_{vs}^\text{c}

In script ``model.py`` the constraint storage capacity rule is defined and calculated by the following code fragment:
::

    m.def_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_capacity_rule,
        doc='storage capacity = inst-cap + new capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_storage_capacity_rule

**Storage Input By Power Rule**: The constraint storage input by power rule limits the variable storage input commodity flow :math:`\epsilon_{vst}^\text{in}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more input power than the storage power capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{in}` must be less than or equal to the variable total storage power :math:`\kappa_{vs}^\text{p}`, scaled by the size of the time steps :math: `\Delta t`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S, t\in T_m\colon\ \epsilon_{vst}^\text{in} \leq \kappa_{vs}^\text{p} \Delta t

In script ``model.py`` the constraint storage input by power rule is defined and calculated by the following code fragment:
::

    m.res_storage_input_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_input_by_power_rule,
        doc='storage input <= storage power')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_storage_input_by_power_rule

**Storage Output By Power Rule**: The constraint storage output by power rule limits the variable storage output commodity flow :math:`\epsilon_{vst}^\text{out}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more output power than the storage power capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{out}` must be less than or equal to the variable total storage power :math:`\kappa_{vs}^\text{p}`, scaled by the size of the time steps :math: `\Delta t`. In mathematical notation this is expressed as:

.. math::

	 \forall v\in V, s\in S, t\in T\colon\ \epsilon_{vst}^\text{out} \leq \kappa_{vs}^\text{p} \Delta t

In script ``model.py`` the constraint storage output by power rule is defined and calculated by the following code fragment:
::

    m.res_storage_output_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_output_by_power_rule,
        doc='storage output <= storage power')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_storage_output_by_power_rule

**Storage State By Capacity Rule**: The constraint storage state by capacity rule limits the variable storage energy content :math:`\epsilon_{vst}^\text{con}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more storage content than the storage content capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{con}` must be less than or equal to the variable total storage size :math:`\kappa_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S, t\in T\colon\ \epsilon_{vst}^\text{con} \leq \kappa_{vs}^\text{c}

In script ``model.py`` the constraint storage state by capacity rule is defined and calculated by the following code fragment.
::

    m.res_storage_state_by_capacity = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_storage_state_by_capacity_rule,
        doc='storage content <= storage capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_storage_state_by_capacity_rule

**Storage Power Limit Rule**: The constraint storage power limit rule limits the variable total storage power :math:`\kappa_{vs}^\text{p}`. This contraint restricts a storage :math:`s` in a site :math:`v` from having more total power output capacity than an upper bound and having less than a lower bound. The constraint states that the variable total storage power :math:`\kappa_{vs}^\text{p}` must be greater than or equal to the parameter storage power lower bound :math:`\underline{K}_{vs}^\text{p}` and less than or equal to the parameter storage power upper bound :math:`\overline{K}_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon\ \underline{K}_{vs}^\text{p} \leq \kappa_{vs}^\text{p} \leq \overline{K}_{vs}^\text{p}

In script ``model.py`` the constraint storage power limit rule is defined and calculated by the following code fragment: 
::

    m.res_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_power_rule,
        doc='storage.cap-lo-p <= storage power <= storage.cap-up-p')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_storage_power_rule

**Storage Capacity Limit Rule**: The constraint storage capacity limit rule limits the variable total storage size :math:`\kappa_{vs}^\text{c}`. This contraint restricts a storage :math:`s` in a site :math:`v` from having more total storage content capacity than an upper bound and having less than a lower bound. The constraint states that the variable total storage size :math:`\kappa_{vs}^\text{c}` must be greater than or equal to the parameter storage content lower bound :math:`\underline{K}_{vs}^\text{c}` and less than or equal to the parameter storage content upper bound :math:`\overline{K}_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon\ \underline{K}_{vs}^\text{c} \leq \kappa_{vs}^\text{c} \leq \overline{K}_{vs}^\text{c}

In script ``model.py`` the constraint storage capacity limit rule is defined and calculated by the following code fragment:
::

    m.res_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_capacity_rule,
        doc='storage.cap-lo-c <= storage capacity <= storage.cap-up-c')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_storage_capacity_rule

**Initial And Final Storage State Rule**:
The constraint initial and final storage state rule defines and restricts the
variable storage energy content :math:`\epsilon_{vst}^\text{con}` of a storage
:math:`s` in a site :math:`v` at the initial timestep :math:`t_1` and at the
final timestep :math:`t_N`.There are two distinct cases:

1. The initial and final storage states are specified by a value of the
parameter :math:`I_{vs}` between 0 and 1.
2. :math:`I_{vs}` is not specified (e.g. by setting it '#NV' in the input
sheet). In this case the initial and final storage state are still equal but
variable.

In case 1 the constraints are written in the following way:

Initial Storage:  Initial storage represents the storage state in a
storage at the beginning of the simulation. The variable storage energy content
:math:`\epsilon_{vst}^\text{con}` at the initial timestep :math:`t_1` is
defined by this constraint. The constraint states that the variable
:math:`\epsilon_{vst_1}^\text{con}` must be equal to the product of the
parameters storage content installed :math:`K_{vs}^\text{c}` and  initial and
final state of charge :math:`I_{vs}`. In mathematical notation this is
expressed as: 

.. math::

	\forall v\in V, s\in S\colon\ \epsilon_{vst_1}^\text{con} = \kappa_{vs}^\text{c} I_{vs}

Final Storage: Final storage represents the storage state in a storage at the
end of the simulation. The variable storage energy content
:math:`\epsilon_{vst}^\text{con}` at the final timestep :math:`t_N` is
restricted by this constraint. The constraint states that the variable
:math:`\epsilon_{vst_N}^\text{con}` must be greater than or equal to the
product of the parameters storage content installed :math:`K_{vs}^\text{c}` and
initial and final state of charge :math:`I_{vs}`. In mathematical notation this
is expressed as:

.. math::

	\forall v\in V, s\in S\colon\ \epsilon_{vst_N}^\text{con} \geq \kappa_{vs}^\text{c} I_{vs}

In script ``model.py`` the constraint initial and final storage state rule is
defined and calculated by the following code fragment:
::

    m.res_initial_and_final_storage_state = pyomo.Constraint(
        m.t, m.sto_init_bound_tuples,
        rule=res_initial_and_final_storage_state_rule,
        doc='storage content initial == and final >= storage.init * capacity')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_initial_and_final_storage_state_rule

In case 2 the constraint becomes a lot easier, since the initial and final
state are simply compared by the following inequality:

.. math::

	\forall v\in V, s\in S\colon\ \epsilon_{vst_1}^\text{con} \leq \epsilon_{vst_N}^\text{con}

In script ``model.py`` the constraint initial and final storage state rule is
then defined and calculated by the following code fragment:
::

    m.res_initial_and_final_storage_state_var = pyomo.Constraint(
        m.t, m.sto_tuples - m.sto_init_bound_tuples,
        rule=res_initial_and_final_storage_state_var_rule,
        doc='storage content initial <= final, both variable')

.. literalinclude:: /../urbs/model.py
   :pyobject: res_initial_and_final_storage_state_var_rule
   
**Storage Energy to Power Ratio Rule**:
For certain type of storage techologies, the power and energy capacities can not be
independently sized but are dependent to each other. Hence, the constraint storage 
energy to power ratio rule sets a linear dependence between the capacities through a
user-defined "energy to power ratio" :math:`k_{vs}^\text{E/P}`. It has to be noted
that this constraint is only active for the storages with a positive value under the 
column "ep-ratio" in the input file, and when this value is not given, the power and
energy capacities can be sized independently. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon\ \kappa_{vs}^c = \kappa_{vs}^p k_{vs}^\text{E/P} 

In script ``model.py`` the constraint storage energy to power rule is
then defined and calculated by the following code fragment:
::

    m.def_storage_energy_power_ratio = pyomo.Constraint(
        m.sto_en_to_pow_tuples,
        rule=def_storage_energy_power_ratio_rule,
        doc='storage capacity = storage power * storage E2P ratio')

.. literalinclude:: /../urbs/model.py
   :pyobject: def_storage_energy_power_ratio_rule   

