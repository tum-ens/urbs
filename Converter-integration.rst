Converter integration
=====================

This file documents the integration of savetojson.py into the GUI of URBS.


Reasoning
---------
The GUI strictly uses single json-type files as input to URBS

whereas the standard method of input for the commandline version is one or multiple Excel files.

Excel files are arguably easier to edit than json files and most datasets only exist in Excel files.
Therefore a converter script was created to combine GUI and Excel files.

To facilitate use of the script it is as of now integrated into the GUI.

How to use
----------

To use the script the user selects *file* from the ribbon menu then selects *import Excel*.
A file selection menu pops up and the user can select multiple files.
If only a single file is selected a json file with identical name is created in the same directory.
If multiple files are selected a json file with all filenames concatenated is created in the same directory.
Any existing json file with a name fitting the naming convention will be overwritten.
For repeated use the user can use the created json file instead.

The user can use intertemporal inputs by selecting any subset of excel files.
This allows incomplete or oversized selections.

modifications made
==================
All modifications where made in a way that keeps the MVC pattern intact.

Mainview.py
-----------
An entry similar to *load config* was created with differences being:
* multiple files can be selected, returned filepaths are stored in a list, even single ones
* labeling was adapted to match task
* called event was changed to use new function in Controller.py

#Insert code#

Events.py
---------
An event was created to use a new function in Controller.py

#Insert code#

Controller.py
-------------

Two modules were additionally imported:
* savetojson.py script to call conversion function
* os to be able to modify filepath strings more conveniently

#Insert code#

OnImportConfig()
----------------

The function receives a list of filenames and checks whether multiple files where selected.
If a single file was selected the file extension is replaced by '.json'.
For multiple files the filenames of every filepath except the first are extracted and they are concatenated to the first filepath with an underscore.

Then the path of the new savefile and the list of filepaths is given over to the converter script, calling *convert_to_json()*.
Afterwards a message is sent to the bus to invoke OnLoadConfig with the path of the new savefile.

#Insert code#

savetojson.py
-------------

Some changes where made to better implement the script as a module.

As multiple files can be selected upon import the filename variable now contains a list.
This means packaging the filepath into a list is no longer necessary
but the functionality is still kept for standalone use.
This also allows the user to select multiple files directly so they do not depend on the Input-folder mechanism.

#Insert code#

The detection of file extensions to add '.json' if necessary was improved to use os.path.splitext instead of comparing the last five letters of the string.
As the os module is already in use in *savetojson.py* nothing extra needs to be imported.

#Insert code#

the main function was changed to only be activated if the script is called in standalone form.