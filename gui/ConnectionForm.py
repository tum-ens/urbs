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


class ConnectionDialog (bf.BasicForm):

    _gridCols = config.DataConfig.CONNECTION_PARAMS

    def __init__(self, parent):
        super().__init__(parent, "Connection data", wx.Size(500, 400), False)

        self._gridTable = gdt.GridDataTable(self._gridCols)
        self._yearsGrid = wx.grid.Grid(self, -1)
        self._yearsGrid.SetTable(self._gridTable, True)
        for i in range(0, len(self._gridCols)):
            self._yearsGrid.SetColSize(i, 150)
        # self._yearsGrid.AutoSizeColumns(False)
        super().SetContent(self._yearsGrid, wx.ALIGN_CENTER_HORIZONTAL)

    def PopulateConnectionGrid(self, connection):
        self._conn = connection
        super().PopulateGrid(self._gridTable, connection['Years'])
