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

from pubsub import pub
from Events import EVENTS


class StorageDialog (bf.BasicForm):

    _gridCols = config.DataConfig.STORAGE_PARAMS

    def __init__(self, parent):
        super().__init__(parent, "Storage data", wx.Size(800, 450))
        contentLayout = wx.BoxSizer(wx.VERTICAL)

        layout0 = self.CreateGeneralLayout()

        h1 = wx.StaticBox(self, wx.ID_ANY, u"Parameters:")
        h1.SetForegroundColour('white')
        layout1 = wx.StaticBoxSizer(h1, wx.VERTICAL)
        # Grid and its data table
        self._gridTable1 = gdt.GridDataTable(self._gridCols)
        self._yearsGrid1 = wx.grid.Grid(h1, -1)
        self._yearsGrid1.SetTable(self._gridTable1, True)
        self._yearsGrid1.AutoSizeColumns(False)
        layout1.Add(self._yearsGrid1, 1, wx.ALL, 3)

        contentLayout.Add(layout0, 0, wx.ALL, 5)
        contentLayout.Add(layout1, 1, wx.ALL | wx.EXPAND, 1)
        super().SetContent(contentLayout, wx.ALIGN_CENTER_HORIZONTAL)

    def CreateGeneralLayout(self):

        layout = wx.BoxSizer(wx.HORIZONTAL)

        # Name Part
        label = wx.StaticText(self, -1, "Storage name:")
        label.SetForegroundColour(wx.WHITE)
        layout.Add(label, 0, wx.ALL, 5)
        self._txtStorageName = wx.TextCtrl(self, size=wx.Size(200, 25))
        layout.Add(self._txtStorageName, 0, wx.ALL, 5)
        #######################################################################
        label = wx.StaticText(self, -1, ".....................")
        layout.Add(label, 0, wx.ALL, 5)
        #######################################################################
        label = wx.StaticText(self, -1, "Commodity:")
        label.SetForegroundColour(wx.WHITE)
        layout.Add(label, 0, wx.ALL, 5)
        self._ddlComm = wx.ComboBox(self, -1, size=wx.Size(200, 25),
                                    style=wx.CB_DROPDOWN | wx.CB_READONLY)
        layout.Add(self._ddlComm, 0, wx.ALL, 5)

        return layout

    def PopulateStorage(self, storage, commList):
        self._orgStrg = cpy.deepcopy(storage)
        self._storage = storage
        self._txtStorageName.SetValue(storage['Name'])
        for k, v in commList.items():
            self._ddlComm.Append(v['Name'], k)
        if len(storage['IN']) > 0:
            self._ddlComm.SetValue(commList[storage['IN'][0]]['Name'])

        super().PopulateGrid(self._gridTable1, storage['Years'])
        super().SetDataItem(self._storage)

    def OnOk(self, event):
        self._storage['Name'] = self._txtStorageName.GetValue()
        self._storage['IN'] = self.GetSelectedCommodity()
        self._gridTable1.Commit()
        pub.sendMessage(EVENTS.STORAGE_SAVE, data=self._storage)

    def GetSelectedCommodity(self):
        x = []
        s = self._ddlComm.GetSelection()
        if s >= 0:
            x.append(self._ddlComm.GetClientData(s))
        return x

    def OnCancel(self, event):
        self._storage.update(self._orgStrg)
        super().OnCancel(event)
