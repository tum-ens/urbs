# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 02:56:46 2018

@author: aelshaha
"""

import wx
import wx.grid
import DataConfig as config
import GridDataTable as gdt
import BasicForm as bf
import copy as cpy
import TimeSeriesForm as ts

from pubsub import pub
from Events import EVENTS


class CommodityDialog (bf.BasicForm):

    _gridCols = config.DataConfig.COMMODITY_PARAMS

    def __init__(self, parent):
        super().__init__(parent, "Commodity data", wx.Size(800, 500))
        contentLayout = wx.BoxSizer(wx.VERTICAL)

        layout0 = self.CreateGeneralLayout()
        layout1 = self.CreateParamsLayout()

        contentLayout.Add(layout0, 0, wx.ALL | wx.EXPAND, 5)
        contentLayout.Add(layout1, 1, wx.ALL | wx.EXPAND |
                          wx.ALIGN_CENTER_HORIZONTAL, 5)

        super().SetContent(contentLayout, wx.ALIGN_CENTER_HORIZONTAL)

    def CreateParamsLayout(self):
        h1 = wx.StaticBox(self, wx.ID_ANY, u"Parameters:")
        h1.SetForegroundColour('white')
        layout1 = wx.StaticBoxSizer(h1, wx.VERTICAL)

        self._gridTable = gdt.GridDataTable(self._gridCols)
        self._yearsGrid = wx.grid.Grid(self)
        self._yearsGrid.SetTable(self._gridTable, True)
        self._yearsGrid.AutoSizeColumns(False)
        self._yearsGrid.HideCol(0)  # time series
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self._yearsGrid.SetColAttr(config.DataConfig.TS_BTN_COL, attr)  # ...
        self._yearsGrid.Bind(
            wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnTimeSerClick)
        layout1.Add(self._yearsGrid, 1, wx.ALL | wx.EXPAND, 5)

        return layout1

    def OnTimeSerClick(self, event):
        if event.GetCol() != config.DataConfig.TS_BTN_COL:
            return

        tsf = ts.TimeSeriesForm(self)
        tsf.PopulateData(self._commodity['Name'],
                         self._gridTable, event.GetRow(), 0)
        tsf.ShowModal()

    def CreateGeneralLayout(self):
        layout0 = wx.BoxSizer(wx.HORIZONTAL)
        # Type
        label = wx.StaticText(self, -1, "Commodity Type:")
        label.SetForegroundColour(wx.WHITE)
        layout0.Add(label, 0, wx.ALL, 5)
        self._lblCommType = wx.StaticText(self, -1, "...")
        self._lblCommType.SetForegroundColour(wx.WHITE)
        layout0.Add(self._lblCommType, 0, wx.ALL, 5)
        label = wx.StaticText(self, -1, "....", size=wx.Size(240, 5))
        layout0.Add(label, 0, wx.ALL, 5)
        self._chkDSM = wx.CheckBox(self, -1, "Demand Side Management (DSM)")
        self._chkDSM.SetForegroundColour(wx.WHITE)
        self._chkDSM.Hide()
        self._chkDSM.Bind(wx.EVT_CHECKBOX, self.OnDSMChange)
        layout0.Add(self._chkDSM, 0, wx.ALL, 5)
        # Name
        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Commodity name:")
        label.SetForegroundColour(wx.WHITE)
        layout1.Add(label, 0, wx.ALL, 5)
        self._txtCommName = wx.TextCtrl(self, size=wx.Size(200, 25))
        layout1.Add(self._txtCommName, 0, wx.ALL, 5)
        # Color
        label = wx.StaticText(self, -1, "...........................")
        layout1.Add(label, 0, wx.ALL, 5)
        label = wx.StaticText(self, -1, "Color:")
        label.SetForegroundColour(wx.WHITE)
        layout1.Add(label, 0, wx.ALL, 5)
        self._color = wx.ColourPickerCtrl(self, -1, wx.Colour(0, 0, 0))
        layout1.Add(self._color, 0, wx.ALL, 5)

        layout2 = wx.BoxSizer(wx.VERTICAL)
        layout2.Add(layout0, 1, wx.ALL | wx.EXPAND, 5)
        layout2.Add(layout1, 1, wx.ALL | wx.EXPAND, 5)

        return layout2

    def OnDSMChange(self, event):
        startCol = config.DataConfig.TS_BTN_COL + 1
        endCol = startCol + len(config.DataConfig.DSM_PARAMS)

        if self._chkDSM.IsChecked():
            for i in range(startCol, endCol):
                self._yearsGrid.ShowCol(i)
        else:
            for i in range(startCol, endCol):
                self._yearsGrid.HideCol(i)

    def PopulateCommodity(self, comm):
        self._orgComm = cpy.deepcopy(comm)
        self._commodity = comm
        self._lblCommType.SetLabel(comm['Type'])
        self._chkDSM.SetValue(comm['DSM'])
        self._txtCommName.SetValue(comm['Name'])
        self._color.SetColour(comm['Color'])
        super().PopulateGrid(self._gridTable, comm['Years'])
        super().SetDataItem(self._commodity)
        # Hide TS column
        if comm['Type'] in (config.DataConfig.COMM_STOCK,
                            config.DataConfig.COMM_ENV):
            # no time series
            self._yearsGrid.HideCol(config.DataConfig.TS_BTN_COL)
        if comm['Type'] in (config.DataConfig.COMM_SUPIM,
                            config.DataConfig.COMM_DEMAND):
            # only time series
            for i in range(1, config.DataConfig.TS_BTN_COL):
                self._yearsGrid.HideCol(i)
        if comm['Type'] in (config.DataConfig.COMM_DEMAND):
            self._chkDSM.Show()

        self.OnDSMChange(None)

    def OnOk(self, event):
        self._commodity['Type'] = self._lblCommType.GetLabelText()
        self._commodity['Name'] = self._txtCommName.GetValue()
        self._commodity['Color'] = self._color.GetColour()
        self._commodity['DSM'] = self._chkDSM.GetValue()
        self._gridTable.Commit()
        pub.sendMessage(EVENTS.COMMODITY_SAVE, data=self._commodity)

    def OnCancel(self, event):
        self._commodity.update(self._orgComm)
        super().OnCancel(event)
