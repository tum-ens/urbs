# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.lib.ogl as ogl
import RESShapes as res
import DataConfig as cfg

from pubsub import pub
from Events import EVENTS


class RESView(wx.Panel):
    """This module represent the Reference Energy System (RES) view in our
    solution. It is created for each site, each site will have its own view and
    model as well. It allows the user to define the commodities, processes,
    storage for this site and show how they are connected graphically.
    """

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
        """
        Each RES view is for a specific site. This method is called to get the
        name of the site associated with this RES view.

        Returns:
            The site name
        """
        return self._siteName
# ----------------------------------------------------------------------------#

    def BuildToolBar(self):
        """
        This method is called to build the tool bar in the RES view. It allows
        the user to add new commodities (with different types), processes and
        storage.

        Returns:
            The tool bar layout
        """
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
        """
        This method is triggered when the user want to add a new shape
        (commodity, process or storage) to the view. It just fire an event for
        the controller to open the proper form for the user.

        Args:
             event: The event object from WX
        """
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
        """
        This method is called to initialize the canvas for drawing the shapes.
        """
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
        """
        This method is called to refresh the view and redraw the whole canvas.
        """
        dc = wx.ClientDC(self._canvas)
        self._canvas.PrepareDC(dc)
        self._canvas.Redraw(dc)

# ----------------------------------------------------------------------------#
    def RebuildRES(self, objId):
        """
        This method is called to rebuild (redraw) the whole view. It clears all
        shapes, draw the commodities and finally the processes.

        Args:
            objId: The last added process/storage
        """
        # print('Inside Rebuild')
        self.RemoveAllShapes()
        self.DrawCommodities()
        self.DrawProcesses(objId)

        self.RefreshCanvas()
# ----------------------------------------------------------------------------#

    def RemoveAllShapes(self):
        """
        This method is called to remove all shapes from the view (clear diagram)
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
        encounter a new group, it start drawing a new area (vertical line) to
        split the view.
        """
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
        """
        This method is called to draw the process shapes on the view. It
        loops on all commodities and for each commodity, it gets the linked
        processes to be drawn.

        Args:
            lastChangedProcess: The last added process/storage
        """
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
        """
        This method is called to get the connections (lines) that should be
        drawn from/to the process shape. It get the Input commodities for the
        process and start add the necessary lines (connections). Similarly, it
        gets the output commodities and loop on them to add the necessary
        connections (to the right).

        Args:
            - p: The process object data
            - procShape: The process shape in the view

        Returns:
            List of connections (connection shapes)
        """
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
        """
        This method is called to draw the connections (lines) connected to a
        certain process/storage. The lines could be to the left and/or the
        right of the process shape.

        Args:
            - procShape: The process/storage shape
            - lines: list of connections to draw
        """
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
        """
        The RES view split into three areas. This method is called to draw a
        new group area (vertical line) starting from point x.

        Args:
            x: The x coordinate
        """
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
        This method is triggered when the user try to drag and move a process or
        storage shape. It keep redrawing the canvas to show the item in the
        new location.

        Args:
            item: The process/storage shape
        """
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
        """
        This method is called to check if the new added (or moved) process
        (or storage) is actually collide or overlap with other existing
        process/storage shapes.

        Args:
            procShape: The added/moved process/storage shape
        """
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
        """
        This method is called to refresh the view. It is simply redraw the
        canvas that contains all drawing.
        """
        # self.OnItemMove(None)
        self._canvas.Draw()
