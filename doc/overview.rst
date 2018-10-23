Overview
--------

urbs consists of several **model entities**. These are commodities, processes,
transmission and storage. Demand and intermittent commodity supply through are 
modelled through time series datasets.

Commodity
^^^^^^^^^

Commodities are goods that can be generated, stored, transmitted and consumed.
By convention, they are represented by their energy content (in MWh), but can
be changed (to J, kW, t, kg) by simply using different (consistent) units for
all input data. Each commodity must be exactly one of the following four types:

  * Stock: Buyable at any time for a given price. Supply can be limited
    per timestep or for a whole year. Examples are coal, gas, uranium
    or biomass.
  * SupIm: Supply intermittent stands for fluctuating resources like
    solar radiation and wind energy, which are available according to 
    a timeseries of values, which could be derived from weather data.
  * Demand: These commodities have a timeseries for the requirement
    associated and must be provided by output from other process or 
    from storage. Usually, there is only one demand commodity called 
    electricity (abbreviated to Elec), but multiple (e.g. electricity, space 
    heating, process heat, space cooling) demands can be specified.
  * Env: The special commodity CO2 is of this type and represents the
    amount (in tons) of greenhouse gas emissions from processes. Its
    total amount can be limited, to investigate the effect of policies
    on the model.

Stock commodities have three numeric attributes that represent their price,
total annual and per timestep supply. Environmental commodities (i.e. CO2) have
a maximum allowed quantity that may be created.

Commodities are defined over the tuple ``(site, commodity, type)``, for example
``(Norway, wind, SupIm)`` for wind in Norway with a time series or 
``(Iceland, electricity, Demand)`` for an electricity demand time series in 
Iceland.

Process
^^^^^^^
Processes describe conversion technologies from one commodity to another. They
can be visualised like a black box with input(s) (commodity) and output(s)
(commodity). Process input and output ratios are the main technical parameters
for processes. Fixed costs for investment and maintenance (per capacity)
and variable costs for operation (per output) are the economical parameters.

Processes are defined over two tuples. The first tuple ``(site, process)``
specifies the location of a given process e.g. ``(Iceland, turbine)`` would
locate a process ``turbine`` at site ``Iceland``. The second tuple ``(process,
commodity, direction)`` then specifies the inputs and outputs for that process.
For example, ``(turbine, geothermal, In)`` and ``(turbine, electricity, Out)``
describes that the process named ``turbine`` has a single input ``geothermal``
and the single output ``electricity``.


Transmission
^^^^^^^^^^^^
Transmission allows instantaneous transportation of commodities between sites. It is
characterised by an efficiency and costs, just like processes. Transmission is
defined over the tuple ``(site in, site out, transmission, commodity)``. For
example, ``(Iceland, Norway, undersea cable, electricity)`` would represent an
undersea cable for electricity between Iceland and Norway.

Storage
^^^^^^^
Storage describes the possibility to deposit a deliberate amount of energy in the 
form of one commodity at one time step; with the purpose of retrieving it later. Efficiencies
for charging/discharging depict losses during input/output. A self-discharge
term is **not** included at the moment, but could be added trivially (one
column, one modification of the storage state equation). Storage is
characterised by capacities both for energy content (in MWh) and
charge/discharge power (in MW). Both capacities have independent sets of
investment, fixed and variable cost parameters to allow for a very flexible
parametrization of various storage technologies; ranging from batteries to hot water
tanks.

Storage is defined over the tuple ``(site, storage, stored commodity)``. For
example, ``(Norway, pump storage, electricity)`` represents a pump storage
power plant in Norway that can store and retrieve energy in form of
electricity.


Timeseries
^^^^^^^^^^

Demand
""""""
Each combination ``(site, demand commodity)`` may have one timeseries,
describing the aggregate demand (typically MWh) for a commodity within a given timestep. They are a crucial
input parameter, as the whole optimisation aims to satisfy these demands with
minimal costs by the given technologies (process, storage, transmission).

Intermittent Supply
"""""""""""""""""""
Each combination ``(site, supim commodity)`` must be supplied with one
timeseries, normalised to a maximum value of 1 relative to the installed
capacity of a process using this commodity as input. For example, a wind power
timeseries should reach value 1, when the wind speed exceeds the modelled wind
turbine's design wind speed is exceeded. This implies that any non-linear
behaviour of intermittent processes can already be incorporated while preparing
this timeseries.
