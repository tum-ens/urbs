# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import os
import webbrowser
import GeneralView as gv
import RESView as res
import TransmissionView as tv

from pubsub import pub
from Events import EVENTS


class MainView (wx.Frame):
    """The MainView module is our application frame or main window. It consists
    of 3 major views:
        - Overview Tab. This is the GeneralView module.
        - Transmission Tab. This is the TransmissionView module.
        - A tab for modeling the energy system for each site. This is the
          RESView module.
    """

    def __init__(self, controller):
        """The constructor
            """
        wx.Frame.__init__(self, None, title="urbs gui 1.0")

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        omi = fileMenu.Append(wx.ID_OPEN, '&Load Config')
        # add import button to menu with name 'I'mport'M'enu'I'tem 
        # ID_ANY is used as there is no dedicated id for imports
        imi = fileMenu.Append(wx.ID_ANY, '&Import Excel')
        smi = fileMenu.Append(wx.ID_SAVE, '&Save Config')
        fileMenu.AppendSeparator()
        qmi = fileMenu.Append(wx.ID_EXIT, 'Exit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        helpMenu = wx.Menu()
        hmi = helpMenu.Append(wx.ID_HELP, '&Quick Start')
        menubar.Append(helpMenu, '&Help')
        self.SetMenuBar(menubar)
        self.CreateStatusBar()
        self.Bind(wx.EVT_MENU, self.OnOpen, omi)
        self.Bind(wx.EVT_MENU, self.OnImport, imi)
        self.Bind(wx.EVT_MENU, self.OnSave, smi)
        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
        self.Bind(wx.EVT_MENU, self.OnHelp, hmi)

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        self._nb = wx.Notebook(p)
        self._nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageSelected)

        # create the page windows as children of the notebook
        tabOne = gv.GeneralView(self._nb, controller)
        tabTwo = tv.TransmissionView(self._nb, controller)

        # add the pages to the notebook with the label to show on the tab
        self._nb.AddPage(tabOne, "Overview")
        self._nb.AddPage(tabTwo, "Transmission")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(self._nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

    def AddRESTab(self, controller, siteName):
        """This function is called when the user add a new site to the system.
        It does the following:
            - Create a new tab for that site (a RESView instance)
            - Add this tab to notebook

        Args:
            - controller: Reference to the controller
            - siteName: The name of the site
        """
        resTab = res.RESView(self._nb, controller, siteName)
        self._nb.AddPage(resTab, "Ref. Energy Sys. [" + siteName + "]")

        return resTab

    def RemoveRESTab(self, sites):
        """This function is called when the user remove a site or more from the
        system. It does the following:
            - For each site of the removed sites

                - Loop on the notebook tabs (pages), from index 2. As index 0
                  is for the Overview tab, and index 1 is for Transmission tab.
                    - Remove the RESView tab (page) from the note book, if its
                      associated name is equal to the site that the user want to
                      remove.
            - Set the Overview tab as the selected tab

        Args:
            sites: List of sites to remove
        """
        for site in sites:
            for i in range(2, self._nb.GetPageCount()):
                if self._nb.GetPage(i).GetSiteName() == site:
                    self._nb.RemovePage(i)
                    break

        self._nb.SetSelection(0)

    def GetTrnsmTab(self):
        """This function returns the RESView of the transmission tab.
        Page #1 in the notebook.

        Return:
             Transmission Tab
        """
        return self._nb.GetPage(1)

    def OnPageSelected(self, event):
        """This function is triggered when the user change the selected tab in
        the notebook.
            - First, we get the tab index
            - If the index is 0 (Overview tab) or 1 (Transmission tab), then
              nothing to do
            - Get the RESView instance of the selected tab
            - Refresh the view to redraw itself
            - Send a notification that the active RES tab is now for Site X.
              The controller is actually interested in such notification, so it
              can obtain a reference for the model of the current active site.
              So, when the user add/remove process for instance, the controller
              will be able to update the model of that particular site.

        Args:
            event: The event object from WX
        """
        pageIndx = event.GetSelection()
        if pageIndx in (0, 1):
            return

        resView = self._nb.GetPage(pageIndx)
        pub.sendMessage(EVENTS.RES_SELECTED, siteName=resView.GetSiteName())
        resView.Refresh()

    def __del__(self):
        pass

    def OnOpen(self, event):
        """This function is triggered when the user select “Load Config” from
        the file menu.
            - It creates an open file dialog and set the filter to json files.
            - If the user selected a file, the method will send a notification
              to load the configuration. The controller subscribe on such
              notification and it will start the loading process.

        Args:
            event: The event object from WX
        """
        # Create open file dialog
        openFileDialog = wx.FileDialog(self, "Open", "./samples", "",
                                       "urbs files (*.json)|*.json",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        fn = openFileDialog.GetPath()
        if fn:
            s = wx.MessageBox('Are you sure? All non saved data will be lost!',
                              'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if s == wx.OK:
                pub.sendMessage(EVENTS.LOAD_CONFIG, filename=fn)

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

    def OnSave(self, event):
        """This function is triggered when the user select “Save Config” from
        the file menu.
            - It creates a save file dialog and set the filter to json files.
            - It warns the user if he tried to override existing file
              (wx.FD_OVERWRITE_PROMPT)
            - If the user selected a file, the method will send a notification
              to save the system. The controller subscribe on such notification
              and it will start the saving process of the whole modeled system.

        Args:
            event: The event object from WX
        """
        openFileDialog = wx.FileDialog(self, "Save", "./samples", "",
                                       "urbs files (*.json)|*.json",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        openFileDialog.ShowModal()
        fn = openFileDialog.GetPath()
        if fn:
            pub.sendMessage(EVENTS.SAVE_CONFIG, filename=fn)

    def OnQuit(self, event):
        """This function is triggered when the user select “Exit” from the file
        menu. It simply terminate the program.

        Args:
            event: The event object from WX
        """
        self.Close()

    def OnHelp(self, event):
        """This function is triggered when the user select “Help” from the file
        menu. It opens the help file in the default browser.

        Args:
            event: The event object from WX
        """
        file = 'file://' + os.path.realpath('./help/quickstart_gui.html')
        webbrowser.open(file, new=2)  # in new tab
