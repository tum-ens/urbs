.. module:: urbs

urbs.py module description
--------------------------

Overview
^^^^^^^^

The following is a minimum "hello world" script that shows the life cycle of 
the optimization object `prob`, and how the various :mod:`urbs` module 
functions create it, modify it and process it.::

	import os
	import pandas as pd
	import pyomo.environ
	import shutil
	import urbs
	from pyomo.opt.base import SolverFactory
   
	# read input, create optimisation problem
	data = urbs.read_excel('mimo-example.xlsx')
	prob = urbs.create_model(data)

	# solve problem, read results
	optim = SolverFactory('glpk')
	result = optim.solve(prob, tee=True)

	# save problem instance (incl. input and result) for later analyses
	urbs.save(prob, 'model.h5')

	# write report and plot timeseries
	urbs.report(prob, 'report.xlsx')
	urbs.result_figures(prob, 'plot', 'scenario_base')

The following lists and describes the use of all module-level functions. They
are roughly ordered from high-level to low-level access, followed by helper 
functions.

Create model
^^^^^^^^^^^^

.. function:: read_excel(filename)

  :param str filename: spreadsheet filename
  :return: urbs input dict 
  
  The spreadsheet must contain 7 sheets labelled 'Commodity', 'Process',
  'Process-Commodity', 'Transmission', 'Storage', 'Demand' and 'SupIm'.
  It can contain three additional sheets called 'Buy-Sell-Price', 'DSM' and 'Global'.
  
  Refer to the `mimo-example.xlsx` file for exemplary documentation of the 
  table contents and definitions of all attributes by selecting the column
  titles. 
  
  
.. function:: create_model(data, [dt=1], [timesteps=None], [dual=False])

  Returns a Pyomo `ConcreteModel` object.
  
  :param dict data: input like created by :func:`read_excel`
  :param float dt: length of each modelled timestep (unit: hours)
  :param list timesteps: consecutive list of modelled timesteps
  :param boolean dual: boolean parameter to enable dual variables in the model
 
  :return: urbs model object
  
  Timestep numbers must match those of the demand and supim timeseries.
  
  If argument ``data`` has the key ``'hacks'``, function :func:`add_hacks` is
  called with ``data['hacks']`` as the second argument.  

  
Report & plotting
^^^^^^^^^^^^^^^^^

These two **high-level** functions cover the envisioned use of the unmodified
urbs model and should cover most use cases.

.. function:: report(prob, filename, [report_tuples=None], [report_sites_name=None])

    Write optimisation result summary to spreadsheet.
    
    :param prob: urbs model instance
    :param str filename: spreadsheet filename, will be overwritten if exists
    :param list report_tuples: list of (site, commodity) tuples for which to output timeseries, default: all
    :param list report_sites_name: dict of names for created timeseries, default: same with tuples' names


.. function:: result_figures(prob, figure_basename, [plot_title_prefix=None], [plot_tuples=None], [plot_sites_name=None], [periods=None], [extensions=None], [**kwds])


    :param prob: urbs model instance
    :param str figure_basename: relative filename prefix that is shared
    :param str plot_title_prefix: plot title identifier, default: same with figure_basename
    :param list plot_tuples: list of (site, commodity) tuples for which to plot (site may be individual site names or lists of sites), default: all demand (sit, com) tuples are plotted
	:param dict plot_sites_name: dict of names for created plots, default: same with tuples' names
	:param dict periods: dict of {'period name': timesteps_list} items, default: one period 'all' with all timesteps is assumed
	:param list extensions: list of file extensions for plot images, default: [png, pdf]
	:param ``*kwds:`` keyword arguments are forwarded to urbs.plot()

.. _medium-level-functions:
  
Retrieve results
^^^^^^^^^^^^^^^^

While :func:`report` and :func:`result_figures` are quite flexible, custom
result analysis scripts might be needed. These can be built on top of the
following two **medium-level** functions. They retrieve all time-dependent and
-independent quantities and return them as ready-to-use DataFrames.

.. function:: get_constants(prob)
  
  Return summary DataFrames for time-independent variables
  
  :param prob: urbs model instance
  
  :return: tuple of constants (costs, process, transmission, storage)

  
.. function:: get_timeseries(prob, com, sit, timesteps=None)

  Return DataFrames of all timeseries referring to a given commodity and site

  :param prob: urbs model instance
  :param str com: commodity name
  :param str sit: site name
  :param list timesteps: timesteps, default: all modelled timesteps

  :return: tuple of timeseries (created, consumed, storage, imported, exported) 
    tuple of DataFrames timeseries. These are:

        * created: timeseries of commodity creation, including stock source
        * consumed: timeseries of commodity consumption, including demand
        * storage: timeseries of commodity storage (level, stored, retrieved)
        * imported: timeseries of commodity import (by site)
        * exported: timeseries of commodity export (by site)
        * dsm: timeseries of DSM up-/downshifts (by site and commodity)

        
Persistence
^^^^^^^^^^^

To store valuable results for later analysis, or cross-scenario comparisons
weeks after the original run, saving a problem instance with loaded results
makes it possible to use one's comparison scripts without having to solve the
optimisation problem again. Simply :func:`load` the previously stored object 
using :func:`save`:

.. function:: save(prob, filename)

    Save urbs model instance to a gzip'ed pickle file
    
    `Pickle <https://docs.python.org/2/library/pickle.html>`_ is the standard
    Python way of serializing and de-serializing Python objects. By using it,
    saving any object, in case of this function a Pyomo ConcreteModel, becomes
    a twoliner.
    
    `GZip <https://docs.python.org/2/library/gzip.html>`_ is a standard Python
    compression library that is used to transparently compress the pickle file
    further.
    
    It is used over the possibly more compact bzip2 compression due to the
    lower runtime. Source: <http://stackoverflow.com/a/18475192/2375855>
    
    :param prob: an urbs model instance
    :param str filename: pickle file to be written
        
    :return: nothing
        
.. function:: load(filename)

    Load an urbs model instance from a gzip'ed pickle file
    
    :param str filename: pickle file
    
    :return prob: the unpickled urbs model instance

Low-level access
^^^^^^^^^^^^^^^^

If the previous functions still don't cut it, there are three **low-level**
functions.

.. function:: list_entities(prob, entity_type)

  :param prob: urbs model instance
  :param str entity_type: allowed values: set, par, var, con, obj 
  
  :return: a DataFrame with name, description and domain of entities

.. function:: get_entity(prob, name)

  :param prob: urbs model instance
  :param str name: name of a model entity

  :return: Series with values of model entity
  
.. function:: get_entities(prob, names)

  :param prob: urbs model instance
  :param list name: list of model entity names
  
  :return: DataFrame with values entities in columns
  
  Only call ``get_entities`` for entities that share identical
  domains. This can be checked with :func:`list_entities`. For example,
  variable ``cap_pro`` naturally has the same domain as ``cap_pro_new``.
  
Helper functions
^^^^^^^^^^^^^^^^

.. function:: annuity_factor(n, i)

  Annuity factor formula.

  Evaluates the annuity factor formula for depreciation duration
  and interest rate. Works also well for equally sized numpy arrays as input.
    
  :param int n: number of depreciation periods (years)
  :param float i: interest rate (e.g. 0.06 means 6 %)

  :return: value of the expression :math:`\frac{(1+i)^n i}{(1+i)^n - 1}`

  
.. function:: commodity_balance(m, tm, sit, com)

  Calculate commodity balance at given timestep.

  For a given commodity, site and timestep, calculate the balance of
  consumed (to process/storage/transmission, counts positive) and provided
  (from process/storage/transmission, counts negative) energy. Used as helper
  function in :func:`create_model` for defining constraints on demand and 
  stock commodities.

  :param m: the ConcreteModel object
  :param tm: the timestep number
  :param sit: the site
  :param co: the commodity

  :return: amount of consumed (positive) or provided (negative) energy

  
.. function:: split_columns(columns, [sep='.'])

  Given a list of column labels containing a separator string (default: '.'),
  derive a MulitIndex that is split at the separator string.
  
  :param list columns: column labels, each containing the separator string
  :param str sep: the separator string (default: '.')
  
  :return: a MultiIndex corresponding to input, with levels split at separator
  
  
.. function:: to_color(obj=None)

  Assign a deterministic pseudo-random color to argument.

  If :data:`COLORS[obj] <COLORS>` is set, return that. Otherwise, create a
  deterministically random color from the :func:`hash` of that object. For
  strings, this value depends only on the string content, so that identical
  strings always yield the same color.

  :param obj: any hashable object

  :return: a `(r,g,b)` tuple if COLORS[obj] exists, otherwise a hexstring

.. data:: COLORS
  
  :class:`dict` of process and site colors. Colors are stored as `(r,g,b)`
  tuples in range `0-255` each. To retrieve a color in a form usable with 
  matplotlib, used the helper function :func:`to_color`.
  
  This snippet from the  example script `runme.py` shows how to add custom 
  colors::
      
      # add or change plot colours
      my_colors = {
          'South': (230, 200, 200),
          'Mid': (200, 230, 200),
          'North': (200, 200, 230)}
      for country, color in my_colors.items():
          urbs.COLORS[country] = color

		  
Helper functions for DSM
^^^^^^^^^^^^^^^^^^^^^^^^		  
		  
.. function:: dsm_down_time_tuples(time, sit_com_tuple, m):
   
   Function to generate dictionaries for DSM timestep pairs (t_upshift, t_downshift)
   of a commodity in a given site.

    :param list time: list with timestep indices, at which the DSM upshift may occur
    :param lost sit_com_tuple: a list of (site, commodity) tuples
    :param m: model instance

    :return: A list of possible timestep pairs (t_upshift, t_downshift) 
	depending on site and commodity

.. function:: dsm_time_tuples(timestep, time, delay):
    
	Function to generate the timesteps, in which DSM downshift has to occur in return of
	a DSM upshift occuring in a given timestep

    :param int timestep: timestep of DSM upshift
    :param list time: list with all modelled timesteps
    :param int delay: allowed DSM delay (in hours) in a particular site and commodity

    :return: A list of possible downshift timesteps in return of a given upshift time step,
	in a particular site and commotidy, subject to a certain allowable delay duration

.. function:: dsm_recovery(timestep, time, recov):

    Function to generate the time frame, at which the limitation of recovery for DSM upshift
	takes place
	
    :param int timestep: timestep of DSM upshift
    :param list time: list with all modelled timesteps
    :param int recov: recovery duration (in hours) required for a DSM upshift in a particular 
	site and commodity

    :return: A list of timesteps which are within the recovery frame of a DSM upshift