.. module:: urbs

urbs.py module description
==========================

Overview
--------

The following is a minimum "hello world" script that shows the life cycle of 
the optimization object `prob`, and how the various :mod:`urbs` module 
functions create it, modify it and process it.::

    import urbs
    from coopr.opt.base import SolverFactory
    
    # read input, create optimisation problem
    data = urbs.read_excel('data-example.xlsx')
    model = urbs.create_model(data)
    prob = model.create()
    
    # solve problem, read results
    optim = SolverFactory('glpk')
    result = optim.solve(prob)
    prob.load(result)

    # write report and plot timeseries
    urbs.report(prob, 'report.xlsx')
    urbs.plot(prob, 'Elec', 'Mid')

Members
-------

This section lists and describes the use of all module-level functions. They
are roughly ordered from high-level to low-level access, followed by helper 
functions.

Create model
^^^^^^^^^^^^

.. function:: read_excel(filename)

  :param str filename: spreadsheet filename
  :return dict data: urbs input dict 
  
  The spreadsheet must contain 6 sheets labelled 'Commodity', 'Process', 
  'Transmission', 'Storage', 'SupIm', and 'Demand'. It can contain a 7th sheet
  called 'Hacks'. If present
  
  Refer to the `mimo-example.xlsx` file for exemplary documentation of the 
  table contents and definitions of all attributes by selecting the column
  titles. 
  
  
.. function:: create_model(data, timesteps)

  Returns a Pyomo `ConcreteModel` object, which as to be still converted to a
  problem instance using its method ``create``.
  
  :param dict data: input like created by urbs.read_excel
  :param list timesteps: consecutive list of modelled timesteps
  
  Timestep numbers must match those of the demand and supim timeseries. 

  
.. function:: add_hacks(model, hacks)

  Is called by :func:`create_model` to add special elements, e.g. constraints,
  to the model. Each hack, if present, can trigger the creation of additional
  sets, parameters, variables or constraints. Refer to the code of this
  function to see which hacks exists and what they do.
  
  As of v0.3, only one hack exists: if a line "Global CO2 limit" exists in the
  hacks DataFrame, its value is used as a global upper limit for a constraint
  that limits the annual creation of the commodity "CO2".

  :param model: urbs model object (not instance!)
  :param hacks: a DataFrame of hacks  
  
  :return model: the modified urbs model object

  
Report & plotting
^^^^^^^^^^^^^^^^^

These two **high-level** functions cover the envisioned use of the unmodified
urbs model and should cover most use cases.

.. function:: plot(prob, com, sit, [timesteps=None])

  :param prob: urbs model instance
  :param str com: commodity name to plot
  :param str sit: site name to plot
  :param list timesteps: timesteps to plot, default: all
  
  :return fig: matplotlib figure handle 

  
.. function:: report(prob, filename, commodities, sites)

  Write optimisation result summary to spreadsheet

  :param prob: urbs model instance
  :param str filename: spreadsheet filename, will be overwritten if exists
  :param list commodities: list of commodities for which to output timeseries
  :param list sites: list sites for which to output timeseries


.. _medium-level-functions:
  
Retrieve results
^^^^^^^^^^^^^^^^

While :func:`report` and :func:`plot` are quite flexible, custom
result analysis scripts might be needed. These can be built on top of the
following two **medium-level** functions. They retrieve all time-dependent and
-independent quantities and return them as ready-to-use DataFrames.

.. function:: urbs.get_constants(prob)
  
  Return summary DataFrames for time-independent variables
  
  :param prob: urbs model instance
  
  :return tuple constants: costs, process, transmission, storage and emissions

  
.. function:: urbs.get_timeseries(prob, com, sit, timesteps=None)

  Return DataFrames of all timeseries referring to a given commodity and site

  :param prob: urbs model instance
  :param str com: commodity name to plot
  :param str sit: site name to plot
  :param list timesteps: timesteps to plot, default: all

  
Low-level access
^^^^^^^^^^^^^^^^

If the previous functions still don't cut it, there are three **low-level**
functions.

.. function:: urbs.list_entities(prob, entity_type)

  :param prob: urbs model instance
  :param str entity_type: allowed values: set, par, var, con, obj 
  
  :return: a DataFrame with name, description and domain of entities

.. function:: urbs.get_entity(prob, name)

  :param prob: urbs model instance
  :param str name: name of a model entity

  :return: Series with values of model entity
  
.. function:: urbs.get_entities(prob, names)

  :param prob: urbs model instance
  :param list name: list of model entity names
  
  :return: DataFrame with values entities in columns
  
  .. note:: only call for entities with identical domains (can be 
    checked with :func:`list_entities`)

Helper functions
^^^^^^^^^^^^^^^^

.. function:: urbs.annuity_factor

  Annuity factor formula.

  Evaluates the annuity factor formula for depreciation duration
  and interest rate. Works also well for equally sized numpy arrays as input.
    
  :param int n: number of depreciation periods (years)
  :param float i: interest rate (percent, e.g. 0.06 means 6 %)

  :return: value of the expression :math:`\frac{(1+i)^n i}{(1+i)^n - 1}`

  
.. function:: urbs.commodity_balance(m, tm, sit, com):

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

  
.. function:: urbs.split_columns(columns, [sep='.'])

  Given a list of column labels containing a separator string (default: '.'),
  derive a MulitIndex that is split at the separator string.
  
  :param list columns: column labels, each containing the separator string
  :param str sep: the separator string (default: '.')
  
  :return: a MultiIndex corresponding to input, with levels split at separator
  
  
.. function:: urbs.to_color(obj=None)

  Assign a deterministic pseudo-random color to argument.

  If :data:`COLORS[obj] <COLORS>` is set, return that. Otherwise, create a 
  deterministically random color from the `` hash(obj)`` representation 
  string. For strings, this value depends only on the string content, so that 
  same strings always yield the same color.

  :param obj: any hashable object

  :return: a `(r,g,b)` tuple if COLORS[obj] exists, otherwise a hexstring

.. data:: COLORS
  
  Dictionary of process and site colors. Colors are stored as `(r,g,b)`
  tuples in range `0-255`. To retrieve a color in a form usable with 
  matplotlib, used the helper function :func:`to_color`.
  
  This snippet from the  example script `runme.py` shows how to add custom 
  colors::
      
      # add or change plot colours
      my_colors = {
          'South': (230, 200, 200),
          'Mid': (200, 230, 200),
          'North': (200, 200, 230)}
      for country, color in my_colors.iteritems():
          urbs.COLORS[country] = color
