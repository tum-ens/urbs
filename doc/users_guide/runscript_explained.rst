.. currentmodule:: urbs

.. _tutorial:

runscript explained
===================

The runscript can be subdivided into several parts. These will be discussed
here in detail.

Imports
-------
The script starts with importing the relevant python libraries as well as the
module ``urbs``.

::

    import os
    import shutil
    import urbs

The included packages have the following functions:

* `os`_ and `shutil`_ are builtin Python modules, included here for their data
  path and copying operations. 
  
* `urbs`_ is the directory which includes the modules, whose functions are used
  mainly in this script. These are :func:`prepare_result_directory`,
  :func:`setup_solver` and :func:`run_scenario`.
  
More functions can be found in the document :ref:`API`.
 
In the following sections the user defined input, output and scenario settings
are described.

Input Settings
--------------
The script starts with the specification of the input files, which is either a
single .xlsx file located in the same folder as the runscript or a collection
of .xlsx files located in the subfolder ``Input``::

    input_files = 'Input'
    result_name = 'Mimo-ex'
    result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp

    # copy input file to result directory
    try:
        shutil.copytree(input_files, os.path.join(result_dir, 'Input'))
    except NotADirectoryError:
        shutil.copyfile(input_files, os.path.join(result_dir, input_files))
    # copy runme.py to result directory
    shutil.copy(__file__, result_dir)

The input file/folder and the runscript are automatically copied into the
result folder.

Next variables specifying the desired solver and objective function are set::

    # choose solver (cplex, glpk, gurobi, ...)
    solver = 'glpk'

    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective

The solver has to be licensed for the specific user, where the open source
solver "glpk" is used as the standard. For the objective function urbs
currently allows for two options: "cost" and "CO2" (case sensitive). In the
former case the total system cost and in the latter case the total
CO2-emissions are minimized.

The model parameters are finalized with a specification of timestep length and
modeled time horizon::

    # simulation timesteps
    (offset, length) = (3500, 168)  # time step selection
    timesteps = range(offset, offset+length+1)
    dt = 1  # length of each time step (unit: hours)

The variable ``timesteps`` is the list of timesteps to be simulated. Its
members must be a subset of the labels used in ``input_file``'s sheets "Demand"
and "SupIm". It is one of the function arguments to :func:`create_model` and
accessible directly, so that one can quickly reduce the problem size by
reducing the simulation ``length``, i.e. the number of timesteps to be
optimised. Variable ``dt`` is the duration of each timestep in the list in
hours, where any positiv real value is allowed. 

:func:`range` is used to create a list of consecutive integers. The argument
``+1`` is needed, because ``range(a,b)`` only includes integers from ``a`` to
``b-1``:: 
    
    >>> range(1,11)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

Output Settings
---------------
The desired output is also specified by the user in the runscript. It is split
into two parts: reporting and plotting. The former is used to generate an excel
output file and the latter for standard graphs.
 
Reporting
^^^^^^^^^
urbs by default generates an .xlsx-file as an ouput in result_dir. This file
includes all commodities of interest to the user and can be specified as report
tuples each consisting of a given ``year``, ``sites`` and
``commodities`` combination. Information about these commodities is  summarized
both in sum (in sheet "Energy sums") and as individual timeseries
(in sheet "... timeseries").
::
    
    # detailed reporting commodity/sites
    report_tuples = [
        (2019, 'North', 'Elec'),
        (2019, 'Mid', 'Elec'),
        (2019, 'South', 'Elec'),
        (2019, ['North', 'Mid', 'South'], 'Elec'),
        (2024, 'North', 'Elec'),
        (2024, 'Mid', 'Elec'),
        (2024, 'South', 'Elec'),
        (2024, ['North', 'Mid', 'South'], 'Elec'),
        (2029, 'North', 'Elec'),
        (2029, 'Mid', 'Elec'),
        (2029, 'South', 'Elec'),
        (2029, ['North', 'Mid', 'South'], 'Elec'),
        (2034, 'North', 'Elec'),
        (2034, 'Mid', 'Elec'),
        (2034, 'South', 'Elec'),
        (2034, ['North', 'Mid', 'South'], 'Elec'),    
        ]

# optional: define names for sites in report_tuples
report_sites_name = {('North', 'Mid', 'South'): 'All'}

Optionally it is possible to define clusters of sites for aggregated
information and with ``report_sites_name`` it is then possible to name these.
If they are empty, the default value will be taken.
   
Plotting
^^^^^^^^
urbs generates default result images. Which images exactly are desired can be
set by the user. via the following input lines:
::
    
    # plotting commodities/sites
    plot_tuples = [
        (2019, 'North', 'Elec'),
        (2019, 'Mid', 'Elec'),
        (2019, 'South', 'Elec'),
        (2019, ['North', 'Mid', 'South'], 'Elec'),
        (2024, 'North', 'Elec'),
        (2024, 'Mid', 'Elec'),
        (2024, 'South', 'Elec'),
        (2024, ['North', 'Mid', 'South'], 'Elec'),
        (2029, 'North', 'Elec'),
        (2029, 'Mid', 'Elec'),
        (2029, 'South', 'Elec'),
        (2029, ['North', 'Mid', 'South'], 'Elec'),
        (2034, 'North', 'Elec'),
        (2034, 'Mid', 'Elec'),
        (2034, 'South', 'Elec'),
        (2034, ['North', 'Mid', 'South'], 'Elec'),    
        ]

    # optional: define names for sites in plot_tuples
    plot_sites_name = {('North', 'Mid', 'South'): 'All'}

    # plotting timesteps
    plot_periods = {
        'all': timesteps[1:]
        }

The logic is similar to the reporting case discussed above. With the setting of
plotting timesteps the exact range of the plotted result can be set. In the
default case shown this range is all modeled timesteps. For larger optimization
timestep ranges this can be impractical and instead the following syntax can be
used to hard code which steps are to be plotted exactly.

::

    # plotting timesteps
    plot_periods = {
        'win': range(1000:1168),
        'sum': range(5000:5168)
        }

In this example two 1 week long ranges are plotted between the specified time
steps. Using this make sure, that the chosen ranges are subsets of the modeled
time steps themselves.

The plot colors can be customized using the module constant :data:`COLORS`. All
plot colors are user-definable by adding color :func:`tuple` ``(r, g, b)`` or
modifying existing tuples for commodities and plot decoration elements. Here,
new colors for displaying import/export are added. Without these, pseudo-random
colors are generated in :func:`to_color`.
::

    # create timeseries plot for each demand (site, commodity) timeseries
    for sit, com in prob.demand.columns:

Scenarios
---------
This section deals with the definition of different scenarios. Starting from
the same base scenarios, defined by the data in ``input_file``, they serve as a
short way of defining the difference in input data. If needed, completely
separate input data files could be loaded as well.

The ``scenarios`` list in the end of the input file allows then to select the
scenarios to be actually run. ::

    scenarios = [
                 urbs.scenario_base,
                 urbs.scenario_stock_prices,
                 urbs.scenario_co2_limit,
                 urbs.scenario_co2_tax_mid,
                 urbs.scenario_no_dsm,
                 urbs.scenario_north_process_caps,
                 urbs.scenario_all_together
                ]

The following scenario functions are specified in the subfolder ``urbs`` in
script ``scenarios.py``. 

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
   
Run scenarios
-------------
This now finally is the function that gets everything going. It is invoked in
the very end of the runscript.
::

    for scenario in scenarios:
    prob = urbs.run_scenario(input_files, solver, timesteps, scenario, 
                        result_dir, dt, objective, 
                        plot_tuples=plot_tuples,
                        plot_sites_name=plot_sites_name,
                        plot_periods=plot_periods,
                        report_tuples=report_tuples,
                        report_sites_name=report_sites_name)

Having prepared settings, input data and scenarios, the actual computations
happen in the function :func:`run_scenario` of the script ``runfunctions.py``
in subfolder ``urbs``. It is executed for each of the scenarios included in the
scenario list. The following sections describe the content of function
:func:`run_scenario`. In a nutshell, it reads the input data from its argument
``input_file``, modifies it with the supplied ``scenario``, runs the
optimisation for the given ``timesteps`` and writes report and plots to
``result_dir``.

Reading input
^^^^^^^^^^^^^
::

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = read_input(input_files,year)
    data = scenario(data)
    validate_input(data)

Function :func:`read_input` returns a dict ``data`` of up to 12 pandas
DataFrames with hard-coded column names that correspond to the parameters of
the optimization problem (like ``eff`` for efficiency or ``inv-cost-c`` for
capacity investment costs). The row labels on the other hand may be freely
chosen (like site names, process identifiers or commodity names). By
convention, it must contain the six keys ``commodity``, ``process``,
``storage``, ``transmission``, ``demand``, and ``supim``. Each value must be a
:class:`pandas.DataFrame`, whose index (row labels) and columns (column labels)
conforms to the specification given by the example dataset in the spreadsheet
:file:`mimo-example.xlsx`.

``data`` is then modified by applying the :func:`scenario` function to it. To
then rule out a list of known errors, that accumulate through growing user
experience, a variety of validation functions specified in script
``validate.py`` in subfolder ``urbs`` is run on the dict ``data``.

Solving
^^^^^^^

::

    # create model
    prob = urbs.create_model(data, dt, timesteps)

    # refresh time stamp string and create filename for logfile
    now = prob.created
    log_filename = os.path.join(result_dir, '{}.log').format(sce)

    # solve model and read results
    optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(prob, tee=True)

This section is the "work horse", where most computation and time is spent. The
optimization problem is first defined (:func:`create_model`) and populated
with parameter values with values. The ``SolverFactory`` object is an abstract
representation of the solver used. The returned object ``optim`` has a method
:meth:`set_options` to set solver options (not used in this tutorial).

The remaining line calls the solver and reads the ``result`` object back
into the ``prob`` object, which is queried to for variable values in the
remaining script file. Argument ``tee=True`` enables the realtime console
output for the solver. If you want less verbose output, simply set it to
``False`` or remove it.
   

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
.. _pyomo: http://www.pyomo.org/
.. _pyomo.opt.base:
    https://pyomo.readthedocs.io/en/latest/_modules/pyomo/opt/base/solvers.html
.. _shutil: https://docs.python.org/2/library/shutil.html
.. _urbs: https://github.com/tum-ens/urbs
.. _urbs.py: https://github.com/tum-ens/urbs/blob/master/urbs.py
