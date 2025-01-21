import os
import threading
from collections import defaultdict
from datetime import date

import requests
from flask import Flask, request

import urbs
from urbs import get_constants, get_input, get_timeseries

app = Flask(__name__)


@app.post('/simulate')
def trigger_simulation():
    config = request.get_json()
    if 'callback' in config:
        thread = threading.Thread(target=simulate, args=[config])
        thread.start()
        return "Simulation started"
    else:
        return run(config)


def simulate(config):
    requests.post(config['callback'], json=run(config))


def scenario(data):
    return data


def run(config):
    result_name = 'Run'
    result_dir = urbs.prepare_result_directory(result_name)
    log_file = os.path.join(result_dir, scenario.__name__ + '.log')

    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective

    # Choose Solver (cplex, glpk, gurobi, ...)
    solver = 'glpk'

    # simulation timesteps
    timesteps = range(config['c_timesteps'])
    dt = 1  # length of each time step (unit: hours)

    # plotting timesteps
    plot_periods = {
        'all': timesteps[1:]
    }

    # select scenarios to be run - only use base scenario
    try:
        (result_type, prob) = urbs.run_scenario_config(config, solver, timesteps, scenario,
                                                       result_dir, dt, objective,
                                                       plot_tuples=[],
                                                       plot_sites_name={},
                                                       plot_periods=plot_periods,
                                                       report_tuples=[],
                                                       report_sites_name={})
    except Exception:
        try:
            with open(log_file, 'r') as log_file:
                log = log_file.read()
        except (FileNotFoundError, IOError):
            log = "Simulation failed in preparation. Optimizer was not started."
        return {
            'data': {},
            'status': 'Error',
            'log': log
        }


    costs, cpro, ctra, csto = get_constants(prob)

    def default():
        return defaultdict(default)

    proc = default()
    for ((year, site, commodity), row) in cpro.iterrows():
        proc[site][commodity]['New'] = row['New']
        proc[site][commodity]['Total'] = row['Total']

    sto = default()
    for ((year, site, storage, commodity), row) in csto.iterrows():
        sto[site][commodity][storage]['C New'] = row['C New']
        sto[site][commodity][storage]['C Total'] = row['C Total']
        sto[site][commodity][storage]['P New'] = row['P New']
        sto[site][commodity][storage]['P Total'] = row['P Total']

    results = default()
    for (site, com) in get_input(prob, 'demand').columns.values.tolist():
        data = get_timeseries(prob, date.today().year, "Elec", site, timesteps=None)
        results[site][com] = {
            'created': {k: list(v.values()) for k, v in data[0].to_dict().items()},
            'demand': list(data[1].to_dict()['Demand'].values()),
            'storage': {k: list(v.values()) for k, v in data[2].to_dict().items()}
        }

    try:
        with open(log_file, 'r') as log_file:
            log = log_file.read()
    except (FileNotFoundError, IOError):
        log = "Error reading log file"
    return {
        'data': {
            'costs': costs.to_dict(),
            'process': proc,
            'storage': sto,
            'results': results
        },
        'status': result_type,
        'log': log
    }


if __name__ == '__main__':
    app.run()
