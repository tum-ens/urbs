import os
import threading
import traceback
import uuid
from collections import defaultdict
from datetime import date, datetime

import requests
from flask import Flask, request

import urbs
from urbs import get_constants, get_input, get_timeseries

app = Flask(__name__)


@app.post('/simulate')
def trigger_simulation():
    config = request.get_json()
    if 'run_config' in config and 'callback' in config['run_config']:
        print(config['run_config'])
        thread = threading.Thread(target=simulate, args=[config])
        thread.start()
        return "Simulation started"
    else:
        return run(config)


def simulate(config):
    requests.post(config['run_config']['callback'], json=run(config))

def run(config):
    now = datetime.now().strftime('%Y%m%d')
    result_dir = os.path.join('result', now, str(uuid.uuid4()))
    generate_report = None
    generate_h5=False
    if 'run_config' in config:
        run_config = config['run_config']
        if "dir" in run_config:
            result_dir = os.path.join('result', run_config["dir"])
        generate_report = run_config["generate_report"] if "generate_report" in run_config else None
        generate_h5 = run_config["generate_h5"] if "generate_h5" in run_config else None

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    log_file = os.path.join(result_dir, 'result.log')

    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective

    # Choose Solver (cplex, glpk, gurobi, ...)
    solver = os.getenv('SOLVER', 'gurobi')

    # simulation timesteps
    timesteps = range(config['c_timesteps'])
    dt = 1  # length of each time step (unit: hours)

    # plotting timesteps
    plot_periods = {
        'all': timesteps[1:]
    }

    # select scenarios to be run - only use base scenario
    try:
        (result_type, prob) = urbs.run_scenario_config(config, solver, timesteps,
                                                       result_dir, dt, objective,
                                                       generate_report=generate_report,
                                                       generate_h5=generate_h5)
    except Exception as e:
        traceback.print_exc()
        try:
            with open(log_file, 'r') as log_file:
                log = log_file.read()
        except (FileNotFoundError, IOError):
            log = "Simulation failed in preparation. Optimizer was not started."
        return {
            'data': {},
            'status': 'Error',
            'log': log + "\nError message: " + str(e)
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
        sto[site][commodity][storage]['CNew'] = row['C New']
        sto[site][commodity][storage]['CTotal'] = row['C Total']
        sto[site][commodity][storage]['PNew'] = row['P New']
        sto[site][commodity][storage]['PTotal'] = row['P Total']

    results = default()
    for (site, dataSite) in config['site'].items():
        for (com, _) in dataSite['commodity'].items():
            data = get_timeseries(prob, date.today().year, com, site, timesteps=None)
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
