Overview model structure
------------------------
urbs is a generator for linear energy system optimization models.

urbs consists of several **model entities**. These are commodities, processes,
transmission and storage. Demand and intermittent commodity supply through are 
modelled through time series datasets.

Commodity
^^^^^^^^^

Commodities are goods that can be generated, stored, transmitted and consumed.
By convention, they are represented by their energy content (in MWh), but can
be changed (to J, kW, t, kg) by simply using different (consistent) units for
all input data. Each commodity must be exactly one of the following six types:

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
  * Buy/Sell: Commodities of these two types can be traded with an external
    market. Similar to Stock commodities they can be limited per hour or per
    year. As opposed to Stock commodities the price at which they can be traded
    is not fixed but follows a user defined time series.    

Stock and environmental commodities have three numeric attributes that
represent their price, total annual and per timestep supply or emission limit,
respectively. Environmental commodities (i.e. CO2) have a maximum allowed
quantity that may be created across the entire modeling horizon.

Commodities are defined over the tuple ``(year, site, commodity, type)``, for
example ``(2020, 'Norway', 'Wind', 'SupIm')`` for wind in Norway with a time
series or  ``(2020, 'Iceland', 'Electricity', 'Demand')`` for an electricity
demand time series in  Iceland.

Process
^^^^^^^
Processes describe conversion technologies from one commodity to another. They
can be visualised like a black box with input(s) (commodity) and output(s)
(commodity). Process input and output ratios are the main technical parameters
for processes. Fixed costs for investment and maintenance (per capacity)
and variable costs for operation (per output) are the economical parameters.

Processes are defined over two tuples. The first tuple
``(year, site, process)`` specifies the location of a given process e.g.
``(2030, 'Iceland', 'Turbine')`` would locate a process ``Turbine`` at site
``Iceland``. The second tuple ``(year, process, commodity, direction)`` then
specifies the inputs and outputs for that process. For example,
``(2030, 'Turbine', 'Geothermal', 'In')`` and
``(2030, 'Turbine', 'Electricity', 'Out')`` describes that the process named
``Turbine`` has a single input ``Geothermal`` and the single output
``Electricity``.


Transmission
^^^^^^^^^^^^
Transmission allows instantaneous transportation of commodities between sites.
It is characterised by an efficiency and costs, just like processes.
Transmission is defined over the tuple
``(year, site in, site out, transmission, commodity)``. For example,
``(2030, 'Iceland', 'Norway', 'Undersea cable', 'Electricity')`` would
represent an undersea cable for electricity between Iceland and Norway.

Storage
^^^^^^^
Storage describes the possibility to deposit a deliberate amount of energy in
the  form of one commodity at one time step; with the purpose of retrieving it
later. Efficiencies for charging/discharging depict losses during input/output.
Storage is characterised by capacities both for energy content (in MWh) and
charge/discharge power (in MW). Both capacities have independent sets of
investment, fixed and variable cost parameters to allow for a very flexible
parametrization of various storage technologies; ranging from batteries to hot
water tanks.

Storage is defined over the tuple ``(year, site, storage, stored commodity)``.
For example, ``(2020, 'Norway', 'Pump storage', 'Electricity')`` represents a
pump storage power plant in Norway that can store and retrieve energy in form
of electricity.


Time series
^^^^^^^^^^^

Demand
""""""
Each combination ``(year, site, demand commodity)`` may have one time series,
describing the aggregate demand (typically MWh) for a commodity within a given
timestep. They are a crucial input parameter, as the whole optimization aims to
satisfy these demands with minimal costs by the given technologies
(process, storage, transmission). An additional feature for demand commodities
is demand side management (DSM) which allows for the shifting of demands in
time.

Intermittent Supply
"""""""""""""""""""
Each combination ``(year, site, supim commodity)`` must be supplied with one
time series, normalized to a maximum value of 1 relative to the installed
capacity of a process using this commodity as input. For example, a wind power
time series should reach value 1, when the wind speed exceeds the modeled wind
turbine's design wind speed is exceeded. This implies that any non-linear
behaviour of intermittent processes can already be incorporated while preparing
this timeseries.

Buy/Sell prices
"""""""""""""""
Each combination ``(year, Buy/sell commodity)`` must be supplied with one
time series which represents the price for purchasing/selling the given
commodities in the given modeled year.

Time variable efficiency
""""""""""""""""""""""""
Each combination ``(year, site, process)`` can optionally be supplied with
one time series which multiplies the outputs of the process with an acoording
factor.
