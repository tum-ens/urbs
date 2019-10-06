# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx

from pubsub import pub
from Events import EVENTS


class BasicForm(wx.Dialog):
    """This module represent the basic form layout in the GUI. It assumes the
    form consists of a grid that contains the data per each year, and a set of
    buttons that user can use like (OK, cancel, copy, clone, delete and Fill
    all as the first year). This layout is common in our forms and will be
    inherited by many other modules as we will see later.
    """

    _gridTables = []

    def __init__(self, parent, formTitle, formSize, allowCopy=True):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY,
                           title=formTitle, size=formSize)
        self.SetBackgroundColour("black")

        mainLayout = wx.BoxSizer(wx.VERTICAL)
        self._contentLayout = wx.BoxSizer(wx.VERTICAL)
        mainLayout.Add(self._contentLayout, 1, wx.ALL |
                       wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 5)

        btnsLayout = wx.BoxSizer(wx.HORIZONTAL)
        btnOk = wx.Button(self, label="Ok")
        btnOk.Bind(wx.EVT_BUTTON, self.OnOk)
        btnCancel = wx.Button(self, label="Cancel")
        btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        btnFillAll = wx.Button(self, label="Fill all as first year")
        btnFillAll.Bind(wx.EVT_BUTTON, self.OnFillAll)
        btnCopy = wx.Button(self, label="Copy to other sites")
        btnCopy.Bind(wx.EVT_BUTTON, self.OnCopy)
        btnDel = wx.Button(self, label="Delete")
        btnDel.Bind(wx.EVT_BUTTON, self.OnDelete)
        btnClone = wx.Button(self, label="Clone here")
        btnClone.Bind(wx.EVT_BUTTON, self.OnClone)
        if not allowCopy:
            btnCopy.Hide()
            btnDel.Hide()
            btnClone.Hide()
        btnsLayout.Add(btnOk, 0, wx.ALL, 5)
        btnsLayout.Add(btnCancel, 0, wx.ALL, 5)
        btnsLayout.Add(btnFillAll, 0, wx.ALL, 5)
        btnsLayout.Add(btnDel, 0, wx.ALL, 5)
        btnsLayout.Add(btnClone, 0, wx.ALL, 5)
        btnsLayout.Add(btnCopy, 0, wx.ALL, 5)
        mainLayout.Add(btnsLayout, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizer(mainLayout)
        self.Layout()
        # mainLayout.Fit(self)
        self.Centre(wx.BOTH)

    def OnCancel(self, event):
        """This method is called when the user click on the Cancel button. It
        simply ignores any data changes that the user did and close the form.

        Args:
            event: The event object from WX
        """
        super().Close()

    def OnOk(self, event):
        """This method is called when the user click on the Ok button. It
        loops on all grids in the form and commit the user changes. Finally it
        closes the form as well.

        Args:
            event: The event object from WX
        """
        for gt in self._gridTables:
            gt.Commit()
        super().Close()

    def OnFillAll(self, event):
        """This method is called when the user click on the Fill All button. It
        asks the grid to fill all years exactly with the data of the first
        year. Then it refresh the grid to view the new values.

        Args:
            event: The event object from WX
        """
        for gt in self._gridTables:
            gt.FillAll()
            msg = wx.grid.GridTableMessage(
                gt, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
            gt.GetView().ProcessTableMessage(msg)

    def OnCopy(self, event):
        """This method is called when the user click on the Copy button. The
        copy button allow the user to copy items from site to another. The
        method fires an event to notify the controller about the user action.

        Args:
            event: The event object from WX
        """
        pub.sendMessage(EVENTS.ITEM_COPY, item=self._dataItem)

    def OnClone(self, event):
        """This method is called when the user click on the Clone button. The
        clone button allow the user to clone items within the same site. The
        method fires an event to notify the controller about the user action.

        Args:
            event: The event object from WX
        """
        pub.sendMessage(EVENTS.ITEM_CLONE, item=self._dataItem)

    def OnDelete(self, event):
        """This method is called when the user click on the Delete button. The
        method asks for the user confirmation first, then it fires an event to
        notify the controller about the user action and finally it closes the
        form.

        Args:
            event: The event object from WX
        """
        s = wx.MessageBox('[Delete] Are you sure?', 'Warning',
                          wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if s == wx.OK:
            pub.sendMessage(EVENTS.ITEM_DELETE, item=self._dataItem)
            self.Close()

    def SetContent(self, content, align):
        """This method is called by the classes that inheret the basic form to
        populate the main layout of the form with the proper content.

        Args:
            - content: The layout to add to the form
            - align: The alignment direction (left, right or center)
        """
        self._contentLayout.Add(content, 1, wx.ALL | wx.EXPAND | align, 5)

    def SetDataItem(self, data):
        """This method is simply called to preserve the data of the item associated
        with the form.

        Args:
            data: The data of the selected item
        """
        self._dataItem = data

    def PopulateGrid(self, gridTable, dataPerYear):
        """This method is called to populate the a grid in the form with the
        proper data. The data is grouped per each defined year in our model.

        Args:
            - gridTable: The grid to populate
            - dataPerYear: The data of each defined year
        """
        self._gridTables.clear()
        self._gridTables.append(gridTable)
        self._grid = gridTable.GetView()
        # self._grid.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
        new = len(dataPerYear)
        cur = gridTable.GetNumberRows()
        msg = None
        if new > cur:  # new rows
            msg = wx.grid.GridTableMessage(
                gridTable, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, new-cur)
        elif new < cur:  # rows removed
            msg = wx.grid.GridTableMessage(
                gridTable, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, new, cur-new)

        if msg:
            gridTable.SetTableData(dataPerYear)
            gridTable.GetView().ProcessTableMessage(msg)

    def OnKeyPress(self, event):
        if event.ControlDown() and event.GetKeyCode() == 86:
            if not wx.TheClipboard.IsOpened():  # may crash, otherwise
                do = wx.TextDataObject()
                wx.TheClipboard.Open()
                success = wx.TheClipboard.GetData(do)
                wx.TheClipboard.Close()
                if success:
                    s = do.GetText()
                    s = str.replace(s, ',', '')
                    cells = s.split('\t')
                    row = self._grid.GetGridCursorRow()
                    col = self._grid.GetGridCursorCol()
                    for v in cells:
                        if col < self._grid.GetNumberCols():
                            self._grid.SetCellValue(row, col, v)
                            col += 1
