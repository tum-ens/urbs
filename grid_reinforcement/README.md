# Grid reinforcement: cable and transformer reinforcement cost from power flow results

The reinforcement step follows the power flow calculation (Step 4 of the GridExpand chain, `run_pwrflw.py`). For each grid it compares the annual maximum line current and transformer loading with the limits and prices the reinforcement (Section 3.7 of the thesis).

## Method (Section 3.7)

**Cables**

* Additional parallel cables per section: `ceil(peak current / (permissible current × limit)) − existing cables`, with limit 1.0 (100%) or 0.6 (60%).
* Cross-section classes of Wintzek et al. (2021): 150, 185 and 240 mm². Cables below 150 mm² use the 150 mm² cost, cables above 240 mm² the 240 mm² cost.
* Method A prices every additional cable as parallel laying. Method B prices the first additional cable of a section as separate laying and further cables as parallel laying.

**Transformers and substations** (100% of the rated power)

* Single units up to 1,600 kVA (400, 630, 800, 1,000, 1,200, 1,600 kVA); above 1,600 kVA additional units are installed in parallel.
* Substation replacement when the first unit is 1,000 kVA or above; one new substation for each additional parallel unit.
* 400 kVA cost: linear fit to the Wintzek et al. (2021) prices of 630 to 1,600 kVA.

**Prices:** Wintzek et al. (2021) in 2021 prices, escalated to 2026 with Destatis indices: ×1.384 for cables and civil works, ×1.521 for transformers and substations.

All unit costs, rules and sources are listed in [COST_ASSUMPTIONS.md](COST_ASSUMPTIONS.md).

## How to run

```bash
pip install -r requirements.txt

# reinforcement cost per grid; the cable limit is set with LOAD_THRESHOLD
LOAD_THRESHOLD=1.0 python analyze_expansion.py <folder_with_powerflow_h5> forch_exp_100_TH100.csv
LOAD_THRESHOLD=0.6 python analyze_expansion.py <folder_with_powerflow_h5> forch_exp_100_TH60.csv

# additional cable length by cross-section (Appendix A, Figures 4.13–4.16)
python cable_req.py <folder_with_powerflow_h5>

# Forchheim tables from the per-grid results in data/forchheim
python summarize_forchheim.py --data-dir data/forchheim --out-dir output
```

`analyze_expansion.py` and `cable_req.py` need the power flow HDF5 files (`raw_data/net`, `pwrflw/output/post/*`), which are not included because of their size. `summarize_forchheim.py` runs on the included CSV files.

## Scripts and thesis tables

|Script|Output|Thesis|
|-|-|-|
|`analyze_expansion.py`|one CSV per case, electrification level and cable limit (`data/forchheim/`, `../bavaria_regression/data/`)|Section 3.7; input of all cost results|
|`cable_req.py`|additional cable length per cross-section|Appendix A, cable length in Figures 4.13–4.16|
|`summarize_forchheim.py`|`output/forchheim_cost.csv`, `output/log_forchheim.txt`|Tables 4.7–4.14, reductions in Section 4.1.5|

`summarize_forchheim.py` reproduces Tables 4.7 to 4.14 exactly, including the split into transformer, substation replacement and new substations.

## Data: `data/forchheim/`

Per-grid results of the 114 synthetic grids of Forchheim (postal code 91301, 30,330 inhabitants), file name `<case>_exp_<level>_TH<limit>.csv`:

|Prefix|Case|
|-|-|
|`forch`|inflexible|
|`forchf`|flexible|
|`forch_p14a`|inflexible with Section 14a control|
|`forch_p14af2`|flexible with Section 14a control|

Levels 25, 50, 75 and 100% electrification; TH100 / TH60 = 100% / 60% cable thermal loading limit.

