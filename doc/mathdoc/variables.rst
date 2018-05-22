.. module:: urbs

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
    
    +------------------------------------+------+------------------------------------+
    | Variable                           | Unit | Description                        |
    +====================================+======+====================================+
    | **Cost  Variables**                                                            |
    +------------------------------------+------+------------------------------------+
    | :math:`\zeta`                      | €/a  | Total System Cost                  |
    +------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{inv}`           | €/a  | Investment Costs                   |
    +------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{fix}`           | €/a  | Fix Costs                          |
    +------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{var}`           | €/a  | Variable Costs                     |
    +------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{fuel}`          | €/a  | Fuel Costs                         |
    +------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{rev}`           | €/a  | Revenue Costs                      |
    +------------------------------------+------+------------------------------------+
    | :math:`\zeta_\text{pur}`           | €/a  | Purchase Costs                     |
    +------------------------------------+------+------------------------------------+
    | **Commodity Variables**                                                        |
    +------------------------------------+------+------------------------------------+
    | :math:`\rho_{vct}`                 | MWh  | Stock Commodity Source Term        |
    +------------------------------------+------+------------------------------------+
    | :math:`\varrho_{vct}`              | MWh  | Sell Commodity Source Term         |
    +------------------------------------+------+------------------------------------+
    | :math:`\psi_{vct}`                 | MWh  | Buy Commodity Source Term          |
    +------------------------------------+------+------------------------------------+
    | **Process Variables**                                                          |
    +------------------------------------+------+------------------------------------+
    | :math:`\kappa_{vp}`                | MW   | Total Process Capacity             |
    +------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{vp}`          | MW   | New Process Capacity               |
    +------------------------------------+------+------------------------------------+
    | :math:`\tau_{vpt}`                 | MWh  | Process Throughput                 |
    +------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{vcpt}^\text{in}`  | MWh  | Process Input Commodity Flow       |
    +------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{vcpt}^\text{out}` | MWh  | Process Output Commodity Flow      |
    +------------------------------------+------+------------------------------------+
    | **Transmission Variables**                                                     |
    +------------------------------------+------+------------------------------------+
    | :math:`\kappa_{af}`                | MW   | Total transmission Capacity        |
    +------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{af}`          | MW   | New Transmission Capacity          |
    +------------------------------------+------+------------------------------------+
    | :math:`\pi_{aft}^\text{in}`        | MWh  | Transmission Input Commodity Flow  | 
    +------------------------------------+------+------------------------------------+
    | :math:`\pi_{aft}^\text{out}`       | MWh  | Transmission Output Commodity Flow |
    +------------------------------------+------+------------------------------------+
    | **Storage Variables**                                                          |
    +------------------------------------+------+------------------------------------+
    | :math:`\kappa_{vs}^\text{c}`       | MWh  | Total Storage Size                 |
    +------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{vs}^\text{c}` | MWh  | New Storage Size                   |
    +------------------------------------+------+------------------------------------+
    | :math:`\kappa_{vs}^\text{p}`       | MW   | Total Storage Power                |
    +------------------------------------+------+------------------------------------+
    | :math:`\hat{\kappa}_{vs}^\text{p}` | MW   | New Storage Power                  |
    +------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{vst}^\text{in}`   | MWh  | Storage Input Commodity Flow       |
    +------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{vst}^\text{out}`  | MWh  | Storage Output Commodity Flow      |
    +------------------------------------+------+------------------------------------+
    | :math:`\epsilon_{vst}^\text{con}`  | MWh  | Storage Energy Content             |
    +------------------------------------+------+------------------------------------+
    | **Demand Side Management Variables**                                           |
    +------------------------------------+------+------------------------------------+
    | :math:`\delta_{vct}^\text{up}`     | MWh   | DSM Upshift                       |
    +------------------------------------+------+------------------------------------+
    | :math:`\delta_{vct,tt}^\text{down}`| MWh   | DSM Downshift                     |
    +------------------------------------+------+------------------------------------+
    

	
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

More information on calculation of this variable is available at the section :ref:`eq-cost-func`.

Total System costs by type: System costs are divided into 6 cost types by their meaning and purpose.
The separation of costs by type, facilitates business planning and provides calculation accuracy
As mentioned before these cost types are hardcoded, which means they are not considered to be fixed or changed by the user.
These cost types are as following;

**Investment Costs** :math:`\zeta_\text{inv}`: The variable :math:`\zeta_\text{inv}` represents the annualised total investment costs.
Costs for required new investments on storage, process and transmission technologies.

**Fix Costs** :math:`\zeta_\text{fix}`: The variable :math:`\zeta_\text{fix}` represents the annualised total fix costs.
Fix costs for all used storage, process, and transmission technologies. Such as maintenance costs.

**Variable Costs** :math:`\zeta_\text{var}`: The variable :math:`\zeta_\text{var}` represents the annualised total variables costs.
Variable costs that are reliant on the usage amount and period of the storage, process, transmission technologies.

**Fuel Costs** :math:`\zeta_\text{fuel}`: The variable :math:`\zeta_\text{fuel}` represents the annualised total fuel costs.
Fuel costs are dependent on the usage of stock commodities( :math:`\forall c \in C_\text{stock}`).

**Revenue Costs** :math:`\zeta_\text{rev}`: The variable :math:`\zeta_\text{rev}` represents the annualised total revenue costs.
Revenue costs is defined for the costs that occures by selling the sell commodities( :math:`\forall c \in C_\text{sell}`).
Since this variable is an income for the system, it is either zero or has a negative value.

**Purchase Costs** :math:`\zeta_\text{pur}`: The variable :math:`\zeta_\text{pur}` represents the annualised total purchase costs.
Purchase costs is defined for the costs that occures by buying the buy commodities ( :math:`\forall c \in C_\text{buy}` ).
    
For more information on calculation of these variables see section :ref:`eq-cost-func`.

Commodity Variables
^^^^^^^^^^^^^^^^^^^

**Stock Commodity Source Term**, :math:`\rho_{vct}`, ``e_co_stock``, MWh : The variable :math:`\rho_{vct}` represents the energy amount in [MWh] that is being used by the system of commodity :math:`c` from type stock (:math:`\forall c \in C_\text{stock}`)  in a site :math:`v` (:math:`\forall v \in V`) at timestep :math:`t` (:math:`\forall t \in T_\text{m}`).
In script ``urbs.py`` this variable is defined by the variable ``e_co_stock`` and initialized by the following code fragment: ::

    m.e_co_stock = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of stock commodity source (MWh) at a given timestep')

**Sell Commodity Source Term**, :math:`\varrho_{vct}`, ``e_co_sell``, MWh : The variable :math:`\varrho_{vct}` represents the energy amount in [MWh] that is being used by the system of commodity :math:`c` from type sell (:math:`\forall c \in C_\text{sell}`)  in a site :math:`v` (:math:`\forall v \in V`) at timestep :math:`t` (:math:`\forall t \in T_\text{m}`).
In script ``urbs.py`` this variable is defined by the variable ``e_co_sell`` and initialized by the following code fragment: ::

    m.e_co_sell = pyomo.Var(
        m.tm, m.com_tuples,
        within=pyomo.NonNegativeReals,
        doc='Use of sell commodity source (MWh) at a given timestep')

**Buy Commodity Source Term**, :math:`\psi_{vct}`, ``e_co_buy``, MWh : The variable :math:`\psi_{vct}` represents the energy amount in [MWh] that is being used by the system of commodity :math:`c` from type buy (:math:`\forall c \in C_\text{buy}`)  in a site :math:`v` (:math:`\forall v \in V`) at timestep :math:`t` (:math:`\forall t \in T_\text{m}`).
In script ``urbs.py`` this variable is defined by the variable ``e_co_buy`` and initialized by the following code fragment: ::

    m.e_co_buy = pyomo.Var(
       m.tm, m.com_tuples,
       within=pyomo.NonNegativeReals,
       doc='Use of buy commodity source (MWh) at a given timestep')

Process Variables
^^^^^^^^^^^^^^^^^

**Total Process Capacity**, :math:`\kappa_{vp}`, ``cap_pro``: The variable :math:`\kappa_{vp}` represents the total potential throughput (capacity) of a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`), that is required in the energy system. The total process capacity includes both the already installed process capacity and the additional new process capacity that needs to be installed. Since the costs of the process technologies are mostly directly proportional to the maximum possible output (and correspondingly to the capacity) of processes, this variable acts as a scale factor of process technologies and helps us to calculate a more accurate cost plan. For further information see Process Capacity Rule.
This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``cap_pro`` and initialized by the following code fragment: ::

    m.cap_pro = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Total process capacity (MW)')

**New Process Capacity**, :math:`\hat{\kappa}_{vp}`, ``cap_pro_new``: The variable :math:`\hat{\kappa}_{vp}` represents the capacity of a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) that needs to be installed additionally to the energy system in order to  provide the optimal solution.
This variable is expressed in the unit MW.
In script ``urbs.py`` this variable is defined by the model variable ``cap_pro_new`` and initialized by the following code fragment: ::

    m.cap_pro_new = pyomo.Var(
        m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='New process capacity (MW)')

**Process Throughput**, :math:`\tau_{vpt}`, ``tau_pro`` : The variable :math:`\tau_{vpt}` represents the measure of (energetic) activity of a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) at a timestep :math:`t` (:math:`\forall t \in T_{m}`). By default, process throughput is represented by the major input commodity flow of the process (e.g. 'Gas' for 'Gas plant', 'Wind' for 'Wind park'). Based on the process throughput amount in a given timestep of a process, flow amounts of the process' input and output commodities at that timestep can be calculated by scaling the process throughput with corresponding process input and output ratios. For further information see **Process Input Ratio** and **Process Output Ratio**. This variable is expressed in the unit MWh. 
In script ``urbs.py`` this variable is defined by the model variable ``tau_pro`` and initialized by the following code fragment: ::

    m.tau_pro = pyomo.Var(
        m.tm, m.pro_tuples,
        within=pyomo.NonNegativeReals,
        doc='Activity (MWh) through process')

**Process Input Commodity Flow**, :math:`\epsilon_{vcpt}^\text{in}`, ``e_pro_in``: The variable :math:`\epsilon_{vcpt}^\text{in}` represents the commodity flow input into a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) caused by an input commodity :math:`c` (:math:`\forall c \in C`) at a timestep :math:`t` (:math:`\forall t \in T_{m}`). This variable is generally expressed in the unit MWh.
In script ``urbs.py`` this variable is defined by the model variable ``e_pro_in`` and initialized by the following code fragment: ::

    m.e_pro_in = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Flow of commodity into process at a given timestep')


**Process Output Commodity Flow**, :math:`\epsilon_{vcpt}^\text{out}`, ``e_pro_out``: The variable :math:`\epsilon_{vcpt}^\text{out}` represents the commodity flow output out of a process tuple :math:`p_v` (:math:`\forall p \in P, \forall v \in V`) caused by an output commodity :math:`c` (:math:`\forall c \in C`) at a timestep :math:`t` (:math:`\forall t \in T_{m}`). This variable is generally expressed in the unit MWh (or tonnes e.g. for the environmental commodity 'CO2').
In script ``urbs.py`` this variable is defined by the model variable ``e_pro_out`` and initialized by the following code fragment: ::

    m.e_pro_out = pyomo.Var(
        m.tm, m.pro_tuples, m.com,
        within=pyomo.NonNegativeReals,
        doc='Flow of commodity out of process at a given timestep')

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

**Transmission Input Commodity Flow**, :math:`\pi_{aft}^\text{in}`, ``e_tra_in``: The variable :math:`\pi_{aft}^\text{in}` represents the commodity flow input into a transmission tuple :math:`f_{ca}` at a timestep :math:`t`, where :math:`a` represents the arc from an origin site :math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by the model variable ``e_tra_in`` and initialized by the following code fragment: ::

    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Commodity flow into transmission line (MWh) at a given timestep')

**Transmission Output Commodity Flow**, :math:`\pi_{aft}^\text{out}`, ``e_tra_out``: The variable :math:`\pi_{aft}^\text{out}` represents the commodity flow output out of a transmission tuple :math:`f_{ca}` at a timestep :math:`t`, where :math:`a` represents the arc from an origin site :math:`v_\text{out}` to a destination site :math:`v_\text{in}`. This variable is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by the model variable ``e_tra_out`` and initialized by the following code fragment: ::

    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of transmission line (MWh) at a given timestep')

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

**Storage Input Commodity Flow**, :math:`\epsilon_{vst}^\text{in}`, ``e_sto_in``: The variable :math:`\epsilon_{vst}^\text{in}` represents the input commodity flow into a storage tuple :math:`s_{vc}` at a timestep :math:`t`. Input commodity flow into a storage tuple can also be defined as the charge of a storage tuple. This variable is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by the model variable ``e_sto_in`` and initialized by the following code fragment:
::

    m.e_sto_in = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Commodity flow into storage (MWh) at a given timestep')

**Storage Output Commodity Flow**, :math:`\epsilon_{vst}^\text{out}`, ``e_sto_out``:  The variable :math:`\epsilon_{vst}^\text{out}` represents the output commodity flow out of a storage tuple :math:`s_{vc}` at a timestep :math:`t`. Output commodity flow out of a storage tuple can also be defined as the discharge of a storage tuple. This variable is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by the model variable ``e_sto_out`` and initialized by the following code fragment:
::

    m.e_sto_out = pyomo.Var(
        m.tm, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Commodity flow out of storage (MWh) at a given timestep')

**Storage Energy Content**, :math:`\epsilon_{vst}^\text{con}`, ``e_sto_con``: The variable :math:`\epsilon_{vst}^\text{con}` represents the energy amount that is loaded in a storage tuple :math:`s_{vc}` at a timestep :math:`t`. This variable is expressed in the unit MWh. In script ``urbs.py`` this variable is defined by the model variable ``e_sto_out`` and initialized by the following code fragment:
::

    m.e_sto_con = pyomo.Var(
        m.t, m.sto_tuples,
        within=pyomo.NonNegativeReals,
        doc='Energy content of storage (MWh) at a given timestep')
        
Demand Side Management Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**DSM Upshift**, :math:`\delta_{vct}^\text{up}`, ``dsm_up``, MWh: The variable :math:`\delta_{vct}^\text{up}` represents the DSM upshift in time step :math:`t` in site :math:`v` for commodity :math:`c`. It is only defined for all ``dsm_site_tuples``. The following code fragment shows the definition of the variable:
::

    m.dsm_up = pyomo.Var(
        m.tm, m.dsm_site_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM upshift (MWh) of a demand commodity at a given timestap')
        
**DSM Downshift**, :math:`\delta_{vct,tt}^\text{down}`, ``dsm_down``, MWh: The variable :math:`\delta_{vct,tt}^\text{down}` represents the DSM downshift in timestepp :math:`tt` caused by the upshift in time :math:`t` in site :math:`v` for commodity :math:`c`. The special combinations of timesteps :math:`t` and :math:`tt` for each site and commodity combination is created by the ``dsm_down_tuples``. The definition of the variable is shown in the code fragment:
::
    
	m.dsm_down = pyomo.Var(
        m.dsm_down_tuples,
        within=pyomo.NonNegativeReals,
        doc='DSM downshift (MWh) of a demand commodity at a given timestep')
