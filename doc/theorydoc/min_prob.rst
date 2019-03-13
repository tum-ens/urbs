.. module:: urbs

.. _theory-min:

Minimal optimization model
==========================
The minimal model in urbs is a simple expansion and dispatch model with only
processes being able to fulfill the given demands. All spatial information is
neglected in this case. The minimal model is already multiple-input/multiple
output (mimo) and the variable vector takes the following form:

.. math::

   x^{\text{T}}=(\zeta, \underbrace{\rho_{ct}}_{\text{commodity variables}},
   \underbrace{\kappa_{p}, \widehat{\kappa}_{p}, \tau_{pt},
   \epsilon^{\text{in}}_{cpt},
   \epsilon^{\text{out}}_{cpt}}_{\text{process variables}}).

Here, :math:`\zeta` represents the total annualized system cost, :math:`\rho_ct`
the amount of commodities :math:`c` taken from a virtual, infinite stock at
time :math:`t`, :math:`\kappa_{p}` and :math:`\widehat{\kappa}_{p}` the total
and the newly installed process capacities of processes :math:`p`,
:math:`\tau_{pt}` the operational state of processes :math:`p` at time
:math:`t` and :math:`\epsilon^{\text{in}}_{cpt}` and
:math:`\epsilon^{\text{out}}_{cpt}` the total inputs and outputs of commodities
:math:`c` to and from process :math:`p` at time :math:`t`, respectively.

Objective
---------
For any urbs problem as the objective function either the total system costs or
the total emissions of CO2 can be chosen. In the former (standard) case this
leads to an objective vector of:

.. math::

   c=(1,0,0,0,0,0,0),

where only the costs are part of the objective function. For the latter choice
of objective no such simple structure can be written.

Costs
-----
In the minimal model the total cost variable can be split into the following
sum:

.. math::

   \zeta = \zeta_{\text{inv}} + \zeta_{\text{fix}} + \zeta_{\text{var}} +
   \zeta_{\text{fuel}} + \zeta_{\text{env}},

where :math:`\zeta_{\text{inv}}` are the annualized invest costs,
:math:`\zeta_{\text{fix}}` the annual fixed costs, :math:`\zeta_{\text{var}}`
the total variable costs accumulating over one year,
:math:`\zeta_{\text{fuel}}` the accumulated fuel costs over one year and
:math:`\zeta_{\text{env}}` the annual penalties for environmental pollution.
These costs are then calculated in the following way:

Annualized invest costs
~~~~~~~~~~~~~~~~~~~~~~~
Investments are typically depreciated over a longer period of time than the
standard modeling horizon of one year. To overcome distortions in the overall
cost function urbs uses the annual cash flow (CAPEX) for the calculation of the
investment costs in the cost function. This is captured by multiplying the
total invest costs for a given process :math:`C_p` with the so-called annuity
factor :math:`f_p`, i.e.:

.. math::

   \zeta_{\text{inv},p}=f_p \cdot C_p

For an interest rate of :math:`i` and a depreciation period of :math:`n` years
the annuity factor can be derived using the remaining debt after :math:`k`
payments :math:`C_k`:

.. math::

   &\text{After 0 Payments:}~C_0=C(1+i)\\
   &\text{After 1 Payment:}~~C_1=(C_0-fC)(1+i)=C(1+i)^2-fC(1+i)\\
   &\text{After 2 Payments:}~C_2=(C_1-fC)(1+i)=C(1+i)^3-fC(1+i)^2-fC(1+i)\\
   &...\\
   &\text{After n Payments:}~C_n=C(1+i)^n+C\sum_{k=0}^{n-1}(1+i)^k=(1+i)^n +
   f\left(\frac{1-(1+i)^n}{i}\right).

Since the outstanding debt becomes :math:`0` at the end of the depreciation
period this leads to:

.. math::

   f=\frac{(1+i)^n\cdot i}{(1+i)^n-1}

The annualized invest costs for all investments made by the optimizer are then
given by:

.. math::
   \zeta_{\text{inv}}=\sum_{p \in P_{\text{exp}}}f_p k^{\text{inv}}_p
   \widehat{\kappa}_p,

where :math:`k^{\text{inv}}_p` signifies the specific invest costs of process
:math:`p` per unit capacity and :math:`P_{\text{exp}}` is the subset of all
processes that are actually expanded. 

Annual fixed costs
~~~~~~~~~~~~~~~~~~
The annual fixed costs represent maintenance and staff payments the processes
used. They are playing a role for unit expansion only and are given as
parameters for all allowed processes. Fixed costs scale with the capacity
(in W) of the processes, and can be calculated using:

.. math::
   \zeta_{\text{fix}}=\sum_{p \in P}k^{\text{fix}}_p\kappa_p,

where :math:`k^{\text{fix}}_p` represents the specific annual fix costs for
process :math:`p`.

Annual variable costs
~~~~~~~~~~~~~~~~~~~~~
Variable costs represent both, additional maintenance requirements due to usage
of processes and taxes or tariffs. They scale with the utilization of
processes (in Wh) and can be calculated in the following way:

.. math::
   \zeta_{\text{var}}=w \Delta t \sum_{t \in T_m\\ p \in P}
   k^{\text{var}}_{pt}\tau_{pt},

where :math:`k^{\text{var}}_{pt}` are the specific variable costs per time
integrated process usage, and :math:`w` and :math:`\Delta t` are a weight
factor that extrapolates the actual modeled time horizon to one year and the
timestep length in hours, respectively.

Annual fuel costs
~~~~~~~~~~~~~~~~~
The usage of fuel adds an additional cost factor to the total costs. As with
variable costs these costs occur when processes are used and are dependent on
the total usage of the fuel (stock) commodities:

.. math::
   \zeta_{\text{fuel}}=w \Delta t \sum_{t \in T_m\\ c \in C_{\text{stock}}}
   k^{\text{fuel}}_{c}\rho_{c},
   
where :math:`k^{\text{fuel}}_{c}` are the specific fuel costs. The distinction
between variable and fuel costs is introduced for clarity of the results, both
could in principle be merged into one class of costs.

Annual environmental costs
~~~~~~~~~~~~~~~~~~~~~~~~~~
Environmental costs occur when the emission of an environmental commodity is
penalized by a fine. Environmental commodities do not have to be balanced but
can be emitted to the surrounding. The total production of the polluting
environmental commodity is then given by:

.. math::
   \zeta_{\text{env}}=-w \Delta t \sum_{t \in T_m\\ c \in C_{\text{env}}}
   k^{\text{env}}_{c}\text{CB}(c,t),

where :math:`k^{\text{env}}_{c}` are the specific costs per unit of
environmental commodity and :math:`CB` is the momentary commodity balnce of
commodity :math:`c` at time :math:`t`. The minus sign is due to the sign
convention used for the commodity balance which is positive when the system
takes in a unit of a commodity.

After this discussion of the individual cost terms the constraints making up
the matrices :math:`A` and :math:`B` are discussed now.

Process expansion constraints
-----------------------------
The unit expansion constraints are independent of the modeled time. In case of
the minimal model the are restricted to two constraints only limiting the
allowed capacity expansion for each process. The total capacity of a given
process is simply given by:

.. math::
   &\forall p \in P:\\
   &\kappa_{p}=K_p + \widehat{\kappa}_p,

where :math:`K_p` is the already installed capacity of process :math:`p`.

Process capacity limit rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The capacity pf each process :math:`p` is limited by a maximal and minimal
capacity, :math:`\overline{K}_p` and :math:`\underline{K}_p`, respectively,
which are both given to the model as parameters:

.. math::
   &\forall p \in P:\\
   &\underline{K}_p\leq\kappa_{p}\leq\overline{K}_p.

All further constraints are time dependent and are determinants of the unit
commitment, i.e. the time series of operation of all processes and commodity
flows.

Commodity dispatch constraints
------------------------------
In this part the rules governing the commodity flow timeseries are shown.  

Vertex rule ("Kirchhoffs current law")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This rule is the central rule for the commodity flows and states that all
commodity flows, (except for those of environmental commodities) have to be
balanced in each time step. As a helper function the already mentioned
commodity balance is calculated in the following way:

.. math::
   &\forall c \in C,~t\in T_m:\\\\
   &\text{CB}(c,t)=
    \sum_{(c,p)\in C^{\mathrm{out}}_p}\epsilon^{\text{in}}_{cpt}-
    \sum_{(c,p)\in C^{\mathrm{in}}_p}\epsilon^{\text{out}}_{cpt}.

Here, the tuple sets :math:`C^{\mathrm{in,out}}_p` represent all input and
output commodities of process :math:`p`, respectively. The commodity balance
thus simply calculates how much more of commodity :math:`c` is emitted by than
added to the system via process :math:`p` in timestep :math:`t`. Using
this term the vertex rule for the various commodity types can now be written in
the following way:

.. math::
   \forall c \in C_{\text{st}},~t \in T_m:
   \rho_{ct} \geq \text{CB}(c,t),

where :math:`C_{\text{st}}` is the set of stock commodities and:

.. math::
   \forall c \in C_{\text{dem}},~ t \in T_m:
   -d_{ct} \geq \text{CB}(c,t),

where :math:`C_{\text{dem}}` is the set of demand commodities and
:math:`d_{ct}` the corresponding demand for commodity :math:`c` at time
:math:`t`. These two rules thus state that all stock commodities that are
consumed at any time in any process must be taken from the stock and that all
demands have to be fulfilled at each time step.

Stock commodity limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~
There are two rule that govern the retrieval of stock commodities from stock:
The total stock and the stock per hour rule. The former limits the total amount
of stock commodity that can be retrieved annually and the latter limits the
same quantity per timestep. the two rules take the following form:

.. math::
   &\forall c \in C_{\text{st}}:\\
   &w \sum_{t\in T_{m}}\rho_{ct}\leq \overline{L}_c\\\\
   &\forall c \in C_{\text{st}},~t\in T_m:\\
   &\rho_ct\leq \overline{l}_{c},

where :math:`\overline{L}_c` and :math:`\overline{l}_c` are the totally allowed
annual and hourly retrieval of commodity :math:`c` from the stock,
respectively.

Environmental commodity limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Similar to stock commodities, environmental commodities can also be limited
per hour or per year. Both properties are assured by the following two
rules:

.. math::
   &\forall c \in C_{\text{env}}:\\
   &-w \sum_{t\in T_{m}}\text{CB}(c,t)\leq \overline{M}_c\\\\
   &\forall c \in C_{\text{env}},~t\in T_m:\\
   & -\text{CB}(c,t)\leq \overline{m}_{c},

where :math:`\overline{M}_c` and :math:`\overline{m}_c` are the totally allowed
annual and hourly emissions of environmental commodity :math:`c` to the
atmosphere, respectively.

Process dispatch constraints
----------------------------
So far, apart from the commodity balance function, the interaction between
processes and commodities have not been discussed. It is perhaps in order to
start with the general idea behind the modeling of the process operation. In
urbs all processes are mimo-processes, i.e., in general they in take in
multiple commodities as inputs and give out multiple commodities as outputs.
The respective ratios between the respective commodity flows remain normally
fixed. The operational state of the process is then captured in just one
variable, the process throughput :math:`\tau_{pt}` and is is linked to the
commodity flows via the following two rules:

.. math::
   &\forall p\in P,~c\in C,~t \in T_m:\\
   &\epsilon^{\text{in}}_{pct}=r^{\text{in}}_{pc}\tau_{pt}\\
   &\epsilon^{\text{out}}_{pct}=r^{\text{out}}_{pc}\tau_{pt},

where :math:`r^{\text{in, out}}_{pc}` are the constant factors linking the
commodity flow to the operational state. The efficiency :math:`\eta` of the
process :math:`p` for the conversion of commodity :math:`c_1` into commodity
:math:`c_2` is then simply given by:

.. math::
   \eta=\frac{r^{\text{out}}_{pc_2}}{r^{\text{in}}_{pc_1}}.

Basic process throughput rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The throughput :math:`\tau_{pt}` of a process is limited by its installed
capacity and the specified minimal operational state. Furthermore, the
switching speed of a process can be limited:

.. math::
   &\forall p\in P,~t\in T_m:\\
   &\tau_{pt}\leq \kappa_{p}\\
   &\tau_{pt}\geq \underline{P}_{p}\kappa_{p}\\
   &|\tau_{pt}-\tau_{p(t-1)}|\leq \Delta t\overline{PG}_p\kappa_{p},

where :math:`\underline{P}_{p}` is the normalized, minimal operational state of
the process and :math:`\overline{PG}_p` the normalized, maximal gradient of the
operational state in full capacity per timestep.

Intermittend supply rule
~~~~~~~~~~~~~~~~~~~~~~~~
If the input commodity is of type 'SupIm', which means that it represents an
operational state rather than a proper material flow, the operational state of
the process is governed by this alone. This feature is typically used for
renewable energies but can be used whenever a certain operation time series of
a given process is desired

.. math::
   &\forall p\in P,~c\in C_{\text{sup}},~t\in T_m:\\
   &\epsilon^{\text{in}}_{cpt}=s_{ct}\kappa_{p}.

Here, :math:`s_{ct}` is the time series that governs the exact operation of
process :math:`p`, leaving only its capacity :math:`\kappa_{p}` as a free
variable.

Part load behavior
~~~~~~~~~~~~~~~~~~
Many processes show a non-trivial part-load behavior. In particular, often a
nonlinear reaction of the efficiency on the operational state is given.
Although urbs itself is a linear program this can with some caveats be captured
in many cases. The reason for this is, that the efficiency of a process is
itself not modeled but only the ratio between input and output multipliers. It
is thus possible to use purely linear functions to get a nonlinear behavior of
the efficiency of the form:

.. math::
   \eta=\frac{a+b\tau_{pt}}{c+d\tau_{pt}},

where a,b,c and d are some constants. Specifically, the input and output ratios
can be set to vary linearly between their respective values at full load
:math:`r^{\text{in,out}}_{pc}` and their values at the minimal allowed
operational state :math:`\underline{P}_{p}\kappa_p`, which are given by
:math:`\underline{r}^{\text{in,out}}_{pc}`. This is achieved with the following
equations:

.. math::
   &\forall p\in P^{\text{partload}},~c\in C,~t\in T_m:\\\\
   &\epsilon^{\text{in,out}}_{pct}=\Delta t\cdot\left(
   \frac{\underline{r}^{\text{in,out}}_{pc}-r^{\text{in,out}}_{pc}}
   {1-\underline{P}_p}\cdot \underline{P}_p\cdot \kappa_p+
   \frac{r^{\text{in,out}}_{pc}-
   \underline{P}_p\underline{r}^{\text{in,out}}_{pc}}
   {1-\underline{P}_p}\cdot \tau_{pt}\right).

A few restrictions have to be kept in mind when using this feature:

* :math:`\underline{P}_p` has to be set larger than 0 otherwise the feature
  will work but not have any effect.
* Environmental output commodities have to mimic the behavior of the inputs by
  which they are generated. Otherwise the emissions per unit of input would
  change together with the efficiency, which is typically not the desired
  behavior.

This concludes the minimal model.