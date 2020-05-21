import pandas as pd
import numpy as np
import datetime
from datetime import datetime
data= pd.read_csv(r'C:\Thesis\Input Resources\Excel\DE_2019_generation.csv',sep=';')
PV_2016= 40680
Wind_on_2016=45280
Wind_off_2016=4150
Hydro_2016=5490

PV_2017= 42290
Wind_on_2017=50170
Wind_off_2017=5410
Hydro_2017=4780

PV_2018=45230
Wind_on_2018=52450
Wind_off_2018=6400
Hydro_2018=4780

PV_2019=49180
Wind_on_2019=53370
Wind_off_2019=7500
Hydro_2019=4780

data['Time']=data['Time of day'].apply(lambda x: datetime.strptime(x, '%I:%M %p').hour)
data['Date']=data['Date'].apply(lambda x: datetime.strptime(x, '%b %d, %Y').date())
#data['Hydropower[MWh]']=data['Hydropower[MWh]'].map(lambda x : x.replace('.',''))
#data['Hydropower[MWh]']=data['Hydropower[MWh]'].map(lambda x: x.replace(',','.'))
if not data['Hydropower[MWh]'].dtype==float:
    data['Hydropower[MWh]']=data['Hydropower[MWh]'].map(lambda x: x.replace(',',''))
    data['Hydropower[MWh]']= data['Hydropower[MWh]'].replace('-', np.nan)
    data['Hydropower[MWh]']= data['Hydropower[MWh]'].astype(float)

#data['Wind offshore[MWh]']=data['Wind offshore[MWh]'].map(lambda x : x.replace('.',''))
#data['Wind offshore[MWh]']=data['Wind offshore[MWh]'].map(lambda x: x.replace(',','.'))
if not data['Wind offshore[MWh]'].dtype==float:
    data['Wind offshore[MWh]']=data['Wind offshore[MWh]'].map(lambda x: x.replace(',',''))
    data['Wind offshore[MWh]']= data['Wind offshore[MWh]'].replace('-', np.nan)
    data['Wind offshore[MWh]']= data['Wind offshore[MWh]'].astype(float)

#data['Wind onshore[MWh]']=data['Wind onshore[MWh]'].map(lambda x : x.replace('.',''))
#data['Wind onshore[MWh]']=data['Wind onshore[MWh]'].map(lambda x: x.replace(',','.'))
if not data['Wind onshore[MWh]'].dtype==float:
    data['Wind onshore[MWh]']=data['Wind onshore[MWh]'].map(lambda x: x.replace(',',''))
    data['Wind onshore[MWh]']= data['Wind onshore[MWh]'].replace('-', np.nan)
    data['Wind onshore[MWh]']= data['Wind onshore[MWh]'].astype(float)

#data['Photovoltaics[MWh]']=data['Photovoltaics[MWh]'].map(lambda x : x.replace('.',''))
#data['Photovoltaics[MWh]']=data['Photovoltaics[MWh]'].map(lambda x: x.replace(',','.'))
if not data['Photovoltaics[MWh]'].dtype==float:
    data['Photovoltaics[MWh]']=data['Photovoltaics[MWh]'].map(lambda x: x.replace(',',''))
    data['Photovoltaics[MWh]']= data['Photovoltaics[MWh]'].replace('-', np.nan)
    data['Photovoltaics[MWh]']= data['Photovoltaics[MWh]'].astype(float)

group= data.groupby(by=[data.Date,data.Time],as_index=False).sum()
group['PV']= group['Photovoltaics[MWh]']/PV_2019
group['Hydro']= group['Hydropower[MWh]']/Hydro_2019
group['wind_on']= group['Wind onshore[MWh]']/Wind_on_2019
group['wind_off']= group['Wind offshore[MWh]']/Wind_off_2019
print('PV (h):',group['PV'].sum())
print('Hydro (h):',group['Hydro'].sum())
print('Wind_off (h):',group['wind_off'].sum())
print('wind on (h):',group['wind_on'].sum())
group.to_excel(r'C:\Thesis\Input Resources\Excel\flh_germany_2019.xlsx', sheet_name='renewables_DE_19')

# data.replace(r'-', np.nan, regex=True)
#data['Time']=data['Time'].apply(lambda x: datetime.strptime(x, '%H:%M').hour)