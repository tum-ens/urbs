.. module:: urbs

Economic Parameters
^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Economic Model Parameters*

	+----------------------------------+---------+-------------------------------------------------+
	|Parameter                         |Unit     |Description                                      |
	+==================================+=========+=================================================+
	|:math:`j`                         | _       |Global Discount rate                             |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`D_y`                       | _       |Factor for any payment made in modeled year y    |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`I_y`                       | _       |Factor for any investment made in modeled year y |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`\overline{L}_{\text{cost}}`|€        |Maximum total system costs (if CO2 is minimized) |
	+----------------------------------+---------+-------------------------------------------------+
	|**Commodity Economic Parameters**                                                             |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvc}^\text{fuel}`       |€/MWh    |Stock Commodity Fuel Costs                       |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvc}^\text{env}`        |€/MWh    |Environmental Commodity Costs                    |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvct}^\text{bs}`        |€/MWh    |Buy/Sell Commodity Buy/Sell Costs                |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvc}^\text{bs}`         | _       |Multiplier for Buy/Sell Commodity Buy/Sell Costs |
	+----------------------------------+---------+-------------------------------------------------+
	|**Process Economic Parameters**                                                               |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`i_{yvp}`                   | _       |Weighted Average Cost of Capital for Process     |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`z_{yvp}`                   | _       |Process Depreciation Period                      |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvp}^\text{inv}`        |€/MW     |Process Capacity Investment Costs                |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvp}^\text{fix}`        |€/(MW a) |Annual Process Capacity Fixed Costs              |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvp}^\text{var}`        |€/MWh    |Process Throughput Variable Costs                |
	+----------------------------------+---------+-------------------------------------------------+
	|**Storage Economic Parameters**                                                               |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`i_{yvs}`                   | _       |Weighted Average Cost of Capital for Storage     |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`z_{yvs}`                   | _       |Storage Depreciation Period                      |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvs}^\text{p,inv}`      |€/MW     |Storage Power Investment Costs                   |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvs}^\text{p,fix}`      |€/(MW a) |Annual Storage Power Fixed Costs                 |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvs}^\text{p,var}`      |€/MWh    |Storage Power Variable Costs                     |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvs}^\text{c,inv}`      |€/MWh    |Storage Size Investment Costs                    |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvs}^\text{c,fix}`      |€/(MWh a)|Annual Storage Size Fixed Costs                  |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yvs}^\text{c,var}`      |€/MWh    |Storage Usage Variable Costs                     |
	+----------------------------------+---------+-------------------------------------------------+
	|**Transmission Economic Parameters**                                                          |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`i_{yvf}`                   | _       |Weighted Average Cost of Capital for Transmission|
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`z_{yaf}`                   | _       |Tranmission Depreciation Period                  |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yaf}^\text{inv}`        |€/MW     |Transmission Capacity Investment Costs           |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yaf}^\text{fix}`        |€/(MW a) |Annual Transmission Capacity Fixed Costs         |
	+----------------------------------+---------+-------------------------------------------------+
	|:math:`k_{yaf}^\text{var}`        |€/MWh    |Tranmission Usage Variable Costs                 |
	+----------------------------------+---------+-------------------------------------------------+

**Discount rate**, :math:`j`,
``m.global_prop.xs('Discount rate', level=1).loc[m.global_prop.index.min()[0]]['value']``:
The discount rate :math:`j` is used to calculate the present value of future
costs. It is set in the worksheet "Global" in the input file of the first
support timeframe.

**Factor for future payments**, :math:`D_y`: The parameter :math:`D_y`
is a multiplier that has to be factored into all cost terms apart from the
invest costs in intertemporal planning based on support timeframes. All other
cost terms for the support timeframe :math:`y` are muliplied directly with this
factor to find the present value of the sum of costs in support timeframe
:math:`y` and all non-modeled time frames until the next modeled time frame
:math:`y_{+1}`, which are identical to the support timeframe with the modeling
approach taken:
 
.. math::
   D_y=(1+j)^{1-(y-y_{\text{min}})}\cdot \frac{1-(1+j)^{-(y_{+1}-y+1)}}{j}

In script ``modelhelper.py`` the factor :math:`D_y` is implemented as the
product of the functions:

.. literalinclude:: /../urbs/features/modelhelper.py
   :pyobject: discount_factor

and

.. literalinclude:: /../urbs/features/modelhelper.py
   :pyobject: effective_distance

**Factor for investment made in support timeframe y**, :math:`I_y`: The
parameter :math:`I_y` is a multiplier that has to be factored into the invest
costs in intertemporal planning based on support timeframes. The book value of
the total invest costs per capacity in support timeframe :math:`y` is muliplied
with this factor to find the present value of the sum of costs of all annual
payments made for this investment within the modeling horizon. The calculation
of this parameter requires several case distinctions and is given by: 

* :math:`i\neq0,~j\neq0`:

.. math::
   I_{y}=(1+j)^{1-(y-y_{\text{min}})}\cdot \frac{i}{j}\cdot
   \left(\frac{1+i}{1+j}\right)^n\cdot
   \frac{(1+j)^n-(1+j)^{n-k}}{(1+i)^n-1}

* :math:`i=0,~j=0`:

  .. math::
    I_{y}=\frac{k}{n}

* :math:`i\neq0,~j=0`:

  .. math::
    I_{y}=k\cdot\frac{(1+i)^n\cdot i}{(1+i)^n-1}

* :math:`i=0,~j\neq0`:

  .. math::
    I_{y}=\frac 1n \cdot (1+j)^{-m}\cdot \frac{(1+j)^k-1}{(1+j)^k\cdot j}

where :math:`k` is the number of annualized payments that have to be made
within the modeling horizon, :math:`n` the depreciation period and :math:`i`
the weighted average cost of capital. Note that the parameters :math:`i` and
:math:`n` take different values for different unit tuples.

In script ``modelhelper.py`` the factor :math:`I_y` is implemented with the
function:

.. literalinclude:: /../urbs/features/modelhelper.py
   :pyobject: invcost_factor

In this formulation also payments after the modeled time horizon are being
made. To fix this the overpay is subtracted via:  

.. literalinclude:: /../urbs/features/modelhelper.py
   :pyobject: overpay_factor

In case of negative values this overpay factor is set to zero afterwards.

**Maximum total system cost**, :math:`\overline{L}_{\text{cost}}`,
``m.global_prop.loc[(min(m.stf), 'Cost budget'), 'value']``: This parameter
restricts the total present costs over the entire modeling horizon. It is only
sensible and active when the objective is a minimization of CO2 emissions.  

Commodity Economic Parameters
-----------------------------

**Stock Commodity Fuel Costs**, :math:`k_{vc}^\text{fuel}`,
``m.commodity_dict['price'][c]``: The parameter :math:`k_{yvc}^\text{fuel}`
represents the book cost for purchasing one unit (1 MWh) of a stock commodity
:math:`c` (:math:`\forall c \in C_\text{stock}`) in modeled timeframe :math:`y`
in a site :math:`v` (:math:`\forall v \in V`). The unit of this parameter is
€/MWh. The related section for this parameter in the spreadsheet belonging the
support timeframe :math:`y` can be found in the "Commodity" sheet. Here each
row represents another commodity tuple :math:`c_{yvq}` and the column of stock
commodity tuples (:math:`\forall q = "Stock"`) in this sheet with the header
label "price" represents the corresponding parameter
:math:`k_{yvc}^\text{fuel}`.

**Environmental Commodity Costs**, :math:`k_{yvc}^\text{env}`,
``m.commodity_dict['price'][c]``: The parameter :math:`k_{yvc}^\text{env}`
represents the book cost for producing/emitting one unit (1 t, 1 kg, ...) of an
environmental commodity :math:`c` (:math:`\forall c \in C_\text{env}`) in
support timeframe :math:`y` in a site :math:`v` (:math:`\forall v \in V`). The
unit of this parameter is €/t (i.e. per unit of output). The related section
for this parameter in the spreadsheet corresponding to support timeframe
:math:`y` is the "Commodity" sheet. Here, each row represents a commodity tuple
:math:`c_{yvq}` and the fourth column of environmental commodity tuples
(:math:`\forall q = "Env"`) in this sheet with the header label "price"
represents the corresponding parameter :math:`k_{yvc}^\text{env}`.

**Buy/Sell Commodity Buy/Sell Costs**, :math:`k_{yvct}^\text{bs}`,
``m.buy_sell_price_dict[c[2], ][(c[0], tm)]``: The parameter
:math:`k_{yvct}^\text{bs}` represents the purchase/buy cost for
purchasing/selling one unit (1 MWh) of a buy/sell commodity :math:`c`
(:math:`\forall c \in C_\text{buy}`)/(:math:`\forall c \in C_\text{sell}`) in
support timeframe :math:`y` in a site :math:`v` (:math:`\forall v \in V`) at
timestep :math:`t` (:math:`\forall t \in T_m`). The unit of this parameter is
€/MWh. The related section for this parameter in the spreadsheet can be found
in the "Buy-Sell-Price" sheet. Here each column represents a commodity tuple
and the row values provide the timestep information.

**Multiplyer for Buy/Sell Commodity Buy/Sell Costs**,
:math:`k_{yvc}^\text{bs}`, ``m.commodity_dict['price'][c]``: The parameter
:math:`k_{yvc}^\text{bs}` is a multiplier for the buy/sell time series. It
represents the factor on the purchase/buy cost for purchasing/selling one unit
(1 MWh) of a buy/sell commodity :math:`c`
(:math:`\forall c \in C_\text{buy}`)/(:math:`\forall c \in C_\text{sell}`) in
support timeframe :math:`y` in a site :math:`v` (:math:`\forall v \in V`). This
parameter is unitless. The related section for this parameter in the
spreadsheet belonging to support timeframe :math:`y` can be found in the
"Commodity" sheet. Here each row represents another commodity tuple
:math:`c_{yvq}` and the column of Buy/Sell commodity tuples
(:math:`\forall q = "Buy/Sell"`) in this sheet with the header label "price"
represents the corresponding parameter :math:`k_{yvc}^\text{bs}`.

Process Economic Parameters
---------------------------

**Weighted Average Cost of Capital for Process**, :math:`i_{yvp}`, : The
parameter :math:`i_{yvp}` represents the weighted average cost of capital for a
process technology :math:`p` in support timeframe ;math:`y` in a site
:math:`v`. The weighted average cost of capital gives the interest rate (%) of
costs for capital after taxes. The related section for this parameter in the
spreadsheet corresponding to support timeframe :math:`y` can be found under the
"Process" sheet. Here each row represents another process tuple and the column
with the header label "wacc" represents the parameters :math:`i_{yvp}`. The
parameter is given as a percentage, where "0.07" means 7%

**Process Depreciation Period**, :math:`z_{yvp}`: The parameter :math:`z_{yvp}`
represents the depreciation period of a process :math:`p` built in support
timeframe :math:`y` in a site :math:`v`. The depreciation period gives the
economic and technical lifetime of a process investment. It thus features in
the calculation of the invest cost factor and determines the end of operation
of the process. The unit of this parameter is "a", where "a" represents a year
of 8760 hours. The related section for this parameter in the spreadsheet can be
found under the "Process" sheet. Here each row represents another process tuple
and the column with the header label "depreciation" represents the parameters
:math:`z_{yvp}`.

**Process Capacity Investment Costs**, :math:`k_{yvp}^\text{inv}`,
``m.process_dict['inv-cost'][p]``: The parameter :math:`k_{yvp}^\text{inv}`
represents the book value of the investment cost for adding one unit new
capacity of a process technology :math:`p` in support timeframe :math:`y` in a
site :math:`v`. The unit of this parameter is €/MW. To get the full impact of
the investment within the modeling horizon this parameter is multiplied with
the factor for the investment made in modeled year y :math:`I_y`. The process
capacity investment cost is to be given as an input by the user. The related
section for the process capacity investment cost in the spreadsheet
representing the support timeframe :math:`y` can be found under the "Process"
sheet. Here each row represents another process :math:`p` in a site :math:`v`
and the column with the header label "inv-cost" represents the process capacity
investment costs of the corresponding process :math:`p` and site :math:`v`
combinations.

**Process Capacity Fixed Costs**, :math:`k_{yvp}^\text{fix}`,
``m.process_dict['fix-cost'][p]``: The parameter :math:`k_{yvp}^\text{fix}`
represents the fix cost per one unit capacity :math:`\kappa_{yvp}` of a process
technology :math:`p` in support timeframe :math:`y` in a site :math:`v`, that
is charged annually. The unit of this parameter is €/(MW a). The related
section for this parameter in the spreadsheet correesponding to the support
timeframe :math:`y` can be found under the "Process" sheet. Here each row
represents another process :math:`p` in a site :math:`v` and the column with
the header label "fix-cost" represents the parameters
:math:`k_{yvp}^\text{fix}` of the corresponding process :math:`p` and site
:math:`v` combinations. 

**Process Variable Costs**, :math:`k_{yvp}^\text{var}`,
``m.process_dict['var-cost'][p]``: The parameter :math:`k_{yvp}^\text{var}`
represents the book value of the variable cost per one unit energy throughput
:math:`\tau_{yvpt}` through a process technology :math:`p` in a site :math:`v`
in support timeframe :math:`y`. The unit of this parameter is €/MWh. The
related section for this parameter in the spreadsheet corresponding to the
support timeframe :math:`y` can be found under the "Process" sheet. Here each
row represents another process :math:`p` in a site :math:`v` and the column
with the header label "var-cost" represents the parameters
:math:`k_{yvp}^\text{var}` of the corresponding process :math:`p` and site
:math:`v` combinations.

Storage Economic Parameters
---------------------------

**Weighted Average Cost of Capital for Storage**, :math:`i_{yvs}`, : The
parameter :math:`i_{yvs}` represents the weighted average cost of capital for a
storage technology :math:`s` in a site :math:`v` and support timeframe
:math:`y`. The weighted average cost of capital gives the interest rate(%) of
costs for capital after taxes. The related section for this parameter in the
spreadsheet corresponding to the support timeframe :math:`y` can be found under
the "Storage" sheet. Here each row represents another storage :math:`s` in a
site :math:`v` and the column with the header label "wacc" represents the
parameters :math:`i_{yvs}` of the corresponding storage :math:`s` and site
:math:`v` combinations. The parameter is given as a percentage, where "0.07"
means 7%.

**Storage Depreciation Period**, :math:`z_{yvs}`, (a): The parameter
:math:`z_{yvs}` represents the depreciation period of a storage :math:`s` in a
site :math:`v` built in support timeframe :math:`y`. The depreciation period
gives the economic and technical lifetime of a storage investment. It thus
features in the calculation of the invest cost factor and determines the end of
operation of the storage. The unit of this parameter is "a", where "a"
represents a year of 8760 hours. The related section for this parameter in the
spreadsheet corresponding to the support timeframe :math:`y` can be found under
the "Storage" sheet. Here each row represents another storage :math:`s` in a
site :math:`v` and the column with the header label "depreciation" represents
the parameters :math:`z_{yvs}` of the corresponding storage :math:`s` and site
:math:`v` combinations.

**Storage Power Investment Costs**, :math:`k_{yvs}^\text{p,inv}`,
``m.storage_dict['inv-cost-p'][s]``: The parameter :math:`k_{yvs}^\text{p,inv}`
represents the book value of the total investment cost for adding one unit new
power output capacity of a storage technology :math:`s` in a site :math:`v` in
support timeframe :math:`y`. The unit of this parameter is €/MW. To get the
full impact of the investment within the modeling horizon this parameter is
multiplied with the factor for the investment made in modeled year y
:math:`I_y`. The related section for the storage power output capacity
investment cost in the spreadsheet corresponding to the support timeframe
:math:`y` can be found under the "Storage" sheet. Here each row represents
another storage :math:`s` in a site :math:`v` and the column with the header
label "inv-cost-p" represents the storage power output capacity investment cost
of the corresponding storage :math:`s` and site :math:`v` combinations. 

**Annual Storage Power Fixed Costs**, :math:`k_{yvs}^\text{p,fix}`,
``m.storage_dict['fix-cost-p'][s]``: The parameter :math:`k_{yvs}^\text{p,fix}`
represents the fix cost per one unit power output capacity of a storage
technology :math:`s` in a site :math:`v` and support timeframe :math:`y`, that
is charged annually. The unit of this parameter is €/(MW a). The related
section for this parameter in the spreadsheet corresponding to support
timeframe :math:`y` can be found under the "Storage" sheet. Here each row
represents another storage :math:`s` in a site :math:`v` and the column with
the header label "fix-cost-p" represents the parameters
:math:`k_{yvs}^\text{p,fix}` of the corresponding storage :math:`s` and site
:math:`v` combinations.

**Storage Power Variable Costs**, :math:`k_{yvs}^\text{p,var}`,
``m.storage_dict['var-cost-p'][s]``: The parameter :math:`k_{yvs}^\text{p,var}`
represents the variable cost per unit energy, that is stored in or retrieved
from a storage technology :math:`s` in a site :math:`v` in support timeframe
:math:`y`. The unit of this parameter is €/MWh. The related section for this
parameter in the spreadsheet corresponding to support timeframe :math:`y` can
be found under the "Storage" sheet. Here each row represents another storage
:math:`s` in a site :math:`v` and the column with the header label "var-cost-p"
represents the parameters :math:`k_{yvs}^\text{p,var}` of the corresponding
storage :math:`s` and site :math:`v` combinations.

**Storage Size Investment Costs**, :math:`k_{yvs}^\text{c,inv}`,
``m.storage_dict['inv-cost-c'][s]``: The parameter :math:`k_{yvs}^\text{c,inv}`
represents the book value of the total investment cost for adding one unit new
storage capacity to a storage technology :math:`s` in a site :math:`v` in
support timeframe :math:`y`. The unit of this parameter is €/MWh. To get the
full impact of the investment within the modeling horizon this parameter is
multiplied with the factor for the investment made in modeled year y
:math:`I_y`. The related section for the storage content capacity investment
cost in the spreadsheet corresponding to support timeframe :math:`y` can be
found under the "Storage" sheet. Here each row represents another storage
:math:`s` in a site :math:`v` and the column with the header label "inv-cost-c"
represents the storage content capacity investment cost of the corresponding
storage :math:`s` and site :math:`v` combinations. 

**Annual Storage Size Fixed Costs**, :math:`k_{yvs}^\text{c,fix}`,
``m.storage_dict['fix-cost-c'][s]``: The parameter :math:`k_{yvs}^\text{c,fix}`
represents the fix cost per year per one unit storage content capacity of a
storage technology :math:`s` in a site :math:`v` in support timeframe
:math:`y`. The unit of this parameter is €/(MWh a). The related section for
this parameter in the spreadsheet corresponding to support timeframe :math:`y`
can be found under the "Storage" sheet. Here each row represents another
storage :math:`s` in a site :math:`v` and the column with the header label
"fix-cost-c" represents the parameters :math:`k_{vs}^\text{c,fix}` of the
corresponding storage :math:`s` and site :math:`v` combinations.

**Storage Usage Variable Costs**, :math:`k_{yvs}^\text{c,var}`,
``m.storage_dict['var-cost-c'][s]``: The parameter :math:`k_{yvs}^\text{p,var}`
represents the variable cost per unit energy, that is conserved in a storage
technology :math:`s` in a site :math:`v` in support timeframe :math:`y`. The
unit of this parameter is €/MWh. The related section for this parameter in the
spreadsheet corresponding to support timeframe :math:`y` can be found under the
"Storage" sheet. Here each row represents another storage :math:`s` in a site
:math:`v` and the column with the header label "var-cost-c" represents the
parameters :math:`k_{yvs}^\text{c,var}` of the corresponding storage :math:`s`
and site :math:`v` combinations. The value of this parameter is usually set to
zero, but the parameter can be taken advantage of if the storage has a short
term usage or has an increased devaluation due to usage, compared to amount of
energy stored. 

Transmission Economic Parameters
--------------------------------

**Weighted Average Cost of Capital for Transmission**, :math:`i_{yvf}`, : The
parameter :math:`i_{yvf}` represents the weighted average cost of capital for a
transmission :math:`f` transferring commodities through an arc :math:`a` built
in support timeframe :math:`y`. The weighted average cost of capital gives the
interest rate(%) of costs for capital after taxes. The related section for this
parameter in the spreadsheet corresponding to support timeframe :math:`y` can be
found under the "Transmission" sheet. Here each row represents another
transmission :math:`f` transferring commodities through an arc :math:`a` and
the column with the header label "wacc" represents the parameters
:math:`i_{yvf}` of the corresponding transmission :math:`f` and arc :math:`a`
combinations. The parameter is given as a percentage, where "0.07" means 7%.

**Transmission Depreciation Period**, :math:`z_{yaf}`, (a): The parameter
:math:`z_{yaf}` represents the depreciation period of a transmission :math:`f`
transferring commodities through an arc :math:`a` built in support timeframe
:math:`y`. The depreciation period of gives the economic and technical lifetime
of a transmission investment. It thus features in the calculation of the invest
cost factor and determines the end of operation of the transmission. The unit
of this parameter is "a", where "a" represents a year of 8760 hours. The
related section for this parameter in the spreadsheet corresponding to support
timeframe :math:`y` can be found under the "Transmission" sheet. Here each row
represents another transmission :math:`f` transferring commodities through an
arc :math:`a` and the column with the header label "depreciation" represents
the parameters :math:`z_{yaf}` of the corresponding transmission :math:`f` and
arc :math:`a` combinations.

**Transmission Capacity Investment Costs**, :math:`k_{yaf}^\text{inv}`,
``m.transmission_dict['inv-cost'][t]``: The parameter
:math:`k_{yaf}^\text{inv}` represents the book value of the investment cost for
adding one unit new transmission capacity to a transmission :math:`f`
transferring commodities through an arc :math:`a` in support timeframe
:math:`y`. To get the full impact of the investment within the modeling horizon
this parameter is multiplied with the factor for the investment made in modeled
year y :math:`I_y`. The unit of this parameter is €/MW. The related section for
the transmission capacity investment cost in the spreadsheet corresponding to
support timeframe :math:`y` can be found under the "Transmission" sheet. Here
each row represents another transmission :math:`f` transferring commodities
through an arc :math:`a` and the column with the header label "inv-cost"
represents the transmission capacity investment cost of the corresponding
transmission :math:`f` and arc :math:`a` combinations.

**Annual Transmission Capacity Fixed Costs**, :math:`k_{yaf}^\text{fix}`,
``m.transmission_dict['fix-cost'][t]``: The parameter
:math:`k_{yaf}^\text{fix}` represents the annual fix cost per one unit capacity
of a transmission :math:`f` transferring commodities through an arc :math:`a`.
The unit of this parameter is €/(MW a). The related section for this parameter
in the spreadsheet corresponding to support timeframe :math:`y` can be found
under the "Transmission" sheet. Here each row represents another transmission
:math:`f` transferring commodities through an arc :math:`a` and the column with
the header label "fix-cost" represents the parameters
:math:`k_{yaf}^\text{fix}` of the corresponding transmission :math:`f` and arc
:math:`a` combinations.

**Transmission Usage Variable Costs**, :math:`k_{yaf}^\text{var}`,
``m.transmission_dict['var-cost'][t]``: The parameter
:math:`k_{yaf}^\text{var}` represents the variable cost per unit energy, that
is transferred with a transmission :math:`f` through an arc :math:`a`. The unit
of this parameter is €/ MWh. The related section for this parameter in the
spreadsheet corresponding to support timeframe :math:`y` can be found under the
"Transmission" sheet. Here each row represents another transmission :math:`f`
transferring commodities through an arc :math:`a` and the column with the
header label "var-cost" represents the parameters :math:`k_{af}^\text{var}` of
the corresponding transmission :math:`f` and arc :math:`a` combinations.