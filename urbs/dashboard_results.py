from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from .input import config_commodity_type, normalize_timeseries_types
from .output import get_timeseries

_TIMESERIES_NAME_HINTS = (
    "ELEC",
    "HEAT",
    "THERMAL",
    "CO2",
    "MJ",
    "GJ",
    "KWH_TH",
)


def commodity_type_label(com_cfg: dict) -> str:
    return config_commodity_type(com_cfg)


def commodity_needs_timeseries(
    com_name: str,
    com_cfg: dict,
    commodity_types: list[str] | None = None,
) -> bool:
    """Return whether dashboard charts need full timeseries for this commodity."""
    com_type = commodity_type_label(com_cfg)
    if commodity_types is not None:
        wanted = set(normalize_timeseries_types(commodity_types))
        return com_type in wanted
    if com_type == "Demand":
        return True
    if com_type == "SupIm":
        return False
    if com_type == "Env" and "CO2" not in com_name.upper():
        return False
    if com_cfg.get("transmission"):
        return True
    name = com_name.upper()
    return any(hint in name for hint in _TIMESERIES_NAME_HINTS)


def _extract_site_com_timeseries(prob, year: int, site: str, com: str, timesteps):
    data = get_timeseries(prob, year, com, site, timesteps=timesteps)
    imported_dict = {}
    exported_dict = {}

    if not data[3].empty:
        imported_df = data[3]
        for source_site in imported_df.columns:
            imported_dict[source_site] = list(
                imported_df[source_site].fillna(0).values
            )

    if not data[4].empty:
        exported_df = data[4]
        for dest_site in exported_df.columns:
            exported_dict[dest_site] = list(
                exported_df[dest_site].fillna(0).values
            )

    demand_series = data[1].to_dict().get("Demand")
    consumed = {}
    if data[1] is not None and not getattr(data[1], "empty", True):
        skip = {"demand", "unshifted", "shifted"}
        for name, series in data[1].to_dict().items():
            if str(name).lower() in skip:
                continue
            consumed[str(name)] = list(series.values())

    return {
        "created": {
            str(k): list(v.values()) for k, v in data[0].to_dict().items()
        },
        "consumed": consumed,
        "demand": list(demand_series.values()) if demand_series is not None else [],
        "storage": {
            str(k): list(v.values()) for k, v in data[2].to_dict().items()
        },
        "imported": imported_dict,
        "exported": exported_dict,
    }


def build_results_timeseries(
    prob,
    config: dict,
    timesteps,
    *,
    full_timeseries: bool = False,
    commodity_types: list[str] | None = None,
    parallel: bool = True,
) -> dict:
    """Build site/commodity timeseries for the web dashboard."""
    year = date.today().year
    tasks: list[tuple[str, str]] = []

    for site, data_site in config.get("site", {}).items():
        for com, com_cfg in data_site.get("commodity", {}).items():
            if commodity_types is not None:
                include = commodity_needs_timeseries(
                    com, com_cfg, normalize_timeseries_types(commodity_types)
                )
            else:
                include = full_timeseries or commodity_needs_timeseries(
                    com, com_cfg
                )
            if include:
                tasks.append((site, com))

    results = defaultdict(dict)
    if not tasks:
        return results

    def _worker(site_com):
        site, com = site_com
        return site, com, _extract_site_com_timeseries(
            prob, year, site, com, timesteps
        )

    if parallel and len(tasks) > 1:
        max_workers = min(8, len(tasks))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for site, com, payload in executor.map(_worker, tasks):
                results[site][com] = payload
    else:
        for site, com in tasks:
            results[site][com] = _extract_site_com_timeseries(
                prob, year, site, com, timesteps
            )

    return results
