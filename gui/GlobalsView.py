# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 23:59:15 2018

@author: aelshaha
"""

import wx
import wx.grid
import sys
import DataConfig as config
import GridDataTable as gdt
import PeriodsView as pv
import wx.richtext as rt

from Events import EVENTS
from pubsub import pub


class RedirectText(object):

    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self, string):
        wx.CallAfter(self.out.WriteText, string)
        # self.out.WriteText(string)

    def flush(self):
        # self.out.flush()
        pass


class GlobalsView():

    _gridCols = config.DataConfig.GLOBAL_COLS
    _gridRows = config.DataConfig.GLOBAL_PARAMS

    def __init__(self, parent, controller):
        self._parent = parent
        self._controller = controller

        gridLayout = wx.BoxSizer(wx.HORIZONTAL)
        # Periods Section
        periodsView = pv.PeriodsView(parent)
        gridLayout.Add(periodsView.GetLayout(), 0, wx.ALL | wx.EXPAND, 1)
        # Global Params Section
        layout = self.CreateGlobalParamsLayout()
        gridLayout.Add(layout, 0, wx.ALL | wx.EXPAND, 1)
        # Scenarios Section
        layout = self.CreateScenariosLayout()
        gridLayout.Add(layout, 1, wx.ALL | wx.EXPAND, 1)

        imgLayout = self.CreateImgsLayout()
        logLayout = self.CreateLogLayout()
        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(logLayout, 1, wx.ALL | wx.EXPAND, 5)
        layout.Add(imgLayout, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self._mainLayout = wx.BoxSizer(wx.VERTICAL)
        self._mainLayout.Add(gridLayout, 1, wx.ALL | wx.EXPAND, 5)
        self._mainLayout.Add(layout, 1, wx.ALL | wx.EXPAND, 0)

        pub.subscribe(self.PopulateGrid, EVENTS.GL_PARAMS_LOADED)
        pub.subscribe(self.PopulateScenarios, EVENTS.SCENARIOS_LOADED)

        redirStd = RedirectText(self._logCtrl)
        sys.stdout = redirStd
        sys.stderr = redirStd

    def GetLayout(self):
        return self._mainLayout

    def CreateGlobalParamsLayout(self):
        # Grid and its data table
        self._gridTable = gdt.GridDataTable(
            self._gridCols, self._gridRows, autoCommit=True)
        self._gridTable.SetTableData(self._controller.GetGlobalParams())
        self._glGrid = wx.grid.Grid(self._parent, -1)
        self._glGrid.SetTable(self._gridTable, True)
        self._glGrid.SetColSize(0, 120)
        self._glGrid.SetRowLabelSize(150)
        self._glGrid.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)

        label = wx.StaticText(self._parent, -1,
                              "Result directory: \n%s" %
                              config.DataConfig.RESULT_DIR)
        label.SetForegroundColour(wx.WHITE)
        label.SetFont(wx.Font(11, wx.DECORATIVE, wx.NORMAL, wx.BOLD))

        headerBox = wx.StaticBox(
            self._parent, wx.ID_ANY, u"Manage Global Parameters:")
        headerBox.SetForegroundColour('white')
        layout = wx.StaticBoxSizer(headerBox, wx.VERTICAL)
        layout.Add(self._glGrid, 1, wx.ALL | wx.EXPAND, 5)
        layout.Add(label, 0, wx.ALL, 5)
        return layout

    def CreateScenariosLayout(self):
        self._lb = wx.CheckListBox(
            self._parent, -1, choices=self._controller.GetScenarios())
        self._lb.Bind(wx.EVT_CHECKLISTBOX, self.OnScenarioChange)
        headerBox = wx.StaticBox(self._parent, wx.ID_ANY, u"Select Scenarios:")
        headerBox.SetForegroundColour('white')
        layout = wx.StaticBoxSizer(headerBox, wx.HORIZONTAL)
        layout.Add(self._lb, 1, wx.ALL | wx.EXPAND, 5)
        return layout

    def CreateLogLayout(self):
        self._logCtrl = rt.RichTextCtrl(self._parent, wx.ID_ANY, size=(
            300, 100), style=rt.RE_MULTILINE | rt.RE_READONLY | wx.VSCROLL)
        sb = wx.StaticBox(self._parent, wx.ID_ANY, u"Log:")
        sb.SetForegroundColour('white')
        logLayout = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        logLayout.Add(self._logCtrl, 1, wx.ALL | wx.EXPAND, 5)
        return logLayout

    def CreateImgsLayout(self):
        imgLayout = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.Bitmap(config.DataConfig.resource_path(
            "imgs/Play.png"), wx.BITMAP_TYPE_ANY)
        btnRun = wx.BitmapButton(
            self._parent,
            wx.ID_ANY,
            bitmap,
            wx.DefaultPosition,
            (132,
             132),
            wx.BU_AUTODRAW | wx.RAISED_BORDER)
        btnRun.Bind(wx.EVT_BUTTON, self.OnRunClick)
        imgLayout.Add(btnRun, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        bitmap = wx.Bitmap(config.DataConfig.resource_path(
            "imgs/Abort.png"), wx.BITMAP_TYPE_ANY)
        btnAbort = wx.BitmapButton(
            self._parent,
            wx.ID_ANY,
            bitmap,
            wx.DefaultPosition,
            (132,
             132),
            wx.BU_AUTODRAW | wx.RAISED_BORDER)
        imgLayout.Add(btnAbort, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        return imgLayout

    def OnRunClick(self, event):
        if not self._controller.ValidateData():
            return

        self._logCtrl.Clear()
        wx.Yield()
        dlg = wx.ProgressDialog("Run",
                                "Please wait, this could take few minutes...",
                                maximum=10,
                                parent=self._parent,
                                style=0 |
                                wx.PD_APP_MODAL |
                                # | wx.PD_CAN_ABORT
                                # | wx.PD_CAN_SKIP
                                wx.PD_ELAPSED_TIME |
                                # | wx.PD_ESTIMATED_TIME
                                # | wx.PD_REMAINING_TIME
                                wx.PD_AUTO_HIDE
                                )
        dlg.Update(5)
        try:
            self._controller.Run()
        except BaseException:
            dlg.Destroy()
            raise
        dlg.Update(10)
        dlg.Destroy()

    def OnScenarioChange(self, event):
        index = event.GetSelection()
        lb = event.GetEventObject()
        label = lb.GetString(index)
        if lb.IsChecked(index):
            pub.sendMessage(EVENTS.SCENARIO_ADDED, scName=label)
        else:
            pub.sendMessage(EVENTS.SCENARIO_REMOVED, scName=label)

    def PopulateGrid(self, gl):
        self._gridTable.SetTableData(gl)
        msg = wx.grid.GridTableMessage(
            self._gridTable,
            wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self._gridTable.GetView().ProcessTableMessage(msg)

    def PopulateScenarios(self, scenarios):
        self._lb.SetCheckedStrings(scenarios)
