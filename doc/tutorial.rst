.. currentmodule:: urbs

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
dataset ``data-example.xlsx``.

Scenario selection
^^^^^^^^^^^^^^^^^^
   
.. literalinclude:: ../runme.py
   :start-after: # select scenarios
   :end-before: # MAIN
   
   
Main loop
---------

Solving
^^^^^^^

.. literalinclude:: ../runme.py
   :start-after: # MAIN
   :end-before: # write report

Reporting
^^^^^^^^^


.. literalinclude:: ../runme.py
   :start-after:     # write report
   :end-before:     # add or change plot colours
   

Plotting
^^^^^^^^

.. literalinclude:: ../runme.py
   :start-after:     # add or change plot colours

.. _coopr: https://software.sandia.gov/trac/coopr
.. _coopr.opt.base: https://projects.coin-or.org/Coopr/browser/coopr.opt/trunk/coopr/opt/base
.. _os: https://docs.python.org/2/library/os.html
.. _os.path: https://docs.python.org/2/library/os.path.html
.. _pandas: https://pandas.pydata.org
.. _pyomo: https://software.sandia.gov/trac/coopr/wiki/Pyomo
.. _urbs: https://github.com/tum-ens/urbs
.. _urbs.py: https://github.com/tum-ens/urbs/blob/master/urbs.py