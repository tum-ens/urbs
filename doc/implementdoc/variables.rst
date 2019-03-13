.. module:: urbs

Variables
=========
All the variables that the optimization model requires to calculate an optimal
solution will be listed and defined in this section. A variable is a numerical
value that is determined during optimization. Variables can denote a single,
independent value, or an array of values. Variables define the search space for
optimization. Variables of this optimization model can be seperated into
sections by their area of use. These Sections are Cost, Commodity, Process,
Transmission, Storage and demand side management.

.. table:: *Table: Model Variables*
    
    +--------------------------------------+------+------------------------------------+
    | Variable                             | Unit | Description                        |
    +======================================+======+====================================+
    | **Cost  Variables**                                                              |
    +--------------------------------------+------+------------------------------------+
    | :math:`\zeta`                        | €    | Total System Cost                  |
    +--------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{inv}`             | €    | Investment Costs                   |
    +--------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{fix}`             | €    | Fix Costs                          |
    +--------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{var}`             | €    | Variable Costs                     |
    +--------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{fuel}`            | €    | Fuel Costs                         |
    +--------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{rev}`             | €    | Revenue Costs                      |
    +--------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{pur}`             | €    | Purchase Costs                     |
    +--------------------------------------+------+------------------------------------+
    | **Commodity Variables**                                                          |
    +--------------------------------------+------+------------------------------------+
    | :math:`\rho_{yvct}`                  | MWh  | Stock Commodity Source Term        |
    +--------------------------------------+------+------------------------------------+
    | :math:`\varrho_{yvct}`               | MWh  | Sell Commodity Source Term         |
    +--------------------------------------+------+------------------------------------+
    | :math:`\psi_{yvct}`                  | MWh  | Buy Commodity Source Term          |
    +--------------------------------------+------+------------------------------------+
    | **Process Variables**                                                            |
    +--------------------------------------+------+------------------------------------+
    | :math:`\kappa_{yvp}`                 | MW   | Total Process Capacity             |
    +--------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{yvp}`           | MW   | New Process Capacity               |
    +--------------------------------------+------+------------------------------------+
    | :math:`\tau_{yvpt}`                  | MWh  | Process Throughput                 |
    +--------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{yvcpt}^\text{in}`   | MWh  | Process Input Commodity Flow       |
    +--------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{yvcpt}^\text{out}`  | MWh  | Process Output Commodity Flow      |
    +--------------------------------------+------+------------------------------------+
    | **Transmission Variables**                                                       |
    +--------------------------------------+------+------------------------------------+
    | :math:`\kappa_{yaf}`                 | MW   | Total transmission Capacity        |
    +--------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{yaf}`           | MW   | New Transmission Capacity          |
    +--------------------------------------+------+------------------------------------+
    | :math:`\pi_{yaft}^\text{in}`         | MWh  | Transmission Input Commodity Flow  | 
    +--------------------------------------+------+------------------------------------+
    | :math:`\pi_{yaft}^\text{out}`        | MWh  | Transmission Output Commodity Flow |
    +--------------------------------------+------+------------------------------------+
    | **Storage Variables**                                                            |
    +--------------------------------------+------+------------------------------------+
    | :math:`\kappa_{yvs}^\text{c}`        | MWh  | Total Storage Size                 |
    +--------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{yvs}^\text{c}`  | MWh  | New Storage Size                   |
    +--------------------------------------+------+------------------------------------+
    | :math:`\kappa_{yvs}^\text{p}`        | MW   | Total Storage Power                |
    +--------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{yvs}^\text{p}`  | MW   | New Storage Power                  |
    +--------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{yvst}^\text{in}`    | MWh  | Storage Input Commodity Flow       |
    +--------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{yvst}^\text{out}`   | MWh  | Storage Output Commodity Flow      |
    +--------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{yvst}^\text{con}`   | MWh  | Storage Energy Content             |
    +--------------------------------------+------+------------------------------------+
    | **Demand Side Management Variables**                                             |
    +--------------------------------------+------+------------------------------------+
    | :math:`\delta_{yvct}^\text{up}`      | MWh  | DSM Upshift                        |
    +--------------------------------------+------+------------------------------------+
    | :math:`\delta_{t,tt,yvc}^\text{down}`| MWh  | DSM Downshift                      |
    +--------------------------------------+------+------------------------------------+
    

	
Cost Variables
^^^^^^^^^^^^^^
**Total System Cost**, :math:`\zeta` : the variable :math:`\zeta` represents
the *total expense incurred* in reaching the satisfaction of the given energy
demand in the entire modeling horizon. If only a fraction of a year is modeled
in each support timeframe, the costs are scaled to the annual expenditures. The
total cost is calculated by the sum total of all costs by
type(:math:`\zeta_r`, :math:`\forall r \in R`) and defined as ``costs`` by the
following code fragment:

::

    m.costs = pyomo.Var(
        m.cost_type,
        within=pyomo.Reals,
        doc='Costs by type (EUR/a)')

System costs are divided into the 7 cost types invest, fix, variable, fuel,
purchase, sell and environmental. The separation of costs by type, facilitates
business planning and provides calculation accuracy. These cost types are
hardcoded, which means they are not considered to be fixed or changed by the
user.
    
For more information on the definition of these variables see section
:ref:`theory-min` and for their implementation see section :ref:`objective`.

Commodity Variables
^^^^^^^^^^^^^^^^^^^

**Stock Commodity Source Term**, :math:`\rho_{yvct}`, ``e_co_stock``, MWh : The
variable :math:`\rho_{yvct}` represents the energy amount in [MWh] that is
being used by the system of commodity :math:`c` from type stock
(:math:`\forall c \in C_\text{stock}`) in support timeframe :math:`y`
(:math:`\forall y \in Y`) in a site :math:`v` (:math:`\forall v \in V`) at
timestep :math:`t` (:math:`\forall t \in T_\text{m}`). In script ``model.py``
this variable is defined by the variable ``e_co_stock`` and initialized by the
following code fragment: ::

    m.e_co_stock = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of stock commodity source (MWh) at a given timestep')

**Sell Commodity Source Term**, :math:`\varrho_{yvct}`, ``e_co_sell``, MWh :
The variable :math:`\varrho_{yvct}` represents the energy amount in [MWh] that
is being used by the system of commodity :math:`c` from type sell
(:math:`\forall c \in C_\text{sell}`) in support timeframe :math:`y`
(:math:`\forall y \in Y`) in a site :math:`v` (:math:`\forall v \in V`) at
timestep :math:`t` (:math:`\forall t \in T_\text{m}`). In script ``model.py``
this variable is defined by the variable ``e_co_sell`` and initialized by the
following code fragment: ::

    m.e_co_sell = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of sell commodity source (MWh) at a given timestep')

**Buy Commodity Source Term**, :math:`\psi_{yvct}`, ``e_co_buy``, MWh : The
variable :math:`\psi_{yvct}` represents the energy amount in [MWh] that is
being used by the system of commodity :math:`c` from type buy
(:math:`\forall c \in C_\text{buy}`) in support timeframe :math:`y`
(:math:`\forall y \in Y`) in a site :math:`v` (:math:`\forall v \in V`) at
timestep :math:`t` (:math:`\forall t \in T_\text{m}`). In script ``model.py``
this variable is defined by the variable ``e_co_buy`` and initialized by the
following code fragment: ::

    m.e_co_buy = pyomo.Var(
       m.tm, m.com_tuples,
       within=pyomo.NonNegativeReals,
       doc='Use of buy commodity source (MWh) at a given timestep')

Process Variables
^^^^^^^^^^^^^^^^^

**Total Process Capacity**, :math:`\kappa_{yvp}`, ``cap_pro``: The variable
:math:`\kappa_{yvp}` represents the total potential throughput (capacity) of a
process tuple :math:`p_{yv}`
(:math:`\forall p \in P, \forall v \in V`, \forall y \in Y`), that is required
in the energy system. The total process capacity includes both the already
installed process capacity and the additional new process capacity that needs
to be installed. Since the costs of the process technologies are mostly
directly proportional to the maximum possible output (and correspondingly to
the capacity) of processes, this variable acts as a scale factor of process
technologies. For further information see Process Capacity Rule. This variable
is expressed in the unit (MW).
In script ``model.py`` this variable is defined by the model variable
``cap_pro`` and initialized by the following code fragment: ::

    m.cap_pro = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total process capacity (MW)')

**New Process Capacity**, :math:`\hat{\kappa}_{yvp}`, ``cap_pro_new``: The
variable :math:`\hat{\kappa}_{yvp}` represents the capacity of a process tuple
:math:`p_{yv}` (:math:`\forall p \in P, \forall v \in V`) that needs to be
installed additionally to the energy system in support timeframe :math:`y` in
site :math:`v` in order to provide the optimal solution. This variable is
expressed in the unit MW. In script ``model.py`` this variable is defined by
the model variable ``cap_pro_new`` and initialized by the following code
fragment: ::

    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')

**Process Throughput**, :math:`\tau_{yvpt}`, ``tau_pro`` : The variable
:math:`\tau_{yvpt}` represents the measure of (energetic) activity of a process
tuple :math:`p_{yv}`
(:math:`\forall p \in P, \forall v \in V, \forall y \in Y`) at a timestep
:math:`t` (:math:`\forall t \in T_{m}`). Based on the process throughput amount
in a given timestep of a process, flow amounts of the process' input and output
commodities at that timestep can be calculated by scaling the process
throughput with corresponding process input and output ratios. For further
information see **Process Input Ratio** and **Process Output Ratio**. The
process throughput variable is expressed in the unit MWh. In script
``model.py`` this variable is defined by the model variable ``tau_pro`` and
initialized by the following code fragment: ::

    m.tau_pro = pyomo.Var(
        m.tm, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Activity (MWh) through process')

**Process Input Commodity Flow**, :math:`\epsilon_{yvcpt}^\text{in}`,
``e_pro_in``: The variable :math:`\epsilon_{yvcpt}^\text{in}` represents the
commodity input flow into a process tuple :math:`p_{yv}`
(:math:`\forall p \in P, \forall v \in V, \forall y \in Y`) caused by an input
commodity :math:`c` (:math:`\forall c \in C`) at a timestep :math:`t`
(:math:`\forall t \in T_{m}`). This variable is generally expressed in the unit
MWh. In script ``model.py`` this variable is defined by the model variable
``e_pro_in`` and initialized by the following code fragment: ::

    m.e_pro_in = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Flow of commodity into process at a given timestep')


**Process Output Commodity Flow**, :math:`\epsilon_{yvcpt}^\text{out}`,
``e_pro_out``: The variable :math:`\epsilon_{vcpt}^\text{out}` represents the
commodity flow output out of a process tuple :math:`p_{yv}`
(:math:`\forall p \in P, \forall v \in V, \forall y \in Y`) caused by an output
commodity :math:`c` (:math:`\forall c \in C`) at a timestep :math:`t`
(:math:`\forall t \in T_{m}`). This variable is generally expressed in the unit
MWh (or tonnes e.g. for the environmental commodity 'CO2'). In script
``model.py`` this variable is defined by the model variable ``e_pro_out`` and
initialized by the following code fragment: ::

    m.e_pro_out = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Flow of commodity out of process at a given timestep')

Transmission Variables
^^^^^^^^^^^^^^^^^^^^^^

**Total Transmission Capacity**, :math:`\kappa_{yaf}`, ``cap_tra``: The
variable :math:`\kappa_{yaf}` represents the total potential transfer power of
a transmission tuple :math:`f_{yca}`, where :math:`a` represents the arc from
an origin site :math:`v_\text{out}` to a destination site
:math:`{v_\text{in}}`. The total transmission capacity includes both the
already installed transmission capacity and the additional new transmission
capacity that needs to be installed. This variable is expressed in the unit MW.
In script ``model.py`` this variable is defined by the model variable
``cap_tra`` and initialized by the following code fragment: ::

    m.cap_tra = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total transmission capacity (MW)')

**New Transmission Capacity**, :math:`\hat{\kappa}_{yaf}`, ``cap_tra_new``: The
variable :math:`\hat{\kappa}_{yaf}` represents the additional capacity, that
needs to be installed, of a transmission tuple :math:`f_{yca}`, where :math:`a`
represents the arc from an origin site :math:`v_\text{out}` to a destination
site :math:`v_\text{in}`. This variable is expressed in the unit MW.
In script ``model.py`` this variable is defined by the model variable
``cap_tra_new`` and initialized by the following code fragment: ::

    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')

**Transmission Input Commodity Flow**, :math:`\pi_{yaft}^\text{in}`,
``e_tra_in``: The variable :math:`\pi_{yaft}^\text{in}` represents the
commodity flow input into a transmission tuple :math:`f_{yca}` at a timestep
:math:`t`, where :math:`a` represents the arc from an origin site
:math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable
is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by
the model variable ``e_tra_in`` and initialized by the following code fragment:
::

    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Commodity flow into transmission line (MWh) at a given timestep')

**Transmission Output Commodity Flow**, :math:`\pi_{yaft}^\text{out}`,
``e_tra_out``: The variable :math:`\pi_{yaft}^\text{out}` represents the
commodity flow output out of a transmission tuple :math:`f_{ca}` at a timestep
:math:`t`, where :math:`a` represents the arc from an origin site
:math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable
is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by
the model variable ``e_tra_out`` and initialized by the following code
fragment: ::

    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of transmission line (MWh) at a given timestep')

Storage Variables
^^^^^^^^^^^^^^^^^

**Total Storage Size**, :math:`\kappa_{yvs}^\text{c}`, ``cap_sto_c``: The
variable :math:`\kappa_{yvs}^\text{c}` represents the total load capacity of a
storage tuple :math:`s_{yvc}`. The total storage load capacity includes both the
already installed storage load capacity and the additional new storage load
capacity that needs to be installed. This variable is expressed in unit MWh. In
script ``model.py`` this variable is defined by the model variable
``cap_sto_c`` and initialized by the following code fragment: ::

    m.cap_sto_c = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage size (MWh)')

**New Storage Size**, :math:`\hat{\kappa}_{yvs}^\text{c}`, ``cap_sto_c_new``:
The variable :math:`\hat{\kappa}_{yvs}^\text{c}` represents the additional
storage load capacity of a storage tuple :math:`s_{vc}` that needs to be
installed to the energy system in order to provide the optimal solution. This
variable is expressed in the unit MWh. In script ``model.py`` this variable is
defined by the model variable ``cap_sto_c_new`` and initialized by the
following code fragment: ::

    m.cap_sto_c_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New storage size (MWh)')

**Total Storage Power**, :math:`\kappa_{yvs}^\text{p}`, ``cap_sto_p``: The
variable :math:`\kappa_{yvs}^\text{p}` represents the total potential discharge
power of a storage tuple :math:`s_{vc}`. The total storage power includes both
the already installed storage power and the additional new storage power that
needs to be installed. This variable is expressed in the unit MW. In script
``model.py`` this variable is defined by the model variable ``cap_sto_p`` and
initialized by the following code fragment:
::

    m.cap_sto_p = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total storage power (MW)')

**New Storage Power**, :math:`\hat{\kappa}_{yvs}^\text{p}`, ``cap_sto_p_new``:
The variable :math:`\hat{\kappa}_{yvs}^\text{p}` represents the additional
potential discharge power of a storage tuple :math:`s_{vc}` that needs to be
installed to the energy system in order to provide the optimal solution. This
variable is expressed in the unit MW. In script ``model.py`` this variable is
defined by the model variable ``cap_sto_p_new`` and initialized by the
following code fragment:
::

    m.cap_sto_p_new = pyomo.Var(
        m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='New  storage power (MW)')

**Storage Input Commodity Flow**, :math:`\epsilon_{yvst}^\text{in}`,
``e_sto_in``: The variable :math:`\epsilon_{yvst}^\text{in}` represents the
input commodity flow into a storage tuple :math:`s_{yvc}` at a timestep
:math:`t`. Input commodity flow into a storage tuple can also be defined as the
charge of a storage tuple. This variable is expressed in the unit MWh. In
script ``model.py`` this variable is defined by the model variable ``e_sto_in``
and initialized by the following code fragment:
::

    m.e_sto_in = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Commodity flow into storage (MWh) at a given timestep')

**Storage Output Commodity Flow**, :math:`\epsilon_{yvst}^\text{out}`,
``e_sto_out``:  The variable :math:`\epsilon_{vst}^\text{out}` represents the
output commodity flow out of a storage tuple :math:`s_{yvc}` at a timestep
:math:`t`. Output commodity flow out of a storage tuple can also be defined as
the discharge of a storage tuple. This variable is expressed in the unit MWh.
In script ``model.py`` this variable is defined by the model variable
``e_sto_out`` and initialized by the following code fragment:
::

    m.e_sto_out = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Commodity flow out of storage (MWh) at a given timestep')

**Storage Energy Content**, :math:`\epsilon_{yvst}^\text{con}`, ``e_sto_con``:
The variable :math:`\epsilon_{yvst}^\text{con}` represents the energy amount
that is loaded in a storage tuple :math:`s_{vc}` at a timestep :math:`t`. This
variable is expressed in the unit MWh. In script ``urbs.py`` this variable is
defined by the model variable ``e_sto_out`` and initialized by the following
code fragment:
::

    m.e_sto_con = pyomo.Var(
        m.t, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Energy content of storage (MWh) at a given timestep')
        
Demand Side Management Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**DSM Upshift**, :math:`\delta_{yvct}^\text{up}`, ``dsm_up``, MWh: The variable
:math:`\delta_{yvct}^\text{up}` represents the DSM upshift in time step
:math:`t` in support timeframe :math:`y` in site :math:`v` for commodity
:math:`c`. It is only defined for all ``dsm_site_tuples``. The following code
fragment shows the definition of the variable:
::

    m.dsm_up = pyomo.Var(
        m.tm, m.dsm_site_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM upshift (MWh) of a demand commodity at a given timestap')
        
**DSM Downshift**, :math:`\delta_{t,tt,yvc}^\text{down}`, ``dsm_down``, MWh:
The variable :math:`\delta_{t,tt,yvc}^\text{down}` represents the DSM downshift
in timestepp :math:`tt` caused by the upshift in time :math:`t` in support
timeframe :math:`y` in site :math:`v` for commodity :math:`c`. The special
combinations of timesteps :math:`t` and :math:`tt` for each (support timeframe,
site, commodity) combination is created by the ``dsm_down_tuples``. The
definition of the variable is shown in the code fragment:
::
    
	m.dsm_down = pyomo.Var(
        m.dsm_down_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM downshift (MWh) of a demand commodity at a given timestep')
