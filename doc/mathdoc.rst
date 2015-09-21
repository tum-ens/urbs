Mathematical Documentation
**************************

Introduction
============
In this Section, **mathematical description** of the model will be explained. This includes listing and describing all relevant sets, parameters, variables
and constraints using mathematical notation together with corresponding code fragment. 

Sets
====

Since urbs is a linear optimization model with many objects (e.g variables, parameters), it is reasonable to use
sets to define the groups of objects. With the usage of sets, many facilities are provided, such as
understanding the main concepts of the model. Many objects are represented by various sets,
therefore sets can be easily used to check whether some object has a specific characteristic or not.
Additionally sets are useful to define a hierarchy of objects. 
Mathematical notation of sets are expressed with uppercase letters, and their members are usually expressed with the same
lowercase letters. Main sets, tuple sets and subsets will be introduced in this respective order.

.. table:: *Table: Model Sets*
	
	======================== =====================
	Set                      Description
	======================== =====================
	:math:`t \in T`          Timesteps
	:math:`t \in T_\text{m}` Modelled Timesteps
	:math:`v \in V`          Sites
	:math:`c \in C`          Commodities
	:math:`q \in Q`          Commodity Types
	:math:`p \in P`          Processes
	:math:`s \in S`          Storages
	:math:`f \in F`          Transmissions
	:math:`r \in R`          Cost Types
	======================== =====================

Time Steps
^^^^^^^^^^

The model urbs is considered to observe a energy system model and calculate the optimal solution within a limited span of time.
This limited span of time is viewed as a discrete variable, which means values of variables are viewed as occurring only at distinct timesteps.
The set of **time steps** :math:`T = \{t_0,\dots,t_N\}` for :math:`N` in :math:`\mathbb{N}`
represents Time. This set contains :math:`N+1` sequential time steps with equal spaces.
Each time step represents another point in time. At the initialisation of the model this set
is fixed by the user by setting the variable ``timesteps`` in script ``runme.py``.
Duration of space between timesteps :math:`\Delta t = t_{x+1} - t_x`, length of simulation :math:`\Delta t \cdot N`,
time interval :math:`[t_0,t_N]` and  can be fixed to satisfy the needs of the user.
In code this set is defined by the set ``t`` and initialized by the section:

::

    m.t = pyomo.Set(
        initialize=m.timesteps,
        ordered=True,
        doc='Set of timesteps')
		
Where;

* `Initialize`: A function that receives the set indices and model to return the value of that set element, initializes the set with data.
* `Ordered`: A boolean value that indicates whether the set is ordered.
* `Doc`: A string describing the set.

Modelled Timesteps
^^^^^^^^^^^^^^^^^^

The Set, **modelled timesteps**, is a subset of the time steps set. The difference between modelled
timesteps set and the timesteps set is that the initial timestep :math:`t_0` is not included. All other
all other features of the set time steps also apply to the set of modelled timesteps. This set
is later required to facilitate the definition of the storage state equation.
In script ``urbs.py`` this set is defined by the set ``tm`` and initialized by the code fragment:

::

    m.tm = pyomo.Set(
        within=m.t,
        initialize=m.timesteps[1:],
        ordered=True,
        doc='Set of modelled timesteps')
		
Where;

* `Within`: The option that supports the validation of a set array.
* ``m.timesteps[1:]`` represents the timesteps set starting from the second element, excluding the first timestep :math:`t_0`

Sites
^^^^^

**Sites** are represented by the set :math:`V`. A Site :math:`v` can be any distinct location, a place of
settlement or activity (e.g `process`, `transmission`, `storage`).A site is for example an individual
building, region, country or even continent. Sites can be imagined as nodes(vertices) on a graph of locations,
connected by edges. Index of this set are the descriptions of the Sites.
(e.g north, middle, south).In script ``urbs.py`` this set is defined by ``sit`` and initialized by the code fragment:

::

    m.sit = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Site').unique(),
        doc='Set of sites')
		
Commodities
^^^^^^^^^^^

As explained in the Overview section, **commodities** are goods that can be
generated, stored, transmitted or consumed. The set of Commodities represents all goods that
are relevant to the modelled energy system, such as all energy carriers, inputs, outputs,
intermediate substances. (e.g Coal, CO2, Electric, Wind) By default, commodities are given by their
energy content (MWh). Usage of some commodities are limited by a maximum value or maximum value
per timestep due to their availability or restrictions, also some commodities have a price that
needs to be compensated..(e.g coal, wind, solar).In script ``urbs.py`` this set is defined by ``com`` 
and initialized by the code fragment:

::

    m.com = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Commodity').unique(),
        doc='Set of commodities')
		
Commodity Types
^^^^^^^^^^^^^^^
Commodities differ in their usage purposes, consequently **commodity types** are introduced to subdivide commodities by their features.
These Types are ``SupIm``, ``Stock``, ``Demand``, ``Env``, ``Buy``, ``Sell``. In script ``urbs.py`` this set is defined as ``com_type`` 
and initialized by the code fragment:

::

    m.com_type = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Type').unique(),
        doc='Set of commodity types')
		

Processes
^^^^^^^^^

One of the most important elements of an energy system is the **process**. A process :math:`p` can be defined by
the action of changing one or more forms of energy to others. In our modelled energy system,
processes convert input commodities into output commodities. Process technologies are represented by
the set processes :math:`P`. Different processes technologies have fixed input and output commodities. These input and output commodities
can be either single or multiple regardless of each other. Some example members of this set can be:
`Wind Turbine`,`Gas Plant`, `Photovoltaics`.
In script ``urbs.py`` this set is defined as ``pro`` and initialized by the code fragment:

::

    m.pro = pyomo.Set(
        initialize=m.process.index.get_level_values('Process').unique(),
        doc='Set of conversion processes')
		
Storages
^^^^^^^^

Energy **Storage** is provided by technical facilities that store energy to generate a commodity at
a later time for the purpose of meeting the demand. Occasionally, on-hand commodities
may not be able to satisfy the required amount of energy to meet the demand, or the available
amount of energy may be much more than required.Storage technologies play a major role in such circumstances.
The Set :math:`S` represents all storage technologies.(e.g `Pump storage`).
In script ``urbs.py`` this set is defined as ``sto`` and initalized by the code fragment:

::

    m.sto = pyomo.Set(
        initialize=m.storage.index.get_level_values('Storage').unique(),
        doc='Set of storage technologies')
		
Transmissions
^^^^^^^^^^^^^

**Transmissions** :math:`f \in F` represent possible conveyances of commodities between sites.
Transmission process technologies can vary between different commodities,
due to distinct physical attributes and forms of commodities. Some examples for Transmission technologies are: `hvac`, `hvdc`, `pipeline`)
In script ``urbs.py`` this set is defined as ``tra`` and initalized by the code fragment:

::

    m.tra = pyomo.Set(
        initialize=m.transmission.index.get_level_values('Transmission').unique(),
        doc='Set of transmission technologies')
		
Cost Types
^^^^^^^^^^

One of the major goals of the model is to calculate the costs of a simulated energy system.
There are 6 different types of costs. Each one has different features and are defined for
different instances. Set of **cost types** is hardcoded, which means they are not considered to be
fixed or changed  by the user.
These types are : ``Investment``, ``Fix``, ``Variable``, ``Fuel``, ``Revenue``, ``Purchase``.
In script ``urbs.py`` this set is defined as ``cost_type`` and initalized by the code fragment:

::

    m.cost_type = pyomo.Set(
        initialize=['Inv', 'Fix', 'Var', 'Fuel','Revenue','Purchase'],
        doc='Set of cost types (hard-coded)')
		

Tuple Sets
==========

A tuple is finite, ordered collection of elements.For example, the tuple ``(hat,red,large)`` consists of 3 ordered elements 
and defines another element itself.
Tuples are needed in this model to define the combinations of elements from different sets.
Defining a tuple lets us assemble related elements and use them as a single element.
As a result a collection of by the same rule defined tuples, represents a tuple set.

Commodity Tuples
^^^^^^^^^^^^^^^^

Commodity tuples represents combinations of defined commodities.
These are represented by the set :math:`C_{vq}`.
A member :math:`c_{vq}` in set :math:`C_{vq}` is a commodity :math:`c` of commodity type :math:`q` in site :math:`v`.
For example, `(Mid, Elec, Demand)` is interpreted as commodity `Elec` of commodity type `Demand` in site `Mid`.
This set is defined as ``com_tuples`` and given by the code fragment:

::

    m.com_tuples = pyomo.Set(
        within=m.sit*m.com*m.com_type,
        initialize=m.commodity.index,
        doc='Combinations of defined commodities, e.g. (Mid,Elec,Demand)')
		

Process Tuples
^^^^^^^^^^^^^^

Process Tuples represents combinations of possible processes.
These are represented by the set :math:`P_v`.
A member :math:`p_v` in set :math:`P_v` is a process :math:`p` in site :math:`v`.
For example, `(North, Coal Plant)` is interpreted as process `Coal Plant` in site `North`.
This set is defined as ``pro_tuples`` and given by the code fragment:

::

    m.pro_tuples = pyomo.Set(
        within=m.sit*m.pro,
        initialize=m.process.index,
        doc='Combinations of possible processes, e.g. (North,Coal plant)')
		

Transmission Tuples
^^^^^^^^^^^^^^^^^^^

Transmission tuples represents combinations of possible transmissions.
These are represented by the set :math:`F_{c{v_\text{out}}{v_\text{in}}}`.
A member :math:`f_{c{v_\text{out}}{v_\text{in}}}` in set :math:`F_{c{v_\text{out}}{v_\text{in}}}` is a transmission :math:`f`,that is directed from an origin site :math:`v_\text{out}` to a destination site :math:`v_{in}` and carries a commodity :math:`c`.
The term "\ `directed from an origin site` :math:`v_\text{out}` `to a destination site` :math:`v_\text{in}`" can also be defined as an Arc :math:`a` .
For example, `(South, Mid, hvac, Elec)` is interpreted as transmission `hvac` that is directed from origin site `South` to destination site `Mid` carrying commodity `Elec`.
This set is defined as ``tra_tuples`` and given by the code fragment:

::

    m.tra_tuples = pyomo.Set(
        within=m.sit*m.sit*m.tra*m.com,
        initialize=m.transmission.index,
        doc='Combinations of possible transmission, e.g. (South,Mid,hvac,Elec)')
		

Additionally, Subsets :math:`F_{vc}^\text{exp}` and :math:`F_{vc}^\text{imp}` represents all exporting and importing transmissions of a commodity :math:`c` in a site :math:`v`.
These subsets can be obtained by fixing either the origin site(for export) :math:`v_\text{out}` or the destination site(for import) :math:`v_\text{in}` to a desired site :math:`v` in tuple set :math:`F_{c{v_\text{out}}{v_\text{in}}}`.

Storage Tuples
^^^^^^^^^^^^^^
Storage tuples represents combinations of possible storages by site.
These are represented by the set :math:`S_{vc}`.
A member :math:`s_{vc}` in set :math:`S_{vc}` is a storage :math:`s` of commodity :math:`c` in site :math:`v`
For example, `(Mid, Bat, Elec)` is interpreted as storage `Bat` of commodity `Elec` in site `Mid`.
This set is defined as ``sto_tuples`` and given by the code fragment:

::

    m.sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com,
        initialize=m.storage.index,
        doc='Combinations of possible storage by site, e.g. (Mid,Bat,Elec)')
		

Process Input Tuples
^^^^^^^^^^^^^^^^^^^^
Process input tuples represents commodities consumed by processes.
These are represented by the set :math:`C_{vp}^\text{in}`.
A member :math:`c_{vp}^\text{in}` in set :math:`C_{vp}^\text{in}` is a commodity :math:`c` consumed by the process :math:`p` in site :math:`v`.
For example, `(Mid,PV,Solar)` is interpreted as commodity `Solar` is consumed by the process `PV` in the site `Mid`. 
This set is defined as ``pro_input_tuples`` and given by the code fragment:

::

    m.pro_input_tuples = pyomo.Set(
        within=m.sit*m.pro*m.com,
        initialize=[(site, process, commodity)
                    for (site, process) in m.pro_tuples
                    for (pro, commodity) in m.r_in.index
                    if process == pro],
        doc='Commodities consumed by process by site, e.g. (Mid,PV,Solar)')

Where; ``r_in`` represents the process input ratio.

Process Output Tuples
^^^^^^^^^^^^^^^^^^^^^
Process output tuples represents commodities generated by processes.
These are represented by the set :math:`C_{vp}^\text{out}`.
A member :math:`c_{vp}^\text{out}` in set :math:`C_{vp}^\text{out}` is a commodity :math:`c` generated by the process :math:`p` in site :math:`v`.
For example, `(Mid,PV,Elec)` is interpreted as the commodity `Elec` is generated by the process `PV` in the site `Mid`. 
This set is defined as ``pro_output_tuples`` and given by the code fragment:

::

    m.pro_output_tuples = pyomo.Set(
        within=m.sit*m.pro*m.com,
        initialize=[(site, process, commodity)
                    for (site, process) in m.pro_tuples
                    for (pro, commodity) in m.r_out.index
                    if process == pro],
        doc='Commodities produced by process by site, e.g. (Mid,PV,Elec)')
		
Where; ``r_out`` represents the process output ratio.

Commodity Type Subsets
======================

Commodity Type Subsets represent the commodities only from a given commodity type.
Commodity Type Subsets are subsets of the sets commodity tuples
These subsets can be obtained by fixing the commodity type :math:`q` to a desired commodity type (e.g SupIm, Stock) in the set commodity tuples :math:`C_{vq}`.
Since there are 6 types of commodity types, there are also 6 commodity type subsets. Commodity type subsets are;

	**Supply Intermittent Commodities** (``SupIm``): The set :math:`C_\text{sup}` represents all commodities :math:`c` of commodity type ``SupIm``. Commodities of this type have intermittent timeseries, in other words, availability of these commodities are not constant. These commodities might have various energy content for every timestep :math:`t`. For example solar radiation is contingent on many factors such as sun position, weather and varies permanently.

	**Stock Commodities** (``Stock``): The set :math:`C_\text{st}` represents all commodities :math:`c` of commodity type ``Stock``. Commodities of this type can be purchased at any time for a given price.

	**Sell Commodities** (``Sell``): The set :math:`C_\text{sell}` represents all commodities :math:`c` of commodity type ``Sell``. Commodities that can be sold.

	**Buy Commodities** (``Buy``): The set :math:`C_\text{buy}` represents all commodities :math:`c` of commodity type ``Buy``. Commodities that can be purchased.

	**Demand Commodities** (``Demand``): The set :math:`C_\text{dem}` represents all commodities :math:`c` of commodity type ``Demand``. Commodities of this type are the requested commodities of the energy system. They are usually the end product of the model (e.g Electricity:Elec).

	**Environmental Commodities** (``Env``): The set :math:`C_\text{env}` represents all commodities :math:`c` of commodity type ``Env``. Commodities of this type are usually the byproducts of processes, an optional maximum creation limit can be set to control the generation of these commodities (e.g Greenhouse Gas Emissions: :math:`\text{CO}_2`).

Commodity Type Subsets are given by the code fragment:
::

    m.com_supim = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'SupIm'),
        doc='Commodities that have intermittent (timeseries) input')
    m.com_stock = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Stock'),
        doc='Commodities that can be purchased at some site(s)')
    m.com_sell = pyomo.Set(
       within=m.com,
       initialize=commodity_subset(m.com_tuples, 'Sell'),
       doc='Commodities that can be sold')
    m.com_buy = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Buy'),
        doc='Commodities that can be purchased')
    m.com_demand = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Demand'),
        doc='Commodities that have a demand (implies timeseries)')
    m.com_env = pyomo.Set(
        within=m.com,
        initialize=commodity_subset(m.com_tuples, 'Env'),
        doc='Commodities that (might) have a maximum creation limit')


Variables
=========

A variable is a numerical value that is determined during optimization. Variables can denote a single, independent value, or an array of
values. Variables define the search space for optimization. 

Cost Variables
^^^^^^^^^^^^^^
**Total System Cost**, :math:`\zeta`, ``costs`` :
::

    m.costs = pyomo.Var(
        m.cost_type,
        within=pyomo.Reals,
        doc='Costs by type (EUR/a)')

Total System costs by type:

	Investment Costs :math:`\zeta_\text{inv}` :
	
	Fix Costs :math:`\zeta_\text{fix}` :
	
	Variable Costs :math:`\zeta_\text{var}` :
	
	Fuel Costs :math:`\zeta_\text{fuel}` :
	
	Revenue Costs :math:`\zeta_\text{rev}` :
	
	Purchase Costs :math:`\zeta_\text{pur}` :


Commodity Variables
^^^^^^^^^^^^^^^^^^^

**Stock Commodity Source Term**, :math:`\rho_{vct}`, ``e_co_stock``:
::

    m.e_co_stock = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of stock commodity source (MW) per timestep')

**Sell Commodity Source Term**, :math:`\varrho_{vct}`, ``e_co_sell``:
::

    m.e_co_sell = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of sell commodity source (kW) per timestep')

**Buy Commodity Source Term**, :math:`\psi_{vct}`, ``e_co_buy``:
::

    m.e_co_buy = pyomo.Var(
       m.tm, m.com_tuples,
       within=pyomo.NonNegativeReals,
       doc='Use of buy commodity source (kW) per timestep')

Process Variables
^^^^^^^^^^^^^^^^^

**Total Process Capacity**, :math:`\kappa_{vp}`, ``cap_pro``:
::

    m.cap_pro = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total process capacity (MW)')

**New Process Capacity**, :math:`\hat{\kappa}_{vp}`, ``cap_pro_new``:
::

    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')

**Process Throughput**, :math:`\tau_{vpt}`, ``tau_pro`` :
::

    m.tau_pro = pyomo.Var(
        m.tm, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow (MW) through process')

**Process Input Commodity Flow**, :math:`\epsilon_{vcpt}^\text{in}`, ``e_pro_in``:
::

    m.e_pro_in = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Power flow of commodity into process (MW) per timestep')


**Process Output Commodity Flow**, :math:`\epsilon_{vcpt}^\text{out}`, ``e_pro_out``:
::

    m.e_pro_out = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of process (MW) per timestep')

Transmission Variables
^^^^^^^^^^^^^^^^^^^^^^

**Total Transmission Capacity**, :math:`\kappa_{af}`, ``cap_tra``:
::

    m.cap_tra = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total transmission capacity (MW)')

**New Transmission Capacity**, :math:`\hat{\kappa}_{af}`, ``cap_tra_new``:
::

    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')

**Transmission Power Flow (Input)**, :math:`\pi_{aft}^\text{in}`, ``e_tra_in``:
::

    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into transmission line (MW) per timestep')

**Transmission Power Flow (Output)**, :math:`\pi_{aft}^\text{out}`, ``e_tra_out``:
::

    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of transmission line (MW) per timestep')

Storage Variables
^^^^^^^^^^^^^^^^^

**Total Storage Size**, :math:`\kappa_{vs}^\text{c}`, ``cap_sto_c``:
::

    m.cap_sto_c = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage size (MWh)')

**New Storage Size**, :math:`\hat{\kappa}_{vs}^\text{c}`, ``cap_sto_c_new``:
::

    m.cap_sto_c_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New storage size (MWh)')

**Total Storage Power**, :math:`\kappa_{vs}^\text{p}`, ``cap_sto_p``:
::

    m.cap_sto_p = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage power (MW)')

**New Storage Power**, :math:`\hat{\kappa}_{vs}^\text{p}`, ``cap_sto_p_new``:
::

    m.cap_sto_p_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New  storage power (MW)')

**Storage Power Flow (Input)**, :math:`\epsilon_{vst}^\text{in}`, ``e_sto_in``:
::

    m.e_sto_in = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into storage (MW) per timestep')

**Storage Power Flow (Output)**, :math:`\epsilon_{vst}^\text{out}`, ``e_sto_out``:
::

    m.e_sto_out = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of storage (MW) per timestep')

**Storage Energy Content**, :math:`\epsilon_{vst}^\text{con}`, ``e_sto_con``:
::

    m.e_sto_con = pyomo.Var(
        m.t, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Energy content of storage (MWh) in timestep')

Parameters
==========

Technical Parameters
^^^^^^^^^^^^^^^^^^^^

General Technical Parameters
----------------------------
**Weight**, :math:`w`, ``weight``:
::

    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.t) * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')
		

**Timestep Duration**, :math:`\Delta t`, ``dt``:
::

    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')
		

Commodity Technical Parameters
------------------------------

**Demand for Commodity**, :math:`d_{vct}`, ``m.demand.loc[tm][sit,com]``:

**Intermittent Supply Capacity Factor**, :math:`s_{vct}`, ``m.supim.loc[tm][sit,com]``:

**Maximum Stock Supply Limit Per Time Step**, :math:`\overline{l}_{vc}`, ``m.commodity.loc[sit,com,com_type]['maxperstep']``:

**Maximum Annual Stock Supply Limit Per Vertex**, :math:`\overline{L}_{vc}`, ``m.commodity.loc[sit,com,com_type]['max']``:

**Maximum Environmental Output Per Time Step**, :math:`\overline{m}_{vc}`, ``m.commodity.loc[sit,com,com_type]['maxperstep']``:

**Maximum Annual Environmental Output**, :math:`\overline{M}_{vc}`, ``m.commodity.loc[sit,com,com_type]['max']``:

**Maximum Sell Limit Per Time Step**, :math:`\overline{g}_{vc}`, ``m.commodity.loc[sit,com,com_type][`maxperstep`]``:

**Maximum Annual Sell Limit**, :math:`\overline{G}_{vc}`, ``m.commodity.loc[sit,com,com_type][`max`]``:

**Maximum Buy Limit Per Time Step**, :math:`\overline{b}_{vc}`, ``m.commodity.loc[sit,com,com_type][`maxperstep`]``:

**Maximum Annual Buy Limit**, :math:`\overline{B}_{vc}`, ``m.commodity.loc[sit,com,com_type][`max`]``:

**Maximum Global Annual CO**:math:`_\text{2}` **Emission Limit**, :math:`\overline{L}_{CO_2}`, ``m.hack.loc['Global CO2 Limit','Value']``:

Process Technical Parameters
----------------------------

**Process Capacity Lower Bound**, :math:`\underline{K}_{vp}`, ``m.process.loc[sit,pro]['cap-lo']``:

**Process Capacity Installed**, :math:`K_{vp}`, ``m.process.loc[sit,pro]['inst-cap']``:

**Process Capacity Upper Bound**, :math:`\overline{K}_{vp}`, ``m.process.loc[sit,pro]['cap-up']``:

**Process Input Ratio**, :math:`r_{pc}^\text{in}`, ``m.r_in.loc[pro,co]``:

**Process Output Ratio**, :math:`r_{pc}^\text{out}`, ``m.r_out.loc[pro,co]``:

Storage Technical Parameters
----------------------------

**Initial and Final Storage Content (relative)**, :math:`I_{vs}`, ``m.storage.loc[sit,sto,com]['init']``:

**Storage Efficiency During Charge**, :math:`e_{vs}^\text{in}`, ``m.storage.loc[sit,sto,com]['eff-in']``:

**Storage Efficiency During Discharge**, :math:`e_{vs}^\text{out}`, ``m.storage.loc[sit,sto,com]['eff-out']``:

**Storage Content Lower Bound**, :math:`\underline{K}_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['cap-lo-c']``:

**Storage Content Installed**, :math:`K_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['inst-cap-c']``:

**Storage Content Upper Bound**, :math:`\overline{K}_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['cap-up-c']``:

**Storage Power Lower Bound**, :math:`\underline{K}_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['cap-lo-p']``:

**Storage Power Installed**, :math:`K_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['inst-cap-p']``:

**Storage Power Upper Bound**, :math:`\overline{K}_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['cap-up-p']``:

Transmission Technical Parameters
---------------------------------

**Transmission Efficiency**, :math:`e_{af}`, ``m.transmission.loc[sin,sout,tra,com]['eff']``:

**Tranmission Capacity Lower Bound**, :math:`\underline{K}_{af}`, ``m.transmission.loc[sin,sout,tra,com]['cap-lo']``:

**Tranmission Capacity Installed**, :math:`K_{af}`, ``m.transmission.loc[sin,sout,tra,com]['inst-cap']``:

**Tranmission Capacity Upper Bound**, :math:`\overline{K}_{af}`, ``m.transmission.loc[sin,sout,tra,com]['cap-up']``:

Economical Parameters
^^^^^^^^^^^^^^^^^^^^^

Commodity Economical Parameters
-------------------------------

**Stock Commodity Fuel Costs**, :math:`k_{vc}^\text{fuel}`, ``m.commodity.loc[c]['price']``:

**Buy/Sell Commodity Buy/Sell Costs**, :math:`k_{vc}^\text{bs}`, ``com_prices[c].loc[tm]``:

Process Economical Parameters
-----------------------------

**Annualised Process Capacity Investment**, :math:`k_{vp}^\text{inv}`, ``m.process.loc[p]['inv-cost'] * m.process.loc[p]['annuity-factor']``:

**Process Capacity Fixed Costs**, :math:`k_{vp}^\text{fix}`, ``m.process.loc[p]['fix-cost']``:

**Process Variable Costs**, :math:`k_{vp}^\text{var}`, ``m.process.loc[p]['var-cost']``:

Storage Economical Parameters
-----------------------------

**Annualised Storage Power Investment**, :math:`k_{vs}^\text{p,inv}`, ``m.storage.loc[s]['inv-cost-p'] * m.storage.loc[s]['annuity-factor']``:

**Annual Storage Power Fixed Costs**, :math:`k_{vs}^\text{p,fix}`, ``m.storage.loc[s]['fix-cost-p']``:

**Storage Power Variable Costs**, :math:`k_{vs}^\text{p,var}`, ``m.storage.loc[s]['var-cost-p']``:

**Annualised Storage Size Investment**, :math:`k_{vs}^\text{c,inv}`, ``m.storage.loc[s]['inv-cost-c'] * m.storage.loc[s]['annuity-factor']``:

**Annual Storage Size Fixed Costs**, :math:`k_{vs}^\text{c,fix}`, ``m.storage.loc[s]['fix-cost-c']``:

**Storage Usage Variable Costs**, :math:`k_{vs}^\text{c,var}`, ``m.storage.loc[s]['var-cost-c']``:

Transmission Economical Parameters
----------------------------------

**Annualised Tranmission Capacity Investment**, :math:`k_{af}^\text{inv}`, ``m.transmission.loc[t]['inv-cost'] * m.transmission.loc[t]['annuity-factor']``:

**Annual Transmission Capacity Fixed Costs**, :math:`k_{af}^\text{fix}`, ``m.transmission.loc[t]['fix-cost']``:

**Tranmission Usage Variable Costs**, :math:`k_{af}^\text{var}`, ``m.transmission.loc[t]['var-cost']``:

Equations
=========

Cost Function
^^^^^^^^^^^^^

.. math::

	\zeta = \zeta_\text{inv} + \zeta_\text{fix} + \zeta_\text{var} + \zeta_\text{fuel} + \zeta_\text{rev} + \zeta_\text{pur}

::

	def obj_rule(m):
		return pyomo.summation(m.costs)


Investment Costs
----------------

.. math::

	\zeta_\text{inv} = 
	\sum_{\substack{v \in V\\ p \in P}} \hat{\kappa}_{vp} k_p^\text{inv} +
	\sum_{\substack{v \in V\\ s \in S}} \left( \hat{\kappa}_{vs}^\text{c} k_{vs}^\text{c,inv} + \hat{\kappa}_{vs}^\text{p} k_{vs}^\text{p,inv}\right) +
	\sum_{\substack{a \in A\\ f \in F}} \hat{\kappa}_{af} k_{af}^\text{inv}

::

    if cost_type == 'Inv':
        return m.costs['Inv'] == \
            sum(m.cap_pro_new[p] *
                m.process.loc[p]['inv-cost'] *
                m.process.loc[p]['annuity-factor']
                for p in m.pro_tuples) + \
            sum(m.cap_tra_new[t] *
                m.transmission.loc[t]['inv-cost'] *
                m.transmission.loc[t]['annuity-factor']
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p_new[s] *
                m.storage.loc[s]['inv-cost-p'] *
                m.storage.loc[s]['annuity-factor'] +
                m.cap_sto_c_new[s] *
                m.storage.loc[s]['inv-cost-c'] *
                m.storage.loc[s]['annuity-factor']
                for s in m.sto_tuples)


Fix Costs
---------

.. math::

	\zeta_\text{fix} = 
	\sum_{\substack{v \in V\\ p \in P}} \kappa_{vp} k_{vp}^\text{fix} +
	\sum_{\substack{v \in V\\ s \in S}} \left( \kappa_{vs}^\text{c} k_{vs}^\text{c,fix} + \kappa_{vs}^\text{p} k_{vs}^\text{p,fix} \right) +
	\sum_{\substack{a \in A\\ f \in F}} \kappa_{af} k_{af}^\text{fix}

::

    elif cost_type == 'Fix':
        return m.costs['Fix'] == \
            sum(m.cap_pro[p] * m.process.loc[p]['fix-cost']
                for p in m.pro_tuples) + \
            sum(m.cap_tra[t] * m.transmission.loc[t]['fix-cost']
                for t in m.tra_tuples) + \
            sum(m.cap_sto_p[s] * m.storage.loc[s]['fix-cost-p'] +
                m.cap_sto_c[s] * m.storage.loc[s]['fix-cost-c']
                for s in m.sto_tuples)


Variable Costs
--------------

.. math::

	\zeta_\text{var} =  w \sum_{t \in T_\text{m}} &\left( \sum_{\substack{v \in V\\ p \in P}} \tau_{vpt} k_{vp}^\text{var} \Delta t + 
	\sum_{\substack{a \in a\\ f \in F}} \pi_{af}^\text{in} k_{af}^\text{var} \Delta t +  
	\right.\nonumber \\
	&\left.\phantom{\Big(} % invisible left parenthesis for horizontal alignment
	\sum_{\substack{v \in V\\ s \in S}} \left[ 
	\epsilon_{vst}^\text{con} k_{vs}^\text{c,var} + \left(
	\epsilon_{vst}^\text{in} + \epsilon_{vst}^\text{out} 
	\right) k_{vs}^\text{p,var} \Delta t 
	\right] 
	\right)

::

    elif cost_type == 'Var':
        return m.costs['Var'] == \
            sum(m.tau_pro[(tm,) + p] * m.dt *
                m.process.loc[p]['var-cost'] *
                m.weight
                for tm in m.tm for p in m.pro_tuples) + \
            sum(m.e_tra_in[(tm,) + t] * m.dt *
                m.transmission.loc[t]['var-cost'] *
                m.weight
                for tm in m.tm for t in m.tra_tuples) + \
            sum(m.e_sto_con[(tm,) + s] *
                m.storage.loc[s]['var-cost-c'] * m.weight +
                (m.e_sto_in[(tm,) + s] + m.e_sto_out[(tm,) + s]) * m.dt *
                m.storage.loc[s]['var-cost-p'] * m.weight
                for tm in m.tm for s in m.sto_tuples)


Fuel Costs
----------

.. math::

	\zeta_\text{fuel} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{stock}}} \rho_{vct} k_{vc}^\text{fuel} \Delta t

::

    elif cost_type == 'Fuel':
        return m.costs['Fuel'] == sum(
            m.e_co_stock[(tm,) + c] * m.dt *
            m.commodity.loc[c]['price'] *
            m.weight
            for tm in m.tm for c in m.com_tuples
            if c[1] in m.com_stock)


Revenue Costs
-------------

.. math::

	\zeta_\text{rev} = 
	-w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{sell}}} \varrho_{vct} k_{vc}^\text{bs} \Delta t

::

    elif cost_type == 'Revenue':
        sell_tuples = commodity_subset(m.com_tuples, m.com_sell)
        com_prices = get_com_price(m, sell_tuples)

        return m.costs['Revenue'] == -sum(
            m.e_co_sell[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in sell_tuples)


Purchase Costs
--------------

.. math::

	\zeta_\text{rev} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{buy}}} \psi_{vct} k_{vc}^\text{bs} \Delta t

::

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)
        com_prices = get_com_price(m, buy_tuples)

        return m.costs['Purchase'] == sum(
            m.e_co_buy[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in buy_tuples)

Commodity Balance
^^^^^^^^^^^^^^^^^

.. math::

	\mathrm{CB}(v,c,t) = 
          \sum_{{p|c \in C_{vp}^\text{in}}} \epsilon_{vcpt}^\text{in}
        - \sum_{{p|c \in C_{vp}^\text{out}}} \epsilon_{vcpt}^\text{out}
        + \sum_{{s\in S_{vc}}} \left( \epsilon_{vst}^\text{in} - \epsilon_{vst}^\text{out} \right)
        + \sum_{{\substack{a\in A_v^\text{s}\\ f \in F_{vc}^\text{exp}}}} \pi_{aft}^\text{in}
        - \sum_{{\substack{a\in A_v^\text{p}\\ f \in F_{vc}^\text{imp}}}} \pi_{aft}^\text{out}

::

	def commodity_balance(m, tm, sit, com):
		balance = 0
		for site, process in m.pro_tuples:
			if site == sit and com in m.r_in.loc[process].index:
				# usage as input for process increases balance
				balance += m.e_pro_in[(tm, site, process, com)]
			if site == sit and com in m.r_out.loc[process].index:
				# output from processes decreases balance
				balance -= m.e_pro_out[(tm, site, process, com)]
		for site_in, site_out, transmission, commodity in m.tra_tuples:
			# exports increase balance
			if site_in == sit and commodity == com:
				balance += m.e_tra_in[(tm, site_in, site_out, transmission, com)]
			# imports decrease balance
			if site_out == sit and commodity == com:
				balance -= m.e_tra_out[(tm, site_in, site_out, transmission, com)]
		for site, storage, commodity in m.sto_tuples:
			# usage as input for storage increases consumption
			# output from storage decreases consumption
			if site == sit and commodity == com:
				balance += m.e_sto_in[(tm, site, storage, com)]
				balance -= m.e_sto_out[(tm, site, storage, com)]
		return balance

Constraints
===========

Commodity Constraints
^^^^^^^^^^^^^^^^^^^^^

**Vertex Rule**:

.. math::

	\qquad & \forall v\in V, c\in C^\text{v}, t\in T\colon \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \rho_{vct} - \mathrm{CB}(v,c,t) - d_{vct} &\geq 0 &&

::

		m.res_vertex = pyomo.Constraint(
			m.tm, m.com_tuples,
			rule=res_vertex_rule,
			doc='storage + transmission + process + source + buy - sell == demand')
		

::

	def res_vertex_rule(m, tm, sit, com, com_type):
		# environmental or supim commodities don't have this constraint (yet)
		if com in m.com_env:
			return pyomo.Constraint.Skip
		if com in m.com_supim:
			return pyomo.Constraint.Skip
	
		# helper function commodity_balance calculates balance from input to
		# and output from processes, storage and transmission.
		# if power_surplus > 0: production/storage/imports create net positive
		#                       amount of commodity com
		# if power_surplus < 0: production/storage/exports consume a net
		#                       amount of the commodity com
		power_surplus = - commodity_balance(m, tm, sit, com)
	
		# if com is a stock commodity, the commodity source term e_co_stock
		# can supply a possibly negative power_surplus
		if com in m.com_stock:
			power_surplus += m.e_co_stock[tm, sit, com, com_type]
	
		# if com is a sell commodity, the commodity source term e_co_sell
		# can supply a possibly positive power_surplus
		if com in m.com_sell:
			power_surplus -= m.e_co_sell[tm, sit, com, com_type]
	
		# if com is a buy commodity, the commodity source term e_co_buy
		# can supply a possibly negative power_surplus
		if com in m.com_buy:
			power_surplus += m.e_co_buy[tm, sit, com, com_type]
	
		# if com is a demand commodity, the power_surplus is reduced by the
		# demand value; no scaling by m.dt or m.weight is needed here, as this
		# constraint is about power (MW), not energy (MWh)
		if com in m.com_demand:
			try:
				power_surplus -= m.demand.loc[tm][sit, com]
			except KeyError:
				pass
		return power_surplus == 0

**Stock Per Step Rule**:

.. math::

	\forall v\in V, c\in C_\text{st}, t\in T\colon \qquad & \rho_{vct} &\leq \overline{l}_{vc}

::

    m.res_stock_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_stock_step_rule,
        doc='stock commodity input per step <= commodity.maxperstep')

::

	def res_stock_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_stock:
			return pyomo.Constraint.Skip
		else:
			return (m.e_co_stock[tm, sit, com, com_type] <=
					m.commodity.loc[sit, com, com_type]['maxperstep'])

**Total Stock Rule**:

.. math::

	\forall v\in V, c\in C_\text{st}\colon \qquad & \qquad  w \sum_{t\in T} \Delta t\, \rho_{vct} &\leq \overline{L}_{vc}

::

    m.res_stock_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_stock_total_rule,
        doc='total stock commodity input <= commodity.max')

::

	def res_stock_total_rule(m, sit, com, com_type):
		if com not in m.com_stock:
			return pyomo.Constraint.Skip
		else:
			# calculate total consumption of commodity com
			total_consumption = 0
			for tm in m.tm:
				total_consumption += (
					m.e_co_stock[tm, sit, com, com_type] * m.dt)
			total_consumption *= m.weight
			return (total_consumption <=
					m.commodity.loc[sit, com, com_type]['max'])


**Sell Per Step Rule**:

.. math::

	\forall v\in V, c\in C_\text{sell}, t\in T\colon \qquad & \qquad \varrho_{vct} &\leq \overline{g}_{vc}

::

    m.res_sell_step = pyomo.Constraint(
       m.tm, m.com_tuples,
       rule=res_sell_step_rule,
       doc='sell commodity output per step <= commodity.maxperstep')

::

	def res_sell_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_sell:
			return pyomo.Constraint.Skip
		else:
			return (m.e_co_sell[tm, sit, com, com_type] <=
					   m.commodity.loc[sit, com, com_type]['maxperstep'])


**Total Sell Rule**:

.. math::

	\forall v\in V, c\in C_\text{sell}\colon \qquad & \qquad  w \sum_{t\in T} \Delta t\, \varrho_{vct} &\leq \overline{G}_{vc}

::

    m.res_sell_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_sell_total_rule,
        doc='total sell commodity output <= commodity.max')

::

	def res_sell_total_rule(m, sit, com, com_type):
		if com not in m.com_sell:
			return pyomo.Constraint.Skip
		else:
			# calculate total sale of commodity com
			total_consumption = 0
			for tm in m.tm:
				total_consumption += (
					m.e_co_sell[tm, sit, com, com_type] * m.dt)
			total_consumption *= m.weight
			return (total_consumption <=
					  m.commodity.loc[sit, com, com_type]['max'])

**Buy Per Step Rule**:

.. math::

	\forall v\in V, c\in C_\text{buy}, t\in T\colon \qquad & \qquad \psi_{vct} &\leq \overline{b}_{vc}

::

    m.res_buy_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_buy_step_rule,
        doc='buy commodity output per step <= commodity.maxperstep')

::

	def res_buy_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_buy:
			return pyomo.Constraint.Skip
		else:
			return (m.e_co_buy[tm, sit, com, com_type] <=
					   m.commodity.loc[sit, com, com_type]['maxperstep'])

**Total Buy Rule**:

.. math::

	\forall v\in V, c\in C_\text{buy}\colon \qquad & \qquad  w \sum_{t\in T} \Delta t\, \psi_{vct} &\leq \overline{B}_{vc}

::

    m.res_buy_total = pyomo.Constraint(
       m.com_tuples,
       rule=res_buy_total_rule,
       doc='total buy commodity output <= commodity.max')

::

	def res_buy_total_rule(m, sit, com, com_type):
		if com not in m.com_buy:
			return pyomo.Constraint.Skip
		else:
			# calculate total sale of commodity com
			total_consumption = 0
			for tm in m.tm:
				total_consumption += (
					m.e_co_buy[tm, sit, com, com_type] * m.dt)
			total_consumption *= m.weight
			return (total_consumption <=
					  m.commodity.loc[sit, com, com_type]['max'])

**Environmental Output Per Step Rule**:

.. math::

	\forall v\in V, c\in C_\text{env}, t\in T\colon \qquad & \qquad -\mathrm{CB}(v,c,t) &\leq \overline{m}_{vc}

::

    m.res_env_step = pyomo.Constraint(
        m.tm, m.com_tuples,
        rule=res_env_step_rule,
        doc='environmental output per step <= commodity.maxperstep')

::

	def res_env_step_rule(m, tm, sit, com, com_type):
		if com not in m.com_env:
			return pyomo.Constraint.Skip
		else:
			environmental_output = - commodity_balance(m, tm, sit, com)
			return (environmental_output <=
					m.commodity.loc[sit, com, com_type]['maxperstep'])

**Total Environmental Output Rule**:

.. math::

	\forall v\in V, c\in C_\text{env}\colon \qquad & \qquad  - w \sum_{t\in T} \Delta t\, \mathrm{CB}(v,c,t) &\leq \overline{M}_{vc}

::

    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

::

	def res_env_total_rule(m, sit, com, com_type):
		if com not in m.com_env:
			return pyomo.Constraint.Skip
		else:
			# calculate total creation of environmental commodity com
			env_output_sum = 0
			for tm in m.tm:
				env_output_sum += (- commodity_balance(m, tm, sit, com) * m.dt)
			env_output_sum *= m.weight
			return (env_output_sum <=
					m.commodity.loc[sit, com, com_type]['max'])

Process Constraints
^^^^^^^^^^^^^^^^^^^

**Process Capacity Rule**:

.. math::

	\forall v\in V, p\in P\colon \qquad & \qquad \kappa_{vp} = K_{vp} + \hat{\kappa}_{vp}

::

    m.def_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=def_process_capacity_rule,
        doc='total process capacity = inst-cap + new capacity')

::

	def def_process_capacity_rule(m, sit, pro):
		return (m.cap_pro[sit, pro] ==
				m.cap_pro_new[sit, pro] +
				m.process.loc[sit, pro]['inst-cap'])

**Process Input Rule**:

.. math::

	\forall v\in V, p\in P, t\in T\colon \qquad & \qquad \epsilon^\text{in}_{vpct} &= \tau_{vpt} r^\text{in}_{pc}

::

    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')

::

	def def_process_input_rule(m, tm, sit, pro, co):
		return (m.e_pro_in[tm, sit, pro, co] ==
				m.tau_pro[tm, sit, pro] * m.r_in.loc[pro, co])

**Process Output Rule**:

.. math::

	\forall v\in V, p\in P, t\in T\colon \qquad & \qquad \epsilon^\text{out}_{vpct} &= \tau_{vpt} r^\text{out}_{pc}

::

    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

::

	def def_process_output_rule(m, tm, sit, pro, co):
		return (m.e_pro_out[tm, sit, pro, co] ==
				m.tau_pro[tm, sit, pro] * m.r_out.loc[pro, co])

**Intermittent Supply Rule**:

.. math::

	\forall v\in V, p\in P, c\in C_\text{sup}, t\in T\colon \qquad & \qquad \epsilon^\text{in}_{vpct} &= \kappa_{vp} s_{vct}

::

    m.def_intermittent_supply = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_intermittent_supply_rule,
        doc='process output = process capacity * supim timeseries')

::

	def def_intermittent_supply_rule(m, tm, sit, pro, coin):
		if coin in m.com_supim:
			return (m.e_pro_in[tm, sit, pro, coin] ==
					m.cap_pro[sit, pro] * m.supim.loc[tm][sit, coin])
		else:
			return pyomo.Constraint.Skip

**Process Throughput By Capacity Rule**:

.. math::

	\forall v\in V, p\in P, t\in T\colon \qquad & \qquad \tau_{vpt} &\leq \kappa_{vp}

::

    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')

::

	def res_process_throughput_by_capacity_rule(m, tm, sit, pro):
		return (m.tau_pro[tm, sit, pro] <= m.cap_pro[sit, pro])

**Process Capacity Rule**:

.. math::

	\forall v\in V, p\in P\colon \qquad & \qquad  \underline{K}_{vp} \leq \kappa_{vp} \leq \overline{K}_{vp}

::

    m.res_process_capacity = pyomo.Constraint(
        m.pro_tuples,
        rule=res_process_capacity_rule,
        doc='process.cap-lo <= total process capacity <= process.cap-up')

::

	def res_process_capacity_rule(m, sit, pro):
		return (m.process.loc[sit, pro]['cap-lo'],
				m.cap_pro[sit, pro],
				m.process.loc[sit, pro]['cap-up'])

**Sell Buy Symmetry Rule**:

.. math::


::

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='total power connection capacity must be symmetric in both directions')

::

	def res_sell_buy_symmetry_rule(m, sit_in, pro_in, coin):
	# constraint only for sell and buy processes
	# and the processes musst be in the same site
		if coin in m.com_buy:
			sell_pro = search_sell_buy_tuple(m, sit_in, pro_in, coin)
			if sell_pro is None:
				return pyomo.Constraint.Skip
			else:
				return (m.cap_pro[sit_in, pro_in] ==
							m.cap_pro[sit_in, sell_pro])
		else:
			return pyomo.Constraint.Skip

Transmission Constraints
^^^^^^^^^^^^^^^^^^^^^^^^

**Transmission Capacity Rule**:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \kappa_{af} &= K_{af} + \hat{\kappa}_{af}

::

    m.def_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity = inst-cap + new capacity')

::

	def def_transmission_capacity_rule(m, sin, sout, tra, com):
		return (m.cap_tra[sin, sout, tra, com] ==
				m.cap_tra_new[sin, sout, tra, com] +
				m.transmission.loc[sin, sout, tra, com]['inst-cap'])

**Transmission Output Rule**:

.. math::

	\forall a\in A, f\in F, t\in T\colon \qquad & \qquad \pi^\text{out}_{aft} &= \pi^\text{in}_{aft} e_{af}

::

    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')

::

	def def_transmission_output_rule(m, tm, sin, sout, tra, com):
		return (m.e_tra_out[tm, sin, sout, tra, com] ==
				m.e_tra_in[tm, sin, sout, tra, com] *
				m.transmission.loc[sin, sout, tra, com]['eff'])

**Transmission Input By Capacity Rule**:

.. math::

	\forall a\in A, f\in F, t\in T\colon \qquad & \qquad \pi^\text{in}_{aft} &\leq \kappa_{af}

::

    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')

::

	def res_transmission_input_by_capacity_rule(m, tm, sin, sout, tra, com):
		return (m.e_tra_in[tm, sin, sout, tra, com] <=
				m.cap_tra[sin, sout, tra, com])

**Transmission Capacity Rule**:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \underline{K}_{af} &\leq \kappa_{af} \leq \overline{K}_{af}

::

    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')

::

	def res_transmission_capacity_rule(m, sin, sout, tra, com):
		return (m.transmission.loc[sin, sout, tra, com]['cap-lo'],
				m.cap_tra[sin, sout, tra, com],
				m.transmission.loc[sin, sout, tra, com]['cap-up'])

**Transmission Symmetry Rule**:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \kappa_{af} &= \kappa_{a'f}

::

    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

::

	def res_transmission_symmetry_rule(m, sin, sout, tra, com):
		return m.cap_tra[sin, sout, tra, com] == m.cap_tra[sout, sin, tra, com]

Storage Constraints
^^^^^^^^^^^^^^^^^^^

**Storage State Rule**:

.. math::

	\forall v\in V, \forall s\in S, t\in T_\text{m}\colon \qquad & \qquad \epsilon_{vst}^\text{con} = \epsilon_{vs(t-1)}^\text{con}  + \epsilon_{vst}^\text{in} \cdot e_{vs}^\text{in} - \epsilon_{vst}^\text{out} / e_{vs}^\text{out}

::

    m.def_storage_state = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=def_storage_state_rule,
        doc='storage[t] = storage[t-1] + input - output')

::

	def def_storage_state_rule(m, t, sit, sto, com):
		return (m.e_sto_con[t, sit, sto, com] ==
				m.e_sto_con[t-1, sit, sto, com] +
				m.e_sto_in[t, sit, sto, com] *
				m.storage.loc[sit, sto, com]['eff-in'] * m.dt -
				m.e_sto_out[t, sit, sto, com] /
				m.storage.loc[sit, sto, com]['eff-out'] * m.dt)

**Storage Power Rule**:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \kappa_{vs}^\text{p} = K_{vs}^\text{p} + \hat{\kappa}_{vs}^\text{p}

::

    m.def_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_power_rule,
        doc='storage power = inst-cap + new power')

::

	def def_storage_power_rule(m, sit, sto, com):
		return (m.cap_sto_p[sit, sto, com] ==
				m.cap_sto_p_new[sit, sto, com] +
				m.storage.loc[sit, sto, com]['inst-cap-p'])

**Storage Capacity Rule**:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \kappa_{vs}^\text{c} = K_{vs}^\text{c} + \hat{\kappa}_{vs}^\text{c}

::

    m.def_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=def_storage_capacity_rule,
        doc='storage capacity = inst-cap + new capacity')

::

	def def_storage_capacity_rule(m, sit, sto, com):
		return (m.cap_sto_c[sit, sto, com] ==
				m.cap_sto_c_new[sit, sto, com] +
				m.storage.loc[sit, sto, com]['inst-cap-c'])

**Storage Input By Power Rule**:

.. math::

	\forall v\in V, s\in S, t\in T\colon \qquad & \qquad \epsilon_{vst}^\text{in} \leq \kappa_{vs}^\text{p}

::

    m.res_storage_input_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_input_by_power_rule,
        doc='storage input <= storage power')

::

	def res_storage_input_by_power_rule(m, t, sit, sto, com):
		return m.e_sto_in[t, sit, sto, com] <= m.cap_sto_p[sit, sto, com]

**Storage Output By Power Rule**:

.. math::

	 \forall v\in V, s\in S, t\in T\colon \qquad & \qquad \epsilon_{vst}^\text{out} \leq \kappa_{vs}^\text{p}

::

    m.res_storage_output_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_output_by_power_rule,
        doc='storage output <= storage power')

::

	def res_storage_output_by_power_rule(m, t, sit, sto, co):
		return m.e_sto_out[t, sit, sto, co] <= m.cap_sto_p[sit, sto, co]

**Storage State By Capacity Rule**:

.. math::

	\forall v\in V, s\in S, t\in T\colon \qquad & \qquad \epsilon_{vst}^\text{con} \leq \kappa_{vs}^\text{c}

::

    m.res_storage_state_by_capacity = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_storage_state_by_capacity_rule,
        doc='storage content <= storage capacity')

::

	def res_storage_state_by_capacity_rule(m, t, sit, sto, com):
		return m.e_sto_con[t, sit, sto, com] <= m.cap_sto_c[sit, sto, com]

**Storage Power Rule**:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \underline{K}_{vs}^\text{p} \leq \kappa_{vs}^\text{p} \leq \overline{K}_{vs}^\text{p}

::

    m.res_storage_power = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_power_rule,
        doc='storage.cap-lo-p <= storage power <= storage.cap-up-p')

::

	def res_storage_power_rule(m, sit, sto, com):
		return (m.storage.loc[sit, sto, com]['cap-lo-p'],
				m.cap_sto_p[sit, sto, com],
				m.storage.loc[sit, sto, com]['cap-up-p'])

**Storage Capacity Rule**:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \underline{K}_{vs}^\text{c} \leq \kappa_{vs}^\text{c} \leq \overline{K}_{vs}^\text{c}

::

    m.res_storage_capacity = pyomo.Constraint(
        m.sto_tuples,
        rule=res_storage_capacity_rule,
        doc='storage.cap-lo-c <= storage capacity <= storage.cap-up-c')

::

	def res_storage_capacity_rule(m, sit, sto, com):
		return (m.storage.loc[sit, sto, com]['cap-lo-c'],
				m.cap_sto_c[sit, sto, com],
				m.storage.loc[sit, sto, com]['cap-up-c'])

**Initial And Final Storage State Rule**:

Initial Storage:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \epsilon_{vst_0}^\text{con} = \kappa_{vs}^\text{c} I_{vs}

Final Storage:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \epsilon_{vst_N}^\text{con} \geq \kappa_{vs}^\text{c} I_{vs}

::

    m.res_initial_and_final_storage_state = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_initial_and_final_storage_state_rule,
        doc='storage content initial == and final >= storage.init * capacity')

::

	def res_initial_and_final_storage_state_rule(m, t, sit, sto, com):
		if t == m.t[1]:  # first timestep (Pyomo uses 1-based indexing)
			return (m.e_sto_con[t, sit, sto, com] ==
					m.cap_sto_c[sit, sto, com] *
					m.storage.loc[sit, sto, com]['init'])
		elif t == m.t[len(m.t)]:  # last timestep
			return (m.e_sto_con[t, sit, sto, com] >=
					m.cap_sto_c[sit, sto, com] *
					m.storage.loc[sit, sto, com]['init'])
		else:
			return pyomo.Constraint.Skip

Environmental Constraints
^^^^^^^^^^^^^^^^^^^^^^^^^

**Global CO2 Limit Rule**:

.. math::

	w \sum_{t\in T_\text{m}} \sum_{v \in V} \mathrm{CB}(v,CO_{2},t) \leq \overline{L}_{CO_{2}}

::

	def add_hacks(model, hacks):
		""" add hackish features to model object

		This function is reserved for corner cases/features that still lack a
		satisfyingly general solution that could become part of create_model.
		Use hack features sparingly and think about how to incorporate into main
		model function before adding here. Otherwise, these features might become
		a maintenance burden.

		"""

		# Store hack data
		model.hacks = hacks

		# Global CO2 limit
		try:
			global_co2_limit = hacks.loc['Global CO2 limit', 'Value']
		except KeyError:
			global_co2_limit = float('inf')

		# only add constraint if limit is finite
		if not math.isinf(global_co2_limit):
			model.res_global_co2_limit = pyomo.Constraint(
				rule=res_global_co2_limit_rule,
				doc='total co2 commodity output <= hacks.Glocal CO2 limit')

		return model

::

	def res_global_co2_limit_rule(m):
		co2_output_sum = 0
		for tm in m.tm:
			for sit in m.sit:
				# minus because negative commodity_balance represents creation of 
				# that commodity.
				co2_output_sum += (- commodity_balance(m, tm, sit, 'CO2') * m.dt)

		# scaling to annual output (cf. definition of m.weight)
		co2_output_sum *= m.weight
		return (co2_output_sum <= m.hacks.loc['Global CO2 limit', 'Value'])

