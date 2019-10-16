# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""
import wx.lib.ogl as ogl

from Events import EVENTS
from pubsub import pub


class RESEvtHandler(ogl.ShapeEvtHandler):
    """
    This module is used to handle the different events that the user can do for
    the shapes in our views. It overrides the following events:
        - OnLeftDoubleClick
        - OnBeginDragLeft
        - OnDragLeft
        - OnEndDragLeft
    """

    def __init__(self, shape):
        ogl.ShapeEvtHandler.__init__(self)
        self.SetShape(shape)
        self.SetPreviousHandler(shape.GetEventHandler())
        self._shapeX = shape.GetX()

    def OnLeftDoubleClick(self, x, y, keys=0, attachment=0):
        """
        This method is triggered when the user double click on one of the shapes
        in our views. It mainly gets the shape id and notify the controller that
        the following shape is double clicked by the user.

        Args:
            Just to have the same signature of the parent class. None of the
            args are used inside the function.
        """
        # print('OnLeftDoubleClick')
        shape = self.GetShape()
        shapeId = shape.GetId()
        pub.sendMessage(EVENTS.ITEM_DOUBLE_CLICK,
                        itemId=shapeId, itemType=shape.GetType())

    def OnBeginDragLeft(self, x, y, keys=0, attachment=0):
        """
        This method is triggered when the user start dragging a shape in our
        views. We allow only vertical moving for the shapes (i.e. up and down).
        Thus, you will find that we always use the shape X coordination so we
        can keep the horizontal position of the shape.

        Args:
            Please refer to OGL documentation for
            ShapeEvtHandler.OnBeginDragLeft
        """
        ogl.ShapeEvtHandler.OnBeginDragLeft(
            self, self._shapeX, y, keys, attachment)

    def OnDragLeft(self, draw, x, y, keys=0, attachment=0):
        """
        This method is triggered when the user actually drag a shape in our
        views. We allow only vertical moving for the shapes (i.e. up and down).
        Thus, you will find that we always use the shape X coordination so we
        can keep the horizontal position of the shape.

        Args:
            Please refer to OGL documentation for
            ShapeEvtHandler.OnDragLeft
        """
        ogl.ShapeEvtHandler.OnDragLeft(
            self, draw, self._shapeX, y, keys, attachment)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        """
        This method is triggered when the user stop dragging a shape in our
        views. We allow only vertical moving for the shapes (i.e. up and down).
        Thus, you will find that we always use the shape X coordination so we
        can keep the horizontal position of the shape. Finally, it trigger an
        event that the following shape is moved. This event will be handled by
        the controller.

        Args:
            Please refer to OGL documentation for
            ShapeEvtHandler.OnEndDragLeft
        """
        ogl.ShapeEvtHandler.OnEndDragLeft(
            self, self._shapeX, y, keys, attachment)
        pub.sendMessage(EVENTS.ITEM_MOVED, item=self.GetShape())
