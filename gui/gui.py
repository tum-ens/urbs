# -*- coding: utf-8 -*-
"""
@author: amrelshahawy

This is the entry point for our application, where we instantiate our wxApp.
    - Create a wx application object.
    - Instantiate the controller. The controller internally will instantiate the
      necessary model(s) and the main view.
    - Start the event loop (user inputs).
"""

import wx
import Controller as ctrl

if __name__ == "__main__":
    app = wx.App()
    c = ctrl.Controller()
    app.MainLoop()
