# Bavaria regression: extrapolating the reinforcement cost of synthetic low-voltage grids

The reinforcement cost was calculated for every synthetic low-voltage grid of 56 sampled postal code areas in Bavaria (2,629 grids), for the inflexible and flexible cases at 25%, 50% and 100% electrification. A regression on population and RegioStaR type extrapolates the cost to all 2,064 postal code areas of Bavaria.

## Model

One fit per scenario (inflexible, flexible) and cost case (A1, B1, A2, B2):

```
log(cost) = b · (log(pop) − mean log(pop))
          + Σ\_t c\_t · Type\_t          7 RegioStaR types, no constant
          + e25 · E25 + e50 · E50     100% electrification is the reference
```

* OLS with standard errors clustered by postal code area (56 clusters).
* The prediction is retransformed with Duan's smearing factor, computed per electrification level.
* Cost cases: A = parallel laying, B = separate laying; 1 = 100% cable thermal loading limit, 2 = 60% (Section 3.7 of the thesis).

## How to run

Requires Python 3.10 or later.

```bash
pip install -r requirements.txt
python bavaria\_regression.py --scenario both --data-dir data --out-dir output
python extrapolate.py        --data-dir data --out-dir output
python leave\_one\_out.py      --data-dir data --out-dir output
```



## Scripts and thesis tables

|Script|Output in `output/`|Thesis|
|-|-|-|
|`bavaria\_regression.py`|`regression\_table\_{inflex,flex}.csv`, `regression\_derived\_{inflex,flex}.csv`, VIF in `log\_regression.txt`|Tables 4.16–4.18|
|`extrapolate.py`|`bavaria\_cost\_total.csv`|Table 4.20, Figure 4.20|
||`bavaria\_cost\_by\_type.csv`|Table 4.21|
||`outside\_sample\_range.csv`|Table 4.23|
||`unit\_cost\_sensitivity.csv`|Table 4.24|
|`leave\_one\_out.py`|`leave\_one\_out\_summary.csv`, `leave\_one\_out\_runs.csv`|Table 4.22|

The `output/` folder contains the results of the run used for the thesis.

## Data

|File|Content|
|-|-|
|`bavaria\_{inflex,flex}\_exp\_{25,50,100}\_TH{100,60}.csv`|Reinforcement result of each sampled grid: line and transformer cost per cost method, transformer peak and required rating, voltage range. `file` holds `<grid>\_<plz>\_<…>.h5`. TH100 / TH60 = 100% / 60% cable thermal loading limit. Costs in EUR, 2026 prices.|
|`plz56\_population.csv`|Population of the 56 sampled postal code areas (`pop\_pylovo` is used in the regression).|
|`sample56.csv`|Sampled postal code areas with RegioStaR type (`regio7`) and population quantile group (`bin`, 1–8).|
|`bavaria\_plz\_all.csv`|All Bavarian postal code areas with population, municipality key (`ags`) and RegioStaR type (`regio7`, `regio5`).|

Sources of the input data: population from the Census 2022 (Statistische Ämter des Bundes und der Länder, 2024); RegioStaR types from the Federal Ministry for Digital and Transport (BMDV). The grid results come from the computation chain of Sections 3.2 to 3.7 of the thesis (pylovo, SurroGrid demand allocation, urbs, pandapower power flow).

The HDF5 files of the individual grids (input, optimization and power flow results) are not included because of their size.

## Notes

* Bavaria: 2,064 postal code areas with 12,446,745 inhabitants.
* The sample covers 957 to 42,982 inhabitants per postal code area
* 82 areas of Bavaria lie outside this range (Table 4.23).



