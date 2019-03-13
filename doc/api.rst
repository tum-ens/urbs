.. module:: urbs

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
the structure of the problem to be built. This is done via the functions:

.. function:: identify_mode(data)

which identifies the mode to be run and

.. function:: identify_expansion(const_unit_df, inst_cap_df)

which identifies whether there are any expansions possible for the different
types of model entities. Both functions create boolean, global variables that
are then used by the 'urbs' to choose the right model constraints for the
mathematical model. It thus decides which scripts and functions from subfolder
'features' are to be used. 

input.py
~~~~~~~~
This file handles the input and prepares the mathematical model itself. The
function

.. function:: read_input(input_files, year)

converts the input files into the dictionary 'data', which is the reference
library of input data used throughout the model generation. The function

.. function:: pyomo_model_prep(data, timesteps)

is then used to manipulate the input data into forms directly usable for the
model. For this task it makes heavy uses of other helper functions described
below.

model.py
~~~~~~~~
This file just includes the central function used for model generation

.. function:: create_model(data, dt=1, timesteps=None, objective='cost', dual=True)

It takes the inputs and generates a Pyomo ConcreteModel instance. This is the
goal of the entire module and it thus makes use of all the other functions in
the module.

plot.py
~~~~~~~
This script generates automated output pictures using the function

.. function:: plot(prob, stf, com, sit, dt, timesteps, timesteps_plot,
         power_name='Power', energy_name='Energy',
         power_unit='MW', energy_unit='MWh', time_unit='h',
         figure_size=(16, 12))

The plots and what is to be plotted can be manipulated in the runscript.

report.py
~~~~~~~~~
This script handles the automated generation of an excel data sheet from the
solved model instance via the function:

.. function:: report(instance, filename, report_tuples=None, report_sites_name={})

It takes the model instance and uses lower level functions from 'output.py'.

runfunctions.py
~~~~~~~~~~~~~~~
This file contains the central function for running a predefined set of inputs
or a scenario thereof

.. function:: run_scenario(input_files, Solver, timesteps, scenario, result_dir, dt,
                 objective, plot_tuples=None,  plot_sites_name=None,
                 plot_periods=None, report_tuples=None,
                 report_sites_name=None)

It takes care of all the data stream from an input file to an output.

saveload.py
~~~~~~~~~~~
This file contains two functions to save and load a collection of inputs and
the corresponding outputs of a model instance

.. function:: save(prob, filename)

and

.. function:: load(filename)

The data format is .hdf5 and allows the access to all variable and dual
variable values of the solution as well as the input parameters of the model
instance.

scenarios.py
~~~~~~~~~~~~
In this script scenario functions are defined. These are used to automatically
change the inputs as given in dictionary 'data'. In this way multiple runs of
similar model instances can be automated.

validation.py
~~~~~~~~~~~~~
makes sure that the input given is not leading to an infeasible or non-sensical
model. It generates error messages for certain known errors. It is a
organically growing script. 