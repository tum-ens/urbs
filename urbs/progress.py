import json
import os
from datetime import datetime, timezone

STEP_BUILDING_MODEL = "building_model"
STEP_OPTIMIZING = "optimizing"
STEP_SAVING_XLSX = "saving_xlsx"
STEP_SAVING_H5 = "saving_h5"
STEP_PREPARING_DASHBOARD = "preparing_dashboard"

STEP_LABELS = {
    STEP_BUILDING_MODEL: "Building Pyomo model",
    STEP_OPTIMIZING: "Running optimization",
    STEP_SAVING_XLSX: "Saving Excel file",
    STEP_SAVING_H5: "Saving h5 file",
    STEP_PREPARING_DASHBOARD: "Preparing result dashboard",
}


def _progress_path(result_dir: str) -> str:
    return os.path.join(result_dir, "progress.json")


def build_step_list(generate_report=None, generate_h5=False) -> list[dict]:
    steps = [
        {"id": STEP_BUILDING_MODEL, "label": STEP_LABELS[STEP_BUILDING_MODEL]},
        {"id": STEP_OPTIMIZING, "label": STEP_LABELS[STEP_OPTIMIZING]},
    ]
    if generate_report is not None:
        steps.append(
            {"id": STEP_SAVING_XLSX, "label": STEP_LABELS[STEP_SAVING_XLSX]}
        )
    if generate_h5:
        steps.append({"id": STEP_SAVING_H5, "label": STEP_LABELS[STEP_SAVING_H5]})
    steps.append(
        {
            "id": STEP_PREPARING_DASHBOARD,
            "label": STEP_LABELS[STEP_PREPARING_DASHBOARD],
        }
    )
    return steps


def _compute_percent(steps: list[dict]) -> int:
    if not steps:
        return 0
    total = len(steps)
    completed = sum(1 for step in steps if step.get("status") == "completed")
    in_progress = any(step.get("status") == "in_progress" for step in steps)
    failed = any(step.get("status") == "failed" for step in steps)
    if failed:
        return max(0, min(100, int((completed / total) * 100)))
    if completed == total:
        return 100
    if in_progress:
        return max(0, min(99, int(((completed + 0.5) / total) * 100)))
    return max(0, min(99, int((completed / total) * 100)))


def _ensure_result_dir(result_dir: str) -> None:
    os.makedirs(result_dir, mode=0o777, exist_ok=True)
    try:
        os.chmod(result_dir, 0o777)
    except OSError:
        pass


def _write(result_dir: str, payload: dict) -> None:
    if not result_dir:
        return
    _ensure_result_dir(result_dir)
    path = _progress_path(result_dir)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
    try:
        os.chmod(path, 0o666)
    except OSError:
        pass


def _read(result_dir: str) -> dict | None:
    path = _progress_path(result_dir)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _is_cancelled(result_dir: str) -> bool:
    payload = _read(result_dir)
    return bool(payload and payload.get("cancelled"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _step_duration_seconds(started_at: str | None) -> float | None:
    if not started_at:
        return None
    try:
        started = datetime.fromisoformat(started_at)
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        elapsed = datetime.now(timezone.utc) - started
        return max(0.0, elapsed.total_seconds())
    except (TypeError, ValueError):
        return None


def _finalize_step_timing(step: dict) -> None:
    if step.get("status") in ("completed", "failed", "cancelled") and step.get(
        "started_at"
    ):
        duration = _step_duration_seconds(step["started_at"])
        if duration is not None:
            step["duration_seconds"] = round(duration, 1)


def init_progress(result_dir: str, generate_report=None, generate_h5=False) -> None:
    steps = build_step_list(generate_report, generate_h5)
    for step in steps:
        step["status"] = "pending"
    if steps:
        steps[0]["status"] = "in_progress"
        steps[0]["started_at"] = _now_iso()
    payload = {
        "steps": steps,
        "current_step": steps[0]["id"] if steps else None,
        "failed_at": None,
        "error_message": None,
        "progress_percent": _compute_percent(steps),
        "updated_at": _now_iso(),
    }
    _write(result_dir, payload)


def set_step_in_progress(result_dir: str, step_id: str) -> None:
    if _is_cancelled(result_dir):
        return
    payload = _read(result_dir)
    if payload is None:
        return
    for step in payload["steps"]:
        if step["id"] == step_id:
            step["status"] = "in_progress"
            step["started_at"] = _now_iso()
        elif step["status"] == "in_progress":
            step["status"] = "pending"
    payload["current_step"] = step_id
    payload["progress_percent"] = _compute_percent(payload["steps"])
    payload["updated_at"] = _now_iso()
    _write(result_dir, payload)


def complete_step(result_dir: str, step_id: str) -> None:
    if _is_cancelled(result_dir):
        return
    payload = _read(result_dir)
    if payload is None:
        return
    for step in payload["steps"]:
        if step["id"] == step_id:
            step["status"] = "completed"
            _finalize_step_timing(step)
    payload["progress_percent"] = _compute_percent(payload["steps"])
    payload["updated_at"] = _now_iso()
    _write(result_dir, payload)


def advance_to_step(result_dir: str, step_id: str) -> None:
    if _is_cancelled(result_dir):
        return
    payload = _read(result_dir)
    if payload is None:
        return
    seen_target = False
    for step in payload["steps"]:
        if step["id"] == step_id:
            step["status"] = "in_progress"
            step["started_at"] = _now_iso()
            seen_target = True
        elif not seen_target and step["status"] != "failed":
            if step["status"] == "in_progress":
                _finalize_step_timing(step)
            step["status"] = "completed"
        elif seen_target and step["status"] == "in_progress":
            step["status"] = "pending"
    payload["current_step"] = step_id
    payload["progress_percent"] = _compute_percent(payload["steps"])
    payload["updated_at"] = _now_iso()
    _write(result_dir, payload)


def fail_step(result_dir: str, step_id: str, error_message: str | None = None) -> None:
    if _is_cancelled(result_dir):
        return
    payload = _read(result_dir)
    if payload is None:
        init_progress(result_dir)
        payload = _read(result_dir)
    if payload is None:
        return
    for step in payload["steps"]:
        if step["id"] == step_id:
            step["status"] = "failed"
            _finalize_step_timing(step)
        elif step["status"] == "in_progress":
            step["status"] = "pending"
    payload["current_step"] = step_id
    payload["failed_at"] = step_id
    payload["error_message"] = error_message
    payload["progress_percent"] = _compute_percent(payload["steps"])
    payload["updated_at"] = _now_iso()
    _write(result_dir, payload)


def complete_all(result_dir: str) -> None:
    if _is_cancelled(result_dir):
        return
    payload = _read(result_dir)
    if payload is None:
        return
    for step in payload["steps"]:
        if step["status"] == "in_progress":
            _finalize_step_timing(step)
        if step["status"] != "failed":
            step["status"] = "completed"
    payload["current_step"] = None
    payload["progress_percent"] = 100
    payload["updated_at"] = _now_iso()
    _write(result_dir, payload)


def cancel_progress(result_dir: str) -> None:
    payload = _read(result_dir)
    if payload is None:
        return
    if payload.get("cancelled"):
        return
    for step in payload["steps"]:
        if step.get("status") == "in_progress":
            step["status"] = "cancelled"
            _finalize_step_timing(step)
        elif step.get("status") == "pending":
            step["status"] = "cancelled"
    payload["current_step"] = None
    payload["cancelled"] = True
    payload["error_message"] = "Simulation stopped."
    payload["progress_percent"] = _compute_percent(payload["steps"])
    payload["updated_at"] = _now_iso()
    _write(result_dir, payload)
