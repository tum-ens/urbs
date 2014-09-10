API
===

.. currentmodule:: urbs

This page contains the extracted `urbs.py` module and function docstrings. The
first section contains a brief model overview. Members shows the annotated 
docstrings of all member functions, grouped by topic.

Module
------

.. automodule:: urbs

Usage
-----

The following is a minimum "hello world" script that shows the life cycle of 
the optimization object `prob`, and how the various `urbs` module functions 
create it, modify it and process it.::

    import urbs
    from coopr.opt.base import SolverFactory
    
    data = urbs.read_excel('data-example.xlsx')
    model = urbs.create_model(data)
    prob = model.create()
    
    optim = SolverFactory('glpk')
    result = optim.solve(prob)
    prob.load(result)

    urbs.report(prob, 'report.xlsx')
    urbs.plot(prob, 'Elec', 'Mid')

Members
-------


Optimisation model
^^^^^^^^^^^^^^^^^^
.. autofunction:: create_model


Report & plotting
^^^^^^^^^^^^^^^^^
.. autofunction:: plot
.. autofunction:: report


Retrieve results
^^^^^^^^^^^^^^^^
.. autofunction:: get_constants
.. autofunction:: get_timeseries


Low-level access
^^^^^^^^^^^^^^^^
.. autofunction:: list_entities
.. autofunction:: get_entity
.. autofunction:: get_entities


Helper functions
^^^^^^^^^^^^^^^^
.. autofunction:: annuity_factor
.. autofunction:: commodity_balance
.. autofunction:: split_columns
.. autofunction:: to_color
