Overview
--------

How to use the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You should start with this overview which explains
the underlying ideas of the regional decomposition.
To fully comprehend the documentation you should be familiar with the urbs model already (see :ref:`overview` of the urbs documentation).
Usually, when some content directly builds on a topic of the urbs documentation, this part of the documentation is explicitly referenced.

The :ref:`tutorial` provides a detailed walkthrough of ``runme_admm.py`` and explains
how to use decomposition for a model. It also explains the ADMM loop.
After the overview you should continue with the tutorial to understand how to apply the code.

If you want to understand the mathematical background of ADMM, you should next look at the
:ref:`admm_theory`.

The implementation of the asynchronous ADMM method, can be seen in the section :ref:`admm_implementation`. This section covers the workflow of the ADMM method, starting from the user-run runme_urbs script, the preparation script runfunctions_admm.py, the parallel jobs run_Worker.py and finally the Class urbsADMMmodel.


Finally the :ref:`guide_for_admm` gives ideas on how to improve, use, or extend the code, and on how to unify it with the urbs master branch.

Decomposition
^^^^^^^^^^^^^^

First the concepts of decomposition are introduced.
The idea of decomposition is that a large model might not fit into working memory,
so it is desirable to split it into several smaller models that are independent to a certain degree.
These models are called sub models.
As the sub models are not truly independent there is a master model which coordinates the communication of the sub models.



Decomposition in energy system modelling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
First the concepts of decomposition are introduced.

Due to computational and organizational reasons, it may be practical to partition an optimization problem (such as one depicting an energy system model) to multiple smaller "subproblems" . In case these smaller problems do not depend on each other, i.e. do not share any common (complicating) variables or common (complicating) constraints, then the approach is trivial: by solving these smaller problems independently, we recover the solution to the original problem.

However, energy systems consist often of subsystems which are dependent of each other. In this case, the solutions of the subproblems need to be consistent with each other, i.e. when one partitions an energy system model regionally, the interconnector power flows (and their capacities) between two regions would couple two regions. Mathematical decomposition methods are iterative methods, by which the subproblems are solved iteratively, and between each iteration, coordination steps are taken so that 1) the coupled subproblems are in consensus regarding their complicating variables and 2) the complicating constraints are satisfied. Thereby, these mettods offer here a so far not thoroughly tapped potential:

a) through the parallel solution of these subproblems, the large number of available processors can be made use of in order to overcome divergent runtimes

b) through sequential solution of these subproblems, only a subset of the original problem has to be contained in the working memory simultaneously.



