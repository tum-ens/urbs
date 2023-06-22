'urbs' module description
=========================
This part gives a brief overview over the architecture of the program.
The data flow in an urbs model is visualized in the following graph:

.. image:: /implementdoc/img/Dataflow.png
    :width: 100%
    :align: center

'urbs' uses a modular structure to build and execute the optimization and to
automatically generate the results. All scripts are placed in the folder
'urbs'. In subfolder 'features' constraint expressions for the mathematical
model are defined. These will not be discussed here and only the highest level
functions will be discussed. The scripts used for these are the following
(in alphabetical order):

identify.py
~~~~~~~~~~~
In this scripts the dictionary of input dataframes 'data' is parsed to conclude
the structure of the problem to be built.

.. automodule:: urbs.identify
    :members:

input.py
~~~~~~~~
This file handles the input and prepares the mathematical model itself.

.. automodule:: urbs.input
    :members:

model.py
~~~~~~~~
This file just includes the central function used for model generation.

.. automodule:: urbs.model
    :members:

output.py
~~~~~~~~~
This file contains lower level functions to retrieve data from a solved model
instance.

.. automodule:: urbs.output
    :members:

plot.py
~~~~~~~
This script generates automated output pictures using the function

.. automodule:: urbs.plot
    :members:

report.py
~~~~~~~~~
This script handles the automated generation of an excel data sheet from the
solved model instance.

.. automodule:: urbs.report
    :members:

runfunctions.py
~~~~~~~~~~~~~~~
This file contains the central function for running a predefined set of inputs
or a scenario thereof.

.. automodule:: urbs.runfunctions
    :members:

saveload.py
~~~~~~~~~~~
This file contains two functions to save and load a collection of inputs and
the corresponding outputs of a model instance.

.. automodule:: urbs.saveload
    :members:

scenarios.py
~~~~~~~~~~~~
In this script scenario functions are defined. These are used to automatically
change the inputs as given in dictionary 'data'. In this way multiple runs of
similar model instances can be automated.

validation.py
~~~~~~~~~~~~~
This file makes sure that the input given is not leading to an infeasible or
non-sensical model. It generates error messages for certain known errors. It is
a organically growing script.

.. automodule:: urbs.validation
    :members: