Workflow
========

This is a brief recipe to get one's own model running. For the sake of an
example, assume you want to investigate whether the state *New Sealand* with
its four islands *Vled Haven*, *Qlyph Archipelago*, *Stryworf Key*, and 
*Jepid Island* would benefit by linking their islands' power systems by costly
underground cables to better integrate fluctuating wind power generation.

Which data is needed?
---------------------


What to do
----------

1. Create a copy of the file ``mimo-example.xlsx`` and give it short,
   descriptive name ``newsealand.xlsx``. Open it.
2. Go through the sheets, either adding, deleting or modifying rows. Keep the
   column titles as they are, because they are required by the model. Each
   title has a tooltip that explains the use of the parameter.

   
Commodity
^^^^^^^^^
Remove the rows with unneeded commodities, here everything except **Gas**,
**Elec**, **Wind**, **CO2**, and **Slack**. *New Sealand* only uses these for
power generation. While **Slack** is not needed, it makes debugging unexpected
model behaviour much easier. Better keep it. Rename the sites to match the
island names. The file should now contain 20 rows, 5 for each island.

Let's assume that *Jepid Island* does not have access to **Gas**, so change the
parameter ``max`` and ``maxperstep`` to 0. *Stryworf Key* does have a gas
connection, but the pipeline can only deliver 5 MW

.. csv-table:: Sheet `Commodity`
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
    Stryworf Key,Gas,Stock,27.0,inf,**5.0**
    Stryworf Key,Slack,Stock,999.0,inf,inf
    Stryworf Key,Wind,SupIm,,,
    Vled Haven,CO2,Env,,inf,inf
    Vled Haven,Elec,Demand,,,
    Vled Haven,Gas,Stock,27.0,inf,inf
    Vled Haven,Slack,Stock,999.0,inf,inf
    Vled Haven,Wind,SupIm,,,

    
    
Process
^^^^^^^
Something else
    
Transmission
^^^^^^^^^^^^

More
    
Storage
^^^^^^^
Moreover
    

