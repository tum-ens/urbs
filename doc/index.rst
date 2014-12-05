.. urbs documentation master file, created by
   sphinx-quickstart on Wed Sep 10 11:43:04 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
.. module:: urbs

urbs: A linear optimisation model for distributed energy systems
================================================================

:Author: Johannes Dorfner, <johannes.dorfner@tum.de>
:Version: |version|
:Date: |today|
:Copyright:
  This documentation is licensed under a `Creative Commons Attribution 4.0 
  International`__ license.

.. __: http://creativecommons.org/licenses/by/4.0/


Features
--------
* `urbs`_ is a linear programming model for multi-commodity energy systems with 
  a focus on optimal storage sizing and use.
* It finds the minimum cost energy system to satisfy given demand timeseries 
  for possibly multiple commodities (e.g. electricity).
* By default, operates on hourly-spaced timesteps (configurable).
* Thanks to `pandas`_, complex data analysis code is short and extensible.
* The model itself is quite small thanks to relying on the `Coopr`_/`Pyomo`_
  packages.
* urbs includes reporting and plotting functions for rapid scenario 
  development.

Changes
-------

Changes from version 0.2 to 0.3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Processes now support multiple inputs and multiple output commodities.
* As a consequence :func:`plot` now plots commodity balance by processes, not 
  input commodities, as this would be underspecified.
* URBS now supports input files with only a single site; simply delete all
  entries from the 'Transmission' spreadsheet and only use a single site name 
  throughout your input.
* Moved hard-coded 'Global CO2 limit' constraint to dedicated "Hacks"
  spreadsheet, while the constraint is :func:`add_hacks`.
* More docstrings and comments in the main file ``urbs.py``

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
all input data. Each commodity must be exactly one of following four types:

  * Stock: Buyable at any time for a given price. Supply can be limited
    per timestep or for a whole year. Examples are coal, gas, uranium
    or biomass.
  * SupIm: Supply intermittent stands for fluctuating resources like
    solar radiation and wind energy, which are available according to 
    a timeseries of values, which could be derived from weather data.
  * Demand: These commodities have a timeseries for the requirement
    associated and must be provided by output from other process or 
    from storage. Usually, there is only one demand commodity called 
    electricity (abbreviated to Elec or ElecAC), but
  * Env: The special commodity CO2 is of this type and represents the
    amount (in tons) of greenhouse gas emissions from processes. Its
    total amount can be limited, to investigate the effect of policies
    on the.

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
can be visualised like a black box with one input (commodity) and one output
(commodity). A fixed conversion efficiency between input and output is the main
technical parameter. Fixed costs for investment and maintenance (per capacity)
and variable costs for operation (per output) are the economic parameters.

Processes are defined over the tuple ``(site, process, input, output)``. For
example, ``(Iceland, turbine, geothermal, electricity)`` describes a geothermal
plant generating electricity in Iceland.


Transmission
^^^^^^^^^^^^
Transmission allows transporting commodities between sites without delay. It is
characterised by an efficiency and costs, just like processes. Transmission is
defined over the tuple ``(site in, site out, transmission, commodity)``. For
example, ``(Iceland, Norway, undersea cable, electricity)`` would represent an
undersea cable for electricity between Iceland and Norway.

Storage
^^^^^^^
Storage describes the possibility to deposit a deliberate amount of energy in
form of one commodity at one time step, and later retrieving it. Efficiencies
for charging/discharging depict losses during input/output. A self-discharge
term is **not** included at the moment, but could be added trivially (one
column, one modification of the storage state equation). Storage is
characterised by capcities both for energy content (in MWh) and
charge/discharge power (in MW). Both capacities have independent sets of
investment, fixed and variable cost parameters to allow for a very flexible
parametrization of various storage technologies from batteries to hot water
tanks.

Storage is defined over the tuple ``(site, storage, stored commodity)``. For
example, ``(Norway, pump storage, electricity)`` represents a pump storage
power plant in Norway that can store and retrieve energy in form of
electricity.


Timeseries
^^^^^^^^^^

Demand
""""""
Each combination of site and demand commodity may have one timeseries,
describing the (average) power demand (MWh/h) per timestep. They are a crucial
input parameter, as the whole optimisation aims to satisfy these demands with
minimal costs from the given technologies (process, storage, transmission).

Intermittent Supply
"""""""""""""""""""
Each combination ``(site, supim commodity)`` must be supplied with one
timeseries, normalised to a maximum value of 1 relative to the installed
capacity of a process using this commodity as input. For eample, a wind power
timeseries should reach value 1, when the wind speed exceeds the modelled wind
turbine's design wind speed is exceeded. This implies that any non-linear
behaviour of intermittent processes can already be incorporated while preparing
this timeseries.


Contents
--------

This documentation contains the following pages:

.. toctree::
   :maxdepth: 2

   tutorial
   report
   api


Screenshots
-----------

Motivational result images:

.. image:: img/plot.*
   :width: 66%
   :align: center
.. image:: img/comp.*
   :width: 66%
   :align: center
   

Dependencies
------------

* `coopr`_ interface to optimisation solvers (CPLEX, GLPK, Gurobi, ...).
  At least one supported solver by coopr must be installed.
* `matplotlib`_ for plotting
* `pandas`_ for input and result data handling, report generation 
* `pyomo`_ for the model equations

   
.. _coopr: https://software.sandia.gov/trac/coopr
.. _matplotlib: http://matplotlib.org
.. _pandas: https://pandas.pydata.org
.. _pyomo: https://software.sandia.gov/trac/coopr/wiki/Pyomo
.. _urbs: https://github.com/tum-ens/urbs

