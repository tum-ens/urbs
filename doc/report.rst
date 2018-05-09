.. currentmodule:: urbs

.. _report-function:

Reporting function explained
============================

This page is a "code walkthrough" through the function :func:`report`. It shows
more technical details than the :ref:`tutorial` or :ref:`workflow` pages, to
facilitate writing one's own analysis scripts that directly retrieve variables
from the optimisation:

Report
------

So let's start by first printing the function as a whole:

.. literalinclude:: ../urbs/report.py
   :pyobject: report
   
After the function header and the docstring briefly explaining its use, another
function, :func:`get_constants`, is called. Before really diving into the
report function, first one of the two :ref:`medium-level-functions` functions
is presented.
   
Get constants
-------------

.. literalinclude:: ../urbs/output.py
   :pyobject: get_constants

Taking only one argument, this function retrieves all time-independent
quantities from the given optimisation problem object and returns them as a
:func:`tuple` of :class:`~pandas.DataFrame`. The low-level access functions
:func:`get_entity` and :func:`get_entities` are beyond the scope of this walk
through. They both yield "raw" :class:`~pandas.DataFrame` objects with only
minor pre-processing of index names.

The second paragraph deals with the emission timeseries ``co2`` by calculating
its sum over time. The :meth:`~pandas.DataFrame.unstack` method allows to move
the time dimension (index level ``0`` or the first) into the column direction. 
To sum over time, method :meth:`~pandas.DataFrame.sum` is called with its
``axis`` argument set to columns (``1``). This yields a DataFrame indexed over 
the tuple *(site, process, input commodity, output commodity)* and the
summed emissions as value.

Get timeseries
--------------

.. literalinclude:: ../urbs/output.py
   :pyobject: get_timeseries

With the arguments ``instance``, ``com`` and ``sit`` the function :func:
`get_timeseries` returns :class:`~pandas.DataFrames` of all timeseries that
are referring to the given commodity and site.
This includes the derivative for ``created`` and ``consumed``, which is
calculated and standardized by the power capacity at the end of the function.
   
Write to Excel
--------------

.. literalinclude:: ../urbs/report.py
   :start-after:     # create spreadsheet writer object 
   :end-before:        # write constants to spreadsheet

The :ref:`ExcelWriter <pandas:io.excel>` class creates a writer object, which
is then used by the :meth:`~pandas.DataFrame.to_excel` method calls to
aggregate all outputs into a single spreadsheet.

.. note:: :meth:`~pandas.DataFrame.to_excel` can also be called with a
   filename. However, this overwrites an existing file completely, thus
   deleting existing sheets. For quickly saving a :class:`~pandas.DataFrame`, 
   to a spreadsheet, a simple ``df.to_excel('df.xlsx', 'df')`` is sufficient.  

Constants
^^^^^^^^^

.. literalinclude:: ../urbs/report.py
   :start-after:        # write constants to spreadsheet
   :end-before:        # initialize timeseries tableaus

As written already, the individual :class:`~pandas.DataFrame` objects are
written to individual sheets within the same spreadsheet file by using the
writer object as a target. ``co2`` is an exception, as it starts as a
:class:`~pandas.Series`. It must be first converted to a DataFrame by calling
:meth:`~pandas.Series.to_frame`.


Timeseries
^^^^^^^^^^
.. literalinclude:: ../urbs/report.py
   :start-after:        # initialize timeseries tableaus
   :end-before:        # collect timeseries data

Initialize an empty :func:`list` and an empty :func:`dict` for collecting the
timeseries data. These are two builtin Python data structures. ``energies``
will become a list of :class:`~pandas.DataFrame` objects before getting
stitched together, while ``timeseries`` becomes a dictionary of
:class:`~pandas.DataFrame` objects, with a tuple ``(commodity, site)`` as key.
   
.. literalinclude:: ../urbs/report.py
   :start-after:        # collect timeseries data
   :end-before:         # write timeseries data (if any)
   
Module function :func:`get_timeseries` is similar to :func:`get_constants`,
just for time-dependent quantities. For a given commodity and site, this
function returns all DataFrames needed to create a balance plot.

Only overproduction is calculated in place. While it should not happen for
scenarios close to today's situation, future scenarios with much excess
renewable infeed, overproduction could happen for significant duration and
amount.

Using the function :func:`pandas.concat`, multiple DataFrames are glued
together next to each other (``axis=1``), while creating a nested column index
wih custom labels (``keys=...``) for each of the list argument (``[...]``). The
resulting timeseries tableau is copied to the corresponding place in the
``timeseries`` dictionary.

For the *Energy sums* sheet, all timeseries DataFrames are summed along the
time axis, resulting in a Series for each timeseries. These are
then glued together on top of each other (``axis=0``) with a nested row index
with custom labels (``keys=...``) for each series type. Finally the Series is
converted back to a DataFrame, using ``Commodity.Site`` as the column title
template.

.. literalinclude:: ../urbs/report.py
   :start-after:        # write timeseries data (if any)

Finally, the *Energy sums* table is assembled by stitching together the
individual energy sums per commodity and site and filling missing values with
:meth:`~pandas.DataFrame.fillna`.

Finally, the *timeseries* tables are saved without change to individual sheets.