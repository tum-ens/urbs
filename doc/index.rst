.. urbs documentation master file, created by
   sphinx-quickstart on Wed Sep 10 11:43:04 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

urbs: A linear optimisation model for distributed energy systems
================================================================

:Author: Johannes Dorfner, <johannes.dorfner@tum.de>
:Version: |version|
:Date: 10 September 2014
:Copyright:
  This documentation is licensed under a `Creative Commons Attribution 4.0 
  International`__ license.

.. __: http://creativecommons.org/licenses/by/4.0/


Overview
--------
* `urbs`_ is a linear programming model for multi-commodity energy systems with 
  a focus on optimal storage sizing and use.
* It finds the minimum cost energy system to satisfy given demand timeseries 
  for possibly multiple commodities (e.g. electricity).
* By default, operates on hourly-spaced timesteps (configurable).
* Thanks to `pandas`_, complex data analysis code is short and extensible.
* The model itself is quite small thanks to relying on the `Coopr`_/`Pyomo`_
  packages.
* urbs includes reporting and plotting functionality.

Contents
--------

.. toctree::
   :maxdepth: 2

   tutorial
   api


Screenshots
-----------

.. image:: img/plot.*
   :width: 66%
   :align: center
.. image:: img/comp.*
   :width: 66%
   :align: center
   

Dependencies
------------

* `coopr`_ interface to optimisation solvers (CPLEX, GLPK, Gurobi, ...).
  At least one supported solver by coopr must be installed.
* `matplotlib`_ for plotting
* `pandas`_ for input and result data handling, report generation 
* `pyomo`_ for the model equations

   
.. _coopr: https://software.sandia.gov/trac/coopr
.. _matplotlib: http://matplotlib.org
.. _pandas: https://pandas.pydata.org
.. _pyomo: https://software.sandia.gov/trac/coopr/wiki/Pyomo
.. _urbs: https://github.com/tum-ens/urbs

