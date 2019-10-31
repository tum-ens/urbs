# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import copy as cpy
import Errors as ERR

from pubsub import pub
from Events import EVENTS


class SitesDialog (wx.Dialog):
    """
    This form is shown to the user when he/she try to copy an item from site to
    another one. It shows a list of sites so the user can select to which
    sites(s) he/she wants to copy the item. The item can be a Commodity,
    Process or Storage.
    """

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
        """This method is called when the user click on the Cancel button. It
        simply ignores any data changes that the user did and close the form.

        Args:
            event: The event object from WX
        """
        self.Close()

    def OnSelectAll(self, event):
        """This method simply select all sites on the form. It means the user
        wants to copy the item to all other sites.

        Args:
            event: The event object from WX
        """
        self._lb.SetCheckedStrings(self._sites)

    def OnOk(self, event):
        """This method is called when the user click Ok in the form. If there's
        at least one site is selected, it fire an even that an item is copied
        (this event will be captured by the controller), then it closes the
        form. Otherwise, it shows an error that at least one site should be
        selected.

        Args:
            event: The event object from WX
        """
        sites = self._lb.GetCheckedStrings()
        if len(sites) > 0:
            pub.sendMessage(EVENTS.ITEM_COPIED,
                            item=cpy.deepcopy(self._item), sites=sites)
            self.Close()
        else:
            wx.MessageBox(ERR.ERRORS[ERR.NO_SITE_SEL],
                          'Error', wx.OK | wx.ICON_ERROR)
