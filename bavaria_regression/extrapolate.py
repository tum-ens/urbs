"""
Extrapolation of the reinforcement cost to Bavaria (Sections 3.9.2, 4.2.2 to 4.2.4).

For each scenario (inflexible, flexible) and cost case (A1, B1, A2, B2) the regression
model of bavaria_regression.py is fitted on the 56 sampled postal code areas and applied to
all 2,064 postal code areas of Bavaria. The prediction is retransformed from logs with
Duan's smearing factor, computed from the residuals of the respective electrification level.

Outputs (in --out-dir):
    bavaria_cost_total.csv        total cost (bn EUR) and cost per inhabitant      Table 4.20
    bavaria_cost_by_type.csv      cost per inhabitant by RegioStaR type at 100%    Table 4.21
    outside_sample_range.csv      areas outside the sampled population range      Table 4.23
    unit_cost_sensitivity.csv     +-20% cable / transformer unit cost             Table 4.24

Usage:
    python extrapolate.py --data-dir data --out-dir output
"""
import argparse
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

import bavaria_regression as br

warnings.filterwarnings("ignore")
SCENARIOS = ["inflex", "flex"]


# ---------------------------------------------------------------- data
def load_sample_pop(data_dir):
    return pd.read_csv(os.path.join(data_dir, "plz56_population.csv"),
                       dtype={"plz": str}).set_index("plz")["pop_pylovo"]


def load_bavaria(data_dir):
    """All Bavarian postal code areas with population and RegioStaR type."""
    a = pd.read_csv(os.path.join(data_dir, "bavaria_plz_all.csv"), dtype={"plz": str})
    a["plz"] = a.plz.str.zfill(5)
    b = a.groupby("plz").agg(pop=("pop", "first"), pp=("pop_postcode", "first"), t=("regio7", "min"))
    b["pop"] = b.pp.fillna(b["pop"])
    return b[b["pop"] > 0][["pop", "t"]]


def load_costs(data_dir, scenario, pop, scale_cable=1.0, scale_trafo=1.0):
    """Postal code level cost per case and level; cable and transformer cost can be scaled."""
    rows = []
    for level in br.LEVELS:
        for th in ["100", "60"]:
            d = pd.read_csv(os.path.join(data_dir, f"bavaria_{scenario}_exp_{level}_TH{th}.csv"))
            d["plz"] = d["file"].str.split("_").str[1]
            d["A"] = d.line_cost_A * scale_cable + d.trafo_cost_AB * scale_trafo
            d["B"] = d.line_cost_B * scale_cable + d.trafo_cost_AB * scale_trafo
            g = d.groupby("plz")[["A", "B"]].sum()
            for case, (m, cth) in br.CASES.items():
                if cth == th:
                    rows += [(case, level, plz, v) for plz, v in g[m].items()]
    c = pd.DataFrame(rows, columns=["case", "level", "plz", "cost"])
    return c[c.plz.isin(pop.index)].reset_index(drop=True)


# ---------------------------------------------------------------- model
def fit(d, pop, mu):
    """OLS fit (point estimates; clustering does not change them) and smearing factor per level."""
    X = br.design(d.plz, d.level, np.log(d.plz.map(pop)) - mu)
    r = sm.OLS(np.log(d.cost), X).fit()
    smear = {L: np.exp(r.resid[d.level == L]).mean() for L in br.LEVELS}
    return X.columns, r.params, smear


def design_bavaria(bav, cols, level, mu):
    X = br.design(pd.Series(bav.index, index=bav.index), pd.Series(level, index=bav.index),
                  np.log(bav["pop"]) - mu)
    for t in br.TYPES:  # Bavarian areas carry their own RegioStaR type
        X[f"T{t}"] = (bav.t == t).astype(float)
    return X[cols]


def predict_bavaria(costs, case, level, pop, mu, bav):
    """Predicted cost of every Bavarian postal code area (EUR)."""
    cols, params, smear = fit(costs[costs.case == case].reset_index(drop=True), pop, mu)
    return np.exp(design_bavaria(bav, cols, level, mu) @ params) * smear[level]


# ---------------------------------------------------------------- tables
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="output")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    pop = load_sample_pop(a.data_dir)
    mu = np.log(pop).mean()
    bav = load_bavaria(a.data_dir)
    inh = bav["pop"].sum()
    print(f"Bavaria: {len(bav)} postal code areas, {int(inh):,} inhabitants")

    tot_rows, type_rows, sens_rows, out_rows = [], [], [], []
    lo, hi = pop.min(), pop.max()
    for sc in SCENARIOS:
        base = load_costs(a.data_dir, sc, pop)
        for case in br.CASES:
            for L in br.LEVELS:
                p = predict_bavaria(base, case, L, pop, mu, bav)
                tot_rows.append((sc, case, L, p.sum() / 1e9, p.sum() / inh))
                if L == 100:
                    per_type = p.groupby(bav.t).sum() / bav.groupby("t")["pop"].sum()
                    type_rows += [(sc, case, t, v) for t, v in per_type.items()]
                if L in (50, 100):
                    # Table 4.23: share of cost outside the sampled population range
                    smp_t = pd.Series({plz: br.TYPE_OF[plz] for plz in pop.index})
                    t_lo = pop.groupby(smp_t).min()
                    t_hi = pop.groupby(smp_t).max()
                    masks = {
                        "outside overall sample range": (bav["pop"] < lo) | (bav["pop"] > hi),
                        "below range of own type": bav["pop"] < bav.t.map(t_lo),
                        "above range of own type": bav["pop"] > bav.t.map(t_hi),
                    }
                    masks["outside range of own type"] = masks["below range of own type"] | masks["above range of own type"]
                    for k, m in masks.items():
                        out_rows.append((k, sc, case, L, int(m.sum()), 100 * bav["pop"][m].sum() / inh,
                                         100 * p[m].sum() / p.sum()))
            # Table 4.24: unit-cost sensitivity at 50% and 100%
            for L in (50, 100):
                ref = predict_bavaria(base, case, L, pop, mu, bav).sum()
                for lab, sc_c, sc_t in [("cable +20%", 1.2, 1.0), ("cable -20%", 0.8, 1.0),
                                        ("transformer +20%", 1.0, 1.2), ("transformer -20%", 1.0, 0.8)]:
                    c = load_costs(a.data_dir, sc, pop, sc_c, sc_t)
                    v = predict_bavaria(c, case, L, pop, mu, bav).sum()
                    sens_rows.append((sc, case, L, lab, 100 * (v / ref - 1)))

    T = pd.DataFrame(tot_rows, columns=["scenario", "case", "level", "total_bn_EUR", "EUR_per_inhabitant"])
    T.to_csv(os.path.join(a.out_dir, "bavaria_cost_total.csv"), index=False)
    print("\nTable 4.20  Bavaria, EUR per inhabitant")
    print(T.pivot_table(index=["scenario", "level"], columns="case", values="EUR_per_inhabitant")
          [list(br.CASES)].round(2).to_string())
    print("\nTotal, bn EUR")
    print(T.pivot_table(index=["scenario", "level"], columns="case", values="total_bn_EUR")
          [list(br.CASES)].round(3).to_string())

    Y = pd.DataFrame(type_rows, columns=["scenario", "case", "regiostar_type", "EUR_per_inhabitant"])
    Y.to_csv(os.path.join(a.out_dir, "bavaria_cost_by_type.csv"), index=False)
    print("\nTable 4.21  EUR per inhabitant by RegioStaR type, 100%")
    print(Y.pivot_table(index="regiostar_type", columns=["scenario", "case"], values="EUR_per_inhabitant")
          .round(2).to_string())

    O = pd.DataFrame(out_rows, columns=["group", "scenario", "case", "level", "n_areas",
                                        "share_population_pct", "share_cost_pct"])
    O.to_csv(os.path.join(a.out_dir, "outside_sample_range.csv"), index=False)
    print(f"\nTable 4.23  sampled population range {lo:,} to {hi:,}")
    print(O.groupby("group", sort=False).agg(n_areas=("n_areas", "first"),
                                              share_population=("share_population_pct", "first"),
                                              cost_min=("share_cost_pct", "min"),
                                              cost_max=("share_cost_pct", "max")).round(1).to_string())

    S = pd.DataFrame(sens_rows, columns=["scenario", "case", "level", "variation", "change_pct"])
    S.to_csv(os.path.join(a.out_dir, "unit_cost_sensitivity.csv"), index=False)
    print("\nTable 4.24  change of the Bavaria cost per inhabitant (%)")
    print(S[S.variation.str.contains(r"\+")].pivot_table(index=["scenario", "case"],
          columns=["variation", "level"], values="change_pct").round(1).to_string())


if __name__ == "__main__":
    main()
