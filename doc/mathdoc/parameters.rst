.. module:: urbs

Parameters
==========
All the parameters that the optimization model requires to calculate an optimal solution will be listed and defined in this section.
A parameter is a data, that is provided by the user before the optimization simulation starts. These parameters are the values that define the specifications of the modelled energy system. Parameters of this optimization model can be seperated into two main parts, these are Technical and Economical Parameters. 

Technical Parameters
^^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Technical Model Parameters*

	+-------------------------------------+----+--------------------------------------------+
	|Parameter                            |Unit|Description                                 |
	+=====================================+====+============================================+
	|**General Technical Parameters**                                                       |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`w`                            | _  |Weight                                      |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\Delta t`                     | h  |Timestep Duration                           |
	+-------------------------------------+----+--------------------------------------------+
	|**Commodity Technical Parameters**                                                     |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`d_{vct}`                      |MW  |Demand for Commodity                        |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`s_{vct}`                      | _  |Intermittent Supply Capacity Factor         |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{l}_{vc}`            |MW  |Maximum Stock Supply Limit Per Time Step    |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{L}_{vc}`            |MW  |Maximum Annual Stock Supply Limit Per Vertex|
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{m}_{vc}`            | t  |Maximum Environmental Output Per Time Step  |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{M}_{vc}`            | t  |Maximum Annual Environmental Output         |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{g}_{vc}`            |MW  |Maximum Sell Limit Per Time Step            |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{G}_{vc}`            |MW  |Maximum Annual Sell Limit                   |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{b}_{vc}`            |MW  |Maximum Buy Limit Per Time Step             |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{B}_{vc}`            |MW  |Maximum Annual Buy Limit                    |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{L}_{CO_2}`          | t  |Maximum Global Annual CO2 Emission Limit    |
	+-------------------------------------+----+--------------------------------------------+
	|**Process Technical Parameters**                                                       |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{vp}`           |MW  |Process Capacity Lower Bound                |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`K_{vp}`                       |MW  |Process Capacity Installed                  |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vp}`            |MW  |Process Capacity Upper Bound                |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{PG}_{vp}`           |1/h |Process Maximal Power Gradient (relative)   |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`r_{pc}^\text{in}`             | _  |Process Input Ratio                         |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`r_{pc}^\text{out}`            | _  |Process Output Ratio                        |
	+-------------------------------------+----+--------------------------------------------+
	|**Storage Technical Parameters**                                                       |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`I_{vs}`                       | 1  |Initial and Final State of Charge           |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`e_{vs}^\text{in}`             | _  |Storage Efficiency During Charge            |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`e_{vs}^\text{out}`            | _  |Storage Efficiency During Discharge         |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{vs}^\text{c}`  |MWh |Storage Content Lower Bound                 |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`K_{vs}^\text{c}`              |MWh |Storage Content Installed                   |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vs}^\text{c}`   |MWh |Storage Content Upper Bound                 |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{vs}^\text{p}`  |MW  |Storage Power Lower Bound                   |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`K_{vs}^\text{p}`              |MW  |Storage Power Installed                     |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vs}^\text{p}`   |MW  |Storage Power Upper Bound                   |
	+-------------------------------------+----+--------------------------------------------+
	|**Transmission Technical Parameters**                                                  |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`e_{af}`                       | _  |Transmission Efficiency                     |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{af}`           |MW  |Tranmission Capacity Lower Bound            |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`K_{af}`                       |MW  |Tranmission Capacity Installed              |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{af}`            |MW  |Tranmission Capacity Upper Bound            |
	+-------------------------------------+----+--------------------------------------------+
    |**Demand Side Management Parameters**                                                  |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`e_{vc}`                       | _  |DSM Efficiency                              |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`y_{vc}`                       | _  |DSM Delay Time                              |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`o_{vc}`                       | _  |DSM Recovery Time                           |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vc}^\text{up}`  |MW  |DSM Maximal Upshift Capacity                |
	+-------------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vc}^\text{down}`|MW  |DSM Maximal Downshift Capacity              |
	+-------------------------------------+----+--------------------------------------------+

General Technical Parameters
----------------------------
**Weight**, :math:`w`, ``weight``: The variable :math:`w` helps to scale variable costs and emissions from the length of simulation, that the energy system model is being observed, to an annual result. This variable represents the rate of a year (8760 hours) to the observed time span. The observed time span is calculated by the product of number of time steps of the set :math:`T` and the time step duration. In script ``urbs.py`` this variable is defined by the model variable ``weight`` and initialized by the following code fragment:
::

    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.tm) * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')
		

**Timestep Duration**, :math:`\Delta t`, ``dt``: The variable :math:`\Delta t` represents the duration between two sequential timesteps :math:`t_x` and :math:`t_{x+1}`. This is calculated by the subtraction of smaller one from the bigger of the two sequential timesteps :math:`\Delta t = t_{x+1} - t_x`. This variable is the unit of time for the optimization model This variable is expressed in the unit h and by default the value is set to ``1``. In script ``urbs.py`` this variable is defined by the model variable ``dt`` and initialized by the following code fragment:
::

    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')
		

Commodity Technical Parameters
------------------------------

**Demand for Commodity**, :math:`d_{vct}`, ``m.demand.loc[tm][sit,com]``: The parameter represents the energy amount of a demand commodity tuple :math:`c_{vq}` required at a timestep :math:`t` (:math:`\forall v \in V, q = "Demand", \forall t \in T_m`). The unit of this parameter is MW. This data is to be provided by the user and to be entered in the spreadsheet. The related section for this parameter in the spreadsheet can be found under the "Demand" sheet. Here each row represents another timestep :math:`t` and each column represent a commodity tuple :math:`c_{vq}`. Rows are named after the timestep number :math:`n` of timesteps :math:`t_n`. Columns are named after the combination of site name :math:`v` and commodity name :math:`c` respecting the order and seperated by a period(.). For example (Mid, Elec) represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted in column declarations, because every commodity of this parameter has to be from commodity type `Demand` in any case.

**Intermittent Supply Capacity Factor**, :math:`s_{vct}`, ``m.supim.loc[tm][sit,com]``: The parameter :math:`s_{vct}` represents the normalized availability of a supply intermittent commodity :math:`c` :math:`(\forall c \in C_\text{sup})` in a site :math:`v` at a timestep :math:`t`. In other words this parameter gives the ratio of current available energy amount to maximum potential energy amount of a supply intermittent commodity. This data is to be provided by the user and to be entered in the spreadsheet. The related section for this parameter in the spreadsheet can be found under the "SupIm" sheet. Here each row represents another timestep :math:`t` and each column represent a commodity tuple :math:`c_{vq}`. Rows are named after the timestep number :math:`n` of timesteps :math:`t_n`. Columns are named after the combination of site name :math:`v` and commodity name :math:`c`, in this respective order and seperated by a period(.). For example (Mid.Elec) represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted in column declarations, because every commodity of this parameter has to be from commodity type `SupIm` in any case.

**Maximum Stock Supply Limit Per Time Step**, :math:`\overline{l}_{vc}`, ``m.commodity.loc[sit,com,com_type]['maxperstep']``: The parameter :math:`\overline{l}_{vc}` represents the maximum energy amount of a stock commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Stock"`) that energy model is allowed to use per time step. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of stock commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{l}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Stock Supply Limit Per Vertex**, :math:`\overline{L}_{vc}`, ``m.commodity.loc[sit,com,com_type]['max']``: The parameter :math:`\overline{L}_{vc}` represents the maximum energy amount of a stock commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Stock"`) that energy model is allowed to use annually. The unit of this parameter is MW. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of stock commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{L}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Environmental Output Per Time Step**, :math:`\overline{m}_{vc}`, ``m.commodity.loc[sit,com,com_type]['maxperstep']``: The parameter :math:`\overline{m}_{vc}` represents the maximum energy amount of an environmental commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Env"`)  that energy model is allowed to produce and release to environment per time step. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of enviromental commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{m}_{vc}`. If there is no desired restriction of an enviromental commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Environmental Output**, :math:`\overline{M}_{vc}`, ``m.commodity.loc[sit,com,com_type]['max']``: The parameter :math:`\overline{M}_{vc}` represents the maximum energy amount of an environmental commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Env"`) that energy model is allowed to produce and release to environment annually. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of an environmental commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{M}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Sell Limit Per Time Step**, :math:`\overline{g}_{vc}`, ``m.commodity.loc[sit,com,com_type][`maxperstep`]``: The parameter :math:`\overline{g}_{vc}` represents the maximum energy amount of a sell commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Sell"`)  that energy model is allowed to sell per time step. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of sell commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{g}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Sell Limit**, :math:`\overline{G}_{vc}`, ``m.commodity.loc[sit,com,com_type][`max`]``: The parameter :math:`\overline{G}_{vc}` represents the maximum energy amount of a sell commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Sell"`) that energy model is allowed to sell annually. The unit of this parameter is MW. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of sell commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{G}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Buy Limit Per Time Step**, :math:`\overline{b}_{vc}`, ``m.commodity.loc[sit,com,com_type][`maxperstep`]``: The parameter :math:`\overline{b}_{vc}` represents the maximum energy amount of a buy commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Buy"`) that energy model is allowed to buy per time step. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of buy commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{b}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Buy Limit**, :math:`\overline{B}_{vc}`, ``m.commodity.loc[sit,com,com_type][`max`]``: The parameter :math:`\overline{B}_{vc}` represents the maximum energy amount of a buy commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Buy"`) that energy model is allowed to buy annually. The unit of this parameter is MW. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of buy commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{B}_{vc}`. If there is no desired restriction of a buy commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Global Annual CO**:math:`_\textbf{2}` **Emission Limit**, :math:`\overline{L}_{CO_2}`, ``m.hack.loc['Global CO2 Limit','Value']``: The parameter :math:`\overline{L}_{CO_2}` represents the maximum total energy amount of all environmental commodities that energy model is allowed to produce and release to environment annually. This parameter is optional. If the user desires to set a maximum annual limit to total :math:`CO_2` emission of the whole energy model, this can be done by entering the desired value to the related spreadsheet. The related section for this parameter can be found under the sheet "hacks". Here the the cell where the "Global CO2 limit" row and "value" column intersects stands for the parameter :math:`\overline{L}_{CO_2}`. If the user wants to disable this parameter and restriction it provides, this cell can be set to "inf" or simply be deleted. 

Process Technical Parameters
----------------------------

**Process Capacity Lower Bound**, :math:`\underline{K}_{vp}`, ``m.process.loc[sit,pro]['cap-lo']``: The parameter :math:`\underline{K}_{vp}` represents the minimum amount of power output capacity of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the fourth column with the header label "cap-lo" represents the parameters :math:`\underline{K}_{vp}` belonging to the corresponding process :math:`p` and site :math:`v` combinations. If there is no desired minimum limit for the process capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Process Capacity Installed**, :math:`K_{vp}`, ``m.process.loc[sit,pro]['inst-cap']``: The parameter :math:`K_{vp}` represents the amount of power output capacity of a process :math:`p` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the third column with the header label "inst-cap" represents the parameters :math:`K_{vp}` belonging to the corresponding process :math:`p` and site :math:`v` combinations.

**Process Capacity Upper Bound**, :math:`\overline{K}_{vp}`, ``m.process.loc[sit,pro]['cap-up']``: The parameter :math:`\overline{K}_{vp}` represents the maximum amount of power output capacity of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the fifth column with the header label "cap-up" represents the parameters :math:`\overline{K}_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. If there is no desired maximum limit for the process capacities, this parameter can be simply set to an unrealistic high value, to ignore this parameter.

**Process Maximal Gradient**, :math:`\overline{PG}_{vp}`, ``m.process.loc[sit,pro]['max-grad']``: The parameter :math:`\overline{PG}_{vp}` represents the maximal power gradient of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is 1/h. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the sixth column with the header label "max-grad" represents the parameters :math:`\overline{PG}_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. If there is no desired maximum limit for the process power gradient, this parameter can be simply set to an unrealistic high value, to ignore this parameter.

**Process Input Ratio**, :math:`r_{pc}^\text{in}`, ``m.r_in.loc[pro,co]``: The parameter :math:`r_{pc}^\text{in}` represents the ratio of the input amount of a commodity :math:`c` in a process :math:`p`, relative to the process throughput at a given timestep. The related section for this parameter in the spreadsheet can be found under the "Process-Comodity" sheet. Here each row represents another commodity :math:`c` that either goes in to or comes out of a process :math:`p`. The fourth column with the header label "ratio" represents the parameters of the corresponding process :math:`p`, commodity :math:`c` and direction (In,Out) combinations.

**Process Output Ratio**, :math:`r_{pc}^\text{out}`, ``m.r_out.loc[pro,co]``: The parameter :math:`r_{pc}^\text{out}` represents the ratio of the output amount of a commodity :math:`c` in a process :math:`p`, relative to the process throughput at a given timestep.  The related section for this parameter in the spreadsheet can be found under the "Process-Comodity" sheet. Here each row represents another commodity :math:`c` that either goes in to or comes out of a process :math:`p`. The fourth column with the header label "ratio" represents the parameters of the corresponding process :math:`p`, commodity :math:`c` and direction (In,Out) combinations.

Process input and output ratios are, in general, dimensionless since the majority of output and input commodities are represented in MW. Exceptionally, some process input and output ratios can be assigned units e.g. the environmental commodity (``Env``) ':math:`\text{CO}_2` could have a process output ratio with the unit of :math: `million tonnes/MWh`.

Since process input and output ratios take the process throughput :math:`\tau_{vpt}` as the reference in order to calculate the input and output commodity flows, the process input (or output) ratio of "1" is assigned to the commodity which represents the throughput. By default, the major input commodity flow of the process (e.g. 'Gas' for 'Gas plant', 'Wind' for 'Wind park') represents the process throughput so those commodities have the process input (or output) ratio of "1"; but the "throughput" selection can be arbitrarily shifted to other commodities (e.g. power output of the process) by scaling all of the process input and output ratios by an appropriate factor. 

Storage Technical Parameters
----------------------------

**Initial and Final State of Charge (relative)**, :math:`I_{vs}`, ``m.storage.loc[sit,sto,com]['init']``: The parameter :math:`I_{vs}` represents the initial load factor of a storage :math:`s` in a site :math:`v`. This parameter shows, as a percentage, how much of a storage is loaded at the beginning of the simulation. The same value should be preserved at the end of the simulation, to make sure that the optimization model doesn't consume the whole storage content at once and leave it empty at the end, otherwise this would disrupt the continuity of the optimization. The value of this parameter is expressed as a normalized percentage, where "1" represents a fully loaded storage and "0" represents an empty storage. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The twentieth column with the header label "init" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Efficiency During Charge**, :math:`e_{vs}^\text{in}`, ``m.storage.loc[sit,sto,com]['eff-in']``: The parameter :math:`e_{vs}^\text{in}` represents the charge efficiency of a storage :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The charge efficiency shows, how much of a desired energy and accordingly power can be succesfully stored into a storage. The value of this parameter is expressed as a normalized percentage, where "1" represents a charge with no power or energy loss and "0" represents that storage technology consumes whole enery during charge. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The tenth column with the header label "eff-in" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Efficiency During Discharge**, :math:`e_{vs}^\text{out}`, ``m.storage.loc[sit,sto,com]['eff-out']``:  The parameter :math:`e_{vs}^\text{out}` represents the discharge efficiency of a storage :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The discharge efficiency shows, how much of a desired energy and accordingly power can be succesfully retrieved out of a storage.  The value of this parameter is expressed as a normalized efipercentage, where "1" represents a discharge with no power or energy loss and "0" represents that storage technology consumes whole enery during discharge. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The eleventh column with the header label "eff-out" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Content Lower Bound**, :math:`\underline{K}_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['cap-lo-c']``: The parameter :math:`\underline{K}_{vs}^\text{c}` represents the minimum amount of energy content capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have. The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The fifth column with the header label "cap-lo-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.  If there is no desired minimum limit for the storage energy content capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Storage Content Installed**, :math:`K_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['inst-cap-c']``: The parameter :math:`K_{vs}^\text{c}` represents the amount of energy content capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The fourth column with the header label "inst-cap-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Content Upper Bound**, :math:`\overline{K}_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['cap-up-c']``: The parameter :math:`\overline{K}_{vs}^\text{c}` represents the maximum amount of energy content capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have.  The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The sixth column with the header label "cap-up-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations. If there is no desired maximum limit for the storage energy content capacitites, this parameter can be simply set to ""inf"" or an unrealistic high value, to ignore this parameter.

**Storage Power Lower Bound**, :math:`\underline{K}_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['cap-lo-p']``: The parameter :math:`\underline{K}_{vs}^\text{p}` represents the minimum amount of power output capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that energy system model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The eighth column with the header label "cap-lo-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.  If there is no desired minimum limit for the storage energy content capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Storage Power Installed**, :math:`K_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['inst-cap-p']``:  The parameter :math:`K_{vs}^\text{c}` represents the amount of power output capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The seventh column with the header label "inst-cap-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Power Upper Bound**, :math:`\overline{K}_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['cap-up-p']``: The parameter :math:`\overline{K}_{vs}^\text{p}` represents the maximum amount of power output capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have.  The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The sixth column with the header label "cap-up-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations. If there is no desired maximum limit for the storage energy content capacitites, this parameter can be simply set to ""inf"" or an unrealistic high value, to ignore this parameter.

Transmission Technical Parameters
---------------------------------

**Transmission Efficiency**, :math:`e_{af}`, ``m.transmission.loc[sin,sout,tra,com]['eff']``: The parameter :math:`e_{af}` represents the energy efficiency of a transmission :math:`f` that transfers a commodity :math:`c` through an arc :math:`a`. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The ratio of the output energy amount to input energy amount, gives the energy efficiency of a transmission process. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The fifth column with the header label "eff" represents the parameters :math:`e_{af}` of the corresponding combinations.

**Transmission Capacity Lower Bound**, :math:`\underline{K}_{af}`, ``m.transmission.loc[sin,sout,tra,com]['cap-lo']``: The parameter :math:`\underline{K}_{af}` represents the minimum power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that the energy system model is allowed to have. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The tenth column with the header label "cap-lo" represents the parameters :math:`\underline{K}_{af}` of the corresponding combinations. 

**Transmission Capacity Installed**, :math:`K_{af}`, ``m.transmission.loc[sin,sout,tra,com]['inst-cap']``: The parameter :math:`K_{af}` represents the amount of power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The tenth column with the header label "inst-cap" represents the parameters :math:`K_{af}` of the corresponding combinations.

**Transmission Capacity Upper Bound**, :math:`\overline{K}_{af}`, ``m.transmission.loc[sin,sout,tra,com]['cap-up']``: The parameter :math:`\overline{K}_{af}` represents the maximum power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that the energy system model is allowed to have. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission, site in, site out, commodity combination. The tenth column with the header label "cap-up" represents the parameters :math:`\overline{K}_{af}` of the corresponding combinations.

Demand Side Management Technical Parameters
-------------------------------------------
**DSM Efficiency**, :math:`e_{vc}`, ``m.dsm.loc[sit,com]['eff']``: The parameter :math:`e_{vc}` represents the efficiency of the DSM upshift process. Which means losses of the DSM up- or downshift have to be taken into account by this factor.

**DSM Delay Time**, :math:`y_{vc}`, ``m.dsm.loc[sit,com]['delay']``: The delay time :math:`y_{vc}` restricts how long the time delta between an upshift and its corresponding downshifts may be.

**DSM Recovery Time**, :math:`o_{vc}`, ``m.dsm.loc[sit,com]['recov']``: The recovery time :math:`o_{vc}` prevents the DSM system to continously shift demand. During the recovery time, all upshifts may not exceed a predfined value.

**DSM Maximal Upshift Capacity**, :math:`\overline{K}_{vc}^\text{up}`, MW, ``m.dsm.loc[sit,com]['cap-max-up']``: The DSM upshift capacity :math:`\overline{K}_{vc}^\text{up}` limits the total upshift in one time step.

**DSM Maximal Downshift Capacity**, :math:`\overline{K}_{vc}^\text{down}`, MW, ``m.dsm.loc[sit,com]['cap-max-down']``: Correspondingly, the DSM downshift capacity :math:`\overline{K}_{vc}^\text{down}` limits the total downshift in one time step.

Economical Parameters
^^^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Economical Model Parameters*

	+---------------------------+---------+-------------------------------------------------+
	|Parameter                  |Unit     |Description                                      |
	+===========================+=========+=================================================+
	|:math:`AF`                 | _       |Annuity factor                                   |
	+---------------------------+---------+-------------------------------------------------+
	|**Commodity Economical Parameters**                                                    |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vc}^\text{fuel}` |€/MWh    |Stock Commodity Fuel Costs                       |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vct}^\text{bs}`  |€/MWh    |Buy/Sell Commodity Buy/Sell Costs                |
	+---------------------------+---------+-------------------------------------------------+
	|**Process Economical Parameters**                                                      |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`i_{vp}`             | _       |Weighted Average Cost of Capital for Process     |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`z_{vp}`             | _       |Process Depreciation Period                      |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vp}^\text{inv}`  |€/(MW a) |Annualised Process Capacity Investment Costs     |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vp}^\text{fix}`  |€/(MW a) |Process Capacity Fixed Costs                     |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vp}^\text{var}`  |€/MWh    |Process Variable Costs                           |
	+---------------------------+---------+-------------------------------------------------+
	|**Storage Economical Parameters**                                                      |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`i_{vs}`             | _       |Weighted Average Cost of Capital for Storage     |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`z_{vs}`             | _       |Storage Depreciation Period                      |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vs}^\text{p,inv}`|€/(MWh a)|Annualised Storage Power Investment Costs        |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vs}^\text{p,fix}`|€/(MW a) |Annual Storage Power Fixed Costs                 |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vs}^\text{p,var}`|€/MWh    |Storage Power Variable Costs                     |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vs}^\text{c,inv}`|€/(MWh a)|Annualised Storage Size Investment Costs         |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vs}^\text{c,fix}`|€/(MWh a)|Annual Storage Size Fixed Costs                  |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vs}^\text{c,var}`|€/MWh    |Storage Usage Variable Costs                     |
	+---------------------------+---------+-------------------------------------------------+
	|**Transmission Economical Parameters**                                                 |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`i_{vf}`             | _       |Weighted Average Cost of Capital for Transmission|
	+---------------------------+---------+-------------------------------------------------+
	|:math:`z_{af}`             | _       |Tranmission Depreciation Period                  |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{af}^\text{inv}`  |€/(MW a) |Annualised Transmission Capacity Investment Costs|
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{af}^\text{fix}`  |€/(MWh a)|Annual Transmission Capacity Fixed Costs         |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{af}^\text{var}`  |€/MWh    |Tranmission Usage Variable Costs                 |
	+---------------------------+---------+-------------------------------------------------+

**Annuity factor**, :math:`AF(n,i)`,: Annuity factor :math:`AF` is used to calculate the present value of future fixed annuities. The parameter annuity factor is the only parameter that is not given as an input by the user. This parameter is derived from the parameters WACC :math:`i` (Weighted average cost of capital) and Depreciation :math:`z` by the annuity factor formula. The value of this parameter is expressed with the following equation.
 
.. math::

	AF = \frac{(1+i)^n i}{(1+i)^n - 1}

where;

* n represents the depreciation period :math:`z`.
* i represents the weighted average cost of capital(wacc) :math:`i`.

This derived parameter is calculated by the helper function :func:`annuity factor` and defined by the following code fragment. ::

    # derive annuity factor from WACC and depreciation periods
    process['annuity-factor'] = annuity_factor(
        process['depreciation'], process['wacc'])
    transmission['annuity-factor'] = annuity_factor(
        transmission['depreciation'], transmission['wacc'])
    storage['annuity-factor'] = annuity_factor(
        storage['depreciation'], storage['wacc'])

.. function:: annuity_factor

  Annuity factor formula.

  Evaluates the annuity factor formula for depreciation duration
  and interest rate. Works also well for equally sized numpy arrays as input.
    
  :param int n: number of depreciation periods (years)
  :param float i: interest rate (e.g. 0.06 means 6 %)

  :return: value of the expression :math:`\frac{(1+i)^n i}{(1+i)^n - 1}`

Commodity Economical Parameters
-------------------------------

**Stock Commodity Fuel Costs**, :math:`k_{vc}^\text{fuel}`, ``m.commodity.loc[c]['price']``: The parameter :math:`k_{vc}^\text{fuel}` represents the purchase cost for purchasing one unit (1 MWh) of a stock commodity :math:`c` (:math:`\forall c \in C_\text{stock}`) in a site :math:`v` (:math:`\forall v \in V`) . The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Commodity" sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fourth column of stock commodity tuples (:math:`\forall q = "Stock"`) in this sheet with the header label "price" represents the corresponding parameter :math:`k_{vc}^\text{fuel}`.

**Buy/Sell Commodity Buy/Sell Costs**, :math:`k_{vct}^\text{bs}`, ``com_prices[c].loc[tm]``: The parameter :math:`k_{vct}^\text{bs}` represents the purchase/buy cost for purchasing/selling one unit(1 MWh) of a buy/sell commodity :math:`c` (:math:`\forall c \in C_\text{buy}`)/(:math:`\forall c \in C_\text{sell}`) in a site :math:`v` (:math:`\forall v \in V`) at a timestep :math:`t` (:math:`\forall t \in T_m`). The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Commodity" sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fourth column of buy/sell commodity tuples (:math:`\forall q = "Buy"`)/(:math:`\forall q = "Sell"`) in this sheet with the header label "price" represents how the parameter :math:`k_{vct}^\text{bs}` will be defined. There are two options for this parameter. This parameter will either be a fix value for the whole simulation duration or will vary with the timesteps :math:`t`. For the first option, if the buy/sell price of a buy/sell commodity is a fix value for the whole simulation duration, this value can be entered directly into the corresponding cell with the unit €/MWh. For the second option, if the buy/sell price of a buy/sell commodity depends on time, accordingly on timesteps, a string (a linear sequence of characters, words, or other data) should be written in the corresponding cell. An example string looks like this: "1,25xBuy" where the first numbers (1,25) represent a coefficient for the price. This value is than multiplied by values from another list given with timeseries. Here the word "Buy" refers to a timeseries located in ""Buy-Sell-Price"" sheet with commodity names, types and timesteps. This timeseries should be filled with time dependent buy/sell price variables. The parameter :math:`k_{vct}^\text{bs}` is then calculated by the product of the price coefficient and the related time variable for a given timestep :math:`t`. This calculation and the decision for one of the two options is executed by the helper function :func:`get_com_price`.

.. function:: get_com_price(instance, tuples)

  :param str instance: a Pyomo ConcreteModel instance
  :param list tuples: a list of (site, commodity, commodity type) tuples
  
  :return: a Pandas DataFrame with entities as columns and timesteps as index
  
  Calculate commodity prices for each modelled timestep.
  Checks whether the input is a float. If it is a float it gets the input value as a fix value for commodity price. Otherwise if the input value is not a float, but a string, it extracts the price coefficient from the string and  multiplies it with a timeseries of commodity price variables.

Process Economical Parameters
-----------------------------

**Weighted Average Cost of Capital for Process**, :math:`i_{vp}`, : The parameter :math:`i_{vp}` represents the weighted average cost of capital for a process technology :math:`p` in a site :math:`v`. The weighted average cost of capital gives the interest rate (%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the tenth column with the header label "wacc" represents the parameters :math:`i_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. The parameter is given as a percentage, where "0,07" means 7%

**Process Depreciation Period**, :math:`z_{vp}`, (a): The parameter :math:`z_{vp}` represents the depreciation period of a process :math:`p` in a site :math:`v`. The depreciation period gives the economic lifetime (more conservative than technical lifetime) of a process investment. The unit of this parameter is "a", where "a" represents a year of 8760 hours. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the eleventh column with the header label "depreciation" represents the parameters :math:`z_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations.

**Annualised Process Capacity Investment Costs**, :math:`k_{vp}^\text{inv}`, ``m.process.loc[p]['inv-cost'] * m.process.loc[p]['annuity-factor']``: The parameter :math:`k_{vp}^\text{inv}` represents the annualised investment cost for adding one unit new capacity of a process technology :math:`p` in a site :math:`v`. The unit of this parameter is €/(MW a). This parameter is derived by the product of annuity factor :math:`AF` and the process capacity investment cost for a given process tuple. The process capacity investment cost is to be given as an input by the user. The related section for the process capacity investment cost in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the seventh column with the header label "inv-cost" represents the process capacity investment costs of the corresponding process :math:`p` and site :math:`v` combinations.

**Process Capacity Fixed Costs**, :math:`k_{vp}^\text{fix}`, ``m.process.loc[p]['fix-cost']``: The parameter :math:`k_{vp}^\text{fix}` represents the fix cost per one unit capacity :math:`\kappa_{vp}` of a process technology :math:`p` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MW a). The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the eighth column with the header label "fix-cost" represents the parameters :math:`k_{vp}^\text{fix}` of the corresponding process :math:`p` and site :math:`v` combinations. 

**Process Variable Costs**, :math:`k_{vp}^\text{var}`, ``m.process.loc[p]['var-cost']``: The parameter :math:`k_{vp}^\text{var}` represents the variable cost per one unit energy throughput :math:`\tau_{vpt}` through a process technology :math:`p` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the ninth column with the header label "var-cost" represents the parameters :math:`k_{vp}^\text{var}` of the corresponding process :math:`p` and site :math:`v` combinations. 

Storage Economical Parameters
-----------------------------

**Weighted Average Cost of Capital for Storage**, :math:`i_{vs}`, : The parameter :math:`i_{vs}` represents the weighted average cost of capital for a storage technology :math:`s` in a site :math:`v`. The weighted average cost of capital gives the interest rate(%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the nineteenth column with the header label "wacc" represents the parameters :math:`i_{vs}` of the corresponding storage :math:`s` and site :math:`v` combinations. The parameter is given as a percentage, where "0,07" means 7%.

**Storage Depreciation Period**, :math:`z_{vs}`, (a): The parameter :math:`z_{vs}` represents the depreciation period of a storage :math:`s` in a site :math:`v`. The depreciation period gives the economic lifetime (more conservative than technical lifetime) of a storage investment. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the eighteenth column with the header label "depreciation" represents the parameters :math:`z_{vs}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Annualised Storage Power Investment Costs**, :math:`k_{vs}^\text{p,inv}`, ``m.storage.loc[s]['inv-cost-p'] * m.storage.loc[s]['annuity-factor']``: The parameter :math:`k_{vs}^\text{p,inv}` represents the annualised investment cost for adding one unit new power output capacity of a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/(MWh a). This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new power output capacity of a storage :math:`s` in a site :math:`v`, which is to be given as an input parameter by the user. The related section for the storage power output capacity investment cost in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the twelfth column with the header label "inv-cost-p" represents the storage power output capacity investment cost of the corresponding storage :math:`s` and site :math:`v` combinations. 

**Annual Storage Power Fixed Costs**, :math:`k_{vs}^\text{p,fix}`, ``m.storage.loc[s]['fix-cost-p']``: The parameter :math:`k_{vs}^\text{p,fix}` represents the fix cost per one unit power output capacity of a storage technology :math:`s` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MW a). The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the fourteenth column with the header label "fix-cost-p" represents the parameters :math:`k_{vs}^\text{p,fix}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Storage Power Variable Costs**, :math:`k_{vs}^\text{p,var}`, ``m.storage.loc[s]['var-cost-p']``: The parameter :math:`k_{vs}^\text{p,var}` represents the variable cost per unit energy, that is stored in or retrieved from a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the sixteenth column with the header label "var-cost-p" represents the parameters :math:`k_{vs}^\text{p,var}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Annualised Storage Size Investment Costs**, :math:`k_{vs}^\text{c,inv}`, ``m.storage.loc[s]['inv-cost-c'] * m.storage.loc[s]['annuity-factor']``: The parameter :math:`k_{vs}^\text{c,inv}` represents the annualised investment cost for adding one unit new storage capacity to a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/(MWh a). This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new storage capacity of a storage :math:`s` in a site :math:`v`, which is to be given as an input parameter by the user. The related section for the storage content capacity investment cost in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the thirteenth column with the header label "inv-cost-c" represents the storage content capacity investment cost of the corresponding storage :math:`s` and site :math:`v` combinations. 


**Annual Storage Size Fixed Costs**, :math:`k_{vs}^\text{c,fix}`, ``m.storage.loc[s]['fix-cost-c']``: The parameter :math:`k_{vs}^\text{c,fix}` represents the fix cost per one unit storage content capacity of a storage technology :math:`s` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MWh a). The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the fifteenth column with the header label "fix-cost-c" represents the parameters :math:`k_{vs}^\text{c,fix}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Storage Usage Variable Costs**, :math:`k_{vs}^\text{c,var}`, ``m.storage.loc[s]['var-cost-c']``: The parameter :math:`k_{vs}^\text{p,var}` represents the variable cost per unit energy, that is conserved in a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the seventeenth column with the header label "var-cost-c" represents the parameters :math:`k_{vs}^\text{c,var}` of the corresponding storage :math:`s` and site :math:`v` combinations. The value of this parameter is usually set to zero, but the parameter can be taken advantage of if the storage has a short term usage or has an increased devaluation due to usage, compared to amount of energy stored. 

Transmission Economical Parameters
----------------------------------

**Weighted Average Cost of Capital for Transmission**, :math:`i_{vf}`, : The parameter :math:`i_{vf}` represents the weighted average cost of capital for a transmission :math:`f` transferring commodities through an arc :math:`a`. The weighted average cost of capital gives the interest rate(%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the twelfth column with the header label "wacc" represents the parameters :math:`i_{vf}` of the corresponding transmission :math:`f` and arc :math:`a` combinations. The parameter is given as a percentage, where "0,07" means 7%.

**Transmission Depreciation Period**, :math:`z_{af}`, (a): The parameter :math:`z_{af}` represents the depreciation period of a transmission :math:`f` transferring commodities through an arc :math:`a`. The depreciation period of gives the economic lifetime (more conservative than technical lifetime) of a transmission investment. The unit of this parameter is €/ (MW a). The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the thirteenth column with the header label "depreciation" represents the parameters :math:`z_{af}` of the corresponding transmission :math:`f` and arc :math:`a` combinations.

**Annualised Transmission Capacity Investment Costs**, :math:`k_{af}^\text{inv}`, ``m.transmission.loc[t]['inv-cost'] * m.transmission.loc[t]['annuity-factor']``: The parameter :math:`k_{af}^\text{inv}` represents the annualised investment cost for adding one unit new transmission capacity to a transmission :math:`f` transferring commodities through an arc :math:`a`. This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new transmission capacity of a transmission :math:`f` running through an arc :math:`a`, which is to be given as an input parameter by the user. The unit of this parameter is €/(MW a). The related section for the transmission capacity investment cost in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the sixth column with the header label "inv-cost" represents the transmission capacity investment cost of the corresponding transmission :math:`f` and arc :math:`a` combinations. 

**Annual Transmission Capacity Fixed Costs**, :math:`k_{af}^\text{fix}`, ``m.transmission.loc[t]['fix-cost']``: The parameter :math:`k_{af}^\text{fix}` represents the fix cost per one unit capacity of a transmission :math:`f` transferring commodities through an arc :math:`a`, that is charged annually. The unit of this parameter is €/(MWh a). The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the seventh column with the header label "fix-cost" represents the parameters :math:`k_{af}^\text{fix}` of the corresponding transmission :math:`f` and arc :math:`a` combinations. 

**Transmission Usage Variable Costs**, :math:`k_{af}^\text{var}`, ``m.transmission.loc[t]['var-cost']``: The parameter :math:`k_{af}^\text{var}` represents the variable cost per unit energy, that is transferred with a transmissiom :math:`f` through an arc :math:`a`. The unit of this parameter is €/ MWh. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the eighth column with the header label "var-cost" represents the parameters :math:`k_{af}^\text{var}` of the corresponding transmission :math:`f` and arc :math:`a` combinations.
