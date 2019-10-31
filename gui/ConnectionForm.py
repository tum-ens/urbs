# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.grid
import DataConfig as config
import GridDataTable as gdt
import BasicForm as bf


class ConnectionDialog (bf.BasicForm):
    """
    This form is used to add a new Connection or edit an existing one. The form
    inherits from the BasicForm class. Connection is the link between a
    a process and a commodity, so it could be IN or OUT connection.
    """

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
        """This method is called when the user try to Edit a connection. The
        form is populated with the data of the selected connection. It shows
        a grid with a row for each year.

        Args:
            connection: The connection data
        """
        self._conn = connection
        super().PopulateGrid(self._gridTable, connection['Years'])
