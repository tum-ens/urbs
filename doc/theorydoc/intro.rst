.. module:: urbs

Structure of an urbs model
==========================
urbs is an abstract generator for linear optimization problems. Such
problems can in general be written in the following standard form:

.. math::

	\text{min}~c^{\text{T}}x\\
	\text{s.t.}~Ax=b\\
	Bx\leq d.

where :math:`x` is the variable vector, :math:`c` the coefficient vector for
the objective function and :math:`A` and :math:`B` the matrices for the
equality and inequality constraints, respectively. The equality constraints
could also be represented by inequality constraints, which is not done here for
simplicity reasons. There are two options for the objective function: either
the total system costs or environmental emissions can be used. The structure of
the following parts will be first a description of :math:`x` and :math:`c` and
subsequently a general formulation of the constraint functions that make up the
matrices :math:`A` and :math:`B` as well as the vectors :math:`b` and
:math:`d`. All variables and equations will be first presented for a minimally
complex problem and the optional additional variables and equations are
presented in extra parts.

Energy system entities
----------------------
For all models that can be generated with urbs, the energy system is built up
out of the following entities:

* Commodities, which represent the various forms of material and energy flows
  in the system.
* Processes, which convert commodities from one type to another. These
  entities are always multiple-input/multiple-output (mimo) that is, a certain
  fixed set of input commodities is converted into another fixed set of output
  commodities.
* Transmission lines, that allow for the transport of commodities between the
  modeled spatial vertices.
* Storages, which allow the storage of a single type of commodity.
* DSM potentials, which make the time shifting of demands possible.