.. module:: urbs

Get started
===========
Welcome to urbs! Here you can learn how to use the program and what to do to
create your own optimization problems and run them.

Inputs
^^^^^^
There are two different types of inputs the user has to make in order to set up
and solve an optimization problem with urbs.

First, there are the model paramters themselves, i.e. the parameters specifying
the behavior of the different model entities such as commodities or processes.
These paramters are entered into spreadsheets with a standardized structure.
These then have to be placed in the subfolder ``Input``. There can be no
further information given on those parameters here since they make up the
particular energy system models. There are, however, two examples provided with
the code, which are explained elsewhere in this documentation.

Second, there are the settings of the modeling run such as the modeling horizon
or the solver to be employed. These settings are made in a run script. For the
standard example such scripts are given named runme.py for the example
``mimo-example`` and runBP.py for the example ``Business park``. To run a
modeling run you then simply execute the according run script by typing::

    $ python3 runscript.py

in the command prompt.

You can immediately test this after the installation by running one of the two
standard examples using the corresponding example run sctipts.