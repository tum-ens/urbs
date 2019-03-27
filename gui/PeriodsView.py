# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 17:10:44 2019

@author: aelshaha
"""

import wx
import wx.grid
import DataConfig as config
import GridDataTable as gdt

from Events import EVENTS
from pubsub import pub


class PeriodsView():

    _gridCols = config.DataConfig.PERIOD_PARAMS

    def __init__(self, parent):

        # manage layout
        headerBox = wx.StaticBox(parent, wx.ID_ANY, u"Manage Periods:")
        headerBox.SetForegroundColour('white')

        self._mainLayout = wx.StaticBoxSizer(headerBox, wx.HORIZONTAL)
        periodsLayout = wx.BoxSizer(wx.VERTICAL)
        # imgLayout = wx.BoxSizer( wx.VERTICAL )

        self._mainLayout.Add(periodsLayout, 0, wx.ALL | wx.EXPAND, 5)
        # mainLayout.Add(imgLayout, 1, wx.EXPAND|wx.ALIGN_CENTER, 5 )

        # Add period section
        addPeriodLayout = wx.StaticBoxSizer(
            wx.StaticBox(parent, wx.ID_ANY, u""), wx.HORIZONTAL)
        # addPeriodLayout = wx.BoxSizer( wx.HORIZONTAL )
        # label = wx.StaticText(addPeriodLayout.GetStaticBox(), -1, "Period:")
        # addPeriodLayout.Add(label, 0, wx.ALL, 5)

        self._txtPeriod = wx.TextCtrl(parent)
        self._txtPeriod.Bind(wx.EVT_TEXT, self.TxtPeriodOnTextChange)
        addPeriodLayout.Add(self._txtPeriod, 1, wx.ALL, 5)

        self._btnAdd = wx.Button(parent, label="Add Period")
        self._btnAdd.Bind(wx.EVT_BUTTON, self.BtnAddOnClick)
        self._btnAdd.Disable()
        addPeriodLayout.Add(self._btnAdd, 1, wx.ALL, 5)

        self._btnRemove = wx.Button(parent, label="Remove Selected Period(s)")
        self._btnRemove.Bind(wx.EVT_BUTTON, self.BtnRemoveOnClick)
        # self._btnRemove.Disable()
        # addPeriodLayout.Add(self._btnRemove, 0, wx.ALL, 5 )

        periodsLayout.Add(addPeriodLayout, 0, wx.ALL | wx.EXPAND, 5)

        # Grid and its data table
        self._gridTable = gdt.GridDataTable(self._gridCols, autoCommit=True)
        self._periodsGrid = wx.grid.Grid(parent, -1)
        self._periodsGrid.SetTable(self._gridTable, True)
        # col2-4
        for i in range(0, len(self._gridCols)):
            self._periodsGrid.SetColSize(i, 100)
        self._periodsGrid.SetColSize(0, 20)
        self._periodsGrid.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)

        periodsLayout.Add(self._periodsGrid, 1, wx.ALL | wx.EXPAND, 5)
        periodsLayout.Add(self._btnRemove, 0, wx.ALL |
                          wx.ALIGN_CENTER_HORIZONTAL, 5)

        pub.subscribe(self.PeriodIsAdded, EVENTS.PERIOD_ADDED)
        pub.subscribe(self.PeriodsAreRemoved, EVENTS.PERIOD_REMOVED)

    def GetLayout(self):
        return self._mainLayout

    def TxtPeriodOnTextChange(self, event):
        txt = event.GetEventObject().GetValue()
        if len(txt) > 0:
            self._btnAdd.Enable()
        else:
            self._btnAdd.Disable()

    def BtnAddOnClick(self, event):
        newPeriod = self._txtPeriod.GetValue()
        pub.sendMessage(EVENTS.PERIOD_ADDING, period=newPeriod)

    def BtnRemoveOnClick(self, event):
        rows = self._periodsGrid.GetNumberRows()
        if rows == 0:
            return

        periodsToRmv = []
        for i in range(0, rows):
            val = self._periodsGrid.GetCellValue(i, 0)
            if val:
                periodsToRmv.append(self._periodsGrid.GetRowLabelValue(i))

        pub.sendMessage(EVENTS.PERIOD_REMOVING, periods=periodsToRmv)

    def PeriodIsAdded(self, periods):
        # tell the grid we've changed the data
        cur = self._periodsGrid.GetNumberRows()
        self._gridTable.SetTableData(periods)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,  # what we did to it
                   # how many
                   len(periods) - cur
                   )
        self._gridTable.GetView().ProcessTableMessage(msg)

    def PeriodsAreRemoved(self, periods, removeCount):
        # tell the grid we've changed the data
        self._gridTable.SetTableData(periods)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,   # what we did to it
                   # how many
                   len(periods), removeCount
                   )
        self._gridTable.GetView().ProcessTableMessage(msg)
