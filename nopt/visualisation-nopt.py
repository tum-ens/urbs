import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import glob
import matplotlib as mpl
mpl.rcParams['figure.autolayout'] = True
#plt.tight_layout()
filename=r'C:\Thesis\pro.xlsx'
result_dir=r'C:\Thesis'
slack_list= ['0.005','0.01','0.02','0.03','0.04','0.05','0.075','0.1']
commodities=  ['Elec','CO2','H2']
sites=['Germany']
objective=['Photovoltaics']
stf=['2020','2030','2040','2040','2050']
info_dict={'slack_list':slack_list,'commodities':commodities,'sites':sites,'stf':stf,'objective':objective}
com_sum_dict={}
time_series_dict={}
min_cost_ts={}
list_of_technologies=['Photovoltaics','Onshore wind','Offshore wind','Biogas', 'Biomass', 'Gas','CCS NGCC',
                      'Geothermal Powerplant',  'Electrolyzer', 'Fuelcell','Hydropower','Hard Coal',
                      'Lignite','Nuclear' ] #, ,'Dummy Gas-CCGT''Dummy H2-CCGT', 'Dummy Gas-GT',,
      # 'Dummy H2-GT', 'CCGT','Gas Turbine',,'Slack PP', 'Curtailment' , ,
#

# Tum Official
colors={'Tum-main-b': (0, 101, 189),'Tum-main-W': (255, 255, 255),
'Tum-main-K': (0, 0, 0),
'Tum-sec-db': (0, 82, 147),
'Tum-sec-b': (100, 160, 200),
'Tum-sec-lb': (152, 198, 234),
'Tum-sec-g': (153, 153, 153),
'Tum-acc-o': (227, 114, 34),
'Tum-acc-y': (162, 173, 0),
'Tum-acc-g': (218, 215, 203)}
def to_color(obj=None):
    if obj is None:
        obj = 'Tum-main-b'
    try:
        color = tuple(rgb / 255.0 for rgb in colors[obj])
    except KeyError:
        # random deterministic color
        import hashlib
        color = '#' + hashlib.sha1(obj.encode()).hexdigest()[-6:]
    return color

with pd.ExcelFile(filename) as xls:
   # costs = xls.parse('Costs').ffill()
    pro_cap=xls.parse('Near-Optimal Process Capacities').ffill()
  #  sto_cap = xls.parse('Near-Optimal Storage Capacities').ffill()
   # mincost_comsum=xls.parse('Commodity sums_Min_Cost').ffill()

    # '''   for year in stf:
    #     for site in sites:
    #         for com in commodities:
    #             ts_name='Min_Cost.'+year+ '.'+site+ '.'+com+' timeseries'
    #             ts_name=ts_name[:31]
    #             min_cost_ts[ts_name]=xls.parse(ts_name).ffill()
    #
    # for slack in slack_list:
    #     for year in stf:
    #         for site in sites:
    #             for com in commodities:
    #                 comsum_name1='Commodity sums'+slack+'_Min'
    #                 comsum_name2 = 'Commodity sums' + slack + '_Max'
    #                 ts_name1=ts=slack+'_Min.'+year+'.'+site+'.'+com+' timeseries'
    #                 ts_name1=ts_name1[:31]
    #                 ts_name2=ts=slack+'_Max.'+year+'.'+site+'.'+com+' timeseries'
    #                 ts_name2=ts_name2[:31]
    #                 #time_series_dict[ts_name1] = []
    #                 #time_series_dict[ts_name2] = []
    #                 com_sum_dict[comsum_name1] = xls.parse(comsum_name1).ffill()
    #                 com_sum_dict[comsum_name2] = xls.parse(comsum_name2).ffill()
    #                 time_series_dict[ts_name1]=xls.parse(ts_name1).ffill()
    #                 time_series_dict[ts_name2]=xls.parse(ts_name2).ffill()
    #
    #



def merge_processes(data,list_of_technologies,year_list):
    data=data[data.Stf.isin(year_list)]
    columns = list(data.columns[4:])
    columns.append('Stf')
    columns.append('Process')
    plot_df = pd.DataFrame(columns=columns)
    for pro in list_of_technologies:
        if pro=='Photovoltaics':
          pro_df = data[(data.Process == 'Photovoltaics') | (data.Process == 'Photovoltaics-30') | (data.Process == 'Photovoltaics-40') | ( data.Process == 'Photovoltaics-50')].copy()
          pro = pro_df.groupby(by='Stf', as_index=False).sum()
          pro['Process'] = 'Photovoltaics'
          plot_df=pd.concat([plot_df,pro],sort=False,ignore_index=True)
        elif pro == 'Onshore Wind':
          pro_df = data[(data.Process == 'Onshore wind') | (data.Process == 'Onshore wind-30') | (
                      data.Process == 'Onshore wind-40') | (data.Process == 'Onshore wind-50')].copy()
          pro = pro_df.groupby(by='Stf', as_index=False).sum()
          pro['Process'] = 'Onshore wind'
          plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
        elif pro == 'Offshore wind':
          pro_df = data[(data.Process == 'Offshore wind') | (data.Process == 'Offshore wind-30') | (
                      data.Process == 'Offshore wind-40')].copy()
          pro = pro_df.groupby(by='Stf', as_index=False).sum()
          pro['Process'] = 'Offshore wind'
          plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
        elif pro == 'Biogas':
          pro_df = data[(data.Process == 'Biogas') | ( data.Process == 'Biogas-40')].copy()
          pro = pro_df.groupby(by='Stf', as_index=False).sum()
          pro['Process'] = 'Biogas'
          plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
        elif pro == 'CCGT':
            pro_df = data[(data.Process == 'CCGT') | (data.Process == 'CCGT-30') | (
                  data.Process == 'CCGT-40')| (data.Process == 'CCGT-50')].copy()
            pro = pro_df.groupby(by='Stf', as_index=False).sum()
            pro['Process'] = 'CCGT'
        elif pro == 'Gas Turbine':
            pro_df = data[(data.Process == 'Gas Turbine') | (data.Process == 'Gas Turbine-30') | (
                  data.Process == 'Gas Turbine-40')| (data.Process == 'Gas Turbine-50')].copy()
            pro = pro_df.groupby(by='Stf', as_index=False).sum()
            pro['Process'] = 'Gas Turbine'
            plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
        elif pro == 'Gas':
            pro_df = data[(data.Process == 'CCGT') | (data.Process == 'CCGT-30') | (data.Process == 'CCGT-40') | (
                    data.Process == 'CCGT-50')|(data.Process == 'Gas Turbine') | (data.Process == 'Gas Turbine-30') | (
                    data.Process == 'Gas Turbine-40')| (data.Process == 'Gas Turbine-50')].copy()
            pro = pro_df.groupby(by='Stf', as_index=False).sum()
            pro['Process'] = 'CCGT + GT'
            plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
        elif pro == 'Hard Coal':
          pro_df = data[(data.Process == 'Hard Coal') | ( data.Process == 'Hard Coal-30')].copy()
          pro = pro_df.groupby(by='Stf', as_index=False).sum()
          pro['Process'] = 'Hard Coal'
          plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
        elif pro == 'Lignite':
          pro_df = data[(data.Process == 'Lignite') | ( data.Process == 'Lignite-30')].copy()
          pro = pro_df.groupby(by='Stf', as_index=False).sum()
          pro['Process'] = 'Lignite'
          plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
        else:
            pro_df= data[data.Process == pro].copy()
            pro=pro_df[columns]
            plot_df = pd.concat([plot_df, pro], sort=False,ignore_index=True)
    return plot_df

def tidy_data (df):
    data_set = df.copy(deep=True)
    data_set = data_set.reset_index(drop=True)
    data_set = data_set.melt(id_vars=["Stf", "Process"], var_name=["Optimization"], value_name="Capacities")
    data_set.loc[(data_set.Optimization == 'Minimum Cost'), 'Optimization'] = 'Min-0.0'
    data_set[['Objective', 'Slack']] = data_set.Optimization.str.split("-", expand=True)
    data_set.drop(columns='Optimization', inplace=True)
    data_set['Slack'] = data_set.Slack.astype(float)
    data_set['Slack'] = data_set['Slack'] * 100
    return data_set



plot_cap = merge_processes(pro_cap, list_of_technologies, [2050])
df = tidy_data(plot_cap)
df_g = df[df.Process != info_dict['objective'][0]].copy(deep=True)
order =list_of_technologies.copy()
order.remove(info_dict['objective'][0])
constant_cap=[]
changing_cap=[]
for pro in order:
    if df_g[df_g.Process == pro].Capacities.min()==df_g[df_g.Process == pro].Capacities.max():
        constant_cap.append(pro)
    else:
        changing_cap.append(pro)




def plot_generation_capacities(pro_cap,changing_cap,info_dict,result_dir,year_list=[2050]):
    year=year_list[0]
    gen_cap = merge_processes(pro_cap, list_of_technologies, [2050])
    df_td = tidy_data(gen_cap)
    df_pgc = df_td[df_td.Process.isin(changing_cap)]

    fig, ax = plt.subplots(figsize=(12,8))

    for i, item in enumerate(changing_cap):
        x = [i, i]
        y = [df_pgc[df_pgc.Process == item].Capacities.min(), df_pgc[df_pgc.Process == item].Capacities.max()]
        ax.plot(x, y, 'o-', linewidth=3, markersize=8, color='slategray', zorder=0)
    # sns.boxplot(x='Process',y='Capacities',data=df_g,order=changing_cap,whis=0,fliersize=0,ax=ax,color='cornflowerblue',zorder=5)
    cost_min = df_pgc[df_pgc.Slack == 0]
    sns.pointplot(x='Process', y='Capacities', data=cost_min, order=changing_cap, ci=0, join=False, ax=ax, color='k',
                  zorder=10)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

    ax.grid()
    ax.set_ylabel('Capacities (MW)')
    ax.set_title(
        'Site: Germany' + '\n Objective: '+str(info_dict['objective'] )+ '\n Year: '+ str(year) + '\n Generation Capacity Range for \n Slacks: ' + str(info_dict['slack_list'] ))
    fig_filename = os.path.join(result_dir,'generation_capacities.png')
    fig.savefig(fig_filename, bbox_inches='tight')
    plt.close(fig)

def stacked_plot_capacities(pro_cap,changing_cap,info_dict,result_dir,year_list=[2020,2030,2040,2050]):
    return None


def line_plot_capacities(pro_cap, info_dict, result_dir,year_list=[2020,2030,2040,2050],slack_to_plot=[0,2,5,10]):

    """Plot near-optimal capacities of objected processes and regions for different slack numbers and years.
       Args:
           - prob: urbs model instance
           - figure_size: optional (width, height) tuple in inch; default: (16, 12)

       Returns:
           fig: figure handle
       """
    plot_cap = merge_processes(pro_cap, info_dict['objective'], year_list)
    data_set = plot_cap[plot_cap.Process == info_dict['objective'][0]].copy(deep=True)
    df_ut = data_set.reset_index(drop=True)
    df = tidy_data(df_ut)
    df_o = df[df.Stf.isin(slack_to_plot)]


    fig, ax1 = plt.subplots(figsize=(16, 12))

   # slack_array = list(map(float, info_dict['slack_list']))
   # slack_array.append(0)
    slack_array= slack_to_plot
    slack_array.sort()
    slackorder = list(np.array(slack_array)*100)

    ax1 = sns.pointplot(x="Stf", y="Capacities", hue="Slack", hue_order=slackorder, data=df_o[(df_o.Objective=='Min')],
                        palette='Paired', ax=ax1,estimator=np.sum, ci=None)
    ax1 = sns.pointplot(x="Stf", y="Capacities", hue="Slack", hue_order=slackorder, data=df_o[(df_o.Objective=='Max')],
                        palette='Paired', ax=ax1,estimator=np.sum, ci=None)
    ax1.set_title("Change in {} capacity with different cost increase allowences and years".format( info_dict['objective'][0]),
                  fontsize=16)
    ax1.set_xlabel('Modelled Year', fontsize=12)
    ax1.set_ylabel('Total {} Capacity (MW)'.format( info_dict['objective'][0]), fontsize=12)
    color = tuple(rgb / 255.0 for rgb in (128, 128, 128))

    handles, labels = ax1.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    lg = ax1.legend(by_label.values(),by_label.keys(),
                   title='Allowed \n Cost \n Increase (%)',
                   frameon=False,
                   loc='upper left',
                   bbox_to_anchor=(1, 1),
                  fontsize='large',title_fontsize='large')
    plt.setp(lg.get_patches(), edgecolor=color,
             linewidth=0.15)

    # save plot to files
    fig_filename = os.path.join(result_dir,'Intertemporal Capacity Change of Objected Technology.png')
    fig.savefig(fig_filename, bbox_inches='tight')
    plt.close(fig)

def line_plot_shaded(pro_cap, info_dict, result_dir,year_list=[2020,2030,2040,2050],slack_to_plot=[0,2,5,10]):
    obj_capacity = merge_processes(pro_cap, list_of_technologies, year_list)
    lps_data = obj_capacity[obj_capacity.Process == info_dict['objective'][0]].copy(deep=True)
    df_ut = lps_data.reset_index()
    df_lps = tidy_data(df_ut)
    data1 = df_lps[df_lps.Objective=='Min']
    data2 = df_lps[df_lps.Objective == 'Max']
    fig, ax = plt.subplots(figsize=(12, 6))
    color_list = ['Tum-main-K',
                  'Tum-main-b',
                  'Tum-sec-b',
                  'Tum-sec-lb',
                  'Tum-acc-o',
                  'Tum-acc-y',
                  'Tum-sec-db',
                  'Tum-acc-g']
    for i, sl in enumerate(sorted(slack_to_plot)):
        line1, = ax.plot('Stf', 'Capacities', data=data1[data1.Slack == sl], color=to_color(color_list[i]),
                         label='{}%'.format(sl), marker='o')
        line2, = ax.plot('Stf', 'Capacities', data=data2[data2.Slack == sl], color=to_color(color_list[i]),
                         label='_{}%'.format(sl), marker='o')
        if not sl==0:
            ax.fill_between(data1[data1.Slack == sl].Stf, data1[data1.Slack == sl].Capacities,
                            data2[data2.Slack == sl].Capacities,
                            facecolor=to_color(color_list[i]), alpha=0.9-(i/10))

    ax.legend(loc='best', title='Allowed Cost Increase')
    ax.grid()
    ax.set_xlabel('Modelled Years', fontsize=16)
    plt.xticks(list(data1.Stf.unique()), list(str(int(x)) for x in list(data1.Stf.unique())))
    ax.set_ylabel(info_dict['objective'][0]+' Capacity (GW)', fontsize=16)
    ax.set_title('Near Cost Optimal Intertemporal Solution', fontsize=16,
                 pad=15)  #
    ax.set_ylim(0, (data2.Capacities.max() + 5000))
    ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x) // 1000, ',')))
    fig_filename = os.path.join(result_dir,'Intertemporal_objected_pro.png')
    fig.savefig(fig_filename, bbox_inches='tight')
    plt.close(fig)

plot_generation_capacities(pro_cap,list_of_technologies,info_dict,result_dir)
#line_plot_capacities(pro_cap, info_dict, result_dir,slack_to_plot=[0,2,5,10])
line_plot_shaded(pro_cap, info_dict, result_dir,year_list=[2020,2030,2040,2050],slack_to_plot=[0,2,5,10])

print('do_nothing')