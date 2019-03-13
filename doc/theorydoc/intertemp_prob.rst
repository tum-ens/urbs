.. module:: urbs

.. _theory-intertemp:

Intertemporal optimization model
================================
Intertemporal models are a more general type of model than the minimal case.
For such models a second time domain is introduced to capture the behavior of
the system over a timeframe of many years, thus rendering a modeling of the
system development, rather than the optimal system configuration, possible. 
To keep the model as small as possible while still capturing most of the
intertemporal behavior, the second time slice is approximated by a number of
support timeframes (years) :math:`Y=(y_1,...,y_n)`, which is in general smaller
than the total model horizon. Each modeled timeframe is then essentially a
minimal (or multinode-) model in its own right. The basic approximative
assumption linking the modeled timeframes are then given by:

* Each modeled year is repeated :math:`k` times if the next modeled year is
  :math:`k` years later. The last year is repeated a user specified number of
  times.
* The depreciation period is assumed to be also the operational period of any
  unit built. There is no operation in an economically fully depreciated state.
* A unit can only be operated in a given modeled year when it is operational
  for the entire period that year represents, i.e., until the next modeled
  year.
* All payments are exponentially discounted with a discount rate :math:`j` that
  is set once for the entire modeling horizon.

The variable vector is as a first step only changed in so far, as the second
time domain is entering the index. It now reads:

.. math::

   x^{\text{T}}=(\zeta, \underbrace{\rho_{yct}}_{\text{commodity variables}},
   \underbrace{\kappa_{yp}, \widehat{\kappa}_{yp}, \tau_{ypt},
   \epsilon^{\text{in}}_{ycpt},
   \epsilon^{\text{out}}_{ycpt}}_{\text{process variables}}).

Here, :math:`\zeta` represents the total discounted system costs over the
entire modeling horizon, :math:`\rho_yct` the amount of commodities :math:`c`
taken from a virtual, infinite stock in year :math:`y` at time :math:`t`,
:math:`\kappa_{yp}` and :math:`\widehat{\kappa}_{yp}` the total
and the newly installed process capacities in year :math:`y` of processes
:math:`p`, :math:`\tau_{ypt}` the operational state in year :math:`y` of
processes :math:`p` at time :math:`t` and :math:`\epsilon^{\text{in}}_{ycpt}`
and :math:`\epsilon^{\text{out}}_{ycpt}` the total inputs and outputs in year
:math:`y` of commodities :math:`c` to and from process :math:`p` at time
:math:`t`, respectively.

All dispatch constraint equations for commodities and processes described in
the minimal model section, as well as all such constraints for transmissions,
storages, DSM described in their respective dedicated sections, remain
structurally the same in an intertemporal model. The only modification there
is, that the modeled year shows up as an additional index.

The parts that change in a more meaningful way are the costs and the unit
expansion constraints.     

Costs
-----
As in the minimal model the total cost variable can be split into the following
sum:

.. math::

   \zeta = \zeta_{\text{inv}} + \zeta_{\text{fix}} + \zeta_{\text{var}} +
   \zeta_{\text{fuel}} + \zeta_{\text{env}},

where :math:`\zeta_{\text{inv}}` are the discounted invest costs accumulated
over the entire modeled period, :math:`\zeta_{\text{fix}}` the discounted,
accumulated fixed costs, :math:`\zeta_{\text{var}}` the discounted, sum over
the modeled years of all variable costs accumulated over each year,
:math:`\zeta_{\text{fuel}}` the discounted sum over the modeled years of
fuel costs accumulated over each year and :math:`\zeta_{\text{env}}`
the discounted total penalty for environmental pollution.

All costs are discounted by the same exponent :math:`j` for the entire modeling
horizon on a yearly basis. This means that any payment :math:`x` that has to be
made in a year :math:`k` will be discounted for the cost function :math:`\zeta`
by:

.. math::
   x_{\text{discounted}}=(1+j)^{-k}\cdot x

Since all non-modeled years are just treated as exact copies of the last
modeled year before them, the discounted sum of fix, variable, fuel and
environmental costs can simply be taken as the costs of the representative
modeled year :math:`m` multiplied by a factor :math:`D_m`. If the distance to
the next modeled year is :math:`k`, it can be calculated via:

.. math::
   D_m&=\sum_{l=m}^{m+k-1}(1+j)^{-l}=(1+j)^{-m}\sum_{l=0}^{k-1}(1+j)^{-l}=
   (1+j)^{-m}\frac{1-(1+j)^{-k}}{1-(1+j)^{-1}}=\\\\
   &=(1+j)^{1-m}\frac{1-(1+j)^{-k}}{j}.

So for example the variable costs for modeled year :math:`m` and its :math:`k`
identical, non-modeled copies :math:`\zeta_{\text{var}}^{\{m,m+1,..,m+k-1\}}`
are given by:

.. math::
   \zeta_{\text{var}}^{\{m,m+1,..,m+k-1\}}=D_m\cdot\zeta_{\text{var}}^{m},

if :math:`\zeta_{\text{var}}^m` is the sum of all variable costs accumulated by
the use of units in the year :math:`m` alone by the model.

Intertemporal calculation of invest costs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In the intertemporal model, invest costs are calculated using the annuity
method. This directly entails that there are no rest values of any units built
by the model that have to be considered for the cost function. It is then
possible to multiply the annuity payments :math:`fC` for a unit with investment
costs :math:`C` built in year :math:`m` simply with the factor :math:`D_{m}`.
The only difference is, that the investment annuity payments are not restricted
to the modeled years but have to be paid for the entire depreciation period
provided that it is within the modeled time horizon. When the depreciation
period is :math:`n` and :math:`k` is the number of payments that fall in the
modeled time horizon, the total costs :math:`C_{\text{total}}`
of an investment of size :math:`C` made in year :math:`m` is given by:

.. math::
   C^{\text{total}}_{\text{m}}&=D_{m}\cdot f \cdot C =
   (1+j)^{1-m}\frac{1-(1+j)^{-k}}{j} \cdot \frac{(1+i)^n\cdot i}{(1+i)^n-1}
   \cdot C=\\\\
   &=\underbrace{(1+j)^{1-m}\cdot \frac{i}{j}\cdot
   \left(\frac{1+i}{1+j}\right)^n\cdot
   \frac{(1+j)^n-(1+j)^{n-k}}{(1+i)^n-1}}_{=:I_{\text{m}}}\cdot C

For either
:math:`i=0` or :math:`j=0` a distinction has to be made, which takes the
following form:

* :math:`i=0,~j=0`:

  .. math::
    C^{\text{total}}_{\text{m}}=\underbrace{\frac{k}{n}}_{=:I_{\text{m}}}\cdot
    C

* :math:`i\neq0,~j=0`:

  .. math::
    C^{\text{total}}_{\text{m}}=k\cdot f\cdot C=\underbrace{k\cdot
    \frac{(1+i)^n\cdot i}{(1+i)^n-1}}_{=:I_{\text{m}}}\cdot C

* :math:`i=0,~j\neq0`:

  .. math::
    C^{\text{total}}_{\text{m}}=\frac 1n \cdot (1+j)^{-m}
    \sum_{l=0}^{k-1}(1+j)^{-l} \cdot C=\underbrace{\frac 1n \cdot (1+j)^{-m}
    \cdot \frac{(1+j)^k-1}{(1+j)^k\cdot j}}_{=:I_{\text{m}}}\cdot C

In any case the total invest costs are then given by:

.. math::
   \zeta_{\text{inv}}=\sum_{y\in Y\\p\in P}C^{\text{total}}_{\text{m}}=
   \sum_{y\in  Y\\p\in P}I_{\text{y}}k^{\text{inv}}_{yp} \widehat{\kappa}_{yp}

Unit expansion constraints
--------------------------
Apart from the costs there are also changes in the unit expansion constraints
for an intertemporal model. These changes mostly concern how the amount of
installed units is found. This becomes an issue since units built in an earlier
modeled year or already installed in the first modeled year, may or may not be
operational in a given modeled year :math:`m` and through :math:`m+k-1`. Here,
:math:`k` is the distance to the next modeled year or the end of the modeled
horizon in case of :math:`m` being the last modeled year. To properly calculate
the capacity of a process in a year :math:`y` the following two sets are
necessary:

.. math::
   O&:=\{(p,y_i,y_j)|p\in P,~\{y_i,y_j\}\in Y,~y_i\leq y_j,~ y_i +
   L_p \geq\ y_{j+1}\}\\\\
   O_{\text{inst}}&:=\{(p, y_j)|p\in P_0,~y\in Y,~y_0+T_p\geq y_{j+1}\},

where :math:`L_p` is the lifetime of processes :math:`p`, :math:`P_0` the
subset of processes that are already installed in the first modeled year
:math:`y_0` and :math:`T_{p}` the rest lifetime of already installed processes.
If :math:`y_j` is the last modeled year, :math:`y_{j+1}` stands for the end of
the model horizon.   

With these two sets the installed process capacity in a given year is then
given by:

.. math::
   \kappa_{yp}&=\sum_{y^{\prime}\in Y\\(p,y^{\prime},y)\in O}
   \widehat{\kappa}_{y^{\prime}p} + K_{p}
   ~,~~\text{if}~(p,y)\in O_{\text{inst}}\\\\
   \kappa_{yp}&=\sum_{y^{\prime}\in Y\\(p,y^{\prime},y)\in O}
   \widehat{\kappa}_{y^{\prime}p}~,~~\text{else}

where :math:`K_{p}` is the installed capacity of process :math:`p` at the
beginning of the modeling horizon. Since for each modeled year still the
capacity constraint

.. math::
   &\forall y\in Y,~ p \in P:\\
   &\underline{K}_{yp}\leq\kappa_{yp}\leq\overline{K}_{yp}

is valid, the set constraints can have effects across years and especially the
modeller has to be careful not to set infeasible constraints.

Commodity dispatch constraints
------------------------------
While in an intertemporal model all commodity constraints within one modeled
year remain valid one addition is possible concerning CO2 emissions. Here, a
budget can be given, which is valid over the entire modeling horizon:

.. math::
   -w\sum_{y\in Y\\t\in T_{m}}\text{CB}(y,\text{CO}_2,t)\leq
   \overline{\overline{L}}_{\text{CO}_2}

Here, :math:`\overline{\overline{L}}_c` is the global budget for the emission
of the environmental commodity. Currently this is hard coded for CO2 only.

This rule concludes the model additions introduced by intertemporal modeling.