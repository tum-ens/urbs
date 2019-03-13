.. module:: urbs

.. _theory-TVE:

Time Variable efficieny
=======================
It is possible to manipulate the operation of a process by introducing a time
series, which changes the output ratios and thus the efficiency of a given
process in each given timestep. This introduces an additional set of
constraints in the form:

.. math::
   &\forall p \in P^{\text{TimeVarEff}},~c\in C-C^{\text{env}} t\in T_m:\\
   &\epsilon^{\text{out}}_{ypct}=r^{\text{out}}_{ypc}f^{\text{out}}_{ypt}
   \tau_{ypct}
   .

Here, :math:`f^{\text{out}}_{pt}` represents the normalized time series of the
varying output ratio. This feature can be helpful when modeling, e.g.,
temperature dependent effects or maintenance intervals. Environmental
commodities are intentionally excluded from the output manipulation. The reason
for this is that they are typically directly linked to inputs as, e.g., CO2
emissions are linked to the fossil inputs. A manipulation of the output for
environmental commodities would thus screw up the mass balance of carbon in
this case.

When the process in question is a process with part load behavior the equation
for the time variable efficiency case takes the form:

.. math::
   &\forall p\in P^{\text{partload}}~\text{and}~ p \in P^{\text{TimeVarEff}},
   ~c\in C,~t\in T_m:\\\\
   &\epsilon^{\text{out}}_{ypct}=\Delta t\cdot f^{\text{out}}_{ypt}\cdot
   \left(\frac{\underline{r}^{\text{out}}_{ypc}-r^{\text{out}}_{ypc}}
   {1-\underline{P}_{yp}}\cdot \underline{P}_{yp}\cdot \kappa_{yp}+
   \frac{r^{\text{out}}_{ypc}-
   \underline{P}_p\underline{r}^{\text{out}}_{ypc}}
   {1-\underline{P}_{yp}}\cdot \tau_{ypt}\right).