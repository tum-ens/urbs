"""Check the stratified sample of 56 postal code areas against the population quantile groups.

For each RegioStaR type the Bavarian postal code areas are sorted by population and split into eight
groups with the same number of areas (Section 3.9.1). The script reports any sampled area that does not
lie in its quantile group and draws the population range, the group boundaries and the sampled areas
(supplementary figure, not a figure of the thesis).

Usage: python check_sample.py --all ../data/bavaria_plz_regio7.csv --sample ../data/sample56.csv
Outputs: Sample_quantile_groups.xlsx (native Excel chart), Sample_quantile_groups.png / .svg
"""
import argparse
import numpy as np
import pandas as pd

TYPES = [71, 72, 73, 74, 75, 76, 77]


def prepare(all_csv, sample_csv):
    a = pd.read_csv(all_csv, dtype={'plz': str}); s = pd.read_csv(sample_csv, dtype={'plz': str})
    a['regio7'] = a.regio7.astype(int); s['regio7'] = s.regio7.astype(int)
    rng, bnd, chk = [], [], []
    for t in TYPES:
        g = a[a.regio7 == t].sort_values('pop').reset_index(drop=True)
        groups = np.array_split(np.arange(len(g)), 8)              # eight groups with the same number of areas
        rng.append((t, g['pop'].min(), g['pop'].max(), len(g)))
        for k in range(7):                                          # boundary between group k+1 and k+2
            lo, hi = g['pop'].iloc[groups[k][-1]], g['pop'].iloc[groups[k + 1][0]]
            bnd.append((t, float(np.sqrt(lo * hi)) if lo > 0 else float(hi)))
        grp = {p: k + 1 for k, idx in enumerate(groups) for p in g.plz.iloc[idx]}
        for r in s[s.regio7 == t].itertuples():
            chk.append((t, r.bin, grp.get(r.plz)))
    bad = [c for c in chk if c[1] != c[2]]
    print('areas per type:', {r[0]: r[3] for r in rng}, 'total', sum(r[3] for r in rng))
    print('sampled areas whose group differs from this split:', bad if bad else 'none')
    return pd.DataFrame(rng, columns=['regio7', 'min', 'max', 'n']), pd.DataFrame(bnd, columns=['regio7', 'pop']), s


def excel(R, Bd, s, out='Sample_quantile_groups.xlsx'):
    from openpyxl import Workbook
    from openpyxl.chart import ScatterChart, Reference, Series
    from openpyxl.chart.marker import Marker
    from openpyxl.chart.shapes import GraphicalProperties
    from openpyxl.chart.text import RichText
    from openpyxl.drawing.line import LineProperties
    from openpyxl.drawing.text import Paragraph, ParagraphProperties, CharacterProperties, Font as DFont
    wb = Workbook(); ws = wb.active; ws.title = 'Data'
    ws.append(['Range: RegioStaR type', 'Population', '', 'Boundary: RegioStaR type', 'Population', '', 'Sample: RegioStaR type', 'Population', 'plz', 'Quantile group'])
    r = 2
    for row in R.itertuples():                                  # min and max per type, blank row = gap in the line
        ws.cell(r, 1, row.regio7); ws.cell(r, 2, float(row.min)); ws.cell(r + 1, 1, row.regio7); ws.cell(r + 1, 2, float(row.max)); r += 3
    nR = r - 2
    for i, row in enumerate(Bd.itertuples(), start=2): ws.cell(i, 4, row.regio7); ws.cell(i, 5, row.pop)
    for i, row in enumerate(s.itertuples(), start=2): ws.cell(i, 7, row.regio7); ws.cell(i, 8, float(row.pop)); ws.cell(i, 9, row.plz); ws.cell(i, 10, int(row.bin))

    def cp(sz, col='404040', b=False): return CharacterProperties(sz=sz, b=b, solidFill=col, latin=DFont(typeface='Arial'))
    def rich(sz, col='404040'): return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp(sz, col)), endParaRPr=cp(sz, col))])
    c = ScatterChart(); c.title = None; c.style = 13; c.display_blanks = 'gap'
    spec = [(1, 2, nR, 'Population range of all areas', 'line'),
            (4, 5, len(Bd), 'Quantile group boundaries', 'dash'),
            (7, 8, len(s), 'Sampled areas', 'dot')]
    for xc, yc, n, name, kind in spec:
        ser = Series(Reference(ws, min_col=yc, min_row=2, max_row=n + 1), Reference(ws, min_col=xc, min_row=2, max_row=n + 1), title=name)
        if kind == 'line':
            ser.marker = Marker(symbol='none'); ser.graphicalProperties.line.solidFill = 'A6A6A6'; ser.graphicalProperties.line.width = 28575
        elif kind == 'dash':
            ser.marker = Marker(symbol='dash', size=10)
            ser.marker.graphicalProperties = GraphicalProperties(solidFill='595959', ln=LineProperties(solidFill='595959'))
            ser.graphicalProperties.line.noFill = True
        else:
            ser.marker = Marker(symbol='circle', size=7)
            ser.marker.graphicalProperties = GraphicalProperties(solidFill='C00000', ln=LineProperties(solidFill='FFFFFF', w=6350))
            ser.graphicalProperties.line.noFill = True
        c.series.append(ser)
    c.x_axis.scaling.min = 70; c.x_axis.scaling.max = 78; c.x_axis.majorUnit = 1
    c.x_axis.number_format = '[<70.5]"";[>77.5]"";0'; c.x_axis.numFmt = c.x_axis.number_format
    c.x_axis.majorGridlines = None
    c.y_axis.scaling.logBase = 10; c.y_axis.scaling.min = 100; c.y_axis.scaling.max = 100000; c.y_axis.number_format = '#,##0'
    c.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill='E5E5E5', w=6350))
    c.x_axis.title = 'RegioStaR type'; c.y_axis.title = 'Population'
    c.x_axis.delete = False; c.y_axis.delete = False
    c.x_axis.txPr = rich(900); c.y_axis.txPr = rich(900, '595959')
    c.legend.position = 't'; c.legend.txPr = rich(850)
    c.graphical_properties = GraphicalProperties(ln=LineProperties(noFill=True))
    c.width = 17; c.height = 9
    fig = wb.create_sheet('Figure', 0); fig['A1'] = 'Population range, quantile groups and sampled postal code areas by RegioStaR type in Bavaria'
    fig.add_chart(c, 'A3'); wb.save(out); print('saved', out)


def figure(R, Bd, s, out='Sample_quantile_groups'):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from matplotlib.lines import Line2D
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    for row in R.itertuples(): ax.plot([row.regio7] * 2, [row.min, row.max], color='#A6A6A6', lw=2.2, solid_capstyle='butt', zorder=1)
    ax.scatter(Bd.regio7, Bd['pop'], marker='_', s=160, color='#595959', linewidths=1.2, zorder=2)
    ax.scatter(s.regio7, s['pop'], s=30, color='#C00000', edgecolors='white', linewidths=0.6, zorder=3)
    ax.set_yscale('log'); ax.set_ylim(100, 100000)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_xticks(TYPES); ax.set_xlim(70.4, 77.6)
    ax.set_xlabel('RegioStaR type'); ax.set_ylabel('Population')
    ax.grid(axis='y', color='#E5E5E5', lw=0.6); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    h = [Line2D([0], [0], color='#A6A6A6', lw=2.2), Line2D([0], [0], marker='_', color='#595959', ls='none', ms=12, mew=1.2),
         Line2D([0], [0], marker='o', color='#C00000', mec='white', ls='none', ms=6)]
    ax.legend(h, ['Population range of all areas', 'Quantile group boundaries', 'Sampled areas'],
              loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3, frameon=False, fontsize=8)
    fig.tight_layout()
    for ext in ('png', 'svg'): fig.savefig(f'{out}.{ext}', dpi=300)
    print('saved', out + '.png/.svg')


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--all', required=True); p.add_argument('--sample', required=True)
    q = p.parse_args(); R, Bd, S = prepare(q.all, q.sample); excel(R, Bd, S); figure(R, Bd, S)
