Workflow
========

This page a step-by-step explanation on how to get one's own model running. For
the sake of an example, assume you want to investigate whether the state *New
Sealand* with its four islands *Vled Haven*, *Qlyph Archipelago*, *Stryworf
Key*, and *Jepid Island* would benefit by linking their islands' power systems
by costly underground cables to better integrate fluctuating wind power
generation.

Create an input data file
-------------------------

Create a copy of the file ``mimo-example.xlsx`` and give it short, descriptive
name ``newsealand.xlsx``. Open it. 

Go through the sheets, either adding, deleting or modifying rows. Keep the
column titles as they are, because they are required by the model. Each title
has a tooltip that explains the use of the parameter.

Commodity
^^^^^^^^^
Remove the rows with unneeded commodities, here everything except **Gas**,
**Elec**, **Wind**, **CO2**, and **Slack**. *New Sealand* only uses these for
power generation. While **Slack** is not needed, it makes debugging unexpected
model behaviour much easier. Better keep it. Rename the sites to match the
island names. The file should now contain 20 rows, 5 for each island.

Let's assume that *Jepid Island* does not have access to **Gas**, so change the
parameter ``max`` and ``maxperstep`` to 0. Island *Stryworf Key* does have a
gas connection, but the pipeline can only deliver 50 MW worth of Gas power.

These steps result in the following table. The bolded values result from the
assumptions described in the previous paragraphs:

.. csv-table:: Sheet **Commodity**; empty cells correspond to ``=NV()`` (*no value*) fields
   :header-rows: 1
   :stub-columns: 3

    Site,Commodity,Type,price,max,maxperstep
    Jepid Island,CO2,Env,,inf,inf
    Jepid Island,Elec,Demand,,,
    Jepid Island,Gas,Stock,27.0,**0.0**,**0.0**
    Jepid Island,Slack,Stock,999.0,inf,inf
    Jepid Island,Wind,SupIm,,,
    Qlyph Archipelago,CO2,Env,,inf,inf
    Qlyph Archipelago,Elec,Demand,,,
    Qlyph Archipelago,Gas,Stock,27.0,inf,inf
    Qlyph Archipelago,Slack,Stock,999.0,inf,inf
    Qlyph Archipelago,Wind,SupIm,,,
    Stryworf Key,CO2,Env,,inf,inf
    Stryworf Key,Elec,Demand,,,
    Stryworf Key,Gas,Stock,27.0,inf,**50.0**
    Stryworf Key,Slack,Stock,999.0,inf,inf
    Stryworf Key,Wind,SupIm,,,
    Vled Haven,CO2,Env,,inf,inf
    Vled Haven,Elec,Demand,,,
    Vled Haven,Gas,Stock,27.0,inf,inf
    Vled Haven,Slack,Stock,999.0,inf,inf
    Vled Haven,Wind,SupIm,,,

    
    
Process
^^^^^^^

First, remove any process from sheet **Process-Commodity** that consumes or
produces a commodity that is no longer mentioned in sheet **Commodity**. For
*New Sealand*, this leaves us with three processes: 

.. csv-table:: Sheet **Process-Commodity**
   :header-rows: 1
   :stub-columns: 3
   
    Process,Commodity,Direction,ratio
    Gas plant,CO2,Out,0.2
    Gas plant,Elec,Out,0.6
    Gas plant,Gas,In,1.0
    Slack powerplant,CO2,Out,0.0
    Slack powerplant,Elec,Out,1.0
    Slack powerplant,Slack,In,1.0
    Wind park,Elec,Out,1.0
    Wind park,Wind,In,1.0

On the sheet **Process**, create an entry for each process that can be built
at a given site:

.. csv-table:: Sheet **Process**
    :header-rows: 1
    :stub-columns: 2

    Site,Process,inst-cap,cap-lo,cap-up,inv-cost,fix-cost,var-cost,wacc,depreciation
    Jepid Island,Gas plant,25,0,100,450000,6000,1.62,0.07,30
    Jepid Island,Slack powerplant,999,999,999,0,0,100.0,0.07,1
    Jepid Island,Wind park,0,0,60,900000,30000,0.0,0.07,25
    Qlyph Archipelago,Gas plant,0,0,100,450000,6000,1.62,0.07,30
    Qlyph Archipelago,Slack powerplant,999,999,999,0,0,999.0,0.07,1
    Qlyph Archipelago,Wind park,0,0,200,900000,30000,0.0,0.07,25
    Stryworf Key,Gas plant,25,0,100,450000,6000,1.62,0.07,30
    Stryworf Key,Slack powerplant,999,999,999,0,0,100.0,0.07,1
    Stryworf Key,Wind park,0,0,60,900000,30000,0.0,0.07,25
    Vled Haven,Gas plant,0,0,80,450000,6000,1.62,0.07,30
    Vled Haven,Slack powerplant,999,999,999,0,0,100.0,0.07,1
    Vled Haven,Wind park,0,0,50,900000,30000,0.0,0.07,25
    
Something else
    
Transmission
^^^^^^^^^^^^

.. csv-table:: Sheet **Transmission**
    :header-rows: 1
    :stub-columns: 4
    
    Site In,Site Out,Transmission,Commodity,eff,inv-cost,fix-cost,var-cost,inst-cap,cap-lo,cap-up,wacc,depreciation
    Jepid Island,Vled Haven,undersea,Elec,0.85,1100000,30000,0,0,0,inf,0.07,30
    Qlyph Archipelago,Vled Haven,undersea,Elec,0.95,500000,15000,0,0,0,inf,0.07,30
    Stryworf Key,Vled Haven,undersea,Elec,0.9,800000,22500,0,0,0,inf,0.07,30
    Vled Haven,Jepid Island,undersea,Elec,0.85,1100000,30000,0,0,0,inf,0.07,30
    Vled Haven,Qlyph Archipelago,undersea,Elec,0.95,500000,15000,0,0,0,inf,0.07,30
    Vled Haven,Stryworf Key,undersea,Elec,0.9,800000,22500,0,0,0,inf,0.07,30
    
Storage
^^^^^^^

.. csv-table:: Sheet **Storage** (1/2)
    :header-rows: 1
    :stub-columns: 3
    
    Site,Storage,Commodity,inst-cap-c,cap-lo-c,cap-up-c,inst-cap-p,cap-lo-p,cap-up-p,eff-in,eff-out
    Qlyph Archipelago,gravity,Elec,0,0,inf,0,0,inf,0.95,0.95
    
.. csv-table:: Sheet **Storage** (2/2)
    :header-rows: 1
    :stub-columns: 3
    
    Site,Storage,Commodity,inv-cost-p,inv-cost-c,fix-cost-p,fix-cost-c,var-cost-p,var-cost-c,depreciation,wacc,init
    Qlyph Archipelago,gravity,Elec,500000,5,0,0.25,0.02,0,50,0.07,0.05

    
    
Hacks
^^^^^

.. csv-table:: Sheet **Transmission**
    :header-rows: 1
    :stub-columns: 1
    
    Name,Value
    Global CO2 limit,**inf**


Time series
^^^^^^^^^^^

.. csv-table:: Sheet **SupIm**
    :header-rows: 1
    :stub-columns: 1
    
    t,Jepid Island.Wind,Qlyph Archipelago.Wind,Stryworf Key.Wind,Vled Haven.Wind
    0,0.0,0.0,0.0,0.0
    1,0.603,0.935,0.935,0.458
    2,0.585,0.942,0.942,0.453
    3,0.571,0.956,0.956,0.453
    4,0.561,0.956,0.956,0.461
    .,.,.,.,.

    
.. csv-table:: Sheet **Demand**
    :header-rows: 1
    :stub-columns: 1
    
    t,Jepid Island.Elec,Qlyph Archipelago.Elec,Stryworf Key.Elec,Vled Haven.Elec
    0,0,0,0,0
    1,4877,4877,11001,43102
    2,4646,4646,10769,41692
    3,4360,4360,10637,40592
    4,4098,4098,10584,40218
    .,.,.,.,.

Test-drive the input
--------------------

Now that ``newsealand.xlsx`` is ready to go, start ``ipython`` in the
console. Execute the following lines, best by manually typing them in one by
one. *(Hint: use tab completion to avoid typing out function or file names!)*

First, load the data::
    
    >>> import urbs
    >>> input_file = 'newsealand.xlsx'
    >>> data = urbs.read_excel(input_file)
    
``data`` now is a standard Python :class:`dict`. So ``data.keys()`` yields the
worksheet names, while ``data['commodity']`` contains the *Commodity*
worksheet as a :class:`~pandas.DataFrame`. Now create a range::
    
    >>> offset, duration = (3500, 14*24)
    >>> timesteps = range(offset, offset + duration + 1)

    [3500, 3501, ..., 3836]
    
Create a run script
-------------------

