# Bavaria regression: extrapolating the reinforcement cost of synthetic low-voltage grids

The reinforcement cost was calculated for every synthetic low-voltage grid of 56 sampled postal code areas in Bavaria (2,629 grids), for the inflexible and flexible cases at 25%, 50% and 100% electrification. A regression on population and RegioStaR type extrapolates the cost to all 2,064 postal code areas of Bavaria. The per-grid costs come from `../grid_reinforcement/analyze_expansion.py`.

## Model

One fit per scenario (inflexible, flexible) and cost case (A1, B1, A2, B2):

```
log(cost) = b · (log(pop) − mean log(pop))
          + Σ_t c_t · Type_t          7 RegioStaR types, no constant
          + e25 · E25 + e50 · E50     100% electrification is the reference
```

- OLS with standard errors clustered by postal code area (56 clusters).
- The prediction is retransformed with Duan's smearing factor, computed per electrification level.
- Cost cases: A = parallel laying, B = separate laying; 1 = 100% cable thermal loading limit, 2 = 60% (Section 3.7 of the thesis).

## How to run

Requires Python 3.10 or later.

```bash
pip install -r requirements.txt
python bavaria_regression.py --scenario both --data-dir data --bavaria bavaria_plz_all.csv --out-dir output
python extrapolate.py        --data-dir data --out-dir output
python leave_one_out.py      --data-dir data --out-dir output
```

The three scripts run in about 20 seconds in total.

## Scripts and thesis tables

| Script | Output in `output/` | Thesis |
|---|---|---|
| `bavaria_regression.py` | `regression_table_{inflex,flex}.csv`, `regression_derived_{inflex,flex}.csv`, VIF in `log_regression.txt` | Tables 4.16–4.18 |
| | `bavaria_prediction_{inflex,flex}.csv` | Table 4.20, Figure 4.20 |
| | `bavaria_model_comparison_{inflex,flex}.csv` | simple model vs. RegioStaR type × electrification model (Section 4.2.1) |
| `extrapolate.py` | `bavaria_cost_total.csv` | Table 4.20 (same values as above) |
| | `bavaria_cost_by_type.csv` | Table 4.21 |
| | `outside_sample_range.csv` | Table 4.23 |
| | `unit_cost_sensitivity.csv` | Table 4.24 |
| `leave_one_out.py` | `leave_one_out_summary.csv`, `leave_one_out_runs.csv` | Table 4.22 |
| `sampling/check_sample.py` | check of the sample, `Sample_quantile_groups.xlsx/.png/.svg` | Section 3.9.1, Table 3.21 |

The `output/` folder contains the results of the run used for the thesis. 

## Sample

The 56 sampled postal code areas are a fixed input (`data/sample56.csv`, Table 3.21). For each RegioStaR type, the Bavarian postal code areas are sorted by population and split into eight groups with the same number of areas, and one area is taken from each group (Section 3.9.1).

`sampling/check_sample.py` checks that every sampled area lies in its quantile group and draws the population range, the group boundaries and the sampled areas:

```bash
cd sampling
python check_sample.py --all ../data/bavaria_plz_regio7.csv --sample ../data/sample56.csv
```

## Data

| File | Content |
|---|---|
| `bavaria_{inflex,flex}_exp_{25,50,100}_TH{100,60}.csv` | Reinforcement result of each sampled grid from `analyze_expansion.py`: line and transformer cost per cost method, transformer peak and required rating, voltage range. `file` holds `<grid>_<plz>_<…>.h5`. TH100 / TH60 = 100% / 60% cable thermal loading limit. Costs in EUR, 2026 prices. |
| `plz56_population.csv` | Population of the 56 sampled postal code areas (`pop_pylovo` is used in the regression). |
| `sample56.csv` | Sampled postal code areas with RegioStaR type (`regio7`) and population quantile group (`bin`, 1–8). |
| `bavaria_plz_all.csv` | All Bavarian postal code areas with population, municipality key (`ags`) and RegioStaR type (`regio7`, `regio5`). |
| `bavaria_plz_regio7.csv` | One row per Bavarian postal code area (`plz`, `pop`, `regio7`), derived from `bavaria_plz_all.csv` for the sample check. |

Sources of the input data: population from the Census 2022 (Statistische Ämter des Bundes und der Länder, 2024); RegioStaR types from the Federal Ministry for Digital and Transport (BMDV).

The HDF5 files of the individual grids (input, optimization and power flow results) are not included because of their size.

## Notes

- Bavaria: 2,064 postal code areas with 12,446,745 inhabitants.
- The sample covers 957 to 42,982 inhabitants per postal code area 82 areas of Bavaria lie outside this range (Table 4.23).