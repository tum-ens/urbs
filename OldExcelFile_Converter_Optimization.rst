Optimization of Converter for old Excel files
=============================================

This file documents the modification of savetojson.py to allow usage of old Excel files.
This mostly consists of checking the file for problematic content and issuing a fitting warning.
Warnings inform the user and provide a guideline on how to make the file compliant to expected standards.
An automatic solution for fixing the files is out of the scope of this task and would be difficult to accomplish without deeper knowledge.

Reasoning
---------
The GUI can import Excel files and convert them automatically but some files do not follow the expected structure perfectly.


Source information
------------------
Most notably some files include information on the source of the data provided.
This works by adding an additional row and column to each sheet both titled 'Source' and writing a combination of a single letter and digit respectively.
In an additional sheet every combination of letter and digit is matched to a source of information.

.. image:: img_OldExcelFile_Converter_Optimization\Excel_Source.png
  :width: 60%
  :align: center

The problem was that the converter would go through the sheets row by row or column by column and always find the Source information.
Sometimes a cell is empty when no source info is given or the converter expects float numbers instead of letters and the conversion can not be completed.

Solution
--------
There where three iterations for the solution.

At first *try/except* statements where used as this is a recommended way of catching unexpected behaviour in python.
They were implemented in every function reading from the Excel file.
These worked well at first and the files could be further processed than before.
But especially when used on library modules errors can be hidden from the user who then can not fix the file manually.
Additionally whenever a set of values was copied and one of the readings raised an error every spot after that would be empty.
This made calculations and advanced arrangements impossible and moved errors from their origin further down.

.. code:: python

    try:
        new_comm[current_year] = {
            "timeSer": "",
            "price": float(comm_df.T.loc["price"][items]),
            "max": float(comm_df.T.loc["max"][items]),
            "maxperhour": float(comm_df.T.loc["maxperhour"][items]),
            "Action": "...",
            "delay": 0.0,
            "eff": 0.0,
            "plot": False,
            "report": False,
            "recov": 0.0,
            "cap-max-do": 0.0,
            "cap-max-up": 0.0
        }
    except KeyError:
        print("In Commodity, entry is not 'maxperhour' (possibly is 'maxperstep'). please correct this manually")

A lot of time went into debugging those cascading errors until their source was found.
Every try/except statement was changed to an *if/else* statement searching in a pandas dataframe for a hint on the error inducing statements.
The fitting statements were varyingly dificult to find and definitely error prone.
The overall performance of the converter decreased as well as if/else statements are considerably inefficient when compared to the try path of a try/except statements.

In the third and current iteration an *if* statement is still used but instead of testing in every single function a test is used on the input right after loading the file.

.. code:: python

    for xls in sheet_list:
        if "Source" in xls.parse().values:
            raise UserWarning("Some cells in " + sheet + " contain 'Source'. All columns and rows containing source information and the source sheet should be removed manually.")

Normally the list of excel sheets is only parsed selectively in each function.
Therefore a collective parsing of all sheets has to be done beforehand and a simple if statement tests for the occurence of 'Source'.
If it evaluates to true a *UserWarning* is raised to imply that it is an active choice of the program to terminate.
Further the user is informed that they should remove the rows and columns containing 'Source'.

This is a simple solution that doesn't adhere too closely to single error calls and gives clear advice.
On the downside it relies on the fact that those lines are marked with 'Source' making it vulnerable in this regard,
but as the tested files had about 20 mentions of this word it is unrealistic to find a file where only the cell 'Source' was removed but not the rest of the content.

Another problem is that this can probably not be the basis for automated correction in the future as it seems difficult to extract the matching rows in the parsed xls.


maxperhour
----------
In the commodity sheet sometimes one of the columns isn't correctly labeled 'maxperhour' but rather 'maxperstep'.
This breaks the converter as it expects 'maxperhour' and writes it into a element maxperhour.
It is not clear whether the GUI can handle a variable other than maxperhour so the decision of renaming it is transferred to the user with a UserWarning.

.. code:: python

    for comm_id in comm_dict:
        # go through every existing commodity; if the current commodity is found: add the
        # information, then break out of the for loop
        if "maxperhour" in comm_df.columns:
            if comm_dict[str(comm_id)]["Name"] == str(items):
                ...
        else:
            raise UserWarning("No 'maxperhour' in Commodity! (possibly old file with 'maxperstep')")

.item() vs float()
------------------
Many transformations in different functions were ending with *.item()* which created problems with some files but worked fine on others.
As no documentation of the .item() function was found in python most were replaced by wrapping the statements in *float()* except where necessary for some reason.

.. code:: python

    #process_dict[current_storage]["Years"][current_year]["lifetime"] = storage_df.loc[storage_types]["lifetime"].item()
    process_dict[current_storage]["Years"][current_year]["lifetime"] = float(storage_df.loc[storage_types]["lifetime"])

Error print modification
------------------------
As the amount of error prints in the style of "No 'TimeVarEff' sheet" was enormous a new way of displaying non-breaking errors was created.
It is a list object *error_list* created directly after the imports which is printed in an orderly manner after the conversion.

.. code:: python

    import os
    import glob
    from datetime import date
    import time

    # create global error list to print all errors related to excel in the end
    error_list = ["The following warnings related to conversion of the Excel file occured:"]

The list is preloaded with a sentence as only non-empty lists can be appended to.
For now this list is for non breaking errors only so it is printed after the conversion is finished.

.. code:: python

    # create json file
    json_file = json.dumps(data_dict, indent=2)
    f = open(json_filename, 'w')
    f.write(json_file)
    f.close()

    # print list of errors related to formatting of excel but only print every errror once
    if len(error_list) > 1:
        print("\n".join(list(dict.fromkeys(error_list))))
        print("\n The excel file was probably converted correctly, but please compare for yourself \n \n")

    else:
        print("No known errors related to connversion of the excel file occured")

This code checks whether error messages where appended and then prints all unique entries in the list.
Uniqueness is created by converting the list to a dict and back to a list as dicts can only hold unique elements.

.. code:: python

    def read_year_and_budget(input_list, year):
        ...
        # read the 'Global' files in all the input sheets
        for xls in input_list:
            if 'Global' in xls.sheet_names:
            ...
            else:
                error_list.append("No global sheet in the input sheet!")

Because the list is an object its functions including *.append()* can be called anywhere in the module.

ToDo
----
A critical error is reported in the module that saves the dataframe to json for those files that should now be functional.
It is reported that a Series is not JSON convertable, which should not happen as no Pandas Series should be left in the dataframe.
Upon further examination it seems to be connected to the rows in the 'Process-Commodity' sheet that contain "Curtailment" as the files are correctly converted when this line is removed.
Furthermore in debugging tools those rows are the content of the variable used.
