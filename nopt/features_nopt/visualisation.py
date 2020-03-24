import pandas as pd
import numpy  as np

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib


from matplotlib import dates as mdates
from matplotlib.dates import DateFormatter


def tidy_data (df):
    data_set = df.copy(deep=True)
    data_set = data_set.reset_index()
    data_set = data_set.melt(id_vars=["Stf", "Site", "Process"], var_name=["Optimization"], value_name="Capacities")
    data_set.loc[(data_set.Optimization == 'Minimum Cost'), 'Optimization'] = 'Min-0.0'
    data_set[['Objective', 'Slack']] = data_set.Optimization.str.split("-", expand=True)
    data_set.drop(columns='Optimization', inplace=True)
    data_set['Slack'] = data_set.Slack.astype(float)
    data_set['Slack'] = data_set['Slack'] * 100
    return data_set

def plot_capacity_to_years(df,result_dir):
    df_tidy=tidy_data(df)
    df_select = df_tidy[(df_tidy.Process == 'Wind park') | (df_tidy.Process == 'Photovoltaics')]
    df = df_select.groupby(by=['Stf', 'Objective', 'Slack'], as_index=False).sum()

    colorPalette = {'Max': 'black', 'Min': 'red'}

    sns.set(context='paper', style='ticks',rc={'axes.grid' :True,'figure.subplot.top':0.88}) #rc={"lines.linewidth": 2}
    g = sns.relplot(x="Slack", y="Capacities", col="Stf", hue="Objective",
                    data=df,
                    palette=colorPalette, col_wrap=4, height=6, aspect=0.8,kind='line',ci=None,style='Objective',markers=True)

    g.fig.suptitle('Objected Capacities vs Slacks through years', fontsize=12,
                   fontweight='bold', y=0.98)

    g = sns.relplot(x="Stf", y="Capacities", col="Slack", hue="Objective",
                    data=df,
                    palette=colorPalette, col_wrap=4, height=6, aspect=0.8,kind='line',ci=None,style='Objective',markers=True)
    g.fig.suptitle('Objected Capacities vs Years through different Slacks', fontsize=12, fontweight='bold', y=0.98)

    plt.show()
    plt.close('all')