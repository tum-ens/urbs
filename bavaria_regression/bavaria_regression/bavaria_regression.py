"""
Bavaria reinforcement cost regression (Sections 3.9.2 and 4.2.1 to 4.2.3, Tables 4.16 to 4.18 and 4.20).

Model, one fit per scenario and cost case:
    log(cost) = b * (log(pop) - mean log(pop))
              + sum_t  c_t * Type_t          (7 RegioStaR types, no constant)
              + e25 * E25 + e50 * E50        (100% electrification is the reference)
OLS with standard errors clustered by postal code area (56 clusters).

Usage:
    python bavaria_regression.py --scenario flex
    python bavaria_regression.py --scenario inflex
    python bavaria_regression.py --scenario both --bavaria bavaria_plz_all.csv

Input files in --data-dir (default: current folder):
    bavaria_{inflex,flex}_exp_{25,50,100}_TH{100,60}.csv   grid-level costs
    plz56_population.csv                                    columns plz, pop_pylovo
    bavaria_plz_all.csv  (optional, --bavaria)              all Bavarian PLZ for the total

Bavaria totals are retransformed from logs with a smearing factor estimated
separately for each electrification level, as the residual spread differs by level.

Cost cases: A1 = total_cost_A at TH100, B1 = total_cost_B at TH100,
            A2 = total_cost_A at TH60,  B2 = total_cost_B at TH60.
"""
import argparse
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

TYPES = {
    71: "81679 90469 90482 81249 80634 90489 90443 81549",
    72: "86150 86152 86153 86154 86157 93051 86159 91052",
    73: "91242 82064 82343 90571 86438 82166 86391 85521",
    74: "86922 86923 97268 91486 85302 85617 82544 91325",
    75: "95032 83024 95447 63739 84034 63743 63741 92637",
    76: "63930 86513 96482 83109 84524 83071 93326 94469",
    77: "84434 91590 94348 92718 83131 89426 94259 94428",
}
TYPE_OF = {p: t for t, s in TYPES.items() for p in s.split()}
CASES = {"A1": ("A", "100"), "B1": ("B", "100"), "A2": ("A", "60"), "B2": ("B", "60")}
LEVELS = [25, 50, 100]


# ---------------------------------------------------------------- data
def load_costs(data_dir, scenario):
    """Sum grid costs to postal code level for each cost case and electrification level."""
    rows = []
    for level in LEVELS:
        for th in ["100", "60"]:
            f = os.path.join(data_dir, f"bavaria_{scenario}_exp_{level}_TH{th}.csv")
            d = pd.read_csv(f)
            d["plz"] = d["file"].str.split("_").str[1]
            g = d.groupby("plz")[["total_cost_A", "total_cost_B"]].sum()
            for case, (m, cth) in CASES.items():
                if cth == th:
                    for plz, v in g[f"total_cost_{m}"].items():
                        rows.append((case, level, plz, v))
    out = pd.DataFrame(rows, columns=["case", "level", "plz", "cost"])
    bad = out[out.cost <= 0]
    if len(bad):
        raise ValueError(f"non-positive cost, log undefined:\n{bad}")
    return out


def design(plz, level, lpop_c, inter=None):
    """Regressor matrix. inter = None | 'pop' | 'type'."""
    X = pd.DataFrame(index=plz.index)
    X["lpop"] = lpop_c
    for t in TYPES:
        X[f"T{t}"] = (plz.map(TYPE_OF) == t).astype(float)
    X["E25"] = (level == 25).astype(float)
    X["E50"] = (level == 50).astype(float)
    if inter == "pop":
        X["lpop_E25"] = X.lpop * X.E25
        X["lpop_E50"] = X.lpop * X.E50
    if inter == "type":
        for t in list(TYPES)[1:]:
            for e in ["E25", "E50"]:
                X[f"T{t}_{e}"] = X[f"T{t}"] * X[e]
    return X


def vif_table(X):
    """VIF of each column on all other columns (no-constant design, uncentered R2)."""
    A = X.values
    out = {}
    for j, c in enumerate(X.columns):
        y = A[:, j]
        Z = np.delete(A, j, axis=1)
        r = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
        out[c] = 1.0 / (r @ r / (y @ y))
    v = pd.Series(out)
    return pd.DataFrame({"VIF": v, "Tolerance": 1 / v})


# ---------------------------------------------------------------- fit
def fit_case(d, mu, pop):
    y = np.log(d.cost)
    g = d.plz.astype("category").cat.codes
    lpop_c = np.log(d.plz.map(pop)) - mu

    def ols(inter=None):
        X = design(d.plz, d.level, lpop_c, inter)
        return X, sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": g})

    X, r = ols()
    names = list(X.columns)
    n, k = X.shape
    r2 = 1 - ((y - r.fittedvalues) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    ar2 = 1 - (1 - r2) * (n - 1) / (n - k)

    def wald(res, R):
        w = res.wald_test(np.atleast_2d(R), use_f=True, scalar=True)
        return float(w.statistic), float(w.pvalue)

    E = np.eye(k)
    ix = lambda c: names.index(c)
    type_contr = [E[ix(f"T{t}")] - E[ix("T71")] for t in list(TYPES)[1:]]
    R_model = [E[ix("lpop")]] + type_contr + [E[ix("E25")], E[ix("E50")]]

    res = {
        "params": r.params, "bse": r.bse, "R2": r2, "adjR2": ar2,
        "F_model": wald(r, R_model), "t_lpop": (r.tvalues["lpop"], r.pvalues["lpop"]),
        "F_type": wald(r, type_contr),
    }
    for inter in ["pop", "type"]:
        Xi, ri = ols(inter)
        added = [j for j, c in enumerate(Xi.columns) if c not in names]
        res[f"F_{inter}xE"] = wald(ri, np.eye(Xi.shape[1])[added])
        res[f"adjR2_{inter}xE"] = 1 - (1 - (1 - ((y - ri.fittedvalues) ** 2).sum()
                                             / ((y - y.mean()) ** 2).sum())) * (n - 1) / (n - Xi.shape[1])
    res["X"] = X
    return res


def stars(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


# ---------------------------------------------------------------- Bavaria total
def bavaria_totals(costs, mu, pop, bav_file):
    a = pd.read_csv(bav_file, dtype={"plz": str})
    a["plz"] = a.plz.str.zfill(5)
    B = a.groupby("plz").agg(pop=("pop", "first"), pp=("pop_postcode", "first"), t=("regio7", "min"))
    B["pop"] = B.pp.fillna(B["pop"])
    B = B[B["pop"] > 0]
    total_pop = B["pop"].sum()
    rows = []
    for case in CASES:
        d = costs[costs.case == case].reset_index(drop=True)
        y = np.log(d.cost)
        lpop_c = np.log(d.plz.map(pop)) - mu
        for inter in [None, "type"]:
            X = design(d.plz, d.level, lpop_c, inter)
            r = sm.OLS(y, X).fit()
            for L in LEVELS:
                # smearing factor per electrification level (Duan 1983, Manning 1998):
                # mean of exp(residual) over the sample observations at level L
                smear = float(np.mean(np.exp(r.resid[(d.level == L).values])))
                Xp = design(pd.Series(B.index, index=B.index), pd.Series(L, index=B.index),
                            np.log(B["pop"]) - mu, inter)
                # Bavarian PLZ carry their own RegioStaR type, not the sample list
                for t in TYPES:
                    Xp[f"T{t}"] = (B.t == t).astype(float)
                if inter == "type":
                    for t in list(TYPES)[1:]:
                        for e in ["E25", "E50"]:
                            Xp[f"T{t}_{e}"] = Xp[f"T{t}"] * Xp[e]
                raw = np.exp(Xp[X.columns] @ r.params).sum()
                rows.append((case, L, inter or "simple", raw / 1e9, smear, raw * smear / 1e9))
    T = pd.DataFrame(rows, columns=["case", "level", "model", "raw_bn", "smear", "bn"])

    # 1) model comparison, both models smeared
    C = T.pivot_table(index=["case", "level"], columns="model", values="bn")
    C["diff_%"] = 100 * (C["type"] / C["simple"] - 1)
    C = C[["simple", "type", "diff_%"]].round(3)

    # 2) Bavaria prediction with the simple model
    S = T[T.model == "simple"].set_index(["case", "level"])
    Pr = pd.DataFrame({
        "smear_factor": S.smear.round(3),
        "total_bn_EUR_unsmeared": S.raw_bn.round(3),
        "total_bn_EUR": S.bn.round(3),
        "EUR_per_inhabitant": (S.bn * 1e9 / total_pop).round(2),
    })
    return C, Pr, len(B), total_pop


# ---------------------------------------------------------------- report
def report(scenario, data_dir, pop, mu, bav_file, out_dir):
    costs = load_costs(data_dir, scenario)
    costs = costs[costs.plz.isin(pop.index)]
    print(f"\n{'=' * 70}\nSCENARIO: {scenario}   postal codes: {costs.plz.nunique()}   "
          f"observations per case: {len(costs) // 4}")

    fits = {c: fit_case(costs[costs.case == c].reset_index(drop=True), mu, pop) for c in CASES}

    # VIF depends on the regressors only, identical for all cases and both scenarios
    print("\nVIF and tolerance")
    print(vif_table(fits["A1"]["X"]).round(3).to_string())

    # regression table in the layout of Tables 4.17 and 4.18
    rows = {}
    labels = {"lpop": "Log (Population), centered", **{f"T{t}": f"Type {t}" for t in TYPES},
              "E25": "Electrification level 25%", "E50": "Electrification level 50%"}
    for key, lab in labels.items():
        rows[lab] = {c: f"{f['params'][key]:.3f} ({f['bse'][key]:.3f})" for c, f in fits.items()}
    rows["R2"] = {c: f"{f['R2']:.3f}" for c, f in fits.items()}
    rows["Adjusted R2"] = {c: f"{f['adjR2']:.3f}" for c, f in fits.items()}
    rows["F (9, 55), model"] = {c: f"{f['F_model'][0]:.2f}{stars(f['F_model'][1])}" for c, f in fits.items()}
    rows["t, log(population)"] = {c: f"{f['t_lpop'][0]:.2f}{stars(f['t_lpop'][1])}" for c, f in fits.items()}
    rows["F (6, 55), RegioStaR type"] = {c: f"{f['F_type'][0]:.2f}{stars(f['F_type'][1])}" for c, f in fits.items()}
    rows["F (2, 55) log population x electrification levels"] = {
        c: f"{f['F_popxE'][0]:.2f}{stars(f['F_popxE'][1])} ({f['F_popxE'][1]:.3f})" for c, f in fits.items()}
    rows["F (12, 55) RegioStaR type x electrification levels"] = {
        c: f"{f['F_typexE'][0]:.2f}{stars(f['F_typexE'][1])} ({f['F_typexE'][1]:.3f})" for c, f in fits.items()}
    tab = pd.DataFrame(rows).T[list(CASES)]
    tab.columns = ["A1 (parallel, 100%)", "B1 (separate, 100%)", "A2 (parallel, 60%)", "B2 (separate, 60%)"]
    print("\nRegression table (clustered SE in parentheses, p-value in parentheses for interaction F)")
    print(tab.to_string())
    tab.to_csv(os.path.join(out_dir, f"regression_table_{scenario}.csv"))

    # exact p-values and derived figures for the text
    der = {}
    for c, f in fits.items():
        p = f["params"]
        tc = {t: p[f"T{t}"] for t in TYPES}
        gap = p["T77"] - p["T71"]
        der[c] = {
            "p F model": f["F_model"][1], "p t lpop": f["t_lpop"][1], "p F type": f["F_type"][1],
            "p F pop x E": f["F_popxE"][1], "p F type x E": f["F_typexE"][1],
            "pop doubled, cost factor": 2 ** p["lpop"],
            "lowest type": min(tc, key=tc.get), "highest type": max(tc, key=tc.get),
            "T77 - T71": gap, "T77 / T71 factor": np.exp(gap),
            "50% lower than 100% [%]": 100 * (1 - np.exp(p["E50"])),
            "25% lower than 100% [%]": 100 * (1 - np.exp(p["E25"])),
            "25% -> 50% factor": np.exp(p["E50"] - p["E25"]),
            "50% -> 100% factor": np.exp(-p["E50"]),
            "adj R2 simple": f["adjR2"], "adj R2 type x E model": f["adjR2_typexE"],
        }
    der = pd.DataFrame(der)
    print("\nDerived figures for the text")
    with pd.option_context("display.float_format", lambda v: f"{v:.4g}"):
        print(der.to_string())
    der.to_csv(os.path.join(out_dir, f"regression_derived_{scenario}.csv"))

    if bav_file:
        C, Pr, nb, tp = bavaria_totals(costs, mu, pop, bav_file)
        print(f"\nBavaria: {nb} PLZ, population {tp:,.0f}. All totals smeared per electrification level.")
        print("\nModel comparison, billion EUR: simple model vs type x electrification model")
        print(C.to_string())
        print(f"max |diff| at 25%: {C.xs(25, level='level')['diff_%'].abs().max():.1f}%   "
              f"at 50/100%: {C.drop(25, level='level')['diff_%'].abs().max():.1f}%")
        print("\nBavaria prediction, simple model")
        print(Pr.to_string())
        C.to_csv(os.path.join(out_dir, f"bavaria_model_comparison_{scenario}.csv"))
        Pr.to_csv(os.path.join(out_dir, f"bavaria_prediction_{scenario}.csv"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", choices=["flex", "inflex", "both"], default="both")
    ap.add_argument("--data-dir", default=".")
    ap.add_argument("--pop", default="plz56_population.csv")
    ap.add_argument("--bavaria", default=None, help="bavaria_plz_all.csv for the Bavaria total check")
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()

    pop = pd.read_csv(os.path.join(a.data_dir, a.pop), dtype={"plz": str}).set_index("plz")["pop_pylovo"]
    mu = np.log(pop).mean()
    print(f"sample PLZ {len(pop)}, geometric mean population {np.exp(mu):.0f} (centering value)")
    bav = os.path.join(a.data_dir, a.bavaria) if a.bavaria else None
    for sc in (["inflex", "flex"] if a.scenario == "both" else [a.scenario]):
        report(sc, a.data_dir, pop, mu, bav, a.out_dir)


if __name__ == "__main__":
    main()
