.. module:: urbs

Technical Parameters
^^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Technical Model Parameters*
    
    +-------------------------------------+----+---------------------------------------------+
    |Parameter                            |Unit|Description                                  |
    +=====================================+====+=============================================+
    |**General Technical Parameters**                                                        |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`w`                            | _  |Weight                                       |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\Delta t`                     | h  |Timestep Size                                |
    +-------------------------------------+----+---------------------------------------------+
    |**Commodity Technical Parameters**                                                      |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`d_{vct}`                      |MWh |Demand for Commodity                         |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`s_{vct}`                      | _  |Intermittent Supply Capacity Factor          |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{l}_{vc}`            |MW  |Maximum Stock Supply Limit Per Hour          |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{L}_{vc}`            |MWh |Maximum Annual Stock Supply Limit Per Vertex |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{m}_{vc}`            |t/h |Maximum Environmental Output Per Hour        |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{M}_{vc}`            | t  |Maximum Annual Environmental Output          |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{g}_{vc}`            |MW  |Maximum Sell Limit Per Hour                  |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{G}_{vc}`            |MWh |Maximum Annual Sell Limit                    |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{b}_{vc}`            |MW  |Maximum Buy Limit Per Hour                   |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{B}_{vc}`            |MWh |Maximum Annual Buy Limit                     |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{L}_{CO_2}`          | t  |Maximum Global Annual CO2 Emission Limit     |
    +-------------------------------------+----+---------------------------------------------+
    |**Process Technical Parameters**                                                        |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\underline{K}_{vp}`           |MW  |Process Capacity Lower Bound                 |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`K_{vp}`                       |MW  |Process Capacity Installed                   |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{K}_{vp}`            |MW  |Process Capacity Upper Bound                 |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{PG}_{vp}`           |1/h |Process Maximal Power Gradient (relative)    |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\underline{P}_{vp}`           | _  |Process Minimum Part Load Fraction           |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`f_{vpt}^\text{out}`           | _  |Process Output Ratio multiplyer              |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`r_{pc}^\text{in}`             | _  |Process Input Ratio                          |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\underline{r}_{pc}^\text{in}` | _  |Process Partial Input Ratio                  |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`r_{pc}^\text{out}`            | _  |Process Output Ratio                         |
    +-------------------------------------+----+---------------------------------------------+
    |**Storage Technical Parameters**                                                        |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`I_{vs}`                       | _  |Initial and Final State of Charge            |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`e_{vs}^\text{in}`             | _  |Storage Efficiency During Charge             |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`e_{vs}^\text{out}`            | _  |Storage Efficiency During Discharge          |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`d_{vs}`                       |1/h |Storage Self-discharge Per Hour              |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\underline{K}_{vs}^\text{c}`  |MWh |Storage Capacity Lower Bound                 |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`K_{vs}^\text{c}`              |MWh |Storage Capacity Installed                   |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{K}_{vs}^\text{c}`   |MWh |Storage Capacity Upper Bound                 |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\underline{K}_{vs}^\text{p}`  |MW  |Storage Power Lower Bound                    |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`K_{vs}^\text{p}`              |MW  |Storage Power Installed                      |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{K}_{vs}^\text{p}`   |MW  |Storage Power Upper Bound                    |
    +-------------------------------------+----+---------------------------------------------+
    |**Transmission Technical Parameters**                                                   |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`e_{af}`                       | _  |Transmission Efficiency                      |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\underline{K}_{af}`           |MW  |Tranmission Capacity Lower Bound             |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`K_{af}`                       |MW  |Tranmission Capacity Installed               |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{K}_{af}`            |MW  |Tranmission Capacity Upper Bound             |
    +-------------------------------------+----+---------------------------------------------+
    |**Demand Side Management Parameters**                                                   |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`e_{vc}`                       | _  |DSM Efficiency                               |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`y_{vc}`                       | _  |DSM Delay Time                               |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`o_{vc}`                       | _  |DSM Recovery Time                            |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{K}_{vc}^\text{up}`  |MW  |DSM Maximal Upshift Per Hour                 |
    +-------------------------------------+----+---------------------------------------------+
    |:math:`\overline{K}_{vc}^\text{down}`|MW  |DSM Maximal Downshift Per Hour               |
    +-------------------------------------+----+---------------------------------------------+

General Technical Parameters
----------------------------
**Weight**, :math:`w`, ``weight``: The parameter :math:`w` helps to scale variable costs and emissions from the length of simulation, that the energy system model is being observed, to an annual result. This parameter represents the rate of a year (8760 hours) to the observed time span. The observed time span is calculated by the product of number of time steps of the set :math:`T` and the time step duration. In script ``model.py`` this parameter is defined by the model parameter ``weight`` and initialized by the following code fragment:
::

    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.tm) * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')
		

**Timestep Duration**, :math:`\Delta t`, ``dt``: The variable :math:`\Delta t` represents the duration between two sequential timesteps :math:`t_x` and :math:`t_{x+1}`. This is calculated by the subtraction of smaller one from the bigger of the two sequential timesteps :math:`\Delta t = t_{x+1} - t_x`. This variable is the unit of time for the optimization model, is expressed in the unit h and by default the value is set to ``1``. In script ``model.py`` this variable is defined by the model variable ``dt`` and initialized by the following code fragment:
::

    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')
		

Commodity Technical Parameters
------------------------------

**Demand for Commodity**, :math:`d_{vct}`, ``m.demand_dict[(sit, com)][tm]``: The parameter represents the energy amount of a demand commodity tuple :math:`c_{vq}` required at a timestep :math:`t` (:math:`\forall v \in V, q = "Demand", \forall t \in T_m`). The unit of this parameter is MWh. This data is to be provided by the user and to be entered in the spreadsheet. The related section for this parameter in the spreadsheet can be found under the "Demand" sheet. Here each row represents another timestep :math:`t` and each column represent a commodity tuple :math:`c_{vq}`. Rows are named after the timestep number :math:`n` of timesteps :math:`t_n`. Columns are named after the combination of site name :math:`v` and commodity name :math:`c` respecting the order and seperated by a period(.). For example (Mid, Elec) represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted in column declarations, because every commodity of this parameter has to be from commodity type `Demand` in any case.

**Intermittent Supply Capacity Factor**, :math:`s_{vct}`, ``m.supim_dict[(sit, coin)][tm]``: The parameter :math:`s_{vct}` represents the normalized availability of a supply intermittent commodity :math:`c` :math:`(\forall c \in C_\text{sup})` in a site :math:`v` at a timestep :math:`t`. In other words this parameter gives the ratio of current available energy amount to maximum potential energy amount of a supply intermittent commodity. This data is to be provided by the user and to be entered in the spreadsheet. The related section for this parameter in the spreadsheet can be found under the "SupIm" sheet. Here each row represents another timestep :math:`t` and each column represent a commodity tuple :math:`c_{vq}`. Rows are named after the timestep number :math:`n` of timesteps :math:`t_n`. Columns are named after the combination of site name :math:`v` and commodity name :math:`c`, in this respective order and seperated by a period(.). For example (Mid.Elec) represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted in column declarations, because every commodity of this parameter has to be from commodity type `SupIm` in any case.

**Maximum Stock Supply Limit Per Hour**, :math:`\overline{l}_{vc}`, ``m.commodity_dict['maxperhour'][(sit, com, com_type)]``: The parameter :math:`\overline{l}_{vc}` represents the maximum energy amount of a stock commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Stock"`) that energy model is allowed to use per hour. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of stock commodity tuples in this sheet with the header label "maxperhour" represents the parameter :math:`\overline{l}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Stock Supply Limit Per Vertex**, :math:`\overline{L}_{vc}`, ``m.commodity_dict['max'][(sit, com, com_type)]``: The parameter :math:`\overline{L}_{vc}` represents the maximum energy amount of a stock commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Stock"`) that energy model is allowed to use annually. The unit of this parameter is MWh. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of stock commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{L}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Environmental Output Per Hour**, :math:`\overline{m}_{vc}`, ``m.commodity_dict['maxperhour'][(sit, com, com_type)]``: The parameter :math:`\overline{m}_{vc}` represents the maximum energy amount of an environmental commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Env"`)  that energy model is allowed to produce and release to environment per time step. This parameter applies to every timestep and does not vary for each timestep :math:`t/h`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of enviromental commodity tuples in this sheet with the header label "maxperhour" represents the parameter :math:`\overline{m}_{vc}`. If there is no desired restriction of an enviromental commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Environmental Output**, :math:`\overline{M}_{vc}`, ``m.commodity_dict['max'][(sit, com, com_type)]``: The parameter :math:`\overline{M}_{vc}` represents the maximum energy amount of an environmental commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Env"`) that energy model is allowed to produce and release to environment annually. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of an environmental commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{M}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Sell Limit Per Hour**, :math:`\overline{g}_{vc}`, ``m.commodity_dict['maxperhour'][(sit, com, com_type)]``: The parameter :math:`\overline{g}_{vc}` represents the maximum energy amount of a sell commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Sell"`) that energy model is allowed to sell per hour. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of sell commodity tuples in this sheet with the header label "maxperhour" represents the parameter :math:`\overline{g}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Sell Limit**, :math:`\overline{G}_{vc}`, ``m.commodity_dict['max'][(sit, com, com_type)]``: The parameter :math:`\overline{G}_{vc}` represents the maximum energy amount of a sell commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Sell"`) that energy model is allowed to sell annually. The unit of this parameter is MWh. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of sell commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{G}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Buy Limit Per Hour**, :math:`\overline{b}_{vc}`, ``m.commodity_dict['maxperhour'][(sit, com, com_type)]``: The parameter :math:`\overline{b}_{vc}` represents the maximum energy amount of a buy commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Buy"`) that energy model is allowed to buy per hour. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of buy commodity tuples in this sheet with the header label "maxperhour" represents the parameter :math:`\overline{b}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Buy Limit**, :math:`\overline{B}_{vc}`, ``m.commodity_dict['max'][(sit, com, com_type)]``: The parameter :math:`\overline{B}_{vc}` represents the maximum energy amount of a buy commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Buy"`) that energy model is allowed to buy annually. The unit of this parameter is MWh. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of buy commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{B}_{vc}`. If there is no desired restriction of a buy commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Global Annual CO**:math:`_\textbf{2}` **Emission Limit**, :math:`\overline{L}_{CO_2}`, ``m.global_prop.loc['CO2 limit', 'value']``: The parameter :math:`\overline{L}_{CO_2}` represents the maximum total energy amount of all environmental commodities that energy model is allowed to produce and release to environment annually. This parameter is optional. If the user desires to set a maximum annual limit to total :math:`CO_2` emission of the whole energy model, this can be done by entering the desired value to the related spreadsheet. The related section for this parameter can be found under the sheet "Global". Here the the cell where the "CO2 limit" row and "value" column intersects stands for the parameter :math:`\overline{L}_{CO_2}`. If the user wants to disable this parameter and restriction it provides, this cell can be set to "inf" or simply be deleted. 

Process Technical Parameters
----------------------------

**Process Capacity Lower Bound**, :math:`\underline{K}_{vp}`, ``m.process_dict['cap-lo'][sit, pro]``: The parameter :math:`\underline{K}_{vp}` represents the minimum amount of power output capacity of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the fourth column with the header label "cap-lo" represents the parameters :math:`\underline{K}_{vp}` belonging to the corresponding process :math:`p` and site :math:`v` combinations. If there is no desired minimum limit for the process capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Process Capacity Installed**, :math:`K_{vp}`, ``m.process_dict['inst-cap'][sit, pro]``: The parameter :math:`K_{vp}` represents the amount of power output capacity of a process :math:`p` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the third column with the header label "inst-cap" represents the parameters :math:`K_{vp}` belonging to the corresponding process :math:`p` and site :math:`v` combinations.

**Process Capacity Upper Bound**, :math:`\overline{K}_{vp}`, ``m.process_dict['cap-up'][sit, pro]``: The parameter :math:`\overline{K}_{vp}` represents the maximum amount of power output capacity of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the fifth column with the header label "cap-up" represents the parameters :math:`\overline{K}_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. Alternatively, :math:`\overline{K}_{vp}` is determined by the column with the label "area-per-cap", whenever the value in "cap-up" times the value "area-per-cap" is larger than the value in column "area" in sheet "Site" for site :math:`v`. If there is no desired maximum limit for the process capacities, both input parameters can be simply set to an unrealistic high value, to ignore this parameter.

**Process Maximal Gradient**, :math:`\overline{PG}_{vp}`, ``m.process_dict['max-grad'][(sit, pro)]``: The parameter :math:`\overline{PG}_{vp}` represents the maximal power gradient of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is 1/h. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the sixth column with the header label "max-grad" represents the parameters :math:`\overline{PG}_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. If there is no desired maximum limit for the process power gradient, this parameter can be simply set to an unrealistic high value, to ignore this parameter.

**Process Minimum Part Load Fraction**, :math:`\underline{P}_{vp}`, ``m.process_dict['min-fraction'][(sit, pro)]``: The parameter :math:`\underline{P}_{vp}` represents the minimum allowable part load of a process :math:`p` at a site :math:`v` as a fraction of the total process capacity. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the twelfth column with the header label "partial" represents the parameters :math:`\underline{P}_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations.

**Process Output Ratio multiplyer**, :math:`f_{vpt}^\text{out}`,
``m.eff_factor_dict[(sit, pro)]``: The parameter time series
:math:`f_{vpt}^\text{out}` allows for a time dependent modification of process
outputs and by extension of the process efficiency. It can be used, e.g., to
model temperature dependent efficiencies of processes or to include scheduled
maintenance intervals. Note that the output of environmental commodities is not
manipulated by this factor as it is typially linked to an input commodity as
, e.g., CO2 output is linked to a fossil input.

**Process Input Ratio**, :math:`r_{pc}^\text{in}`, ``m.r_in_dict[(pro, co)]``: The parameter :math:`r_{pc}^\text{in}` represents the ratio of the input amount of a commodity :math:`c` in a process :math:`p`, relative to the process throughput at a given timestep. The related section for this parameter in the spreadsheet can be found under the "Process-Comodity" sheet. Here each row represents another commodity :math:`c` that either goes in to or comes out of a process :math:`p`. The fourth column with the header label "ratio" represents the parameters of the corresponding process :math:`p`, commodity :math:`c` and direction (In,Out) combinations.

**Process Partial Input Ratio**, :math:`\underline{r}_{pc}^\text{in}`, ``m.r_in_min_fraction[pro, coin]``: The parameter :math:`\underline{r}_{pc}^\text{in}` represents the ratio of the amount of input commodity :math:`c` a process :math:`p` consumes if it is at its minimum allowable partial operation. More precisely, when its throughput :math:`\tau_{vpt}` has the minimum value :math:`\omega_{vpt} \underline{P}_{vp}`.

**Process Output Ratio**, :math:`r_{pc}^\text{out}`, ``m.r_out_dict[(pro, co)]``: The parameter :math:`r_{pc}^\text{out}` represents the ratio of the output amount of a commodity :math:`c` in a process :math:`p`, relative to the process throughput at a given timestep.  The related section for this parameter in the spreadsheet can be found under the "Process-Commodity" sheet. Here each row represents another commodity :math:`c` that either goes in to or comes out of a process :math:`p`. The fourth column with the header label "ratio" represents the parameters of the corresponding process :math:`p`, commodity :math:`c` and direction (In,Out) combinations. 

Process input and output ratios are, in general, dimensionless since the majority of output and input commodities are represented in MW. Exceptionally, some process input and output ratios can be assigned units e.g. the environmental commodity (``Env``) ':math:`\text{CO}_2` could have a process output ratio with the unit of :math:`Mt/MWh`.

Since process input and output ratios take the process throughput :math:`\tau_{vpt}` as the reference in order to calculate the input and output commodity flows, the process input (or output) ratio of "1" is assigned to the commodity which represents the throughput. By default, the major input commodity flow of the process (e.g. 'Gas' for 'Gas plant', 'Wind' for 'Wind park') represents the process throughput, so those commodities have the process input (or output) ratio of "1"; but the "throughput" selection can be arbitrarily shifted to other commodities (e.g. power output of the process) by scaling all of the process input and output ratios by an appropriate factor. 

Storage Technical Parameters
----------------------------

**Initial and Final State of Charge (relative)**, :math:`I_{vs}`, ``m.storage_dict['init'][(sit, sto, com)]``: The parameter :math:`I_{vs}` represents the initial load factor of a storage :math:`s` in a site :math:`v`. This parameter shows, as a percentage, how much of a storage is loaded at the beginning of the simulation. If this value is left unspecified the initial storage constraint is variable. The same value should be preserved at the end of the simulation, to make sure that the optimization model doesn't consume the whole storage content at once and leave it empty at the end, otherwise this would disrupt the continuity of the optimization. The value of this parameter is expressed as a normalized percentage, where "1" represents a fully loaded storage and "0" represents an empty storage. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The twentieth column with the header label "init" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Efficiency During Charge**, :math:`e_{vs}^\text{in}`, ``m.storage_dict['eff-in'][(sit, sto, com)]``: The parameter :math:`e_{vs}^\text{in}` represents the charge efficiency of a storage :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The charge efficiency shows, how much of a desired energy and accordingly power can be succesfully stored into a storage. The value of this parameter is expressed as a normalized percentage, where "1" represents a charge with no power or energy loss and "0" represents that storage technology consumes whole enery during charge. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The tenth column with the header label "eff-in" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Efficiency During Discharge**, :math:`e_{vs}^\text{out}`, ``m.storage_dict['eff-out'][(sit, sto, com)]``:  The parameter :math:`e_{vs}^\text{out}` represents the discharge efficiency of a storage :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The discharge efficiency shows, how much of a desired energy and accordingly power can be succesfully retrieved out of a storage.  The value of this parameter is expressed as a normalized efipercentage, where "1" represents a discharge with no power or energy loss and "0" represents that storage technology consumes whole enery during discharge. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The eleventh column with the header label "eff-out" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Self-discharge Per Hour**, :math:`d_{vs}`, ``m.storage_dict['discharge'][(sit, sto, com)]``: The parameter :math:`d_{vs}` represents the fraction of the energy content within a storage which is lost due to self-discharge per hour. It introduces an exponential decay of a given storage state if no charging/discharging takes place. The unit of this parameter is 1/h.

**Storage Capacity Lower Bound**, :math:`\underline{K}_{vs}^\text{c}`, ``m.storage_dict['cap-lo-c'][(sit, sto, com)]``: The parameter :math:`\underline{K}_{vs}^\text{c}` represents the minimum amount of energy content capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have. The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The fifth column with the header label "cap-lo-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.  If there is no desired minimum limit for the storage energy content capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Storage Capacity Installed**, :math:`K_{vs}^\text{c}`, ``m.storage_dict['inst-cap-c'][(sit, sto, com)]]``: The parameter :math:`K_{vs}^\text{c}` represents the amount of energy content capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The fourth column with the header label "inst-cap-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Capacity Upper Bound**, :math:`\overline{K}_{vs}^\text{c}`, ``m.storage_dict['cap-up-c'][(sit, sto, com)]``: The parameter :math:`\overline{K}_{vs}^\text{c}` represents the maximum amount of energy content capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have.  The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The sixth column with the header label "cap-up-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations. If there is no desired maximum limit for the storage energy content capacitites, this parameter can be simply set to ""inf"" or an unrealistic high value, to ignore this parameter.

**Storage Power Lower Bound**, :math:`\underline{K}_{vs}^\text{p}`, ``m.storage_dict['cap-lo-p'][(sit, sto, com)]``: The parameter :math:`\underline{K}_{vs}^\text{p}` represents the minimum amount of power output capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that energy system model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The eighth column with the header label "cap-lo-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.  If there is no desired minimum limit for the storage energy content capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Storage Power Installed**, :math:`K_{vs}^\text{p}`, ``m.storage_dict['inst-cap-p'][(sit, sto, com)]]``:  The parameter :math:`K_{vs}^\text{c}` represents the amount of power output capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The seventh column with the header label "inst-cap-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Power Upper Bound**, :math:`\overline{K}_{vs}^\text{p}`, ``m.storage_dict['cap-up-p'][(sit, sto, com)]``: The parameter :math:`\overline{K}_{vs}^\text{p}` represents the maximum amount of power output capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have.  The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The sixth column with the header label "cap-up-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations. If there is no desired maximum limit for the storage energy content capacitites, this parameter can be simply set to ""inf"" or an unrealistic high value, to ignore this parameter.

Transmission Technical Parameters
---------------------------------

**Transmission Efficiency**, :math:`e_{af}`, ``m.transmission_dict['eff'][(sin, sout, tra, com)]``: The parameter :math:`e_{af}` represents the energy efficiency of a transmission :math:`f` that transfers a commodity :math:`c` through an arc :math:`a`. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The ratio of the output energy amount to input energy amount, gives the energy efficiency of a transmission process. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The fifth column with the header label "eff" represents the parameters :math:`e_{af}` of the corresponding combinations.

**Transmission Capacity Lower Bound**, :math:`\underline{K}_{af}`, ``m.transmission_dict['cap-lo'][(sin, sout, tra, com)]``: The parameter :math:`\underline{K}_{af}` represents the minimum power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that the energy system model is allowed to have. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The tenth column with the header label "cap-lo" represents the parameters :math:`\underline{K}_{af}` of the corresponding combinations. 

**Transmission Capacity Installed**, :math:`K_{af}`, ``m.transmission_dict['inst-cap'][(sin, sout, tra, com)]``: The parameter :math:`K_{af}` represents the amount of power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The tenth column with the header label "inst-cap" represents the parameters :math:`K_{af}` of the corresponding combinations.

**Transmission Capacity Upper Bound**, :math:`\overline{K}_{af}`, ``m.transmission_dict['cap-up'][(sin, sout, tra, com)]``: The parameter :math:`\overline{K}_{af}` represents the maximum power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that the energy system model is allowed to have. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission, site in, site out, commodity combination. The tenth column with the header label "cap-up" represents the parameters :math:`\overline{K}_{af}` of the corresponding combinations.

Demand Side Management Technical Parameters
-------------------------------------------
**DSM Efficiency**, :math:`e_{vc}`, ``m.dsm_dict['eff'][(sit, com)]``: The parameter :math:`e_{vc}` represents the efficiency of the DSM upshift process. Which means losses of the DSM up- or downshift have to be taken into account by this factor.

**DSM Delay Time**, :math:`y_{vc}`, ``m.dsm_dict['delay'][(sit, com)]``: The delay time :math:`y_{vc}` restricts how long the time delta between an upshift and its corresponding downshifts may be.

**DSM Recovery Time**, :math:`o_{vc}`, ``m.dsm_dict['recov'][(sit, com)]``: The recovery time :math:`o_{vc}` prevents the DSM system to continously shift demand. During the recovery time, all upshifts may not exceed a predfined value.

**DSM Maximal Upshift Per Hour**, :math:`\overline{K}_{vc}^\text{up}`, MW, ``m.dsm_dict['cap-max-up'][(sit, com)]``: The DSM upshift capacity :math:`\overline{K}_{vc}^\text{up}` limits the total upshift in one hour.

**DSM Maximal Downshift Per Hour**, :math:`\overline{K}_{vc}^\text{down}`, MW, ``m.dsm_dict['cap-max-down'][(sit, com)]``: Correspondingly, the DSM downshift capacity :math:`\overline{K}_{vc}^\text{down}` limits the total downshift in one hour.

