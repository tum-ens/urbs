.. module:: urbs

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
Duration of space between timesteps :math:`\Delta t = t_{x+1} - t_x`, length of simulation :math:`\Delta t \cdot N` and
time interval :math:`[t_0,t_N]` can be fixed to satisfy the needs of the user.
In code this set is defined by the set ``t`` and initialized by the section:

::

    m.t = pyomo.Set(
        initialize=m.timesteps,
        ordered=True,
        doc='Set of timesteps')
		
Where:

* `Initialize`: A function that receives the set indices and model to return the value of that set element, initializes the set with data.
* `Ordered`: A boolean value that indicates whether the set is ordered.
* `Doc`: A string describing the set.

Modelled Timesteps
^^^^^^^^^^^^^^^^^^

The Set, **modelled timesteps**, is a subset of the time steps set. The difference between modelled
timesteps set and the timesteps set is that the initial timestep :math:`t_0` is not included.
All other features of the set time steps also apply to the set of modelled timesteps. This set
is later required to facilitate the definition of the storage state equation.
In script ``urbs.py`` this set is defined by the set ``tm`` and initialized by the code fragment:

::

    m.tm = pyomo.Set(
        within=m.t,
        initialize=m.timesteps[1:],
        ordered=True,
        doc='Set of modelled timesteps')
		
Where:

* `Within`: The option that supports the validation of a set array.
* ``m.timesteps[1:]`` represents the timesteps set starting from the second element, excluding the first timestep :math:`t_0`

Sites
^^^^^

**Sites** are represented by the set :math:`V`. A Site :math:`v` can be any distinct location, a place of
settlement or activity (e.g `process`, `transmission`, `storage`).A site is for example an individual
building, region, country or even continent. Sites can be imagined as nodes(vertices) on a graph of locations,
connected by edges. Index of this set are the descriptions of the Sites (e.g north, middle, south).
In script ``urbs.py`` this set is defined by ``sit`` and initialized by the code fragment:

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
In script ``urbs.py`` this set is defined as ``tra`` and initialized by the code fragment:

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
The Set :math:`R` defines the Cost Types, each member :math:`r` of this set :math:`R` represents a unique cost type name.
The cost types are : ``Investment``, ``Fix``, ``Variable``, ``Fuel``, ``Revenue``, ``Purchase``.
In script ``urbs.py`` this set is defined as ``cost_type`` and initialized by the code fragment:

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

Commodity tuples represent combinations of defined commodities.
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

Process tuples represent combinations of possible processes.
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

Transmission tuples represent combinations of possible transmissions.
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
Storage tuples represent combinations of possible storages by site.
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
Process input tuples represent commodities consumed by processes.
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

Where: ``r_in`` represents the process input ratio.

Process Output Tuples
^^^^^^^^^^^^^^^^^^^^^
Process output tuples represent commodities generated by processes.
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
		
Where: ``r_out`` represents the process output ratio.

Commodity Type Subsets
======================

Commodity Type Subsets represent the commodity tuples only from a given commodity type.
Commodity Type Subsets are subsets of the sets commodity tuples
These subsets can be obtained by fixing the commodity type :math:`q` to a desired commodity type (e.g SupIm, Stock) in the set commodity tuples :math:`C_{vq}`.
Since there are 6 types of commodity types, there are also 6 commodity type subsets. Commodity type subsets are;

	**Supply Intermittent Commodities** (``SupIm``): The set :math:`C_\text{sup}` represents all commodities :math:`c` of commodity type ``SupIm``. Commodities of this type have intermittent timeseries, in other words, availability of these commodities are not constant. These commodities might have various energy content for every timestep :math:`t`. For example solar radiation is contingent on many factors such as sun position, weather and varies permanently.

	**Stock Commodities** (``Stock``): The set :math:`C_\text{st}` represents all commodities :math:`c` of commodity type ``Stock``. Commodities of this type can be purchased at any time for a given price( :math:`k_{vc}^\text{fuel}`).

	**Sell Commodities** (``Sell``): The set :math:`C_\text{sell}` represents all commodities :math:`c` of commodity type ``Sell``. Commodities that can be sold. These Commodities have a sell price ( :math:`k_{vct}^\text{bs}` ) that may vary with the given timestep :math:`t`.

	**Buy Commodities** (``Buy``): The set :math:`C_\text{buy}` represents all commodities :math:`c` of commodity type ``Buy``. Commodities that can be purchased. These Commodities have a buy price ( :math:`k_{vc}^\text{bs}` ) that may vary with the given timestep :math:`t`.

	**Demand Commodities** (``Demand``): The set :math:`C_\text{dem}` represents all commodities :math:`c` of commodity type ``Demand``. Commodities of this type are the requested commodities of the energy system. They are usually the end product of the model (e.g Electricity:Elec).

	**Environmental Commodities** (``Env``): The set :math:`C_\text{env}` represents all commodities :math:`c` of commodity type ``Env``. Commodities of this type are usually the undesired byproducts of processes that might be harmful for environment, optional maximum creation limits can be set to control the generation of these commodities (e.g Greenhouse Gas Emissions: :math:`\text{CO}_2`).

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

Where:

.. function:: commodity_subset(com_tuples, type_name)

  Returns the commodity names(:math:`c`) of the given commodity type(:math:`q`).

  :param com_tuples: A list of tuples (site, commodity, commodity type)
  :param type_name: A commodity type or a list of commodity types

  :return: The set (unique elements/list) of commodity names of the desired commodity type.

Variables
=========
All the variables that the optimization model requires to calculate an optimal
solution will be listed and defined in this section.
A variable is a numerical value that is determined during optimization.
Variables can denote a single, independent value, or an array of
values. Variables define the search space for optimization.
Variables of this optimization model can be seperated into sections by their area of use.
These Sections are Cost, Commodity, Process, Transmission and Storage.

.. table:: *Table: Model Variables*

	+------------------------------------+------+----------------------------------+
	| Variable                           | Unit | Description                      |
	+====================================+======+==================================+
	| **Cost  Variables**                                                          |
	+------------------------------------+------+----------------------------------+
	| :math:`\zeta`                      | €/a  | Total System Cost                |
	+------------------------------------+------+----------------------------------+
	| :math:`\zeta_\text{inv}`           | €/a  | Investment Costs                 |
	+------------------------------------+------+----------------------------------+
	| :math:`\zeta_\text{fix}`           | €/a  | Fix Costs                        |
	+------------------------------------+------+----------------------------------+
	| :math:`\zeta_\text{var}`           | €/a  | Variable Costs                   |
	+------------------------------------+------+----------------------------------+
	| :math:`\zeta_\text{fuel}`          | €/a  | Fuel Costs                       |
	+------------------------------------+------+----------------------------------+
	| :math:`\zeta_\text{rev}`           | €/a  | Revenue Costs                    |
	+------------------------------------+------+----------------------------------+
	| :math:`\zeta_\text{pur}`           | €/a  | Purchase Costs                   |
	+------------------------------------+------+----------------------------------+
	| **Commodity Variables**                                                      |
	+------------------------------------+------+----------------------------------+
	| :math:`\rho_{vct}`                 | MW   | Stock Commodity Source Term      |
	+------------------------------------+------+----------------------------------+
	| :math:`\varrho_{vct}`              | kW   | Sell Commodity Source Term       |
	+------------------------------------+------+----------------------------------+
	| :math:`\psi_{vct}`                 | kW   | Buy Commodity Source Term        |
	+------------------------------------+------+----------------------------------+
	| **Process Variables**                                                        |
	+------------------------------------+------+----------------------------------+
	| :math:`\kappa_{vp}`                | MW   | Total Process Capacity           |
	+------------------------------------+------+----------------------------------+
	| :math:`\hat{\kappa}_{vp}`          | MW   | New Process Capacity             |
	+------------------------------------+------+----------------------------------+
	| :math:`\tau_{vpt}`                 | MW   | Process Throughput               |
	+------------------------------------+------+----------------------------------+
	| :math:`\epsilon_{vcpt}^\text{in}`  | MW   | Process Input Commodity Flow     |
	+------------------------------------+------+----------------------------------+
	| :math:`\epsilon_{vcpt}^\text{out}` | MW   | Process Output Commodity Flow    |
	+------------------------------------+------+----------------------------------+
	| **Transmission Variables**                                                   |
	+------------------------------------+------+----------------------------------+
	| :math:`\kappa_{af}`                | MW   | Total transmission Capacity      |
	+------------------------------------+------+----------------------------------+
	| :math:`\hat{\kappa}_{af}`          | MW   | New Transmission Capacity        |
	+------------------------------------+------+----------------------------------+
	| :math:`\pi_{aft}^\text{in}`        | MW   | Transmission Power Flow (Input)  |
	+------------------------------------+------+----------------------------------+
	| :math:`\pi_{aft}^\text{out}`       | MW   | Transmission Power Flow (Output) |
	+------------------------------------+------+----------------------------------+
	| **Storage Variables**                                                        |
	+------------------------------------+------+----------------------------------+
	| :math:`\kappa_{vs}^\text{c}`       | MW   | Total Storage Size               |
	+------------------------------------+------+----------------------------------+
	| :math:`\hat{\kappa}_{vs}^\text{c}` | MW   | New Storage Size                 |
	+------------------------------------+------+----------------------------------+
	| :math:`\kappa_{vs}^\text{p}`       | MWh  | Total Storage Power              |
	+------------------------------------+------+----------------------------------+
	| :math:`\hat{\kappa}_{vs}^\text{p}` | MWh  | New Storage Power                |
	+------------------------------------+------+----------------------------------+
	| :math:`\epsilon_{vst}^\text{in}`   | MWh  | Storage Power Flow (Input)       |
	+------------------------------------+------+----------------------------------+
	| :math:`\epsilon_{vst}^\text{out}`  | MWh  | Storage Power Flow (Output)      |
	+------------------------------------+------+----------------------------------+
	| :math:`\epsilon_{vst}^\text{con}`  | MW   | Storage Energy Content           |
	+------------------------------------+------+----------------------------------+


	
Cost Variables
^^^^^^^^^^^^^^
**Total System Cost**, :math:`\zeta` : the variable :math:`\zeta` represents
the *annual total expense incurred* in reaching the satisfaction of the given energy demand.
This is calculated by the sum total of all costs by type(:math:`\zeta_r`, :math:`\forall r \in R`) and defined as  ``costs`` by the following code fragment:

::

    m.costs = pyomo.Var(
        m.cost_type,
        within=pyomo.Reals,
        doc='Costs by type (EUR/a)')

More information on calculation of this variable is available at the `Cost Function`_ section.

Total System costs by type: System costs are divided into 6 cost types by their meaning and purpose.
The separation of costs by type, facilitates business planning and provides calculation accuracy
As mentioned before these cost types are hardcoded, which means they are not considered to be fixed or changed by the user.
These cost types are as following;

	**Investment Costs** :math:`\zeta_\text{inv}` : The variable :math:`\zeta_\text{inv}` represents the annualised total investment costs.
		Costs for required new investments on storage, process and transmission technologies.
	
	**Fix Costs** :math:`\zeta_\text{fix}` : The variable :math:`\zeta_\text{fix}` represents the annualised total fix costs.
		Fix costs for all used storage, process, and transmission technologies. Such as maintenance costs.
		
	**Variable Costs** :math:`\zeta_\text{var}` : The variable :math:`\zeta_\text{var}` represents the annualised total variables costs.
		Variable costs that are reliant on the usage amount and period of the storage, process, transmission technologies.
		
	**Fuel Costs** :math:`\zeta_\text{fuel}` : The variable :math:`\zeta_\text{fuel}` represents the annualised total fuel costs.
		Fuel costs are dependent on the usage of stock commodities( :math:`\forall c \in C_\text{stock}`).
		
	**Revenue Costs** :math:`\zeta_\text{rev}` : The variable :math:`\zeta_\text{rev}` represents the annualised total revenue costs.
		Revenue costs is defined for the costs that occures by selling the sell commodities( :math:`\forall c \in C_\text{sell}`).
		Since this variable is an income for the system, it is either zero or has a negative value.
		
	**Purchase Costs** :math:`\zeta_\text{pur}` : The variable :math:`\zeta_\text{pur}` represents the annualised total purchase costs.
		Purchase costs is defined for the costs that occures by buying the buy commodities ( :math:`\forall c \in C_\text{buy}` ).
		
	For more information on calculation of these variables see `Cost Function`_ section.

Commodity Variables
^^^^^^^^^^^^^^^^^^^

**Stock Commodity Source Term**, :math:`\rho_{vct}`, ``e_co_stock``, MW : The variable :math:`\rho_{vct}` represents the energy amount in [MW] that is being used by the system of commodity :math:`c` from type stock (:math:`\forall c \in C_\text{stock}`)  in a site :math:`v` (:math:`\forall v \in V`) at timestep :math:`t` (:math:`\forall t \in T_\text{m}`).
In script ``urbs.py`` this variable is defined by the variable ``e_co_stock`` and initialized by the following code fragment: ::

    m.e_co_stock = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of stock commodity source (MW) per timestep')

**Sell Commodity Source Term**, :math:`\varrho_{vct}`, ``e_co_sell``, kW : The variable :math:`\varrho_{vct}` represents the energy amount in [kW] that is being used by the system of commodity :math:`c` from type sell (:math:`\forall c \in C_\text{sell}`)  in a site :math:`v` (:math:`\forall v \in V`) at timestep :math:`t` (:math:`\forall t \in T_\text{m}`).
In script ``urbs.py`` this variable is defined by the variable ``e_co_sell`` and initialized by the following code fragment: ::

    m.e_co_sell = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of sell commodity source (kW) per timestep')

**Buy Commodity Source Term**, :math:`\psi_{vct}`, ``e_co_buy``, kW : The variable :math:`\psi_{vct}` represents the energy amount in [kW] that is being used by the system of commodity :math:`c` from type buy (:math:`\forall c \in C_\text{buy}`)  in a site :math:`v` (:math:`\forall v \in V`) at timestep :math:`t` (:math:`\forall t \in T_\text{m}`).
In script ``urbs.py`` this variable is defined by the variable ``e_co_buy`` and initialized by the following code fragment: ::

    m.e_co_buy = pyomo.Var(
       m.tm, m.com_tuples,
       within=pyomo.NonNegativeReals,
       doc='Use of buy commodity source (kW) per timestep')

Process Variables
^^^^^^^^^^^^^^^^^

**Total Process Capacity**, :math:`\kappa_{vp}`, ``cap_pro``: The variable :math:`\kappa_{vp}` represents the total potential power output (capacity) of a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`), that is required in the energy system. The total process capacity includes both the already installed process capacity and the additional new process capacity that needs to be installed. Since the costs of the process technologies are mostly directly proportional to the power output of processes, this variable acts as a scale factor of process technologies and helps us to calculate a more accurate cost plan. For further information see Process Capacity Rule.
This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``cap_pro`` and initialized by the following code fragment: ::

    m.cap_pro = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total process capacity (MW)')

**New Process Capacity**, :math:`\hat{\kappa}_{vp}`, ``cap_pro_new``: The variable :math:`\hat{\kappa}_{vp}` represents the power output capacity of a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) that needs to be installed additionally to the energy system in order to  provide the optimal solution.
This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``cap_pro_new`` and initialized by the following code fragment: ::

    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')

**Process Throughput**, :math:`\tau_{vpt}`, ``tau_pro`` : The variable :math:`\tau_{vpt}` represents the power flow through a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) at a timestep :math:`t` (:math:`\forall t \in T_{m}`). This variable is expressed in the unit MW. 
In script ``urbs.py`` this variable is defined by the model variable ``tau_pro`` and initialized by the following code fragment: ::

    m.tau_pro = pyomo.Var(
        m.tm, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow (MW) through process')

**Process Input Commodity Flow**, :math:`\epsilon_{vcpt}^\text{in}`, ``e_pro_in``: The variable :math:`\epsilon_{vcpt}^\text{in}` represents the power flow input into a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) caused by an input commodity :math:`c` (:math:`\forall c \in C`) at a timestep :math:`t` (:math:`\forall t \in T_{m}`). This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``e_pro_in`` and initialized by the following code fragment: ::

    m.e_pro_in = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Power flow of commodity into process (MW) per timestep')


**Process Output Commodity Flow**, :math:`\epsilon_{vcpt}^\text{out}`, ``e_pro_out``: The variable :math:`\epsilon_{vcpt}^\text{out}` represents the power flow output out of a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) caused by an output commodity :math:`c` (:math:`\forall c \in C`) at a timestep :math:`t` (:math:`\forall t \in T_{m}`). This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``e_pro_out`` and initialized by the following code fragment: ::

    m.e_pro_out = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of process (MW) per timestep')

Transmission Variables
^^^^^^^^^^^^^^^^^^^^^^

**Total Transmission Capacity**, :math:`\kappa_{af}`, ``cap_tra``: The variable :math:`\kappa_{af}` represents the total potential transfer power of a transmission tuple :math:`f_{ca}`, where :math:`a` represents the arc from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The total transmission capacity includes both the already installed transmission capacity and the additional new transmission capacity that needs to be installed. This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``cap_tra`` and initialized by the following code fragment: ::

    m.cap_tra = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total transmission capacity (MW)')

**New Transmission Capacity**, :math:`\hat{\kappa}_{af}`, ``cap_tra_new``: The variable :math:`\hat{\kappa}_{af}` represents the additional capacity, that needs to be installed, of a transmission tuple :math:`f_{ca}`, where :math:`a` represents the arc from an origin site :math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``cap_tra_new`` and initialized by the following code fragment: ::

    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')

**Transmission Power Flow (Input)**, :math:`\pi_{aft}^\text{in}`, ``e_tra_in``: The variable :math:`\pi_{aft}^\text{in}` represents the power flow input into a transmission tuple :math:`f_{ca}` at a timestep :math:`t`, where :math:`a` represents the arc from an origin site :math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable is expressed in the unit MW. In script ``urbs.py`` this variable is defined by the model variable ``e_tra_in`` and initialized by the following code fragment: ::

    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into transmission line (MW) per timestep')

**Transmission Power Flow (Output)**, :math:`\pi_{aft}^\text{out}`, ``e_tra_out``: The variable :math:`\pi_{aft}^\text{out}` represents the power flow output out of a transmission tuple :math:`f_{ca}` at a timestep :math:`t`, where :math:`a` represents the arc from an origin site :math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable is expressed in the unit MW. In script ``urbs.py`` this variable is defined by the model variable ``e_tra_out`` and initialized by the following code fragment: ::

    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of transmission line (MW) per timestep')

Storage Variables
^^^^^^^^^^^^^^^^^

**Total Storage Size**, :math:`\kappa_{vs}^\text{c}`, ``cap_sto_c``: The variable :math:`\kappa_{vs}^\text{c}` represents the total load capacity of a storage tuple :math:`s_{vc}`. The total storage load capacity includes both the already installed storage load capacity and the additional new storage load capacity that needs to be installed. This variable is expressed in unit MWh. In script ``urbs.py`` this variable is defined by the model variable ``cap_sto_c`` and initialized by the following code fragment: ::

    m.cap_sto_c = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage size (MWh)')

**New Storage Size**, :math:`\hat{\kappa}_{vs}^\text{c}`, ``cap_sto_c_new``: The variable :math:`\hat{\kappa}_{vs}^\text{c}` represents the additional storage load capacity of a storage tuple :math:`s_{vc}` that needs to be installed to the energy system in order to provide the optimal solution.
This variable is expressed in the unit MWh.
In script ``urbs.py`` this variable is defined by the model variable ``cap_sto_c_new`` and initialized by the following code fragment: ::

    m.cap_sto_c_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New storage size (MWh)')

**Total Storage Power**, :math:`\kappa_{vs}^\text{p}`, ``cap_sto_p``: The variable :math:`\kappa_{vs}^\text{p}` represents the total potential discharge power of a storage tuple :math:`s_{vc}`. The total storage power includes both the already installed storage power and the additional new storage power that needs to be installed. This variable is expressed in the unit MW. In script ``urbs.py`` this variable is defined by the model variable ``cap_sto_p`` and initialized by the following code fragment:
::

    m.cap_sto_p = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage power (MW)')

**New Storage Power**, :math:`\hat{\kappa}_{vs}^\text{p}`, ``cap_sto_p_new``: The variable :math:`\hat{\kappa}_{vs}^\text{p}` represents the additional potential discharge power of a storage tuple :math:`s_{vc}` that needs to be installed to the energy system in order to provide the optimal solution.
This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``cap_sto_p_new`` and initialized by the following code fragment:
::

    m.cap_sto_p_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New  storage power (MW)')

**Storage Power Flow (Input)**, :math:`\epsilon_{vst}^\text{in}`, ``e_sto_in``: The variable :math:`\epsilon_{vst}^\text{in}` represents the input power flow into a storage tuple :math:`s_{vc}` at a timestep :math:`t`. Input power flow into a storage tuple can also be defined as the charge of a storage tuple. This variable is expressed in the unit MW. In script ``urbs.py`` this variable is defined by the model variable ``e_sto_in`` and initialized by the following code fragment:
::

    m.e_sto_in = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into storage (MW) per timestep')

**Storage Power Flow (Output)**, :math:`\epsilon_{vst}^\text{out}`, ``e_sto_out``:  The variable :math:`\epsilon_{vst}^\text{out}` represents the output power flow out of a storage tuple :math:`s_{vc}` at a timestep :math:`t`. Output power flow out of a storage tuple can also be defined as the discharge of a storage tuple. This variable is expressed in the unit MW. In script ``urbs.py`` this variable is defined by the model variable ``e_sto_out`` and initialized by the following code fragment:
::

    m.e_sto_out = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of storage (MW) per timestep')

**Storage Energy Content**, :math:`\epsilon_{vst}^\text{con}`, ``e_sto_con``: The variable :math:`\epsilon_{vst}^\text{con}` represents the energy amount that is loaded in a storage tuple :math:`s_{vc}` at a timestep :math:`t`. This variable is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by the model variable ``e_sto_out`` and initialized by the following code fragment:
::

    m.e_sto_con = pyomo.Var(
        m.t, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Energy content of storage (MWh) in timestep')

Parameters
==========
All the parameters that the optimization model requires to calculate an optimal solution will be listed and defined in this section.
A parameter is a data, that is provided by the user before the optimization simulation starts. These parameters are the values that define the specifications of the modelled energy system. Parameters of this optimization model can be seperated into two main parts, these are Technical and Economical Parameters. 

Technical Parameters
^^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Technical Model Parameters*

	+-----------------------------------+----+--------------------------------------------+
	|Parameter                          |Unit|Description                                 |
	+===================================+====+============================================+
	|**General Technical Parameters**                                                     |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`w`                          | _  |Weight                                      |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\Delta t`                   | h  |Timestep Duration                           |
	+-----------------------------------+----+--------------------------------------------+
	|**Commodity Technical Parameters**                                                   |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`d_{vct}`                    |MW  |Demand for Commodity                        |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`s_{vct}`                    |MW  |Intermittent Supply Capacity Factor         |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{l}_{vc}`          |MW  |Maximum Stock Supply Limit Per Time Step    |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{L}_{vc}`          |MW  |Maximum Annual Stock Supply Limit Per Vertex|
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{m}_{vc}`          |MW  |Maximum Environmental Output Per Time Step  |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{M}_{vc}`          |MW  |Maximum Annual Environmental Output         |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{g}_{vc}`          |MW  |Maximum Sell Limit Per Time Step            |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{G}_{vc}`          |MW  |Maximum Annual Sell Limit                   |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{b}_{vc}`          |MW  |Maximum Buy Limit Per Time Step             |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{B}_{vc}`          |MW  |Maximum Annual Buy Limit                    |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{L}_{CO_2}`        |MW  |Maximum Global Annual CO2 Emission Limit    |
	+-----------------------------------+----+--------------------------------------------+
	|**Process Technical Parameters**                                                     |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{vp}`         |MW  |Process Capacity Lower Bound                |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`K_{vp}`                     |MW  |Process Capacity Installed                  |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vp}`          |MW  |Process Capacity Upper Bound                |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`r_{pc}^\text{in}`           | _  |Process Input Ratio                         |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`r_{pc}^\text{out}`          | _  |Process Output Ratio                        |
	+-----------------------------------+----+--------------------------------------------+
	|**Storage Technical Parameters**                                                     |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`I_{vs}`                     | 1  |Initial and Final Storage Content(relative) |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`e_{vs}^\text{in}`           | _  |Storage Efficiency During Charge            |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`e_{vs}^\text{out}`          | _  |Storage Efficiency During Discharge         |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{vs}^\text{c}`|MWh |Storage Content Lower Bound                 |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`K_{vs}^\text{c}`            |MWh |Storage Content Installed                   |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vs}^\text{c}` |MWh |Storage Content Upper Bound                 |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{vs}^\text{p}`|MW  |Storage Power Lower Bound                   |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`K_{vs}^\text{p}`            |MW  |Storage Power Installed                     |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{vs}^\text{p}` |MW  |Storage Power Upper Bound                   |
	+-----------------------------------+----+--------------------------------------------+
	|**Transmission Technical Parameters**                                                |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`e_{af}`                     | _  |Transmission Efficiency                     |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\underline{K}_{af}`         |MW  |Tranmission Capacity Lower Bound            |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`K_{af}`                     |MW  |Tranmission Capacity Installed              |
	+-----------------------------------+----+--------------------------------------------+
	|:math:`\overline{K}_{af}`          |MW  |Tranmission Capacity Upper Bound            |
	+-----------------------------------+----+--------------------------------------------+

General Technical Parameters
----------------------------
**Weight**, :math:`w`, ``weight``: The variable :math:`w` helps to scale variable costs and emissions from the length of simulation, that the energy system model is being observed, to an annual result. This variable represents the rate of a year (8760 hours) to the observed time span. The observed time span is calculated by the product of number of time steps of the set :math:`T` and the time step duration. In script ``urbs.py`` this variable is defined by the model variable ``weight`` and initialized by the following code fragment:
::

    m.weight = pyomo.Param(
        initialize=float(8760) / (len(m.t) * dt),
        doc='Pre-factor for variable costs and emissions for an annual result')
		

**Timestep Duration**, :math:`\Delta t`, ``dt``: The variable :math:`\Delta t` represents the duration between two sequential timesteps :math:`t_x` and :math:`t_{x+1}`. This is calculated by the subtraction of smaller one from the bigger of the two sequential timesteps :math:`\Delta t = t_{x+1} - t_x`. This variable is the unit of time for the optimization model This variable is expressed in the unit h and by default the value is set to ``1``. In script ``urbs.py`` this variable is defined by the model variable ``dt`` and initialized by the following code fragment:
::

    m.dt = pyomo.Param(
        initialize=dt,
        doc='Time step duration (in hours), default: 1')
		

Commodity Technical Parameters
------------------------------

**Demand for Commodity**, :math:`d_{vct}`, ``m.demand.loc[tm][sit,com]``: The parameter represents the energy amount of a demand commodity tuple :math:`c_{vq}` required at a timestep :math:`t` (:math:`\forall v \in V, q = "Demand", \forall t \in T_m`). The unit of this parameter is MW. This data is to be provided by the user and to be entered in the spreadsheet. The related section for this parameter in the spreadsheet can be found under the "Demand" sheet. Here each row represents another timestep :math:`t` and each column represent a commodity tuple :math:`c_{vq}`. Rows are named after the timestep number :math:`n` of timesteps :math:`t_n`. Columns are named after the combination of site name :math:`v` and commodity name :math:`c` respecting the order and seperated by a period(.). For example (Mid, Elec) represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted in column declarations, because every commodity of this parameter has to be from commodity type `Demand` in any case.

**Intermittent Supply Capacity Factor**, :math:`s_{vct}`, ``m.supim.loc[tm][sit,com]``: The parameter :math:`s_{vct}` represents the normalized availability of a supply intermittent commodity :math:`c` :math:`(\forall c \in C_\text{sup})` in a site :math:`v` at a timestep :math:`t`. In other words this parameter gives the ratio of current available energy amount to maximum potential energy amount of a supply intermittent commodity. This data is to be provided by the user and to be entered in the spreadsheet. The related section for this parameter in the spreadsheet can be found under the "SupIm" sheet. Here each row represents another timestep :math:`t` and each column represent a commodity tuple :math:`c_{vq}`. Rows are named after the timestep number :math:`n` of timesteps :math:`t_n`. Columns are named after the combination of site name :math:`v` and commodity name :math:`c`, in this respective order and seperated by a period(.). For example (Mid.Elec) represents the commodity Elec in site Mid. Commodity Type :math:`q` is omitted in column declarations, because every commodity of this parameter has to be from commodity type `SupIm` in any case.

**Maximum Stock Supply Limit Per Time Step**, :math:`\overline{l}_{vc}`, ``m.commodity.loc[sit,com,com_type]['maxperstep']``: The parameter :math:`\overline{l}_{vc}` represents the maximum energy amount of a stock commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Stock"`) that energy model is allowed to use per time step. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of stock commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{l}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Stock Supply Limit Per Vertex**, :math:`\overline{L}_{vc}`, ``m.commodity.loc[sit,com,com_type]['max']``: The parameter :math:`\overline{L}_{vc}` represents the maximum energy amount of a stock commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Stock"`) that energy model is allowed to use annually. The unit of this parameter is MW. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of stock commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{L}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Environmental Output Per Time Step**, :math:`\overline{m}_{vc}`, ``m.commodity.loc[sit,com,com_type]['maxperstep']``: The parameter :math:`\overline{m}_{vc}` represents the maximum energy amount of an environmental commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Env"`)  that energy model is allowed to produce and release to environment per time step. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of enviromental commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{m}_{vc}`. If there is no desired restriction of an enviromental commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Environmental Output**, :math:`\overline{M}_{vc}`, ``m.commodity.loc[sit,com,com_type]['max']``: The parameter :math:`\overline{M}_{vc}` represents the maximum energy amount of an environmental commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Env"`) that energy model is allowed to produce and release to environment annually. The unit of this parameter is MW. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of an environmental commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{M}_{vc}`. If there is no desired restriction of a stock commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Sell Limit Per Time Step**, :math:`\overline{g}_{vc}`, ``m.commodity.loc[sit,com,com_type][`maxperstep`]``: The parameter :math:`\overline{g}_{vc}` represents the maximum energy amount of a sell commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Sell"`)  that energy model is allowed to sell per time step. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of sell commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{g}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.

**Maximum Annual Sell Limit**, :math:`\overline{G}_{vc}`, ``m.commodity.loc[sit,com,com_type][`max`]``: The parameter :math:`\overline{G}_{vc}` represents the maximum energy amount of a sell commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Sell"`) that energy model is allowed to sell annually. The unit of this parameter is MW. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of sell commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{G}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Buy Limit Per Time Step**, :math:`\overline{b}_{vc}`, ``m.commodity.loc[sit,com,com_type][`maxperstep`]``: The parameter :math:`\overline{b}_{vc}` represents the maximum energy amount of a buy commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Buy"`) that energy model is allowed to buy per time step. The unit of this parameter is MW. This parameter applies to every timestep and does not vary for each timestep :math:`t`. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the sixth column of buy commodity tuples in this sheet with the header label "maxperstep" represents the parameter :math:`\overline{b}_{vc}`. If there is no desired restriction of a sell commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter.


**Maximum Annual Buy Limit**, :math:`\overline{B}_{vc}`, ``m.commodity.loc[sit,com,com_type][`max`]``: The parameter :math:`\overline{B}_{vc}` represents the maximum energy amount of a buy commodity tuple :math:`c_{vq}` (:math:`\forall v \in V , q = "Buy"`) that energy model is allowed to buy annually. The unit of this parameter is MW. This parameter is to be provided by the user and to be entered in spreadsheet. The related section for this parameter in the spreadsheet can be found under the ``Commodity`` sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fifth column of buy commodity tuples in this sheet with the header label "max" represents the parameter :math:`\overline{B}_{vc}`. If there is no desired restriction of a buy commodity tuple usage per timestep, the corresponding cell can be set to "inf" to ignore this parameter. 

**Maximum Global Annual CO**:math:`_\textbf{2}` **Emission Limit**, :math:`\overline{L}_{CO_2}`, ``m.hack.loc['Global CO2 Limit','Value']``: The parameter :math:`\overline{L}_{CO_2}` represents the maximum total energy amount of all environmental commodities that energy model is allowed to produce and release to environment annually. The unit of this parameter is MW. This parameter is optional. If the user desires to set a maximum annual limit to total :math:`CO_2` emission of the whole energy model, this can be done by entering the desired value to the related spreadsheet. The related section for this parameter can be found under the sheet "hacks". Here the the cell where the "Global CO2 limit" row and "value" column intersects stands for the parameter :math:`\overline{L}_{CO_2}`. If the user wants to disable this parameter and restriction it provides, this cell can be set to "inf" or simply be deleted. 

Process Technical Parameters
----------------------------

**Process Capacity Lower Bound**, :math:`\underline{K}_{vp}`, ``m.process.loc[sit,pro]['cap-lo]``: The parameter :math:`\underline{K}_{vp}` represents the minimum amount of power output capacity of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the fourth column with the header label "cap-lo" represents the parameters :math:`\underline{K}_{vp}` belonging to the corresponding process :math:`p` and site :math:`v` combinations. If there is no desired minimum limit for the process capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Process Capacity Installed**, :math:`K_{vp}`, ``m.process.loc[sit,pro]['inst-cap']``: The parameter :math:`K_{vp}` represents the amount of power output capacity of a process :math:`p` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the third column with the header label "inst-cap" represents the parameters :math:`K_{vp}` belonging to the corresponding process :math:`p` and site :math:`v` combinations.

**Process Capacity Upper Bound**, :math:`\overline{K}_{vp}`, ``m.process.loc[sit,pro]['cap-up']``: The parameter :math:`\overline{K}_{vp}` represents the maximum amount of power output capacity of a process :math:`p` at a site :math:`v`, that energy model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the fifth column with the header label "cap-up" represents the parameters :math:`\underline{K}_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. If there is no desired maximum limit for the process capacities, this parameter can be simply set to an unrealistic high value, to ignore this parameter.

**Process Input Ratio**, :math:`r_{pc}^\text{in}`, ``m.r_in.loc[pro,co]``: The parameter :math:`r_{pc}^\text{in}` represents the normalized ratio of the amount of a commodity :math:`c` that goes into a process :math:`p` as an input commodity. The related section for this parameter in the spreadsheet can be found under the "Process-Comodity" sheet. Here each row represents another commodity :math:`c` that either goes in to or comes out of a process :math:`p`. The fourth column with the header label "ratio" represents the parameters of the corresponding process :math:`p`, commodity :math:`c` and direction (In,Out) combinations.

**Process Output Ratio**, :math:`r_{pc}^\text{out}`, ``m.r_out.loc[pro,co]``: The parameter :math:`r_{pc}^\text{out}` represents the normlized ratio of the amount of a commodity :math:`c`, that comes out of a process :math:`p` as an output commodity.  The related section for this parameter in the spreadsheet can be found under the "Process-Comodity" sheet. Here each row represents another commodity :math:`c` that either goes in to or comes out of a process :math:`p`. The fourth column with the header label "ratio" represents the parameters of the corresponding process :math:`p`, commodity :math:`c` and direction (In,Out) combinations.


Basically these ratios show how much of which commodity is consumed and generated by a process :math:`p` in a site :math:`v`.

Storage Technical Parameters
----------------------------

**Initial and Final Storage Content (relative)**, :math:`I_{vs}`, ``m.storage.loc[sit,sto,com]['init']``: The parameter :math:`I_{vs}` represents the initial load factor of a storage :math:`s` in a site :math:`v`. This parameter shows as a percentage, how much of a storage is loaded at the beginning of the simulation. The same value should be preserved at the end of the simulation, to make sure that the optimization model doesn't consume the whole storage content at once and leave it empty at the end, otherwise this would disrupt the continuity of the optimization. The value of this parameter is expressed as a normalized percentage, where "1" represents a fully loaded storage and "0" represents an empty storage. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The twentieth column with the header label "init" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Efficiency During Charge**, :math:`e_{vs}^\text{in}`, ``m.storage.loc[sit,sto,com]['eff-in']``: The parameter :math:`e_{vs}^\text{in}` represents the charge efficiency of a storage :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The charge efficiency shows, how much of a desired energy and accordingly power can be succesfully stored into a storage. The value of this parameter is expressed as a normalized percentage, where "1" represents a charge with no power or energy loss and "0" represents that storage technology consumes whole enery during charge. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The tenth column with the header label "eff-in" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Efficiency During Discharge**, :math:`e_{vs}^\text{out}`, ``m.storage.loc[sit,sto,com]['eff-out']``:  The parameter :math:`e_{vs}^\text{out}` represents the discharge efficiency of a storage :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The discharge efficiency shows, how much of a desired energy and accordingly power can be succesfully retrieved out of a storage.  The value of this parameter is expressed as a normalized efipercentage, where "1" represents a discharge with no power or energy loss and "0" represents that storage technology consumes whole enery during discharge. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The eleventh column with the header label "eff-out" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Content Lower Bound**, :math:`\underline{K}_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['cap-lo-c']``: The parameter :math:`\underline{K}_{vs}^\text{c}` represents the minimum amount of energy content capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have. The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The fifth column with the header label "cap-lo-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.  If there is no desired minimum limit for the storage energy content capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Storage Content Installed**, :math:`K_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['inst-cap-c']``: The parameter :math:`K_{vs}^\text{c}` represents the amount of energy content capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The fourth column with the header label "inst-cap-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Content Upper Bound**, :math:`\overline{K}_{vs}^\text{c}`, ``m.storage.loc[sit,sto,com]['cap-up-c']``: The parameter :math:`\overline{K}_{vs}^\text{c}` represents the maximum amount of energy content capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have.  The unit of this parameter is MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The sixth column with the header label "cap-up-c" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations. If there is no desired maximum limit for the storage energy content capacitites, this parameter can be simply set to ""inf"" or an unrealistic high value, to ignore this parameter.

**Storage Power Lower Bound**, :math:`\underline{K}_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['cap-lo-p']``: The parameter :math:`\underline{K}_{vs}^\text{p}` represents the minimum amount of power output capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that energy system model is allowed to have. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The eighth column with the header label "cap-lo-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.  If there is no desired minimum limit for the storage energy content capacities, this parameter can be simply set to "0", to ignore this parameter. 

**Storage Power Installed**, :math:`K_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['inst-cap-p']``:  The parameter :math:`K_{vs}^\text{c}` represents the amount of power output capacity of a storage :math:`s` storing commodity :math:`c` in a site :math:`v`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The seventh column with the header label "inst-cap-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations.

**Storage Power Upper Bound**, :math:`\overline{K}_{vs}^\text{p}`, ``m.storage.loc[sit,sto,com]['cap-up-p']``: The parameter :math:`\overline{K}_{vs}^\text{p}` represents the maximum amount of power output capacity allowed of a storage :math:`s` storing a commodity :math:`c` in a site :math:`v`, that the energy system model is allowed to have.  The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents a storage technology :math:`s` in a site :math:`v` that stores a commodity :math:`c`. The sixth column with the header label "cap-up-p" represents the parameters for corresponding storage :math:`s`, site :math:`v`, commodity :math:`c` combinations. If there is no desired maximum limit for the storage energy content capacitites, this parameter can be simply set to ""inf"" or an unrealistic high value, to ignore this parameter.

Transmission Technical Parameters
---------------------------------

**Transmission Efficiency**, :math:`e_{af}`, ``m.transmission.loc[sin,sout,tra,com]['eff']``: The parameter :math:`e_{af}` represents the energy efficiency of a transmission :math:`f` that transfers a commodity :math:`c` through an arc :math:`a`. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The ratio of the output energy amount to input energy amount, gives the energy efficiency of a transmission process. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The fifth column with the header label "eff" represents the parameters :math:`e_{af}` of the corresponding combinations.

**Tranmission Capacity Lower Bound**, :math:`\underline{K}_{af}`, ``m.transmission.loc[sin,sout,tra,com]['cap-lo']``: The parameter :math:`\underline{K}_{af}` represents the minimum power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that the energy system model is allowed to have. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The tenth column with the header label "cap-lo" represents the parameters :math:`\underline{K}_{af}` of the corresponding combinations. 

**Tranmission Capacity Installed**, :math:`K_{af}`, ``m.transmission.loc[sin,sout,tra,com]['inst-cap']``: The parameter :math:`K_{af}` represents the amount of power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that is already installed to the energy system at the beginning of the simulation. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission,site in, site out, commodity combination. The tenth column with the header label "inst-cap" represents the parameters :math:`K_{af}` of the corresponding combinations.

**Tranmission Capacity Upper Bound**, :math:`\overline{K}_{af}`, ``m.transmission.loc[sin,sout,tra,com]['cap-up']``: The parameter :math:`\overline{K}_{af}` represents the maximum power output capacity of a transmission :math:`f` transferring a commodity :math:`c` through an arc :math:`a`, that the energy system model is allowed to have. Here an arc :math:`a` defines the connection line from an origin site :math:`v_\text{out}` to a destination site :math:`{v_\text{in}}`. The unit of this parameter is MW. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission, site in, site out, commodity combination. The tenth column with the header label "cap-up" represents the parameters :math:`\overline{K}_{af}` of the corresponding combinations. 

Economical Parameters
^^^^^^^^^^^^^^^^^^^^^

.. table:: *Table: Economical Model Parameters*

	+---------------------------+---------+-------------------------------------------------+
	|Parameter                  |Unit     |Description                                      |
	+===========================+=========+=================================================+
	|:math:`AF`                 | _       |Annuity factor                                   |
	+---------------------------+---------+-------------------------------------------------+
	|**Commodity Economical Parameters**                                                    |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vc}^\text{fuel}` |€/MWh    |Stock Commodity Fuel Costs                       |
	+---------------------------+---------+-------------------------------------------------+
	|:math:`k_{vct}^\text{bs}`  |€/MWh    |Buy/Sell Commodity Buy/Sell Costs                |
	+---------------------------+---------+-------------------------------------------------+
	|**Process Economical Parameters**                                                      |
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
	|**Storage Economical Parameters**                                                      |
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
	|**Transmission Economical Parameters**                                                 |
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

Commodity Economical Parameters
-------------------------------

**Stock Commodity Fuel Costs**, :math:`k_{vc}^\text{fuel}`, ``m.commodity.loc[c]['price']``: The parameter :math:`k_{vc}^\text{fuel}` represents the purchase cost for purchasing one unit (1 MWh) of a stock commodity :math:`c` (:math:`\forall c \in C_\text{stock}`) in a site :math:`v` (:math:`\forall v \in V`) . The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Commodity" sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fourth column of stock commodity tuples (:math:`\forall q = "Stock"`) in this sheet with the header label "price" represents the corresponding parameter :math:`k_{vc}^\text{fuel}`.

**Buy/Sell Commodity Buy/Sell Costs**, :math:`k_{vct}^\text{bs}`, ``com_prices[c].loc[tm]``: The parameter :math:`k_{vct}^\text{bs}` represents the purchase/buy cost for purchasing/selling one unit(1 MWh) of a buy/sell commodity :math:`c` (:math:`\forall c \in C_\text{buy}`)/(:math:`\forall c \in C_\text{sell}`) in a site :math:`v` (:math:`\forall v \in V`) at a timestep :math:`t` (:math:`\forall t \in T_m`). The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Commodity" sheet. Here each row represents another commodity tuple :math:`c_{vq}` and the fourth column of buy/sell commodity tuples (:math:`\forall q = "Buy"`)/(:math:`\forall q = "Sell"`) in this sheet with the header label "price" represents how the parameter :math:`k_{vct}^\text{bs}` will be defined. There are two options for this parameter. This parameter will either be a fix value for the whole simulation duration or will vary with the timesteps :math:`t`. For the first option, if the buy/sell price of a buy/sell commodity is a fix value for the whole simulation duration, this value can be entered directly into the corresponding cell with the unit €/MWh. For the second option, if the buy/sell price of a buy/sell commodity depends on time, accordingly on timesteps, a string (a linear sequence of characters, words, or other data) should be written in the corresponding cell. An example string looks like this: "1,25xBuy" where the first numbers (1,25) represent a coefficient for the price. This value is than multiplied by values from another list given with timeseries. Here the word "Buy" refers to a timeseries located in ""Buy-Sell-Price"" sheet with commodity names, types and timesteps. This timeseries should be filled with time dependent buy/sell price variables. The parameter :math:`k_{vct}^\text{bs}` is then calculated by the product of the price coefficient and the related time variable for a given timestep :math:`t`. This calculation and the decision for one of the two options is executed by the helper function :func:`get_com_price`.

.. function:: get_com_price(instance, tuples)

  :param str instance: a Pyomo ConcreteModel instance
  :param list tuples: a list of (site, commodity, commodity type) tuples
  
  :return: a Pandas DataFrame with entities as columns and timesteps as index
  
  Calculate commodity prices for each modelled timestep.
  Checks whether the input is a float. If it is a float it gets the input value as a fix value for commodity price. Otherwise if the input value is not a float, but a string, it extracts the price coefficient from the string and  multiplies it with a timeseries of commodity price variables.

Process Economical Parameters
-----------------------------

**Weighted Average Cost of Capital for Process**, :math:`i_{vp}`, : The parameter :math:`i_{vp}` represents the weighted average cost of capital for a process technology :math:`p` in a site :math:`v`. The weighted average cost of capital gives the interest rate (%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the ninth column with the header label "wacc" represents the parameters :math:`i_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations. The parameter is given as a percentage, where "0,07" means 7%

**Process Depreciation Period**, :math:`z_{vp}`, (a): The parameter :math:`z_{vp}` represents the depreciation period of a process :math:`p` in a site :math:`v`. The depreciation period gives the economic lifetime (more conservative than technical lifetime) of a process investment. The unit of this parameter is "a", where "a" represents a year of 8760 hours. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the tenth column with the header label "depreciation" represents the parameters :math:`z_{vp}` of the corresponding process :math:`p` and site :math:`v` combinations.

**Annualised Process Capacity Investment Costs**, :math:`k_{vp}^\text{inv}`, ``m.process.loc[p]['inv-cost'] * m.process.loc[p]['annuity-factor']``: The parameter :math:`k_{vp}^\text{inv}` represents the annualised investment cost for adding one unit new capacity of a process technology :math:`p` in a site :math:`v`. The unit of this parameter is €/(MW a). This parameter is derived by the product of annuity factor :math:`AF` and the process capacity investment cost for a given process tuple. The process capacity investment cost is to be given as an input by the user. The related section for the process capacity investment cost in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the sixth column with the header label "inv-cost" represents the process capacity investment costs of the corresponding process :math:`p` and site :math:`v` combinations.

**Process Capacity Fixed Costs**, :math:`k_{vp}^\text{fix}`, ``m.process.loc[p]['fix-cost']``: The parameter :math:`k_{vp}^\text{fix}` represents the fix cost per one unit capacity :math:`\kappa_{vp}` of a process technology :math:`p` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MW a). The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the seventh column with the header label "fix-cost" represents the parameters :math:`k_{vp}^\text{fix}` of the corresponding process :math:`p` and site :math:`v` combinations. 

**Process Variable Costs**, :math:`k_{vp}^\text{var}`, ``m.process.loc[p]['var-cost']``: The parameter :math:`k_{vp}^\text{var}` represents the variable cost per one unit energy throughput :math:`\tau_{vpt}` through a process technology :math:`p` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Process" sheet. Here each row represents another process :math:`p` in a site :math:`v` and the eighth column with the header label "var-cost" represents the parameters :math:`k_{vp}^\text{var}` of the corresponding process :math:`p` and site :math:`v` combinations. 

Storage Economical Parameters
-----------------------------

**Weighted Average Cost of Capital for Storage**, :math:`i_{vs}`, : The parameter :math:`i_{vs}` represents the weighted average cost of capital for a storage technology :math:`s` in a site :math:`v`. The weighted average cost of capital gives the interest rate(%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the nineteenth column with the header label "wacc" represents the parameters :math:`i_{vs}` of the corresponding storage :math:`s` and site :math:`v` combinations. The parameter is given as a percentage, where "0,07" means 7%.

**Storage Depreciation Period**, :math:`z_{vs}`, (a): The parameter :math:`z_{vs}` represents the depreciation period of a storage :math:`s` in a site :math:`v`. The depreciation period gives the economic lifetime (more conservative than technical lifetime) of a storage investment. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the eighteenth column with the header label "depreciation" represents the parameters :math:`z_{vs}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Annualised Storage Power Investment Costs**, :math:`k_{vs}^\text{p,inv}`, ``m.storage.loc[s]['inv-cost-p'] * m.storage.loc[s]['annuity-factor']``: The parameter :math:`k_{vs}^\text{p,inv}` represents the annualised investment cost for adding one unit new power output capacity of a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/(MWh a). This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new power output capacity of a storage :math:`s` in a site :math:`v`, which is to be given as an input parameter by the user. The related section for the storage power output capacity investment cost in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the twelfth column with the header label "inv-cost-p" represents the storage power output capacity investment cost of the corresponding storage :math:`s` and site :math:`v` combinations. 

**Annual Storage Power Fixed Costs**, :math:`k_{vs}^\text{p,fix}`, ``m.storage.loc[s]['fix-cost-p']``: The parameter :math:`k_{vs}^\text{p,fix}` represents the fix cost per one unit power output capacity of a storage technology :math:`s` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MW a). The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the fourteenth column with the header label "fix-cost-p" represents the parameters :math:`k_{vs}^\text{p,fix}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Storage Power Variable Costs**, :math:`k_{vs}^\text{p,var}`, ``m.storage.loc[s]['var-cost-p']``: The parameter :math:`k_{vs}^\text{p,var}` represents the variable cost per unit energy, that is stored in or retrieved from a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the sixteenth column with the header label "var-cost-p" represents the parameters :math:`k_{vs}^\text{p,var}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Annualised Storage Size Investment Costs**, :math:`k_{vs}^\text{c,inv}`, ``m.storage.loc[s]['inv-cost-c'] * m.storage.loc[s]['annuity-factor']``: The parameter :math:`k_{vs}^\text{c,inv}` represents the annualised investment cost for adding one unit new storage capacity to a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/(MWh a). This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new storage capacity of a storage :math:`s` in a site :math:`v`, which is to be given as an input parameter by the user. The related section for the storage content capacity investment cost in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the thirteenth column with the header label "inv-cost-c" represents the storage content capacity investment cost of the corresponding storage :math:`s` and site :math:`v` combinations. 


**Annual Storage Size Fixed Costs**, :math:`k_{vs}^\text{c,fix}`, ``m.storage.loc[s]['fix-cost-c']``: The parameter :math:`k_{vs}^\text{c,fix}` represents the fix cost per one unit storage content capacity of a storage technology :math:`s` in a site :math:`v`, that is charged annually. The unit of this parameter is €/(MWh a). The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the fifteenth column with the header label "fix-cost-c" represents the parameters :math:`k_{vs}^\text{c,fix}` of the corresponding storage :math:`s` and site :math:`v` combinations.

**Storage Usage Variable Costs**, :math:`k_{vs}^\text{c,var}`, ``m.storage.loc[s]['var-cost-c']``: The parameter :math:`k_{vs}^\text{p,var}` represents the variable cost per unit energy, that is conserved in a storage technology :math:`s` in a site :math:`v`. The unit of this parameter is €/MWh. The related section for this parameter in the spreadsheet can be found under the "Storage" sheet. Here each row represents another storage :math:`s` in a site :math:`v` and the seventeenth column with the header label "var-cost-c" represents the parameters :math:`k_{vs}^\text{c,var}` of the corresponding storage :math:`s` and site :math:`v` combinations. The value of this parameter is usually set to zero, but the parameter can be taken advantage of if the storage has a short term usage or has an increased devaluation due to usage, compared to amount of energy stored. 

Transmission Economical Parameters
----------------------------------

**Weighted Average Cost of Capital for Transmission**, :math:`i_{vf}`, : The parameter :math:`i_{vf}` represents the weighted average cost of capital for a transmission :math:`f` transferring commodities through an arc :math:`a`. The weighted average cost of capital gives the interest rate(%) of costs for capital after taxes. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the twelfth column with the header label "wacc" represents the parameters :math:`i_{vf}` of the corresponding transmission :math:`f` and arc :math:`a` combinations. The parameter is given as a percentage, where "0,07" means 7%.

**Tranmission Depreciation Period**, :math:`z_{af}`, (a): The parameter :math:`z_{af}` represents the depreciation period of a transmission :math:`f` transferring commodities through an arc :math:`a`. The depreciation period of gives the economic lifetime (more conservative than technical lifetime) of a transmission investment. The unit of this parameter is €/ (MW a). The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the thirteenth column with the header label "depreciation" represents the parameters :math:`z_{af}` of the corresponding transmission :math:`f` and arc :math:`a` combinations.

**Annualised Transmission Capacity Investment Costs**, :math:`k_{af}^\text{inv}`, ``m.transmission.loc[t]['inv-cost'] * m.transmission.loc[t]['annuity-factor']``: The parameter :math:`k_{af}^\text{inv}` represents the annualised investment cost for adding one unit new transmission capacity to a transmission :math:`f` transferring commodities through an arc :math:`a``. This parameter is derived by the product of annuity factor :math:`AF` and the investment cost for one unit of new transmission capacity of a transmission :math:`f` running through an arc :math:`a`, which is to be given as an input parameter by the user. The unit of this parameter is €/(MW a). The related section for the transmission capacity investment cost in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the sixth column with the header label "inv-cost" represents the transmission capacity investment cost of the corresponding transmission :math:`f` and arc :math:`a` combinations. 

**Annual Transmission Capacity Fixed Costs**, :math:`k_{af}^\text{fix}`, ``m.transmission.loc[t]['fix-cost']``: The parameter :math:`k_{af}^\text{fix}` represents the fix cost per one unit capacity of a transmission :math:`f` transferring commodities through an arc :math:`a`, that is charged annually. The unit of this parameter is €/(MWh a). The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the seventh column with the header label "fix-cost" represents the parameters :math:`k_{af}^\text{fix}` of the corresponding transmission :math:`f` and arc :math:`a` combinations. 

**Tranmission Usage Variable Costs**, :math:`k_{af}^\text{var}`, ``m.transmission.loc[t]['var-cost']``: The parameter :math:`k_{af}^\text{var}` represents the variable cost per unit energy, that is transferred with a transmissiom :math:`f` through an arc :math:`a`. The unit of this parameter is €/ MWh. The related section for this parameter in the spreadsheet can be found under the "Transmission" sheet. Here each row represents another transmission :math:`f` transferring commodities through an arc :math:`a` and the eighth column with the header label "var-cost" represents the parameters :math:`k_{af}^\text{var}` of the corresponding transmission :math:`f` and arc :math:`a` combinations.

Equations
=========

Cost Function
^^^^^^^^^^^^^

The variable total system cost :math:`\zeta` is calculated by the cost function. The cost function is the objective function of the optimization  model. Minimizing the value of the variable total system cost would give the most reasonable solution for the modelled energy system  The formula of the cost function expressed in mathematical notation is as following:

.. math::

	\zeta = \zeta_\text{inv} + \zeta_\text{fix} + \zeta_\text{var} + \zeta_\text{fuel} + \zeta_\text{rev} + \zeta_\text{pur}

The calculation of the variable total system cost is given in ``urbs.py`` by the following code fragment.  

::

	def obj_rule(m):
		return pyomo.summation(m.costs)

The variable total system cost :math:`\zeta` is basically calculated by the summation of every type of total costs. As previously mentioned on `Cost Types`_ these cost types are : ``Investment``, ``Fix``, ``Variable``, ``Fuel``, ``Revenue``, ``Purchase``. The calculation of each single cost types are listed below.

Investment Costs
----------------

The variable investment costs :math:`\zeta_\text{inv}` represent the required annual expenses made, in the hope of future benefits. These expenses are made on every new investment. The possible investments of an energy system in this model are:

1. Additional power output capacity for process technologies.
2. Additional power output capacity for storage technologies and additional content capacity for storage technologies.
3. Additional power output capacity for transmission technologies.

The calculation of total annual investment cost :math:`\zeta_\text{inv}` is expressed by the formula: 

.. math::

	\zeta_\text{inv} = 
	\sum_{\substack{v \in V\\ p \in P}} \hat{\kappa}_{vp} k_p^\text{inv} +
	\sum_{\substack{v \in V\\ s \in S}} \left( \hat{\kappa}_{vs}^\text{c} k_{vs}^\text{c,inv} + \hat{\kappa}_{vs}^\text{p} k_{vs}^\text{p,inv}\right) +
	\sum_{\substack{a \in A\\ f \in F}} \hat{\kappa}_{af} k_{af}^\text{inv}


Total annual investment cost is calculated by the sum of three main summands, these are the investment costs for processes, storages, and transmissions. 

1. The first summand of the formula calculates the required annual investment expenses to install an additional power output capacity to process technologies for every member of the set process tuples :math:`\forall p_v \in P_v`. Total process investment cost for all process tuples is defined by the sum of all possible annual process investment costs, which are calculated seperately for each process tuple ( :math:`p_v`, ``m.pro_tuples``) consisting of process :math:`p` in site :math:`v`. Annual process investment cost for a given process tuple :math:`p_v` is calculated by the product of the variable new process capacity ( :math:`\hat{\kappa}_{vp}`,``m.cap_pro_new``) and the parameter annualised process capacity investment cost ( :math:`k_{vp}^\text{inv}`, ``m.process.loc[p]['inv-cost'] * m.process.loc[p]['annuity-factor']``). In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ p \in P}} \hat{\kappa}_{vp} k_p^\text{inv}

2. The second summand of the formula calculates the required investment expenses to install additional power output capacity and storage content capacity to storage technologies for every member of the set storage tuples ( :math:`\forall s_{vc} \in S_{vc}`). This summand consists of two products:
	* The first product calculates the required annual investment expenses to install an additional storage content capacity to a given storage tuple . This is calculated by the product of the variable new storage size ( :math:`\hat{\kappa}_{vs}^\text{c}`, ``cap_sto_c_new``) and the parameter annualised storage size investment costs ( :math:`k_{vs}^\text{c,inv}`, ``m.storage.loc[s]['inv-cost-c'] * m.storage.loc[s]['annuity-factor']``).
	* The second product calculates the required annual investment expenses to install an additional power output capacity to a given storage tuple. This is calculated by the product of the variable new storage power ( :math:`\hat{\kappa}_{vs}^\text{p}`, ``cap_sto_p_new``) and the parameter annualised storage power investment costs ( :math:`k_{vs}^\text{p,inv}`, ``m.storage.loc[s]['inv-cost-p'] * m.storage.loc[s]['annuity-factor']``).

   These two products for a given storage tuple are than added up. The calculation of investment costs for a given storage tuple is than repeated for every single storage tuple and summed up to calculate the total investment costs for storage technologies. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ s \in S}} ( \hat{\kappa}_{vs}^\text{c} k_{vs}^\text{c,inv} + \hat{\kappa}_{vs}^\text{p} k_{vs}^\text{p,inv})

3. The third and the last summand of the formula calculates the required investment expenses to install additional power output capacity to transmission technologies for every member of the set transmission tuples :math:`\forall f_{ca} \in F_{ca}`. Total transmission investment cost for all transmission tuples is defined by the sum of all possible annual transmission investment costs, which are calculated seperately for each transmission tuple ( :math:`f_{ca}`). Annual transmission investment cost for a given transmission tuple is calculated by the product of the variable new transmission capacity ( :math:`\hat{\kappa}_{af}`, ``cap_tra_new``) and the parameter annualised transmission capacity investment costs ( :math:`k_{af}^\text{inv}`, ``m.transmission.loc[t]['inv-cost'] * m.transmission.loc[t]['annuity-factor']``) for the given transmission tuple. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{a \in A\\ f \in F}} \hat{\kappa}_{af} k_{af}^\text{inv}

As mentioned above the variable investment costs :math:`\zeta_\text{inv}` is calculated by the sum of these 3 summands.

In script ``urbs.py`` the value of the total investment cost is calculated by the following code fragment:

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

The variable fix costs :math:`\zeta_\text{fix}` represents the total annual fixed costs for all used storage, process and transmission technologies. The possible fix costs of an energy system in this model can be divided into sections, these are:

1. Fix costs for process technologies
2. Fix costs for storage technologies
3. Fix costs for transmission technologies.

The calculation of total annual fix cost :math:`\zeta_\text{fix}` is expressed by the formula:

.. math::

	\zeta_\text{fix} = 
	\sum_{\substack{v \in V\\ p \in P}} \kappa_{vp} k_{vp}^\text{fix} +
	\sum_{\substack{v \in V\\ s \in S}} \left( \kappa_{vs}^\text{c} k_{vs}^\text{c,fix} + \kappa_{vs}^\text{p} k_{vs}^\text{p,fix} \right) +
	\sum_{\substack{a \in A\\ f \in F}} \kappa_{af} k_{af}^\text{fix}

Total annual fix cost :math:`\zeta_\text{fix}` is calculated by the sum of three main summands, these are the fix costs for process, storage and transmission technologies.

1. The first summand of the formula calculates the required annual fix cost to keep all the process technologies maintained. This is calculated for every member of the set process tuples :math:`\forall p_v \in P_v`. Total process fix cost for all process tuples is defined by the sum of all possible annual process fix costs, which are calculated seperately for each process tuple ( :math:`p_v`, ``m.pro_tuples``) consisting of process :math:`p` in site :math:`v`. Annual process fix cost for a given process tuple is calculated by the product of the variable total process capacity ( :math:`\kappa_{vp}`, ``cap_pro``) and process capacity fixed cost ( :math:`k_{vp}^\text{fix}`, ``m.process.loc[p]['fix-cost']``). In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ p \in P}} \kappa_{vp} k_{vp}^\text{fix}

2. The second summand of the formula calculates the required fix expenses to keep the power output capacity and storage content capacity of storage technologies maintained. The storage technologies here are, every member of the set storage tuples :math:`\forall s_{vc} \in S_{vc}`. This summand consists of two products:
	* The first product calculates the required annual fix expenses to keep the storage content capacity of a given storage tuple maintained.  This is calculated by the product of the variable total storage size ( :math:`\kappa_{vs}^\text{c}`, ``cap_sto_c``) and the parameter annual storage size fixed costs ( :math:`k_{vs}^\text{c,fix}`, ``m.storage.loc[s]['fix-cost-c']``).
	* The second product calculates the required annual fix expenses to keep the power output capacity of a given storage tuple maintained. This is calculated by the product of the variable total storage power ( :math:`\kappa_{vs}^\text{p}`, ``cap_sto_p``) and the parameter annual storage power fixed costs (:math:`k_{vs}^\text{p,fix}`, ``m.storage.loc[s]['fix-cost-p']``).

   These two products for a given storage tuple are than added up. The calculation of fix costs for a storage tuple is then repeated for every single storage tuple and summed up to calculate the total fix costs for storage technologies. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{v \in V\\ s \in S}} (\kappa_{vs}^\text{c} k_{vs}^\text{c,fix} + \kappa_{vs}^\text{p} k_{vs}^\text{p,fix})

3. The third and the last summand of the formula calculates the required fix expenses to keep the power output capacity of transmission technologies maintained. The transmission technologies here are, every member of the set transmission tuples :math:`\forall f_{ca} \in F_{ca}`. Total transmission fix cost for all transmission tuples is defined by the sum of all possible annual transmission fix costs, which are calculated seperately for each transmission tuple :math:`f_{ca}`. Annual transmission fix cost for a given transmission tuple is calculated by the product of the variable total transmission capacity ( :math:`\kappa_{af}`, ``cap_tra``) and the parameter annual transmission capacity fixed costs ( :math:`k_{af}^\text{fix}`, ``m.transmission.loc[t]['fix-cost']``) for the given transmission tuple :math:`f_{ca}`. In mathematical notation this summand is expressed as:

.. math:: \sum_{\substack{a \in A\\ f \in F}} \kappa_{af} k_{af}^\text{fix}

As mentioned above the variable fix costs :math:`\zeta_\text{fix}` is calculated by the sum of these 3 summands.

In script ``urbs.py`` the value of the total fix cost is calculated by the following code fragment:

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

The variable fuel costs :math:`\zeta_\text{fuel}` represents the total annual expenses that are required to be made to buy stock commodities :math:`c \in C_\text{stock}`. The calculation of the variable total annual fuel cost :math:`\zeta_\text{fuel}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{fuel} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{stock}}} \rho_{vct} k_{vc}^\text{fuel} \Delta t

The variable :math:`\zeta_\text{fuel}` is calculated by the sum of all possible annual fuel costs, defined by the combinations of commodity tuples of commodity type 'Stock'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Stock'}`) and timesteps( :math:`\forall t \in T_m`). These annual fuel costs are calculated by the product of the following elements:

	* The parameter stock commodity fuel cost for a given stock commodity :math:`c` in a site :math:`v`.( :math:`k_{vc}^\text{fuel}`, ``m.commodity.loc[c]['price']``)
	* The variable stock commodity source term for a given stock commodity :math:`c` in a site :math:`v` at a timestep :math:`t`.( :math:`\rho_{vct}`, ``e_co_stock``)
	* The variable timestep duration.( :math:`\Delta t`, ``dt``)
	* The variable weight.( :math:`w`, ``weight``)

In script ``urbs.py`` the value of the total fuel cost is calculated by the following code fragment:
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

The variable revenue costs :math:`\zeta_\text{rev}` represents the total annual expenses that are required to be made to sell sell commodities :math:`c \in C_\text{sell}`. The calculation of the variable total annual revenue cost :math:`\zeta_\text{rev}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{rev} = 
	-w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{sell}}} \varrho_{vct} k_{vct}^\text{bs} \Delta t

The variable :math:`\zeta_\text{rev}` is calculated by the sum of all possible annual revenue costs, defined by the combinations of commodity tuples of commodity type 'Sell'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Sell'}`) and timesteps (:math:`\forall t \in T_m`). These annual revenue costs are calculated by the product of the following elements:

	* The parameter sell commodity sell cost for given sell commodity :math:`c` in a site :math:`v`.( :math:`k_{vct}^\text{bs}`, ``com_prices[c].loc[tm]`` )
	* The variable sell commodity source term for a given sell commodity :math:`c` in a site :math:`v` at a timestep :math:`t`.( :math:`\varrho_{vct}`, ``e_co_sell``)
	* The variable timestep duration.( :math:`\Delta t`, ``dt``)
	* The variable weight.( :math:`w`, ``weight``)
	* Coefficient [-1].

Since this variable is an income for the energy system, it is multiplied with the value -1 to be able to give it in the cost function as a summand.
In script ``urbs.py`` the value of the total revenue cost is calculated by the following code fragment:
::

    elif cost_type == 'Revenue':
        sell_tuples = commodity_subset(m.com_tuples, m.com_sell)
        com_prices = get_com_price(m, sell_tuples)

        return m.costs['Revenue'] == -sum(
            m.e_co_sell[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in sell_tuples)


Purchase Costs
--------------

The variable purchase costs :math:`\zeta_\text{pur}` represents the total annual expenses that are required to be made to purchase buy commodities :math:`c \in C_\text{buy}`. The calculation of the variable total annual purchase cost :math:`\zeta_\text{pur}` is expressed by the following mathematical notation:

.. math::

	\zeta_\text{pur} = 
	w \sum_{t\in T_\text{m}} \sum_{v \in V} \sum_{{\ \quad c \in C_\text{buy}}} \psi_{vct} k_{vct}^\text{bs} \Delta t

The variable :math:`\zeta_\text{pur}` is calculated by the sum of all possible annual purchase costs, defined by the combinations of commodity tuples of commodity type 'Buy'( :math:`\forall c_{vq} \in C_{vq} \land q = \text{'Buy'}`) and timesteps (:math:`\forall t \in T_m`). These annual purchase costs are calculated by the product of the following elements:

	* The parameter buy commodity buy cost for a given buy commodity :math:`c` in a site :math:`v`. ( :math:`k_{vct}^\text{bs}`, ``com_prices[c].loc[tm]`` )
	* The variable buy commodity source term for a given buy commodity :math:`c` in a site :math:`v` at a timestep :math:`t`.( :math:`\psi_{vct}`, ``e_co_buy``)
	* The variable timestep duration.( :math:`\Delta t`, ``dt``)
	* The variable weight.( :math:`w`, ``weight``)

In script ``urbs.py`` the value of the total purchase cost is calculated by the following code fragment:
::

    elif cost_type == 'Purchase':
        buy_tuples = commodity_subset(m.com_tuples, m.com_buy)
        com_prices = get_com_price(m, buy_tuples)

        return m.costs['Purchase'] == sum(
            m.e_co_buy[(tm,) + c] * com_prices[c].loc[tm] * m.weight * m.dt
            for tm in m.tm for c in buy_tuples)

Commodity Balance
^^^^^^^^^^^^^^^^^

The function commodity balance calculates the balance of a commodity :math:`c` in a site :math:`v` at a timestep :math:`t`. Commodity balance function facilitates the formulation of commodity constraints. The formula for commodity balance is expressed in mathematical notation as:

.. math::

	\mathrm{CB}(v,c,t) = 
          \sum_{{p|c \in C_{vp}^\text{in}}} \epsilon_{vcpt}^\text{in}
        - \sum_{{p|c \in C_{vp}^\text{out}}} \epsilon_{vcpt}^\text{out}
        + \sum_{{s\in S_{vc}}} \left( \epsilon_{vst}^\text{in} - \epsilon_{vst}^\text{out} \right)
        + \sum_{{\substack{a\in A_v^\text{s}\\ f \in F_{vc}^\text{exp}}}} \pi_{aft}^\text{in}
        - \sum_{{\substack{a\in A_v^\text{p}\\ f \in F_{vc}^\text{imp}}}} \pi_{aft}^\text{out}

This function sums up for a given commodity :math:`c`, site :math:`v` and timestep :math:`t`;

	* the consumption: Process input commodity flow  :math:`\epsilon_{vcpt}^\text{in}` of all process tuples using the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.
	* the export: Input transmission power flow :math:`\pi_{aft}^\text{in}` of all transmission tuples exporting the commodity :math:`c` from the origin site :math:`v` at the timestep :math:`t`.
	* the storage input: Input power flow :math:`\epsilon_{vst}^\text{in}` of all storage tuples storing the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.

and subtracts for the same given commodity :math:`c`, site :math:`v` and timestep :math:`t`;
	* the creation: Process output commodity flow :math:`\epsilon_{vcpt}^\text{out}` of all process tuples using the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.
	* the import: Output transmission power flow :math:`\pi_{aft}^\text{out}` of all transmission tuples importing the commodity math:`c` to the destination site :math:`v` at the timestep :math:`t`.
	* the storage output: Output power flow :math:`\epsilon_{vst}^\text{out}` of all storage tuples storing the commodity :math:`c` in the site :math:`v` at the timestep :math:`t`.

The value of the function :math:`\mathrm{CB}` being greater than zero :math:`\mathrm{CB} > 0` means that the presence of the commodity :math:`c` in the site :math:`v` at the timestep :math:`t` is getting less than before by the technologies given above. Correspondingly, the value of the function being greater than zero means that the presence of the commodity in the site at the timestep is getting more than before by the technologies given above.

In script ``urbs.py`` the value of the commodity balance function :math:`\mathrm{CB}(v,c,t)` is calculated by the following code fragment: 

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

Further information on this function can be found in Helper function section. :func:`commodity_balance(m, tm, sit, com)`

Constraints
===========

Commodity Constraints
^^^^^^^^^^^^^^^^^^^^^

**Vertex Rule**: Vertex rule is the main constraint that has to be satisfied for every commodity. This constraint is defined differently for each commodity type. The inequality requires, that any imbalance (CB>0, CB<0) of a commodity :math:`c` in a site :math:`v` at a timestep :math:`t` to be balanced by a corresponding source term or demand.

* Environmental commodities :math:`C_\text{env}`: this constraint is not defined for environmental commodities.
* Suppy intermittent commodities :math:`C_\text{sup}`: this constraint is not defined for supply intermittent commodities.
* Stock commodities :math:`C_\text{st}`: For stock commodities, the possible imbalance of the commodity must be supplied by the stock commodity purchases. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from the variable stock commodity source term :math:`\rho_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{st}, t\in T_m\colon \qquad & \qquad - \mathrm{CB}(v,c,t) + \rho_{vct} &\geq 0


* Sell commodities :math:`C_\text{sell}`: For sell commodities, the possible imbalance of the commodity must be supplied by the sell commodity trades. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from minus the variable sell commodity source term :math:`\varrho_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{sell}, t\in T_m\colon \qquad & \qquad  - \mathrm{CB}(v,c,t) - \varrho_{vct} &\geq 0

* Buy commodities :math:`C_\text{buy}`: For buy commodities, the possible imbalance of the commodity must be supplied by the buy commodity purchases. In other words, commodity balance :math:`\mathrm{CB}(v,c,t)` subtracted from the variable buy commodity source term :math:`\psi_{vct}` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as:

.. math::
	\forall v\in V, c\in C_\text{buy}, t\in T_m\colon \qquad & \qquad  - \mathrm{CB}(v,c,t) + \psi_{vct} &\geq 0

* Demand commodities :math:`C_\text{dem}`: For demand commodities, the possible imbalance of the commodity must supply the demand :math:`d_{vct}` of demand commodities :math:`c \C_\text{dem}`. In other words, the parameter demand for commodity subtracted :math:`d_{vct}` from the minus commodity balance :math:`-\mathrm{CB}(v,c,t)` must be greater than or equal to 0 to satisfy this constraint. In mathematical notation this is expressed as: 

.. math::
	\forall v\in V, c\in C_\text{dem}, t\in T_m\colon \qquad & \qquad  - \mathrm{CB}(v,c,t) - d_{vct} &\geq 0

In script ``urbs.py`` the constraint vertex rule is defined and calculated by the following code fragments:

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

**Stock Per Step Rule**: The constraint stock per step rule applies only for commodities of type "Stock" ( :math:`c \in C_\text{st}`). This constraint limits the amount of stock commodity :math:`c \in C_\text{st}`, that can be used by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum stock supply limit per time step :math:`\overline{l}_{vc}`. To satisfy this constraint, the value of the variable stock commodity source term :math:`\rho_{vct}` must be less than or equal to the value of the parameter maximum stock supply limit per time step :math:`\overline{l}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{st}, t\in T_m\colon \qquad & \qquad \rho_{vct} &\leq \overline{l}_{vc}

In script ``urbs.py`` the constraint stock per step rule is defined and calculated by the following code fragment:

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

**Total Stock Rule**: The constraint total stock rule applies only for commodities of type "Stock" (:math:`c \in C_\text{st}`). This constraint limits the amount of stock commodity :math:`c \in C_\text{st}`, that can be used annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual stock supply limit per vertex :math:`\overline{L}_{vc}`. To satisfy this constraint, the annual usage of stock commodity must be less than or equal to the value of the parameter stock supply limit per vertex :math:`\overline{L}_{vc}`. The annual usage of stock commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the parameter stock commodity source term :math:`\rho_{vct}` for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{st}\colon \qquad & \qquad  w \sum_{t\in T_m} \Delta t\, \rho_{vct} &\leq \overline{L}_{vc}

In script ``urbs.py`` the constraint total stock rule is defined and calculated by the following code fragment:

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


**Sell Per Step Rule**: The constraint sell per step rule applies only for commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be sold by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum sell supply limit per time step :math:`\overline{g}_{vc}`. To satisfy this constraint, the value of the variable sell commodity source term :math:`\varrho_{vct}` must be less than or equal to the value of the parameter maximum sell supply limit per time step :math:`\overline{g}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{sell}, t\in T_m\colon \qquad & \qquad \varrho_{vct} &\leq \overline{g}_{vc}

In script ``urbs.py`` the constraint sell per step rule is defined and calculated by the following code fragment:
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


**Total Sell Rule**: The constraint total sell rule applies only for commodities of type "Sell" ( :math:`c \in C_\text{sell}`). This constraint limits the amount of sell commodity :math:`c \in C_\text{sell}`, that can be sold annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual sell supply limit per vertex :math:`\overline{G}_{vc}`. To satisfy this constraint, the annual usage of sell commodity must be less than or equal to the value of the parameter sell supply limit per vertex :math:`\overline{G}_{vc}`. The annual usage of sell commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the parameter sell commodity source term :math:`\varrho_{vct}` for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{sell}\colon \qquad & \qquad  w \sum_{t\in T_m} \Delta t\, \varrho_{vct} &\leq \overline{G}_{vc}

In script ``urbs.py`` the constraint total sell rule is defined and calculated by the following code fragment:
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

**Buy Per Step Rule**: The constraint buy per step rule applies only for commodities of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits the amount of buy commodity :math:`c \in C_\text{buy}`, that can be bought by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum buy supply limit per time step :math:`\overline{b}_{vc}`. To satisfy this constraint, the value of the variable buy commodity source term :math:`\psi_{vct}` must be less than or equal to the value of the parameter maximum buy supply limit per time step :math:`\overline{b}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{buy}, t\in T_m\colon \qquad & \qquad \psi_{vct} &\leq \overline{b}_{vc}

In script ``urbs.py`` the constraint buy per step rule is defined and calculated by the following code fragment:
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

**Total Buy Rule**: The constraint total buy rule applies only for commodities of type "Buy" ( :math:`c \in C_\text{buy}`). This constraint limits the amount of buy commodity :math:`c \in C_\text{buy}`, that can be bought annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual buy supply limit per vertex :math:`\overline{B}_{vc}`. To satisfy this constraint, the annual usage of buy commodity must be less than or equal to the value of the parameter buy supply limit per vertex :math:`\overline{B}_{vc}`. The annual usage of buy commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the parameter buy commodity source term :math:`\psi_{vct}` for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{buy}\colon \qquad & \qquad  w \sum_{t\in T_m} \Delta t\, \psi_{vct} &\leq \overline{B}_{vc}

In script ``urbs.py`` the constraint total buy rule is defined and calculated by the following code fragment:
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

**Environmental Output Per Step Rule**: The constraint environmental output per step rule applies only for commodities of type "Env" ( :math:`c \in C_\text{env}`). This constraint limits the amount of environmental commodity :math:`c \in C_\text{env}`, that can be released to environment by the energy system in the site :math:`v` at the timestep :math:`t`. The limited amount is defined by the parameter maximum environmental output per time step :math:`\overline{m}_{vc}`. To satisfy this constraint, the negative value of the commodity balance for the given environmental commodity :math:`c \in C_\text{env}` must be less than or equal to the value of the parameter maximum environmental output per time step :math:`\overline{m}_{vc}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{env}, t\in T_m\colon \qquad & \qquad -\mathrm{CB}(v,c,t) &\leq \overline{m}_{vc}

In script ``urbs.py`` the constraint environmental output per step rule is defined and calculated by the following code fragment:
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

**Total Environmental Output Rule**: The constraint total environmental output rule applies only for commodities of type "Env" ( :math:`c \in C_\text{env}`). This constraint limits the amount of environmental commodity :math:`c \in C_\text{env}`, that can be released to environment annually by the energy system in the site :math:`v`. The limited amount is defined by the parameter maximum annual environmental output limit per vertex :math:`\overline{M}_{vc}`. To satisfy this constraint, the annual release of environmental commodity must be less than or equal to the value of the parameter maximum annual environmental output :math:`\overline{M}_{vc}`. The annual release of environmental commodity is calculated by the sum of the products of the parameter weight :math:`w`, the parameter timestep duration :math:`\Delta t` and the negative value of commodity balance function, for every timestep :math:`t \in T_m`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, c\in C_\text{env}\colon \qquad & \qquad  - w \sum_{t\in T_m} \Delta t\, \mathrm{CB}(v,c,t) &\leq \overline{M}_{vc}

In script ``urbs.py`` the constraint total environmental output rule is defined and calculated by the following code fragment:
::

    m.res_env_total = pyomo.Constraint(
        m.com_tuples,
        rule=res_env_total_rule,
        doc='total environmental commodity output <= commodity.max')

In script ``urbs.py`` the constraint total environmental output rule is defined and calculated by the following code fragment:
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

**Process Capacity Rule**: The constraint process capacity rule defines the variable total process capacity :math:`\kappa_{vp}`. The variable total process capacity is defined by the constraint as the sum of the parameter process capacity installed :math:`K_{vp}` and the variable new process capacity :math:`\hat{\kappa}_{vp}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P\colon \qquad & \qquad \kappa_{vp} = K_{vp} + \hat{\kappa}_{vp}

In script ``urbs.py`` the constraint process capacity rule is defined and calculated by the following code fragment:
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

**Process Input Rule**: The constraint process input rule defines the variable process input commodity flow :math:`\epsilon_{vcpt}^\text{in}`. The variable process input commodity flow is defined by the constraint as the product of the variable process throughput :math:`\tau_{vpt}` and the parameter process input ratio :math:`r_{pc}^\text{in}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \epsilon^\text{in}_{vcpt} &= \tau_{vpt} r^\text{in}_{pc}

In script ``urbs.py`` the constraint process input rule is defined and calculated by the following code fragment:
::

    m.def_process_input = pyomo.Constraint(
        m.tm, m.pro_input_tuples,
        rule=def_process_input_rule,
        doc='process input = process throughput * input ratio')

::

	def def_process_input_rule(m, tm, sit, pro, co):
		return (m.e_pro_in[tm, sit, pro, co] ==
				m.tau_pro[tm, sit, pro] * m.r_in.loc[pro, co])

**Process Output Rule**: The constraint process output rule defines the variable process output commodity flow :math:`\epsilon_{vcpt}^\text{out}`. The variable process output commodity flow is defined by the constraint as the product of the variable process throughput :math:`\tau_{vpt}` and the parameter process output ratio :math:`r_{pc}^\text{out}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \epsilon^\text{out}_{vpct} &= \tau_{vpt} r^\text{out}_{pc}

In script ``urbs.py`` the constraint process output rule is defined and calculated by the following code fragment:
::

    m.def_process_output = pyomo.Constraint(
        m.tm, m.pro_output_tuples,
        rule=def_process_output_rule,
        doc='process output = process throughput * output ratio')

::

	def def_process_output_rule(m, tm, sit, pro, co):
		return (m.e_pro_out[tm, sit, pro, co] ==
				m.tau_pro[tm, sit, pro] * m.r_out.loc[pro, co])

**Intermittent Supply Rule**: The constraint intermittent supply rule defines the variable process input commodity flow :math:`\epsilon_{vcpt}^\text{in}` for processes :math:`p` that use a supply intermittent commodity :math:`c \in C_\text{sup}` as input. Therefore this constraint only applies if a commodity is an intermittent supply commodity :math:`c \in C_\text{sup}`. The variable process input commodity flow is defined by the constraint as the product of the variable total process capacity :math:`\kappa_{vp}` and the parameter intermittent supply capacity factor :math:`s_{vct}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, c\in C_\text{sup}, t\in T_m\colon \qquad & \qquad \epsilon^\text{in}_{vpct} &= \kappa_{vp} s_{vct}

In script ``urbs.py`` the constraint intermittent supply rule is defined and calculated by the following code fragment:
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

**Process Throughput By Capacity Rule**: The constraint process throughput by capacity rule limits the variable process throughput :math:`\tau_{vpt}`. This constraint prevents processes from exceeding their possible power output capacity. The constraint states that the variable process throughput must be less than or equal to the variable total process capacity :math:`\kappa_{vp}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P, t\in T_m\colon \qquad & \qquad \tau_{vpt} &\leq \kappa_{vp}

In script ``urbs.py`` the constraint process throughput by capacity rule is defined and calculated by the following code fragment:
::

    m.res_process_throughput_by_capacity = pyomo.Constraint(
        m.tm, m.pro_tuples,
        rule=res_process_throughput_by_capacity_rule,
        doc='process throughput <= total process capacity')

::

	def res_process_throughput_by_capacity_rule(m, tm, sit, pro):
		return (m.tau_pro[tm, sit, pro] <= m.cap_pro[sit, pro])

**Process Capacity Limit Rule**: The constraint process capacity limit rule limits the variable total process capacity :math:`\kappa_{vp}`. This constraint restricts a process :math:`p` in a site :math:`v` from having more total power output capacity than an upper bound and having less than a lower bound. The constraint states that the variable total process capacity :math:`\kappa_{vp}` must be greater than or equal to the parameter process capacity lower bound :math:`\underline{K}_{vp}` and less than or equal to the parameter process capacity upper bound :math:`\overline{K}_{vp}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, p\in P\colon \qquad & \qquad  \underline{K}_{vp} \leq \kappa_{vp} \leq \overline{K}_{vp}

In script ``urbs.py`` the constraint process capacity limit rule is defined and calculated by the following code fragment:
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

**Sell Buy Symmetry Rule**: The constraint sell buy symmetry rule defines the total process capacity :math:`\kappa_{vp}` of a process :math:`p` in a site :math:`v` that uses either sell or buy commodities ( :math:`c \in C_\text{sell} \vee C_\text{buy}`), therefore this constraint only applies to processes that use sell or buy commodities. The constraint states that the total process capacities :math:`\kappa_{vp}` of processes that use complementary buy and sell commodities must be equal. Buy and sell commodities are complementary, when a commodity :math:`c` is an output of a process where the buy commodity is an input, and at the same time the commodity :math:`c` is an input commodity of a process where the sell commodity is an output.

In script ``urbs.py`` the constraint sell buy symmetry rule is defined and calculated by the following code fragment:
::

    m.res_sell_buy_symmetry = pyomo.Constraint(
        m.pro_input_tuples,
        rule=res_sell_buy_symmetry_rule,
        doc='total power connection capacity must be symmetric in both directions')

::

	def res_sell_buy_symmetry_rule(m, sit_in, pro_in, coin):
	# constraint only for sell and buy processes
	# and the processes must be in the same site
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

**Transmission Capacity Rule**: The constraint transmission capacity rule defines the variable total transmission capacity :math:`\kappa_{af}`. The variable total transmission capacity is defined by the constraint as the sum of the variable transmission capacity installed :math:`K_{af}` and the variable new transmission capacity :math:`\hat{\kappa}_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \kappa_{af} &= K_{af} + \hat{\kappa}_{af}

In script ``urbs.py`` the constraint transmission capacity rule is defined and calculated by the following code fragment:
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

**Transmission Output Rule**: The constraint transmission output rule defines the variable transmission power flow (output) :math:`\pi_{aft}^\text{out}`. The variable transmission power flow (output) is defined by the constraint as the product of the variable transmission power flow (input) :math:`\pi_{aft}^\text{in}` and the parameter transmission efficiency :math:`e_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F, t\in T_m\colon \qquad & \qquad \pi^\text{out}_{aft} &= \pi^\text{in}_{aft} e_{af}

In script ``urbs.py`` the constraint transmission output rule is defined and calculated by the following code fragment:
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

**Transmission Input By Capacity Rule**: The constraint transmission input by capacity rule limits the variable transmission power flow (input) :math:`\pi_{aft}^\text{in}`. This constraint prevents  transmissions from exceeding their possible power input capacity. The constraint states that the variable transmission power flow (input) :math:`\pi_{aft}^\text{in}` must be less than or equal to the variable total transmission capacity :math:`\kappa_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F, t\in T_m\colon \qquad & \qquad \pi^\text{in}_{aft} &\leq \kappa_{af}

In script ``urbs.py`` the constraint transmission input by capacity rule is defined and calculated by the following code fragment:
::

    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')

::

	def res_transmission_input_by_capacity_rule(m, tm, sin, sout, tra, com):
		return (m.e_tra_in[tm, sin, sout, tra, com] <=
				m.cap_tra[sin, sout, tra, com])

**Transmission Capacity Limit Rule**: The constraint transmission capacity limit rule limits the variable total transmission capacity :math:`\kappa_{af}`. This constraint restricts a transmission :math:`f` through an arc :math:`a` from having more total power output capacity than an upper bound and having less than a lower bound. The constraint states that the variable total transmission capacity :math:`\kappa_{af}` must be greater than or equal to the parameter transmission capacity lower bound :math:`\underline{K}_{af}` and less than or equal to the parameter transmission capacity upper bound :math:`\overline{K}_{af}`. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \underline{K}_{af} &\leq \kappa_{af} \leq \overline{K}_{af}

In script ``urbs.py`` the constraint transmission capacity limit rule is defined and calculated by the following code fragment:
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

**Transmission Symmetry Rule**: The constraint transmission symmetry rule defines the power output capacities of incoming and outgoing arcs :math:`a , a'` of a transmission :math:`f`. The constraint states that the power output capacities :math:`\kappa_{af}` of the incoming arc :math:`a` and the complementary outgoing arc :math:`a'` between two sites must be equal. In mathematical notation this is expressed as:

.. math::

	\forall a\in A, f\in F\colon \qquad & \qquad \kappa_{af} &= \kappa_{a'f}

In script ``urbs.py`` the constraint transmission symmetry rule is defined and calculated by the following code fragment:
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

**Storage State Rule**: The constraint storage state rule is the main storage constraint and it defines the storage energy content of a storage :math:`s` in a site :math:`v` at a timestep :math:`t`. This constraint calculates the storage energy content at a timestep :math:`t` by adding or subtracting differences, such as ingoing and outgoing energy, to/from a storage energy content at a previous timestep :math:`t-1`. Here ingoing energy is given by the product of the variable input storage power flow :math:`\epsilon_{vst}^\text{in}`, the parameter timestep duration :math:`\Delta t` and the parameter storage efficiency during charge :math:`e_{vs}^\text{in}`. Outgoing energy is given by the product of the variable output storage power flow :math:`\epsilon_{vst}^\text{out}` and the parameter timestep duration :math:`\Delta t` divided by the parameter storage efficiency during discharge :math:`e_{vs}^\text{out}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, \forall s\in S, t\in T_\text{m}\colon \qquad & \qquad \epsilon_{vst}^\text{con} = \epsilon_{vs(t-1)}^\text{con}  + \epsilon_{vst}^\text{in} \cdot e_{vs}^\text{in} - \epsilon_{vst}^\text{out} / e_{vs}^\text{out}

In script ``urbs.py`` the constraint storage state rule is defined and calculated by the following code fragment:

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

**Storage Power Rule**: The constraint storage power rule defines the variable total storage power :math:`\kappa_{vs}^\text{p}`. The variable total storage power is defined by the constraint as the sum of the parameter storage power installed :math:`K_{vs}^\text{p}` and the variable new storage power :math:`\hat{\kappa}_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \kappa_{vs}^\text{p} = K_{vs}^\text{p} + \hat{\kappa}_{vs}^\text{p}

In script ``urbs.py`` the constraint storage power rule is defined and calculated by the following code fragment:
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

**Storage Capacity Rule**: The constraint storage capacity rule defines the variable total storage size :math:`\kappa_{vs}^\text{c}`. The variable total storage size is defined by the constraint as the sum of the parameter storage content installed :math:`K_{vs}^\text{c}` and the variable new storage size :math:`\hat{\kappa}_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \kappa_{vs}^\text{c} = K_{vs}^\text{c} + \hat{\kappa}_{vs}^\text{c}

In script ``urbs.py`` the constraint storage capacity rule is defined and calculated by the following code fragment:
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

**Storage Input By Power Rule**: The constraint storage input by power rule limits the variable storage input power flow :math:`\epsilon_{vst}^\text{in}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more input power than the storage power capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{in}` must be less than or equal to the variable total storage power :math:`\kappa_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S, t\in T_m\colon \qquad & \qquad \epsilon_{vst}^\text{in} \leq \kappa_{vs}^\text{p}

In script ``urbs.py`` the constraint storage input by power rule is defined and calculated by the following code fragment:
::

    m.res_storage_input_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_input_by_power_rule,
        doc='storage input <= storage power')

::

	def res_storage_input_by_power_rule(m, t, sit, sto, com):
		return m.e_sto_in[t, sit, sto, com] <= m.cap_sto_p[sit, sto, com]

**Storage Output By Power Rule**: The constraint storage output by power rule limits the variable storage output power flow :math:`\epsilon_{vst}^\text{out}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more output power than the storage power capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{out}` must be less than or equal to the variable total storage power :math:`\kappa_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	 \forall v\in V, s\in S, t\in T\colon \qquad & \qquad \epsilon_{vst}^\text{out} \leq \kappa_{vs}^\text{p}

In script ``urbs.py`` the constraint storage output by power rule is defined and calculated by the following code fragment:
::

    m.res_storage_output_by_power = pyomo.Constraint(
        m.tm, m.sto_tuples,
        rule=res_storage_output_by_power_rule,
        doc='storage output <= storage power')

::

	def res_storage_output_by_power_rule(m, t, sit, sto, co):
		return m.e_sto_out[t, sit, sto, co] <= m.cap_sto_p[sit, sto, co]

**Storage State By Capacity Rule**: The constraint storage state by capacity rule limits the variable storage energy content :math:`\epsilon_{vst}^\text{con}`. This constraint restricts a storage :math:`s` in a site :math:`v` at a timestep :math:`t` from having more storage content than the storage content capacity. The constraint states that the variable :math:`\epsilon_{vst}^\text{con}` must be less than or equal to the variable total storage size :math:`\kappa_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S, t\in T\colon \qquad & \qquad \epsilon_{vst}^\text{con} \leq \kappa_{vs}^\text{c}

In script ``urbs.py`` the constraint storage state by capacity rule is defined and calculated by the following code fragment.
::

    m.res_storage_state_by_capacity = pyomo.Constraint(
        m.t, m.sto_tuples,
        rule=res_storage_state_by_capacity_rule,
        doc='storage content <= storage capacity')

::

	def res_storage_state_by_capacity_rule(m, t, sit, sto, com):
		return m.e_sto_con[t, sit, sto, com] <= m.cap_sto_c[sit, sto, com]

**Storage Power Limit Rule**: The constraint storage power limit rule limits the variable total storage power :math:`\kappa_{vs}^\text{p}`. This contraint restricts a storage :math:`s` in a site :math:`v` from having more total power output capacity than an upper bound and having less than a lower bound. The constraint states that the variable total storage power :math:`\kappa_{vs}^\text{p}` must be greater than or equal to the parameter storage power lower bound :math:`\underline{K}_{vs}^\text{p}` and less than or equal to the parameter storage power upper bound :math:`\overline{K}_{vs}^\text{p}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \underline{K}_{vs}^\text{p} \leq \kappa_{vs}^\text{p} \leq \overline{K}_{vs}^\text{p}

In script ``urbs.py`` the constraint storage power limit rule is defined and calculated by the following code fragment: 
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

**Storage Capacity Limit Rule**: The constraint storage capacity limit rule limits the variable total storage size :math:`\kappa_{vs}^\text{c}`. This contraint restricts a storage :math:`s` in a site :math:`v` from having more total storage content capacity than an upper bound and having less than a lower bound. The constraint states that the variable total storage size :math:`\kappa_{vs}^\text{c}` must be greater than or equal to the parameter storage content lower bound :math:`\underline{K}_{vs}^\text{c}` and less than or equal to the parameter storage content upper bound :math:`\overline{K}_{vs}^\text{c}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \underline{K}_{vs}^\text{c} \leq \kappa_{vs}^\text{c} \leq \overline{K}_{vs}^\text{c}

In script ``urbs.py`` the constraint storage capacity limit rule is defined and calculated by the following code fragment:
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

**Initial And Final Storage State Rule**: The constraint initial and final storage state rule defines and restricts the variable storage energy content :math:`\epsilon_{vst}^\text{con}` of a storage :math:`s` in a site :math:`v` at the initial timestep :math:`t_1` and at the final timestep :math:`t_N`.  

Initial Storage:  Initial storage represents how much energy is installed in a storage at the beginning of the simulation. The variable storage energy content :math:`\epsilon_{vst}^\text{con}` at the initial timestep :math:`t_1` is defined by this constraint. The constraint states that the variable :math:`\epsilon_{vst_1}^\text{con}` must be equal to the product of the parameters storage content installed :math:`K_{vs}^\text{c}` and  initial and final storage content :math:`I_{vs}`. In mathematical notation this is expressed as: 

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \epsilon_{vst_1}^\text{con} = \kappa_{vs}^\text{c} I_{vs}

Final Storage: Final storage represents how much energy is installed in a storage at the end of the simulation. The variable storage energy content :math:`\epsilon_{vst}^\text{con}` at the final timestep :math:`t_N` is restricted by this constraint. The constraint states that the variable :math:`\epsilon_{vst_N}^\text{con}` must be greater than or equal to the product of the parameters storage content installed :math:`K_{vs}^\text{c}` and  initial and final storage content :math:`I_{vs}`. In mathematical notation this is expressed as:

.. math::

	\forall v\in V, s\in S\colon \qquad & \qquad \epsilon_{vst_N}^\text{con} \geq \kappa_{vs}^\text{c} I_{vs}

In script ``urbs.py`` the constraint initial and final storage state rule is defined and calculated by the following code fragment:
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

**Global CO2 Limit Rule**: The constraint global CO2 limit rule applies to the whole energy system, that is to say it applies to every site and timestep in general. This constraints restricts the energy model from releasing more environmental commodities, namely CO2 to environment than allowed. The constraint states that the sum of released environmental commodities for every site :math:`v` and every timestep :math:`t` must be less than or equal to the parameter maximum global annual CO2 emission limit :math:`\overline{L}_{CO_{2}}`, where the amount of released enviromental commodites in a single site :math:`v` at a single timestep :math:`t` is calculated by the product of commodity balance of enviromental commodities :math:`\mathrm{CB}(v,CO_{2},t)` and the parameter weight :math:`w`. This constraint is skipped if the value of the parameter :math:`\overline{L}_{CO_{2}}` is set to ``inf``. In mathematical notation this constraint is expressed as:

.. math::

	w \sum_{t\in T_\text{m}} \sum_{v \in V} \mathrm{CB}(v,CO_{2},t) \leq \overline{L}_{CO_{2}}

In script ``urbs.py`` the constraint global CO2 limit rule is defined and calculated by the following code fragment:
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

