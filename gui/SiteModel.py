# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 20:53:37 2018

@author: aelshaha
"""
from pubsub import pub
from Events import EVENTS

import DataConfig as config
import copy as cpy


class SiteModel():

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
        data = {}
        for col in cols:
            data[col[config.DataConfig.PARAM_KEY]
                 ] = col[config.DataConfig.PARAM_DEFVALUE]

        return data

    def InitializeCommodity(self):
        return SiteModel.InitializeData(config.DataConfig.COMMODITY_PARAMS)

    def InitializeProcess(self):
        return SiteModel.InitializeData(config.DataConfig.PROCESS_COLS)

    def InitializeStorage(self):
        return SiteModel.InitializeData(config.DataConfig.STORAGE_PARAMS)

    def InitializeConnection(self):
        return SiteModel.InitializeData(config.DataConfig.CONNECTION_PARAMS)

    def AddYear(self, year):
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
        self._years.remove(year)

        for data in self._commodities.values():
            data['Years'].pop(year)

        for data in self._processes.values():
            data['Years'].pop(year)

        for data in self._connections.values():
            data['Years'].pop(year)

    def GetCommodityGroup(self, commType):
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
        grp = self.GetCommodityGroup(commType)
        num = str(len(self._commodities) + 1)
        if(len(num) < 2):
            num = '0' + num
        commId = grp + '_' + num + '_' + str.replace(commType, ' ', '_')

        return grp, num, commId

    def CreateNewCommodity(self, commType):
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
        if commId in self._commodities:
            return self._commodities[commId]

    def RemoveCommodity(self, commId):
        idsToDel = []
        for k, v in self._connections.items():
            if v['Comm'] == commId:
                idsToDel.append(k)

        for k in idsToDel:
            self._connections.pop(k)

        for v in self._processes.values():
            if commId in v['IN']:
                v['IN'].remove(commId)
            if commId in v['OUT']:
                v['OUT'].remove(commId)

        if commId in self._commodities:
            self._commodities.pop(commId)

    def CloneCommodity(self, comm):
        grp, num, commId = self.CreateNewCommId(comm['Type'])
        comm['Id'] = commId
        comm['Name'] = comm['Type'] + '#' + num
        self.SaveCommodity(comm)

    def GetCommodityList(self):
        x = {}
        ids = sorted(self._commodities.keys())
        for k in ids:
            x[k] = {'selected': '', 'Name': self._commodities[k]
                    ['Name'], 'Action': '...'}

        return x

    def CreateNewProcess(self):
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
        return self._processes[processId]

    def RemoveProcess(self, processId):
        idsToDel = []
        for k, v in self._connections.items():
            if v['Proc'] == processId:
                idsToDel.append(k)

        for k in idsToDel:
            self._connections.pop(k)

        self._processes.pop(processId)

    def CopyProcess(self, proc, fromSiteModel):
        # copy the linked process commodities (if not there)
        self.SyncProcessCommodities(proc['IN'], fromSiteModel)
        self.SyncProcessCommodities(proc['OUT'], fromSiteModel)

        # Save the process itself
        self.SaveProcess(proc)

        # update connections data
        self.SyncProcessConnections(proc, fromSiteModel, proc['Id'], 'IN')
        self.SyncProcessConnections(proc, fromSiteModel, proc['Id'], 'OUT')

    def CloneProcess(self, proc):
        oldProcId = proc['Id']
        newProcId = 'New' + proc['Type'] + '#' + str(len(self._processes) + 1)
        proc['Id'] = newProcId
        proc['Name'] = newProcId
        self.SaveProcess(proc)
        # update connections data
        self.SyncProcessConnections(proc, self, oldProcId, 'IN')
        self.SyncProcessConnections(proc, self, oldProcId, 'OUT')

    def SyncProcessCommodities(self, commList, fromSiteModel):
        for commId in commList:
            if commId not in self._commodities:
                comm = fromSiteModel._commodities[commId]
                self.SaveCommodity(cpy.deepcopy(comm))

    def SyncProcessConnections(self, proc, fromSiteModel, fromProcId, connDir):
        procId = proc['Id']
        for commId in proc[connDir]:
            fromConn = fromSiteModel.GetConnection(fromProcId, commId, connDir)
            toConn = self.GetConnection(procId, commId, connDir)
            toConn['Years'] = cpy.deepcopy(fromConn['Years'])

    def AddConnection(self, procId, commId, In_Out):
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
        connId = self.AddConnection(procId, commId, In_Out)
        return self._connections[connId]

    def CreateNewStorage(self):
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
        return self._processes[storageId]

    def GetSiteName(self):
        return self._name

    def GetCommByName(self, commName):
        for v in self._commodities.values():
            if v['Name'] == commName:
                return v

        return None
