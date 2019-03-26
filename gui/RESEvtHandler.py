# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:57:58 2018

@author: aelshaha
"""
import wx.lib.ogl as ogl

from Events import EVENTS
from pubsub import pub


class RESEvtHandler(ogl.ShapeEvtHandler):

    def __init__(self, shape):
        ogl.ShapeEvtHandler.__init__(self)
        self.SetShape(shape)
        self.SetPreviousHandler(shape.GetEventHandler())
        self._shapeX = shape.GetX()

    def OnLeftDoubleClick(self, x, y, keys=0, attachment=0):
        # print('OnLeftDoubleClick')
        shape = self.GetShape()
        shapeId = shape.GetId()
        pub.sendMessage(EVENTS.ITEM_DOUBLE_CLICK,
                        itemId=shapeId, itemType=shape.GetType())

    def OnBeginDragLeft(self, x, y, keys=0, attachment=0):
        ogl.ShapeEvtHandler.OnBeginDragLeft(
            self, self._shapeX, y, keys, attachment)

    def OnDragLeft(self, draw, x, y, keys=0, attachment=0):
        ogl.ShapeEvtHandler.OnDragLeft(
            self, draw, self._shapeX, y, keys, attachment)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        ogl.ShapeEvtHandler.OnEndDragLeft(
            self, self._shapeX, y, keys, attachment)
        pub.sendMessage(EVENTS.ITEM_MOVED, item=self.GetShape())
