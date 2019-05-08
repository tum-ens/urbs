.. module:: urbs

Sets
====

Since urbs is a linear optimization model with many objects
(e.g variables, parameters), it is reasonable to use sets to define the groups
of objects. With the usage of sets, many facilities are provided, such as
understanding the main concepts of the model. Many objects are represented by
various sets, therefore sets can be easily used to check whether some object
has a specific characteristic or not. Additionally sets are useful to define a
hierarchy of objects. Mathematical notation of sets are expressed with
uppercase letters, and their members are usually expressed with the same
lowercase letters. Main sets, tuple sets and subsets will be introduced in this
respective order.

Elementary sets
---------------

.. table:: *Table: Model Sets*
	
	======================== =====================
	Set                      Description
	======================== =====================
	:math:`t \in T`          Timesteps
	:math:`t \in T_\text{m}` Modelled Timesteps
	:math:`y \in Y`          Support timeframes
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

The model urbs is considered to observe a energy system model and calculate the
optimal solution within a limited span of time. This limited span of time is
viewed as a discrete variable, which means values of variables are viewed as
occurring only at distinct timesteps. The set of **time steps**
:math:`T = \{t_0,\dots,t_N\}` for :math:`N` in :math:`\mathbb{N}` represents
Time. This set contains :math:`N+1` sequential time steps with equal spaces.
Each time step represents another point in time. At the initialisation of the
model this set is fixed by the user by setting the variable ``timesteps`` in
script ``runme.py``. Duration of space between timesteps
:math:`\Delta t = t_{x+1} - t_x`, length of simulation :math:`\Delta t \cdot N`
and time interval :math:`[t_0,t_N]` can be fixed to satisfy the needs of the
user. In code this set is defined by the set ``t`` and initialized by the
section:

::

    m.t = pyomo.Set(
        initialize=m.timesteps,
        ordered=True,
        doc='Set of timesteps')
		
Where:

* `Initialize`: A function that receives the set indices and model to return
  the value of that set element, initializes the set with data.
* `Ordered`: A boolean value that indicates whether the set is ordered.
* `Doc`: A string describing the set.

Modelled Timesteps
^^^^^^^^^^^^^^^^^^

The Set, **modelled timesteps**, is a subset of the time steps set. The only
difference between modelled timesteps set and the timesteps set is that the
initial timestep :math:`t_0` is not included. All other features of the set
time steps also apply to the set of modelled timesteps. This set is the main
time set used in the model. The distinction with the set **timesteps** is only 
required to facilitate the definition of the storage state equation. In script
``model.py`` this set is defined by the set ``tm`` and initialized by the code
fragment:

::

    m.tm = pyomo.Set(
        within=m.t,
        initialize=m.timesteps[1:],
        ordered=True,
        doc='Set of modelled timesteps')
		
Where:

* `Within`: The option that supports the validation of a set array.
* ``m.timesteps[1:]`` represents the timesteps set starting from the second
  element, excluding the first timestep :math:`t_0`

Support timeframes
^^^^^^^^^^^^^^^^^^

**Support timeframes** are represented by the set :math:`Y`. They represent the
explicitly modeled support timeframes, e.g., years, for intertemporal models.
In script ``model.py`` the set is defined as:

::

    m.stf = pyomo.Set(
        initialize=(m.commodity.index.get_level_values('support_timeframe')
                    .unique()),
        doc='Set of modeled support timeframes (e.g. years)')

Sites
^^^^^

**Sites** are represented by the set :math:`V`. A Site :math:`v` can be any
distinct location, a place of settlement or activity (e.g `process`,
`transmission`, `storage`).A site is for example an individual building,
region, country or even continent. Sites can be imagined as nodes(vertices) on
a graph of locations, connected by edges. Index of this set are the
descriptions of the Sites (e.g north, middle, south). In script ``model.py``
this set is defined by ``sit`` and initialized by the code fragment:

::

    m.sit = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Site').unique(),
        doc='Set of sites')
		
Commodities
^^^^^^^^^^^

As explained in the Overview section, **commodities** are goods that can be
generated, stored, transmitted or consumed. The set of Commodities represents
all goods that are relevant to the modelled energy system, such as all energy
carriers, inputs, outputs, intermediate substances. (e.g Coal, CO2, Electric,
Wind) By default, commodities are given by their energy content (MWh). Usage of
some commodities are limited by a maximum value or maximum value per timestep
due to their availability or restrictions, also some commodities have a price
that needs to be compensated..(e.g coal, wind, solar).In script ``model.py``
this set is defined by ``com`` and initialized by the code fragment:

::

    m.com = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Commodity').unique(),
        doc='Set of commodities')
		
Commodity Types
^^^^^^^^^^^^^^^
Commodities differ in their usage purposes, consequently **commodity types**
are introduced to subdivide commodities by their features. These Types are hard
coded as ``SupIm``, ``Stock``, ``Demand``, ``Env``, ``Buy``, ``Sell``. In
script ``model.py`` this set is defined as ``com_type`` and initialized by the
code fragment:

::

    m.com_type = pyomo.Set(
        initialize=m.commodity.index.get_level_values('Type').unique(),
        doc='Set of commodity types')
		

Processes
^^^^^^^^^

One of the most important elements of an energy system is the **process**. A
process :math:`p` can be defined by the action of changing one or more forms of
energy, i.e. commodities, to others. In our modelled energy system, processes
convert input commodities into output commodities. Process technologies are
represented by the set processes :math:`P`. Different processes technologies
have fixed input and output commodities. These input and output commodities can
be either single or multiple regardless of each other. Some example members of
this set can be: `Wind Turbine`,`Gas Plant`, `Photovoltaics`. In script
``model.py`` this set is defined as ``pro`` and initialized by the code
fragment:

::

    m.pro = pyomo.Set(
        initialize=m.process.index.get_level_values('Process').unique(),
        doc='Set of conversion processes')

        
Storages
^^^^^^^^

Energy **Storage** is provided by technical facilities that store energy to
generate a commodity at a later time for the purpose of meeting the demand.
Occasionally, on-hand commodities may not be able to satisfy the required
amount of energy to meet the demand, or the available amount of energy may be
much more than required.Storage technologies play a major role in such
circumstances. The Set :math:`S` represents all storage technologies (e.g
`Pump storage`). In script ``model.py`` this set is defined as ``sto`` and
initialized by the code fragment:

::

    m.sto = pyomo.Set(
        initialize=m.storage.index.get_level_values('Storage').unique(),
        doc='Set of storage technologies')
		
Transmissions
^^^^^^^^^^^^^

**Transmissions** :math:`f \in F` represent possible conveyances of commodities
between sites. Transmission process technologies can vary between different
commodities, due to distinct physical attributes and forms of commodities. Some
examples for Transmission technologies are: `hvac`, `hvdc`, `pipeline`) In
script ``model.py`` this set is defined as ``tra`` and initialized by the code
fragment:

::

    m.tra = pyomo.Set(
        initialize=m.transmission.index.get_level_values('Transmission').unique(),
        doc='Set of transmission technologies')
		
.. _sec-cost-types:
        
Cost Types
^^^^^^^^^^

One of the major goals of the model is to calculate the costs of a simulated
energy system. There are 6 different types of costs. Each one has different
features and are defined for different instances. Set of **cost types** is
hardcoded, which means they are not considered to be fixed or changed  by the
user. The Set :math:`R` defines the Cost Types, each member :math:`r` of this
set :math:`R` represents a unique cost type name. The cost types are hard coded
as: ``Investment``, ``Fix``, ``Variable``, ``Fuel``, ``Revenue``, ``Purchase``,
``Startup``. In script ``model.py`` this set is defined as ``cost_type`` and
initialized by the code fragment:

::

    m.cost_type = pyomo.Set(
        initialize=['Inv', 'Fix', 'Var', 'Fuel','Revenue','Purchase','Startup'],
        doc='Set of cost types (hard-coded)')
		

Tuple Sets
----------

A tuple is finite, ordered collection of elements. For example, the tuple
``(hat,red,large)`` consists of 3 ordered elements and defines another element
itself. Tuples are needed in this model to define the combinations of elements
from different sets. Defining a tuple lets us assemble related elements and use
them as a single element. These tuples are then collected into tuple sets.
These tuple sets are then immensely useful for efficient indexing of model
variables and parameters and for defining the constraint rules.

Commodity Tuples
^^^^^^^^^^^^^^^^

Commodity tuples represent combinations of defined commodities.
These are represented by the set :math:`C_{yvq}`. A member :math:`c_{yvq}` in
set :math:`C_{yvq}` is a commodity :math:`c` of commodity type :math:`q` in
support timeframe :math:`y` and site :math:`v`. For example, `(2020, Mid, Elec,
Demand)` is interpreted as commodity `Elec` of commodity type `Demand` in the
year `2020` in site `Mid`. This set is defined as ``com_tuples`` and given by
the code fragment:

::

    m.com_tuples = pyomo.Set(
        within=m.stf*m.sit*m.com*m.com_type,
        initialize=m.commodity.index,
        doc='Combinations of defined commodities, e.g. (2020,Mid,Elec,Demand)')
		

Process Tuples
^^^^^^^^^^^^^^

Process tuples represent possible placements of processes within the model.
These are represented by the set :math:`P_v`. A member :math:`p_{yv}` in set
:math:`P_{yv}` is a process :math:`p` in support timeframe :math:`y` and site
:math:`v`. For example, `(2020, North, Coal Plant)` is interpreted as process
`Coal Plant` in site `North` in the year `2020`. This set is defined as
``pro_tuples`` and given by the code fragment:

::

    m.pro_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=m.process.index,
        doc='Combinations of possible processes, e.g. (2020,North,Coal plant)')

There are three subsets defined for process tuples, which each activate a
different set of modeling constraints.

The first subset of the process tuples ``pro_partial_tuples``
:math:`P_{yv}^\text{partial}` is formed in order to identify processes that
have partial operation properties. Programmatically, they are identified by
those processes, which have the parameter ``ratio-min`` set for one of their
input commodities in table *Process-Commodity*. The tuple set is defined as:
        
::

    m.pro_partial_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=[(stf, site, process)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, _) in m.r_in_min_fraction.index
                    if process == pro and s == stf],
        doc='Processes with partial input')        

The second subset is formed in order to capture all processes that take up a
certain area and are thus subject to the area constraint at the given site.
These processes are identified by the parameter ``area-per-cap`` set in table
*Process*, if at the same time a value for ``area`` is set in table *Site*. The
tuple set is defined as:
  
::

    m.pro_area_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=m.proc_area.index,
        doc='Processes and Sites with area Restriction')

Finally, processes that are subject to restrictions in the change of
operational state are captured with the ``pro_maxgrad_tuples``. This subset is
defined as:

::

    m.pro_maxgrad_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro,
        initialize=[(stf, sit, pro)
                    for (stf, sit, pro) in m.pro_tuples
                    if m.process.loc[stf, sit, pro]['max-grad'] < 1.0 / dt],
        doc='Processes with maximum gradient smaller than timestep length')

Transmission Tuples
^^^^^^^^^^^^^^^^^^^

Transmission tuples represent possible transmissions. These are represented by
the set :math:`F_{yc{v_\text{out}}{v_\text{in}}}`. A member
:math:`f_{yc{v_\text{out}}{v_\text{in}}}` in set
:math:`F_{yc{v_\text{out}}{v_\text{in}}}` is a transmission :math:`f`,that is
directed from an origin site :math:`v_\text{out}` to a destination site
:math:`v_{in}` and carrying the commodity :math:`c` in support timeframe
:math:`y`. The term "\ `directed from an origin site` :math:`v_\text{out}`
`to a destination site` :math:`v_\text{in}`" can also be defined as an arc
:math:`a` . For example, `(2020, South, Mid, hvac, Elec)` is interpreted as
transmission `hvac` that is directed from origin site `South` to destination
site `Mid` carrying commodity `Elec` in year `2020`. This set is defined as
``tra_tuples`` and given by the code fragment:

::

    m.tra_tuples = pyomo.Set(
        within=m.stf*m.sit*m.sit*m.tra*m.com,
        initialize=m.transmission.index,
        doc='Combinations of possible transmissions, e.g. '
            '(2020,South,Mid,hvac,Elec)')


Storage Tuples
^^^^^^^^^^^^^^
Storage tuples label storages. They are represented by the set :math:`S_{yvc}`.
A member :math:`s_{yvc}` in set :math:`S_{yvc}` is a storage :math:`s` of
commodity :math:`c` in site :math:`v` and support timeframe :math:`y` For
example, `(2020, Mid, Bat, Elec)` is interpreted as storage `Bat` for commodity
`Elec` in site `Mid` in the year `2020`. This set is defined as ``sto_tuples``
and given by the code fragment:

::

    m.sto_tuples = pyomo.Set(
        within=m.stf*m.sit*m.sto*m.com,
        initialize=m.storage.index,
        doc='Combinations of possible storage by site,'
            'e.g. (2020,Mid,Bat,Elec)')

There are two subsets of storage tuples.

In a first subset of the storage tuples are all storages that have a user
defined fixed value for the initial state are collected.

::
    
    m.sto_init_bound_tuples = pyomo.Set(
        within=m.stf*m.sit*m.sto*m.com,
        initialize=m.stor_init_bound.index,
        doc='storages with fixed initial state')

A second subset is defined for all storages that have a fixed ratio between
charging/discharging power and storage content.

::
    
    m.sto_ep_ratio_tuples = pyomo.Set(
        within=m.stf*m.sit*m.sto*m.com,
        initialize=tuple(m.sto_ep_ratio_dict.keys()),
        doc='storages with given energy to power ratio')


Process Input Tuples
^^^^^^^^^^^^^^^^^^^^
Process input tuples represent commodities consumed by processes. These are
represented by the set :math:`C_{yvp}^\text{in}`. A member
:math:`c_{yvp}^\text{in}` in set :math:`C_{vp}^\text{in}` is a commodity
:math:`c` consumed by the process :math:`p` in site :math:`v` in support
timeframe :math:`y`. For example, `(2020, Mid, PV, Solar)` is interpreted as
commodity `Solar` consumed by the process `PV` in the site `Mid` in the year
`2020`. This set is defined as ``pro_input_tuples`` and given by the code
fragment:

::

    m.pro_input_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in m.r_in.index
                    if process == pro and s == stf],
        doc='Commodities consumed by process by site,'
            'e.g. (2020,Mid,PV,Solar)')

Where: ``r_in`` represents the process input ratio as set in the input.

For processes in the tuple set ``pro_partial_tuples``, the following tuple set
``pro_partial_input_tuples`` enumerates their input commodities. It is used to
index the constraints that modifies a process' input commodity flow with
respect to the standard case without partial operation. It is defined by the
following code fragment:

::
        
    m.pro_partial_input_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_partial_tuples
                    for (s, pro, commodity) in m.r_in_min_fraction.index
                    if process == pro and s == stf],
        doc='Commodities with partial input ratio,'
            'e.g. (2020,Mid,Coal PP,Coal)')


Process Output Tuples
^^^^^^^^^^^^^^^^^^^^^
Process output tuples represent commodities generated by processes. These are
represented by the set :math:`C_{yvp}^\text{out}`. A member
:math:`c_{yvp}^\text{out}` in set :math:`C_{yvp}^\text{out}` is a commodity
:math:`c` generated by the process :math:`p` in site :math:`v` and support
timeframe :math:`y`. For example, `(2020, Mid,PV,Elec)` is interpreted as the
commodity `Elec` is generated by the process `PV` in the site `Mid` in the year
`2020`. This set is defined as ``pro_output_tuples`` and given by the code
fragment:

::

    m.pro_output_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_tuples
                    for (s, pro, commodity) in m.r_out.index
                    if process == pro and s == stf],
        doc='Commodities produced by process by site, e.g. (2020,Mid,PV,Elec)')
		
Where: ``r_out`` represents the process output ratio as set in the input.

There are two alternative tuple sets that are active whenever their respective
features are set in the input.

First, for processes in the tuple set ``pro_partial_tuples``, the tuple set
``pro_partial_output_tuples`` enumerates their output commodities. It is used
to index the constraints that modifies a process' output commodity flow with
respect to the standard case without partial operation. It is defined by the
following code fragment:

::
        
    m.pro_partial_output_tuples = pyomo.Set(
        within=m.stf*m.sit*m.pro*m.com,
        initialize=[(stf, site, process, commodity)
                    for (stf, site, process) in m.pro_partial_tuples
                    for (s, pro, commodity) in m.r_out_min_fraction.index
                    if process == pro and s == stf],
        doc='Commodities with partial input ratio, e.g. (Mid,Coal PP,CO2)')

Second, the output of all processes that have a time dependent efficiency are
collected in an additional tuple set. The set contains all outputs
corresponding to processes that are specified as column indices in the input
file worksheet ``TimeVarEff``.
::

    m.pro_timevar_output_tuples = pyomo.Set(
        within=m.sit*m.pro*m.com,
        initialize=[(site, process, commodity)
                    for (site, process) in m.eff_factor.columns.values
                    for (pro, commodity) in m.r_out.index
                    if process == pro],
        doc='Outputs of processes with time dependent efficiency')

Demand Side Management Tuples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There are two kinds of demand side management (DSM) tuples in the model:
DSM site tuples :math:`D_{yvc}` and DSM down tuples
:math:`D_{yvct,tt}^\text{down}`. The first kind :math:`D_{yvc}` represents all
possible combinations of support timeframe :math:`y`, site :math:`v` and
commodity :math:`c` of the DSM sheet. It is given by the code fragment:

::

    m.dsm_site_tuples = pyomo.Set(
        within=m.stf*m.sit*m.com,
        initialize=m.dsm.index,
        doc='Combinations of possible dsm by site, e.g. (2020, Mid, Elec)')
        
The second kind :math:`D_{t,tt,yvc}^\text{down}` refers to all possible DSM
downshift possibilities. It is defined to overcome the difficulty caused by the
two time indices of the DSM downshift variable. Dependend on support timeframe
:math:`y`, site :math:`v` and commodity :math:`c` the tuples contain two time
indices. For example `(5001, 5003, 2020, Mid, Elec)` is intepreted as the
downshift in timestep `5003`, which was caused by the upshift of timestep
`5001` in year `2020 and `site `Mid` for commodity `Elec`. The tuples are given
by the following code fragment:

::

    m.dsm_down_tuples = pyomo.Set(
        within=m.tm*m.tm*m.stf*m.sit*m.com,
        initialize=[(t, tt, stf, site, commodity)
                    for (t, tt, stf, site, commodity)
                    in dsm_down_time_tuples(m.timesteps[1:],
                                            m.dsm_site_tuples,
                                            m)],
        doc='Combinations of possible dsm_down combinations, e.g. '
            '(5001,5003,2020,Mid,Elec)')

where the following function is utilized:

.. literalinclude:: /../urbs/features/dsm.py
   :pyobject: dsm_down_time_tuples


Commodity Type Subsets
----------------------

Commodity Type Subsets represent the commodity tuples only from a given
commodity type. Commodity Type Subsets are subsets of the sets commodity tuples
These subsets can be obtained by fixing the commodity type :math:`q` to a
desired commodity type (e.g SupIm, Stock) in the set commodity tuples
:math:`C_{vq}`. Since there are 6 types of commodity types, there are also 6
commodity type subsets. Commodity type subsets are;

**Supply Intermittent Commodities** (``SupIm``): The set :math:`C_\text{sup}`
represents all commodities :math:`c` of commodity type ``SupIm``. Commodities
of this type have intermittent timeseries, in other words, availability of
these commodities are not constant. These commodities might have various energy
content for every timestep :math:`t`. For example solar radiation is contingent
on many factors such as sun position, weather and varies permanently.

**Stock Commodities** (``Stock``): The set :math:`C_\text{st}` represents all
commodities :math:`c` of commodity type ``Stock``. Commodities of this type can
be purchased at any time for a given price( :math:`k_{vc}^\text{fuel}`).

**Sell Commodities** (``Sell``): The set :math:`C_\text{sell}` represents all
commodities :math:`c` of commodity type ``Sell``. Commodities that can be sold.
These Commodities have a sell price ( :math:`k_{vct}^\text{bs}` ) that may vary
with the given timestep :math:`t`.

**Buy Commodities** (``Buy``): The set :math:`C_\text{buy}` represents all
commodities :math:`c` of commodity type ``Buy``. Commodities that can be
purchased. These Commodities have a buy price ( :math:`k_{vc}^\text{bs}` ) that
may vary with the given timestep :math:`t`.

**Demand Commodities** (``Demand``): The set :math:`C_\text{dem}` represents
all commodities :math:`c` of commodity type ``Demand``. Commodities of this
type are the requested commodities of the energy system. They are usually the
end product of the model (e.g Electricity:Elec).

**Environmental Commodities** (``Env``): The set :math:`C_\text{env}`
represents all commodities :math:`c` of commodity type ``Env``. Commodities of
this type are usually the undesired byproducts of processes that might be
harmful for environment, optional maximum creation limits can be set to control
the generation of these commodities
(e.g Greenhouse Gas Emissions: :math:`\text{CO}_2`).

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

  Returns the commodity names(:math:`c`) of the given commodity
  type(:math:`q`).

  :param com_tuples: A list of tuples (site, commodity, commodity type)
  :param type_name: A commodity type or a list of commodity types

  :return: The set (unique elements/list) of commodity names of the desired
           commodity type.
  

Operational state tuples
------------------------

For intertemporal optimization the operational state of units in a support
timeframe `y` has to be calculated from both the initially installed units and
their remaining lifetime and the units installed in a previous support
timeframe which are still operational in `y`. This is achieved via 6 tuple sets
two each for processes, transmissions and storages.

Intially installed units
^^^^^^^^^^^^^^^^^^^^^^^^
Processes which are already installed at the beginning of the modeled time
horizon and still operational in support timeframe `stf` are collected in the
following tuple set:

::

    m.inst_pro_tuples = pyomo.Set(
        within=m.sit*m.pro*m.stf,
        initialize=[(sit, pro, stf)
                    for (sit, pro, stf)
                    in inst_pro_tuples(m)],
        doc=' Installed processes that are still operational through stf')

where the following function is utilized:

.. literalinclude:: /../urbs/features/modelhelper.py
   :pyobject: inst_pro_tuples

Transmissions which are already installed at the beginning of the modeled time
horizon and still operational in support timeframe `stf` are collected in the
following tuple set:

::

    m.inst_tra_tuples = pyomo.Set(
        within=m.sit*m.sit*m.tra*m.com*m.stf,
        initialize=[(sit, sit_, tra, com, stf)
                    for (sit, sit_, tra, com, stf)
                    in inst_tra_tuples(m)],
        doc='Installed transmissions that are still operational through stf')

where the following function is utilized:

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: inst_tra_tuples

Storages which are already installed at the beginning of the modeled time
horizon and still operational in support timeframe `stf` are collected in the
following tuple set:

::

    m.inst_sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com*m.stf,
        initialize=[(sit, sto, com, stf)
                    for (sit, sto, com, stf)
                    in inst_sto_tuples(m)],
        doc='Installed storages that are still operational through stf')

where the following function is utilized:

.. literalinclude:: /../urbs/features/storage.py
   :pyobject: inst_sto_tuples

Installation in earlier support timeframe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Processes installed in an earlier support timeframe `stf` and still usable in
support timeframe `stf_later` are collected in the following tuple set:

::

    m.operational_pro_tuples = pyomo.Set(
        within=m.sit*m.pro*m.stf*m.stf,
        initialize=[(sit, pro, stf, stf_later)
                    for (sit, pro, stf, stf_later)
                    in op_pro_tuples(m.pro_tuples, m)],
        doc='Processes that are still operational through stf_later'
            '(and the relevant years following), if built in stf'
            'in stf.')

where the following function is utilized:

.. literalinclude:: /../urbs/features/modelhelper.py
   :pyobject: op_pro_tuples

Transmissions installed in an earlier support timeframe `stf` and still usable
in support timeframe `stf_later` are collected in the following tuple set:

::

    m.operational_tra_tuples = pyomo.Set(
        within=m.sit*m.sit*m.tra*m.com*m.stf*m.stf,
        initialize=[(sit, sit_, tra, com, stf, stf_later)
                    for (sit, sit_, tra, com, stf, stf_later)
                    in op_tra_tuples(m.tra_tuples, m)],
        doc='Transmissions that are still operational through stf_later'
            '(and the relevant years following), if built in stf'
        'in stf.')

where the following function is utilized:

.. literalinclude:: /../urbs/features/transmission.py
   :pyobject: op_tra_tuples

Storages installed in an earlier support timeframe `stf` and still usable in
support timeframe `stf_later` are collected in the following tuple set:

::

    m.operational_sto_tuples = pyomo.Set(
        within=m.sit*m.sto*m.com*m.stf*m.stf,
        initialize=[(sit, sto, com, stf, stf_later)
                    for (sit, sto, com, stf, stf_later)
                    in op_sto_tuples(m.sto_tuples, m)],
        doc='Processes that are still operational through stf_later'
            '(and the relevant years following), if built in stf'
        'in stf.')

where the following function is utilized:

.. literalinclude:: /../urbs/features/storage.py
   :pyobject: op_sto_tuples