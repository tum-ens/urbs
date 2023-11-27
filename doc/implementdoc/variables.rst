﻿.. module:: urbs

Variables
=========
All the variables that the optimization model requires to calculate an optimal
solution will be listed and defined in this section. A variable is a numerical
value that is determined during optimization. Variables can denote a single,
independent value, or an array of values. Variables define the search space for
optimization. Variables of this optimization model can be separated into
sections by their area of use. These Sections are Cost, Commodity, Process,
Transmission, Storage and demand side management.

.. table:: *Table: Model Variables*
    
    +----------------------------------------+------+-----------------------------------+
    | Variable                               | Unit | Description                       |
    +========================================+======+===================================+
    | **Cost  Variables**                                                               |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta`                          | €    | Total System Cost                 |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta_\text{inv}`               | €    | Investment Costs                  |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta_\text{fix}`               | €    | Fix Costs                         |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta_\text{var}`               | €    | Variable Costs                    |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta_\text{fuel}`              | €    | Fuel Costs                        |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta_\text{rev}`               | €    | Revenue Costs                     |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta_\text{pur}`               | €    | Purchase Costs                    |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\zeta_\text{start}`             | €    | Start Costs                       |
    +----------------------------------------+------+-----------------------------------+
    | **Commodity Variables**                                                           |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\rho_{yvct}`                    | MWh  | Stock Commodity Source Term       |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\varrho_{yvct}`                 | MWh  | Sell Commodity Source Term        |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\psi_{yvct}`                    | MWh  | Buy Commodity Source Term         |
    +----------------------------------------+------+-----------------------------------+
    | **Process Variables**                                                             |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\kappa_{yvp}`                   | MW   | Total Process Capacity            |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\hat{\kappa}_{yvp}`             | MW   | New Process Capacity              |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\beta_{yvp}`                    | -    | New Process Capacity Units        |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\tau_{yvpt}`                    | MWh  | Process Throughput                |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\epsilon_{yvcpt}^\text{in}`     | MWh  | Process Input Commodity Flow      |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\epsilon_{yvcpt}^\text{out}`    | MWh  | Process Output Commodity Flow     |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\omicron_{yvpt}`                |-     | Process On/Off Marker             |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\sigma_{yvpt}`                  |-     | Process Start-up Marker           |
    +----------------------------------------+------+-----------------------------------+
    | **Transmission Variables**                                                        |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\kappa_{yaf}`                   | MW   | Total transmission Capacity       |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\hat{\kappa}_{yaf}`             | MW   | New Transmission Capacity         |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\beta_{yaf}`                    |-     | New Transmission Capacity Units   |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\pi_{yaft}^\text{in}`           | MWh  | Transmission Input Commodity Flow |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\pi_{yaft}^\text{out}`          | MWh  | Transmission Output Commodity Flow|
    +----------------------------------------+------+-----------------------------------+
    | **DCPF Transmission Variables**                                                   |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\theta_{yvt}`                   | deg. | Voltage Angle                     |
    +----------------------------------------+------+-----------------------------------+
    | :math:`{\pi_{yaft}^{\text{in}}}^\prime`| MW   | Absolute Transmission Flow        |
    +----------------------------------------+------+-----------------------------------+
    | **Storage Variables**                                                             |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\kappa_{yvs}^\text{c}`          | MWh  | Total Storage Size                |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\hat{\kappa}_{yvs}^\text{c}`    | MWh  | New Storage Size                  |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\beta_{yvs}^\text{c}`           | -    | New Storage Size Units            |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\kappa_{yvs}^\text{p}`          | MW   | Total Storage Power               |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\hat{\kappa}_{yvs}^\text{p}`    | MW   | New Storage Power                 |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\beta_{yvs}^\text{c}`           | -    | New Storage Power Units           |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\epsilon_{yvst}^\text{in}`      | MWh  | Storage Input Commodity Flow      |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\epsilon_{yvst}^\text{out}`     | MWh  | Storage Output Commodity Flow     |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\epsilon_{yvst}^\text{con}`     | MWh  | Storage Energy Content            |
    +----------------------------------------+------+-----------------------------------+
    | **Demand Side Management Variables**                                              |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\delta_{yvct}^\text{up}`        | MWh  | DSM Upshift                       |
    +----------------------------------------+------+-----------------------------------+
    | :math:`\delta_{t,tt,yvc}^\text{down}`  | MWh  | DSM Downshift                     |
    +----------------------------------------+------+-----------------------------------+

	
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
	
**New Process Capacity Units**, :math:`\beta_{yvp}`, ``pro_cap_unit``: The
variable :math:`\beta_{yvp}` represents the number of capacity blocks of a
process tuple :math:`p_{yv}` (:math:`\forall p \in P, \forall v \in V`) that
needs to be installed additionally to the energy system in support timeframe
:math:`y` in site :math:`v` in order to provide the optimal solution. In 
script ``model.py`` this variable is defined by the model variable
``cap_pro_new`` and initialized by the following code fragment: ::  

    m.pro_cap_unit = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeIntegers,
        doc='Number of newly installed capacity units')

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
	
**Process On/Off Marker**, :math:`\omicron_{yvpt}`, ``on_off``: The boolean
variable :math:`\omicron_{yvpt}` marks whether process tuple :math:`p_{yv}` 
(:math:`\forall p \in P^\text{on/off}, \forall v \in V, \forall y \in Y`) 
is on and producing (:math:`\omicron_{yvpt}` is 1) or it is not 
producing (:math:`\omicron_{yvpt}` is 0) at a timestep :math:`t`. While not 
producing, the process is either turned off or it started, without reaching the
minimum fraction :math:`\underline{P}_{yvp}`.
In the script ``AdvancedProcesses.py``, this variable is defined by the model 
variable ``on_off`` and initialized by the following code fragment: ::

    m.on_off = pyomo.Var(
        m.t, m.pro_on_off_tuples,
        within=pyomo.Boolean,
        doc='Turn on/off a process with minimum working load')
	    
**Process Start-up Marker**, :math:`\sigma_{yvpt}`, ``start_ups``: The boolean
variable :math:`\sigma_{yvpt}` marks whether process tuple :math:`p_{yv}` 
(:math:`\forall p \in P^\text{on/off}, \forall v \in V, \forall y \in Y`) 
is starting (:math:`\sigma_{yvpt}` becomes 1) or not (:math:`\sigma_{yvpt}` is 0) 
at a timestep :math:`t`. The process is considered to start when its output
``e_pro_out`` becomes greater than 0.
In the script ``AdvancedProcesses.py``, this variable is defined by the model 
variable ``start_ups`` and initialized by the following code fragment: ::

    m.start_up = pyomo.Var(
            m.tm, m.pro_start_up_tuples,
            within=pyomo.Boolean,
            doc='Start-up marker')
	    
Transmission Variables
^^^^^^^^^^^^^^^^^^^^^^

**Total Transmission Capacity**, :math:`\kappa_{yaf}`, ``cap_tra``: The
variable :math:`\kappa_{yaf}` represents the total potential transfer power of
a transmission tuple :math:`f_{yca}`, where :math:`a` represents the arc from
an origin site :math:`v_\text{out}` to a destination site
:math:`{v_\text{in}}`. The total transmission capacity includes both the
already installed transmission capacity and the additional new transmission
capacity that needs to be installed. This variable is expressed in the unit MW.
In script ``transmission.py`` this variable is defined by the model variable
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
In script ``transmission.py`` this variable is defined by the model variable
``cap_tra_new`` and initialized by the following code fragment: ::

    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')

**New Transmission Capacity Units**, :math:`\beta_{yaf}`, ``tra_cap_unit``: The
variable :math:`\beta_{yaf}` represents the number of additional capacity blocks
of a transmission tuple :math:`f_{yca}` that need to be installed , where 
:math:`a` represents the arc from an origin site :math:`v_\text{out}` to a 
destination site :math:`v_\text{in}`. In script ``transmission.py`` this variable
is defined by the model variable ``cap_tra_new`` and initialized by the following 
code fragment: ::

    m.tra_cap_unit =pyomo.Var(
        m.tra_block_tuples,
        within=pyomo.NonNegativeIntegers,
        doc='New transmission capacity blocks')

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

DCPF Transmission Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the DC Power Flow transmission modelling is activated, two new variables are introduced to the model.

**Voltage Angle**, :math:`\theta_{yvt}`, ``voltage_angle``: The variable :math:`\theta_{yvt}` represents the voltage
angle of a site :math:`v`, which has a DCPF transmission line connection, at a timestep :math:`t`. This variable is
expressed in the unit degrees. In script ``urbs.py`` this variable is defined by the model variable ``voltage_angle``
and initialized by the following code
fragment: ::

    m.voltage_angle = pyomo.Var(
            m.tm, m.stf, m.sit,
            within=pyomo.Reals,
            doc='Voltage angle of a site')

**Absolute Value of Transmission Commodity Flow**, :math:`{\pi_{yaft}^{\text{in}}}^\prime`, ``e_tra_abs``:
The variable :math:`{\pi_{yaft}^{\text{in}}}^\prime` represents the absolute value of the transmission commodity flow
on a DCPF transmission tuple :math:`f_{yca}` at a timestep
:math:`t`, where :math:`a` represents the arc from an origin site
:math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable
is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by
the model variable ``e_tra_abs`` and initialized by the following code
fragment: ::

    m.e_tra_abs = pyomo.Var(
        m.tm, m.tra_tuples_dc,
        within=pyomo.NonNegativeReals,
        doc='Absolute power flow on transmission line (MW) per timestep')

**Transmission Commodity Flow Domain Changes**
:DC Power Flow transmission lines are represented by bidirectional single arcs instead of unidirectional symmetrical
arcs as in the default transmission model. Consequently the power flow is allowed to be both positive or negative for
DCPF transmission lines contrary to the transport transmission lines. For this reason, the domains of the variables
transmission input commodity flow :math:`\pi_{yaft}^\text{in}` and  transmission output commodity flow
:math:`\pi_{yaft}^\text{out}` are defined with the :py:func:`e_tra_domain_rule` function depending on the corresponding
transmission tuple set. These variables are defined by the model variables ``e_tra_in`` and ``e_tra_out`` and
intialized by the code
fragment: ::

    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=e_tra_domain_rule,
        doc='Power flow into transmission line (MW) per timestep')
    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=e_tra_domain_rule,
        doc='Power flow out of transmission line (MW) per timestep')

The function :py:func:`e_tra_domain_rule` is given by the code
fragment: ::

    def e_tra_domain_rule(m, tm, stf, sin, sout, tra, com):
        # assigning e_tra_in and e_tra_out variable domains for transport and DCPF
        if (stf, sin, sout, tra, com) in m.tra_tuples_dc:
            return pyomo.Reals
        elif (stf, sin, sout, tra, com) in m.tra_tuples_tp:
            return pyomo.NonNegativeReals

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

**New Storage Size Units**, :math:`\beta_{yvs}^\text{c}`, ``sto_cap_c_unit``:
The variable :math:`\hat{\kappa}_{yvs}^\text{c}` represents the number of
additional storage load capacity blocks of a storage tuple :math:`s_{vc}` that
needs to be installed to the energy system in order to provide the optimal solution. 
In script ``storage.py`` this variable is defined by the model variable ``cap_sto_c_unit``
and initialized by the following code fragment: ::

    m.sto_cap_c_unit = pyomo.Var(
        m.sto_block_c_tuples,
        within=pyomo.NonNegativeIntegers,
        doc='New storage size units')
	
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

**New Storage Power Units**, :math:`\beta_{yvs}^\text{c}`, ``sto_cap_p_unit``:
The variable :math:`\beta_{yvs}^\text{c}` represents the number of additional
potential discharge power blocks of a storage tuple :math:`s_{vc}` that needs 
to be installed to the energy system in order to provide the optimal solution. 
In the script ``storage.py`` this variable is defined by the model variable
``sto_cap_p_unit`` and initialized by the following code fragment:
::	

    m.sto_cap_p_unit = pyomo.Var(
        m.sto_block_p_tuples,
        within=pyomo.NonNegativeIntegers,
        doc='New storage power units')
	
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
in timestep :math:`tt` caused by the upshift in time :math:`t` in support
timeframe :math:`y` in site :math:`v` for commodity :math:`c`. The special
combinations of timesteps :math:`t` and :math:`tt` for each (support timeframe,
site, commodity) combination is created by the ``dsm_down_tuples``. The
definition of the variable is shown in the code fragment:
::
    
	m.dsm_down = pyomo.Var(
        m.dsm_down_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM downshift (MWh) of a demand commodity at a given timestep')
