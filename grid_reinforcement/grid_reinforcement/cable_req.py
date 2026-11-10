import sys, glob, os, warnings
import numpy as np, pandas as pd, h5py, pandapower as pp
warnings.filterwarnings("ignore")

THS = {"100": 1.0, "60": 0.6}


def xs_class(std_type):
    st = str(std_type)
    if "240" in st:
        return 240
    if "185" in st:
        return 185
    for s in ("150", "120", "95", "70", "50", "35", "25", "16"):
        if s in st:
            return 150
    return 240


def one(h5):
    with h5py.File(h5, "r") as hf:
        raw = hf["raw_data/net"][()]
        if isinstance(raw, np.ndarray):
            raw = raw[0]
        if isinstance(raw, bytes):
            raw = raw.decode()
    net = pp.from_json_string(raw)
    with pd.HDFStore(h5, "r") as s:
        ll = s["/pwrflw/output/post/line_loads"]
    peak = ll.xs("i_from_ka", axis=1, level=1).max().values
    ln = net.line[["std_type", "length_km", "max_i_ka", "parallel"]].copy()
    ln["peak"] = peak
    ln["xs"] = ln.std_type.map(xs_class)
    row = {"grid": int(os.path.basename(h5).split("_")[0]), "route_km": ln.length_km.sum()}
    for k, th in THS.items():
        req = np.ceil(ln.peak / (ln.max_i_ka * th)).astype(int)
        add = (req - ln.parallel).clip(lower=0)
        row[f"n_lines_TH{k}"] = int((add > 0).sum())
        row[f"reinf_route_km_TH{k}"] = ln.length_km[add > 0].sum()
        row[f"add_km_TH{k}"] = (add * ln.length_km).sum()
        for c in (150, 185, 240):
            m = ln.xs == c
            row[f"add_km_{c}_TH{k}"] = (add[m] * ln.length_km[m]).sum()
    return row


for folder in sys.argv[1:]:
    files = sorted(glob.glob(os.path.join(folder.rstrip("/"), "*.h5")))
    rows = []
    for f in files:
        try:
            rows.append(one(f))
        except Exception as e:
            print("FAIL", os.path.basename(f), e)
    df = pd.DataFrame(rows).sort_values("grid")
    out = os.path.expanduser(f"~/cable_req_{os.path.basename(folder.rstrip('/'))}.csv")
    df.to_csv(out, index=False)
    s = df.sum(numeric_only=True)
    print(os.path.basename(folder.rstrip("/")), len(df), "grids ->", out)
    print("  route km %.1f" % s.route_km)
    for k in THS:
        print("  TH%s grids %d  reinf route %.1f km  add %.1f km  (150 %.1f / 185 %.1f / 240 %.1f)" % (
            k, (df[f"n_lines_TH{k}"] > 0).sum(), s[f"reinf_route_km_TH{k}"], s[f"add_km_TH{k}"],
            s[f"add_km_150_TH{k}"], s[f"add_km_185_TH{k}"], s[f"add_km_240_TH{k}"]))
