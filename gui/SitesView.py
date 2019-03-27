# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 15:43:07 2018

@author: aelshaha
"""

import wx
import wx.grid
import DataConfig as config
import GridDataTable as gdt

from Events import EVENTS
from pubsub import pub


class SitesView():

    _gridCols = config.DataConfig.SITE_PARAMS

    def __init__(self, parent):

        # manage layout
        headerBox = wx.StaticBox(parent, wx.ID_ANY, u"Manage Sites:")
        headerBox.SetForegroundColour('white')

        self._mainLayout = wx.StaticBoxSizer(headerBox, wx.HORIZONTAL)
        sitesLayout = wx.BoxSizer(wx.VERTICAL)
        # imgLayout = wx.BoxSizer( wx.VERTICAL )

        self._mainLayout.Add(sitesLayout, 0, wx.ALL | wx.EXPAND, 5)
        # mainLayout.Add(imgLayout, 1, wx.EXPAND|wx.ALIGN_CENTER, 5 )

        # Add site section
        addSiteLayout = wx.StaticBoxSizer(
            wx.StaticBox(parent, wx.ID_ANY, u""), wx.HORIZONTAL)
        # label = wx.StaticText(addSiteLayout.GetStaticBox(), -1, "Site:")
        # addSiteLayout.Add(label, 0, wx.ALL, 5)

        self._txtSite = wx.TextCtrl(addSiteLayout.GetStaticBox())
        self._txtSite.Bind(wx.EVT_TEXT, self.TxtSiteOnTextChange)
        addSiteLayout.Add(self._txtSite, 0, wx.ALL, 5)

        self._btnAdd = wx.Button(
            addSiteLayout.GetStaticBox(), label="Add Site")
        self._btnAdd.Bind(wx.EVT_BUTTON, self.BtnAddOnClick)
        self._btnAdd.Disable()
        addSiteLayout.Add(self._btnAdd, 0, wx.ALL, 5)

        self._btnRemove = wx.Button(parent, label="Remove Selected Site(s)")
        self._btnRemove.Bind(wx.EVT_BUTTON, self.BtnRemoveOnClick)
        # self._btnRemove.Disable()
        # addSiteLayout.Add(self._btnRemove, 0, wx.ALL, 5 )

        sitesLayout.Add(addSiteLayout, 0, wx.ALL | wx.EXPAND, 5)

        # Grid and its data table
        self._gridTable = gdt.GridDataTable(self._gridCols, autoCommit=True)
        self._sitesGrid = wx.grid.Grid(parent, -1)
        self._sitesGrid.SetTable(self._gridTable, True)
        # col2-4
        for i in range(0, len(self._gridCols)):
            self._sitesGrid.SetColSize(i, 120)
        self._sitesGrid.SetColSize(0, 20)
        self._sitesGrid.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)

        sitesLayout.Add(self._sitesGrid, 1, wx.ALL | wx.EXPAND, 5)
        sitesLayout.Add(self._btnRemove, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL, 5)

        pub.subscribe(self.SiteIsAdded, EVENTS.SITE_ADDED)
        pub.subscribe(self.SitesAreRemoved, EVENTS.SITE_REMOVED)

    def GetLayout(self):
        return self._mainLayout

    def TxtSiteOnTextChange(self, event):
        txt = event.GetEventObject().GetValue()
        if len(txt) > 0:
            self._btnAdd.Enable()
        else:
            self._btnAdd.Disable()

    def BtnAddOnClick(self, event):
        newSite = self._txtSite.GetValue()
        pub.sendMessage(EVENTS.SITE_ADDING, site=newSite)

    def BtnRemoveOnClick(self, event):
        rows = self._sitesGrid.GetNumberRows()
        if rows == 0:
            return

        sitesToRmv = []
        for i in range(0, rows):
            val = self._sitesGrid.GetCellValue(i, 0)
            if val:
                sitesToRmv.append(self._sitesGrid.GetRowLabelValue(i))

        pub.sendMessage(EVENTS.SITE_REMOVING, sites=sitesToRmv)

    def SiteIsAdded(self, sites):
        # tell the grid we've changed the data
        cur = self._sitesGrid.GetNumberRows()
        self._gridTable.SetTableData(sites)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,  # what we did to it
                   # how many
                   len(sites) - cur
              )
        self._gridTable.GetView().ProcessTableMessage(msg)

    def SitesAreRemoved(self, sites, removeCount):
        # tell the grid we've changed the data
        self._gridTable.SetTableData(sites)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,   # what we did to it
                   # how many
                   len(sites), removeCount
              )
        self._gridTable.GetView().ProcessTableMessage(msg)
