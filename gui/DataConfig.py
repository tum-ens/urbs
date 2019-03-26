# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 15:02:37 2018

@author: aelshaha
"""

import wx.grid
import wx._adv
import wx._html
import wx._xml
import math
import os

import sys
sys.path.insert(0, '..')
import urbs  # noqa: E402


class DataConfig():

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    PARAM_KEY = 'key'
    PARAM_DEFVALUE = 'defVal'

    GRID_COL_LABEL = 'col_label'
    GRID_ROW_LABEL = 'row_label'
    GRID_COL_DATATYPE = 'col_dataType'
    GRID_ROW_DATATYPE = 'row_dataType'

    COMM_SUPIM = 'SupIm'
    COMM_BUY = 'Buy'
    COMM_STOCK = 'Stock'
    COMM_DEMAND = 'Demand'
    COMM_SELL = 'Sell'
    COMM_ENV = 'Env'

    TS_BTN_COL = 4
    TS_LEN = 8761

    INF = 'inf'
    NAN = 'nan'
# ----------------------------------------------------------------------------#
    GLOBAL_PARAMS = [{PARAM_KEY: 'Discount rate',
                      GRID_ROW_LABEL: 'Discount rate',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 0.03},
                     {PARAM_KEY: 'CO2 budget',
                      GRID_ROW_LABEL: 'CO2 budget',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 1000000},
                     {PARAM_KEY: 'Cost budget',
                      GRID_ROW_LABEL: 'Cost budget',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 300000000},
                     {PARAM_KEY: 'Weight',
                      GRID_ROW_LABEL: 'Last year weight',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 10},
                     {PARAM_KEY: 'Solver',
                      GRID_ROW_LABEL: 'Solver',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_CHOICE +
                      ':cplex,glpk,gurobi',
                      PARAM_DEFVALUE: 'glpk'},
                     {PARAM_KEY: 'Objective',
                      GRID_ROW_LABEL: 'Objective',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_CHOICE +
                      ':cost,CO2',
                      PARAM_DEFVALUE: 'cost'},
                     {PARAM_KEY: 'TSOffset',
                      GRID_ROW_LABEL: 'Time steps offset',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 1000},
                     {PARAM_KEY: 'TSLen',
                      GRID_ROW_LABEL: 'Time steps length',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 168},
                     {PARAM_KEY: 'DT',
                      GRID_ROW_LABEL: 'Time step (in hours)',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 1},
                     {PARAM_KEY: 'RsltName',
                      GRID_ROW_LABEL: 'Result Name',
                      GRID_ROW_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 'Campus'}]

    GLOBAL_COLS = [
        {PARAM_KEY: 'value',
         GRID_COL_LABEL: 'Value', GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING}
    ]
# ----------------------------------------------------------------------------#

    YEAR_PARAMS = [{PARAM_KEY: 'selected',
                    GRID_COL_LABEL: '',
                    GRID_COL_DATATYPE: wx.grid.GRID_VALUE_BOOL,
                    PARAM_DEFVALUE: ''},
                   {PARAM_KEY: 'CO2 limit',
                    GRID_COL_LABEL: 'CO2 limit',
                    GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                    PARAM_DEFVALUE: INF}]
# ----------------------------------------------------------------------------#
    SITE_PARAMS = [{PARAM_KEY: 'selected',
                    GRID_COL_LABEL: '',
                    GRID_COL_DATATYPE: wx.grid.GRID_VALUE_BOOL,
                    PARAM_DEFVALUE: ''},
                   {PARAM_KEY: 'area',
                    GRID_COL_LABEL: 'Site Area',
                    GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                    PARAM_DEFVALUE: 100000}]
# ----------------------------------------------------------------------------#
    PERIOD_PARAMS = [{PARAM_KEY: 'selected',
                      GRID_COL_LABEL: '',
                      GRID_COL_DATATYPE: wx.grid.GRID_VALUE_BOOL,
                      PARAM_DEFVALUE: ''},
                     {PARAM_KEY: 'offset',
                      GRID_COL_LABEL: 'Offset',
                      GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 1000},
                     {PARAM_KEY: 'length',
                      GRID_COL_LABEL: 'Length',
                      GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                      PARAM_DEFVALUE: 168}]
# ----------------------------------------------------------------------------#

    DSM_PARAMS = [
        # DSM
        {PARAM_KEY: 'delay',
         GRID_COL_LABEL: 'Delay time (h)',
            GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
            PARAM_DEFVALUE: NAN},
        {PARAM_KEY: 'eff',
         GRID_COL_LABEL: 'Efficiency',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: NAN},
        {PARAM_KEY: 'recov',
         GRID_COL_LABEL: 'Recovery time (h)',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: NAN},
        {PARAM_KEY: 'cap-max-do',
         GRID_COL_LABEL: 'Downshift capacity (MWh)',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: NAN},
        {PARAM_KEY: 'cap-max-up',
         GRID_COL_LABEL: 'Upshift capacity (MWh)',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: NAN}
    ]

    COMMODITY_PARAMS = [
        {PARAM_KEY: 'timeSer',
         GRID_COL_LABEL: 'Hidden',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: ''},
        {PARAM_KEY: 'price',
         GRID_COL_LABEL: 'Commodity price (€/MWh)',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: 0.00},
        {PARAM_KEY: 'max',
         GRID_COL_LABEL: 'Maximum commodity use',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: INF},
        {PARAM_KEY: 'maxperhour',
         GRID_COL_LABEL: 'Maximum commodity use per step',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: INF},
        {PARAM_KEY: 'Action',
         GRID_COL_LABEL: 'Time S.',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING, PARAM_DEFVALUE: '...'}
    ] + DSM_PARAMS + [
        ########
        {PARAM_KEY: 'plot',
         GRID_COL_LABEL: 'Plot',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_BOOL, PARAM_DEFVALUE: ''},
        {PARAM_KEY: 'report',
         GRID_COL_LABEL: 'Report',
         GRID_COL_DATATYPE: wx.grid.GRID_VALUE_BOOL, PARAM_DEFVALUE: ''}

    ]

    COMMODITY_COLS = [{PARAM_KEY: 'selected',
                       GRID_COL_LABEL: '',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_BOOL,
                       PARAM_DEFVALUE: ''},
                      {PARAM_KEY: 'Name',
                       GRID_COL_LABEL: 'Name',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: ''},
                      {PARAM_KEY: 'Action',
                       GRID_COL_LABEL: '',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: '...'}]
# ----------------------------------------------------------------------------#
    PROCESS_PARAMS = [{PARAM_KEY: 'inst-cap',
                       GRID_COL_LABEL: 'Installed capacity (MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'lifetime',
                       GRID_COL_LABEL: 'Lifetime of inst-cap (years)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'cap-lo',
                       GRID_COL_LABEL: 'Minimum capacity (MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'cap-up',
                       GRID_COL_LABEL: 'Maximum capacity (MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'max-grad',
                       GRID_COL_LABEL: 'Maximum power gradient (1/h)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: INF},
                      {PARAM_KEY: 'min-fraction',
                       GRID_COL_LABEL: 'Minimum load fraction',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'inv-cost',
                       GRID_COL_LABEL: 'Investment cost (€/MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'fix-cost',
                       GRID_COL_LABEL: 'Annual fix cost (€/MW/a)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'var-cost',
                       GRID_COL_LABEL: 'Variable costs (€/MWh)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'wacc',
                       GRID_COL_LABEL: 'Weighted average cost of capital',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.05},
                      {PARAM_KEY: 'depreciation',
                       GRID_COL_LABEL: 'Depreciation period (a)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 20},
                      {PARAM_KEY: 'area-per-cap',
                       GRID_COL_LABEL: 'Area use per capacity (m^2/MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: NAN}]

    PROCESS_COLS = [{PARAM_KEY: 'timeEff',
                     GRID_COL_LABEL: 'Hidden',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: ''}
                    ] + PROCESS_PARAMS + [{
                        PARAM_KEY: 'Action',
                        GRID_COL_LABEL: 'Time Eff.',
                        GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                        PARAM_DEFVALUE: '...'}
    ]
# ----------------------------------------------------------------------------#
    CONNECTION_PARAMS = [{PARAM_KEY: 'ratio',
                          GRID_COL_LABEL: 'Ratio (1)',
                          GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                          PARAM_DEFVALUE: 1.00},
                         {PARAM_KEY: 'ratio-min',
                          GRID_COL_LABEL: 'Ratio-Min',
                          GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                          PARAM_DEFVALUE: math.nan}]
# ----------------------------------------------------------------------------#
    STORAGE_PARAMS = [{PARAM_KEY: 'inst-cap-c',
                       GRID_COL_LABEL: 'Installed capacity (MWh)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'cap-lo-c',
                       GRID_COL_LABEL: 'Minimum capacity (MWh)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'cap-up-c',
                       GRID_COL_LABEL: 'Maximum capacity (MWh)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'inst-cap-p',
                       GRID_COL_LABEL: 'Installed storage power (MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'cap-lo-p',
                       GRID_COL_LABEL: 'Minimum power (MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'cap-up-p',
                       GRID_COL_LABEL: 'Maximum power (MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'eff-in',
                       GRID_COL_LABEL: 'Efficiency input (1)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 1.00},
                      {PARAM_KEY: 'eff-out',
                       GRID_COL_LABEL: 'Efficiency output (1)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 1.00},
                      {PARAM_KEY: 'inv-cost-p',
                       GRID_COL_LABEL: 'Investment cost power (€/MW)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'inv-cost-c',
                       GRID_COL_LABEL: 'Investment cost cap. (€/MWh)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'fix-cost-p',
                       GRID_COL_LABEL: 'Fix cost power (€/MW/a)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'fix-cost-c',
                       GRID_COL_LABEL: 'Fix cost capacity (€/MWh/a)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'var-cost-p',
                       GRID_COL_LABEL: 'Variable cost in/out (€/MWh)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'var-cost-c',
                       GRID_COL_LABEL: 'Variable cost cap. (€/MWh)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'lifetime',
                       GRID_COL_LABEL: 'Lifetime inst-cap (years)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      {PARAM_KEY: 'depreciation',
                       GRID_COL_LABEL: 'Depreciation period (a)',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 20.00},
                      {PARAM_KEY: 'wacc',
                       GRID_COL_LABEL: 'Weighted average cost of capital',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.05},
                      {PARAM_KEY: 'init',
                       GRID_COL_LABEL: 'Initial storage content',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.50},
                      {PARAM_KEY: 'discharge',
                       GRID_COL_LABEL: 'Discharge',
                       GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                       PARAM_DEFVALUE: 0.00},
                      ]
# ----------------------------------------------------------------------------#
    TRANS_PARAMS = [{PARAM_KEY: 'eff',
                     GRID_COL_LABEL: 'Efficiency (1)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 1.00},
                    {PARAM_KEY: 'inv-cost',
                     GRID_COL_LABEL: 'Investment cost (€/MW)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 0.00},
                    {PARAM_KEY: 'fix-cost',
                     GRID_COL_LABEL: 'Annual fix cost (€/MW/a)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: INF},
                    {PARAM_KEY: 'var-cost',
                     GRID_COL_LABEL: 'Variable costs (€/MWh)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: INF},
                    {PARAM_KEY: 'inst-cap',
                     GRID_COL_LABEL: 'Installed capacity (MW)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 0.00},
                    {PARAM_KEY: 'lifetime',
                     GRID_COL_LABEL: 'Lifetime of inst-cap (years)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 0.00},
                    {PARAM_KEY: 'cap-lo',
                     GRID_COL_LABEL: 'Minimum capacity (MW)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 0.00},
                    {PARAM_KEY: 'cap-up',
                     GRID_COL_LABEL: 'Maximum capacity (MW)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 0.00},
                    {PARAM_KEY: 'wacc',
                     GRID_COL_LABEL: 'Weighted average cost of capital',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 0.05},
                    {PARAM_KEY: 'depreciation',
                     GRID_COL_LABEL: 'Depreciation period (a)',
                     GRID_COL_DATATYPE: wx.grid.GRID_VALUE_STRING,
                     PARAM_DEFVALUE: 20}]
# ----------------------------------------------------------------------------#
    SCENARIOS = {
        'scenario_base': urbs.scenario_base,
        'scenario_stock_prices': urbs.scenario_stock_prices,
        'scenario_co2_limit': urbs.scenario_co2_limit,
        'scenario_co2_tax_mid': urbs.scenario_co2_tax_mid,
        'scenario_north_process_caps': urbs.scenario_north_process_caps,
        'scenario_no_dsm': urbs.scenario_no_dsm,
    }
# ----------------------------------------------------------------------------#
    RESULT_DIR = os.path.expanduser('~/Documents/urbs/result')
