# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.lib.ogl as ogl
import RESShapes as res

from pubsub import pub
from Events import EVENTS


class TransmissionView(wx.Panel):
    """This module represent the Transmission view (tab) in our solution. It
    allows the user to define the transmission lines that connect different
    sites. The connected sites should share at least one common commodity so
    they can be connected.
    """

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
        """
        This method is called to build the tool bar in the transmision view,
        which is just a button to add a new transmission line.

        Returns:
            The tool bar layout
        """
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
        """
        This method is triggered when the user want to add a new transmission
        line. It just fire an event for the controller to open the Transmission
        form for the user.

        Args:
             event: The event object from WX
        """
        # print('OnAddTrnsClick')
        pub.sendMessage(EVENTS.TRNSM_ADDING)
# ----------------------------------------------------------------------------#

    def BuildCanvas(self):
        """
        This method is called to initialize the canvas for drawing the shapes.
        """
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
        """
        This method is called to refresh the view and redraw the whole canvas.
        """
        dc = wx.ClientDC(self._canvas)
        self._canvas.PrepareDC(dc)
        self._canvas.Redraw(dc)

# ----------------------------------------------------------------------------#
    def RebuildTrnsm(self, objId):
        """
        This method is called to rebuild (redraw) the transmission on the
        canvas.

        Args:
            objId: The last added transmission
        """
        # print('Inside Rebuild')
        self.RemoveAllShapes()

        self._trnsmXs = {}
        self.DrawCommodities()
        self.DrawTransmissions(objId)

        self.RefreshCanvas()
# ----------------------------------------------------------------------------#

    def RemoveAllShapes(self):
        """
        This method is called to remove all shapes from the view.
        """
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
        """
        This method is called to draw the commodities shapes on the view. It
        loops on all commodities and add a shape for each one. When the function
        encounter a new site, it start drawing a new area labeled with the site
        name.
        """
        x = 100
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
        """
        This method is called to draw the transmission shapes on the view. It
        loops on all transmission lines and create a shape for each one
        (rectangle on the canvas)

        Args:
            lastChangedTrnsm: The last added transmission
        """
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
        """
        This method just calling BuildConnections method twice. One for the IN
        Commodities and the 2nd call for the OUT ones.

        Args:
            - p: The transmission object data
            - trnsmShape: The transmission shape (in the drawing)

        Returns:
            List of connections (connection shapes)
        """
        lines = []
        inLines = self.BuildConnections(trnsmShape, p['IN'])
        outLines = self.BuildConnections(trnsmShape, p['OUT'])
        lines = inLines + outLines

        return lines
# ----------------------------------------------------------------------------#

    def BuildConnections(self, trnsmShape, commodities):
        """
        This method is called to get the connections (lines) that connect the
        commodities from different sites through the the transmission lines.

        Args:
            - trnsmShape: The transmission line (shape)
            - commodities: List of commodities

        Returns:
            List of connections (connection shapes)
        """
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
        """
        This method is called to draw the connections (lines) connected to a
        certain transmission line. The lines could be to the left and/or the
        right of the transmission shape.

        Args:
            - trnsmShape: The transmission line
            - lines: list of connections to draw
        """
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
        """
        The transmission view split to areas. This method is called to draw a
        new group area (vertical line) starting from point x.

        Args:
            x: The x coordinate
        """
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
        """
        This method is triggered when the user try to drag and move a
        transmission line. It keep redrawing the canvas to show the item in the
        new location.

        Args:
            item: The transmission to move
        """
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
        """
        This method is called to check if the new added (or moved) transmission
        is actually collide or overlap with other existing transmission shapes.

        Args:
            trnsmShape: The added/moved transmission shape
        """
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
        """
        This method is called to refresh the transmission view. It is simply
        redraw the canvas that contains all drawing.
        """
        # self.OnItemMove(None)
        self._canvas.Draw()
