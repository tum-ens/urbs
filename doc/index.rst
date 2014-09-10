.. urbs documentation master file, created by
   sphinx-quickstart on Wed Sep 10 11:43:04 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

urbs: A linear optimisation model for distributed energy systems
================================================================

Overview
--------
* URBS is a linear programming model for multi-commodity energy systems with 
  a focus on optimal storage sizing and use.
* It finds the minimum cost energy system to satisfy given demand timeseries 
  for possibly multiple commodities (e.g. electricity).
* By default, operates on hourly-spaced timesteps (configurable).
* Thanks to `pandas <https://pandas.pydata.org>`_, complex data analysis is 
  easy.
* The model itself is quite small (<50 kB source code) thanks to relying on 
  the `Coopr <https://software.sandia.gov/trac/coopr>`_/`Pyomo 
  <https://software.sandia.gov/trac/coopr/wiki/Pyomo>`_ and includes 
  reporting and plotting functionality.


Contents
--------

.. toctree::
   :maxdepth: 2

   tutorial
   api

