# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""

import wx
import wx.grid
import DataConfig as config
import GridDataTable as gdt
import BasicForm as bf
import copy as cpy
import TimeSeriesForm as ts

from pubsub import pub
from Events import EVENTS


class ProcessDialog (bf.BasicForm):
    """
    This form is used to add a new Process or edit an existing one. The form
    inherits from the BasicForm class.
    """

    _gridCols = config.DataConfig.PROCESS_COLS

    def __init__(self, parent):
        super().__init__(parent, "Process data", wx.Size(800, 650))
        contentLayout = wx.BoxSizer(wx.VERTICAL)

        layout0 = self.CreateGeneralLayout()

        h1 = wx.StaticBox(self, wx.ID_ANY, u"Parameters:")
        h1.SetForegroundColour('white')
        layout1 = wx.StaticBoxSizer(h1, wx.VERTICAL)
        # Grid and its data table
        self._gridTable1 = gdt.GridDataTable(self._gridCols)
        self._yearsGrid1 = wx.grid.Grid(h1, -1)
        self._yearsGrid1.SetTable(self._gridTable1, True)
        self._yearsGrid1.AutoSizeColumns(False)
        self._yearsGrid1.HideCol(0)  # time series
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self._yearsGrid1.SetColAttr(len(self._gridCols) - 1, attr)  # ...
        self._yearsGrid1.Bind(
            wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnTimeSerClick)
        layout1.Add(self._yearsGrid1, 1, wx.ALL, 3)

        contentLayout.Add(layout0, 0, wx.ALL, 5)
        contentLayout.Add(layout1, 1, wx.ALL | wx.EXPAND, 1)
        super().SetContent(contentLayout, wx.ALIGN_CENTER_HORIZONTAL)

    def CreateGeneralLayout(self):
        """This method is called to create the form layout itself, which is a
        grid table consist of a row for each defined year in our Reference
        Energy System.

        Return:
            The created layout
        """

        layout = wx.BoxSizer(wx.VERTICAL)

        # Name Part
        layout0 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Process name:")
        label.SetForegroundColour(wx.WHITE)
        layout0.Add(label, 0, wx.ALL, 5)
        self._txtProcessName = wx.TextCtrl(self, size=wx.Size(200, 25))
        layout0.Add(self._txtProcessName, 0, wx.ALL, 5)
        # Color
        label = wx.StaticText(self, -1, "...........................")
        layout0.Add(label, 0, wx.ALL, 5)
        label = wx.StaticText(self, -1, "Plot Color:")
        label.SetForegroundColour(wx.WHITE)
        layout0.Add(label, 0, wx.ALL, 5)
        self._plotColor = wx.ColourPickerCtrl(self, -1, wx.Colour(0, 0, 0))
        layout0.Add(self._plotColor, 0, wx.ALL, 5)
        #######################################################################

        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        layout1_1 = self.CreateInCommLayout()
        layout1.Add(layout1_1, 1, wx.ALL | wx.EXPAND, 5)

        layout1_2 = self.CreateOutCommLayout()
        layout1.Add(layout1_2, 1, wx.ALL, 5)

        layout.Add(layout0, 0, wx.ALL, 5)
        layout.Add(layout1, 0, wx.ALL, 5)

        return layout

    def CreateInCommLayout(self):
        """This method is called to create the layout for selecting the IN
        commodities. It's a grid table consist of a row for each defined
        commodity. The user can select one or more commodity as input to the
        process.

        Return:
            The created layout
        """
        # Input Commodities
        sb = wx.StaticBox(self, wx.ID_ANY, u"Input Commodities:")
        sb.SetForegroundColour('white')
        layout1_1 = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        # Grid and its data table
        self._inCommTbl = gdt.GridDataTable(config.DataConfig.COMMODITY_COLS)
        self._inCommGrid = wx.grid.Grid(
            sb, -1, wx.DefaultPosition, wx.Size(350, 200), 0)
        self._inCommGrid.SetTable(self._inCommTbl)
        self._inCommGrid.SetColSize(0, 20)
        self._inCommGrid.SetColSize(1, 200)
        self._inCommGrid.SetRowLabelSize(0)
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        self._inCommGrid.SetColAttr(1, attr)
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self._inCommGrid.SetColAttr(2, attr)
        self._inCommGrid.Bind(
            wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnInConnEdit)
        layout1_1.Add(self._inCommGrid, 1, wx.ALL | wx.EXPAND, 1)

        return layout1_1

    def CreateOutCommLayout(self):
        """This method is called to create the layout for selecting the OUT
        commodities. It's a grid table consist of a row for each defined
        commodity. The user can select one or more commodity as output of the
        process.

        Return:
            The created layout
        """
        # Output Commodities
        sb = wx.StaticBox(self, wx.ID_ANY, u"Output Commodities:")
        sb.SetForegroundColour('white')
        layout1_2 = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        # Grid and its data table
        self._outCommTbl = gdt.GridDataTable(config.DataConfig.COMMODITY_COLS)
        self._outCommGrid = wx.grid.Grid(
            sb, -1, wx.DefaultPosition, wx.Size(350, 200), 0)
        self._outCommGrid.SetTable(self._outCommTbl)
        self._outCommGrid.SetColSize(0, 20)
        self._outCommGrid.SetColSize(1, 200)
        self._outCommGrid.SetRowLabelSize(0)
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        self._outCommGrid.SetColAttr(1, attr)
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self._outCommGrid.SetColAttr(2, attr)
        self._outCommGrid.Bind(
            wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnOutConnEdit)
        layout1_2.Add(self._outCommGrid, 1, wx.ALL | wx.EXPAND, 5)

        return layout1_2

    def PopulateProcess(self, process, commList):
        """This method is called when the user try to Edit a process. The
        form is populated with the data of the selected process. It shows the
        process data and to which IN/OUT commodities the process is connected.

        Args:
            - process: The process data
            - commList: List of the commodities associated with the process
        """
        self._orgProc = cpy.deepcopy(process)
        self._process = process
        self._txtProcessName.SetValue(process['Name'])
        self._plotColor.SetColour(process['PlotColor'])
        ##
        inCommList = cpy.deepcopy(commList)
        for k, v in inCommList.items():
            if k in process['IN']:
                v['selected'] = True

        outCommList = cpy.deepcopy(commList)
        for k, v in outCommList.items():
            if k in process['OUT']:
                v['selected'] = True
        ##
        super().PopulateGrid(self._inCommTbl, inCommList)
        super().PopulateGrid(self._outCommTbl, outCommList)
        super().PopulateGrid(self._gridTable1, process['Years'])
        super().SetDataItem(self._process)

    def OnTimeSerClick(self, event):
        """This method is called when the user want to define the time series
        information for the process (for certain year). It shows the
        'TimeSeries' form so the user can enter the data.

        Args:
            event: The event object from WX
        """
        if event.GetCol() != len(self._gridCols) - 1:
            return

        tsf = ts.TimeSeriesForm(self)
        tsf.PopulateData(self._process['Name'],
                         self._gridTable1, event.GetRow(), 0)
        tsf.ShowModal()

    def OnOk(self, event):
        """This method is called when the user click Ok to save the process
        data. It gets the process info from the view and store it in the
        process data dictionary. Finally, it notifies the controller that the
        user want to save the process.

        Args:
            event: The event object from WX
        """
        self._process['Name'] = self._txtProcessName.GetValue()
        self._process['PlotColor'] = self._plotColor.GetColour().GetAsString()
        self._inCommTbl.Commit()
        self._process['IN'] = self.GetSelectedCommodities(self._inCommTbl)
        self._outCommTbl.Commit()
        self._process['OUT'] = self.GetSelectedCommodities(self._outCommTbl)
        self._gridTable1.Commit()
        pub.sendMessage(EVENTS.PROCESS_SAVE, data=self._process)

    def GetSelectedCommodities(self, gridTbl):
        """
        This method is called to get the list of commodities that the user
        selected as input (or output) for the process.

        Args:
            gridTbl: The grid that contains all commodities

        Return:
            The list of selected commodities
        """
        x = []
        data = gridTbl.GetData()
        for k in sorted(data):
            if data[k]['selected']:
                x.append(k)

        return x

    def OnCancel(self, event):
        """This method is called when the user click cancel to ignore the
        changes he/she did. The method store the process info and call the
        parent class OnCancel method.

        Args:
            event: The event object from WX
        """
        self._process.update(self._orgProc)
        super().OnCancel(event)

    def OnInConnEdit(self, event):
        """This method triggered when the user wants to Edit the Connection
        properties. Connection here is the link from input commodity to the
        process. It just call OnCellDblClk method with 'IN' as the connection
        direction.

        Args:
            event: The event object from WX
        """
        self.OnCellDblClk(event, 'IN')

    def OnOutConnEdit(self, event):
        """This method triggered when the user wants to Edit the Connection
        properties. Connection here is the link from the process to the output
        commodity. It just call OnCellDblClk method with 'OUT' as the connection
        direction.

        Args:
            event: The event object from WX
        """
        self.OnCellDblClk(event, 'OUT')

    def OnCellDblClk(self, event, In_Out):
        """This method is called to show the connection form to edit the
        connection properties per year. If the row of the grid (the commodity)
        is not selected, the user get an error message.

        Args:
            - event: The event object from WX
            - In_Out: The direction of the connection
        """
        col = event.GetCol()
        if col != 2:
            return

        row = event.GetRow()
        grid = event.GetEventObject()
        selected = grid.GetCellValue(row, 0)  # selected
        if selected:
            pub.sendMessage(
                EVENTS.CONNECTION_EDITING,
                procId=self._process['Id'],
                commId=grid.GetRowLabelValue(row),
                In_Out=In_Out)
        else:
            wx.MessageBox('You have to select the commodity first.',
                          'Info', wx.OK | wx.ICON_INFORMATION)
