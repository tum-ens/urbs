.. currentmodule:: urbs

.. _tutorial:

Tutorial
========

The README file contains `complete installation instructions`__. This manual
expands on the steps that follow this installation.

.. __: https://github.com/tum-ens/urbs/blob/master/README.md#installation

This tutorial is a commented walk-through through the script ``runme.py``,
which is a demonstration user script that can serve as a good basis for a
production script.

Initialisation
--------------

Imports
^^^^^^^

.. literalinclude:: ../runme.py
   :end-before: # INIT
   
Several packages are included.

* `coopr.environ` is not used, but required for compatibility with future 
  releases of `coopr`_. Omitting this line triggers the following warning:
  
  .. note:: DEPRECATION WARNING: beginning in Coopr 4.0, plugins (including
     solvers and DataPortal clients) will not be automatically registered. To
     automatically register all plugins bundled with core Coopr, user scripts
     should include the line, "import coopr.environ". 

* `os`_ is a builtin Python module, included here for its `os.path`_ submodule
  that offers operating system independent path manipulation routines. The 
  following code creates the path string ``'result' + os.path.sep + 'foo'``,
  checks whether it exists and creates the folder(s) if needed. This can
  become handy to prepare a new directory for result output::
      
      result_dir = os.path.join('result', 'foo')
      if not os.path.exists(result_dir):
          os.makedirs(result_dir)
  
* `urbs`_ is the module whose functions are used mainly in this script. These
  are :func:`read_excel`, :func:`create_model`, :func:`report` and
  :func:`plot`. More functions can be found in the document :ref:`API`.

* `coopr.opt.base`_ is a utility package by `coopr`_ and provides the function
  ``SolverFactory`` that allows creating a ``solver`` object. This objects 
  hides the differences in input/output formats among solvers from the user.
  More on that in section `Solving`_ below.

Settings
^^^^^^^^
   
.. literalinclude:: ../runme.py
   :start-after: # INIT
   :end-before: # SCENARIOS

Variable ``filename`` defines the input spreadsheet, from which the
optimization problem will draw all its set/parameter data. Its structure is
highly standardised, but only because of :func:`read_excel` and its underlying
function :func:`pandas.read_excel`.
   
Variable ``timesteps`` is the list of timesteps to be simulated. Its members
must be a subset of the labels used in ``filename``'s sheets "Demand" and
"SupIm". It is one of the two function arguments to :func:`create_model` and
accessible directly, because one can quickly reduce the problem size by
reducing the simulation ``length``, i.e. the number of timesteps to be
optimised. 

:func:`range` is used to create a list of consecutive integers. The argument
``+1`` is needed, because ``range(a,b)`` only includes integers from ``a`` to
``b-1``:: 
    
    >>> range(1,11)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

Scenarios
---------

The following section deals with the definition of different scenarios.
Starting from the same base scenarios, defined by the data in ``filename``,
they serve as a short way of defining the difference in input data. If needed,
completely separate input data files could be loaded as well.

In addition to defining scenarios, the ``scenarios`` list allows to select a
subset to be actually run.

Scenario functions
^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../runme.py
   :start-after: # SCENARIOS
   :end-before: # select scenarios
   
A scenario is simply a function with the required argument ``data``, the input
data :class:`dict`. By convention, it must contain the six keys ``commodity``,
``process``, ``storage``, ``transmission``, ``demand``, and ``supim``. Each
value must be a :class:`pandas.DataFrame`, whose index (row labels) and
columns (column labels) conforms to the specification given by the dummy
dataset in the spreadsheet :file:`data-example.xlsx`.

For example, :func:`scenario_stock_prices` selects all stock commodities from
the :class:`DataFrame` ``commodity``, and increases their *price* value by 50%.
See also pandas documentation :ref:`Selection by label <pandas:indexing.label>`
for more information about the ``.loc`` function to access fields. Also note
the use of `Augmented assignment statements`_ (``*=``) to modify data 
in-place.

Scenario :func:`scenario_co2_limit` shows the simple case of changing a single
input data value. In this case, a 95% CO2 reduction compared to the base
scenario must be accomplished. This drastically limits the amount of coal and
gas that may be used by all three sites.

Scenario :func:`scenario_north_process_caps` demonstrates accessing single
values in the ``process`` :class:`~pandas.DataFrame`. By reducing the amount of
renewable energy conversion processes (hydropower and biomass), this scenario
explores the "second best" option for this region to supply its demand.

Scenario :func:`scenario_all_together` finally shows that scenarios can also be
combined by calling other scenario functions.

Scenario selection
^^^^^^^^^^^^^^^^^^
   
.. literalinclude:: ../runme.py
   :start-after: # select scenarios
   :end-before: # MAIN

In Python, functions are objects, so they can be put into data structures just
like any variable could be. In the following `main loop`_, this list is used to
control which scenarios are being optimised. 
   
Main loop
---------

Having prepared settings, input data and scenarios, the actual computations
happen in the remainder of the script. It is executed ``for`` each of the
scenarios included in the scenario list.

Solving
^^^^^^^

.. literalinclude:: ../runme.py
   :start-after: # MAIN
   :end-before: # write report

This section is the "work horse", where most computation and time is spent. For
each scenario, first the scenario name is retrieved from the function object in
local variable ``sce``. It is used for figure captions and filenames later on.
The dataset for the base scenario is (re)loaded from the input file and the
:func:`scenario` function is applied to modify the input data accordingly.

In the next five lines, the optimization problem is first defined
(:func:`create_model`), then filled with values (``create``). The
``SolverFactory`` object is an abstract representation of the solver used.
The returned object ``optim`` has a method :meth:`set_options` to set solver
options (not shown in this tutorial).

.. note:: If you use :meth:`set_options`, to set custom solver options,
   always make its use dependent on the attribute ``optim.name``.
   Otherwise, the script will raise Exceptions if the used solver is changed.

The remaining two lines call the solver and read the ``result`` object back
into the ``prob`` object, which is queried to for variable values in the
remaining script file. Argument ``tee=True`` enables the realtime console
output for the solver. If you want less verbose output, simply set it to
``False`` or remove it.
   
Reporting
^^^^^^^^^

.. literalinclude:: ../runme.py
   :start-after:     # write report
   :end-before:     # add or change plot colours
   
The :func:`urbs.report` function creates a spreadsheet from the main results.
Summaries of costs, emissions, capacities (process, transmissions, storage) are
saved to one sheet each. For timeseries, each combination of the given
``sites`` and ``commodities`` are summarised both in sum (in sheet "Energy
sums") and as individual timeseries (in sheet "... timeseries"). See also
:ref:`report-function` for a detailed explanation of this function's implementation.
   
Plotting
^^^^^^^^

.. literalinclude:: ../runme.py
   :start-after:     # add or change plot colours
   :end-before:    # create timeseries plot for each demand
   
First, the use of the module constant :data:`COLORS` for customising plot
colors is demonstrated. All plot colors are user-defineable by adding color 
:func:`tuple` ``(r, g, b)`` or modifying existing tuples for commodities and 
plot decoration elements. Here, new colors for displaying import/export are
added. Without these, pseudo-random colors are generated in 
:func:`to_color`.

.. literalinclude:: ../runme.py
   :start-after:    # create timeseries plot for each demand
   
Finally, for each demand commodity (only ``Elec`` in this case), a plot over
the whole optimisation period is created. If ``timesteps`` were longer, a
shorter plotting period could be defined and given as an optional argument to
:func:`plot`.

The paragraph "change figure title" shows exemplarily how to use matplotlib
manually to modify some aspects of a plot without having to recreate the
plotting function from scratch. For more ideas for adaptations, look into
:func:`plot`'s code or the `matplotlib documentation`_.

The last paragraph uses the :meth:`~matplotlib.figure.Figure.savefig` method
to save the figure as a pixel ``png`` (raster) and ``pdf`` (vector) image. The
``bbox_inches='tight'`` argument eliminates whitespace around the plot.

.. note:: :meth:`~matplotlib.figure.Figure.savefig` has some more interesting
   arguments. For example ``dpi=600`` can be used to create higher resolution
   raster output for use with printing, in case the preferable vector images.
   The filename extension or the optional ``format`` argument can be used to
   set the output format. Available formats depend on the used `plotting
   backend`_. Most backends support png, pdf, ps, eps and svg.  

   
.. _augmented assignment statements: 
    http://docs.python.org/2/reference/\
    simple_stmts.html#augmented-assignment-statements
.. _coopr: https://software.sandia.gov/trac/coopr
.. _coopr.opt.base: 
    https://projects.coin-or.org/Coopr/browser/coopr.opt/trunk/coopr/opt/base
.. _matplotlib documentation:
    http://matplotlib.org/contents.html
.. _os: https://docs.python.org/2/library/os.html
.. _os.path: https://docs.python.org/2/library/os.path.html
.. _pandas: https://pandas.pydata.org
.. _plotting backend: 
    http://matplotlib.org/faq/usage_faq.html#what-is-a-backend
.. _pyomo: https://software.sandia.gov/trac/coopr/wiki/Pyomo
.. _side effect: 
    https://en.wikipedia.org/wiki/Side_effect_%28computer_science%29
.. _urbs: https://github.com/tum-ens/urbs
.. _urbs.py: https://github.com/tum-ens/urbs/blob/master/urbs.py