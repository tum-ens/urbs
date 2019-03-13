.. module:: urbs

Technical Parameters
^^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Technical Model Parameters*
    
    +---------------------------------------------+----+--------------------------------------------+
    |Parameter                                    |Unit|Description                                 |
    +=============================================+====+============================================+
    |**General Technical Parameters**                                                               |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`w`                                    | _  |Fraction of 1 year of modeled timesteps     |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\Delta t`                             | h  |Timestep Size                               |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`W`                                    | a  |Weight of last support timeframe            |
    +---------------------------------------------+----+--------------------------------------------+
    |**Commodity Technical Parameters**                                                             |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`d_{yvct}`                             |MWh |Demand for Commodity                        |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`s_{yvct}`                             | _  |Intermittent Supply Capacity Factor         |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{l}_{yvc}`                   |MW  |Maximum Stock Supply Limit Per Hour         |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{L}_{yvc}`                   |MWh |Maximum Annual Stock Supply Limit Per Vertex|
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{m}_{yvc}`                   |t/h |Maximum Environmental Output Per Hour       |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{M}_{yvc}`                   | t  |Maximum Annual Environmental Output         |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{g}_{yvc}`                   |MW  |Maximum Sell Limit Per Hour                 |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{G}_{yvc}`                   |MWh |Maximum Annual Sell Limit                   |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{b}_{yvc}`                   |MW  |Maximum Buy Limit Per Hour                  |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{B}_{yvc}`                   |MWh |Maximum Annual Buy Limit                    |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{L}_{\text{CO}_2,y}`         | t  |Maximum Global Annual CO2 Emission Limit    |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{\overline{L}}_{\text{CO}_2}`| t  |CO2 Emission Budget for modeling horizon    |
    +---------------------------------------------+----+--------------------------------------------+
    |**Process Technical Parameters**                                                               |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\underline{K}_{yvp}`                  |MW  |Process Capacity Lower Bound                |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`K_{vp}`                               |MW  |Process Capacity Installed                  |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{K}_{yvp}`                   |MW  |Process Capacity Upper Bound                |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`T_{vp}`                               |MW  |Remaining lifetime of installed processes   |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{PG}_{yvp}`                  |1/h |Process Maximal Power Gradient (relative)   |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\underline{P}_{yvp}`                  | _  |Process Minimum Part Load Fraction          |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`f_{yvpt}^\text{out}`                  | _  |Process Output Ratio multiplyer             |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`r_{ypc}^\text{in}`                    | _  |Process Input Ratio                         |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\underline{r}_{ypc}^\text{in}`        | _  |Process Partial Input Ratio                 |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\underline{r}_{ypc}^\text{out}`       | _  |Process Partial Output Ratio                |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`r_{ypc}^\text{out}`                   | _  |Process Output Ratio                        |
    +---------------------------------------------+----+--------------------------------------------+
    |**Storage Technical Parameters**                                                               |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`I_{yvs}`                              | _  |Initial and Final State of Charge           |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`e_{yvs}^\text{in}`                    | _  |Storage Efficiency During Charge            |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`e_{yvs}^\text{out}`                   | _  |Storage Efficiency During Discharge         |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`d_{yvs}`                              |1/h |Storage Self-discharge Per Hour             |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\underline{K}_{yvs}^\text{c}`         |MWh |Storage Capacity Lower Bound                |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`K_{yvs}^\text{c}`                     |MWh |Storage Capacity Installed                  |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{K}_{yvs}^\text{c}`          |MWh |Storage Capacity Upper Bound                |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\underline{K}_{yvs}^\text{p}`         |MW  |Storage Power Lower Bound                   |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`K_{yvs}^\text{p}`                     |MW  |Storage Power Installed                     |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{K}_{yvs}^\text{p}`          |MW  |Storage Power Upper Bound                   |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`T_{vs}`                               |MW  |Remaining lifetime of installed storages    |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`k_{yvs}^\text{E/P}`                   |h   |Storage Energy to Power Ratio               |    
    +---------------------------------------------+----+--------------------------------------------+
    |**Transmission Technical Parameters**                                                          |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`e_{yaf}`                              | _  |Transmission Efficiency                     |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\underline{K}_{yaf}`                  |MW  |Tranmission Capacity Lower Bound            |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`K_{yaf}`                              |MW  |Tranmission Capacity Installed              |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{K}_{yaf}`                   |MW  |Tranmission Capacity Upper Bound            |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`T_{af}`                               |MW  |Remaining lifetime of installed transmission|
    +---------------------------------------------+----+--------------------------------------------+
    |**Demand Side Management Parameters**                                                          |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`e_{yvc}`                              | _  |DSM Efficiency                              |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`y_{yvc}`                              | _  |DSM Delay Time                              |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`o_{yvc}`                              | _  |DSM Recovery Time                           |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{K}_{yvc}^\text{up}`         |MW  |DSM Maximal Upshift Per Hour                |
    +---------------------------------------------+----+--------------------------------------------+
    |:math:`\overline{K}_{yvc}^\text{down}`       |MW  |DSM Maximal Downshift Per Hour              |
    +---------------------------------------------+----+--------------------------------------------+

General Technical Parameters
----------------------------
**Weight**, :math:`w`, ``weight``: The parameter :math:`w` helps to scale
variable costs and emissions from the length of simulation, that the energy
system model is being observed, to an annual result. This parameter represents
the fraction of a year (8760 hours) of the observed time span. The observed
time span is calculated by the product of number of time steps of the set
:math:`T` and the time step duration. In script ``model.py`` this parameter is
defined by the model parameter ``weight`` and initialized by the following code
fragment:
::

    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.tm) * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')
		

**Timestep Duration**, :math:`\Delta t`, ``dt``: The parameter :math:`\Delta t`
represents the duration between two sequential timesteps :math:`t_x` and
:math:`t_{x+1}`. This is calculated by the subtraction of smaller one from the
bigger of the two sequential timesteps :math:`\Delta t = t_{x+1} - t_x`. This
parameter is the unit of time for the optimization model, is expressed in the
unit h and by default the value is set to ``1``. In script ``model.py`` this
parameter is defined by the model paramter ``dt`` and initialized by the
following code fragment:
::

    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')

The user can set the paramteter in script ``runme.py`` in the line:
::

    dt = 1  # length of each time step (unit: hours)

**Weight of last modeled support timeframe**, :math:`W`,
``m.global_prop.loc[(min(m.stf), 'Cost budget'), 'value']``: This parameter
specifies how long the time intervall represented by the last support timeframe
is. The unit of this paramter is years. By extension it also specifies the end
of the modeling horizon. The paramter is set in the spreadsheet corresponding
to the last support timeframe in worksheet "Global" in the line denoted
"Weight" in the column titled "value".  

Commodity Technical Parameters
------------------------------

**Demand for Commodity**, :math:`d_{yvct}`,
``m.demand_dict[(stf, sit, com)][tm]``: The parameter represents the energy
amount of a demand commodity tuple :math:`c_{yvq}` required at a timestep
:math:`t`
(:math:`\forall y \in Y, \forall v \in V, q = "Demand", \forall t \in T_m`).
The unit of this parameter is MWh. This data is to be provided by the user and
to be entered in the spreadsheet corresponding to the specified support
timeframe. The related section for this parameter in the spreadsheet can be
found in the "Demand" sheet. Here each row represents another timestep
:math:`t` and each column represent a commodity tuple :math:`c_{yvq}`. Rows are
named after the timestep number :math:`n` of timesteps :math:`t_n`. Columns are
named after the combination of site name :math:`v` and commodity name :math:`c`
respecting the order and seperated by a period(.). For example (Mid, Elec)
represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted
in column declarations, because every commodity of this parameter has to be
from commodity type `Demand` in any case.

**Intermittent Supply Capacity Factor**, :math:`s_{yvct}`,
``m.supim_dict[(stf, sit, coin)][tm]``: The parameter :math:`s_{yvct}`
represents the normalized availability of a supply intermittent commodity
:math:`c` :math:`(\forall c \in C_\text{sup})` in a support timeframe :math:`y` 
and site :math:`v` at a timestep :math:`t`. In other words this parameter gives
the ratio of current available energy amount to maximum potential energy amount
of a supply intermittent commodity. This data is to be provided by the user and
to be entered in the spreadsheet corresponding to the support timeframe. The
related section for this parameter in the spreadsheet can be found under the
"SupIm" sheet. Here each row represents another timestep :math:`t` and each
column represent a commodity tuple :math:`c_{vq}`. Rows are named after the
timestep number :math:`n` of timesteps :math:`t_n`. Columns are named after the
combination of site name :math:`v` and commodity name :math:`c`, in this
respective order and seperated by a period(.). For example (Mid.Elec)
represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted
in column declarations, because every commodity of this parameter has to be
from commodity type `SupIm` in any case.

**Maximum Stock Supply Limit Per Hour**, :math:`\overline{l}_{yvc}`,
``m.commodity_dict['maxperhour'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{l}_{yvc}` represents the maximum energy amount of a stock
commodity tuple :math:`c_{yvq}`
(:math:`\forall y\in Y, \forall v \in V , q = "Stock"`) that energy model is
allowed to use per hour. The unit of this parameter is MW. This parameter
applies to every timestep and does not vary for each timestep :math:`t`. This
parameter is to be provided by the user and to be entered in spreadsheet
corresponding to the support timeframe. The related section for this parameter
in the spreadsheet can be found under the ``Commodity`` sheet. Here each row
represents another commodity tuple :math:`c_{yvq}` and the column with the
header label "maxperhour" represents the parameter :math:`\overline{l}_{yvc}`.
If there is no desired restriction of a stock commodity tuple usage per
timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Stock Supply Limit Per Vertex**, :math:`\overline{L}_{yvc}`,
``m.commodity_dict['max'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{L}_{yvc}` represents the maximum energy amount of a stock
commodity tuple :math:`c_{yvq}`
(:math:`\forall y\in Y, \forall v \in V , q = "Stock"`) that energy model is
allowed to use annually. The unit of this parameter is MWh. This parameter is
to be provided by the user and to be entered in spreadsheet corresponding to
the support timeframe. The related section for this parameter in the
spreadsheet can be found under the ``Commodity`` sheet. Here each row
represents another commodity tuple :math:`c_{yvq}` and the column with the
header label "max" represents the parameter :math:`\overline{L}_{yvc}`. If
there is no desired restriction of a stock commodity tuple usage per timestep,
the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Environmental Output Per Hour**, :math:`\overline{m}_{yvc}`,
``m.commodity_dict['maxperhour'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{m}_{yvc}` represents the maximum energy amount of an
environmental commodity tuple :math:`c_{yvq}`
(:math:`\forall y\in Y, \forall v \in V , q = "Env"`) that energy model is
allowed to produce and release to environment per time step. This parameter
applies to every timestep and does not vary for each timestep :math:`t/h`. This
parameter is to be provided by the user and to be entered in spreadsheet
corresponding to the support timeframe. The related section for this parameter
in the spreadsheet can be found under the ``Commodity`` sheet. Here each row
represents another commodity tuple :math:`c_{yvq}` and the column with the
header label "maxperhour" represents the parameter :math:`\overline{m}_{yvc}`.
If there is no desired restriction of an enviromental commodity tuple usage per
timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Environmental Output**, :math:`\overline{M}_{yvc}`,
``m.commodity_dict['max'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{M}_{vc}` represents the maximum energy amount of an
environmental commodity tuple :math:`c_{yvq}`
(:math:`\forall y\in Y, \forall v \in V , q = "Env"`) that energy model is
allowed to produce and release to environment annually. This parameter is to be
provided by the user and to be entered in spreadsheet corresponding to the
support timeframe. The related section for this parameter in the spreadsheet
can be found under the ``Commodity`` sheet. Here each row represents another
commodity tuple :math:`c_{yvq}` and the column with the header label "max"
represents the parameter :math:`\overline{M}_{yvc}`. If there is no desired
restriction of a stock commodity tuple usage per timestep, the corresponding
cell can be set to "inf" to ignore this parameter.

**Maximum Sell Limit Per Hour**, :math:`\overline{g}_{yvc}`,
``m.commodity_dict['maxperhour'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{g}_{yvc}` represents the maximum energy amount of a sell
commodity tuple :math:`c_{yvq}`
(:math:`\forall y\in Y, \forall v \in V , q = "Sell"`) that energy model is
allowed to sell per hour. The unit of this parameter is MW. This parameter
applies to every timestep and does not vary for each timestep :math:`t`. This
parameter is to be provided by the user and to be entered in spreadsheet. The
related section for this parameter in the spreadsheet corresponding to the
support timeframe can be found under the ``Commodity`` sheet. Here each row
represents another commodity tuple :math:`c_{yvq}` and the column with the
header label "maxperhour" represents the parameter :math:`\overline{g}_{yvc}`.
If there is no desired restriction of a sell commodity tuple usage per
timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Sell Limit**, :math:`\overline{G}_{yvc}`,
``m.commodity_dict['max'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{G}_{yvc}` represents the maximum energy amount of a sell
commodity tuple :math:`c_{yvq}`
(:math:`\forall y\in Y, \forall v \in V , q = "Sell"`) that energy model is
allowed to sell annually. The unit of this parameter is MWh. This parameter is
to be provided by the user and to be entered in spreadsheet corresponding to
the support timeframe. The related section for this parameter in the
spreadsheet can be found under the ``Commodity`` sheet. Here each row
represents another commodity tuple :math:`c_{yvq}` and the column of sell with
the header label "max" represents the parameter :math:`\overline{G}_{yvc}`. If
there is no desired restriction of a sell commodity tuple usage per timestep,
the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Buy Limit Per Hour**, :math:`\overline{b}_{yvc}`,
``m.commodity_dict['maxperhour'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{b}_{yvc}` represents the maximum energy amount of a buy
commodity tuple :math:`c_{yvq}`
(:math:`\foral y\in Y, \forall v \in V , q = "Buy"`) that energy model is
allowed to buy per hour. The unit of this parameter is MW. This parameter
applies to every timestep and does not vary for each timestep :math:`t`. This
parameter is to be provided by the user and to be entered in spreadsheet
corresponding to the support timeframe. The related section for this parameter
in the spreadsheet can be found under the ``Commodity`` sheet. Here each row
represents another commodity tuple :math:`c_{yvq}` and the column with the
header label "maxperhour" represents the parameter :math:`\overline{b}_{yvc}`.
If there is no desired restriction of a sell commodity tuple usage per
timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Buy Limit**, :math:`\overline{B}_{yvc}`,
``m.commodity_dict['max'][(stf, sit, com, com_type)]``: The parameter
:math:`\overline{B}_{yvc}` represents the maximum energy amount of a buy
commodity tuple :math:`c_{yvq}`
(:math:`\forall y\in Y, \forall v \in V , q = "Buy"`) that energy model is
allowed to buy annually. The unit of this parameter is MWh. This parameter is
to be provided by the user and to be entered in spreadsheet corresponding to
the support timeframe. The related section for this parameter in the
spreadsheet can be found under the ``Commodity`` sheet. Here each row
represents another commodity tuple :math:`c_{yvq}` and the column with the
header label "max" represents the parameter :math:`\overline{B}_{yvc}`. If
there is no desired restriction of a buy commodity tuple usage per timestep,
the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Global Annual CO**:math:`_\textbf{2}` **Annual Emission Limit**,
:math:`\overline{L}_{CO_2,y}`,
``m.global_prop.loc[stf, 'CO2 limit']['value']``: The parameter
:math:`\overline{L}_{CO_2,y}` represents the maximum total amount of CO2 the
energy model is allowed to produce and release to the environment annually. If
the user desires to set a maximum annual limit to total :math:`CO_2` emission
across all sites of the energy model in a given support timeframe :math:`y`,
this can be done by entering the desired value to the spreadsheet corresponding
to the support timeframe. The related section for this parameter can be found
under the sheet "Global". Here the the cell where the "CO2 limit" row and
"value" column intersects stands for the parameter
:math:`\overline{L}_{CO_2,y}`. If the user wants to disable this parameter and
restriction it provides, this cell can be set to "inf" or simply be deleted.

**CO**:math:`_\textbf{2}`** emission budget **Total Emission budget**,
:math:`\overline{\overline{L}}_{CO_2}`,
``m.global_prop.loc[min(m.stf), 'CO2 budget']['value']``: The parameter
:math:`\overline{\overline{L}}_{CO_2}` represents the maximum total amount of
CO2 the energy model is allowed to produce and release to the environment
over the entire modeling horizon. If the user desires to set a limit to total
:math:`CO_2` emission across all sites and the entire modeling horizon of the
energy model, this can be done by entering the desired value to the spreadsheet
of the first support timeframe. The related section for this parameter can be
found under the sheet "Global". Here the the cell where the "CO2 budget" row
and "value" column intersects stands for the parameter
:math:`\overline{\overline{L}}_{CO_2}`. If the user wants to disable this
parameter and restriction it provides, this cell can be set to "inf" or simply
be deleted. 

Process Technical Parameters
----------------------------

**Process Capacity Lower Bound**, :math:`\underline{K}_{yvp}`,
``m.process_dict['cap-lo'][stf, sit, pro]``: The parameter
:math:`\underline{K}_{yvp}` represents the minimum amount of power output
capacity of a process :math:`p` at a site :math:`v` in support timeframe
:math:`y`, that energy model is required to have. The unit of this parameter is
MW. The related section for this parameter in the spreadsheet corresponding to
the support timeframe can be found under the "Process" sheet. Here each row
represents another process :math:`p` in a site :math:`v` and the column with
the header label "cap-lo" represents the parameters :math:`\underline{K}_{yvp}`
belonging to the corresponding process :math:`p` and site :math:`v`
combinations. If there is no desired minimum limit for the process capacities,
this parameter can be simply set to "0". 

**Process Capacity Installed**, :math:`K_{vp}`,
``m.process_dict['inst-cap'][min(m.stf), sit, pro]``: The parameter
:math:`K_{vp}` represents the amount of power output capacity of a process
:math:`p` in a site :math:`v`, that is already installed to the energy system
at the beginning of the modeling period. The unit of this parameter is MW. The
related section for this parameter can be found in the spreadsheet
corresponding to the first support timeframe under the "Process" sheet. Here
each row represents another process :math:`p` in a site :math:`v` and the
column with the header label "inst-cap" represents the parameters
:math:`K_{vp}` belonging to the corresponding process :math:`p` and site
:math:`v` combinations.

**Process Capacity Upper Bound**, :math:`\overline{K}_{yvp}`,
``m.process_dict['cap-up'][stf, sit, pro]``: The parameter
:math:`\overline{K}_{yvp}` represents the maximum amount of power output
capacity of a process :math:`p` at a site :math:`v` in support timeframe
:math:`y`, that energy model is allowed to have. The unit of this parameter is
MW. The related section for this parameter in the spreadsheet corresponding to
the support timeframe can be found under the "Process" sheet. Here each row
represents another process :math:`p` in a site :math:`v` and the column with
the header label "cap-up" represents the parameters :math:`\overline{K}_{yvp}`
of the corresponding process :math:`p` and site :math:`v` combinations.
Alternatively, :math:`\overline{K}_{yvp}` is determined by the column with the
label "area-per-cap", whenever the value in "cap-up" times the value
"area-per-cap" is larger than the value in column "area" in sheet "Site" for
site :math:`v` in support timeframe :math:`y`. If there is no desired maximum
limit for the process capacities, both input parameters can be simply set to
"inf".

**Remaining lifetime of installed processes**, :math:`T_{vp}`,
``m.process.loc[(min(m.stf), sit, pro), 'lifetime']``: The parameter
:math:`T_{vp}` represents the remaining lifetime of already installed units. It
is used to determine the set `m.inst_pro_tuples`, i.e. to identify for which
support timeframes the installed unit can still be used.

**Process Maximal Gradient**, :math:`\overline{PG}_{yvp}`,
``m.process_dict['max-grad'][(stf, sit, pro)]``: The parameter
:math:`\overline{PG}_{yvp}` represents the maximal power gradient of a process
:math:`p` at a site :math:`v` in support timeframe :math:`y`, that energy model
is allowed to have. The unit of this parameter is 1/h. The related section for
this parameter in the spreadsheet can be found under the "Process" sheet. Here
each row represents another process :math:`p` in a site :math:`v` and the
column with the header label "max-grad" represents the parameters
:math:`\overline{PG}_{yvp}` of the corresponding process :math:`p` and site
:math:`v` combinations. If there is no desired maximum limit for the process
power gradient, this parameter can be simply set to a value larger or equal to
1.

**Process Minimum Part Load Fraction**, :math:`\underline{P}_{yvp}`,
``m.process_dict['min-fraction'][(stf, sit, pro)]``: The parameter
:math:`\underline{P}_{yvp}` represents the minimum allowable part load of a
process :math:`p` at a site :math:`v` in support timeframe :math:`y` as a
fraction of the total process capacity. The related section for this parameter
in the spreadsheet can be found under the "Process" sheet. Here each row
represents another process :math:`p` in a site :math:`v` and the column with
the header label "min-fraction" represents the parameters
:math:`\underline{P}_{yvp}` of the corresponding process :math:`p` and site
:math:`v` combinations. The minimum part load fraction parameter constraints is
only relevant when the part load behavior for the process is active, i.e., when
in the process commoditiy sheet a value for "ratio-min" is set for at least one
input commodity.  

**Process Output Ratio multiplyer**, :math:`f_{yvpt}^\text{out}`,
``m.eff_factor_dict[(stf, sit, pro)]``: The parameter time series
:math:`f_{yvpt}^\text{out}` allows for a time dependent modification of process
outputs and by extension of the efficiency of a process :math:`p` in site
:math:`v` and support timeframe :math:`y`. It can be used, e.g., to
model temperature dependent efficiencies of processes or to include scheduled
maintenance intervals. In the spreadsheet corresponding to the support
timeframe this timeseries is set in worksheet "TimeVarEff". Here each row
represents another timestep :math:`t` and each column represent a process tuple
:math:`p_{yv}`. Rows are named after the timestep number :math:`n` of timesteps
:math:`t_n`. Columns are named after the combination of site name :math:`v` and
commodity name and process name :math:`p` respecting the order and seperated by
a period(.). For example (Mid, Lignite plant) represents the process Lignite
plant in site Mid. Note that the output of environmental commodity outputs are
not manipulated by this factor as it is typially linked to an input commodity
as , e.g., CO2 output is linked to a fossil input.

**Process Input Ratio**, :math:`r_{ypc}^\text{in}`,
``m.r_in_dict[(stf, pro, co)]``: The parameter :math:`r_{ypc}^\text{in}`
represents the ratio of the input amount of a commodity :math:`c` in a process
:math:`p` and support timeframe :math:`y`, relative to the process throughput
at a given timestep. The related section for this parameter in the spreadsheet
corresponding to the support timeframe can be found under the
"Process-Comodity" sheet. Here each row represents another commodity :math:`c`
that either goes in to or comes out of a process :math:`p`. The column with the
header label "ratio" represents the parameters :math:`r_{ypc}^\text{in}` of
the corresponding process :math:`p` and commodity :math:`c` if the latter is an
input commodity.

**Process Partial Input Ratio**, :math:`\underline{r}_{ypc}^\text{in}`,
``m.r_in_min_fraction[stf, pro, coin]``: The parameter
:math:`\underline{r}_{ypc}^\text{in}` represents the ratio of the amount of
input commodity :math:`c` a process :math:`p` and support timeframe :math:`y`
consumes if it is at its minimum allowable partial operation. More precisely,
when its throughput :math:`\tau_{yvpt}` has the minimum value
:math:`\kappa_{yvp} \underline{P}_{yvp}`. The related section for this
parameter in the spreadsheet corresponding to the support timeframe can be
found under the "Process-Comodity" sheet. Here each row represents another
commodity :math:`c` that either goes in to or comes out of a process :math:`p`.
The column with the header label "ratio-min" represents the parameters
:math:`\underline{r}_{ypc}^\text{in,out}` of the corresponding process
:math:`p` and commodity :math:`c` if the latter is an input commodity.

**Process Output Ratio**, :math:`r_{ypc}^\text{out}`,
``m.r_out_dict[(stf, pro, co)]``: The parameter :math:`r_{ypc}^\text{out}`
represents the ratio of the output amount of a commodity :math:`c` in a process
:math:`p` in support timeframe :math:`y`, relative to the process throughput at
a given timestep.  The related section for this parameter in the spreadsheet
corresponding to the support timeframe can be found under the
"Process-Commodity" sheet. Here each row represents another commodity :math:`c`
that either goes in to or comes out of a process :math:`p`. The column with the
header label "ratio" represents the parameters of the corresponding process
:math:`p` and commodity :math:`c` if the latter is an output commodity.

**Process Partial Output Ratio**, :math:`\underline{r}_{ypc}^\text{out}`,
``m.r_out_min_fraction[stf, pro, coo]``: The parameter
:math:`\underline{r}_{ypc}^\text{out}` represents the ratio of the amount of
output commodity :math:`c` a process :math:`p` and support timeframe :math:`y`
emits if it is at its minimum allowable partial operation. More precisely, when
its throughput :math:`\tau_{yvpt}` has the minimum value
:math:`\kappa_{yvp} \underline{P}_{yvp}`. The related section for this
parameter in the spreadsheet corresponding to the support timeframe can be
found under the "Process-Comodity" sheet. Here each row represents another
commodity :math:`c` that either goes in to or comes out of a process :math:`p`.
The column with the header label "ratio-min" represents the parameters
:math:`\underline{r}_{ypc}^\text{in,out}` of the corresponding process
:math:`p` and commodity :math:`c` if the latter is an output commodity.

Process input and output ratios are, in general, used for unit conversion
between the different commodities.

Since all costs and capacity constraints take the process throughput
:math:`\tau_{yvpt}` as the reference, it is reasonable to assign an in- or
output ratio of "1" to at least one commodity. The flow of this commodity then
tracks the throughput and can be used as a reference. All other values of in-
and output ratios can then be adjusted by scaling them by an appropriate factor
to the reference commodity flow. 

Storage Technical Parameters
----------------------------

**Initial and Final State of Charge (relative)**, :math:`I_{yvs}`,
``m.storage_dict['init'][(stf, sit, sto, com)]``: The parameter :math:`I_{yvs}`
represents the initial state of charge of a storage :math:`s` in a site
:math:`v` and support timeframe :math:`y`. If this value is left unspecified,
the initial state of charge is variable. The initial and final value are set as
identical in each modeled support timeframe to avoid windfall profits through
emptying of a storage. The value of this parameter is expressed as a normalized
percentage, where "1" represents a fully loaded storage and "0" represents an
empty storage. The related section for this parameter in the spreadsheet
corrsponding to the support timeframe can be found under the "Storage" sheet.
Here each row represents a storage technology :math:`s` in a site :math:`v`
that stores a commodity :math:`c`. The column with the header label "init"
represents the parameters for corresponding storage :math:`s`, site :math:`v`,
commodity :math:`c` combinations. When no initial value is to be set this cell
can be left empty.

**Storage Efficiency During Charge**, :math:`e_{yvs}^\text{in}`,
``m.storage_dict['eff-in'][(stf, sit, sto, com)]``: The parameter
:math:`e_{yvs}^\text{in}` represents the charging efficiency of a storage
:math:`s` in a site :math:`v` and support timeframe :math:`y` that stores a
commodity :math:`c`. The charging efficiency shows, how much of a desired
energy and accordingly power can be succesfully stored into a storage. The
value of this parameter is expressed as a normalized percentage, where "1"
represents a charging without energy losses. The related section for this
parameter in the spreadsheet corresponding to the support timeframe can be
found under the "Storage" sheet. Here each row represents a storage technology
:math:`s` in a site :math:`v` that stores a commodity :math:`c`. The column
with the header label "eff-in" represents the parameters
:math:`e_{yvs}^\text{in}` for corresponding storage tuples.

**Storage Efficiency During discharge**, :math:`e_{yvs}^\text{out}`,
``m.storage_dict['eff-out'][(stf, sit, sto, com)]``: The parameter
:math:`e_{yvs}^\text{out}` represents the discharging efficiency of a storage
:math:`s` in a site :math:`v` and support timeframe :math:`y` that stores a
commodity :math:`c`. The discharging efficiency shows, how much of a desired
energy and accordingly power can be succesfully released from a storage. The
value of this parameter is expressed as a normalized percentage, where "1"
represents a discharging without energy losses. The related section for this
parameter in the spreadsheet corresponding to the support timeframe can be
found under the "Storage" sheet. Here each row represents a storage technology
:math:`s` in a site :math:`v` that stores a commodity :math:`c`. The column
with the header label "eff-out" represents the parameters
:math:`e_{yvs}^\text{out}` for corresponding storage tuples.

**Storage Self-discharge Per Hour**, :math:`d_{yvs}`,
``m.storage_dict['discharge'][(stf, sit, sto, com)]``: The parameter
:math:`d_{vs}` represents the fraction of the energy content within a storage
which is lost due to self-discharge per hour. It introduces an exponential
decay of a given storage state if no charging/discharging takes place. The unit
of this parameter is 1/h. The related section for this parameter in the
spreadsheet corresponding to the support timeframe can be found under the
"Storage" sheet. Here each row represents a storage technology :math:`s` in a
site :math:`v` that stores a commodity :math:`c`. The column with the header
label "discharge" represents the parameters :math:`d_{yvs}` for corresponding
storage tuples.

**Storage Capacity Lower Bound**, :math:`\underline{K}_{yvs}^\text{c}`,
``m.storage_dict['cap-lo-c'][(stf, sit, sto, com)]``: The parameter
:math:`\underline{K}_{yvs}^\text{c}` represents the minimum amount of energy
content capacity required for a storage :math:`s` storing a commodity :math:`c`
in a site :math:`v` in support timeframe :math:`y`. The unit of this parameter
is MWh. The related section for this parameter in the spreadsheet can be found
under the "Storage" sheet. Here each row represents a storage technology
:math:`s` in a site :math:`v` that stores a commodity :math:`c`. The column
with the header label "cap-lo-c" represents the parameters
:math:`\underline{K}_{yvs}^\text{c}` for corresponding storage tuples. If there
is no desired minimum limit for the storage energy content capacities, this
parameter can be simply set to "0". 

**Storage Capacity Installed**, :math:`K_{vs}^\text{c}`,
``m.storage_dict['inst-cap-c'][(min(m.stf), sit, sto, com)]]``: The parameter
:math:`K_{vs}^\text{c}` represents the amount of energy content capacity of a
storage :math:`s` storing commodity :math:`c` in a site :math:`v` and support
timeframe :math:`y`, that is already installed to the energy system at the
beginning of the model horizon. The unit of this parameter is MWh. The related
section for this parameter in the spreadsheet corresponding to the first
support timeframe can be found under the "Storage" sheet. Here each row
represents a storage technology :math:`s` in a site :math:`v` that stores a
commodity :math:`c`. The column with the header label "inst-cap-c" represents
the parameters :math:`K_{vs}^\text{c}` for corresponding storage tuples.

**Storage Capacity Upper Bound**, :math:`\overline{K}_{yvs}^\text{c}`,
``m.storage_dict['cap-up-c'][(stf, sit, sto, com)]``: The parameter
:math:`\overline{K}_{yvs}^\text{c}` represents the maximum amount of energy
content capacity allowed of a storage :math:`s` storing a commodity :math:`c`
in a site :math:`v` in support timeframe :math:`y`. The unit of this parameter
is MWh. The related section for this parameter in the spreadsheet corresponding
to the support timeframe can be found under the "Storage" sheet. Here each row
represents a storage technology :math:`s` in a site :math:`v` that stores a
commodity :math:`c`. The column with the header label "cap-up-c" represents the
parameters :math:`\overline{K}_{yvs}^\text{c}` for corresponding storage
tuples. If there is no desired maximum limit for the storage energy content
capacitites, this parameter can be simply set to ""inf"".

**Storage Power Lower Bound**, :math:`\underline{K}_{yvs}^\text{p}`,
``m.storage_dict['cap-lo-p'][(stf, sit, sto, com)]``: The parameter
:math:`\underline{K}_{yvs}^\text{p}` represents the minimum amount of
charging/discharging power required for a storage :math:`s` storing a commodity
:math:`c` in a site :math:`v` in support timeframe :math:`y`. The unit of this
parameter is MW. The related section for this parameter in the spreadsheet can
be found under the "Storage" sheet. Here each row represents a storage
technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The
column with the header label "cap-lo-p" represents the parameters
:math:`\underline{K}_{yvs}^\text{p}` for corresponding storage tuples. If there
is no desired minimum limit for the storage charging/discharging powers, this
parameter can be simply set to "0". 

**Storage Power Installed**, :math:`K_{vs}^\text{p}`,
``m.storage_dict['inst-cap-p'][(min(m.stf), sit, sto, com)]]``: The parameter
:math:`K_{vs}^\text{p}` represents the amount of charging/discharging power of
a storage :math:`s` storing commodity :math:`c` in a site :math:`v` and support
timeframe :math:`y`, that is already installed to the energy system at the
beginning of the model horizon. The unit of this parameter is MW. The related
section for this parameter in the spreadsheet corresponding to the first
support timeframe can be found under the "Storage" sheet. Here each row
represents a storage technology :math:`s` in a site :math:`v` that stores a
commodity :math:`c`. The column with the header label "inst-cap-p" represents
the parameters :math:`K_{vs}^\text{p}` for corresponding storage tuples.

**Storage Power Upper Bound**, :math:`\overline{K}_{yvs}^\text{p}`,
``m.storage_dict['cap-up-p'][(stf, sit, sto, com)]``: The parameter
:math:`\overline{K}_{yvs}^\text{c}` represents the maximum amount of
charging/discharging power allowed of a storage :math:`s` storing a commodity
:math:`c` in a site :math:`v` in support timeframe :math:`y`. The unit of this
parameter is MW. The related section for this parameter in the spreadsheet
corresponding to the support timeframe can be found under the "Storage" sheet.
Here each row represents a storage technology :math:`s` in a site :math:`v`
that stores a commodity :math:`c`. The column with the header label "cap-up-p"
represents the parameters :math:`\overline{K}_{yvs}^\text{p}` for corresponding
storage tuples. If there is no desired maximum limit for the storage energy
content capacitites, this parameter can be simply set to ""inf"".

**Remaining lifetime of installed storages**, :math:`T_{vs}`,
``m.storage.loc[(min(m.stf), sit, pro), 'lifetime']``: The parameter
:math:`T_{vs}` represents the remaining lifetime of already installed units. It
is used to determine the set `m.inst_sto_tuples`, i.e. to identify for which
support timeframes the installed units can still be used.

**Storage Energy to Power Ratio**, :math:`k_{yvs}^\text{E/P}`,
``m.storage_dict['ep-ratio'][(stf, sit, sto, com)]``: The parameter
:math:`k_{yvs}^\text{E/P}` represents the linear ratio between the energy and
power capacities of a storage :math:`s` storing a commodity :math:`c` in a site
:math:`v` in support timeframe :math:`y`. The unit of this parameter is hours.
The related section for this parameter in the spreadsheet corresponding to the
support timeframe can be found under the "Storage" sheet. Here each row
represents a storage technology :math:`s` in a site :math:`v` that stores a
commodity :math:`c`. The column with the header label "ep-ratio" represents the
parameters :math:`k_{yvs}^\text{E/P}` for corresponding storage tuples. If
there is no desired set ratio for the storage energy and power capacities
(which means the storage energy and power capacities can be sized independently
from each other), this cell can be left empty.

Transmission Technical Parameters
---------------------------------

**Transmission Efficiency**, :math:`e_{yaf}`,
``m.transmission_dict['eff'][(stf, sin, sout, tra, com)]``: The parameter
:math:`e_{yaf}` represents the energy efficiency of a transmission :math:`f`
that transfers a commodity :math:`c` through an arc :math:`a` in support
timeframe :math:`y`. Here an arc :math:`a` defines the connection line from an
origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`.
The ratio of the output energy amount to input energy amount, gives the energy
efficiency of a transmission process. The related section for this parameter in
the spreadsheet corresponding to the support timeframe can be found under the
"Transmission" sheet. Here each row represents another combination of
transmission :math:`f` and arc :math:`a`. The column with the header label
"eff" represents the parameters :math:`e_{yaf}` of the corresponding
transmission tuples.

**Transmission Capacity Lower Bound**, :math:`\underline{K}_{yaf}`,
``m.transmission_dict['cap-lo'][(stf, sin, sout, tra, com)]``: The parameter
:math:`\underline{K}_{<af}` represents the minimum power output capacity of a
transmission :math:`f` transferring a commodity :math:`c` through an arc
:math:`a`, that the energy system model is required to have. Here an arc
:math:`a` defines the connection line from an origin site :math:`v_\text{out}`
to a destination site :math:`{v_\text{in}}`. The unit of this parameter is MW.
The related section for this parameter in the spreadsheet corresponding to the
support timeframe can be found under the "Transmission" sheet. Here each row
represents another transmission :math:`f`, arc :math:`a` combination. The
column with the header label "cap-lo" represents the parameters
:math:`\underline{K}_{yaf}` of the corresponding transmission tuples. 

**Transmission Capacity Installed**, :math:`K_{af}`,
``m.transmission_dict['inst-cap'][(min(m.stf), sin, sout, tra, com)]``: The
parameter :math:`K_{af}` represents the amount of power output capacity of a
transmission :math:`f` transferring a commodity :math:`c` through an arc
:math:`a`, that is already installed to the energy system at the beginning of
the modeling horizon. The unit of this parameter is MW. The related section for
this parameter in the spreadsheet corresponding to the first support timeframe
can be found under the "Transmission" sheet. Here each row represents another
transmission :math:`f`, arc :math:`a` combination. The column with the header
label "inst-cap" represents the parameters :math:`K_{af}` of the transmission
tuples.

**Transmission Capacity Upper Bound**, :math:`\overline{K}_{yaf}`,
``m.transmission_dict['cap-up'][(stf, sin, sout, tra, com)]``: The parameter
:math:`\overline{K}_{yaf}` represents the maximum power output capacity of a
transmission :math:`f` transferring a commodity :math:`c` through an arc
:math:`a` in support timeframe :math:`y`, that the energy system model is
allowed to have. Here an arc :math:`a` defines the connection line from an
origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`.
The unit of this parameter is MW. The related section for this parameter in the
spreadsheet corresponding to the support timeframe can be found under the
"Transmission" sheet. Here each row represents another transmission :math:`f`,
arc :math:`a` combination. The column with the header label "cap-up" represents 
the parameters :math:`\overline{K}_{yaf}` of the corresponding transmission
tuples.

**Remaining lifetime of installed transmission**, :math:`T_{af}`,
``m.transmission.loc[(min(m.stf), sitin, sitout, tra, com), 'lifetime']``: The
parameter :math:`T_{af}` represents the remaining lifetime of already installed
units. It is used to determine the set `m.inst_tra_tuples`, i.e. to identify
for which support timeframes the installed units can still be used.

Demand Side Management Technical Parameters
-------------------------------------------
**DSM Efficiency**, :math:`e_{yvc}`, ``m.dsm_dict['eff'][(stf, sit, com)]``:
The parameter :math:`e_{yvc}` represents the efficiency of the DSM process,
i.e., the fraction of DSM upshift that is benefitting the system via the
corresponding DSM downshifts of demand commodity :math:`c` in site :math:`v`
and support timeframe :math:`y`. The parameter is given as a fraction with "1"
meaning a perfect recovery of the DSM upshift. The related section for this
parameter in the spreadsheet corresponding to the support timeframe can be
found under the "DSM" sheet. Here each row represents another DSM potential for
demand commodity :math:`c` in site :math:`v`. The column with the header label
"eff" represents the parameters :math:`e_{yvc}` of the corresponding DSM
tuples.

**DSM Delay Time**, :math:`y_{yvc}`, ``m.dsm_dict['delay'][(stf, sit, com)]``:
The delay time :math:`y_{yvc}` restricts how long the time difference between
an upshift and its corresponding downshifts may be for demand commodity
:math:`c` in site :math:`v` and support timeframe :math:`y`. The parameter is
given in h. The related section for this parameter in the spreadsheet
corresponding to the support timeframe can be found under the "DSM" sheet. Here
each row represents another DSM potential for demand commodity :math:`c` in
site :math:`v`. The column with the header label "delay" represents the
parameters :math:`y_{yvc}` of the corresponding DSM tuples.

**DSM Recovery Time**, :math:`o_{yvc}`,
``m.dsm_dict['recov'][(stf, sit, com)]``: The recovery time :math:`o_{yvc}`
prevents the DSM system to continously shift demand. During the recovery time,
all upshifts of demand commodity :math:`c` in site :math:`v` and support
timeframe :math:`y` may not exceed the product of the delay time and the
maximal upshift capacity. The paramter is given in h. The related section for
this parameter in the spreadsheet corresponding to the support timeframe can be
found under the "DSM" sheet. Here each row represents another DSM potential for
demand commodity :math:`c` in site :math:`v`. The column with the header label
"recov" represents the parameters :math:`o_{yvc}` of the corresponding DSM
tuples. If no limitation via this parameter is desired it has to be set to
values lower than the delay time :math:`y_{yvc}`.

**DSM Maximal Upshift Per Hour**, :math:`\overline{K}_{yvc}^\text{up}`, MW,
``m.dsm_dict['cap-max-up'][(stf, sit, com)]``: The DSM upshift capacity
:math:`\overline{K}_{yvc}^\text{up}` limits the total upshift per hour for a
DSM potential of demand commodity :math:`c` in site :math:`v` and support
timeframe :math:`y`. The parameter is given in MW. The related section for
this parameter in the spreadsheet corresponding to the support timeframe can be
found under the "DSM" sheet. Here each row represents another DSM potential for
demand commodity :math:`c` in site :math:`v`. The column with the header label
"cap-max-up" represents the parameters :math:`\overline{K}_{yvc}^\text{up}` of
the corresponding DSM tuples. 

**DSM Maximal Downshift Per Hour**, :math:`\overline{K}_{yvc}^\text{down}`, MW,
``m.dsm_dict['cap-max-do'][(stf, sit, com)]``: The DSM downshift capacity
:math:`\overline{K}_{yvc}^\text{up}` limits the total downshift per hour for a
DSM potential of demand commodity :math:`c` in site :math:`v` and support
timeframe :math:`y`. The parameter is given in MW. The related section for
this parameter in the spreadsheet corresponding to the support timeframe can be
found under the "DSM" sheet. Here each row represents another DSM potential for
demand commodity :math:`c` in site :math:`v`. The column with the header label
"cap-max-do" represents the parameters :math:`\overline{K}_{yvc}^\text{down}` of
the corresponding DSM tuples.
