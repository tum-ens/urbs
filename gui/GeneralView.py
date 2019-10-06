# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import YearsView as yv
import SitesView as sv
import GlobalsView as gv


class GeneralView(wx.Panel):
    """This module simply create the content of the Overview tab. It consists
    of 3 other modules:

    - SitesView, which allow the user to add/remove sites to the system
    - YearsView, which allow the user to add/remove years to model in the syste,
    - GlobalsView, which create the rest of the components in the overview tab.

        - Manage periods section (PeriodsView)
        - Manage global parameters.
        - Select Senarios to execute.
        - Finally, the run/abort buttons and the log area.
    You will notice that SitesView, YearsView and PeriodsView are exactly the
    same, just labels are changed and the grid columns. Each grid, has its
    columns definition and this definition is stored in the DataConfig Module
    as we will see later.
    """

    def __init__(self, parent, controller):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour("black")
        # self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        yearsView = yv.YearsView(self)
        yearsLayout = yearsView.GetLayout()

        sitesView = sv.SitesView(self)
        sitesLayout = sitesView.GetLayout()

        globalsLayout = gv.GlobalsView(self, controller).GetLayout()

        mainLayout = wx.BoxSizer(wx.HORIZONTAL)
        vLayout = wx.BoxSizer(wx.VERTICAL)
        vLayout.Add(sitesLayout, 1, wx.ALL | wx.EXPAND, 5)
        vLayout.Add(yearsLayout, 1, wx.ALL | wx.EXPAND, 5)
        mainLayout.Add(vLayout, 0, wx.ALL | wx.EXPAND, 1)
        mainLayout.Add(globalsLayout, 1, wx.ALL | wx.EXPAND, 1)

        self.SetSizer(mainLayout)
        self.Layout()
        self.Centre(wx.BOTH)
