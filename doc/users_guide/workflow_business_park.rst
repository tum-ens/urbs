.. module:: urbs

Business park example explained
===============================
In this part the input files of the standard example **Business park** will be
explained in detail.

Task
^^^^
The task we set ourselves here is to build our own intertemporal model. The
task is the following:

The technical staff of a business park management company wants you to find the
cost optimal energy system for their business park. You are to provide this
with increasingly stricter CO2 emission limits over time. As the company expects
to operate this business park for a long time still, they want you to help
developing a long term strategy how to transform the energy supply
infrastructure of the business park in cost optimal way over the time frame of
3 decades. The company also expects that the business park will be increasingly
closely interacting with the neighboring small city and its energy system. All
current and expected demand curves are given to you. You also have full access
to regional climate models and all relevant parameters for the energy conversion
units relevant for your problem. 

Input files
^^^^^^^^^^^
The task set is intertemporal. That is we need to provide several .xlsx input
files, one for each modeled year. Here we chose to use 3 files representing
modeled years 10 years apart. For the given task this seems to be a good
compromise between accuracy and computational effort. The files are named
``2020.xlsx``, ``2030.xlsx`` and ``2040.xlsx`` and sit in the folder
``Input (Business park)``. We will now proceed with a detailed walkthrough of
the individual files.  

Sheet Global
~~~~~~~~~~~~
Here you can now specify the global properties needed for the modeling of the
energy system. Note that this sheet has different entries for the different
input files:

* **Support timeframe** (All files): Give the value for the modeled year here.
* **Discount rate** (Only first file): This value gives the discount rate that
  is used for intertemporal planning. It stands for the annual devaluation of
  money across the modeling horizon.
  In the example a discount rate of *3 %* is used.
  
  
* **CO2 limit** (All files ): This parameter limits the CO2 emissions across
  all sites within one modeled year, the *CO2 budget* sets a cap on the total
  emissions across all sites in the entire modeling horizon. If no restriction
  is desired enter 'inf' here.
  In the example increasingly strict values for the CO2 limit are used for the
  different modeled years, from *60 kt/a* in 2020 over *45 kt/a* in 2030 to
  *30 kt/a* in 2040. This represents the will of the company to achieve
  milestones in the emission reductions while gradually changing their energy
  infrastructure.    
  
* **CO2 budget** (Only first file): While the *CO2 limit* specified for each
  year limits the CO2 emissions across all sites within one modeled year, the
  *CO2 budget* sets a cap on the total emissions across all sites in the entire
  modeling horizon. If no restriction is desired enter 'inf' here. The
  *CO2 budget* is only active when the *Objective* is set to its default value
  'cost'.
  In the example a CO2 budget of *1.2 Mt* is used. This budget imposes a
  stricter limit on the emissions than the combined targets for the individual
  modeled year. In terms of climate impact his limit is the more important one.
  For all CO2 limitations the business park and the city are considered
  together since in the assumed case the company running the business park
  wants to act as an electricity provider for the city as well.
  
* **Cost budget** (Only first file): With this parameter a limit on the total
  system cost over the entire modeling horizon can be set. If no restriction is
  desired enter 'inf' here. The *Cost budget* is only active when the
  *Objective* is set to the value 'CO2'.
  In the example no CO2 optimization is considered this parameter is thus set
  to infinity.
  
* **Last year weight** (Only last file): In intertemporal modeling each modeled
  year is repeated until the next modeled year is reached. This is done ba
  assigning a weight to the costs accrued in each of the modeled years. For the
  last modeled year the number of repetitions has to be set by the user here,
  where a high number leads to a stronger weighting of the last modeled year,
  i.e. of the final energy system configuration.
  In the example the last year has a weight of *10 years*. This means that it
  will be equally weighted identically to the others which always represent all
  years until the ext modeled year.

Sheet Site
~~~~~~~~~~
In this sheet you can specify the site names and also the area of each site.
The line index represents all the sites. The only site specific property to be
set is then:

* **Area**: Specifies the usable area for processes in the given site. The area
  does not need to be the total floor area. It is used to limit the use of area
  consuming processes and can be seen as, e.g., the roof area for solar
  technologies.
  
  In the example two sites 'Business park' and 'City' are given. These and
  their respective areas do not change. The areas here represent roof areas for
  PV and the city has more of this.

Sheet Commodity
~~~~~~~~~~~~~~~
In this sheet all the commodities, i.e. energy or material carriers, are
specified. The line index completes a commodity tuple, i.e. a connection
``(year, site, commodity, type)``. There are three properties to be specified
for all commodities of types **Stock**, **Buy**, **Sell** and
**Environmental**.

* **Price** denotes the cost of taking one unit of energy from the stock for
  **Stock** commodities or emitting one unit of **Environmental**. For **Buy**
  and **Sell** commodities this is not directly a price but a multiplier for
  the time series given in the sheet 'Buy-Sell-Price'. It is thus typically set
  to 1 for these commodity types.
* **max** limits the total amount of the commodity that may be bought, sold or
  emitted per year.
* **maxperhaour** limits the total amount of the commodity that may be bought,
  sold or emitted per hour (not timestep but really hour).

In the site 'Business park' there are 9 commodities defined:

* *Solar (West/East)* is of type **SupIm** and represents the capacity factor
  timeseries of solar panels mounted with a given inclination (10° both West
  and East).
* *Grid electricity* is of type **Buy** and represents the electricity price as
  bought from the regional grid operator. The business park pays constant price
  over the year. In the site 'City' this price is different and hence a
  multiplier is used to increase the wholesale price for households.
* *Gas* is of type **Stock** and represents the price for the purchase of
  natural gas from the local provider.
* *Electricity*, *Heat* and *Cooling* are of type **Demand** and represent the
  hourly demand for these three energy carriers.
* *Intermediate* is of type **Stock**. However, it is not possible to buy this
  commodity from the stock. It is introduced to allow for a flexible operation
  of a combined heat and power (CHP) plant according to section
  :ref:`nuggets`.
* *Intermediate low temperature* is of type **Stock**. It is also not buyable
  from an external source. Its purpose is to make the operation of the cooling
  processes more realistic by preventing the storage of high temperature
  cooling from ambient air cooling in cold storages.

In site 'City' one additional commodity, *Operation decentral units* is
introduced. It is of type **SupIm** and makes sure that the different heating
technologies usable in the site all operate at a fixed share of the total heat
demand. This is necessary, since these technologies are build up in a decentral
way in the individual houses. The idea behind this is laid out in section
:ref:`nuggets`.

Sheet Process
~~~~~~~~~~~~~
In this sheet the energy conversion technologies are described. Here only the
economical and some general technical parameters are set. The interactions with
the commodities are introduced in the next sheet. The following parameters are
set here for the processes:

* **Installed capacity (MW) (Only first file)** gives the capacity of the
  process that is already istalled at the start of the modeling horizon.
* **Lifetime of installed capacity (years) (Only first file)** gives the rest
  lifetime of the installed processes in years. A process can be used in a
  modeled year *y* still if the lifetime plus the first modeled year exceeds
  the next year *y+1*.
* **Minimum capacity (MW)** denotes a capacity target that has to be met by the
  process in a given modeled year. This means that the system will build at
  least this capacity.
* **Maximum capacity (MW)** restricts the capacity that can be built to the
  specified value.
* **Maximum power gradient (1/h)** restricts the ramping of process operational
  states, i.e. the change in the throughput variable. The value gives the
  fraction of the total capacity that can be changed in one hour. A value of
  *1* thus restricts the change from idle to full operational state
  (or vice versa) to at least a duration of one hour.
* **Minimum load fraction** gives a lower limit for the operational state of a
  process as a fraction of the total capacity. It is only relevant for
  processes where part-load behavior is modeled. A value here is only active
  when 'Ratio-Min' is numerical for at least one input commodity.
* **Investment cost (€/MW)** denotes the capacity specific investment costs for
  the process. You should give the book value here. The program will then
  translate this into the correct total, discounted cost within the model
  horizon.
* **Annual fix costs (€/MW)** represent the amount of money that has to be
  spent annually for the operation of a process capacity. They can represent,
  e.g., labour costs or calendaric ageing costs.
* **Variable costs (€/MWh)** are linked to the operation of a process and are
  to be paid for each unit of throughput through the process. They can
  represent anything from usage ageing to taxes.
* **Weighted average cost of capital** denotes the interest rate or expected
  return on investment with which the investor responsible for the energy
  system calculates.
* **Depreciation period** denotes both the economical and technical lifetime of
  all units in the system. It thus determines two things: the total costs of a
  given investment and the end of operational time for all units in the energy
  system modeled.
* **Area use per capcacity (m^2/MW)** specifies the physical area a given
  process takes up at the site it is built. This can be used, e.g. to
  restrict the capacity of solar technologies by a total maximal roof area. The
  restricting area is defined in sheet 'Site'.

While the details of the processes will be discussed in more detail in the next
section one mention on the processes 'Load dump' and 'Slack' is made here.
These processes are not introduced to represent real units but help making
operation more realistic and error fixing more easy. A load dump process just
destroys energy which is sometimes necessary in order to prevent the system from
doing unrealistic gymnastics to keep the vertex rule. A 'Slack' process can
create a demand commodity out of thin air for an extremely high price. It thus
indicates when the problem is not feasible, making error fixing much easier.
Both should typically be included in models.

Sheet Process-Commodity
~~~~~~~~~~~~~~~~~~~~~~~
In this sheet the technical properties of processes are set. These properties
are given for each process independent of the site where the process is
located. You need to make an imput for all the processes defined in the
'Process' sheet. The line index is a tuple ``(process, commodity, direction)``, 
where 'Direction' has to be set as either 'In' or 'Out' and specifies wether a
commodity is an in- or an output of a given process. Under the column 'ratio'
you then have to specify the commodity in- or outflows per installed capacity
and time step at the point of full operation. The efficiency of the process for
the conversion of one input into one output commodity is then given by the
ratio of the chosen values. For example, in the modeled year 2020 the process
'Gas engine power plant' converts 2.2 MWh of 'Gas' into one MWh each of
'Electricity' and 'Heat' while emitting 0.2 t of 'CO2'. This corresponds to an
efficiency of 0.45 for 'Heat' and 'Electricity' conversion.

If a process has a more complex part load behavior, where, e.g., the efficiency
changes this can be partly captured by setting values in the 'ratio-min'
column. These specify the commodity flows at the minimum operation point
specified in the 'Process' sheet under 'min-fract'. The process will then no
longer be allowed to turn off so use this carefully. In the present case this
behavior is set for the combined heat and power plant 'CHP (Operational state)'
only.

There are a few special settings made in the example. First, the CHP plant is
divided into three parts. The idea behind this is described in :ref:`nuggets`.
The two processes 'CHP (Electricity driven)' and 'CHP (Heat driven)' specify
the commodity flows in the two extreme operational states. The system can then
chose all linear interpolations between both states by guiding the commodity
flow of 'Intermediate' through the two processes in the desired ratio. Second,
the cooling technologies are implemented in a two stage way. The reason for
this is that the process 'Ambient air cooling' is extremely efficient and
extremely cheap. While it can only be used in certain time intervals (see
explanation of 'TimeVarEff' further below), its output could nevertheless be
stored otherwise which is not realistic. The introduction of commodity
'Intermediate low temperature' prevents this. It is the output of all the
cooling technologies except for 'Ambient air cooling' and is also the one that
can be stored (see below).

Sheet Transmission
~~~~~~~~~~~~~~~~~~
In this sheet the parameters for transmission lines between sites are specified.
The line index is part of a transmission tuple ``(Site In, Site Out,
Transmission, Commodity)``. Note that for each transmission the inverse one
with the same properties should also be given. The parameters are the
following:

* **Efficiency (1)** specifies the transport efficiency of the transmission
  line.
* **Lifetime of installed capacity (years) (Only first file)** gives the rest
  lifetime of the installed transmission lines in years. A transmission line
  can be used in a modeled year *y* still if the lifetime plus the first
  modeled year exceeds the next year *y+1*.
* **Investment cost (€/MW)** denotes the capacity specific investment costs for
  the transmission line. You should give the book value here. The program will
  then translate this into the correct total, discounted cost within the model
  horizon.
* **Annual fix costs (€/MW)** represent the amount of money that has
  to be spent annually for the operation of a transmission capacity. They can
  represent, e.g., labour costs or calendaric ageing costs.
* **Variable costs (€/MWh)** are linked to the operation of a given
  transmission line.
* **Installed capacity (MW) (Only first file)** gives the transmission capacity
  of transmission lines already installed at the start of the modeling horizon.
* **Minimum capacity (MW)** denotes a transmission capacity target that has
  to be met by the transmission lines in a given modeled year. This means that
  the system will build at least this transmission capacity.
* **Maximum capacity (MW)** restricts the transmission capacity that can be
  built to the specified value.
* **Weighted average cost of capital** denotes the interest rate or expected
  return on investment with which the investor responsible for the energy
  system calculates.
* **Depreciation period** denotes both the economical and technical lifetime of
  all units in the system. It thus determines two things: the total costs of a
  given investment and the end of operational time for all units in the energy
  system modeled.

In the example the only commodity that can be transported from one site to the
other is electricity.

Sheet Storage
~~~~~~~~~~~~~
In this sheet the parameters for storage units are specified. Each storage unit
is indexed with parts of a storage tuple ``(storage, commodity)``. In storages
charging/discharging power and the capacity are sized independently. The
parameters specifying the storage properties are the following:

* **Installed capacity (MWh) (Only first file)** gives the storage capacity of
  storages already installed at the start of the modeling horizon.
* **Installed storage power (MW) (Only first file)** gives the
  charging/discharging power of storages already installed at the start of the
  modeling horizon.
* **Lifetime of installed capacity (years) (Only first file)** gives the rest
  lifetime of the installed storages in years. A storage can be used in a
  modeled year *y* still if the lifetime plus the first modeled year exceeds
  the next year *y+1*.
* **Minimum storage capacity (MWh)** denotes a storage capacity target that has
  to be met by the storage in a given modeled year. This means that the system
  will build at least this capacity.
* **Maximum storage capacity (MWh)** restricts the storage capacity that can be
  built to the specified value.
* **Minimum storage power (MW)** denotes a storage charging/discharging power
  target that has to be met by the storage in a given modeled year. This means
  that the system will build at least this power.
* **Maximum storage power (MW)** restricts the storage charging/discharging
  that can be built to the specified value.
* **Efficiency input (1)** specifies the charging efficiency of the storage.
* **Efficiency output (1)** specifies the discharging efficiency of the
  storage.
* **Investment cost capacity (€/MWh)** denotes the storage capacity specific
  investment costs for the storage. You should give the book value here. The
  program will then translate this into the correct total, discounted cost
  within the model horizon.
* **Investment cost power (€/MW)** denotes the storage charging/discharging
  power specific investment costs for the storage. You should give the book
  value here. The program will then translate this into the correct total,
  discounted cost within the model horizon.
* **Annual fix costs capacity (€/MWh)** represent the amount of money that has
  to be spent annually for the operation of a storage capacity. They can
  represent, e.g., labour costs or calendaric ageing costs.
* **Annual fix costs power (€/MW)** represent the amount of money that has to
  be spent annually for the operation of a storage power. They can represent,
  e.g., labour costs or calendaric ageing costs.
* **Variable costs capacity (€/MWh)** are linked to the operation of a given
  storage state, i.e. they lead to costs whenever a storage has a non-zero
  state of charge. These costs should typically set to zero but can be used to
  manipulate the storage duration or model state-of-charge dependent ageing.
* **Variable costs power (€/MWh)** are linked to the charging and discharging
  of a storage. Each unit of commodity leaving the storage requires the payment
  of these costs.
* **Weighted average cost of capital** denotes the interest rate or expected
  return on investment with which the investor responsible for the energy
  system calculates.
* **Depreciation period** denotes both the economical and technical lifetime of
  all units in the system. It thus determines two things: the total costs of a
  given investment and the end of operational time for all units in the energy
  system modeled.
* **Initial storage state** can be used to set the state of charge of a storages
  in the beginning of the modeling time steps. If *nan* is given this value is
  an optimization variable. In any case the storage content in the end is the
  same as in the beginning to avoid windfall profits from simply discharging a
  storage.
* **Discharge** gives the hourly discharge of a storage. Over time, when no
  charging or discharging occurs, the storage content will decrease
  exponentially.

In the example there are no storages in site 'City' and there is a storage for
each demand in site 'Business park'. The commodity 'Cooling' is not directly
storable to avoid an unrealistic behavior for the process 'Ambient air cooling'
as was discussed above in the 'Process-Commodity' section.

Sheets Demand, SupIm, Buy/Sell price
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In these sheets the time series for all the demands, capacity factors of
processes using commodities of type 'SupIm' and market prices for 'Buy' and
'Sell' commodities are to be specified. For the former two the syntax
'site.commodity' has to be used as a column index to specify the corresponding
tuple.

Sheet TimeVarEff
~~~~~~~~~~~~~~~~
In this sheet a time series for the output of processes can be given. This is
always useful, when processes are somehow dependent on external parameters. The
syntax to be used to specify which process is to be addressed by this is
'site.process'. In the present example, this is used for the process
'Ambient air cooling' which has a boolean 'TimeVarEff' curve giving the value
'1' for temperatures below a threshold and '0' else.

This concludes the input generation. Of course all parameters have to be set
in all the input sheets.

Run script
^^^^^^^^^^
To run the example you can make a copy of the file ``runme.py`` calling it,
e.g., ``run_BP.py`` in the same folder. You now just have to make 3
modifications. First, replace the report tuples by:
::

    report_tuples = [
        (2020, 'Business park', 'Electricity'),
        (2020, 'Business park', 'Heat'),
        (2020, 'Business park', 'Cooling'),
        (2020, 'Business park', 'Intermediate low temperature'),
        (2020, 'Business park', 'CO2'),
        (2030, 'Business park', 'Electricity'),
        (2030, 'Business park', 'Heat'),
        (2030, 'Business park', 'Cooling'),
        (2030, 'Business park', 'Intermediate low temperature'),
        (2030, 'Business park', 'CO2'),
        (2040, 'Business park', 'Electricity'),
        (2040, 'Business park', 'Heat'),
        (2040, 'Business park', 'Cooling'),
        (2040, 'Business park', 'Intermediate low temperature'),
        (2040, 'Business park', 'CO2'),
        (2020, 'City', 'Electricity'),
        (2020, 'City', 'Heat'),
        (2020, 'City', 'CO2'),
        (2030, 'City', 'Electricity'),
        (2030, 'City', 'Heat'),
        (2030, 'City', 'CO2'),
        (2040, 'City', 'Electricity'),
        (2040, 'City', 'Heat'),
        (2040, 'City', 'CO2'),
        (2020, ['Business park', 'City'], 'Electricity'),
        (2020, ['Business park', 'City'], 'Heat'),
        (2020, ['Business park', 'City'], 'CO2'),
        (2030, ['Business park', 'City'], 'Electricity'),
        (2030, ['Business park', 'City'], 'Heat'),
        (2030, ['Business park', 'City'], 'CO2'),
        (2040, ['Business park', 'City'], 'Electricity'),
        (2040, ['Business park', 'City'], 'Heat')
        (2040, ['Business park', 'City'], 'CO2'),
        ]
    
    # optional: define names for sites in report_tuples
    report_sites_name = {('Business park', 'City'): 'Together'}

and the plot tuples by:
::

    plot_tuples = [
        (2020, 'Business park', 'Electricity'),
        (2020, 'Business park', 'Heat'),
        (2020, 'Business park', 'Cooling'),
        (2020, 'Business park', 'Intermediate low temperature'),
        (2020, 'Business park', 'CO2'),
        (2030, 'Business park', 'Electricity'),
        (2030, 'Business park', 'Heat'),
        (2030, 'Business park', 'Cooling'),
        (2030, 'Business park', 'Intermediate low temperature'),
        (2030, 'Business park', 'CO2'),
        (2040, 'Business park', 'Electricity'),
        (2040, 'Business park', 'Heat'),
        (2040, 'Business park', 'Cooling'),
        (2040, 'Business park', 'Intermediate low temperature'),
        (2040, 'Business park', 'CO2'),
        (2020, 'City', 'Electricity'),
        (2020, 'City', 'Heat'),
        (2020, 'City', 'CO2'),
        (2030, 'City', 'Electricity'),
        (2030, 'City', 'Heat'),
        (2030, 'City', 'CO2'),
        (2040, 'City', 'Electricity'),
        (2040, 'City', 'Heat'),
        (2040, 'City', 'CO2'),
        (2020, ['Business park', 'City'], 'Electricity'),
        (2020, ['Business park', 'City'], 'Heat'),
        (2020, ['Business park', 'City'], 'CO2'),
        (2030, ['Business park', 'City'], 'Electricity'),
        (2030, ['Business park', 'City'], 'Heat'),
        (2030, ['Business park', 'City'], 'CO2'),
        (2040, ['Business park', 'City'], 'Electricity'),
        (2040, ['Business park', 'City'], 'Heat')
        (2040, ['Business park', 'City'], 'CO2'),
        ]
    
    # optional: define names for sites in plot_tuples
    plot_sites_name = {('Business park', 'City'): 'Together'}

In this way you get a meaningful output for the optimization runs. Second, the
scenarios are made for the other example and are as such no longer usable
here. Thus only the base scenario is to be run. Change the list scenario to the
following:
::

    scenarios = [
                 urbs.scenario_base
                ]

Having completed all these steps you can execute the code.