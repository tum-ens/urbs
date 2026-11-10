"""
Leave-one-out validation of the regression model and the extrapolation (Section 4.2.3, Table 4.22).

The estimation is repeated 56 times, each time without one sampled postal code area.
For each run:
  - the cost of the left-out area is predicted and compared with its power flow result,
  - the Bavaria total is recomputed and compared with the full-sample total.

Outputs (in --out-dir):
    leave_one_out_runs.csv      one row per scenario, case, level and left-out area
    leave_one_out_summary.csv   ranges over the four cost cases, as in Table 4.22

Usage:
    python leave_one_out.py --data-dir data --out-dir output
"""
import argparse
import os
import warnings

import numpy as np
import pandas as pd

import bavaria_regression as br
from extrapolate import design_bavaria, fit, load_bavaria, load_costs, load_sample_pop

warnings.filterwarnings("ignore")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="output")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    pop = load_sample_pop(a.data_dir)
    mu = np.log(pop).mean()
    bav = load_bavaria(a.data_dir)

    rows = []
    for sc in ["inflex", "flex"]:
        costs = load_costs(a.data_dir, sc, pop)
        for case in br.CASES:
            d = costs[costs.case == case].reset_index(drop=True)
            cols, params, smear = fit(d, pop, mu)
            for L in (50, 100):
                full = (np.exp(design_bavaria(bav, cols, L, mu) @ params) * smear[L]).sum()
                for plz in sorted(d.plz.unique()):
                    dd = d[d.plz != plz].reset_index(drop=True)
                    c2, p2, s2 = fit(dd, pop, mu)
                    tot = (np.exp(design_bavaria(bav, c2, L, mu) @ p2) * s2[L]).sum()
                    x = br.design(pd.Series([plz]), pd.Series([L]), pd.Series([np.log(pop[plz]) - mu]))[c2]
                    pred = float(np.exp(x.values @ p2.values)[0] * s2[L])
                    act = float(d[(d.plz == plz) & (d.level == L)].cost.iloc[0])
                    rows.append((sc, case, L, plz, pop[plz], act, pred, 100 * (tot / full - 1)))

    R = pd.DataFrame(rows, columns=["scenario", "case", "level", "plz", "population",
                                    "cost_calculated", "cost_predicted", "bavaria_change_pct"])
    R["abs_error_per_inh"] = (R.cost_predicted - R.cost_calculated).abs() / R.population
    R["abs_pct_error"] = 100 * (R.cost_predicted - R.cost_calculated).abs() / R.cost_calculated
    R.to_csv(os.path.join(a.out_dir, "leave_one_out_runs.csv"), index=False)

    g = R.groupby(["scenario", "level", "case"])
    per_case = pd.DataFrame({
        "bavaria_change_min": g.bavaria_change_pct.min(),
        "bavaria_change_max": g.bavaria_change_pct.max(),
        "median_abs_error_per_inh": g.abs_error_per_inh.median(),
        "median_abs_pct_error": g.abs_pct_error.median(),
        "sum_error_pct": 100 * (g.cost_predicted.sum() / g.cost_calculated.sum() - 1),
    })
    s = per_case.groupby(level=["scenario", "level"])
    summary = pd.DataFrame({
        "Change in Bavaria cost per inhabitant (%)": s.bavaria_change_min.min().round(1).astype(str)
        + " to " + s.bavaria_change_max.max().round(1).astype(str),
        "Median absolute error (EUR per inhabitant)": s.median_abs_error_per_inh.min().round(0).astype(int).astype(str)
        + " to " + s.median_abs_error_per_inh.max().round(0).astype(int).astype(str),
        "Median absolute percentage error (%)": s.median_abs_pct_error.min().round(0).astype(int).astype(str)
        + " to " + s.median_abs_pct_error.max().round(0).astype(int).astype(str),
        "Error of the sum over left-out areas (%)": s.sum_error_pct.min().round(1).astype(str)
        + " to " + s.sum_error_pct.max().round(1).astype(str),
    }).T
    summary.to_csv(os.path.join(a.out_dir, "leave_one_out_summary.csv"))
    print("Table 4.22  leave-one-out validation (range over the four cost cases)")
    print(summary.to_string())


if __name__ == "__main__":
    main()
