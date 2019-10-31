# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx.grid
import copy as cpy
import DataConfig as config


class GridDataTable(wx.grid.GridTableBase):
    """
    This is the basic module for all grids we have in our solution. This handle
    the grid data and how it is displayed. It extends the wx.grid.GridTableBase
    functionality.
    """

    def __init__(self, cols, rows=None, autoCommit=False):
        wx.grid.GridTableBase.__init__(self)

        self._cols = cols
        self._rows = []
        self._autoCommit = autoCommit
        self._tmpData = {}
        self._data = {}

        if rows:
            self._rows = rows

    # --------------------------------------------------
    def SetTableData(self, data):
        """
        This method is called to set the grid data. It stores a copy of it in
        case the user decided to discard the changes.

        Args:
            data: The grid data dictionary
        """
        self._data = data
        if self._autoCommit:
            self._tmpData = self._data
        else:
            self._tmpData = cpy.deepcopy(self._data)

    def Commit(self):
        """
        This method is called when the user want to save the changes he/she
        made.
        """
        # print('Commit')
        self._data.update(self._tmpData)  # only if data is NOT shared
#        for year, params in self._tmpData.items():
#            for col in self._cols:
#                colKey = col[config.DataConfig.PARAM_KEY]
#                self._data[year][colKey] = params[colKey]

    # --------------------------------------------------
    # required methods for the wxPyGridTableBase interface
    def GetNumberRows(self):
        """
        This method is called to get the number of rows in the grid.

        Returns:
            Number of rows
        """
        # print('GetNumberRows', len(self._data))
        return len(self._data)

    def GetNumberCols(self):
        """
        This method is called to get the number of cols in the grid.

        Returns:
            Number of cols
        """
        # print('GetNumberCols', len(self._cols))
        return len(self._cols)

    def IsEmptyCell(self, row, col):
        """
        This method is called to check if a cell in the grid is empty or not.

        Args:
            - row: The row number for the cell
            - col: The col number for the cell

        Returns:
            True in case the cell us empty
        """
        # print('IsEmptyCell', row, col)
        rowKey = self.GetRowKey(row)
        colKey = self._cols[col][config.DataConfig.PARAM_KEY]
        if rowKey and colKey:
            return not self._tmpData[rowKey][colKey]

        return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        """
        This method is called to get the value of a cell in the grid.

        Args:
            - row: The row number for the cell
            - col: The col number for the cell

        Returns:
            The value (content) of the cell
        """
        # print('GetValue', row, col)
        rowKey = self.GetRowKey(row)
        colKey = self._cols[col][config.DataConfig.PARAM_KEY]
        if rowKey and colKey:
            try:
                return self._tmpData[rowKey][colKey]
            except KeyError:
                return ''

        return ''

    def SetValue(self, row, col, value):
        """
        This method is called to set the value of a cell in the grid.

        Args:
            - row: The row number for the cell
            - col: The col number for the cell
            - value: The new value for the cell
        """
        # print('SetValue', row, col, value)
        v = value
        cellType = self.GetTypeName(row, col)
        colKey = self._cols[col][config.DataConfig.PARAM_KEY]
        rowKey = self.GetRowKey(row)

        if (cellType != wx.grid.GRID_VALUE_BOOL and
            not cellType.startswith(wx.grid.GRID_VALUE_CHOICE) and
                colKey not in ('timeSer', 'timeEff')):
            v = self.ConvertToNumber(value)
            if v is None:
                return

        self._tmpData[rowKey][colKey] = v

    # --------------------------------------------------
    # Some optional methods
    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        """
        This method is called to get the label (header) for a certain column.

        Args:
            col: The col number

        Returns:
            The header for the col
        """
        # print('GetColLabelValue', col)
        return self._cols[col][config.DataConfig.GRID_COL_LABEL]

    def GetRowLabelValue(self, row):
        """
        This method is called to get the label (header) for a certain row.

        Args:
            row: The row number

        Returns:
            The header for the row
        """
        # print('GetRowLabelValue', row, len(self._data))
        lbl = ''
        if len(self._rows) > 0 and row < len(self._rows):
            lbl = self._rows[row][config.DataConfig.GRID_ROW_LABEL]
        elif row < len(self._data):
            lbl = sorted(self._data.keys())[row]

        return lbl

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        """
        This method is called to determine the kind of editor/renderer to use.
        By default, doesn't necessarily have to be the same type used natively
        by the editor/renderer if they know how to convert.

        Args:
            - row: The row number for the cell
            - col: The col number for the cell
        """
        # print('GetTypeName', row, col)
        if len(self._rows) > 0 and row < len(self._rows):
            dataType = self._rows[row][config.DataConfig.GRID_ROW_DATATYPE]
            return dataType

        return self._cols[col][config.DataConfig.GRID_COL_DATATYPE]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        """
        This method is called to determine how the data can be fetched and
        stored by the editor and renderer.  This allows you to enforce some
        type-safety in the grid.

        Args:
            - row: The row number for the cell
            - col: The col number for the cell
            - typeName: The type of the data for the cell

        Returns:
            True in case the cell value of the passed type
        """
        cellType = self.GetTypeName(row, col).split(':')[0]
        if typeName == cellType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        """
        This method is just calling the CanGetValueAs method.

        Args:
            - row: The row number for the cell
            - col: The col number for the cell
            - typeName: The type of the data for the cell

        Returns:
            True in case the cell value of the passed type
        """
        return self.CanGetValueAs(row, col, typeName)

    def GetData(self):
        """
        This method is called to get the grid data.

        Returns:
            The data of the grid
        """
        return self._tmpData

    def FillAll(self):
        """
        This method is called to fill all grid rows with the same values of the
        first row.
        """
        data = {}
        if self._autoCommit:
            data = self._data
        else:
            data = self._tmpData

        if len(data) == 0:
            return

        firstKey = sorted(data)[0]
        for key in data.keys():
            if key != firstKey:
                data[key] = data[firstKey]

    def ConvertToNumber(self, value):
        """
        This method is called to check if the passed value can be converted to
        a number or not.

        Args:
            value: The value to check
        """
        try:
            vf = float(value)
            try:
                vi = int(value)
                return vi
            except ValueError:
                return vf
        except ValueError:
            if value.lower() == config.DataConfig.INF.lower():
                return config.DataConfig.INF
            elif value.lower() == config.DataConfig.NaN:
                return config.DataConfig.NaN
            else:
                return None

    def GetRowKey(self, row):
        """
        This method is called to get the row key.

        Args:
            row: The row number

        Returns:
            The key of the passed row
        """
        if len(self._rows) > 0:
            return self._rows[row][config.DataConfig.PARAM_KEY]

        return self.GetRowLabelValue(row)
# ---------------------------------------------------------------------------
