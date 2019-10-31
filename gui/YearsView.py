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


class YearsView:
    """This module build the Years view, which allow the user to add/remove
    years to the system. It builds the view by adding the necessary elements as
    following:

    - The most outer box, which is labeled “Manage Years”. This is considered
      as the main layout.
    - The “Add year” box or layout, which contains the textbox and “Add” button
      that allow the user to enter a new year
    - The Grid that list the years and allow the user to specify the CO2 limit
      of each year.
    - Finally, the button “Remove selected Year(s)”, which allow the user to
      delete a year from the grid.

    This view subscribe on two notifications to update the view:

        - When a year is added. When the user press the “Add Year” button, we
          are not sure if the model will accept this year or not (for example,
          the year already exist) or any other kind of validation that the
          model do to verify the data. Thus, in this case, the view needs to
          subscribe on a notification that confirm that the year is added
          successfully to the system.
        - When year(s) are removed.
    """

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
        """This method just return the main layout of the view.
        """
        return self._mainLayout

    def TxtYearOnKeyPress(self, event):
        """This method is triggered when the user press a key to type something
        in the “Year” text box.
            - It accept that the user enter a digit “1234567890” in addition of
              course to back space, so the user can change the year he typed.
            - Zero is not allowed to be the first digit
            - Skip the event, means that the event is handled and stop the
              event propagation.

        Args:
             event: The event object from WX
        """
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
        """This method is triggered when the value in the year textbox changes.
        It enables the “Add year” button if the text length is 4, otherwise it
        keep the button disabled.

        Args:
             event: The event object from WX
        """
        txt = event.GetEventObject().GetValue()
        if len(txt) == 4:
            self._btnAdd.Enable()
        else:
            self._btnAdd.Disable()

    def BtnAddOnClick(self, event):
        """This method is called when the user click on the “Add Year” button.

            - It gets the value of the year from the textbox
            - Trigger a notification that the user is trying to add the
              following year. This notification will be captured by the
              controller.

        Args:
             event: The event object from WX
        """
        newYear = self._txtYear.GetValue()
        pub.sendMessage(EVENTS.YEAR_ADDING, year=newYear)

    def BtnRemoveOnClick(self, event):
        """This method is called when the user click on “Remove selected years”
        button.
            - If the size of the grid is zero, then nothing to do
            - Loop on the grid rows and see if the row is selected (check box
              in the cell 0 of the current row)
            - If the row is selected, then add the year to “years to remove”
              list.
            - Trigger a notification that the user is trying to remove the
              following years. This notification will be captured by the
              controller.

        Args:
             event: The event object from WX
        """
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
        """This method is called when the notification “YearIsAdded” is
        triggered. In this case the view wants to notify the grid that some new
        rows are added. It simply send a message to the grid that X rows are
        appended. Where X is the total number of years minus the current rows
        number in the grid.

        Args:
             years: List of the added years
        """
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
        """This method is called when the notification “YearsAreRemoved” is
        triggered. In this case the view wants to notify the grid that some
        existing rows are removed. It simply send a message to the grid with
        following information.
            - The total number of years now (the new number of rows)
            - How many rows are removed

        Args:
             - years: List of the current years
             - removeCount: How many years are removed
        """
        # tell the grid we've changed the data
        self._gridTable.SetTableData(years)
        msg = wx.grid.GridTableMessage(
                   self._gridTable,                         # The table
                   wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,   # what we did to it
                   len(years), removeCount                  # how many
              )
        self._gridTable.GetView().ProcessTableMessage(msg)
