# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 11:35:21 2018

@author: aelshaha
"""
import Model as model
import MainView as view
import CommodityForm as commf
import ProcessForm as procf
import ConnectionForm as connf
import StorageForm as strgf
import TransmissionForm as tf
import SitesForm as sf
import DataConfig as config
import Errors as ERR
import copy as cpy
import json
import time
import urbs
import wx

from pubsub import pub
from Events import EVENTS


class Controller():

    def __init__(self):

        # Model part
        self._resModel = model.RESModel()
        self._model = None

        # view part
        self._view = view.MainView(self)
        self._view.Maximize()
        self._view.Show()

        # subscribe on Views events
        pub.subscribe(self.AddYear, EVENTS.YEAR_ADDING)
        pub.subscribe(self.RemoveYears, EVENTS.YEAR_REMOVING)

        pub.subscribe(self.AddSite, EVENTS.SITE_ADDING)
        pub.subscribe(self.RemoveSites, EVENTS.SITE_REMOVING)

        pub.subscribe(self.AddPeriod, EVENTS.PERIOD_ADDING)
        pub.subscribe(self.RemovePeriods, EVENTS.PERIOD_REMOVING)

        pub.subscribe(self.AddCommodity, EVENTS.COMMODITY_ADDING)
        pub.subscribe(self.EditCommodity, EVENTS.COMMODITY_EDITING)
        pub.subscribe(self.SaveCommodity, EVENTS.COMMODITY_SAVE)
        # pub.subscribe(self.SelectCommodity, EVENTS.COMMODITY_SELECTED)
        # pub.subscribe(self.DeselectCommodity, EVENTS.COMMODITY_DESELECTED)

        pub.subscribe(self.AddProcess, EVENTS.PROCESS_ADDING)
        pub.subscribe(self.EditProcess, EVENTS.PROCESS_EDITING)
        pub.subscribe(self.SaveProcess, EVENTS.PROCESS_SAVE)
        # pub.subscribe(self.SelectProcess, EVENTS.PROCESS_SELECTED)
        # pub.subscribe(self.DeselectProcess, EVENTS.PROCESS_DESELECTED)

        pub.subscribe(self.AddStorage, EVENTS.STORAGE_ADDING)
        pub.subscribe(self.EditStorage, EVENTS.STORAGE_EDITING)
        pub.subscribe(self.SaveStorage, EVENTS.STORAGE_SAVE)

        pub.subscribe(self.EditConnection, EVENTS.CONNECTION_EDITING)

        pub.subscribe(self.AddTransmission, EVENTS.TRNSM_ADDING)
        pub.subscribe(self.SaveTransmission, EVENTS.TRNSM_SAVE)

        pub.subscribe(self.RESSelected, EVENTS.RES_SELECTED)
        pub.subscribe(self.OnItemDoubleClick, EVENTS.ITEM_DOUBLE_CLICK)
        pub.subscribe(self.OnItemMove, EVENTS.ITEM_MOVED)
        pub.subscribe(self.OnSaveConfig, EVENTS.SAVE_CONFIG)
        pub.subscribe(self.OnLoadConfig, EVENTS.LOAD_CONFIG)

        pub.subscribe(self.AddScenario, EVENTS.SCENARIO_ADDED)
        pub.subscribe(self.RemoveScenario, EVENTS.SCENARIO_REMOVED)

        pub.subscribe(self.OnCopyClick, EVENTS.ITEM_COPY)
        pub.subscribe(self.CopyItem, EVENTS.ITEM_COPIED)
        pub.subscribe(self.DeleteItem, EVENTS.ITEM_DELETE)
        pub.subscribe(self.CloneItem, EVENTS.ITEM_CLONE)

    def AddSite(self, site):
        status = self._resModel.AddSite(site)
        if status == 1:
            wx.MessageBox('A Site with the same name already exist!', 'Error',
                          wx.OK | wx.ICON_ERROR)
        else:
            self._view.AddRESTab(self, site)
            self._view.Refresh(False)

    def RemoveSites(self, sites):
        s = wx.MessageBox('Are you sure? All site(s) data will be lost!',
                          'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if s == wx.OK:
            self._resModel.RemoveSites(sites)
            self._view.RemoveRESTab(sites)

    def AddPeriod(self, period):
        status = self._resModel.AddPeriod(period)
        if status == 1:
            wx.MessageBox('A Period with the same name already exist!',
                          'Error', wx.OK | wx.ICON_ERROR)

    def RemovePeriods(self, periods):
        s = wx.MessageBox('Are you sure? ', 'Warning',
                          wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if s == wx.OK:
            self._resModel.RemovePeriods(periods)

    def RESSelected(self, siteName):
        self._model = self._resModel.GetSiteModel(siteName)

    def AddYear(self, year):
        self._resModel.AddYear(year)

    def RemoveYears(self, years):
        s = wx.MessageBox('Are you sure? All year(s) data will be lost!',
                          'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if s == wx.OK:
            self._resModel.RemoveYears(years)

    def AddCommodity(self, commType):
        comm = self._model.CreateNewCommodity(commType)
        self._comForm = commf.CommodityDialog(self._view)
        self._comForm.PopulateCommodity(comm)
        self._comForm.ShowModal()

    def EditCommodity(self, commId):
        comm = self._model.GetCommodity(commId)
        if comm:
            self._comForm = commf.CommodityDialog(self._view)
            self._comForm.PopulateCommodity(comm)
            self._comForm.ShowModal()

    def SaveCommodity(self, data):
        status = self._model.SaveCommodity(data)
        if status:
            self._comForm.Close()
        else:
            wx.MessageBox('A Commodity with the same name already exist!',
                          'Error', wx.OK | wx.ICON_ERROR)

    def AddProcess(self):
        newProcess = self._model.CreateNewProcess()
        self._processForm = procf.ProcessDialog(self._view)
        self._processForm.PopulateProcess(
            newProcess, self._model.GetCommodityList())
        self._processForm.ShowModal()

    def SaveProcess(self, data):
        status = self._model.SaveProcess(data)
        if status == 1:
            wx.MessageBox('A process with the same name already exist!',
                          'Error', wx.OK | wx.ICON_ERROR)
        elif status == 2:
            wx.MessageBox(
                'Please select atleast one input and one output commodity!',
                'Error',
                wx.OK | wx.ICON_ERROR)
        else:
            self._processForm.Close()

    def EditProcess(self, processId):
        process = self._model.GetProcess(processId)
        self._processForm = procf.ProcessDialog(self._view)
        self._processForm.PopulateProcess(
            process, self._model.GetCommodityList())
        self._processForm.ShowModal()

    def AddStorage(self):
        newStorage = self._model.CreateNewStorage()
        self._storageForm = strgf.StorageDialog(self._view)
        self._storageForm.PopulateStorage(
            newStorage, self._model.GetCommodityList())
        self._storageForm.ShowModal()

    def SaveStorage(self, data):
        status = self._model.SaveProcess(data)  # storage is a process
        if status == 1:
            wx.MessageBox('A storage with the same name already exist!',
                          'Error', wx.OK | wx.ICON_ERROR)
        elif status == 2:
            wx.MessageBox('Please select a commodity!',
                          'Error', wx.OK | wx.ICON_ERROR)
        else:
            self._storageForm.Close()

    def EditStorage(self, storageId):
        storage = self._model.GetStorage(storageId)
        self._storageForm = strgf.StorageDialog(self._view)
        self._storageForm.PopulateStorage(
            storage, self._model.GetCommodityList())
        self._storageForm.ShowModal()

    def EditConnection(self, procId, commId, In_Out):
        connection = self._model.GetConnection(procId, commId, In_Out)
        connForm = connf.ConnectionDialog(self._view)
        connForm.PopulateConnectionGrid(connection)
        connForm.ShowModal()

    def GetCommodities(self, siteName):
        m = self._resModel.GetSiteModel(siteName)
        return m._commodities

    def GetProcesses(self):
        return self._model._processes

    def GetLinkedProcesses(self, siteName, commName):
        d = {}
        m = self._resModel.GetSiteModel(siteName)
        for k, p in m._processes.items():
            if len(p['IN']) > 0 and p['IN'][-1] == commName:
                d[k] = p

        for k, p in m._processes.items():
            if len(p['IN']) == 0 and len(
                    p['OUT']) > 0 and p['OUT'][0] == commName:
                d[k] = p

        return d

    def AddTransmission(self):
        newTrns = self._resModel.CreateNewTrnsm()
        self._trnsForm = tf.TransmissionDialog(self._view, self)
        self._trnsForm.PopulateTrans(newTrns, self._resModel.GetSites())
        self._trnsForm.ShowModal()

    def SaveTransmission(self, data):
        status = self._resModel.SaveTransmission(data)
        if status:
            self._trnsForm.Close()
        else:
            wx.MessageBox(
                'A Transmission line with the same name already exist!',
                'Error',
                wx.OK | wx.ICON_ERROR)

    def EditTransmission(self, trnsmId):
        trnsm = self._resModel.GetTransmission(trnsmId)
        self._trnsForm = tf.TransmissionDialog(self._view, self)
        self._trnsForm.PopulateTrans(trnsm, self._resModel.GetSites())
        self._trnsForm.ShowModal()

    def GetTransmissions(self):
        return self._resModel._transmissions

    def GetTrnsmCommodities(self):
        return self._resModel._trnsmCommodities

    def GetCommonCommodities(self, site1, site2):
        m1 = self._resModel.GetSiteModel(site1)
        m2 = self._resModel.GetSiteModel(site2)

        c1 = set([x['Name'] for x in m1._commodities.values()])
        c2 = set([x['Name'] for x in m2._commodities.values()])

        mergedSet = c1 & c2
        return list(mergedSet)

    def OnItemDoubleClick(self, itemId, itemType):
        if itemType == 'Commodity':
            self.EditCommodity(itemId)
        elif itemType == 'Process':
            self.EditProcess(itemId)
        elif itemType == 'Storage':
            self.EditStorage(itemId)
        elif itemType == 'Trnsm':
            self.EditTransmission(itemId)

    def OnItemMove(self, item):
        if item.GetType() == 'Trnsm':
            pub.sendMessage(EVENTS.TRNSM_ITEM_MOVED, item=item)
        else:
            pub.sendMessage(EVENTS.ITEM_MOVED +
                            self._model.GetSiteName(), item=item)

    def SerializeObj(self, obj):
        # print(obj)
        if isinstance(obj, wx.Colour):
            return obj.GetAsString()

        return obj.__dict__

    def OnSaveConfig(self, filename):
        with open(filename, 'w') as fp:
            json.dump(self._resModel, fp, default=self.SerializeObj, indent=2)

    def OnLoadConfig(self, filename):
        self._view.RemoveRESTab(self._resModel._sites)
        with open(filename, 'r') as fp:
            data = json.load(fp)
            self._resModel = model.RESModel(data)
            trnsmView = self._view.GetTrnsmTab()
            trnsmView.RebuildTrnsm(None)
            trnsmView.Refresh()
            for site in sorted(self._resModel._sites):
                resTab = self._view.AddRESTab(self, site)
                self._model = self._resModel.GetSiteModel(site)
                resTab.RebuildRES(None)
                resTab.Refresh()

        self._view.Refresh(False)

    def GetGlobalParams(self):
        return self._resModel.GetGlobalParams()

    def GetScenarios(self):
        return sorted(config.DataConfig.SCENARIOS.keys())

    def AddScenario(self, scName):
        self._resModel.AddScenario(scName)

    def RemoveScenario(self, scName):
        self._resModel.RemoveScenario(scName)

    def OnCopyClick(self, item):
        sites = [x for x in self._resModel.GetSites() if x !=
                 self._model.GetSiteName()]
        if len(sites) > 0:
            self._sitesForm = sf.SitesDialog(self._view, sites, item)
            self._sitesForm.ShowModal()
        else:
            wx.MessageBox(ERR.ERRORS[ERR.ONE_SITE],
                          'Error', wx.OK | wx.ICON_ERROR)

    def CopyItem(self, item, sites):
        # print(item)
        for site in sites:
            m = self._resModel.GetSiteModel(site)
            if item['Type'] in ('Process', 'Storage'):
                if item['Id'] in m._processes:
                    wx.MessageBox(ERR.ERRORS[ERR.ALREADY_COPIED] %
                                  site, 'Error', wx.OK | wx.ICON_ERROR)
                else:
                    m.CopyProcess(item, self._model)
            else:
                m.SaveCommodity(item)

    def DeleteItem(self, item):
        if item['Type'] in ('Process', 'Storage'):
            self._model.RemoveProcess(item['Id'])
        else:
            self._model.RemoveCommodity(item['Id'])

        pub.sendMessage(EVENTS.ITEM_DELETED +
                        self._model.GetSiteName(), objId=None)

    def CloneItem(self, item):
        if item['Type'] in ('Process', 'Storage'):
            self._model.CloneProcess(cpy.deepcopy(item))
        else:
            self._model.CloneCommodity(cpy.deepcopy(item))

    def ValidateData(self):
        success = True
        if len(self._resModel._years) == 0:
            success = False
            wx.MessageBox(ERR.ERRORS[ERR.NO_YEAR],
                          'Error', wx.OK | wx.ICON_ERROR)

        if len(self._resModel._sites) == 0:
            success = False
            wx.MessageBox(ERR.ERRORS[ERR.NO_SITE],
                          'Error', wx.OK | wx.ICON_ERROR)

        if len(self._resModel._scenarios) == 0:
            success = False
            wx.MessageBox(ERR.ERRORS[ERR.NO_SCENARIO],
                          'Error', wx.OK | wx.ICON_ERROR)

        for site, m in self._resModel._models.items():
            if len(m._commodities) > 0:
                for comm in m._commodities.values():
                    if comm['Type'] in (config.DataConfig.COMM_SUPIM):
                        for year in m._years:
                            timeSer = comm['Years'][year]['timeSer']
                            if timeSer != '':
                                ln = len(timeSer.split('|'))
                                if ln != config.DataConfig.TS_LEN:
                                    success = False
                                    msg = ERR.ERRORS[ERR.TS_LEN] % (
                                        config.DataConfig.TS_LEN, ln,
                                        site, comm['Name'], year)
                                    wx.MessageBox(
                                        msg, 'Error', wx.OK | wx.ICON_ERROR)
                            else:
                                success = False
                                wx.MessageBox(ERR.ERRORS[ERR.NO_TS] % (
                                    site, comm['Name'], year),
                                    'Error', wx.OK | wx.ICON_ERROR)
            else:
                success = False
                wx.MessageBox(ERR.ERRORS[ERR.NO_COMM] %
                              site, 'Error', wx.OK | wx.ICON_ERROR)

            processes = {k: v for k, v in m._processes.items()
                         if v['Type'] == 'Process'}
            if len(processes) == 0:
                success = False
                wx.MessageBox(ERR.ERRORS[ERR.NO_PROC] %
                              site, 'Error', wx.OK | wx.ICON_ERROR)

        return success

    def Run(self):

        result_name = self._resModel.GetResultName()
        result_dir = urbs.prepare_result_directory(
            result_name,
            config.DataConfig.RESULT_DIR)  # name + time stamp

        #  copy input file to result directory
        #  shutil.copyfile(input_file, os.path.join(result_dir, input_file))
        #  copy runme.py to result directory
        #  shutil.copyfile(__file__, os.path.join(result_dir, __file__))

        #  Choose Solver (cplex, glpk, gurobi, ...)
        # Solver = 'gurobi'
        Solver = self._resModel.GetSolver()

        #  objective function
        #  set either 'cost' or 'CO2' as objective
        objective = self._resModel.GetObjective()

        #  simulation timesteps
        (offset, length) = self._resModel.GetTimeStepTuple()
        # print((offset, length))
        timesteps = range(offset, offset + length + 1)
        dt = self._resModel.GetDT()
        # print(dt)

        #  plotting commodities/sites
        plot_tuples = self._resModel.GetPlotTuples()

        #  optional: define names for sites in plot_tuples
        plot_sites_name = {}

        #  detailed reporting commodity/sites
        report_tuples = self._resModel.GetReportTuples()

        #  optional: define names for sites in report_tuples
        report_sites_name = {}

        #  plotting timesteps
        plot_periods = self._resModel.GetPlotPeriods()
        # print(plot_periods)

        #  add or change plot colors
        my_colors = {
            'South': (230, 200, 200),
            'Mid': (200, 230, 200),
            'North': (200, 200, 230)}
        for country, color in my_colors.items():
            urbs.COLORS[country] = color

        for m in self._resModel._models.values():
            for p in m._processes.values():
                if p['Type'] == 'Process':  # not storage
                    color = wx.Colour()
                    color.Set(p['PlotColor'])
                    urbs.COLORS[p['Name']] = color.Get(False)

        #  select scenarios to be run
        t_start = time.time()
        data = self._resModel.GetDataFrames()
        t_read = time.time() - t_start
        print("Time to build data frames: %.2f sec" % t_read)
        wx.Yield()

        scenarios = []
        for k, v in config.DataConfig.SCENARIOS.items():
            if k in self._resModel._scenarios:
                scenarios.append(v)

        # save config file
        self.OnSaveConfig(result_dir + "/config.json")

        # print(scenarios)
        for scenario in scenarios:
            # print(scenario)
            urbs.run_scenario_df(
                data,
                Solver,
                timesteps,
                scenario,
                result_dir,
                dt,
                objective,
                plot_tuples=plot_tuples,
                plot_sites_name=plot_sites_name,
                plot_periods=plot_periods,
                report_tuples=report_tuples,
                report_sites_name=report_sites_name)
