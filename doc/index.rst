.. urbs documentation master file, created by
   sphinx-quickstart on Wed Sep 10 11:43:04 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
.. module:: urbs

urbs: A linear optimisation model for distributed energy systems
================================================================

:Maintainer: Johannes Dorfner, <johannes.dorfner@tum.de>
:Organization: `Institute for Renewable and Sustainable Energy Systems`_,
               Technische Universität München
:Version: |version|
:Date: |today|
:Copyright:
  This documentation is licensed under a `Creative Commons Attribution 4.0 
  International`__ license.

.. __: http://creativecommons.org/licenses/by/4.0/


Contents
--------

This documentation contains the following pages:

.. toctree::
   :maxdepth: 1

   overview
   tutorial
   workflow
   
More technical documents deal with the internal workings:   
   
.. toctree::
   :maxdepth: 1
   
   report
   api
   mathdoc


Features
--------
* `urbs`_ is a linear programming model for multi-commodity energy systems with 
  a focus on optimal storage sizing and use.
* It finds the minimum cost energy system to satisfy given demand timeseries 
  for possibly multiple commodities (e.g. electricity).
* By default, operates on hourly-spaced timesteps (configurable).
* Thanks to `pandas`_, complex data analysis code is short and extensible.
* The model itself is quite small thanks to relying on the `Coopr`_/`Pyomo`_
  packages.
* urbs includes reporting and plotting functions for rapid scenario 
  development.

Changes
-------

2015-07-29 Version 0.4
^^^^^^^^^^^^^^^^^^^^^^

* Additional commodity types `Buy` and `Sell`, which support time-dependent 
  prices.
* Persistence functions `load` and `save`, based on pickle, allow saving
  and retrieving input data and problem instances including results, for later
  re-plotting or re-analysis without having to solve them again.
* Documenation: :doc:`workflow` tutorial added with example "Newsealand"

2014-12-05 Version 0.3
^^^^^^^^^^^^^^^^^^^^^^

* Processes now support multiple inputs and multiple output commodities.
* As a consequence :func:`plot` now plots commodity balance by processes, not 
  input commodities.
* urbs now supports input files with only a single site; simply delete all
  entries from the 'Transmission' spreadsheet and only use a single site name 
  throughout your input.
* Moved hard-coded 'Global CO2 limit' constraint to dedicated "Hacks"
  spreadsheet, while the constraint is :func:`add_hacks`.
* More docstrings and comments in the main file ``urbs.py``.


Screenshots
-----------

This is a typical result plot created by :func:`urbs.plot`, showing electricity
generation and storage levels in one site over 10 days (240 time steps):

.. image:: img/plot.*
   :width: 95%
   :align: center
   
A comparison script ``comp.py`` how one can create automated cross-scenario
analyses. This figure shows costs and generated electricity by source for 5
scenarios: 
   
.. image:: img/comparison.*
   :width: 95%
   :align: center
   

Dependencies
------------

* `coopr`_ interface to optimisation solvers (CPLEX, GLPK, Gurobi, ...).
  At least one supported solver by coopr must be installed.
* `matplotlib`_ for plotting
* `pandas`_ for input and result data handling, report generation 
* `pyomo`_ for the model equations

   
.. _coopr: https://software.sandia.gov/trac/coopr
.. _Institute for Renewable and Sustainable Energy Systems: http://www.ens.ei.tum.de/
.. _matplotlib: http://matplotlib.org
.. _pandas: https://pandas.pydata.org
.. _pyomo: https://software.sandia.gov/trac/coopr/wiki/Pyomo
.. _urbs: https://github.com/tum-ens/urbs

