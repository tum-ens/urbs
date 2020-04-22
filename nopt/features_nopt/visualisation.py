import pandas as pd
import numpy  as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from ..colorcodes_nopt import COLORS
from ..plot_nopt import to_color
plt.style.use('urbs')



def tidy_data (df):
    data_set = df.copy(deep=True)
    data_set = data_set.reset_index()
    data_set['Max-0.0'] = data_set['Minimum Cost']
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


def single_year_capacities_bar(list_of_processes_to_plot,data_frame,fig_name_to_save='single_year_bar.png'):
    '''

    Args:
        list_of_processes_to_plot: list of process names that are desired to appear on plot given as they are in the data set
        data_frame: prob.near_optimal_capacities
        fig_name_to_save: desired path and figure name and extension to save the figure

    Returns:
        Nothing, saves the figure
    '''
    # prepare data for plotting
    plot_pro=list_of_processes_to_plot
    year= data_frame.Stf.values[0]
    data_s = tidy_data(data_frame)
    data_s = data_s.groupby(by=['Stf', 'Process', 'Objective', 'Slack'], as_index=False)['Capacities'].sum()
    data1 = data_s[(data_s.Objective == 'Min') & (data_s.Slack == 0) & (data_s.Process.isin(plot_pro))].copy(deep=True)
    data1.sort_values(by=['Capacities'], inplace=True)

    #plotting
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh('Process', 'Capacities', data=data1, color=to_color('Tum-main-b'))
    ax.grid()
    ax.set_ylabel('Process', fontsize=16)
    ax.set_xlabel('Capacity (MW)', fontsize=16)
    ax.set_title('Minimum Cost Solution\n Germany-{}, 95% GHG Reduction'.format(year), fontsize=16)
    ax.set_xlim(0, (data1.Capacities.max() + 1000))
    ax.set_xticks(np.arange(0, data1.Capacities.max() + 5000, 25000))
    ax.get_xaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.xticks(rotation=45, horizontalalignment='right')
    plt.savefig(fig_name_to_save)
    plt.close(fig)


def single_year_nopt_cap_line (list_of_processes_to_plot,data_frame,fig_name_to_save='single_year_nopt_line.png'):
    '''

    Args:
        list_of_processes_to_plot: list of objected process names as they appear in the data set
        data_frame: prob.near_optimal_capacities
        fig_name_to_save: desired path and figure name and extension to save the figure

    Returns:
        Nothing, saves the figure
    '''
    # prepare data for plotting
    plot_pro=list_of_processes_to_plot
    year= data_frame.Stf.values[0]
    data_s = tidy_data(data_frame)
    data_s = data_s.groupby(by=['Stf', 'Process', 'Objective', 'Slack'], as_index=False)['Capacities'].sum()
    data1 = data_s[(data_s.Objective == 'Min') & (data_s.Slack == 0) & (data_s.Process.isin(plot_pro))].copy(deep=True)
    data1.sort_values(by=['Capacities'], inplace=True)
    data2 = data_s[(data_s.Objective == 'Max') & (data_s.Process.isin(plot_pro))].copy(deep=True)
    data2.sort_values(by=['Capacities'], ascending=False, inplace=True)

    #plotting
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh('Process', 'Capacities', data=data1, color=to_color('Tum-main-b'))
    ax.grid()
    ax.set_ylabel('Process', fontsize=16)
    ax.set_xlabel('Capacity (MW)', fontsize=16)
    ax.set_title('Minimum Cost Solution\n Germany-2050, 95% GHG Reduction', fontsize=16)
    ax.set_xlim(0, (data1.Capacities.max() + 1000))
    ax.set_xticks(np.arange(0, data1.Capacities.max() + 5000, 25000))
    ax.get_xaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.xticks(rotation=45, horizontalalignment='right')
    plt.savefig(fig_name_to_save)
    plt.close(fig)