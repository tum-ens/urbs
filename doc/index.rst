.. urbs documentation master file, created by
   sphinx-quickstart on Wed Sep 10 11:43:04 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
.. module:: urbs

urbs: A linear optimisation model for distributed energy systems
================================================================

:Maintainer: Johannes Dorfner, <johannes.dorfner@tum.de>
:Organization: `Chair of Renewable and Sustainable Energy Systems`_,
               Technical University of Munich
:Version: |version|
:Date: |today|
:Copyright:
  The model code is licensed under the `GNU General Public License 3.0
  <http://www.gnu.org/licenses/gpl-3.0>`_.
  This documentation is licensed under a `Creative Commons Attribution 4.0 
  International <http://creativecommons.org/licenses/by/4.0/>`_ license.


Contents
--------

User's manual
^^^^^^^^^^^^^

These documents give a general overview and help you getting started from after
the installation (which is covered in the `README.md`_ file on GitHub) to you
first running model.

.. toctree::
   :maxdepth: 1

   Users_guide

Mathematical documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Continue here if you want to understand the theoretical conception of the model
generator, the logic behind the equations and the structure of the features.

.. toctree::
   :maxdepth: 1

   theory

Technical documentation
^^^^^^^^^^^^^^^^^^^^^^^

Continue here if you want to understand in detail the model generator
implementation.

.. toctree::
   :maxdepth: 1
   
   implementation
   api


Features
--------
* `urbs`_ is a linear programming optimization model for multi-commodity energy
  systems, their sizing, development and utilization.
* It finds the minimum cost energy system to satisfy given demand timeseries 
  for possibly multiple commodities (e.g. electricity, heat).
* By default, operates on hourly-spaced timesteps (configurable) and can be 
  used for intertemporal optimization.
* Thanks to `pandas`_, complex data analysis code is short and extensible.
* The model itself is quite small thanks to relying on the `Pyomo`_
  package.
* urbs includes reporting and plotting functions for rapid scenario 
  development.

Changes
-------

2017-01-13 Version 0.7
^^^^^^^^^^^^^^^^^^^^^^

* Maintenance: Model file ``urbs.py`` split into subfiles in folder ``urbs``
* Feature: Usable area in site implemented as possible constraint
* Feature: Plot function (and ``get_timeseries``) now support grouping of
  multiple sites
* Feature: Environmental commodity costs (e.g. emission taxes or other
  pollution externalities)
* Bugfix: column *Overproduction* in report sheet did not respect DSM


2016-08-18 Version 0.6
^^^^^^^^^^^^^^^^^^^^^^

* :ref:`sec-dsm-constr` added
* :ref:`sec-partial-startup-constr` added
* Various fixes in examples, docs and tutorials for Pyomo 4/Python 3 changes


2016-02-16 Version 0.5
^^^^^^^^^^^^^^^^^^^^^^

* Support for Python 3 added
* Support for Pyomo 4 added, while maintaining Pyomo 3 support. Upgrading to
  Pyomo 4 is advised, as support while be dropped with the next release to
  support new features.
* New feature: maximal power gradient for conversion processes
* Documentation: `buyselldoc` (expired) long explanation for `Buy` and `Sell` 
  commodity types
* Documentation: :doc:`implementation` full listing of sets, parameter,
  variables, objective function and constraints in mathematical notation and
  textual explanation
* Documentation: updated installation notes in `README.md`_
* Plotting: automatic sorting of time series by variance makes it easier to
  read stacked plots with many technologies  


2015-07-29 Version 0.4
^^^^^^^^^^^^^^^^^^^^^^

* Additional commodity types `Buy` and `Sell`, which support time-dependent 
  prices.
* Persistence functions `load` and `save`, based on pickle, allow saving
  and retrieving input data and problem instances including results, for later
  re-plotting or re-analysis without having to solve them again.
* Documenation: `workflow` tutorial added with example "Newsealand"

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
   
An exemplary comparison script ``comp.py`` shows how one can create automated 
cross-scenario analyses with very few lines of `pandas`_ code. This resulting 
figure shows system costs and generated electricity by energy source over five 
scenarios: 
   
.. image:: img/comparison.*
   :width: 95%
   :align: center
   

Dependencies
------------

* `Python`_ versions 2.7 or 3.x are both supported.
* `pyomo`_ for model equations and as the interface to optimisation solvers 
  (CPLEX, GLPK, Gurobi, ...). Version 4 recommended, as version 3 support
  (a.k.a. as coopr.pyomo) will be dropped soon.
* `matplotlib`_ for plotting due to its capability to customise everything.
* `pandas`_ for input and result data handling, report generation 
* Any solver supported by pyomo; suggestion: `GLPK`_
   
.. _glpk: https://www.gnu.org/software/glpk/
.. _Chair of Renewable and Sustainable Energy Systems: http://www.ens.ei.tum.de/
.. _matplotlib: http://matplotlib.org
.. _pandas: http://pandas.pydata.org
.. _pyomo: http://www.pyomo.org
.. _python: https://www.python.org/
.. _readme.md: https://github.com/tum-ens/urbs/blob/master/README.md#installation
.. _urbs: https://github.com/tum-ens/urbs

