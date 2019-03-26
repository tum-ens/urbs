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


class YearsView():

    _gridCols = config.DataConfig.YEAR_PARAMS

    def __init__(self, parent):

        # manage layout
        headerBox = wx.StaticBox(parent, wx.ID_ANY, u"Manage Years:")
        headerBox.SetForegroundColour('white')

        self._mainLayout = wx.StaticBoxSizer(headerBox, wx.HORIZONTAL)
        yearsLayout = wx.BoxSizer(wx.VERTICAL)
        # imgLayout = wx.BoxSizer( wx.VERTICAL )

        self._mainLayout.Add(yearsLayout, 0, wx.ALL | wx.EXPAND, 5)
        # mainLayout.Add(imgLayout, 1, wx.EXPAND|wx.ALIGN_CENTER, 5 )

        # Add year section
        addYearLayout = wx.StaticBoxSizer(
            wx.StaticBox(parent, wx.ID_ANY, u""), wx.HORIZONTAL)
        # label = wx.StaticText(addYearLayout.GetStaticBox(), -1, "Year:")
        # addYearLayout.Add(label, 0, wx.ALL, 5)

        self._txtYear = wx.TextCtrl(addYearLayout.GetStaticBox())
        self._txtYear.SetMaxLength(4.0)
        self._txtYear.Bind(wx.EVT_CHAR, self.TxtYearOnKeyPress)
        self._txtYear.Bind(wx.EVT_TEXT, self.TxtYearOnTextChange)
        addYearLayout.Add(self._txtYear, 0, wx.ALL, 5)

        self._btnAdd = wx.Button(
            addYearLayout.GetStaticBox(), label="Add Year")
        self._btnAdd.Bind(wx.EVT_BUTTON, self.BtnAddOnClick)
        self._btnAdd.Disable()
        addYearLayout.Add(self._btnAdd, 0, wx.ALL, 5)

        self._btnRemove = wx.Button(parent, label="Remove Selected Year(s)")
        self._btnRemove.Bind(wx.EVT_BUTTON, self.BtnRemoveOnClick)
        # self._btnRemove.Disable()
        # addYearLayout.Add(self._btnRemove, 0, wx.ALL, 5 )

        yearsLayout.Add(addYearLayout, 0, wx.ALL | wx.EXPAND, 5)

        # Grid and its data table
        self._gridTable = gdt.GridDataTable(self._gridCols, autoCommit=True)
        self._yearsGrid = wx.grid.Grid(parent, -1)
        self._yearsGrid.SetTable(self._gridTable, True)
        # col2-4
        for i in range(0, len(self._gridCols)):
            self._yearsGrid.SetColSize(i, 120)
        self._yearsGrid.SetColSize(0, 20)

        yearsLayout.Add(self._yearsGrid, 1, wx.ALL | wx.EXPAND, 5)
        yearsLayout.Add(self._btnRemove, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL, 5)

        pub.subscribe(self.YearIsAdded, EVENTS.YEAR_ADDED)
        pub.subscribe(self.YearsAreRemoved, EVENTS.YEAR_REMOVED)

    def GetLayout(self):
        return self._mainLayout

    def TxtYearOnKeyPress(self, event):
        acceptable_characters = "1234567890\b"  # include backspace
        key = event.GetKeyCode()

        if chr(key) in acceptable_characters:
            txt = event.GetEventObject().GetValue()
            if len(txt) == 0 and chr(key) == '0':
                return False

            event.Skip()
            return
        else:
            return False

    def TxtYearOnTextChange(self, event):
        txt = event.GetEventObject().GetValue()
        if len(txt) == 4:
            self._btnAdd.Enable()
        else:
            self._btnAdd.Disable()

    def BtnAddOnClick(self, event):
        newYear = self._txtYear.GetValue()
        pub.sendMessage(EVENTS.YEAR_ADDING, year=newYear)

    def BtnRemoveOnClick(self, event):
        rows = self._yearsGrid.GetNumberRows()
        if rows == 0:
            return

        yrsToRmv = []
        for i in range(0, rows):
            val = self._yearsGrid.GetCellValue(i, 0)
            if val:
                yrsToRmv.append(self._yearsGrid.GetRowLabelValue(i))

        pub.sendMessage(EVENTS.YEAR_REMOVING, years=yrsToRmv)

    def YearIsAdded(self, years):
        # tell the grid we've changed the data
        cur = self._yearsGrid.GetNumberRows()
        self._gridTable.SetTableData(years)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,  # what we did to it
                   len(years) - cur                         # how many
              )
        self._gridTable.GetView().ProcessTableMessage(msg)

    def YearsAreRemoved(self, years, removeCount):
        # tell the grid we've changed the data
        self._gridTable.SetTableData(years)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,   # what we did to it
                   len(years), removeCount                  # how many
              )
        self._gridTable.GetView().ProcessTableMessage(msg)
