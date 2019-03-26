# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 02:56:46 2018

@author: aelshaha
"""

import wx
import copy as cpy
import Errors as ERR

from pubsub import pub
from Events import EVENTS


class SitesDialog (wx.Dialog):

    def __init__(self, parent, sites, item):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY,
                           title="Select Sites", size=wx.Size(400, 300))
        self.SetBackgroundColour("black")

        self._item = item
        self._sites = sites
        self._lb = wx.CheckListBox(self, -1, choices=sites)

        btnsLayout = wx.BoxSizer(wx.HORIZONTAL)
        btnOk = wx.Button(self, label="Ok")
        btnOk.Bind(wx.EVT_BUTTON, self.OnOk)
        btnCancel = wx.Button(self, label="Cancel")
        btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        btnAll = wx.Button(self, label="Select All")
        btnAll.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        btnsLayout.Add(btnOk, 0, wx.ALL, 5)
        btnsLayout.Add(btnCancel, 0, wx.ALL, 5)
        btnsLayout.Add(btnAll, 0, wx.ALL, 5)

        mainLayout = wx.BoxSizer(wx.VERTICAL)
        mainLayout.Add(self._lb, 1, wx.ALL | wx.EXPAND, 5)
        mainLayout.Add(btnsLayout, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizer(mainLayout)
        self.Layout()
        # mainLayout.Fit(self)
        self.Centre(wx.BOTH)

    def OnCancel(self, event):
        self.Close()

    def OnSelectAll(self, event):
        self._lb.SetCheckedStrings(self._sites)

    def OnOk(self, event):
        sites = self._lb.GetCheckedStrings()
        if len(sites) > 0:
            pub.sendMessage(EVENTS.ITEM_COPIED,
                            item=cpy.deepcopy(self._item), sites=sites)
            self.Close()
        else:
            wx.MessageBox(ERR.ERRORS[ERR.NO_SITE_SEL],
                          'Error', wx.OK | wx.ICON_ERROR)
