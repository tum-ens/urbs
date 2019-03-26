# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 21:50:21 2018

@author: aelshaha
"""

import wx
import wx.lib.ogl as ogl
import RESEvtHandler as evt


class ProcessShape(ogl.RectangleShape):
    def __init__(self, canvas, x, y, uuid, text, pType):
        self._width = 150
        self._hight = 45
        ogl.RectangleShape.__init__(self, self._width, self._hight)
        self.SetDraggable(True, False)
        self.SetCanvas(canvas)
        self.SetX(x)
        self.SetY(y)
        self.SetPen(wx.BLACK_PEN)
        self.SetBrush(wx.WHITE_BRUSH)
        if text:
            self.AddText(text)
        if pType == 'Storage':
            self.SetCornerRadius(-0.3)
        # shape.SetShadowMode(ogl.SHADOW_RIGHT)
        self.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        canvas.GetDiagram().AddShape(self)
        self.Show(True)

        evthandler = evt.RESEvtHandler(self)
        self.SetEventHandler(evthandler)

        self._uuid = uuid
        self._connections = []
        self._subType = pType
        self._minX = 0
        self._maxX = 0

    def GetId(self):
        return self._uuid

    def GetType(self):
        if self._subType:
            return self._subType

        return 'Process'

    def GetAttachX(self, forward=False):
        if forward:
            return self.GetX() + self._width/2

        return self.GetX() - self._width/2

    def GetAttachY(self):
        return self.GetY() - self._hight/2

    def SetConnections(self, lines):
        self._connections = lines
        xs = []
        xs.append(self.GetAttachX())
        xs.append(self.GetAttachX(True))
        for l in lines:
            x1 = l.GetEnds()[0]
            x2 = l.GetEnds()[2]
            xs.append(x1)
            xs.append(x2)
        xs = sorted(xs)
        # print(xs)
        self._minX = xs[0]
        self._maxX = xs[-1]

    def GetConnections(self):
        return self._connections

    def IsOverlapping(self, p):
        # print(self._minX, self._maxX)
        # print(p._minX, p._maxX)
        overlap = False
        if p._minX >= self._minX and p._minX < self._maxX:
            overlap = True
        elif p._maxX > self._minX and p._maxX <= self._maxX:
            overlap = True
        elif p._minX < self._minX and p._maxX > self._minX:
            overlap = True

        return overlap


class CommodityShape(ogl.LineShape):
    def __init__(self, canvas, x, y, uuid, text, color):
        ogl.LineShape.__init__(self)
        self.MakeLineControlPoints(2)
        self.SetEnds(x, y, x, 2000)
        # self.SetDraggable(True, True)
        self.SetCanvas(canvas)
        self._color = color
        self.SetPen(wx.Pen(color, 0.5, wx.SOLID))
        # if brush:  shape.SetBrush(brush)
        if text:
            # self.AddText(text)
            self.SetFormatMode(ogl.FORMAT_SIZE_TO_CONTENTS, 1)
            self.FormatText(wx.ClientDC(canvas), text, 1)  # start
        # shape.SetShadowMode(ogl.SHADOW_RIGHT)
        self.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        canvas.GetDiagram().AddShape(self)
        self.Show(True)

        evthandler = evt.RESEvtHandler(self)
        self.SetEventHandler(evthandler)

        self._uuid = uuid

    def GetId(self):
        return self._uuid

    def GetType(self):
        return 'Commodity'

    def GetGroup(self):
        return self._uuid[0]

    def GetColor(self):
        return self._color


class ConnectionShape(ogl.LineShape):
    def __init__(self, canvas, uuid, color, isDblArrow=False):
        ogl.LineShape.__init__(self)
        self.MakeLineControlPoints(2)
        self.AddArrow(ogl.ARROW_ARROW, size=6)
        if isDblArrow:
            self.AddArrow(ogl.ARROW_ARROW, ogl.ARROW_POSITION_START, 6)
        # self.SetDraggable(True, True)
        self.SetCanvas(canvas)
        self.SetPen(wx.Pen(color, 0.5, wx.SOLID))
        self.SetBrush(wx.Brush(color))
        # shape.SetShadowMode(ogl.SHADOW_RIGHT)
        canvas.GetDiagram().AddShape(self)
        self.Show(True)

        self._uuid = uuid

    def GetId(self):
        return self._uuid
