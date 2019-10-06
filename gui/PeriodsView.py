# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.grid
import DataConfig as config
import GridDataTable as gdt

from Events import EVENTS
from pubsub import pub


class PeriodsView:
    """This module represent plot periods section in the Overview tab
    (GeneralView), which allow the user to add/remove plot periods to the
    system.
    """

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
        """This method just return the main layout of the view.
        """
        return self._mainLayout

    def TxtPeriodOnTextChange(self, event):
        """This method is triggered when the value in the plot period textbox
        changes. It enables the “Add Period” button if the text length is
        greater than zero, otherwise it keep the button disabled.

        Args:
             event: The event object from WX
        """
        txt = event.GetEventObject().GetValue()
        if len(txt) > 0:
            self._btnAdd.Enable()
        else:
            self._btnAdd.Disable()

    def BtnAddOnClick(self, event):
        """This method is called when the user click on the “Add Period” button.

            - It gets the value of the period name from the textbox
            - Trigger a notification that the user is trying to add the
              following period. This notification will be captured by the
              controller.

        Args:
             event: The event object from WX
        """
        newPeriod = self._txtPeriod.GetValue()
        pub.sendMessage(EVENTS.PERIOD_ADDING, period=newPeriod)

    def BtnRemoveOnClick(self, event):
        """
        This method is called when the user click on “Remove selected periods”
        button.
            - If the size of the grid is zero, then nothing to do
            - Loop on the grid rows and see if the row is selected (check box
              in the cell 0 of the current row)
            - If the row is selected, then add the period to “periods to remove”
              list.
            - Trigger a notification that the user is trying to remove the
              following periods. This notification will be captured by the
              controller.

        Args:
             event: The event object from WX
        """
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
        """This method is called when the notification “PeriodIsAdded” is
        triggered. In this case the view wants to notify the grid that some new
        rows are added. It simply send a message to the grid that X rows are
        appended. Where X is the total number of periods minus the current rows
        number in the grid.

        Args:
             periods: List of the added periods
        """
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
        """This method is called when the notification “PeriodsAreRemoved” is
        triggered. In this case the view wants to notify the grid that some
        existing rows are removed. It simply send a message to the grid with
        following information.
            - The total number of periods now (the new number of rows)
            - How many rows are removed

        Args:
             - periods: List of the current periods
             - removeCount: How many periods are removed
        """
        # tell the grid we've changed the data
        self._gridTable.SetTableData(periods)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,   # what we did to it
                   # how many
                   len(periods), removeCount
                   )
        self._gridTable.GetView().ProcessTableMessage(msg)
