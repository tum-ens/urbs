.. module:: urbs

.. _theory-multinode:

Multinode optimization model
=============================
The introduction of multiple spatial nodes into the model is the second big
extension of the minimal model that is possible. Similar to the intertemporal
model expansion it also adds an index level to all variables and parameters.
This addition is perpendicular to the intertemporal modeling and both
extensions do not interact in any complex way with each other. Here, the
multinode model extension will be shown without the intertemporal extension,
i.e., it is shown as an extension to the minimal model. In this case the
variable vector of the optimization problem reads:

.. math::

   x^{\text{T}}=(\zeta, \underbrace{\rho_{vct}}_{\text{commodity variables}},
   \underbrace{\kappa_{vp}, \widehat{\kappa}_{vp}, \tau_{vpt},
   \epsilon^{\text{in}}_{vcpt},
   \epsilon^{\text{out}}_{vcpt}}_{\text{process variables}},
   \underbrace{\kappa_{af}, \widehat{\kappa}_{af}, \pi^{\text{in}}_{aft},
   \pi^{\text{out}}_{aft}}_{\text{transmission variables}}).

Here, :math:`\zeta` represents the total annualized system cost across all 
modeled vertices :math:`v\in V`, :math:`\rho_{vct}` the amount of commodities
:math:`c` taken from a virtual, infinite stock at vertex :math:`v` and time
:math:`t`, :math:`\kappa_{vp}` and :math:`\widehat{\kappa}_{vp}` the total
and the newly installed process capacities of processes :math:`p` at vertex
:math:`v`, :math:`\tau_{vpt}` the operational state of processes :math:`p` at
vertex :math:`v` and time :math:`t`, :math:`\epsilon^{\text{in}}_{vcpt}` and
:math:`\epsilon^{\text{out}}_{vcpt}` the total inputs and outputs of
commodities :math:`c` to and from process :math:`p` at vertex :math:`v` and
time :math:`t`, :math:`\kappa_{af}` and :math:`\widehat{\kappa}_{af}` the
installed and new capacities of a transmission line :math:`f` linking two
vertices with the arc :math:`a` and :math:`\pi^{\text{in}}_{aft}` and
:math:`\pi^{\text{out}}_{aft}` the in- and outflows into arc :math:`a` via
transmission line :math:`f` at time :math:`t`.

There are no qualitative changes to the cost function only the sum of all units
now extends over processes and transmission lines.

Transmission capacity constraints
---------------------------------
Transmission lines are modeled as unidirectional arcs in urbs. This means that
they have a input site and an output site. Furthermore, an arc already
specifies a commodity that can travel across it. However, from the modelers
point of view the transmissions rather behave like non-directional edges,
linking both sites with the identical capacity in both directions. This
behavior is then ensured by the transmission symmetry rule, which sets the
capacity of both unidirectional arcs to be identical:

.. math::
   &\forall a\in V\times V\times C,~f\in F:\\
   &\kappa_{af}=\kappa_{a^{\prime}f},

where :math:`a^{\prime}` is the inverse arc of :math:`a`. The transmission
capacity is then calculated similar to process capacities in the minimal model:

.. math::
   &\forall a\in V\times V\times C,~f\in F:\\
   &\kappa_{af}=K_{af}+\widehat{\kappa}_{af},

where :math:`K_{af}` represents the already installed and
:math:`\widehat{\kappa}_{af}` the new capacity of transmission :math:`f`
installed in arc :math:`a`.

Transmission capacity limit rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Completely analogous to processes also transmission line capacities are limited
by a maximal and minimal allowed capacity :math:`\overline{K}_{af}` and
:math:`\underline{K}_{af}` via:

.. math::
   &\forall a\in V\times V\times C,~f\in F:\\
   &\underline{K}_{af}\leq \kappa_{af}\leq \overline{K}_{af}

Commodity dispatch constraints
------------------------------
Apart from these time independent rules, the time dependent rules governing the
unit utilization are amended with respect to the minimal model by the
introduction of transmission lines.

Amendments to the Vertex rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The vertex rule is changed, since additional commodity flows through the
transmission lines occur in each vertex. The commodity balance function is thus
changed to:

.. math::
   &\forall c \in C,~t\in T_m:\\\\
   &\text{CB}(c,t)=
    \sum_{(c,p)\in C^{\mathrm{in}}_p}\epsilon^{\text{in}}_{vcpt}+
    \sum_{(a,f)\in A^{\mathrm{in}}_{v}}\pi^{\text{in}}_{aft}-
    \sum_{(c,p)\in C^{\mathrm{out}}_p}\epsilon^{\text{out}}_{vcpt}-
    \sum_{(a,f)\in A^{\mathrm{out}}_{v}}\pi^{\text{out}}_{aft}.

Here, the new tuple sets :math:`A^{\mathrm{in,out}}_v` represent all input and
output arcs :math:`a` connecting vertex :math:`v`, respectively. The commodity
balance is thereby allowing for commodities to leave the system at vertex
:math:`v` via arcs as well as processes. Apart from this change to the
commodity balance the vertex rule and the other rules restricting commodity
flows remain unchanged with respect to the minimal model.

Global CO2 limit
~~~~~~~~~~~~~~~~
In addition to the general vertex specific constraint for the emissions of
environmental commodities as discussed in the minimal model, there is a hard
coded possibility to limit the CO2 emissions across all modeled sites:

.. math::
   -w\sum_{v\in V\\t\in T_{m}}\text{CB}(v,\text{CO}_2,t)\leq
   \overline{L}_{\text{CO}_2,y}
     

Transmission dispatch constraints
---------------------------------
There are two main constraints for the commodity flows to and from transmission
lines. The first restricts the total amount of commodity :math:`c` flowing in
arc :math:`a` on transmission line :math:`f` to the total capacity of the line:

.. math::
   &\forall a\in V\times V\times C,~f\in F,~t\in T_m:\\
   & \pi^{\text{in}}_{aft}\leq \kappa_{af}.

Here, the input into the arc :math:`\pi^{\text{in}}_{aft}` is taken as a
reference for the total capacity. The output of the arc in the target site is
then linked to the input with the transmission efficiency :math:`e_{af}`

.. math::
   &\forall a\in V\times V\times C,~f\in F,~t\in T_m:\\
   & \pi^{\text{out}}_{aft}= e_{af}\cdot \pi^{\text{in}}_{aft}.

DC Power Flow feature
--------------------------------

Transmission lines can be modelled with DC Power Flow as an optional feature to represent the AC network grid.
With the DC Power Flow feature, the variable voltage angle is introduced for the vertices connected with DC Power Flow
transmission lines
The DC Power Flow is defined by the relation between the voltage angle :math:`\theta_{vt}` of connecting vertices.

It is possible to combine the default transmission model with the DC Power Flow transmission model.
The DCPF feature can be activated on the selected transmission lines. This way two different sets of transmission
tuples, subject to different constraints, will be modelled. These transmission tuple sets are defined as the set of
transport model (default) transmission lines :math:`F_{c{v_\text{out}}{v_\text{in}}}^{TP}` and the set of DCPF transmission
lines :math:`F_{c{v_\text{out}}{v_\text{in}}}^{DCPF}`

Usage
~~~~~

This feature can be activated for selected transmission lines by including the following parameters:

- The reactance :math:`X_{af}` of a transmission line is required to be included in the model input to model the given
  transmission line with DCPF. This parameter should be greater than 0 and given in per-unit system. If this parameter
  is excluded from the model input, DCPF will not be activated for the transmission line.

- The voltage angle difference of two connecting sites should be limited with angle difference limit
  :math:`\overline{dl}_{af}` to create a stable model. This parameter is required to limit the voltage angle difference
  between two connecting sites. A degree value between 0 and 91 is allowed.

- The base voltage :math:`V_{af\text{base}}` of transmission lines are required to convert the power flow from per-unit
  system to MW. The base voltage parameter is required in kV for every transmission line, which should be modelled with
  DCPF. The value of this parameter should be greater than 0.

- Since the DC Power Flow model ignores the loss of a transmission line, the efficiency :math:`e_{af}` of the
  transmission lines modelled with the DCPF should be set to 100% represented with the value "1".

Contrary to the default transmission line representation, DC Power Flow transmission lines are represented with a single
bidirectional arc between two vertices. The complementary arc of a DC Power Flow transmission line will be excluded from
the model even if it is defined by the user. Depending on the voltage angle difference of two connecting sites, the
power flow :math:`\pi_{aft}` on a DC Power Flow transmission line can be both negative or positive indicating the
direction of the flow.

DC Power Flow Equation
~~~~~~~~~~~~~~~~~~~~~~
Power flow on a transmission line modelled with DCPF:

.. math::
        \pi_{aft}^\text{in} = \frac{(\theta_{v_{\text{in}}t}- \theta_{v_{\text{out}}t})}{57.2958}(-\frac{-1}{X_{af}}){V_{af\text{base}}^2}

Here :math:`\theta_{v_{\text{in}}t}` and :math:`\theta_{v_{\text{out}}t}` are the voltage angles of the source site
:math:`{v_{\text{in}}}` and destinaton site :math:`v_{\text{out}}`. These are converted to radian from degrees by
dividing by 57,2958. :math:`{X_{af}}` is the reactance of the transmission line in per unit system and
:math:`(-\frac{-1}{X_{af}})` is the admittance of the transmission line.

Constraints
~~~~~~~~~~~

Constraints applied to the DCPF transmission lines vary from those applied to the transport transmission lines.

Symmetry rule is ignored for the DCPF transmission lines, since these lines only consist of single bidirectional arcs.
Since the DCPF transmission lines do not have complementary arcs the fixed and investment costs would be halved.
To prevent this error caused by the excluded symmetry constraint for DCPF transmission lines, fixed and investment
prices for DCPF lines are doubled automatically before calculating the costs.

The constraint which restricts the commodity flow :math:`\pi_{aft}^\text{in}` on a transmission line with the installed
capacity :math:`\kappa_{af}` is expanded for DCPF transmission lines. The additional constraint restricts the lower
limit of the power flow, since the power flow with DCPF can also be negative.

.. math::
         -\pi_{aft}^\text{in} \leq \kappa_{af}

Voltage angle difference of two connecting vertices :math:`v_{\text{in}}` and :math:`v_{\text{out}}` is restricted with the angle difference limit parameter :math:`\overline{dl}_{af}` given
for a DCPF transmission :math:`f` on an arc :math:`a`

.. math::
        -\overline{dl}_{af} \leq (\theta_{v_{\text{in}}t}- \theta_{v_{\text{out}}t}) \leq \overline{dl}_{af}

Two additional constraints are used in DCPF feature to retrieve the absolute value :math:`{\pi_{aft}^{\text{in}}}^\prime`
of the power flow on a DCPF transmission line, which is included in the variable cost calculation. With the help of
these constraints and minimization of objective function , which includes the substitute variable
:math:`{\pi_{aft}^{\text{in}}}^\prime`, the substitute variable will be equal to the absolute value of the power flow
variable :math:`|\pi_{aft}^{\text{in}}|`

.. math::
        {\pi_{aft}^{\text{in}}}^\prime \geq \pi_{aft}^{\text{in}}

.. math::

        {\pi_{aft}^{\text{in}}}^\prime \geq -\pi_{aft}^{\text{in}}








