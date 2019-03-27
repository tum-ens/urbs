# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 19:03:07 2018

@author: aelshaha
"""

import wx
import wx.lib.ogl as ogl
import RESShapes as res

from pubsub import pub
from Events import EVENTS


class TransmissionView(wx.Panel):

    def __init__(self, parent, controller):
        wx.Panel.__init__(self, parent)
        self._controller = controller
        self._shapes = {}
        # self.SetBackgroundColour("black")

        # manage layout
        mainLayout = wx.BoxSizer(wx.VERTICAL)
        barLayout = self.BuildToolBar()
        mainLayout.Add(barLayout, 0, wx.ALL | wx.EXPAND, 2)

        self.BuildCanvas()
        mainLayout.Add(self._canvas, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainLayout)
        self.Layout()
        self.Centre(wx.BOTH)

        pub.subscribe(self.RebuildTrnsm, EVENTS.TRNSM_ADDED)
        pub.subscribe(self.RebuildTrnsm, EVENTS.TRNSM_EDITED)
        pub.subscribe(self.OnItemMove, EVENTS.TRNSM_ITEM_MOVED)
# ----------------------------------------------------------------------------#

    def BuildToolBar(self):
        barLayout = wx.BoxSizer(wx.HORIZONTAL)

        actionsLayout = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, u"Actions:"), wx.HORIZONTAL)
        btnAddTrns = wx.Button(self, -1, "Add Transmission Line")
        btnAddTrns.Bind(wx.EVT_BUTTON, self.OnAddTrnsClick)
        actionsLayout.Add(btnAddTrns, 0, wx.ALL | wx.EXPAND, 2)

        barLayout.Add(actionsLayout, 1, wx.ALL | wx.EXPAND, 2)

        return barLayout
# ----------------------------------------------------------------------------#

    def OnAddTrnsClick(self, event):
        # print('OnAddTrnsClick')
        pub.sendMessage(EVENTS.TRNSM_ADDING)
# ----------------------------------------------------------------------------#

    def BuildCanvas(self):
        ogl.OGLInitialize()
        self._canvas = ogl.ShapeCanvas(self)
        maxWidth = 4000
        maxHeight = 2000
        self._canvas.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)
        self._canvas.SetBackgroundColour(wx.WHITE)
        self._diagram = ogl.Diagram()
        self._canvas.SetDiagram(self._diagram)
        self._diagram.SetCanvas(self._canvas)
        # self._canvas.Bind(wx.EVT_CHAR_HOOK, self.WhenAkeyIsPressed)

# ----------------------------------------------------------------------------#
    def RefreshCanvas(self):
        dc = wx.ClientDC(self._canvas)
        self._canvas.PrepareDC(dc)
        self._canvas.Redraw(dc)

# ----------------------------------------------------------------------------#
    def RebuildTrnsm(self, objId):
        # print('Inside Rebuild')
        self.RemoveAllShapes()

        self._trnsmXs = {}
        self.DrawCommodities()
        self.DrawTransmissions(objId)

        self.RefreshCanvas()
# ----------------------------------------------------------------------------#

    def RemoveAllShapes(self):
        dc = wx.ClientDC(self._canvas)
        self._canvas.PrepareDC(dc)
        for shape in self._diagram.GetShapeList():
            shape.Show(False)
            self._canvas.RemoveShape(shape)

        self._diagram.RemoveAllShapes()
        self._diagram.Clear(dc)
        self._canvas.Redraw(dc)
        # self._shapes.clear()
# ----------------------------------------------------------------------------#

    def DrawCommodities(self):
        x = 50
        prevSite = None
        commDict = self._controller.GetTrnsmCommodities()
        for k in sorted(commDict):
            data = commDict[k]
            site = k.split('.')[0]
            if not prevSite:
                prevSite = site
            if prevSite != site:
                self.DrawGroupArea(x)
                self._trnsmXs[site] = x
                prevSite = site
                x += 100

            commShape = res.CommodityShape(
                self._canvas, x, 10, k, k, data['Color'])
            self._shapes[k] = commShape
            x += 100
# ----------------------------------------------------------------------------#

    def DrawTransmissions(self, lastChangedTrnsm):
        y = 50
        transmissions = self._controller.GetTransmissions()
        for k in sorted(transmissions):
            t = transmissions[k]
            if k in self._shapes.keys():
                y = self._shapes[k].GetY()
            x = self._trnsmXs[max(t['SiteIn'], t['SiteOut'])]
            trnsmShape = res.ProcessShape(
                self._canvas, x, y, k, t['Name'], 'Trnsm')
            self._shapes[k] = trnsmShape
            lines = self.BuildTrnsmConnections(t, trnsmShape)
            self.DrawTrnsmConnections(trnsmShape, lines)
            trnsmShape.SetConnections(lines)
            if lastChangedTrnsm is None or k == lastChangedTrnsm:
                self.CheckCollision(trnsmShape)
# ----------------------------------------------------------------------------#

    def BuildTrnsmConnections(self, p, trnsmShape):
        lines = []
        inLines = self.BuildConnections(trnsmShape, p['IN'])
        outLines = self.BuildConnections(trnsmShape, p['OUT'])
        lines = inLines + outLines

        return lines
# ----------------------------------------------------------------------------#

    def BuildConnections(self, trnsmShape, commodities):
        lines = []
        lineY = trnsmShape.GetAttachY()
        for comm in commodities:
            commShape = self._shapes[comm]
            line = res.ConnectionShape(
                self._canvas, wx.ID_ANY, commShape.GetColor(), True)
            x1, x2 = 0, 0
            if commShape.GetX() > trnsmShape.GetX():
                x1 = trnsmShape.GetAttachX(True)
            else:
                x1 = trnsmShape.GetAttachX()
            x2 = commShape.GetX()
            line.SetEnds(x1, lineY, x2, lineY)
            lines.append(line)

        return lines
# ----------------------------------------------------------------------------#

    def DrawTrnsmConnections(self, trnsmShape, lines):
        # loop on lines and adjust Y
        leftLines = [l for l in lines if l.GetX() < trnsmShape.GetX()]
        rightLines = [l for l in lines if l.GetX() > trnsmShape.GetX()]
        # print(leftLines, rightLines)
        lineY = trnsmShape.GetAttachY()
        for line in leftLines:
            lineY += trnsmShape._hight / (len(leftLines)+1)
            line.SetEnds(line.GetEnds()[0], lineY, line.GetEnds()[2], lineY)

        lineY = trnsmShape.GetAttachY()
        for line in rightLines:
            lineY += trnsmShape._hight / (len(rightLines)+1)
            line.SetEnds(line.GetEnds()[0], lineY, line.GetEnds()[2], lineY)
# ----------------------------------------------------------------------------#

    def DrawGroupArea(self, x):
        # print('DrawGroupArea')
        line = ogl.LineShape()
        line.MakeLineControlPoints(2)
        line.SetEnds(x, 0, x, 2000)
        # self.SetDraggable(True, True)
        line.SetCanvas(self._canvas)
        line.SetPen(wx.Pen(wx.BLACK, 1, wx.DOT_DASH | wx.ALPHA_TRANSPARENT))
        # if brush:  shape.SetBrush(brush)
        self._diagram.AddShape(line)
        line.Show(True)
# ----------------------------------------------------------------------------#

    def OnItemMove(self, item):
        dc = wx.ClientDC(self._canvas)
        self._canvas.PrepareDC(dc)
        if item:
            trnsm = item
            lines = trnsm.GetConnections()
            self.DrawTrnsmConnections(trnsm, lines)
        self._diagram.Clear(dc)
        self._canvas.Redraw(dc)
# ----------------------------------------------------------------------------#

    def CheckCollision(self, trnsmShape):
        shapes = []
        for k, v in self._shapes.items():
            if v.GetType() in ('Trnsm') and k != trnsmShape.GetId():
                shapes.append(v)
        y = 50
        overlap = True
        while overlap:
            overlap = False
            for s in shapes:
                if y > s.GetAttachY() and y < s.GetAttachY()+s.GetHeight():
                    if trnsmShape.IsOverlapping(s):
                        # print('X overlap', y)
                        overlap = True
                        break
            if overlap:
                y += trnsmShape.GetHeight() + 10
            # print(y)
        trnsmShape.SetY(y)
        self.OnItemMove(trnsmShape)
# ----------------------------------------------------------------------------#

    def Refresh(self):
        # self.OnItemMove(None)
        self._canvas.Draw()
