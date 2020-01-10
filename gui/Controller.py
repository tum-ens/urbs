# -*- coding: utf-8 -*-
"""
@author: amrelshahawy
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
import win32api
import json
import time
import urbs
import wx

import ConvertToJSON
import os

from pubsub import pub
from Events import EVENTS


class Controller:
    """From its name, this the controller part in the MVC architecture. The
    Controller mainly facilitate the communication between the Model and other
    views. There is no core logic inside the controller itself.
        """

    def __init__(self):
        """Instantiate the controller object.

            It creates the main view and the model instances.
            subscribe on the user events and handle them accordingly.
        """

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
        pub.subscribe(self.OnImportConfig, EVENTS.IMPORT_CONFIG)

        pub.subscribe(self.AddScenario, EVENTS.SCENARIO_ADDED)
        pub.subscribe(self.RemoveScenario, EVENTS.SCENARIO_REMOVED)

        pub.subscribe(self.OnCopyClick, EVENTS.ITEM_COPY)
        pub.subscribe(self.CopyItem, EVENTS.ITEM_COPIED)
        pub.subscribe(self.DeleteItem, EVENTS.ITEM_DELETE)
        pub.subscribe(self.CloneItem, EVENTS.ITEM_CLONE)

    def AddSite(self, site):
        """The method is triggered when the user wants to add a new site.

        Args:
            site: the site name

        Returns:
            An Error could be returned if a site with the same name already
            exist.
        """

        status = self._resModel.AddSite(site)
        if status == 1:
            wx.MessageBox('A Site with the same name already exist!', 'Error',
                          wx.OK | wx.ICON_ERROR)
        else:
            self._view.AddRESTab(self, site)
            self._view.Refresh(False)

    def RemoveSites(self, sites):
        """The method is triggered when the user wants to remove one or more
        site.

        Args:
            sites: list of site names
        """
        s = wx.MessageBox('Are you sure? All site(s) data will be lost!',
                          'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if s == wx.OK:
            self._resModel.RemoveSites(sites)
            self._view.RemoveRESTab(sites)

    def AddPeriod(self, period):
        """The method is triggered when the user wants to add a new period.

        Args:
            period: the period name

        Returns:
            An Error could be returned if a period with the same name already
            exist.
        """
        status = self._resModel.AddPeriod(period)
        if status == 1:
            wx.MessageBox('A Period with the same name already exist!',
                          'Error', wx.OK | wx.ICON_ERROR)

    def RemovePeriods(self, periods):
        """The method is triggered when the user wants to remove one or more
        period.

        Args:
            periods: list of period names
        """
        s = wx.MessageBox('Are you sure? ', 'Warning',
                          wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if s == wx.OK:
            self._resModel.RemovePeriods(periods)

    def RESSelected(self, siteName):
        """When the user select one of the site(s) tab, the current active
        model will be the one belongs to this site.

        Args:
            siteName: the name of the selected site
        """
        self._model = self._resModel.GetSiteModel(siteName)

    def AddYear(self, year):
        """The method is triggered when the user wants to add a new year.

        Args:
            year: four digits number represent the year
        """
        self._resModel.AddYear(year)

    def RemoveYears(self, years):
        """The method is triggered when the user wants to remove one or more
        years.

        Args:
            years: list of years to remove
        """
        s = wx.MessageBox('Are you sure? All year(s) data will be lost!',
                          'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if s == wx.OK:
            self._resModel.RemoveYears(years)

    def AddCommodity(self, commType):
        """The method is triggered when the user try to add a new commodity to
        the model.

        Args:
            commType: The type of the commodity (ex: Buy, Sell etc...)
        """
        comm = self._model.CreateNewCommodity(commType)
        self._comForm = commf.CommodityDialog(self._view)
        self._comForm.PopulateCommodity(comm)
        self._comForm.ShowModal()

    def EditCommodity(self, commId):
        """The method is triggered when the user try to edit an existing
        commodity. Each commodity has a unique Id.

        Args:
            commId: The Id of the commodity.
        """
        comm = self._model.GetCommodity(commId)
        if comm:
            self._comForm = commf.CommodityDialog(self._view)
            self._comForm.PopulateCommodity(comm)
            self._comForm.ShowModal()

    def SaveCommodity(self, data):
        """The method is triggered when the user press OK to save the changes
        he/she made while adding/updating a commodity. All the changes are
        NOT reflected immediately until the user press OK in the view.

        Args:
            data: a dictionary with the commodity information.

        Returns:
            An Error could be returned if a commodity with the same name already
            exist.
        """
        status = self._model.SaveCommodity(data)
        if status:
            self._comForm.Close()
        else:
            wx.MessageBox('A Commodity with the same name already exist!',
                          'Error', wx.OK | wx.ICON_ERROR)

    def AddProcess(self):
        """The method is triggered when the user try to add a new process to
        the model.
        """
        newProcess = self._model.CreateNewProcess()
        self._processForm = procf.ProcessDialog(self._view)
        self._processForm.PopulateProcess(
            newProcess, self._model.GetCommodityList())
        self._processForm.ShowModal()

    def SaveProcess(self, data):
        """The method is triggered when the user press OK to save the changes
        he/she made while adding/updating a process. All the changes are
        NOT reflected immediately until the user press OK in the view.

        Args:
            data: a dictionary with the process information.

        Returns:
            An Error could be returned if:

            - A process with the same name already exist.
            - The process is not connected to in/out commodities.
        """
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
        """The method is triggered when the user try to edit an existing
        process. Each process has a unique Id.

        Args:
            processId: The Id of the process.
        """
        process = self._model.GetProcess(processId)
        self._processForm = procf.ProcessDialog(self._view)
        self._processForm.PopulateProcess(
            process, self._model.GetCommodityList())
        self._processForm.ShowModal()

    def AddStorage(self):
        """The method is triggered when the user try to add a new storage to
        the model.
        """
        newStorage = self._model.CreateNewStorage()
        self._storageForm = strgf.StorageDialog(self._view)
        self._storageForm.PopulateStorage(
            newStorage, self._model.GetCommodityList())
        self._storageForm.ShowModal()

    def SaveStorage(self, data):
        """The method is triggered when the user press OK to save the changes
        he/she made while adding/updating a storage. All the changes are
        NOT reflected immediately until the user press OK in the view.

        Args:
            data: a dictionary with the storage information.

        Returns:
            An Error could be returned if:

            - A storage with the same name already exist.
            - The storage is not connected to a commodity
        """
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
        """The method is triggered when the user try to edit an existing
        storage. Each storage has a unique Id.

        Args:
            storageId: The Id of the process.
        """
        storage = self._model.GetStorage(storageId)
        self._storageForm = strgf.StorageDialog(self._view)
        self._storageForm.PopulateStorage(
            storage, self._model.GetCommodityList())
        self._storageForm.ShowModal()

    def EditConnection(self, procId, commId, In_Out):
        """The method is triggered when the user try to edit an existing
        connection. A connection is an edge between process/storage and a
        commodity. The connection is identified by the process, the commodity,
        the direction of the connection (IN or OUT).

        Args:
            - procId: The Id of the process.
            - commId: The Id of the commodity.
            - In_Out: The direction of the connection.
        """
        connection = self._model.GetConnection(procId, commId, In_Out)
        connForm = connf.ConnectionDialog(self._view)
        connForm.PopulateConnectionGrid(connection)
        connForm.ShowModal()

    def GetCommodities(self, siteName):
        """The method is used to retrieve all commodities associated with a
        specific site.

        Args:
            siteName: The name of the current active site (tab).

        Returns:
            A list of commodities
        """
        m = self._resModel.GetSiteModel(siteName)
        return m._commodities

    def GetProcesses(self):
        """The method is used to retrieve all processes associated with the
        current active site (tab).

        Returns:
            list of process
        """
        return self._model._processes

    def GetLinkedProcesses(self, siteName, commName):
        """The method is used to retrieve all processes linked to a specific
        commodity for a certain site.

        Args:
            - siteName: The name of the current active site (tab).
            - commName: The commodity name.

        Returns:
            A list of commodities
        """
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
        """The method is triggered when the user try to add a new Transmission
        line.
        """
        newTrns = self._resModel.CreateNewTrnsm()
        self._trnsForm = tf.TransmissionDialog(self._view, self)
        self._trnsForm.PopulateTrans(newTrns, self._resModel.GetSites())
        self._trnsForm.ShowModal()

    def SaveTransmission(self, data):
        """The method is triggered when the user press OK to save the changes
        he/she made while adding/updating a transmission. All the changes are
        NOT reflected immediately until the user press OK in the view.

        Args:
            data: a dictionary with the transmission information.

        Returns:
            An Error could be returned if a transmission with the same name
            already exist.
        """
        status = self._resModel.SaveTransmission(data)
        if status:
            self._trnsForm.Close()
        else:
            wx.MessageBox(
                'A Transmission line with the same name already exist!',
                'Error',
                wx.OK | wx.ICON_ERROR)

    def EditTransmission(self, trnsmId):
        """The method is triggered when the user try to edit an existing
        transmission. Each transmission has a unique Id.

        Args:
            trnsmId: The Id of the process.
        """
        trnsm = self._resModel.GetTransmission(trnsmId)
        self._trnsForm = tf.TransmissionDialog(self._view, self)
        self._trnsForm.PopulateTrans(trnsm, self._resModel.GetSites())
        self._trnsForm.ShowModal()

    def GetTransmissions(self):
        """The method is used to retrieve all transmissions.

        Returns:
            list of transmissions
        """
        return self._resModel._transmissions

    def GetTrnsmCommodities(self):
        """The method is used to retrieve the commodities used any transmission
        line.

        Returns:
            list of commodities
        """
        return self._resModel._trnsmCommodities

    def GetCommonCommodities(self, site1, site2):
        """The method is used to get the common commodities between two sites.

        Args:
            - site1: the name of the site.
            - site2: the name of the other site.

        Returns:
            A list of commodities that are in common.
        """
        m1 = self._resModel.GetSiteModel(site1)
        m2 = self._resModel.GetSiteModel(site2)

        c1 = set([x['Name'] for x in m1._commodities.values()])
        c2 = set([x['Name'] for x in m2._commodities.values()])

        mergedSet = c1 & c2
        return list(mergedSet)

    def OnItemDoubleClick(self, itemId, itemType):
        """The method is triggered when the user double click on an object/item
        in the view. The controller calls the proper method based on the item
        type.

        Args:
            - itemId: The Id of the clicked item.
            - itemType: The type of the clicked item (Process, Storage,
              Commodity or Transmission).
        """
        if itemType == 'Commodity':
            self.EditCommodity(itemId)
        elif itemType == 'Process':
            self.EditProcess(itemId)
        elif itemType == 'Storage':
            self.EditStorage(itemId)
        elif itemType == 'Trnsm':
            self.EditTransmission(itemId)

    def OnItemMove(self, item):
        """The method is triggered when the user try to move an object/item in
        the view.

        Args:
            item: a dictionary with the item data.
        """
        if item.GetType() == 'Trnsm':
            pub.sendMessage(EVENTS.TRNSM_ITEM_MOVED, item=item)
        else:
            pub.sendMessage(EVENTS.ITEM_MOVED +
                            self._model.GetSiteName(), item=item)

    def SerializeObj(self, obj):
        """The method is used to get any object as dictionary (key/value pairs).
        This is used in saving the configuration file.

        Returns:
            dictionary contains the object attributes.
        """
        # print(obj)
        if isinstance(obj, wx.Colour):
            return obj.GetAsString()

        return obj.__dict__

    def OnSaveConfig(self, filename):
        """The method is triggered when the user save his/her work as
        configuration file.

        Args:
            filename: the name of the file
        """
        with open(filename, 'w') as fp:
            json.dump(self._resModel, fp, default=self.SerializeObj, indent=2)

    def OnImportConfig(self, filename):
        # Import function calls converter script with a list of filepaths
        # and the first path in the list as output filename
        # onLoadConfig loads the converted file and updates the gui
        if len(filename) > 1:
            stems = [os.path.basename(os.path.splitext(path)[0]) for path in filename[1:]]
            stems.insert(0,os.path.splitext(filename[0])[0])
            savename = '_'.join(stems) + '.json'
        else:
            savename = os.path.splitext(filename[0])[0] + '.json'
        ConvertToJSON.convert_to_json(filename, json_filename = savename)
        pub.sendMessage(EVENTS.LOAD_CONFIG, filename = savename)

    def OnLoadConfig(self, filename):
        """The method is triggered when the user try to load a configuration
        file. It reconstruct the model and the necessary views based on the
        saved configurations.

        Args:
            filename: the name of the file
        """
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
        """The method is used to get the data for the global parameters view.

        Returns:
            dictionary with the global parameters (key/value pairs)
        """
        return self._resModel.GetGlobalParams()

    def GetScenarios(self):
        """The method is used to get the list of scenarios that the user can
        select among them.

        Returns:
            A list of scenarios names
        """
        return sorted(config.DataConfig.SCENARIOS.keys())

    def AddScenario(self, scName):
        """The method is triggered when the user select (check) a scenario in
        the main view.

        Args:
            scName: the name of the scenario
        """
        self._resModel.AddScenario(scName)

    def RemoveScenario(self, scName):
        """The method is triggered when the user deselect (uncheck) a scenario
        in the main view.

        Args:
            scName: the name of the scenario
        """
        self._resModel.RemoveScenario(scName)

    def OnCopyClick(self, item):
        """The method is triggered when the user try to copy an item from site
        to another. If there is more than one site, the user will get a form
        with other sites to select among them. Otherwise, he/she will get an
        error message indicate that there is only one site defined.

        Args:
            item: the item (Commodity, Process or Storage) to copy
        """
        sites = [x for x in self._resModel.GetSites() if x !=
                 self._model.GetSiteName()]
        if len(sites) > 0:
            self._sitesForm = sf.SitesDialog(self._view, sites, item)
            self._sitesForm.ShowModal()
        else:
            wx.MessageBox(ERR.ERRORS[ERR.ONE_SITE],
                          'Error', wx.OK | wx.ICON_ERROR)

    def CopyItem(self, item, sites):
        """The method is used to copy an item to other sites. It check if the
        item (Process or Storage) is already copied before.

        Args:
            - item: the item (Commodity, Process or Storage) to copy
            - sites: list of sites to copy to
        """
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
        """The method is triggered when the user try to delete an item. If the
        item is Commodity, then we check if the item is used by a Transmission
        line. If os, we prevent the deletion of the item.

        Args:
            item: the item (Commodity, Process or Storage) to delete
        """
        deleted = False
        if item['Type'] in ('Process', 'Storage'):
            self._model.RemoveProcess(item['Id'])
            deleted = True
        else:
            # check if the commodity is used by any transmission
            for trns in self._resModel._transmissions.values():
                if trns['CommName'] == item['Name']:
                    # can not be deleted, just return
                    wx.MessageBox(
                          'This commodity can NOT be deleted as it is used by '
                          'the transmission "%s".' % trns['Name'],
                          'Error', wx.OK | wx.ICON_ERROR)
                    return

            s = wx.MessageBox(
                  'If a process is connected only to this commodity '
                  '(i.e. not connected to any other commodities), '
                  'then this process will be also deleted. '
                  'Do you want to proceed?', 'Warning',
                  wx.OK | wx.CANCEL | wx.ICON_WARNING)

            if s == wx.OK:
                self._model.RemoveCommodity(item['Id'])
                deleted = True

        if deleted:
            pub.sendMessage(EVENTS.ITEM_DELETED +
                            self._model.GetSiteName(), objId=None)

    def CloneItem(self, item):
        """The method is similar to copy item but within the same site.

        Args:
            item: the item (Commodity, Process or Storage) to clone
        """
        if item['Type'] in ('Process', 'Storage'):
            self._model.CloneProcess(cpy.deepcopy(item))
        else:
            self._model.CloneCommodity(cpy.deepcopy(item))

    def ValidateData(self):
        """The method is used to do some set of validation before running the
        solver to detect the errors in early stage. It's mainly do the following
        validations:
            - At least one year is defined.
            - At least one site is defined.
            - At least one scenario is selected.
            - At least once Commodity is defined.
            - If the commodity is of type "SupIm", then the time series should
              be defined.
            - At least one process is defined.
        """
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
        """The method is used to do run 'urbs' to solve the problem. It simply
        get the necessary info from the model and execute for evey selected
        scenario.
        """
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
                win32api.GetShortPathName(result_dir),
                dt,
                objective,
                plot_tuples=plot_tuples,
                plot_sites_name=plot_sites_name,
                plot_periods=plot_periods,
                report_tuples=report_tuples,
                report_sites_name=report_sites_name)
