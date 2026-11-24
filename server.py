import json
import math
import multiprocessing
import os
import threading
import traceback
import uuid
from collections import defaultdict
from datetime import date, datetime

import requests
from flask import Flask, jsonify, request

import urbs
from urbs import get_constants, get_input, get_timeseries
from urbs import progress as sim_progress
from urbs.dashboard_results import build_results_timeseries

app = Flask(__name__)

_active_runs: dict[str, multiprocessing.Process] = {}
_active_run_configs: dict[str, dict] = {}
_cancelled_runs: set[str] = set()
_runs_lock = threading.Lock()

QUEUE_TIMEOUT_SEC = 120
CALLBACK_TIMEOUT_SEC = 300


def _result_dir_from_config(config) -> str | None:
    run_config = config.get("run_config") or {}
    if "dir" not in run_config:
        return None
    return os.path.join("result", run_config["dir"])


def _to_jsonable(obj):
    if isinstance(obj, defaultdict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    if hasattr(obj, "item"):
        try:
            value = obj.item()
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return None
            return value
        except Exception:
            pass
    return str(obj)


def _callback_json_path(result_dir: str) -> str:
    return os.path.join(result_dir, "callback.json")


def _result_subdir_from_config(config) -> str | None:
    run_config = config.get("run_config") or {}
    return run_config.get("dir")


def _post_callback(
    callback_url: str,
    result_dir: str | None,
    payload: dict,
    *,
    result_subdir: str | None = None,
) -> None:
    """Notify backend. Large results are read from shared result_dir/callback.json."""
    payload = dict(payload)
    payload["status"] = _normalize_status(payload.get("status", "Error"))
    log_text = payload.get("log", "")
    if result_dir and len(log_text) < 500:
        log_tail = _read_log_tail(result_dir, max_chars=50000)
        if log_tail:
            log_text = log_tail if not log_text else log_text + "\n" + log_tail
    if result_dir:
        _write_callback_payload(result_dir, {**payload, "log": log_text})
        body = {
            "status": payload["status"],
            "log": log_text,
            "data": {},
            "load_from_disk": True,
        }
        if result_subdir:
            body["result_subdir"] = result_subdir
    else:
        body = _to_jsonable(payload)
    response = requests.post(callback_url, json=body, timeout=CALLBACK_TIMEOUT_SEC)
    if response.status_code >= 400:
        raise RuntimeError(
            f"Callback failed ({response.status_code}): {response.text[:500]}"
        )


def _normalize_status(status) -> str:
    text = str(status).lower()
    if "optimal" in text:
        return "optimal"
    if "infeasible" in text:
        return "infeasible"
    if "error" in text:
        return "Error"
    return text


def _write_callback_payload(result_dir: str, payload: dict) -> None:
    payload = dict(payload)
    payload["status"] = _normalize_status(payload.get("status", "Error"))
    path = os.path.join(result_dir, "callback.json")
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(_to_jsonable(payload), handle)
    except Exception as exc:
        traceback.print_exc()
        fallback = {
            "data": {},
            "status": "Error",
            "log": (
                payload.get("log", "")
                + f"\nFailed to write callback.json: {exc}\n"
                + _read_log_tail(result_dir, max_chars=50000)
            ),
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(fallback, handle)


def _read_callback_payload(result_dir: str) -> dict:
    path = os.path.join(result_dir, "callback.json")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _read_log_tail(result_dir: str | None, max_chars: int = 8000) -> str:
    if not result_dir:
        return ""
    log_path = os.path.join(result_dir, "result.log")
    if not os.path.exists(log_path):
        return ""
    with open(log_path, encoding="utf-8", errors="replace") as handle:
        return handle.read()[-max_chars:]


def _sim_id_from_config(config) -> str | None:
    run_config = config.get("run_config") or {}
    if run_config.get("sim_id"):
        return str(run_config["sim_id"])
    callback = run_config.get("callback", "")
    parts = callback.rstrip("/").split("/")
    if len(parts) >= 2 and parts[-2] == "simulation":
        return parts[-1]
    return None


def _simulate_worker(config, result_queue):
    result_dir = _result_dir_from_config(config)
    try:
        payload = run(config)
        if result_dir:
            _write_callback_payload(result_dir, payload)
            result_queue.put(("ok", result_dir))
        else:
            result_queue.put(("ok", payload))
    except Exception as exc:
        traceback.print_exc()
        if result_dir:
            error_payload = {
                "data": {},
                "status": "Error",
                "log": f"Worker failed: {exc}\n" + _read_log_tail(result_dir, max_chars=50000),
            }
            try:
                _write_callback_payload(result_dir, error_payload)
                result_queue.put(("ok", result_dir))
            except Exception:
                result_queue.put(("error", str(exc)))
        else:
            result_queue.put(("error", str(exc)))


def _monitor_simulation(sim_id: str, config, process: multiprocessing.Process, result_queue):
    callback = config["run_config"]["callback"]
    result_dir = _result_dir_from_config(config)
    result_subdir = _result_subdir_from_config(config)
    process.join()
    exitcode = process.exitcode

    with _runs_lock:
        _active_runs.pop(sim_id, None)
        _active_run_configs.pop(sim_id, None)
        cancelled = sim_id in _cancelled_runs
        if cancelled:
            _cancelled_runs.discard(sim_id)

    if cancelled:
        _post_callback(
            callback,
            result_dir,
            {
                "data": {},
                "status": "cancelled",
                "log": "Simulation stopped.",
            },
            result_subdir=result_subdir,
        )
        return

    payload = None
    try:
        status, payload = result_queue.get(timeout=QUEUE_TIMEOUT_SEC)
    except Exception:
        status = None

    if status == "ok":
        if isinstance(payload, str):
            try:
                payload = _read_callback_payload(payload)
            except Exception as exc:
                _post_callback(
                    callback,
                    result_dir,
                    {
                        "data": {},
                        "status": "Error",
                        "log": (
                            f"Simulation finished but callback data could not be read: {exc}\n"
                            + _read_log_tail(result_dir)
                        ),
                    },
                    result_subdir=result_subdir,
                )
                return
        try:
            _post_callback(
                callback, result_dir, payload, result_subdir=result_subdir
            )
        except Exception as exc:
            traceback.print_exc()
            _post_callback(
                callback,
                result_dir,
                {
                    "data": {},
                    "status": "Error",
                    "log": f"Callback delivery failed: {exc}\n" + _read_log_tail(result_dir),
                },
                result_subdir=result_subdir,
            )
        return

    if result_dir and os.path.exists(_callback_json_path(result_dir)):
        try:
            payload = _read_callback_payload(result_dir)
            _post_callback(
                callback, result_dir, payload, result_subdir=result_subdir
            )
            return
        except Exception:
            traceback.print_exc()

    if status == "error":
        _post_callback(
            callback,
            result_dir,
            {
                "data": {},
                "status": "Error",
                "log": f"Simulation failed: {payload}\n" + _read_log_tail(result_dir),
            },
            result_subdir=result_subdir,
        )
        return

    log = _read_log_tail(result_dir)
    hint = (
        f"Simulation process ended without returning a result "
        f"(exit code {exitcode})."
    )
    if log:
        hint += "\n\n--- optimizer log ---\n" + log
    _post_callback(
        callback,
        result_dir,
        {"data": {}, "status": "Error", "log": hint},
        result_subdir=result_subdir,
    )


@app.post("/simulate")
def trigger_simulation():
    config = request.get_json()
    if "run_config" in config and "callback" in config["run_config"]:
        sim_id = _sim_id_from_config(config)
        if not sim_id:
            return "Missing simulation id in run_config", 400

        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_simulate_worker,
            args=(config, result_queue),
        )

        with _runs_lock:
            _cancelled_runs.discard(sim_id)
            _active_runs[sim_id] = process
            _active_run_configs[sim_id] = config

        process.start()
        threading.Thread(
            target=_monitor_simulation,
            args=(sim_id, config, process, result_queue),
            daemon=True,
        ).start()
        return "Simulation started"
    return run(config)


@app.post("/compute_iis")
def compute_iis_endpoint():
    """Rebuild a previously-run model and write its Gurobi IIS (model.ilp).

    Expects the original run config (including run_config.dir) so the model is
    reconstructed identically to the failed run.
    """
    config = request.get_json()
    result_dir = _result_dir_from_config(config)
    if not result_dir:
        return jsonify({"detail": "Missing result directory in run_config"}), 400

    total = config.get("c_timesteps")
    if not total:
        return jsonify({"detail": "Missing c_timesteps in config"}), 400

    run_config = config.get("run_config") or {}
    try:
        t_from = int(run_config.get("timestep_from", 0))
        t_to = int(run_config.get("timestep_to", total - 1))
    except (TypeError, ValueError):
        return jsonify({"detail": "Invalid timestep range in run_config"}), 400
    timesteps = range(t_from, t_to + 1)

    try:
        ilp_path = urbs.compute_iis(config, result_dir, timesteps)
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"detail": str(exc)}), 400

    return jsonify({"detail": "IIS computed", "file": os.path.basename(ilp_path)})


@app.post("/simulate/stop/<sim_id>")
def stop_simulation(sim_id):
    with _runs_lock:
        process = _active_runs.get(sim_id)
        config = _active_run_configs.get(sim_id)
        if process is None:
            return jsonify({"detail": "Simulation is not running"}), 404

        _cancelled_runs.add(sim_id)
        result_dir = _result_dir_from_config(config) if config else None
        if result_dir:
            sim_progress.cancel_progress(result_dir)

        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
                process.join(timeout=5)

        _active_runs.pop(sim_id, None)
        _active_run_configs.pop(sim_id, None)

    return jsonify({"detail": "Simulation stop requested"})


def run(config):
    start_time = datetime.now()

    now = datetime.now().strftime("%Y%m%d")
    result_dir = os.path.join("result", now, str(uuid.uuid4()))
    generate_report = None
    generate_h5 = False
    # Choose Solver (cplex, glpk, gurobi, ...); default from env, overridable per request
    solver = os.getenv("SOLVER", "gurobi")
    if "run_config" in config:
        run_config = config["run_config"]
        if "dir" in run_config:
            result_dir = os.path.join("result", run_config["dir"])
        generate_report = (
            run_config["generate_report"] if "generate_report" in run_config else None
        )
        generate_h5 = run_config["generate_h5"] if "generate_h5" in run_config else None
        if run_config.get("solver") in ("gurobi", "glpk"):
            solver = run_config["solver"]

    if not os.path.exists(result_dir):
        os.makedirs(result_dir, mode=0o777)
    else:
        try:
            os.chmod(result_dir, 0o777)
        except OSError:
            pass

    log_file = os.path.join(result_dir, "result.log")

    sim_progress.init_progress(result_dir, generate_report, generate_h5)

    # objective function
    objective = "cost"  # set either 'cost' or 'CO2' as objective

    # simulation timesteps (optional subset for faster test runs)
    run_config = config.get("run_config") or {}
    total_timesteps = config["c_timesteps"]
    t_from = run_config.get("timestep_from", 0)
    t_to = run_config.get("timestep_to", total_timesteps - 1)
    try:
        t_from = int(t_from)
        t_to = int(t_to)
    except (TypeError, ValueError):
        return {
            "data": {},
            "status": "Error",
            "log": "Invalid timestep range in run_config.",
        }
    if t_from < 0 or t_to >= total_timesteps or t_from > t_to:
        return {
            "data": {},
            "status": "Error",
            "log": (
                f"Timestep range must satisfy 0 <= from <= to < {total_timesteps} "
                f"(got from={t_from}, to={t_to})."
            ),
        }
    timesteps = range(t_from, t_to + 1)
    dt = 1  # length of each time step (unit: hours)

    # plotting timesteps
    plot_periods = {"all": timesteps[1:]}

    # select scenarios to be run - only use base scenario
    dashboard_step = sim_progress.STEP_PREPARING_DASHBOARD
    try:
        (result_type, prob, time_setup_finished, time_solve_finished) = (
            urbs.run_scenario_config(
                config,
                solver,
                timesteps,
                result_dir,
                dt,
                objective,
                generate_report=generate_report,
                generate_h5=generate_h5,
            )
        )
        sim_progress.advance_to_step(result_dir, dashboard_step)
    except Exception as e:
        traceback.print_exc()
        try:
            with open(log_file, "r") as log_file_handle:
                log = log_file_handle.read()
        except (FileNotFoundError, IOError):
            log = "Simulation failed in preparation. Optimizer was not started."
        return {
            "data": {},
            "status": "Error",
            "log": log + "\nError message: " + str(e),
        }

    # Stop here if the solver did not find an optimal solution. There is no
    # result to post-process, so report the termination condition instead of
    # crashing while reading uninitialized model variables.
    status = _normalize_status(result_type)
    if status != "optimal":
        try:
            with open(log_file, "r") as log_file_handle:
                log = log_file_handle.read()
        except (FileNotFoundError, IOError):
            log = ""
        message = (
            f"Optimization finished without an optimal solution "
            f"(termination condition: {result_type})."
        )
        sim_progress.fail_step(result_dir, dashboard_step, message)
        return {
            "data": {},
            "status": status,
            "log": log + "\n" + message,
        }

    try:
        end_time = datetime.now()

        costs, cpro, ctra, csto = get_constants(prob)

        def default():
            return defaultdict(default)

        # Process capacities (as before)
        proc = default()
        for ((year, site, commodity), row) in cpro.iterrows():
            proc[site][commodity]["New"] = row["New"]
            proc[site][commodity]["Total"] = row["Total"]

        # Storage capacities (as before)
        sto = default()
        for ((year, site, storage, commodity), row) in csto.iterrows():
            sto[site][commodity][storage]["CNew"] = row["C New"]
            sto[site][commodity][storage]["CTotal"] = row["C Total"]
            sto[site][commodity][storage]["PNew"] = row["P New"]
            sto[site][commodity][storage]["PTotal"] = row["P Total"]

        # Per-process and per-storage cost breakdown from URBS
        process_costs_dd = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        try:
            process_costs_series = urbs.get_entity(prob, "process_costs")
            for (stf, site, process, cost_type), value in process_costs_series.items():
                process_costs_dd[site][process][cost_type] += float(value)
        except Exception:
            process_costs_dd = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

        storage_costs_dd = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        try:
            storage_costs_series = urbs.get_entity(prob, "storage_costs")
            for (stf, site, storage, commodity, cost_type), value in storage_costs_series.items():
                key = f"{storage} ({commodity})"
                storage_costs_dd[site][key][cost_type] += float(value)
        except Exception:
            storage_costs_dd = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

        full_timeseries = generate_report == "full"
        commodity_types = run_config.get("timeseries_commodity_types")
        if not isinstance(commodity_types, list):
            commodity_types = None
        raw_results = build_results_timeseries(
            prob,
            config,
            timesteps,
            full_timeseries=full_timeseries,
            commodity_types=commodity_types,
        )
        results = {site: dict(com_map) for site, com_map in raw_results.items()}

        try:
            with open(log_file, "r") as log_file_handle:
                log = log_file_handle.read()
        except (FileNotFoundError, IOError):
            log = "Error reading log file"

        log += (
            f"\n-Duration-------------------------------------------"
            f"\nProcess started at: {str(start_time)}"
            f"\nSimulation started at: {str(time_setup_finished)} - delta: {str(time_setup_finished - start_time)}"
            f"\nSimulation finished at: {str(time_solve_finished)} - delta: {str(time_solve_finished - time_setup_finished)}"
            f"\nWriting result files finished at: {str(end_time)} - delta: {str(end_time - time_solve_finished)}"
            f"\nTotal time needed: {str(end_time - start_time)}\n"
        )

        sim_progress.complete_step(result_dir, dashboard_step)
        sim_progress.complete_all(result_dir)

        return {
            "data": {
                "costs": costs.to_dict(),
                "process": proc,
                "storage": sto,
                "results": results,
                "process_costs": process_costs_dd,
                "storage_costs": storage_costs_dd,
            },
            "status": _normalize_status(result_type),
            "log": log,
        }
    except Exception as e:
        traceback.print_exc()
        sim_progress.fail_step(result_dir, dashboard_step, str(e))
        try:
            with open(log_file, "r") as log_file_handle:
                log = log_file_handle.read()
        except (FileNotFoundError, IOError):
            log = ""
        return {
            "data": {},
            "status": "Error",
            "log": log + "\nPost-processing failed: " + str(e),
        }


if __name__ == "__main__":
    app.run()
