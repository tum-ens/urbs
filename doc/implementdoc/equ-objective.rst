.. module urbs

.. _objective:


Objective function
^^^^^^^^^^^^^^^^^^

There are two possible choices of objective function for urbs problems, either
the costs (default option) or the total CO2-emissions can be minimized.

If the total CO2-emissions are minimized the objective function takes the form:

.. math::

	w \sum_{t\in T_\text{m}} \sum_{v \in V} \mathrm{-CB}(v,CO_{2},t)

In script ``model.py`` the global CO2 emissions are defined and calculated by
the following code fragment:

.. literalinclude:: /../urbs/model.py
   :pyobject: co2_rule

In the default case the total system costs are minimized. These variable total
system costs :math:`\zeta` are calculated by the cost function. The cost
function is the objective function of the optimization model. Minimizing the
value of the variable total system cost would give the most reasonable solution
for the modelled energy system. The formula of the cost function expressed in
mathematical notation is as following:

.. math::
    \zeta = (\zeta_\text{inv} + \zeta_\text{fix} + \zeta_\text{var} +
    \zeta_\text{fuel} + \zeta_\text{rev} + \zeta_\text{pur} +
    \zeta_\text{startup})

The calculation of the variable total system cost is given in ``model.py`` by
the following code fragment.  

.. literalinclude:: /../urbs/model.py
   :pyobject: cost_rule

The variable total system cost :math:`\zeta` is basically calculated by the
summation of every type of total costs. As previously mentioned in section
:ref:`sec-cost-types`, these cost types are : ``Investment``, ``Fix``,
``Variable``, ``Fuel``, ``Revenue``, ``Purchase``.

In script ``model.py`` the individual cost functions are calculated by
the following code fragment:

.. literalinclude:: /../urbs/model.py
   :pyobject: def_costs_rule