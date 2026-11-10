"""
Reinforcement cost of Forchheim by case and electrification level (Section 4.1.4, Tables 4.7 to 4.14).

Reads the per-grid results of analyze_expansion.py and splits the transformer cost into
transformer equipment, substation replacement and new substations with the same rule as
analyze_expansion.trafo_costs:
  - units up to 1,600 kVA, additional units in parallel above 1,600 kVA,
  - substation replacement when the first unit is 1,000 kVA or above,
  - one new substation for each additional parallel unit.

Usage:
    python summarize_forchheim.py --data-dir data/forchheim --out-dir output
"""
import argparse
import os

import pandas as pd

from analyze_expansion import STATION_NEW, STATION_RENEW, STATION_THRESHOLD_KVA, TRF, W_RONT_COST, W_RONT_KVA

CASES = {"inflexible": "forch", "flexible": "forchf",
         "inflexible_14a": "forch_p14a", "flexible_14a": "forch_p14af2"}
LEVELS = [25, 50, 75, 100]
INHABITANTS = 30330


def units(required_kva):
    """Transformer units installed for a required capacity (same rule as analyze_expansion)."""
    top = W_RONT_KVA[-1]
    if required_kva > top:
        n_full = int(required_kva // top)
        rest = required_kva - n_full * top
        sizes = [top] * n_full
        if rest > 0:
            sizes.append(next(k for k in W_RONT_KVA if k >= rest))
        return sizes
    return [next((k for k in W_RONT_KVA if k >= required_kva), top)]


def split_trafo(d):
    """Transformer equipment, substation replacement and new substation cost (EUR) per grid."""
    cost = dict(zip(W_RONT_KVA, W_RONT_COST))
    rows = []
    for r in d.itertuples():
        if r.trafo_cost_AB <= 0:
            rows.append((0.0, 0.0, 0.0))
            continue
        s = units(r.trafo_required_kva)
        rows.append((TRF * sum(cost[k] for k in s),
                     TRF * STATION_RENEW if s[0] >= STATION_THRESHOLD_KVA else 0.0,
                     TRF * STATION_NEW * (len(s) - 1)))
    return pd.DataFrame(rows, columns=["transformer", "substation_replacement", "new_substation"], index=d.index)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=os.path.join("data", "forchheim"))
    ap.add_argument("--out-dir", default="output")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    out = []
    for case, prefix in CASES.items():
        for L in LEVELS:
            d100 = pd.read_csv(os.path.join(a.data_dir, f"{prefix}_exp_{L}_TH100.csv"))
            d60 = pd.read_csv(os.path.join(a.data_dir, f"{prefix}_exp_{L}_TH60.csv"))
            t = split_trafo(d100).sum() / 1e6
            assert abs(t.sum() - d100.trafo_cost_AB.sum() / 1e6) < 1e-3   # split adds up to the result file
            row = {"case": case, "level": L,
                   "Transformer": t.transformer, "Substation replacement": t.substation_replacement,
                   "New substation": t.new_substation, "Transformer and substations": t.sum(),
                   "Cables A1": d100.line_cost_A.sum() / 1e6, "Cables A2": d60.line_cost_A.sum() / 1e6,
                   "Cables B1": d100.line_cost_B.sum() / 1e6, "Cables B2": d60.line_cost_B.sum() / 1e6,
                   "Total A1": d100.total_cost_A.sum() / 1e6, "Total A2": d60.total_cost_A.sum() / 1e6,
                   "Total B1": d100.total_cost_B.sum() / 1e6, "Total B2": d60.total_cost_B.sum() / 1e6,
                   "Grids with transformer reinforcement": int((d100.trafo_cost_AB > 0).sum()),
                   "Grids with cable reinforcement, 100% limit": int((d100.n_overloaded_lines > 0).sum()),
                   "Grids with cable reinforcement, 60% limit": int((d60.n_overloaded_lines > 0).sum())}
            out.append(row)
    T = pd.DataFrame(out)
    T.to_csv(os.path.join(a.out_dir, "forchheim_cost.csv"), index=False)

    money = [c for c in T.columns if c not in ("case", "level") and not c.startswith("Grids")]
    for case in CASES:
        S = T[T.case == case].set_index("level")
        print(f"\n{case}: reinforcement cost, million EUR in 2026 prices")
        print(S[money].T.round(2).to_string())
        print(f"{case}: reinforcement cost per inhabitant, EUR ({INHABITANTS:,} inhabitants)")
        print((S[["Total A1", "Total A2", "Total B1", "Total B2"]].T * 1e6 / INHABITANTS).round(0).astype(int).to_string())

    base = T[(T.case == "inflexible") & (T.level == 100)].iloc[0]
    print("\nReduction relative to the inflexible case at 100% (%)")
    for case in list(CASES)[1:]:
        r = T[(T.case == case) & (T.level == 100)].iloc[0]
        print(f"  {case:15s} A1 {100 * (1 - r['Total A1'] / base['Total A1']):5.1f}   "
              f"B2 {100 * (1 - r['Total B2'] / base['Total B2']):5.1f}")


if __name__ == "__main__":
    main()
