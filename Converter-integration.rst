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

.. code-block:: python
    :emphasize-lines: 7,8,9,13
    def __init__(self, controller):
        wx.Frame.__init__(self, None, title="urbs gui 1.0")

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        omi = fileMenu.Append(wx.ID_OPEN, '&Load Config')
        # add import button to menu with name 'I'mport'M'enu'I'tem 
        # ID_ANY is used as there is no dedicated id for imports
        imi = fileMenu.Append(wx.ID_ANY, '&Import Excel')
        smi = fileMenu.Append(wx.ID_SAVE, '&Save Config')
        ...
        self.Bind(wx.EVT_MENU, self.OnOpen, omi)
        self.Bind(wx.EVT_MENU, self.OnImport, imi)
        self.Bind(wx.EVT_MENU, self.OnSave, smi)

.. code-block:: python
    def OnImport(self, event):
    # create import dialog where one can select multiple files
    # filepaths are returned as list
        openFileDialog = wx.FileDialog(self, "Import", "./samples", "",
                                       "urbs files (*.xlsx)|*.xlsx",
                                        wx.FD_MULTIPLE | wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        fn = openFileDialog.GetPaths()
        if fn:
            s = wx.MessageBox('Are you sure? All non saved data will be lost!',
                              'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if s == wx.OK:
                pub.sendMessage(EVENTS.IMPORT_CONFIG, filename=fn)

Events.py
---------
An event was created to use a new function in Controller.py

.. code-block:: python
    :emphasize-lines: 13
    class EVENTS():
        ...
        ITEM_DOUBLE_CLICK = "ITEM_DOUBLE_CLICK_"
        ITEM_MOVED = "ITEM_MOVED_"
        ITEM_COPY = "ITEM_COPY_"
        ITEM_COPIED = "ITEM_COPIED_"
        ITEM_DELETE = "ITEM_DELETE_"
        ITEM_DELETED = "ITEM_DELETED_"
        ITEM_CLONE = "ITEM_CLONE_"
        TRNSM_ITEM_MOVED = "TRNSM_ITEM_MOVED_"
        SAVE_CONFIG = "SAVE_CONFIG_"
        LOAD_CONFIG = "LOAD_CONFIG_"
        IMPORT_CONFIG = "IMPORT_CONFIG_"

Controller.py
-------------

Two modules were additionally imported:
* savetojson.py script to call conversion function
* os to be able to modify filepath strings more conveniently

.. code-block:: python
    #import converter script from same folder urbs/gui for now
    import savetojson
    import os

.. code-block:: python
    :emphasize-lines: 4
    class Controller():
        def __init__(self):
            ...
            pub.subscribe(self.OnImportConfig, EVENTS.IMPORT_CONFIG)

OnImportConfig()
----------------

The function receives a list of filenames and checks whether multiple files where selected.
If a single file was selected the file extension is replaced by '.json'.
For multiple files the filenames of every filepath except the first are extracted and they are concatenated to the first filepath with an underscore.

Then the path of the new savefile and the list of filepaths is given over to the converter script, calling *convert_to_json()*.
Afterwards a message is sent to the bus to invoke OnLoadConfig with the path of the new savefile.

.. code-block:: python
    def OnImportConfig(self, filename):
        # Import function calls converter script with a list of filepaths
        # and the first path in the list as output filename
        # onLoadConfig loads the converted file and updates the gui
        if len(filename) > 1:
            stems = [os.path.basename(os.path.splitext(path)[0]) for path in filename[1:]]
            stems.insert(0,os.path.splitext(filename[0])[0])
            #stems.append('.json')
            savename = '_'.join(stems) + '.json'
        else:
            savename = os.path.splitext(filename[0])[0] + '.json'
        savetojson.convert_to_json(filename, json_filename = savename)
        pub.sendMessage(EVENTS.LOAD_CONFIG, filename = savename)

savetojson.py
-------------

Some changes where made to better implement the script as a module.

As multiple files can be selected upon import the filename variable now contains a list.
This means packaging the filepath into a list is no longer necessary
but the functionality is still kept for standalone use.
This also allows the user to select multiple files directly so they do not depend on the Input-folder mechanism.

.. code-block:: python
    :emphasize-lines: 4,5,6
    if input_files == 'Input':
        glob_input = os.path.join("..", input_files, '*.xlsx')
        input_files = sorted(glob.glob(glob_input))
    # removed packaging of filepath into list 
    # so that multiple filepaths can be selected in gui which are already stored in a list
    elif isinstance(input_files, str):
        input_files = [input_files]

The detection of file extensions to add '.json' if necessary was improved to use os.path.splitext instead of comparing the last five letters of the string.
As the os module is already in use in *savetojson.py* nothing extra needs to be imported.

.. code-block:: python
    :emphasize-lines: 2
    # make sure that json_filename is valid
    if os.path.splitext(json_filename)[1] != '.json': 
    #if json_filename[-5:] is not '.json':
        json_filename += '.json'
the main function was changed to only be activated if the script is called in standalone form.