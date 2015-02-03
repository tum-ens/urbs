.. currentmodule:: urbs

.. _tutorial:

Tutorial
========

The README file contains `installation notes`__. This tutorial
expands on the steps that follow this installation.

.. __: https://github.com/tum-ens/urbs/blob/master/README.md#installation

This tutorial is a commented walk-through through the script ``runme.py``,
which is a demonstration user script that can serve as a good basis for one's 
own script.

Initialisation
--------------

Imports
^^^^^^^

::

    import coopr.environ
    import os
    import urbs
    from coopr.opt.base import SolverFactory
    from datetime import datetime
   
Several packages are included.

* `coopr.environ` is not used, but required for compatibility with future 
  releases of `coopr`_.

* `os`_ is a builtin Python module, included here for its `os.path`_ submodule
  that offers operating system independent path manipulation routines. The 
  following code creates the path string ``'result/foo'`` or ``'result\\foo'``
  (depending on the operating system),checks whether it exists and creates the
  folder(s) if needed. This is used to prepare a new directory for generated
  result file::
      
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
  
* `datetime` is used to append the current date and time to the result
  directory name (used in :func:`prepare_result_directory`)

Settings
^^^^^^^^

From here on, the script is best read from the back.::

    if __name__ == '__main__':
        input_file = 'mimo-example.xlsx'
        result_name = os.path.splitext(input_file)[0]  # cut away file extension
        result_dir = prepare_result_directory(result_name)  # name + time stamp
    
        (offset, length) = (4000, 5*24)  # time step selection
        timesteps = range(offset, offset+length+1)

Variable ``input_file`` defines the input spreadsheet, from which the
optimization problem will draw all its set/parameter data.
   
Variable ``timesteps`` is the list of timesteps to be simulated. Its members
must be a subset of the labels used in ``input_file``'s sheets "Demand" and
"SupIm". It is one of the two function arguments to :func:`create_model` and
accessible directly, because one can quickly reduce the problem size by
reducing the simulation ``length``, i.e. the number of timesteps to be
optimised. 

:func:`range` is used to create a list of consecutive integers. The argument
``+1`` is needed, because ``range(a,b)`` only includes integers from ``a`` to
``b-1``:: 
    
    >>> range(1,11)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

The following section deals with the definition of different scenarios.
Starting from the same base scenarios, defined by the data in ``input_file``,
they serve as a short way of defining the difference in input data. If needed,
completely separate input data files could be loaded as well.

In addition to defining scenarios, the ``scenarios`` list allows to select a
subset to be actually run.

Scenario functions
^^^^^^^^^^^^^^^^^^

A scenario is simply a function that takes the input ``data`` and modifies it
in a certain way. with the required argument ``data``, the input
data :class:`dict`.::
    
    # SCENARIOS
    def scenario_base(data):
        # do nothing
        return data
    
The simplest scenario does not change anything in the original input file. It
usually is called "base" scenario for that reason. All other scenarios are
defined by 1 or 2 distinct changes in parameter values, relative to this common
foundation.::
    
    def scenario_stock_prices(data):
        # change stock commodity prices
        co = data['commodity']
        stock_commodities_only = (co.index.get_level_values('Type') == 'Stock')
        co.loc[stock_commodities_only, 'price'] *= 1.5
        return data
    
For example, :func:`scenario_stock_prices` selects all stock commodities from
the :class:`DataFrame` ``commodity``, and increases their *price* value by 50%.
See also pandas documentation :ref:`Selection by label <pandas:indexing.label>`
for more information about the ``.loc`` function to access fields. Also note
the use of `Augmented assignment statements`_ (``*=``) to modify data 
in-place.::
    
    def scenario_co2_limit(data):
        # change global CO2 limit
        hacks = data['hacks']
        hacks.loc['Global CO2 limit', 'Value'] *= 0.05
        return data

Scenario :func:`scenario_co2_limit` shows the simple case of changing a single
input data value. In this case, a 95% CO2 reduction compared to the base
scenario must be accomplished. This drastically limits the amount of coal and
gas that may be used by all three sites.::
    
    def scenario_north_process_caps(data):
        # change maximum installable capacity
        pro = data['process']
        pro.loc[('North', 'Hydro plant'), 'cap-up'] *= 0.5
        pro.loc[('North', 'Biomass plant'), 'cap-up'] *= 0.25
        return data
    
Scenario :func:`scenario_north_process_caps` demonstrates accessing single
values in the ``process`` :class:`~pandas.DataFrame`. By reducing the amount of
renewable energy conversion processes (hydropower and biomass), this scenario
explores the "second best" option for this region to supply its demand.::
    
    def scenario_all_together(data):
        # combine all other scenarios
        data = scenario_stock_prices(data)
        data = scenario_co2_limit(data)
        data = scenario_north_process_caps(data)
        return data 

Scenario :func:`scenario_all_together` finally shows that scenarios can also be
combined by chaining other scenario functions, making them dependent. This way,
complex scenario trees can written with any single input change coded at a
single place and then building complex composite scenarios from those.

Scenario selection
^^^^^^^^^^^^^^^^^^
   
::
    
    # select scenarios to be run
    scenarios = [
        scenario_base,
        scenario_stock_prices,
        scenario_co2_limit,
        scenario_north_process_caps,
        scenario_all_together]
    scenarios = scenarios[:1]  # select by slicing 

In Python, functions are objects, so they can be put into data structures just
like any variable could be. In the following, the list ``scenarios`` is used to
control which scenarios are being actually computed. 
   
Run scenarios
-------------

::

    for scenario in scenarios:
        prob = run_scenario(input_file, timesteps, scenario, result_dir)

Having prepared settings, input data and scenarios, the actual computations
happen in the function :func:`run_scenario` of the script. It is executed 
``for`` each of the scenarios included in the scenario list. The following
sections describe the content of function :func:`run_scenario`. In a nutshell,
it reads the input data from its argument ``input_file``, modifies it with the
supplied ``scenario``, runs the optimisation for the given ``timesteps`` and
writes report and plots to ``result_dir``.

Reading input
^^^^^^^^^^^^^

::

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = urbs.read_excel(input_file)
    data = scenario(data)

Function :func:`read_excel` returns a dict ``data`` of six pandas DataFrames
with hard-coded column names that correspond to the parameters of the
optimization problem (like ``eff`` for efficiency or ``inv-cost-c`` for
capacity investment costs). The row labels on the other hand may be freely
chosen (like site names, process identifiers or commodity names). By
convention, it must contain the six keys ``commodity``, ``process``,
``storage``, ``transmission``, ``demand``, and ``supim``. Each value must be a
:class:`pandas.DataFrame`, whose index (row labels) and columns (column labels)
conforms to the specification given by the example dataset in the spreadsheet
:file:`mimo-example.xlsx`.

``data`` is then modified by applying the :func:`scenario` function to it.


Solving
^^^^^^^

::

    # create model, solve it, read results
    model = urbs.create_model(data, timesteps)
    prob = model.create()
    optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
    result = optim.solve(prob, tee=True)
    prob.load(result)

This section is the "work horse", where most computation and time is spent. The
optimization problem is first defined (:func:`create_model`), then filled with
values (``create``). The ``SolverFactory`` object is an abstract representation
of the solver used. The returned object ``optim`` has a method
:meth:`set_options` to set solver options (not used in this tutorial).

The remaining two lines call the solver and read the ``result`` object back
into the ``prob`` object, which is queried to for variable values in the
remaining script file. Argument ``tee=True`` enables the realtime console
output for the solver. If you want less verbose output, simply set it to
``False`` or remove it.
   
Reporting
^^^^^^^^^

::
    
    # write report to spreadsheet
    urbs.report(
        prob,
        os.path.join(result_dir, '{}-{}.xlsx').format(sce, now),
        ['Elec'], ['South', 'Mid', 'North'])
   
The :func:`urbs.report` function creates a spreadsheet from the main results.
Summaries of costs, emissions, capacities (process, transmissions, storage) are
saved to one sheet each. For timeseries, each combination of the given
``sites`` and ``commodities`` are summarised both in sum (in sheet "Energy
sums") and as individual timeseries (in sheet "... timeseries"). See also
:ref:`report-function` for a detailed explanation of this function's implementation.
   
Plotting
^^^^^^^^

::
    
    # add or change plot colors
    my_colors = {
        'South': (230, 200, 200),
        'Mid': (200, 230, 200),
        'North': (200, 200, 230)}
    for country, color in my_colors.iteritems():
        urbs.COLORS[country] = color
   
First, the use of the module constant :data:`COLORS` for customising plot
colors is demonstrated. All plot colors are user-defineable by adding color 
:func:`tuple` ``(r, g, b)`` or modifying existing tuples for commodities and 
plot decoration elements. Here, new colors for displaying import/export are
added. Without these, pseudo-random colors are generated in 
:func:`to_color`.::

    # create timeseries plot for each demand (site, commodity) timeseries
    for sit, com in prob.demand.columns:
        # create figure
        fig = urbs.plot(prob, com, sit)
        
        # change the figure title
        ax0 = fig.get_axes()[0]
        nice_sce_name = sce.replace('_', ' ').title()
        new_figure_title = ax0.get_title().replace(
            'Energy balance of ', '{}: '.format(nice_sce_name))
        ax0.set_title(new_figure_title)
        
        # save plot to files 
        for ext in ['png', 'pdf']:
            fig_filename = os.path.join(
                result_dir, '{}-{}-{}-{}.{}').format(sce, com, sit, now, ext)
            fig.savefig(fig_filename, bbox_inches='tight')
   
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
   raster output for use with printing, in case the preferable vector images
   cannot be used. The filename extension or the optional ``format`` argument
   can be used to set the output format. Available formats depend on the used
   `plotting backend`_. Most backends support png, pdf, ps, eps and svg.
   
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
.. _urbs: https://github.com/tum-ens/urbs
.. _urbs.py: https://github.com/tum-ens/urbs/blob/master/urbs.py