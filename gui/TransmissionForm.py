# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.grid
import DataConfig as config
import GridDataTable as gdt
import BasicForm as bf
import copy as cpy

from pubsub import pub
from Events import EVENTS


class TransmissionDialog (bf.BasicForm):
    """
    This form is used to add a new Transmission or edit an existing one. The
    form inherits from the BasicForm class.
    """

    _gridCols = config.DataConfig.TRANS_PARAMS

    def __init__(self, parent, controller):
        super().__init__(parent, "Transmission data", wx.Size(800, 550))
        contentLayout = wx.BoxSizer(wx.VERTICAL)

        layout0 = self.CreateGeneralLayout()

        h1 = wx.StaticBox(self, wx.ID_ANY, u"Parameters:")
        h1.SetForegroundColour('white')
        layout1 = wx.StaticBoxSizer(h1, wx.VERTICAL)
        # Grid and its data table
        self._gridTable1 = gdt.GridDataTable(self._gridCols)
        self._yearsGrid1 = wx.grid.Grid(h1, -1)
        self._yearsGrid1.SetTable(self._gridTable1, True)
        self._yearsGrid1.AutoSizeColumns(False)
        layout1.Add(self._yearsGrid1, 1, wx.ALL, 3)

        contentLayout.Add(layout0, 0, wx.ALL, 5)
        contentLayout.Add(layout1, 1, wx.ALL | wx.EXPAND, 1)
        super().SetContent(contentLayout, wx.ALIGN_CENTER_HORIZONTAL)

        self._controller = controller

    def CreateGeneralLayout(self):
        """This method is called to create the form layout itself, which is a
        grid table consist of a row for each defined year in our Reference
        Energy System.

        Return:
            The created layout
        """

        layout = wx.BoxSizer(wx.VERTICAL)

        # Name Part
        layout0 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(
            self, -1, "Transmission name:", size=wx.Size(120, -1))
        label.SetForegroundColour(wx.WHITE)
        layout0.Add(label, 0, wx.ALL, 5)
        self._txtTrnsmName = wx.TextCtrl(self, size=wx.Size(200, 25))
        layout0.Add(self._txtTrnsmName, 0, wx.ALL, 5)
        layout.Add(layout0, 0, wx.ALL, 5)
        #######################################################################

        #######################################################################
        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Site 1:", size=wx.Size(120, -1))
        label.SetForegroundColour(wx.WHITE)
        layout1.Add(label, 0, wx.ALL, 5)
        self._ddlSiteIn = wx.ComboBox(self, -1, size=wx.Size(200, 25),
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self._ddlSiteIn.Bind(wx.EVT_COMBOBOX, self.OnSiteChange)
        layout1.Add(self._ddlSiteIn, 0, wx.ALL, 5)
        layout.Add(layout1, 0, wx.ALL, 5)

        ###
        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Site 2:", size=wx.Size(120, -1))
        label.SetForegroundColour(wx.WHITE)
        layout1.Add(label, 0, wx.ALL, 5)
        self._ddlSiteOut = wx.ComboBox(self, -1, size=wx.Size(200, 25),
                                       style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self._ddlSiteOut.Bind(wx.EVT_COMBOBOX, self.OnSiteChange)
        layout1.Add(self._ddlSiteOut, 0, wx.ALL, 5)
        layout.Add(layout1, 0, wx.ALL, 5)

        ###
        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Commodity:", size=wx.Size(120, -1))
        label.SetForegroundColour(wx.WHITE)
        layout1.Add(label, 0, wx.ALL, 5)
        self._ddlComm = wx.ComboBox(self, -1, size=wx.Size(200, 25),
                                    style=wx.CB_DROPDOWN | wx.CB_READONLY)
        layout1.Add(self._ddlComm, 0, wx.ALL, 5)
        layout.Add(layout1, 0, wx.ALL, 5)

        return layout

    def OnSiteChange(self, event):
        """
        This method is triggered when the selected site is changed. The main
        purpose is to populate the commodities drop down list with the common
        commodities only between the selected sites.

        Args:
            event: The event object from WX
        """
        self._ddlComm.Clear()
        if not self._ddlSiteIn.GetValue() or not self._ddlSiteOut.GetValue():
            return
        elif self._ddlSiteIn.GetValue() == self._ddlSiteOut.GetValue():
            wx.MessageBox('Site out should not be the same as site in.',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        commList = self._controller.GetCommonCommodities(
                                            self._ddlSiteIn.GetValue(),
                                            self._ddlSiteOut.GetValue())

        if len(commList) > 0:
            self._ddlComm.SetItems(commList)
        else:
            wx.MessageBox(
                      'There is no common commodities between selected sites',
                      'Error', wx.OK | wx.ICON_ERROR)

    def PopulateTrans(self, trnsm, sitesList):
        """This method is called when the user try to Edit a transmission. The
       form is populated with the data of the selected transmission. It shows
       the transmission data and to which sites and commodity the transmission i
       s connected.

       Args:
           - trnsm: The transmission data
           - sitesList: List of all sites
       """
        self._orgTrnsm = cpy.deepcopy(trnsm)
        self._trnsm = trnsm
        self._txtTrnsmName.SetValue(trnsm['Name'])
        ##
        self._ddlSiteIn.SetItems(sitesList)
        self._ddlSiteIn.SetValue(trnsm['SiteIn'])
        self._ddlSiteOut.SetItems(sitesList)
        self._ddlSiteOut.SetValue(trnsm['SiteOut'])
        if trnsm['SiteIn'] and trnsm['SiteOut']:
            commList = self._controller.GetCommonCommodities(
                trnsm['SiteIn'], trnsm['SiteOut'])
            self._ddlComm.SetItems(commList)
            self._ddlComm.SetValue(trnsm['CommName'])
        ##
        super().PopulateGrid(self._gridTable1, trnsm['Years'])

    def OnOk(self, event):
        """This method is called when the user click Ok to save the transmission
        data. It makes sure that a Input site is selected, the output site is
        selected and the in and out sites are different sites. It gets the
        transmission info from the view and store it in the transmission data
        dictionary.  Finally, it notifies the controller that the user wants
        to save the transmission.

        Args:
            event: The event object from WX
        """
        if not self._ddlSiteIn.GetValue():
            wx.MessageBox('Please select a site in.',
                          'Error', wx.OK | wx.ICON_ERROR)
        elif not self._ddlSiteOut.GetValue():
            wx.MessageBox('Please select a site out.',
                          'Error', wx.OK | wx.ICON_ERROR)
        elif self._ddlSiteIn.GetValue() == self._ddlSiteOut.GetValue():
            wx.MessageBox('Site out should not be the same as site in.',
                          'Error', wx.OK | wx.ICON_ERROR)
        elif not self._ddlComm.GetValue():
            wx.MessageBox('Please select a commodity.',
                          'Error', wx.OK | wx.ICON_ERROR)
        else:
            self._trnsm['Name'] = self._txtTrnsmName.GetValue()
            self._trnsm['SiteIn'] = self._ddlSiteIn.GetValue()
            self._trnsm['SiteOut'] = self._ddlSiteOut.GetValue()
            self._trnsm['CommName'] = self._ddlComm.GetValue()
            self._gridTable1.Commit()
            pub.sendMessage(EVENTS.TRNSM_SAVE, data=self._trnsm)

    def OnCancel(self, event):
        """This method is called when the user click cancel to ignore the
        changes he/she did. The method store the transmission info and call the
        parent class OnCancel method.

        Args:
            event: The event object from WX
        """
        self._trnsm.update(self._orgTrnsm)
        super().OnCancel(event)
