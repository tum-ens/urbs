
import wx
import os
import webbrowser
import GeneralView as gv
import RESView as res
import TransmissionView as tv

from pubsub import pub
from Events import EVENTS


class MainView (wx.Frame):

    def __init__(self, controller):
        wx.Frame.__init__(self, None, title="urbs gui 1.0")

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        omi = fileMenu.Append(wx.ID_OPEN, '&Load Config')
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
        resTab = res.RESView(self._nb, controller, siteName)
        self._nb.AddPage(resTab, "Ref. Energy Sys. [" + siteName + "]")

        return resTab

    def RemoveRESTab(self, sites):
        for site in sites:
            for i in range(2, self._nb.GetPageCount()):
                if self._nb.GetPage(i).GetSiteName() == site:
                    self._nb.RemovePage(i)
                    break

        self._nb.SetSelection(0)

    def GetTrnsmTab(self):
        return self._nb.GetPage(1)

    def OnPageSelected(self, event):
        pageIndx = event.GetSelection()
        if pageIndx in (0, 1):
            return

        resView = self._nb.GetPage(pageIndx)
        pub.sendMessage(EVENTS.RES_SELECTED, siteName=resView.GetSiteName())
        resView.Refresh()

    def __del__(self):
        pass

    def OnOpen(self, event):
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

    def OnSave(self, event):
        openFileDialog = wx.FileDialog(self, "Save", "./samples", "",
                                       "urbs files (*.json)|*.json",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        openFileDialog.ShowModal()
        fn = openFileDialog.GetPath()
        if fn:
            pub.sendMessage(EVENTS.SAVE_CONFIG, filename=fn)

    def OnQuit(self, event):
        self.Close()

    def OnHelp(self, event):
        file = 'file://' + os.path.realpath('./help/quickstart_gui.html')
        webbrowser.open(file, new=2)  # in new tab
