# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 11:28:37 2018

@author: aelshaha
"""

from pubsub import pub
from Events import EVENTS

import DataConfig as config
import SiteModel as sm
import pandas as pd
import math


class RESModel():

    def __init__(self, data=None):
        self._years = {}
        self._sites = {}
        self._periods = {}
        self._models = {}
        self._transmissions = {}
        self._trnsmCommodities = {}
        self._gl = self.InitializeGlobalParams()
        self._scenarios = []
        if data:
            if '_scenarios' in data:
                self._scenarios = data['_scenarios']
                pub.sendMessage(EVENTS.SCENARIOS_LOADED,
                                scenarios=self._scenarios)
            if '_gl' in data:
                self._gl = data['_gl']
                pub.sendMessage(EVENTS.GL_PARAMS_LOADED, gl=self._gl)
            if '_sites' in data:
                self._sites = data['_sites']
                pub.sendMessage(EVENTS.SITE_ADDED, sites=self._sites)
            if '_years' in data:
                self._years = data['_years']
                pub.sendMessage(EVENTS.YEAR_ADDED, years=self._years)
            if '_transmissions' in data:
                self._transmissions = data['_transmissions']
            if '_trnsmCommodities' in data:
                self._trnsmCommodities = data['_trnsmCommodities']
            if '_periods' in data:
                self._periods = data['_periods']
                pub.sendMessage(EVENTS.PERIOD_ADDED, periods=self._periods)
            if '_models' in data:
                for k, v in data['_models'].items():
                    self._models[k] = sm.SiteModel(k,
                                                   sorted(self._years.keys()),
                                                   v['_commodities'],
                                                   v['_processes'],
                                                   v['_connections']
                                                   )
# ----------------------------------------------------------------------------#

    def InitializeGlobalParams(self):
        data = {}
        for p in config.DataConfig.GLOBAL_PARAMS:
            key = p[config.DataConfig.PARAM_KEY]
            v = {}
            for col in config.DataConfig.GLOBAL_COLS:
                colKey = col[config.DataConfig.PARAM_KEY]
                v[colKey] = p[config.DataConfig.PARAM_DEFVALUE]
            data[key] = v

        return data
# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------------------#

    def InitializeSite(self, name):
        return sm.SiteModel.InitializeData(config.DataConfig.SITE_PARAMS)
# ----------------------------------------------------------------------------#

    def AddSite(self, siteName):
        status = 0
        if not (siteName in self._sites):
            self._sites[siteName] = self.InitializeSite(siteName)
            self._models[siteName] = sm.SiteModel(
                siteName, list(self._years.keys()))
            # notify subscribers that a site is added
            pub.sendMessage(EVENTS.SITE_ADDED, sites=self._sites)
        else:
            status = 1

        return status
# ----------------------------------------------------------------------------#

    def RemoveSites(self, sites):
        notify = 0
        for site in sites:
            self._sites.pop(site)
            self._models.pop(site)
            notify += 1

        # notify subscribers that a site is removed
        if notify > 0:
            pub.sendMessage(EVENTS.SITE_REMOVED,
                            sites=self._sites, removeCount=notify)
# ----------------------------------------------------------------------------#

    def GetSites(self):
        return sorted(self._sites.keys())
# ----------------------------------------------------------------------------#

    def InitializeYear(self):
        return sm.SiteModel.InitializeData(config.DataConfig.YEAR_PARAMS)
# ----------------------------------------------------------------------------#

    def AddYear(self, year):
        if not (year in self._years):
            self._years[year] = self.InitializeYear()
            for m in self._models.values():
                m.AddYear(year)
            for v in self._transmissions.values():
                v['Years'][year] = sm.SiteModel.InitializeData(
                    config.DataConfig.TRANS_PARAMS)

            # notify subscribers that a year is added
            pub.sendMessage(EVENTS.YEAR_ADDED, years=self._years)
# ----------------------------------------------------------------------------#

    def RemoveYears(self, years):
        for year in years:
            self._years.pop(year)
            for m in self._models.values():
                m.RemoveYear(year)

        # notify subscribers that years are removed
        pub.sendMessage(EVENTS.YEAR_REMOVED, years=self._years,
                        removeCount=len(years))
# ----------------------------------------------------------------------------#

    def AddPeriod(self, pName):
        status = 0
        if not (pName in self._periods):
            newP = sm.SiteModel.InitializeData(config.DataConfig.PERIOD_PARAMS)
            self._periods[pName] = newP
            # notify subscribers that a period is added
            pub.sendMessage(EVENTS.PERIOD_ADDED, periods=self._periods)
        else:
            status = 1

        return status
# ----------------------------------------------------------------------------#

    def RemovePeriods(self, periods):
        notify = 0
        for p in periods:
            self._periods.pop(p)
            notify += 1

        # notify subscribers that a period is removed
        if notify > 0:
            pub.sendMessage(EVENTS.PERIOD_REMOVED,
                            periods=self._periods, removeCount=notify)
# ----------------------------------------------------------------------------#

    def GetSiteModel(self, siteName):
        return self._models[siteName]
# ----------------------------------------------------------------------------#

    def GetGlobalParams(self):
        return self._gl
# ----------------------------------------------------------------------------#

    def AddScenario(self, scName):
        self._scenarios.append(scName)
# ----------------------------------------------------------------------------#

    def RemoveScenario(self, scName):
        self._scenarios.remove(scName)
# ----------------------------------------------------------------------------#

    def CreateNewTrnsm(self):
        trnsId = 'NewTrnsm#' + str(len(self._transmissions) + 1)
        data = {}
        data['SiteIn'] = ''
        data['SiteOut'] = ''
        data['CommName'] = ''
        data['Years'] = {}
        data['Id'] = trnsId
        data['Name'] = trnsId
        data['Type'] = 'Trnsm'
        for year in self._years:
            data['Years'][year] = sm.SiteModel.InitializeData(
                config.DataConfig.TRANS_PARAMS)

        return data
# ----------------------------------------------------------------------------#

    def SaveTransmission(self, data):
        trnsmId = data['Id']
        trnsmName = data['Name']
        success = True
        for v in self._transmissions.values():
            if v['Name'] == trnsmName and v['Id'] != trnsmId:
                success = False
                break
        if success:
            self.SaveTrnsmCommodities(data)
            if trnsmId not in self._transmissions:
                self._transmissions[trnsmId] = data
                pub.sendMessage(EVENTS.TRNSM_ADDED, objId=trnsmId)
            else:
                pub.sendMessage(EVENTS.TRNSM_EDITED, objId=trnsmId)

        return success
# ----------------------------------------------------------------------------#

    def SaveTrnsmCommodities(self, data):
        # In part
        commInId = data['SiteIn'] + '.' + data['CommName']
        m = self._models[data['SiteIn']]
        commIn = m.GetCommByName(data['CommName'])
        self._trnsmCommodities[commInId] = commIn
        data['IN'] = [commInId]

        # out part
        commOutId = data['SiteOut'] + '.' + data['CommName']
        m = self._models[data['SiteOut']]
        commOut = m.GetCommByName(data['CommName'])
        self._trnsmCommodities[commOutId] = commOut
        data['OUT'] = [commOutId]
# ----------------------------------------------------------------------------#

    def GetTransmission(self, trnsmId):
        return self._transmissions[trnsmId]
# ----------------------------------------------------------------------------#

    def CreateDF(self, tuples, names, columns, values):
        index = None
        if len(tuples) > 0:
            index = pd.MultiIndex.from_tuples(tuples, names=names)
            lvls = [index.levels[0].astype(float)]
            for l in index.levels[1:]:
                lvls.append(l)
            index = index.set_levels(lvls)
        else:
            labels = []
            for n in names:
                labels.append([])
            index = pd.MultiIndex(codes=labels, levels=labels, names=names)
            # print(index)

        df = pd.DataFrame(values, columns=columns, index=index)
        if len(values) > 0:
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])

        # print(df.info())
        return df
# ----------------------------------------------------------------------------#

    def GetGlobalDF(self):
        tuples = []
        values = []
        key = config.DataConfig.PARAM_KEY
        colKey = config.DataConfig.GLOBAL_COLS[0][key]
        years = sorted(self._years.keys())
        for year in years:
            if year == years[0]:
                # Discount rate
                prop = config.DataConfig.GLOBAL_PARAMS[0][key]
                tuples.append((year, prop))
                values.append(self._gl[prop][colKey])
                # co2 budget
                prop = config.DataConfig.GLOBAL_PARAMS[1][key]
                tuples.append((year, prop))
                values.append(self._gl[prop][colKey])
                # Cost budget
                prop = config.DataConfig.GLOBAL_PARAMS[2][key]
                tuples.append((year, prop))
                values.append(self._gl[prop][colKey])
            data = self._years[year]
            for k, v in data.items():
                # skip 'selected'
                if k == config.DataConfig.YEAR_PARAMS[0][key]:
                    continue

                tuples.append((year, k))
                values.append(v)
            if year == years[-1]:
                # Weight
                param = config.DataConfig.GLOBAL_PARAMS[3]
                paramKey = param[config.DataConfig.PARAM_KEY]
                tuples.append((year, paramKey))
                values.append(self._gl[paramKey][colKey])

        names = ['support_timeframe', 'Property']
        return self.CreateDF(tuples, names, [colKey], values)
# ----------------------------------------------------------------------------#

    def GetSitesDF(self):
        tuples = []
        values = []
        columns = ['area']
        years = sorted(self._years.keys())
        for year in years:
            for site, data in self._sites.items():
                tuples.append((year, site))
                for col in columns:
                    values.append(data[col])

        names = ['support_timeframe', 'Name']
        df = self.CreateDF(tuples, names, columns, values)
        # print(df)
        return df
# ----------------------------------------------------------------------------#

    def GetCommoditiesDF(self):
        tuples = []
        values = []
        columns = ['price', 'max', 'maxperhour']
        years = sorted(self._years.keys())
        for year in years:
            for site, m in self._models.items():
                ids = sorted(m._commodities.keys())
                for k in ids:
                    comm = m._commodities[k]
                    t = (year, site, comm['Name'], comm['Type'])
                    tuples.append(t)
                    data = comm['Years'][year]
                    v = []
                    for col in columns:
                        s = data[col]
                        if comm['Type'] in (config.DataConfig.COMM_SUPIM,
                                            config.DataConfig.COMM_DEMAND):
                            s = math.nan
                        v.append(s)
                    values.append(v)

        names = ['support_timeframe', 'Site', 'Commodity', 'Type']
        return self.CreateDF(tuples, names, columns, values)
# ----------------------------------------------------------------------------#

    def GetProcessesDF(self):
        tuples = []
        values = []
        columns = []
        for c in config.DataConfig.PROCESS_PARAMS:
            columns.append(c[config.DataConfig.PARAM_KEY])
        years = sorted(self._years.keys())
        for year in years:
            for site, m in self._models.items():
                ids = sorted(m._processes.keys())
                for k in ids:
                    p = m._processes[k]
                    if p['Type'] == 'Storage':
                        continue
                    t = (year, site, p['Name'])
                    tuples.append(t)
                    data = p['Years'][year]
                    v = []
                    for col in columns:
                        s = data[col]
                        if (
                            year != years[0] and
                            col in (columns[0], columns[1])
                        ):
                            s = math.nan
                        v.append(s)
                    values.append(v)

        names = ['support_timeframe', 'Site', 'Process']
        return self.CreateDF(tuples, names, columns, values)
# ----------------------------------------------------------------------------#

    def GetStoragesDF(self):
        tuples = []
        values = []
        columns = []
        for c in config.DataConfig.STORAGE_PARAMS:
            columns.append(c[config.DataConfig.PARAM_KEY])
        years = sorted(self._years.keys())
        for year in years:
            for site, m in self._models.items():
                ids = sorted(m._processes.keys())
                for k in ids:
                    strg = m._processes[k]
                    if strg['Type'] != 'Storage':
                        continue
                    commName = m._commodities[strg['IN'][0]]['Name']
                    t = (year, site, strg['Name'], commName)
                    tuples.append(t)
                    data = strg['Years'][year]
                    v = []
                    for col in columns:
                        s = data[col]
                        if year != years[0] and col in ('inst-cap-c',
                                                        'inst-cap-p',
                                                        'lifetime'):
                            s = math.nan
                        v.append(s)
                    values.append(v)

        names = ['support_timeframe', 'Site', 'Storage', 'Commodity']
        df = self.CreateDF(tuples, names, columns, values)
        # print(df)
        return df
# ----------------------------------------------------------------------------#

    def GetConnectionsDF(self):
        tuples = []
        values = []
        columns = []
        for c in config.DataConfig.CONNECTION_PARAMS:
            columns.append(c[config.DataConfig.PARAM_KEY])
        years = sorted(self._years.keys())
        for year in years:
            for site, m in self._models.items():
                ids = sorted(m._connections.keys())
                for k in ids:
                    conn = m._connections[k]
                    t = (year,
                         m._processes[conn['Proc']]['Name'],
                         m._commodities[conn['Comm']]['Name'],
                         conn['Dir'].title())
                    if t in tuples:
                        continue
                    tuples.append(t)
                    data = conn['Years'][year]
                    v = []
                    for col in columns:
                        v.append(data[col])
                    values.append(v)

        names = ['support_timeframe', 'Process', 'Commodity', 'Direction']
        df = self.CreateDF(tuples, names, columns, values)
        # print(df)
        return df
# ----------------------------------------------------------------------------#

    def GetCommTimeSerDF(self, commTypes, includSite=True):
        # columns
        data = {}
        for site, m in self._models.items():
            ids = sorted(m._commodities.keys())
            for k in ids:
                comm = m._commodities[k]
                if comm['Type'] not in commTypes:
                    continue
                col = comm['Name']
                if includSite:
                    col = site + '.' + col
                data[col] = comm
        # tuples
        years = sorted(self._years.keys())
        t = range(0, config.DataConfig.TS_LEN)
        tuples = [(x, y) for x in years for y in t]
        names = ['support_timeframe', 't']
        df = self.CreateDF(tuples, names, [], [])
        for col, comm in data.items():
            v = []
            for year in years:
                timeSer = comm['Years'][year]['timeSer']
                entries = timeSer.split('|')
                v = v + entries
            df[col] = pd.Series(v, index=df.index, dtype=float)

        if includSite and len(df.columns) > 0:
            column_tuples = [tuple(col.split('.')) for col in df.columns]
            df.columns = pd.MultiIndex.from_tuples(column_tuples)

        return df
# ----------------------------------------------------------------------------#

    def GetDemandTimeSerDF(self):
        return self.GetCommTimeSerDF([config.DataConfig.COMM_DEMAND])
# ----------------------------------------------------------------------------#

    def GetSupImTimeSerDF(self):
        return self.GetCommTimeSerDF([config.DataConfig.COMM_SUPIM])
# ----------------------------------------------------------------------------#

    def GetBuySellTimeSerDF(self):
        commTypes = [config.DataConfig.COMM_BUY, config.DataConfig.COMM_SELL]
        return self.GetCommTimeSerDF(commTypes, False)
# ----------------------------------------------------------------------------#

    def GetDsmDF(self):
        tuples = []
        values = []
        columns = []
        for c in config.DataConfig.DSM_PARAMS:
            columns.append(c[config.DataConfig.PARAM_KEY])
        years = sorted(self._years.keys())
        for year in years:
            for site, m in self._models.items():
                ids = sorted(m._commodities.keys())
                for k in ids:
                    comm = m._commodities[k]
                    if (
                        comm['Type'] != config.DataConfig.COMM_DEMAND or
                        comm['DSM'] is not True
                    ):
                        continue

                    t = (year, site, comm['Name'])
                    tuples.append(t)
                    data = comm['Years'][year]
                    v = []
                    for col in columns:
                        s = data[col]
                        v.append(s)
                    values.append(v)

        names = ['support_timeframe', 'Site', 'Commodity']
        return self.CreateDF(tuples, names, columns, values)
# ----------------------------------------------------------------------------#

    def GetTrnsmDF(self):
        tuples = []
        values = []
        columns = []
        for c in config.DataConfig.TRANS_PARAMS:
            columns.append(c[config.DataConfig.PARAM_KEY])
        years = sorted(self._years.keys())
        for year in years:
            ids = sorted(self._transmissions.keys())
            for k in ids:
                trnsm = self._transmissions[k]
                t = (year, trnsm['SiteIn'], trnsm['SiteOut'],
                     trnsm['Name'], trnsm['CommName'])
                tuples.append(t)
                t = (year, trnsm['SiteOut'], trnsm['SiteIn'],
                     trnsm['Name'], trnsm['CommName'])
                tuples.append(t)
                data = trnsm['Years'][year]
                v = []
                for col in columns:
                    s = data[col]
                    if year != years[0] and col in ('lifetime'):
                        s = math.nan
                    v.append(s)
                values.append(v)  # SiteIn->SiteOut
                values.append(v)  # SiteOut->SiteIn

        names = ['support_timeframe', 'Site In', 'Site Out',
                 'Transmission', 'Commodity']
        return self.CreateDF(tuples, names, columns, values)
# ----------------------------------------------------------------------------#

    def GetTimeEffDF(self):
        data = {}
        tuples = []
        t = range(0, config.DataConfig.TS_LEN)
        years = sorted(self._years.keys())
        foundYears = []
        for year in years:
            found = False
            for site, m in self._models.items():
                ids = sorted(m._processes.keys())
                for k in ids:
                    p = m._processes[k]
                    if p['Type'] != 'Process':
                        continue
                    timeEff = p['Years'][year]['timeEff']
                    if timeEff != '':
                        found = True
                        col = site + '.' + p['Name']
                        data[col] = p
            if found:
                yearTuples = [(year, x) for x in t]
                tuples = tuples + yearTuples
                foundYears.append(year)

        names = ['support_timeframe', 't']
        df = self.CreateDF(tuples, names, [], [])
        for col, p in data.items():
            v = []
            for year in foundYears:
                timeEff = p['Years'][year]['timeEff']
                entries = timeEff.split('|')
                v = v + entries
            df[col] = pd.Series(v, index=df.index, dtype=float)

        if len(df.columns) > 0:
            column_tuples = [tuple(col.split('.')) for col in df.columns]
            df.columns = pd.MultiIndex.from_tuples(column_tuples)

        return df
# ----------------------------------------------------------------------------#

    def GetDataFrames(self):
        data = {
            'global_prop': self.GetGlobalDF(),
            'site': self.GetSitesDF(),
            'commodity': self.GetCommoditiesDF(),
            'process': self.GetProcessesDF(),
            'process_commodity': self.GetConnectionsDF(),
            'transmission': self.GetTrnsmDF(),
            'storage': self.GetStoragesDF(),
            'demand': self.GetDemandTimeSerDF(),
            'supim': self.GetSupImTimeSerDF(),
            'buy_sell_price': self.GetBuySellTimeSerDF(),
            'dsm': self.GetDsmDF(),
            'eff_factor': self.GetTimeEffDF()
        }

        # sort nested indexes to make direct assignments work
        for key in data:
            if isinstance(data[key].index, pd.core.index.MultiIndex):
                data[key].sort_index(inplace=True)
            # print(data[key].info(verbose=True))
        # print(data['transmission'])
        return data
# ----------------------------------------------------------------------------#

    def GetSolver(self):
        vCol = config.DataConfig.GLOBAL_COLS[0][config.DataConfig.PARAM_KEY]
        return self._gl['Solver'][vCol]
# ----------------------------------------------------------------------------#

    def GetObjective(self):
        vCol = config.DataConfig.GLOBAL_COLS[0][config.DataConfig.PARAM_KEY]
        return self._gl['Objective'][vCol]
# ----------------------------------------------------------------------------#

    def GetTimeStepTuple(self):
        vCol = config.DataConfig.GLOBAL_COLS[0][config.DataConfig.PARAM_KEY]
        return (self._gl['TSOffset'][vCol], self._gl['TSLen'][vCol])
# ----------------------------------------------------------------------------#

    def GetDT(self):
        vCol = config.DataConfig.GLOBAL_COLS[0][config.DataConfig.PARAM_KEY]
        return self._gl['DT'][vCol]
# ----------------------------------------------------------------------------#

    def GetPlotTuples(self):
        tuples = []
        years = sorted(self._years.keys())
        for year in years:
            for site, m in self._models.items():
                for comm in m._commodities.values():
                    plot = False
                    try:
                        plot = comm['Years'][year]['plot']
                    except KeyError:
                        plot = False

                    if plot is True:
                        tuples.append((float(year), site, comm['Name']))
        # print(tuples)
        return tuples
# ----------------------------------------------------------------------------#

    def GetReportTuples(self):
        tuples = []
        years = sorted(self._years.keys())
        for year in years:
            for site, m in self._models.items():
                for comm in m._commodities.values():
                    report = False
                    try:
                        report = comm['Years'][year]['report']
                    except KeyError:
                        report = False

                    if report is True:
                        tuples.append((float(year), site, comm['Name']))
        # print(tuples)
        return tuples
# ----------------------------------------------------------------------------#

    def GetPlotPeriods(self):
        pp = {}
        for k, v in self._periods.items():
            pp[k] = range(v['offset'], v['offset'] + v['length'])

        return pp
# ----------------------------------------------------------------------------#

    def GetResultName(self):
        return self._gl['RsltName']['value']
