# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
"""
from pubsub import pub
from Events import EVENTS

import DataConfig as config
import copy as cpy


class SiteModel:
    """
    This module represent the model for each site. It maintains the Commodities,
    Processes and Connections belong to that site.
    """

    def __init__(
            self,
            name,
            years,
            commodities=None,
            processes=None,
            connections=None):
        self._name = name
        self._years = years
        self._commodities = {}
        self._processes = {}
        self._connections = {}

        if commodities:
            self._commodities = commodities
        if processes:
            self._processes = processes
        if connections:
            self._connections = connections

    def InitializeData(cols):
        """
        This method is called to initialize each parameter in the Commodities,
        Processes, Connections (corresponding to a cell in the grid view) with
        its default or initial value.

        Args:
            cols: dictionary with the columns/parameters configurations

        Returns:
            the data dictionary
        """
        data = {}
        for col in cols:
            data[col[config.DataConfig.PARAM_KEY]
                 ] = col[config.DataConfig.PARAM_DEFVALUE]

        return data

    def InitializeCommodity(self):
        """
        This method is called to initialize the commodity data. It simply call
        the InitializeData method with the COMMODITY_PARAMS configuration.

        Returns:
            Data dictionary for the commodity
        """
        return SiteModel.InitializeData(config.DataConfig.COMMODITY_PARAMS)

    def InitializeProcess(self):
        """
        This method is called to initialize the process data. It simply call
        the InitializeData method with the PROCESS_COLS configuration.

        Returns:
            Data dictionary for the process
        """
        return SiteModel.InitializeData(config.DataConfig.PROCESS_COLS)

    def InitializeStorage(self):
        """
        This method is called to initialize the storage data. It simply call
        the InitializeData method with the STORAGE_PARAMS configuration.

        Returns:
            Data dictionary for the storage
        """
        return SiteModel.InitializeData(config.DataConfig.STORAGE_PARAMS)

    def InitializeConnection(self):
        """
        This method is called to initialize the connection data. It simply call
        the InitializeData method with the CONNECTION_PARAMS configuration.

        Returns:
            Data dictionary for the connection
        """
        return SiteModel.InitializeData(config.DataConfig.CONNECTION_PARAMS)

    def AddYear(self, year):
        """
        This method is called to add a new year to our model. It loops on all
        data in our model and append the new year to it.

        Args:
            year: The new added year
        """
        self._years.append(year)

        for data in self._commodities.values():
            data['Years'][year] = self.InitializeCommodity()

        for data in self._processes.values():
            if data['Type'] == 'Storage':
                data['Years'][year] = self.InitializeStorage()
            else:
                data['Years'][year] = self.InitializeProcess()

        for data in self._connections.values():
            data['Years'][year] = self.InitializeConnection()

    def RemoveYear(self, year):
        """
        This method is called to remove a year from our model. It loops on all
        data in our model and delete that year.

        Args:
            year: The year to remove
        """
        self._years.remove(year)

        for data in self._commodities.values():
            data['Years'].pop(year)

        for data in self._processes.values():
            data['Years'].pop(year)

        for data in self._connections.values():
            data['Years'].pop(year)

    def GetCommodityGroup(self, commType):
        """
        This method is called to calculate the group of the commodity, each
        commodity based on its type should belongs to a certain group. This
        group assignment is actually a part from the commodity id itself. This
        is used for sorting the commodities.

        Args:
            commType: The type of the commodity

        Returns:
            the group assigned to the commodity
        """
        grp = '2-1'
        if commType in (
                config.DataConfig.COMM_SUPIM,
                config.DataConfig.COMM_BUY):
            grp = '0-1'
        elif commType in (config.DataConfig.COMM_STOCK):
            grp = '1-1'
        elif commType in (config.DataConfig.COMM_ENV):
            grp = '2-2'

        return grp

    def CreateNewCommId(self, commType):
        """
        This method is called to calculate the id of the commodity, each
        commodity will have a unique identifier.

        Args:
            commType: The type of the commodity

        Returns:
            the group, number and the id of the commodity
        """
        grp = self.GetCommodityGroup(commType)
        num = str(len(self._commodities) + 1)
        if(len(num) < 2):
            num = '0' + num
        commId = grp + '_' + num + '_' + str.replace(commType, ' ', '_')

        return grp, num, commId

    def CreateNewCommodity(self, commType):
        """
        This method is called to create a new commodity and initialize its data.

        Args:
            commType: The type of the commodity

        Returns:
            the commodity data dictionary
        """
        grp, num, commId = self.CreateNewCommId(commType)
        data = {}
        data['Years'] = {}
        data['Id'] = commId
        data['Name'] = commType + '#' + num
        data['Type'] = commType
        data['Group'] = grp[0]
        data['Color'] = (0, 0, 0)
        data['DSM'] = False
        for year in self._years:
            data['Years'][year] = self.InitializeCommodity()

        return data

    def SaveCommodity(self, data):
        """
        This method is called to save the commodity data to our model. It checks
        if a commodity with the same name already exist or not. If it's ok, it
        saves the data and fire an event that a commodity is added (if new) or
        edited successfully.

        Args:
            data: The commodity data dictionary

        Returns:
            success or not
        """
        commId = data['Id']
        commName = data['Name']
        success = True
        for v in self._commodities.values():
            if v['Name'] == commName and v['Id'] != commId:
                success = False
                break
        if success:
            if commId not in self._commodities:
                self._commodities[commId] = data
                pub.sendMessage(EVENTS.COMMODITY_ADDED +
                                self._name, objId=commId)
            else:
                pub.sendMessage(EVENTS.COMMODITY_EDITED +
                                self._name, objId=commId)

        # Add further checks for status
        return success

    def GetCommodity(self, commId):
        """
        This method is called to get the commodity data by its Id.

        Args:
            commId: The id of the commodity

        Returns:
            the commodity data
        """
        if commId in self._commodities:
            return self._commodities[commId]

    def RemoveCommodity(self, commId):
        """
        This method is called to remove a commodity from our model by its Id.

        Args:
            commId: The id of the commodity
        """
        # remove connections linked to this commodity
        idsToDel = []
        for k, v in self._connections.items():
            if v['Comm'] == commId:
                idsToDel.append(k)

        for k in idsToDel:
            self._connections.pop(k)

        idsToDel.clear()

        # remove this commodity from process IN and/or OUT commodities
        for k, v in self._processes.items():
            if commId in v['IN']:
                v['IN'].remove(commId)
            if commId in v['OUT']:
                v['OUT'].remove(commId)
            # if the process is not linked to any other commodities
            # then the process should be deleted as well
            if len(v['IN']) == 0 and len(v['OUT']) == 0:
                idsToDel.append(k)

        # remove processes
        for k in idsToDel:
            self._processes.pop(k)

        if commId in self._commodities:
            self._commodities.pop(commId)

    def CloneCommodity(self, comm):
        """
        This method is called to clone a commodity in our model. It copies
        everything and assign the commodity a new Id.

        Args:
            comm: The commodity data dictionary
        """
        grp, num, commId = self.CreateNewCommId(comm['Type'])
        comm['Id'] = commId
        comm['Name'] = comm['Type'] + '#' + num
        self.SaveCommodity(comm)

    def GetCommodityList(self):
        """
        This method is called to list of the commodity, so later the user can
        choose which ones as input and/or output for the processes.

        Returns:
            dictionary with commodity names
        """
        x = {}
        ids = sorted(self._commodities.keys())
        for k in ids:
            x[k] = {'selected': '', 'Name': self._commodities[k]
                    ['Name'], 'Action': '...'}

        return x

    def CreateNewProcess(self):
        """
        This method is called to create a new process and initialize its data.

        Returns:
            the process data dictionary
        """
        processId = 'NewProcess#' + str(len(self._processes) + 1)
        data = {}
        data['IN'] = []
        data['OUT'] = []
        data['Years'] = {}
        data['Id'] = processId
        data['Name'] = processId
        data['Type'] = 'Process'
        data['PlotColor'] = (0, 0, 0)
        for year in self._years:
            data['Years'][year] = self.InitializeProcess()

        return data

    def SaveProcess(self, data):
        """
        This method is called to save the process data to our model. It checks
        if a process with the same name already exist or not. If it's ok, it
        saves the data and fire an event that a process is added (if new) or
        edited successfully.

        Args:
            data: The process data dictionary

        Returns:
            success or not
        """
        processId = data['Id']
        processName = data['Name']
        status = 0
        for v in self._processes.values():
            if v['Name'] == processName and v['Id'] != processId:
                status = 1
                break

        if len(data['IN']) == 0 and len(data['OUT']) == 0:
            status = 2

        if status == 0:
            self.SaveConnections(processId, data['IN'], 'IN')
            self.SaveConnections(processId, data['OUT'], 'OUT')
            if processId not in self._processes:
                self._processes[processId] = data
                pub.sendMessage(EVENTS.PROCESS_ADDED +
                                self._name, objId=processId)
            else:
                pub.sendMessage(EVENTS.PROCESS_EDITED +
                                self._name, objId=processId)

        # Add further checks for status
        return status

    def GetProcess(self, processId):
        """
        This method is called to get the process data by its Id.

        Args:
            processId: The id of the process

        Returns:
            the process data
        """
        return self._processes[processId]

    def RemoveProcess(self, processId):
        """
        This method is called to remove a process from our model by its Id.

        Args:
            processId: The id of the process
        """
        idsToDel = []
        for k, v in self._connections.items():
            if v['Proc'] == processId:
                idsToDel.append(k)

        for k in idsToDel:
            self._connections.pop(k)

        self._processes.pop(processId)

    def CopyProcess(self, proc, fromSiteModel):
        """
        This method is called to copy a process to our site model, from a
        different site.

        Args:
            - proc: The process data dictionary
            - fromSiteModel: the source site
        """
        # copy the linked process commodities (if not there)
        self.SyncProcessCommodities(proc['IN'], fromSiteModel)
        self.SyncProcessCommodities(proc['OUT'], fromSiteModel)

        # Save the process itself
        self.SaveProcess(proc)

        # update connections data
        self.SyncProcessConnections(proc, fromSiteModel, proc['Id'], 'IN')
        self.SyncProcessConnections(proc, fromSiteModel, proc['Id'], 'OUT')

    def CloneProcess(self, proc):
        """
        This method is called to clone a process in our model. It copies
        everything and assign the process a new Id.

        Args:
            proc: The process data dictionary
        """
        oldProcId = proc['Id']
        newProcId = 'New' + proc['Type'] + '#' + str(len(self._processes) + 1)
        proc['Id'] = newProcId
        proc['Name'] = newProcId
        self.SaveProcess(proc)
        # update connections data
        self.SyncProcessConnections(proc, self, oldProcId, 'IN')
        self.SyncProcessConnections(proc, self, oldProcId, 'OUT')

    def SyncProcessCommodities(self, commList, fromSiteModel):
        """
        This method is called to copy the commodities associated with a
        certain process to our site from another site model (if they are not
        already part of our model)

        Args:
            - commList: The list of commodities
            - fromSiteModel: The source model
        """
        for commId in commList:
            if commId not in self._commodities:
                comm = fromSiteModel._commodities[commId]
                self.SaveCommodity(cpy.deepcopy(comm))

    def SyncProcessConnections(self, proc, fromSiteModel, fromProcId, connDir):
        """
        This method is called to copy the connections associated with a
        certain process to our site from another site model (if they are not
        already part of our model)

        Args:
            - proc: The process data
            - fromSiteModel: The source model
            - fromProcId: The source process id
            - connDir: The direction of the connection
        """
        procId = proc['Id']
        for commId in proc[connDir]:
            fromConn = fromSiteModel.GetConnection(fromProcId, commId, connDir)
            toConn = self.GetConnection(procId, commId, connDir)
            toConn['Years'] = cpy.deepcopy(fromConn['Years'])

    def AddConnection(self, procId, commId, In_Out):
        """
        This method is called to add a new connection between a certain process
        and certain commodity in a specific direction.

        Args:
            - procId: The Id of the process
            - commId: The Id of the commodity
            - In_Out: The direction of the connection (In/Out)

        Returns:
            The connection Id
        """
        connId = procId + '$' + commId + '$' + In_Out
        if connId not in self._connections.keys():
            yearsData = {}
            for year in self._years:
                yearsData[year] = self.InitializeConnection()
            data = {}
            data['Dir'] = In_Out
            data['Proc'] = procId
            data['Comm'] = commId
            data['Years'] = yearsData
            self._connections[connId] = data

        return connId

    def SaveConnections(self, processId, commList, direction):
        """
        This method is called to save the connections data to our model.

        Args:
            - processId: The Id of the process
            - commList: The commodity list
            - direction: The direction of the connections (In/Out)
        """
        # Remove deselcted connections
        idsToDel = []
        for k, v in self._connections.items():
            if v['Proc'] == processId and v['Dir'] == direction:
                if v['Comm'] not in commList:
                    idsToDel.append(k)

        for k in idsToDel:
            self._connections.pop(k)

        for comm in commList:
            self.AddConnection(processId, comm, direction)
        #
        # print(direction, self._connections.keys())

    def GetConnection(self, procId, commId, In_Out):
        """
        This method is called to get the connection data based on the process,
        the commodity, the direction of the connection. It creates it if the
        connection doesn't exist.

        Args:
            - procId: The Id of the process
            - commId: The Id of the commodity
            - In_Out: The direction of the connection (In/Out)

        Returns:
            The connection data dictionary
        """
        connId = self.AddConnection(procId, commId, In_Out)
        return self._connections[connId]

    def CreateNewStorage(self):
        """
        This method is called to create a new storage and initialize its data.

        Returns:
            the storage data dictionary
        """
        storageId = 'NewStorage#' + str(len(self._processes) + 1)
        data = {}
        data['IN'] = []
        data['OUT'] = []
        data['Years'] = {}
        data['Id'] = storageId
        data['Name'] = storageId
        data['Type'] = 'Storage'
        for year in self._years:
            data['Years'][year] = self.InitializeStorage()

        return data

    def GetStorage(self, storageId):
        """
        This method is called to get the storage data by its Id.

        Args:
            storageId: The id of the process

        Returns:
            the storage data
        """
        return self._processes[storageId]

    def GetSiteName(self):
        """
        This method is called to get the site name associated with this model
        instance.

        Returns:
            the site name
        """
        return self._name

    def GetCommByName(self, commName):
        """
        This method is called to get the commodity data by its name.

        Args:
            commName: The name of the commodity

        Returns:
            the commodity data
        """
        for v in self._commodities.values():
            if v['Name'] == commName:
                return v

        return None
