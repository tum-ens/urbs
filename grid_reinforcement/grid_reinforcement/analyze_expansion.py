"""Grid expansion cost analysis from powerflow results.

Applies the thermal-capacity expansion heuristic (cost_assumptions.md,
key: de_lv_heuristic_2026) to powerflow-augmented h5 files produced by
Step 4 (run_pwrflw.py).

For each grid h5 it computes:
  - per-line peak current vs installed capacity -> additional parallel cables -> EUR
  - transformer peak apparent power vs rated kVA -> replacement bin -> EUR
  - voltage min/max -> violation flag (not costed, per cost_assumptions.md)

Usage:
  python3 analyze_expansion.py <folder_with_pwrflw_h5> [output.csv]

Example:
  python3 analyze_expansion.py Output_flex100 expansion_flex100.csv
"""
import sys
import glob
import os
import warnings
import numpy as np
import pandas as pd
import h5py
import pandapower as pp

warnings.filterwarnings("ignore")

# ---- cost assumptions: variants A / B / C ----
# cable + civil works  x1.384  Destatis Baupreisindex Tiefbau "Ortskanaele" (2021=100 -> 138.4, 2026Q1)
# transformers         x1.521  Destatis GP19-27114 "Elektrische Transformatoren" (2021=100 -> 152.1, 2026-07)
# station rebuild      x1.000  dena-Verteilnetzstudie II, already 2025 prices
CIV = 1.384
TRF = 1.521
W_EINZELN  = {150: 150000.0, 185: 175000.0, 240: 200000.0}
W_PARALLEL = {150:  20000.0, 185:  40000.0, 240:  60000.0}
C_DUCT     = {150:  25000.0, 185:  45000.0, 240:  70000.0}
C_REOPEN   = {"rural": 90000.0, "semi": 100000.0, "urban": 165000.0}
C_DUCT_SHARE = 0.20
W_RONT_KVA  = [400, 630, 800, 1000, 1200, 1600]
W_RONT_COST = [18054.0, 21200.0, 24200.0, 27500.0, 30000.0, 36000.0]  # 400 kVA: linear fit to Wintzek 630-1600

# Ortsnetzstation (Wintzek 2021, Tab. 17.2), escalated with TRF.
# Candas (2023) reports that replacing a transformer with a unit of
# 1000 kVA or above entails replacement of the substation.
STATION_THRESHOLD_KVA = 1000.0
STATION_RENEW = 55000.0      # Erneuerung, existing site
STATION_NEW   = 45000.0      # Neubau, additional parallel station

# Candas (2023) all-in transformer prices, incl. station building and civil
# works; units >= 1000 kVA include replacement of the substation.
# Escalated to 2026 prices with the producer price index GP19-27114.
CAN = 1.058
W_CAN_KVA  = [160, 250, 400, 630, 800, 1000, 1250, 1600, 2000]
W_CAN_COST = [25197.0, 31102.0, 34694.0, 38000.0, 40315.0,
              191447.0, 196099.0, 200557.0, 206178.0]
C_TRAFO = [(400, 33000.0), (630, 38000.0), (800, 42000.0), (1000, 48000.0)]
# station replacement, Candas Table 3.8 (all-in, DSO measured 2023) x1.096
C_STATION = [(1000, 209826.0), (1250, 214924.0), (1600, 219810.0), (2000, 225971.0)]
LV_MAX_KVA = 2000  # above this the position leaves the LV supply range
V_MIN, V_MAX = 0.9, 1.1
import os as _os
TH = float(_os.environ.get('LOAD_THRESHOLD','1.0'))  # planning loading limit
VARIANTS = ("A", "B", "C_rural", "C_semi", "C_urban")


def cable_size(std_type):
    st = str(std_type)
    if "kV" in st or "N2XS" in st or "NA2XS" in st:
        return None
    if "240" in st:
        return 240
    if "185" in st:
        return 185
    for small in ("150", "120", "95", "70", "50", "35", "25", "16"):
        if small in st:
            return 150
    return 240


def route_eur_per_km(size, n_add):
    if size is None or n_add <= 0:
        return dict.fromkeys(VARIANTS, 0.0)
    par, duct = W_PARALLEL[size], C_DUCT[size]
    out = {"A": CIV * n_add * par,
           "B": CIV * (W_EINZELN[size] + (n_add - 1) * par)}
    for cls, key in (("rural","C_rural"), ("semi","C_semi"), ("urban","C_urban")):
        out[key] = n_add * duct + (1.0 - C_DUCT_SHARE) * (C_REOPEN[cls] - duct)
    return out


def _pick(required_kva, kva_list, cost_list, factor):
    """Cost of covering required_kva with standard units of one price list."""
    unit = kva_list[-1]
    if required_kva > unit:
        n_full = int(required_kva // unit)
        rest = required_kva - n_full * unit
        cost = n_full * factor * cost_list[-1]
        installed = n_full * unit
        if rest > 0:
            k, c = next((k, c) for k, c in zip(kva_list, cost_list) if k >= rest)
            cost += factor * c
            installed += k
        return cost, installed
    installed, c = next(((k, c) for k, c in zip(kva_list, cost_list)
                         if k >= required_kva), (unit, cost_list[-1]))
    return factor * c, installed


def trafo_costs(required_kva, rated_kva):
    """Return (cost variant A/B, cost variant C, installed kVA, beyond LV).

    Variants A and B: transformer equipment only (rONT, Wintzek 2021).
    Variant C: adds the Ortsnetzstation.  A unit of 1000 kVA or above
    requires renewal of the existing station; each additional parallel
    unit requires a new station.
    """
    if required_kva is None or (isinstance(required_kva, float) and np.isnan(required_kva)):
        return 0.0, 0.0, np.nan, False
    if rated_kva and required_kva <= rated_kva:
        return 0.0, 0.0, rated_kva, False

    unit = W_RONT_KVA[-1]
    sizes = []
    if required_kva > unit:
        n_full = int(required_kva // unit)
        rest = required_kva - n_full * unit
        sizes = [unit] * n_full
        if rest > 0:
            k, _ = next((k, c) for k, c in zip(W_RONT_KVA, W_RONT_COST) if k >= rest)
            sizes.append(k)
    else:
        k, _ = next(((k, c) for k, c in zip(W_RONT_KVA, W_RONT_COST)
                     if k >= required_kva), (unit, W_RONT_COST[-1]))
        sizes = [k]

    cost_map = dict(zip(W_RONT_KVA, W_RONT_COST))
    equip = TRF * sum(cost_map[k] for k in sizes)
    installed = sum(sizes)

    # stations: first unit renews the existing site if it is >= threshold,
    # every additional parallel unit needs a new station
    station = 0.0
    if sizes[0] >= STATION_THRESHOLD_KVA:
        station += STATION_RENEW
    station += STATION_NEW * (len(sizes) - 1)

    total = equip + TRF * station
    # the same transformer rule applies to every cable variant, so that the
    # variants differ only in the cable laying assumption
    return total, total, installed, required_kva > LV_MAX_KVA


def analyze_grid(h5path: str) -> dict:
    """Apply the expansion heuristic to one powerflow-augmented h5 file."""
    base = os.path.basename(h5path)
    gid = base.split("_")[0]

    # --- network: h5py (variable-length string not readable via pandas) ---
    with h5py.File(h5path, "r") as hf:
        raw = hf["raw_data/net"][()]
        if isinstance(raw, np.ndarray):
            raw = raw[0]
        if isinstance(raw, bytes):
            raw = raw.decode()
    net = pp.from_json_string(raw)

    # --- powerflow results: pandas ---
    with pd.HDFStore(h5path, "r") as s:
        ll = s["/pwrflw/output/post/line_loads"]
        vm = s["/pwrflw/output/post/vm"]
        imp = s["/pwrflw/output/post/demand_import"]

    # ---------- lines ----------
    peak_i = ll.xs("i_from_ka", axis=1, level=1).max()
    lines = net.line[["std_type", "length_km", "max_i_ka", "parallel"]].copy()
    lines["peak_i_ka"] = peak_i.values
    lines["installed_ka"] = lines.max_i_ka * lines.parallel
    lines["loading_pct"] = lines.peak_i_ka / lines.installed_ka * 100
    lines["required_parallel"] = np.ceil(lines.peak_i_ka / (lines.max_i_ka * TH)).astype(int)
    lines["additional_parallel"] = (lines.required_parallel - lines.parallel).clip(lower=0)
    lines["size"] = lines.std_type.map(cable_size)
    line_cost = dict.fromkeys(VARIANTS, 0.0)
    for _, r in lines.iterrows():
        n_add = int(r.additional_parallel)
        if n_add <= 0:
            continue
        pk = route_eur_per_km(r["size"], n_add)
        for v in VARIANTS:
            line_cost[v] += pk[v] * float(r.length_km)

    n_overloaded = int((lines.additional_parallel > 0).sum())
    max_line_loading = float(lines.loading_pct.max())

    # ---------- transformer ----------
    rated_kva = float(net.trafo.sn_mva.iloc[0] * 1000) if len(net.trafo) > 0 else np.nan
    cols = list(imp.columns)
    p, q = imp[cols[0]], imp[cols[1]]
    peak_s_kva = float(np.sqrt(p**2 + q**2).max() * 1000)
    required_kva = float(peak_s_kva)
    t_ab, t_c, installed_kva, beyond_lv = trafo_costs(required_kva, rated_kva)
    redesign = beyond_lv
    trafo_loading = peak_s_kva / rated_kva * 100 if rated_kva else np.nan

    # ---------- voltage (flag only) ----------
    vmin = float(vm.min().min())
    vmax = float(vm.max().max())
    v_violation = bool(vmin < V_MIN or vmax > V_MAX)

    tt = {"A": line_cost["A"] + t_ab, "B": line_cost["B"] + t_ab,
          "C_rural": line_cost["C_rural"] + t_c,
          "C_semi": line_cost["C_semi"] + t_c,
          "C_urban": line_cost["C_urban"] + t_c}
    return {
        "grid": gid,
        "file": base,
        "n_lines": len(lines),
        "n_overloaded_lines": n_overloaded,
        "max_line_loading_pct": round(max_line_loading, 1),
        "line_cost_A": round(line_cost["A"]),
        "line_cost_B": round(line_cost["B"]),
        "line_cost_C_rural": round(line_cost["C_rural"]),
        "line_cost_C_semi": round(line_cost["C_semi"]),
        "line_cost_C_urban": round(line_cost["C_urban"]),
        "trafo_rated_kva": rated_kva,
        "trafo_peak_kva": round(peak_s_kva, 1),
        "trafo_loading_pct": round(trafo_loading, 1),
        "trafo_required_kva": required_kva,
        "trafo_installed_kva": installed_kva,
        "trafo_beyond_lv": beyond_lv,
        "structural_redesign": redesign,
        "trafo_cost_AB": round(t_ab),
        "trafo_cost_C": round(t_c),
        "total_cost_A": round(tt["A"]),
        "total_cost_B": round(tt["B"]),
        "total_cost_C_rural": round(tt["C_rural"]),
        "total_cost_C_semi": round(tt["C_semi"]),
        "total_cost_C_urban": round(tt["C_urban"]),
        "requires_expansion": bool(n_overloaded > 0 or t_ab > 0),
        "vmin_pu": round(vmin, 4),
        "vmax_pu": round(vmax, 4),
        "voltage_violation": v_violation,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    folder = sys.argv[1].rstrip("/")
    out_csv = sys.argv[2] if len(sys.argv) > 2 else f"expansion_{os.path.basename(folder)}.csv"

    files = sorted(glob.glob(os.path.join(folder, "*.h5")))
    if not files:
        print(f"no h5 files in {folder}")
        sys.exit(1)

    rows, failed = [], []
    for i, f in enumerate(files, 1):
        try:
            rows.append(analyze_grid(f))
            print(f"[{i}/{len(files)}] {os.path.basename(f).split('_')[0]} ok")
        except Exception as e:
            failed.append((os.path.basename(f), str(e)))
            print(f"[{i}/{len(files)}] {os.path.basename(f)} FAILED: {e}")

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)

    # ---------- summary ----------
    peak = df.trafo_peak_kva.sum()
    print("\n" + "=" * 62)
    print(f"SUMMARY  ({folder})   grids {len(df)}   peak {peak/1000:,.1f} MVA")
    print(f"expansion {int(df.requires_expansion.sum())}  |  line {int((df.n_overloaded_lines>0).sum())}  trafo {int((df.trafo_cost_AB>0).sum())}  station {int(df.trafo_beyond_lv.sum())}  volt {int(df.voltage_violation.sum())}")
    print("=" * 62)
    print(f"{'variant':<10}{'cable M':>11}{'trafo M':>11}{'total M':>11}{'EUR/kVA':>11}")
    for v, tc in (("A","trafo_cost_AB"),("B","trafo_cost_AB"),("C_rural","trafo_cost_C"),("C_semi","trafo_cost_C"),("C_urban","trafo_cost_C")):
        cab = df[f"line_cost_{v}"].sum()/1e6; tr = df[tc].sum()/1e6; tot = df[f"total_cost_{v}"].sum()/1e6
        print(f"{v:<10}{cab:11.2f}{tr:11.2f}{tot:11.2f}{tot*1e6/peak:11.2f}")
    print()
    if failed:
        print(f"\nFAILED files: {len(failed)}")
        for name, err in failed[:5]:
            print(f"  {name}: {err[:80]}")
    print(f"\nsaved: {out_csv}")


if __name__ == "__main__":
    main()
