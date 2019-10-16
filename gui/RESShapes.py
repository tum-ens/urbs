# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.lib.ogl as ogl
import RESEvtHandler as evt


class ProcessShape(ogl.RectangleShape):
    """
    This class represent the process shape that we draw in the views.
    """

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
        """
        This method is called to get the id of the shape.

        Returns:
            The uuid of the shape
        """
        return self._uuid

    def GetType(self):
        """
        This method is called to get the type of the shape.

        Returns:
            Process or Storage
        """
        if self._subType:
            return self._subType

        return 'Process'

    def GetAttachX(self, forward=False):
        """
        This method is called to get the X coordination of the shape. The
        forward arguments means if you want to get the x to the left or the
        right edge of the shape.

        Args:
            forward: to the right of the shape or not

        Returns:
            The X position of the shape
        """
        if forward:
            return self.GetX() + self._width/2

        return self.GetX() - self._width/2

    def GetAttachY(self):
        """
        This method is called to get the Y coordination of the shape.

        Returns:
            The Y position of the shape
        """
        return self.GetY() - self._hight/2

    def SetConnections(self, lines):
        """
        This method is called to set the connections (lines) associated with
        this process/storage shape. Based on that, it also calculate the min and
        max X for drawing all connections. This will be used to detect the
        collision and overlapping of the shapes.

        Args:
             lines: The list of connections
        """
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
        """
        This method is called to get the list of connections (lines) associated
        with the process/storage shape.

        Returns:
            The list of connections
        """
        return self._connections

    def IsOverlapping(self, p):
        """
        This method is called to check if two processes are overlapping or not
        for their drawing area.

        Args:
            p: The process to check against

        Returns:
            Overlapping or not
        """
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
    """
    This class represent the commodity shape that we draw in the views.
    """

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
        """
        This method is called to get the id of the shape.

        Returns:
            The uuid of the shape
        """
        return self._uuid

    def GetType(self):
        """
        This method is called to get the type of the shape.

        Returns:
            Commodity
        """
        return 'Commodity'

    def GetGroup(self):
        """
        This method is called to get the group that the commodity belongs to.

        Returns:
            The first char of the shape uuid, which is 0, 1 or 2.
        """
        return self._uuid[0]

    def GetColor(self):
        """
        This method is called to get the color of the commodity.

        Returns:
            The color of the commodity
        """
        return self._color


class ConnectionShape(ogl.LineShape):
    """
    This class represent the connection shape (between the commodity and the
    process/storage) that we draw in the views.
    """

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
        """
        This method is called to get the id of the shape.

        Returns:
            The uuid of the shape
        """
        return self._uuid
