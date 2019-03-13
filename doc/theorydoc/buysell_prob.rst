.. module:: urbs

.. _theory-buysell:

Trading with an external market
===============================
In urbs it is possible to model the trade with an external market. For this two
new commodity types, buy and sell commodities, are introduced. For each a time
series representing the momentary cost at each timestep is given. This time
series is of course known to the model in advance, which has two implications.
First, the modeled system is considered too small to influence the external
market and any possible influence is not captured by th model, and, second, the
perfect price foresight can distort the results when compared to a realistic
trader in a market. For models with buy and sell commodities the variable
vector takes the following form: 

.. math::

   x^{\text{T}}=(\zeta, \underbrace{\rho_{yvct}, \varrho_{yvct}, \psi_{yvct}}
   _{\text{commodity variables}},
   \underbrace{\kappa_{yvp}, \widehat{\kappa}_{yvp}, \tau_{yvpt},
   \epsilon^{\text{in}}_{yvcpt},
   \epsilon^{\text{out}}_{yvcpt}}_{\text{process variables}},
   \underbrace{\kappa_{yaf}, \widehat{\kappa}_{yaf}, \pi^{\text{in}}_{yaft},
   \pi^{\text{out}}_{yaft}}_{\text{transmission variables}}),

where :math:`\varrho_{yvct}` is the amount of sell commodity :math:`c` sold to
the external market in year :math:`y` from vertex :math:`v` at time :math:`t`
and :math:`\psi_{yvct}` is the amount of buy commodity :math:`c` bought from
the external market in year :math:`y` at vertex :math:`v` and time :math:`t`.

Costs
-----
The cost function is amended by two new cost types when the trading with an
external market is modeled, the purchase and the revenue costs

.. math::
   \zeta = \zeta_{\text{inv}} + \zeta_{\text{fix}} + \zeta_{\text{var}} +
   \zeta_{\text{fuel}} + \zeta_{\text{rev}} + \zeta_{\text{pur}} +
   \zeta_{\text{env}}.

The two new cost types are then specified by the following equations:

.. math::
   \zeta_{\text{rev}}=&-w\Delta t
   \sum_{y\in Y\\v\in V\\c\in C_{sell}\\ t\in T_m}D_{m}\cdot
   k^{\text{bs}}_{yvct}\cdot \varrho_{yvct}\\\\
   \zeta_{\text{pur}}=&w\Delta t\sum_{y\in Y\\v\in V\\c\in C_{buy}\\ t\in T_m}
   D_{m}\cdot k^{\text{bs}}_{yvct}\cdot \psi_{yvct},

where :math:`k^{\text{bs}}_{yvct}` represents the time series of the given
buy and sell commodity prices.

Commodity dispatch constraints
------------------------------
Buy and sell commodities change the vertex rule (Kirchhoff's current law), by
adding a new way for in- an output flows of commodities. The rule is thus
amended by the following two equations:

.. math::
   &\forall y\in Y,~v\in V,~c \in C_{\text{sell}},~t \in T_m:\\
   &-\varrho_{ct} \geq \text{CB}(c,t)\\\\
   &\forall y\in Y,~v\in V,~c \in C_{\text{buy}},~t \in T_m:\\
   &\psi_{ct} \geq \text{CB}(c,t).

The commodity balance itself is not changed. The new rules state that any
amount of energy sold needs to be provided to (negative CB) the system via
processes, storages or transmission lines, while buy commodity consumed by
processes, storages or transmission lines in the system has to be replenished. 

Buy/sell commodity limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The trade with the market in each modeled year and each vertex can be limited
per time step and for an entire year. This introduces the following constraints:

.. math::
   &\forall y\in Y,~v\in V,~c \in C_{\text{sell}}:\\
   &w\sum_{t\in T_{m}}\varrho_{ct}\leq \overline{G}_{yvc}\\\\
   &\forall y\in Y,~v\in V,~c \in C_{\text{sell}},~t\in T_m:\\
   & \varrho_{yvct}\leq \overline{g}_{yvc}

and

.. math::
   &\forall y\in Y,~v\in V,~c \in C_{\text{buy}}:\\
   &w \sum_{t\in T_{m}}\psi_{ct}\leq \overline{B}_{yvc}\\\\
   &\forall y\in Y,~v\in V,~c \in C_{\text{buy}},~t\in T_m:\\
   & \varrho_{yvct}\leq \overline{b}_{yvc}.

Here, the parameters :math:`\overline{b}_{yvc}` and :math:`\overline{B}_{yvc}`
limit the hourly and yearly maximums of buy from and :math:`\overline{g}_{yvc}`
and :math:`\overline{G}_{yvc}` the hourly and yearly maximum of selling to the
external market.

This concludes the discussion of the modeled trading with an external market.