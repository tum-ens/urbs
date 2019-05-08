.. module:: urbs

.. _theory-storage:

Energy Storage
==============
Storages can optionally be set in urbs. They introduce additional variables and
constraints, contribute to the cost function but do not increase the index
depth of all variables and parameters. For this and all the further features
all variables will be written in the full index depth, i.e. for intertemporal
models with multiple vertices. For storages the capacity and the
charging/discharging power are expanded independently. For each storage one
commodity is specified which is stored. It is thus not necessary to specify the
commodity as an extra index in the variables and parameters. With added
storages the variable vector then reads:

.. math::

   x^{\text{T}}=(&\zeta, \underbrace{\rho_{yvct}}_{\text{commodity variables}},
   \underbrace{\kappa_{yvp}, \widehat{\kappa}_{yvp}, \tau_{yvpt},
   \epsilon^{\text{in}}_{yvcpt},
   \epsilon^{\text{out}}_{yvcpt}}_{\text{process variables}},
   \underbrace{\kappa_{yaf}, \widehat{\kappa}_{yaf}, \pi^{\text{in}}_{yaft},
   \pi^{\text{out}}_{yaft}}_{\text{transmission variables}},\\\\
   &\underbrace{\kappa^{\text{c}}_{yvs}, \kappa^{\text{p}}_{yvs},
   \widehat{\kappa}^{\text{c}}_{yvs}, \widehat{\kappa}^{\text{p}}_{yvs},
   \epsilon^{\text{in}}_{yvst}, \epsilon^{\text{out}}_{yvst},
   \epsilon^{\text{con}}_{yvst}}_{\text{storage variables}}).

Here, the new storage variables :math:`\kappa^{\text{c,p}}_{yvs}` and
:math:`\widehat{\kappa}^{\text{c,p}}_{yvs}` stand for the total and new
capacities of storage capacity and power of storage unit :math:`s`, in modeled
year :math:`y` at vertex :math:`v`, respectively, the variables
:math:`\epsilon^{\text{in,out}}_{yvst}` represent the input and output to
storage :math:`s` in year :math:`y` at vertex :math:`v` at time :math:`t` and
:math:`\epsilon^{\text{con}}_{yvst}` the storage state.

Costs
-----
The costs are changed in a straightforward way. The invest, fix and variable
costs are now summed over the storage capacities, powers and the total amount
of charged and discharged commodity in addition to the process indices. As in
the case of transmissions there are no qualitative changes to the costs.

Storage expansion constraints
-----------------------------
Storages are expanded in their capacity and charging and discharging power
separately. The respective constraints read:

.. math::
   \kappa^{\text{c,p}}_{yvs}&=\sum_{y^{\prime}\in Y\\(s,v,y^{\prime},y)\in O}
   \widehat{\kappa}^{\text{c,p}}_{y^{\prime}vs} + K_{vs}
   ~,~~\text{if}~(s,v,y)\in O_{\text{inst}}\\\\
   \kappa^{\text{c,p}}_{yvs}&=\sum_{y^{\prime}\in Y\\(s,v,y^{\prime},y)\in O}
   \widehat{\kappa}^{\text{c,p}}_{y^{\prime}vs}~,~~\text{else},

where :math:`\kappa^{\text{c,p}}_{yvs}` are the total installed
capacity and power, repectively, in year :math:`y` at site :math:`v` of storage
:math:`s` and :math:`\widehat{\kappa}^{\text{c,p}}_{yvs}` the corresponding
newly installed storage capacities and powers. Both quantities are then also
given an upper and a lower bond via:

.. math::
   &\forall y\in Y,~v\in V,~s\in S:\\
   &\underline{K}^{\text{c}}_{yvs}\leq \kappa^{\text{c}}_{yvs}\leq
   \overline{K}^{\text{c}}_{yvs}\\
   &\underline{K}^{\text{p}}_{yvs}\leq \kappa^{\text{p}}_{yvs}\leq
   \overline{K}^{\text{p}}_{yvs}

Commodity dispatch constraints
------------------------------
The commodity unit utilization constraints are expanded by the use of
storages.

Amendments to the Vertex rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The vertex rule is changed, since additional commodity flows into and out of
the storages can occur. The commodity balance function is thus changed to:

.. math::
   &\forall y\in Y,~v\in V,~c \in C,~t\in T_m:\\\\
   \text{CB}(y,v,c,t)=&
   \sum_{(y,v,c,p)\in C^{\text{in}}_{y,v,c,p}}\epsilon^{\text{in}}_{vcpt}+
   \sum_{(y,v,s,c)\in C_{y,v,s,c}}\epsilon^{\text{in}}_{yvst}+
   \sum_{(y,a,f)\in A^{\text{in}}_{v}}\pi^{\text{in}}_{aft}-\\\\
   &-\sum_{(y,v,c,p)\in C^{\text{out}}_p}\epsilon^{\text{out}}_{vcpt}-
   \sum_{(y,v,s,c)\in C_{y,v,s,c}}\epsilon^{\text{out}}_{yvst}-
   \sum_{(y,a,f)\in A^{\text{out}}_{v}}\pi^{\text{out}}_{aft}.

Here, the new tuple sets :math:`C^{\text{in,out}}_{y,v,s,c}` represent all
inputs and outputs in year :math:`y` at vertex :math:`v` of commodity :math:`c`
into storage :math:`s`. The variables :math:`\epsilon^{\text{in,out}}_{yvst}`
are then the inputs and outputs of commodities to and from storages.

Storage dispatch constraints
----------------------------
In a storage the energy content :math:`\epsilon^{\text{con}}_{yvst}` has to be
calculated. This is achieved by simply adding all inputs to and subtracting all
outputs from the storage content at the previous time step
:math:`\epsilon^{\text{con}}_{yvs(t-1)}`:

.. math::
   &\forall y\in Y,~v\in V,~s\in S,~t\in T_m:\\
   &\epsilon^{\text{con}}_{yvst}=\epsilon^{\text{con}}_{yvs(t-1)}\cdot
   (1-d_{yvs})^{\Delta t}+e^{\text{in}}_{yvs}\cdot \epsilon^{\text{in}}_{yvst}-
   \frac{\epsilon^{\text{out}}_{yvst}}{e^{\text{out}}_{yvs}}.

Here, :math:`e^{\text{in,out}}_{yvs}` are the efficiencies for charging and
discharging, respectively, and :math:`d_{yvs}` is the hourly self discharge
rate.

Basic storage dispatch rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Similar to processes and transmission lines, inputs and outputs are limited by
the power capacity of the storage:

.. math::
   &\forall y\in Y,~v\in V,~s\in S,~t\in T_m:\\
   &\epsilon^{\text{in,out}}_{yvst}\leq\Delta t \cdot \kappa^{\text{p}}_{yvs}.

Additionally, the storage content is limited by the total storage energy
capacity:

.. math::
   &\forall y\in Y,~v\in V,~s\in S,~t\in T_m:\\
   &\epsilon^{\text{con}}_{yvst}\leq\kappa^{\text{c}}_{yvs}.

Initial and final state
~~~~~~~~~~~~~~~~~~~~~~~
In order to avoid windfall profits for the optimization by, e.g., emptying a
storage over the model horizon, the initial and final storage content are
linked via:

.. math::

	&\forall y\in Y,~v\in V,~s\in S:\\
    &\epsilon_{yvs(t_1)}^\text{con} \leq \epsilon_{yvst_N}^\text{con},

where :math:`t_{1,N}` are the initial and final modeled timesteps,
respectively. The inequality simplifies the model solving by relaying an
otherwise unnecessarily strict constraint. A small disadvantage arises when the
system can gain costs or save CO2 by filling a storage. This case is, however,
not too common. It is additionally possible for the user to fix the initial
storage content via:

.. math::

	&\forall y\in Y,~v\in V,~s\in S:\\
    &\epsilon_{vst_1}^\text{con} = \kappa_{yvs}^\text{c} I_{yvs},

where :math:`I_{yvs}` is the fraction of the total storage capacity that is
filled at the beginning of the modeling period.

Fixed energy/power ratio
~~~~~~~~~~~~~~~~~~~~~~~~
It is sometimes desirable to fix the ratio between energy capacity and
charging/discharging power for a given storage. This is modeled by the
possibility to set a linear dependence between the capacities through a
user-defined "energy to power ratio" :math:`k_{yvs}^\text{E/P}`. Note that this
constraint is only active for the storages with a positive value under the
column "ep-ratio" in the input file, and when this value is not given, the
power and energy capacities can be sized independently

.. math::

	&\forall y\in Y,~v\in V,~s\in S:\\
    &\kappa_{yvs}^c = \kappa_{yvs}^p k_{yvs}^\text{E/P}.

This concludes the storage feature.