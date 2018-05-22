.. module:: urbs

Economic Parameters
^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Economic Model Parameters*

	+---------------------------+---------+-------------------------------------------------+
	|Parameter                  |Unit     |Description                                      |
	+===========================+=========+=================================================+
	|:math:`AF`                 | _       |Annuity factor                                   |
	+---------------------------+---------+-------------------------------------------------+
	|**Commodity Economic Parameters**                                                      |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vc}^\text{fuel}` |€/MWh    |Stock Commodity Fuel Costs                       |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vc}^\text{env}`  |€/MWh    |Environmental Commodity Costs                    |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vct}^\text{bs}`  |€/MWh    |Buy/Sell Commodity Buy/Sell Costs                |
	+---------------------------+---------+-------------------------------------------------+
	|**Process Economic Parameters**                                                        |
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
	|**Storage Economic Parameters**                                                        |
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
	|**Transmission Economic Parameters**                                                   |
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

Commodity Economic Parameters
-----------------------------

**Stock Commodity Fuel Costs**, :math:`k_{vc}^\text{fuel}`, ``m.commodity.loc[c]['price']``: The parameter :math:`k_{vc}^\text{fuel}` represents the purchase cost for purchasing one unit (1 MWh) of a stock commodity :math:`c` (:math:`\forall c \in C_\text{stock}`) in a site :math:`v` (:math:`\forall v \in V`). The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Commodity" sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fourth column of stock commodity tuples (:math:`\forall q = "Stock"`) in this sheet with the header label "price" represents the corresponding parameter :math:`k_{vc}^\text{fuel}`.

**Environmental Commodity Costs**, :math:`k_{vc}^\text{env}`, ``m.commodity.loc[c]['price']``: The parameter :math:`k_{vc}^\text{env}` represents the cost for producing/emitting one unit (1 t, 1 kg, ...) of an environmentcal commodity :math:`c` (:math:`\forall c \in C_\text{env}`) in a site :math:`v` (:math:`\forall v \in V`). The unit of this parameter is €/t (i.e. per unit of output). The related section for this parameter in the spreadsheet is the "Commodity" sheet. Here, each row represents a commodity tuple :math:`c_{vq}` and the fourth column of environmental commodity tuples (:math:`\forall q = "Env"`) in this sheet with the header label "price" represents the corresponding parameter :math:`k_{vc}^\text{env}`.

**Buy/Sell Commodity Buy/Sell Costs**, :math:`k_{vct}^\text{bs}`, ``com_prices[c].loc[tm]``: The parameter :math:`k_{vct}^\text{bs}` represents the purchase/buy cost for purchasing/selling one unit(1 MWh) of a buy/sell commodity :math:`c` (:math:`\forall c \in C_\text{buy}`)/(:math:`\forall c \in C_\text{sell}`) in a site :math:`v` (:math:`\forall v \in V`) at a timestep :math:`t` (:math:`\forall t \in T_m`). The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Commodity" sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fourth column of buy/sell commodity tuples (:math:`\forall q = "Buy"`)/(:math:`\forall q = "Sell"`) in this sheet with the header label "price" represents how the parameter :math:`k_{vct}^\text{bs}` will be defined. There are two options for this parameter. This parameter will either be a fix value for the whole simulation duration or will vary with the timesteps :math:`t`. For the first option, if the buy/sell price of a buy/sell commodity is a fix value for the whole simulation duration, this value can be entered directly into the corresponding cell with the unit €/MWh. For the second option, if the buy/sell price of a buy/sell commodity depends on time, accordingly on timesteps, a string (a linear sequence of characters, words, or other data) should be written in the corresponding cell. An example string looks like this: "1.25xBuy" where the first numbers (1.25) represent a coefficient for the price. This value is than multiplied by values from another list given with timeseries. Here the word "Buy" refers to a timeseries located in ""Buy-Sell-Price"" sheet with commodity names, types and timesteps. This timeseries should be filled with time dependent buy/sell price variables. The parameter :math:`k_{vct}^\text{bs}` is then calculated by the product of the price coefficient and the related time variable for a given timestep :math:`t`. This calculation and the decision for one of the two options is executed by the helper function :func:`get_com_price`.

.. function:: get_com_price(instance, tuples)

  :param str instance: a Pyomo ConcreteModel instance
  :param list tuples: a list of (site, commodity, commodity type) tuples
  
  :return: a Pandas DataFrame with entities as columns and timesteps as index
  
  Calculate commodity prices for each modelled timestep.
  Checks whether the input is a float. If it is a float it gets the input value as a fix value for commodity price. Otherwise if the input value is not a float, but a string, it extracts the price coefficient from the string and  multiplies it with a timeseries of commodity price variables.

Process Economic Parameters
---------------------------

**Weighted Average Cost of Capital for Process**, :math:`i_{vp}`, : The parameter :math:`i_{vp}` represents the weighted average cost of capital for a process technology :math:`p` in a site :math:`v`. The weighted average cost of capital gives the interest rate (%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the tenth column with the header label "wacc" represents the parameters :math:`i_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. The parameter is given as a percentage, where "0.07" means 7%

**Process Depreciation Period**, :math:`z_{vp}`, (a): The parameter :math:`z_{vp}` represents the depreciation period of a process :math:`p` in a site :math:`v`. The depreciation period gives the economic lifetime (more conservative than technical lifetime) of a process investment. The unit of this parameter is "a", where "a" represents a year of 8760 hours. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the eleventh column with the header label "depreciation" represents the parameters :math:`z_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations.

**Annualised Process Capacity Investment Costs**, :math:`k_{vp}^\text{inv}`, ``m.process.loc[p]['inv-cost'] * m.process.loc[p]['annuity-factor']``: The parameter :math:`k_{vp}^\text{inv}` represents the annualised investment cost for adding one unit new capacity of a process technology :math:`p` in a site :math:`v`. The unit of this parameter is €/(MW a). This parameter is derived by the product of annuity factor :math:`AF` and the process capacity investment cost for a given process tuple. The process capacity investment cost is to be given as an input by the user. The related section for the process capacity investment cost in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the seventh column with the header label "inv-cost" represents the process capacity investment costs of the corresponding process :math:`p` and site :math:`v` combinations.

**Process Capacity Fixed Costs**, :math:`k_{vp}^\text{fix}`, ``m.process.loc[p]['fix-cost']``: The parameter :math:`k_{vp}^\text{fix}` represents the fix cost per one unit capacity :math:`\kappa_{vp}` of a process technology :math:`p` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MW a). The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the eighth column with the header label "fix-cost" represents the parameters :math:`k_{vp}^\text{fix}` of the corresponding process :math:`p` and site :math:`v` combinations. 

**Process Variable Costs**, :math:`k_{vp}^\text{var}`, ``m.process.loc[p]['var-cost']``: The parameter :math:`k_{vp}^\text{var}` represents the variable cost per one unit energy throughput :math:`\tau_{vpt}` through a process technology :math:`p` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the ninth column with the header label "var-cost" represents the parameters :math:`k_{vp}^\text{var}` of the corresponding process :math:`p` and site :math:`v` combinations.

Storage Economic Parameters
---------------------------

**Weighted Average Cost of Capital for Storage**, :math:`i_{vs}`, : The parameter :math:`i_{vs}` represents the weighted average cost of capital for a storage technology :math:`s` in a site :math:`v`. The weighted average cost of capital gives the interest rate(%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the nineteenth column with the header label "wacc" represents the parameters :math:`i_{vs}` of the corresponding storage :math:`s` and site :math:`v` combinations. The parameter is given as a percentage, where "0.07" means 7%.

**Storage Depreciation Period**, :math:`z_{vs}`, (a): The parameter :math:`z_{vs}` represents the depreciation period of a storage :math:`s` in a site :math:`v`. The depreciation period gives the economic lifetime (more conservative than technical lifetime) of a storage investment. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the eighteenth column with the header label "depreciation" represents the parameters :math:`z_{vs}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Annualised Storage Power Investment Costs**, :math:`k_{vs}^\text{p,inv}`, ``m.storage.loc[s]['inv-cost-p'] * m.storage.loc[s]['annuity-factor']``: The parameter :math:`k_{vs}^\text{p,inv}` represents the annualised investment cost for adding one unit new power output capacity of a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/(MWh a). This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new power output capacity of a storage :math:`s` in a site :math:`v`, which is to be given as an input parameter by the user. The related section for the storage power output capacity investment cost in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the twelfth column with the header label "inv-cost-p" represents the storage power output capacity investment cost of the corresponding storage :math:`s` and site :math:`v` combinations. 

**Annual Storage Power Fixed Costs**, :math:`k_{vs}^\text{p,fix}`, ``m.storage.loc[s]['fix-cost-p']``: The parameter :math:`k_{vs}^\text{p,fix}` represents the fix cost per one unit power output capacity of a storage technology :math:`s` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MW a). The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the fourteenth column with the header label "fix-cost-p" represents the parameters :math:`k_{vs}^\text{p,fix}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Storage Power Variable Costs**, :math:`k_{vs}^\text{p,var}`, ``m.storage.loc[s]['var-cost-p']``: The parameter :math:`k_{vs}^\text{p,var}` represents the variable cost per unit energy, that is stored in or retrieved from a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the sixteenth column with the header label "var-cost-p" represents the parameters :math:`k_{vs}^\text{p,var}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Annualised Storage Size Investment Costs**, :math:`k_{vs}^\text{c,inv}`, ``m.storage.loc[s]['inv-cost-c'] * m.storage.loc[s]['annuity-factor']``: The parameter :math:`k_{vs}^\text{c,inv}` represents the annualised investment cost for adding one unit new storage capacity to a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/(MWh a). This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new storage capacity of a storage :math:`s` in a site :math:`v`, which is to be given as an input parameter by the user. The related section for the storage content capacity investment cost in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the thirteenth column with the header label "inv-cost-c" represents the storage content capacity investment cost of the corresponding storage :math:`s` and site :math:`v` combinations. 

**Annual Storage Size Fixed Costs**, :math:`k_{vs}^\text{c,fix}`, ``m.storage.loc[s]['fix-cost-c']``: The parameter :math:`k_{vs}^\text{c,fix}` represents the fix cost per one unit storage content capacity of a storage technology :math:`s` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MWh a). The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the fifteenth column with the header label "fix-cost-c" represents the parameters :math:`k_{vs}^\text{c,fix}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Storage Usage Variable Costs**, :math:`k_{vs}^\text{c,var}`, ``m.storage.loc[s]['var-cost-c']``: The parameter :math:`k_{vs}^\text{p,var}` represents the variable cost per unit energy, that is conserved in a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the seventeenth column with the header label "var-cost-c" represents the parameters :math:`k_{vs}^\text{c,var}` of the corresponding storage :math:`s` and site :math:`v` combinations. The value of this parameter is usually set to zero, but the parameter can be taken advantage of if the storage has a short term usage or has an increased devaluation due to usage, compared to amount of energy stored. 

Transmission Economic Parameters
--------------------------------

**Weighted Average Cost of Capital for Transmission**, :math:`i_{vf}`, : The parameter :math:`i_{vf}` represents the weighted average cost of capital for a transmission :math:`f` transferring commodities through an arc :math:`a`. The weighted average cost of capital gives the interest rate(%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the twelfth column with the header label "wacc" represents the parameters :math:`i_{vf}` of the corresponding transmission :math:`f` and arc :math:`a` combinations. The parameter is given as a percentage, where "0.07" means 7%.

**Transmission Depreciation Period**, :math:`z_{af}`, (a): The parameter :math:`z_{af}` represents the depreciation period of a transmission :math:`f` transferring commodities through an arc :math:`a`. The depreciation period of gives the economic lifetime (more conservative than technical lifetime) of a transmission investment. The unit of this parameter is €/ (MW a). The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the thirteenth column with the header label "depreciation" represents the parameters :math:`z_{af}` of the corresponding transmission :math:`f` and arc :math:`a` combinations.

**Annualised Transmission Capacity Investment Costs**, :math:`k_{af}^\text{inv}`, ``m.transmission.loc[t]['inv-cost'] * m.transmission.loc[t]['annuity-factor']``: The parameter :math:`k_{af}^\text{inv}` represents the annualised investment cost for adding one unit new transmission capacity to a transmission :math:`f` transferring commodities through an arc :math:`a`. This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new transmission capacity of a transmission :math:`f` running through an arc :math:`a`, which is to be given as an input parameter by the user. The unit of this parameter is €/(MW a). The related section for the transmission capacity investment cost in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the sixth column with the header label "inv-cost" represents the transmission capacity investment cost of the corresponding transmission :math:`f` and arc :math:`a` combinations. 

**Annual Transmission Capacity Fixed Costs**, :math:`k_{af}^\text{fix}`, ``m.transmission.loc[t]['fix-cost']``: The parameter :math:`k_{af}^\text{fix}` represents the fix cost per one unit capacity of a transmission :math:`f` transferring commodities through an arc :math:`a`, that is charged annually. The unit of this parameter is €/(MWh a). The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the seventh column with the header label "fix-cost" represents the parameters :math:`k_{af}^\text{fix}` of the corresponding transmission :math:`f` and arc :math:`a` combinations. 

**Transmission Usage Variable Costs**, :math:`k_{af}^\text{var}`, ``m.transmission.loc[t]['var-cost']``: The parameter :math:`k_{af}^\text{var}` represents the variable cost per unit energy, that is transferred with a transmissiom :math:`f` through an arc :math:`a`. The unit of this parameter is €/ MWh. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the eighth column with the header label "var-cost" represents the parameters :math:`k_{af}^\text{var}` of the corresponding transmission :math:`f` and arc :math:`a` combinations.
