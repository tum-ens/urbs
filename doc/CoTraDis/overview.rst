Overview
--------

How to use the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You should start with this overview which explains the underlying ideas of coupling transmission and distribution systems in the given model framework as developed in the master thesis of Beneharo Reveron Baecker: "Implementation of a novel energy system model coupling approach to co-optimize transmission and active distribution systems", 2021.

To fully comprehend the documentation you should be familiar with the urbs model already (see :ref:`overview` of the urbs documentation).

The documentation is structured into four main parts:

1. The development of a model framework that enables the consideration of distribution systems. The implementations to consider their characteristics properly are described in :ref:`distribution_system_implementation`.

2. An automated coupling of transmission and distribution system data. The implementation can be seen in the section :ref:`transdist_implementation`.

3. A suitable approach to reduce the computational complexity. The implementations introduce the typeperiod idea in combination with time series aggregation methods.
It is decribed in detailin the section :ref:`typeperiod_tsam_implementation`. If you want to understand the mathematical background of tsam, you should first have a look at the documentation of the
open source `python tsam package <https://tsam.readthedocs.io/en/latest/index.html>`__  described by Kotzuer et al.

4. Finally the :ref:`user-guide` gives ideas on how to use the provided framework for future projects.


