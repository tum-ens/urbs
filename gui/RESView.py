# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 11:07:15 2018

@author: aelshaha
"""

import wx
import wx.lib.ogl as ogl
import RESShapes as res
import DataConfig as cfg

from pubsub import pub
from Events import EVENTS


class RESView(wx.Panel):

    _actions = {1: {'Name': 'SupIm', 'ImgPath': 'Solar_WE_10.png'},
                2: {'Name': 'Buy', 'ImgPath': 'Buy.png'},
                #######################################################
                3: {'Name': 'Stock', 'ImgPath': 'Gas.png'},
                #######################################################
                4: {'Name': 'Demand', 'ImgPath': 'Elec.png'},
                5: {'Name': 'Sell', 'ImgPath': 'Sell.png'},
                6: {'Name': 'Env', 'ImgPath': 'Env.png'},
                #######################################################
                10: {'Name': 'Process', 'ImgPath': 'Process.png'},
                11: {'Name': 'Storage', 'ImgPath': 'Storage.png'},
                }

    def __init__(self, parent, controller, siteName):
        wx.Frame.__init__(self, parent)
        self._controller = controller
        self._siteName = siteName
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

        pub.subscribe(self.RebuildRES, EVENTS.COMMODITY_ADDED + self._siteName)
        pub.subscribe(self.RebuildRES,
                      EVENTS.COMMODITY_EDITED + self._siteName)
        pub.subscribe(self.RebuildRES, EVENTS.PROCESS_ADDED + self._siteName)
        pub.subscribe(self.RebuildRES, EVENTS.PROCESS_EDITED + self._siteName)
        pub.subscribe(self.RebuildRES, EVENTS.ITEM_DELETED + self._siteName)

        pub.subscribe(self.OnItemMove, EVENTS.ITEM_MOVED + self._siteName)
# ----------------------------------------------------------------------------#

    def GetSiteName(self):
        return self._siteName
# ----------------------------------------------------------------------------#

    def BuildToolBar(self):
        barLayout = wx.BoxSizer(wx.HORIZONTAL)

        actionsLayout = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, u"Actions:"), wx.HORIZONTAL)
        tb = wx.ToolBar(actionsLayout.GetStaticBox(), -1,
                        style=wx.TB_HORIZONTAL | wx.TB_FLAT)
        for key, val in self._actions.items():
            res_path = cfg.DataConfig.resource_path('imgs/' + val['ImgPath'])
            img = wx.Image(res_path, wx.BITMAP_TYPE_ANY)
            # img = img.Scale(32, 32)
            tooltip = val['Name']
            if key % 10 == 0:
                tb.AddSeparator()
            tb.AddTool(
                key,
                tooltip,
                wx.Bitmap(img),
                wx.NullBitmap,
                wx.ITEM_NORMAL,
                tooltip,
                "Add new '" +
                tooltip +
                "'",
                None)

        tb.Bind(wx.EVT_TOOL, self.OnToolClick)
        actionsLayout.Add(tb, 1, wx.ALL | wx.EXPAND, 2)
        tb.Realize()

        barLayout.Add(actionsLayout, 1, wx.ALL | wx.EXPAND, 2)

        return barLayout
# ----------------------------------------------------------------------------#

    def OnToolClick(self, event):
        # print("tool %s clicked\n" % event.GetId())
        if event.GetId() == 10:
            pub.sendMessage(EVENTS.PROCESS_ADDING)
        elif event.GetId() == 11:
            pub.sendMessage(EVENTS.STORAGE_ADDING)
        else:
            commType = self._actions[event.GetId()]['Name']
            pub.sendMessage(EVENTS.COMMODITY_ADDING, commType=commType)
# ----------------------------------------------------------------------------#

    def BuildCanvas(self):
        ogl.OGLInitialize()
        self._canvas = ogl.ShapeCanvas(self)
        maxWidth = 4000
        maxHeight = 2000
        self._canvas.SetScrollbars(20, 20, maxWidth / 20, maxHeight / 20)
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
    def RebuildRES(self, objId):
        # print('Inside Rebuild')
        self.RemoveAllShapes()
        self.DrawCommodities()
        self.DrawProcesses(objId)

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
        x = 60
        prevGrp = '0'
        prevCommHasProc = False
        commDict = self._controller.GetCommodities(self._siteName)
        for k in sorted(commDict):
            data = commDict[k]
            if prevGrp != data['Group']:
                if prevCommHasProc:
                    x -= 100
                self.DrawGroupArea(x)
                prevGrp = data['Group']
                x += 100

            commShape = res.CommodityShape(
                self._canvas, x, 10, k, data['Name'], data['Color'])
            self._shapes[k] = commShape
            processes = self._controller.GetLinkedProcesses(self._siteName, k)
            if len(processes) > 0:
                x += 25 + 150 + 25
                prevCommHasProc = True
            else:
                x += 100
                prevCommHasProc = False
# ----------------------------------------------------------------------------#

    def DrawProcesses(self, lastChangedProcess):
        commDict = self._controller.GetCommodities(self._siteName)
        for commId in sorted(commDict):
            x = self._shapes[commId].GetX() + 100
            y = 50
            processes = self._controller.GetLinkedProcesses(
                self._siteName, commId)
            for k in sorted(processes):
                p = processes[k]
                if k in self._shapes.keys():
                    y = self._shapes[k].GetY()
                procShape = res.ProcessShape(
                    self._canvas, x, y, k, p['Name'], p['Type'])
                self._shapes[k] = procShape
                lines = self.BuildProcConnections(p, procShape)
                self.DrawProcConnections(procShape, lines)
                procShape.SetConnections(lines)
                if lastChangedProcess is None or k == lastChangedProcess:
                    self.CheckCollision(procShape)
# ----------------------------------------------------------------------------#

    def BuildProcConnections(self, p, procShape):
        lines = []
        lineY = procShape.GetAttachY()
        # Draw in (always from left to right)
        isDblArrow = (p['Type'] == 'Storage')
        for inComm in p['IN']:
            commShape = self._shapes[inComm]
            line = res.ConnectionShape(
                self._canvas, wx.ID_ANY, commShape.GetColor(), isDblArrow)
            line.SetEnds(commShape.GetX(), lineY,
                         procShape.GetAttachX(), lineY)
            lines.append(line)
        # Draw out
        for outComm in p['OUT']:
            commShape = self._shapes[outComm]
            line = res.ConnectionShape(
                self._canvas, wx.ID_ANY, commShape.GetColor())
            x1, x2 = 0, 0
            if commShape.GetX() > procShape.GetX():
                x1 = procShape.GetAttachX(True)
            else:
                x1 = procShape.GetAttachX()
            x2 = commShape.GetX()
            line.SetEnds(x1, lineY, x2, lineY)
            lines.append(line)

        return lines
# ----------------------------------------------------------------------------#

    def DrawProcConnections(self, procShape, lines):
        # loop on lines and adjust Y
        leftLines = [l for l in lines if l.GetX() < procShape.GetX()]
        rightLines = [l for l in lines if l.GetX() > procShape.GetX()]
        # print(leftLines, rightLines)
        lineY = procShape.GetAttachY()
        for line in leftLines:
            lineY += procShape._hight / (len(leftLines) + 1)
            line.SetEnds(line.GetEnds()[0], lineY, line.GetEnds()[2], lineY)

        lineY = procShape.GetAttachY()
        for line in rightLines:
            lineY += procShape._hight / (len(rightLines) + 1)
            line.SetEnds(line.GetEnds()[0], lineY, line.GetEnds()[2], lineY)
# ----------------------------------------------------------------------------#

    def DrawGroupArea(self, x):
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
            process = item
            lines = process.GetConnections()
            self.DrawProcConnections(process, lines)
        self._diagram.Clear(dc)
        self._canvas.Redraw(dc)
# ----------------------------------------------------------------------------#

    def CheckCollision(self, procShape):
        shapes = []
        for k, v in self._shapes.items():
            if (
                v.GetType() in ('Process', 'Storage') and
                k != procShape.GetId()
            ):
                shapes.append(v)
        y = 50
        overlap = True
        while overlap:
            overlap = False
            for s in shapes:
                if y > s.GetAttachY() and y < s.GetAttachY() + s.GetHeight():
                    # print('Y overlap', y)
                    if procShape.IsOverlapping(s):
                        # print('X overlap', y)
                        overlap = True
                        break
            if overlap:
                y += procShape.GetHeight() + 10
            # print(y)
        procShape.SetY(y)
        self.OnItemMove(procShape)
# ----------------------------------------------------------------------------#

    def Refresh(self):
        # self.OnItemMove(None)
        self._canvas.Draw()
