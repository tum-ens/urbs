.. module urbs


Cost Constraints
^^^^^^^^^^^^^^^^^^

The variable total system cost :math:`\zeta` is calculated by the cost
function. In cases of CO2-minimization the total system cost is constrained by
the following expression:

.. math::
    \zeta = \zeta_\text{inv} + \zeta_\text{fix} + \zeta_\text{var} +
    \zeta_\text{fuel} + \zeta_\text{rev} + \zeta_\text{pur} +
    \zeta_\text{startup} \leq \overline{L}_{cost}

This constraint is given in ``model.py`` by
the following code fragment.  

.. literalinclude:: /../urbs/model.py
   :pyobject: res_global_cost_limit_rule

