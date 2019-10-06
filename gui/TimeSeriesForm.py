# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.richtext as rt


class TimeSeriesForm(wx.Dialog):
    """
    This module represent the time series form. It allow the user to enter the
    time index data for a certain year for certain commodity.
    """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY,
                           title="Time Series", size=wx.Size(300, 450))
        self.SetBackgroundColour("black")

        mainLayout = wx.BoxSizer(wx.VERTICAL)
        self._lblCommName = wx.StaticText(self, -1, "Name: ")
        self._lblCommName.SetForegroundColour(wx.WHITE)
        self._lblYear = wx.StaticText(self, -1, "Year: ")
        self._lblYear.SetForegroundColour(wx.WHITE)
        self._txtTS = rt.RichTextCtrl(
            self, wx.ID_ANY, size=wx.Size(250, 300), style=wx.VSCROLL)

        btnsLayout = wx.BoxSizer(wx.HORIZONTAL)
        btnOk = wx.Button(self, label="Ok")
        btnOk.Bind(wx.EVT_BUTTON, self.OnOk)
        btnCancel = wx.Button(self, label="Cancel")
        btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        btnsLayout.Add(btnOk, 0, wx.ALL, 5)
        btnsLayout.Add(btnCancel, 0, wx.ALL, 5)

        mainLayout.Add(self._lblCommName, 0, wx.ALL, 5)
        mainLayout.Add(self._lblYear, 0, wx.ALL, 5)
        mainLayout.Add(self._txtTS, 0, wx.ALL, 5)
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
        self.Close()

    def OnOk(self, event):
        """This method is called when the user click on the Ok button. It saves
        the time series data that the user entered. It replace the new line
        character by a pipe so we can store the data in the config file as one
        line.

        Args:
            event: The event object from WX
        """
        s = self._txtTS.GetValue()
        s = str.replace(s, '\r', '')
        s = str.replace(s, '\n', '|')
        s = s.strip('|')
        # print(len(s.split('|')))
        self._gt.SetValue(self._row, self._col, s)
        self.Close()

    def PopulateData(self, commName, gt, row, col):
        """This method is triggered when the user want to edit the time series
        data he/she already entered before for specific year of specific
        commodity.

        Args:
            - commName: The commodity name
            - gt: The grid table
            - row: which row of the grid is clicked (year)
            - col: The col that contains the time series data
        """
        self._lblCommName.SetLabelText(
            self._lblCommName.GetLabelText() + commName)
        self._lblYear.SetLabelText(
            self._lblYear.GetLabelText() + gt.GetRowLabelValue(row))

        s = gt.GetValue(row, col)
        s = str.replace(s, '|', '\n')
        self._txtTS.SetValue(s)
        self._gt, self._row, self._col = gt, row, col
