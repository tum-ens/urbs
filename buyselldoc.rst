.. module:: urbs

Demand Side Management Documentation
**********************

This documentation explains the Demand Side Management  feature of urbs. 
With it one can model time variant Demand Side Management Up/Downshift 
from energy exchanges.

Introduction
============

The DSM Up/Downshifts are closely related to commodities ， 
which are given by default in the urbs with their energy content [ MWh ] . 
The size of the modelled market has to be considered small relative to the 
surrounding market. use this feature your excel input file needs an additional 
**Demand Side Management ** sheet with the five parameters containing the 
columns ``delay`` ,``eff`` ,``recov``,``cap-max-do`` and ``cap-max-up``, which 
are set in DSM constraints as technical parameters .For a more detailed 
description of the implementation have a look at the Mathematical Documentation. 

Exemplification
===============

This section contains prototypical scenarios illustrating the system behaviour
with time variant DSM up/downshifts . Electricity can be moved *locally* with 
transmission losses and *temporally* with storage losses.
In this part there is an island as an example named ``Greenland`` , which 
composed of three parts ``Mid``,``North``, and ``South``. Between the three 
parts most of the electricity from ``South`` has to be transported to supply 
``Mid``. The electricity of ``North`` is relative independent of the other two 
parts .

When is electricity DSM upward?

- it is *necessary* to constraint the whole system with DSM Upshifts, if the 
demand is greater than the total output capacity .
- it is *profitable* to constraint the whole system with DSM Upshifts , if the 
demand keeps on increasing till the peak value .

When is electricity DSM downward?

- it is *possible* **and** *profitable* to constraint the whole system with DSM 
Downshifts , if the demand is lesser than the total output capacity **and** keeps
on decreasing ceaselessly


High Maximal Up/Downshift Capacity 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All process, transmission and storage capacities are predetermined and constant.

The following scenario illustrates the energy balance of the ``South`` of ``greenland``.
It has a demand of 50000-100000 MW that is supplied by a 50000 MW photovoltaics plant 
and a 50000 MW wind plant . In addition a 50000 MW transmission cable exports electricity ,
which connects the ``Mid`` of island with the grid of ``South``. Both capacities and 
prices are fix. Because of the  meteorological effects on Photovoltaics plants,the timesteps 
began at the 3000. hour of the year , which was also the beginning of the summer

.. csv-table:: Scenario All Together: Elec in South
    :header-rows: 1
    :stub-columns: 1

    Process,     eff, inst-cap, inst-cap-out, fuel-cost, var-cost, total-var-cost
  Photovoltaics
     plant,      1.00, 50000,   50000,            0,         0,          0 
    Wind plant,  1.00, 100000,  100000,           0,         0,          0
    Purchase,    1.00, 1000,    1000,         **15/45/75**,  0,       15/45/75
    Feed-in,     1.00, 1000,    1000,         **15/45/75**,  0,       15/45/75
	
	
.. csv-table::DSM in South
    :header-rows: 1
    :stub-columns: 1
	
	Site,   Commodity, delay,  eff,  recov, cap-max-do, cap-max-up
	South,    Elec,     16,    0.90    1,     2000        2000

The modelled timespan lasted 7 days with five parameters from DSM sheet in ``greenland 
south.xlsx``. In day 1 the first ten hours the electricity power was at a high level , 
because the supply was much less than the demand. So the DSM began wiht downshifts. But 
the situation will change into opposite direction over time . After the supply exceeded 
the demand the DSM upshifts appeared to take place of downshifts . How much electricity 
can the photovoltaics plants and wind plants generate all depending on the weather 
conditions.The wind plants worked the whole day 24 hours , as long as the wind blow 
strongly enough. But photovoltaics plants generated electricity only in daytime , that 
is why the parameter ``delay`` was set to 16 hours . It just coincided the time in one 
day ,that was covered by sunshine . Before the second day the wind blew srongly enough , 
so that the surplus of wind plant generated electricity was converted into storage .
From the 3. day the wind became weakly , and the electricity of storage had to be taken
out to meet the demand . At the midnight of the 5. day electricity capacity came to 
the lowest point of all , and the output and input kept nearly in balance .  Not only 
the frequency of ``up/downshifts`` , but also the amount of ``up/downshifts`` will 
decrease correspondingly . In the seven days simulation the electricity capacity will
fluctuate relative more stably than it without DSM .
 

.. image:: dsm_greenland/scenario_all_together-Elec-South-sum.png
    :width: 90%
    :align: center



Low Maximal Up/Downshift Capacity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All process, transmission and storage capacities are predetermined and constant.



For the second scenario half of the gas plant is replaced by a coal plant.
Additionally there is a new power limited energy storage with variable storage
costs of 5 €/MWh. The load curve stays the same. Capacities are fix and prices
are varying.

.. csv-table:: Scenario Fix Cap Var Prices
    :header-rows: 1
    :stub-columns: 1

    Process, eff, inst-cap, inst-cap-out, fuel-cost, var-cost, total-var-cost
    Nuclear plant,  0.33, 1500,  500,         5,   5,    10
    **Coal Plant**, 0.40,  625,  250,        11,   5,    16
    Gas plant,      0.50,  500,  250,        25,   5,    30
    **Storage**,    1.00,  125,  125,          , 2.5,     5
    Purchase,       1.00, 1000, 1000, **50-75**,   0, 50-75
    Feed-in,        1.00, 1000, 1000, **35-65**,   0, 35-65

The modelled timespan is 7 days. The buy price varies around the variable costs
of the gas plant. But except for day 3 purchase is only a profitable substitute
for energy from the gas plant at timesteps it is not needed. The sell price
varies around the variable costs of the coal plant. But similar to the buy
price except for day 5 it only allows production of energy for selling at
timesteps it required to cover the demand instead. Producing and storing
energy from the coal plant at timesteps with a low demand limited only by the
storage power capacity is profitable, because it has total variable costs of
45 €/MWh and substitutes ebergy from the gas plant costing 60 €/MWh. At day 5
at noon the sell price exceeds the purchase price 12 hours before by 15 €/MWh.
Even discounting storage costs of 5 €/MWh it would allow infinite arbitrage.
But since the storage capacities are limited the opportunity costs of 15 €/MWh
of substituting energy from the gas plant are higher than the 10 €/MWh profit
margin it is not done.

.. image:: paradiso/Scenario_2_-_Fix_Cap_Var_Prices.png
    :width: 95%
    :align: center

.. note::

    For trial e.g. of the result of greater storage capacities this
    :download:`paradiso_2.xlsx <paradiso/paradiso_2.xlsx>`
    is the input file used for this scenario

	
Low Maximal Up/Downshift Capacity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All process, transmission and storage capacities are variable and determined at
optimal total cost, prices are varying over the modelled timespan.

When is electricity purchased?

- if it is *necessary* that is the demand is greater than the total output
  capacity it is bought at every price
- if it is *profitable* that is if the buy price is lesser than the current
  variable costs of the most expensive needed process *or* including storage
  costs lesser than future variable costs of the most expensive needed process
  *or* it reduces the peak load allowing the capacity investments to be
  reduced in a way that overcompensates the additional costs in summary

When is electricity fed-in?

- if it is *possible* **and** *profitable* that is if the demand is lesser than
  the total output capacity **and** the sell price greater than the cheapest
  currently not needed process *and* does not prevent a total costs decrease by
  reduction of the capacity investments

The next scenario is very similar to the previous one, only that this time all
capacities are initially 0 and investment in new capacities is done in a cost
optimal way. The ascencing order of variable prices is still nuclear plant -
coal plant - gas plan. The ascending order of fix costs, the sum of annual fix
costs ``fix-cost`` and annualized depreciations calculated from the investment
costs ``inv-cost``, weighted average cost of capital ``wacc`` and economic life
time ``depreciation`` is the opposite: gas plant - coal plant - nuclear plant.

.. csv-table:: Scenario Var Cap Var Prices (1)
    :header-rows: 1
    :stub-columns: 1

    Process, eff, **inst-cap**, inst-cap-out, fuel-cost, var-cost, total-var-cost
    Nuclear plant, 0.33, 0, 0,       5,   5,          10
    Coal Plant,    0.40, 0, 0,      11,   5,          16
    Gas plant,     0.50, 0, 0,      25,   5,      **30**
    Storage,       1.00, 0, 0,        , 2.5,           5
    Purchase,      1.00, 0, 0, 150-250,   0, **150-250**
    Feed-in,       1.00, 0, 0,   30-50,   0,       30-50

This scenario should demonstrate a typical composition of power plants. This is
the result of each power plant being cost optimal for a certain range of full
load hours per year leading nuclear energy to cover the base load and gas
energy to cover the peak load. It should also demonstrate, why the purchase
of energy that at the moment exceeds variable costs of power plants can be
economically worthwhile as it reduces peak loads and decreases overall costs.

.. csv-table:: Scenario Var Cap Var Prices (2)
    :header-rows: 1
    :stub-columns: 1

    Process, fix-cost, inv-costs, wacc, depreciation, anf, annuity, total-fix-cost
    Gas plant, 2000, 2250000, 0.07, 30, 0.08, 181319, **183319**
    Purchase,     0,       0, 0.07,   ,     ,      0,      **0**

The variable peak costs of purchased energy of 250 €/MWh clearly exceed the
variable costs of the gas plant of 60 €/MWh. However the necessary transmission
cables for purchasing energy are already needed anyways and do not require
additional fix costs in this scenario while the gas plant has total annual fix
costs of 183.319 €/MW throughput power and 362.639 €/MW output power. Focussing
on one week reducing the needed output capacity by 1MW would save 6.955 €.
As showed by the following diagramms this justifies the additional costs of
250 € - 60 € = 190 € per purchased MWh to an amount that reduces the peak load
by 73 MW.

.. image:: paradiso/Scenario_3_-_Var_Cap_Var_Prices.png
    :width: 95%
    :align: center

.. note::

    For trial e.g. of the result of different storage capacities this
    :download:`paradiso_3.xlsx <paradiso/paradiso_3.xlsx>`
    is the input file used for this scenario.

System support by variable prices
=================================

Making the prices a function proportional to demand and inversely proportional
to intermittent supply is both a good approximation and can demonstrate the
system support of such prices. Especially in case of photovoltaics it limits
the installed capacity to a reasonable amount and/or encourages investment in
storages. This leads to lower peak loads decreasing stress on the grid and a
smoother residual demand increasing stability and autarky. Without variable
prices storages will run a greedy operation strategy instead of peak shaving
and put even more stress on the grid with large power gradients.

.. csv-table:: Scenario Var Cap Sup Im
    :header-rows: 1
    :stub-columns: 1

    Process, eff, inst-cap, inst-cap-out, fuel-cost, var-cost, total-var-cost
    Nuclear plant, 0.33, 0, 0,       5,   5,   10
    Coal Plant,    0.40, 0, 0,      11,   5,   16
    Gas plant,     0.50, 0, 0,      25,   5,   30
    Photovoltaics, 1.00, 0, 0,       0,   0,    0
    Storage,       1.00, 0, 0,       0, 2.5,    5
    Purchase,      1.00, 0, 0, 150-250,   0, ~200
    Feed-in,       1.00, 0, 0,   30-50,   0,  ~40

The price function for the scenario was chosen as:

.. code-block:: excel

    Buy price = 100 + 100 * Demand / mean(Demand) * (1.5 - SupIm)

    Sell price = Buy Price / 5

The result is both more realistic and protective of the grid.

.. image:: paradiso/Scenario_4_-_Var_Cap_Sup_Im.png
    :width: 95%
    :align: center
   
Arbitrage
=========

Arbitrage is the profitable buying and selling of commodities exploiting price
differences. For urbs this can be at one timestep or with storages between two
different timesteps. It can lead the model to be unbounded, if the buy price at
one time step is lower than the sell price or if the price difference between
two different timesteps is large enough to finance storage investments. A
simple solution to avoid that possibility is to add a large finite upper limit
for storage capacities.