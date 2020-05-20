import pandas as pd
import numpy as np
import datetime
from datetime import datetime
data= pd.read_csv(r'C:\Thesis\Input Resources\Excel\Actual_generation_201601010000_201612312359_1.csv',sep=';')

data['Time']=data['Time of day'].apply(lambda x: x[:-3])
data['Time']=data['Time'].apply(lambda x: datetime.strptime(x, '%H:%M').hour)
#data['Date']=data['Date'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y').date())
data['Hydropower[MWh]']=data['Hydropower[MWh]'].map(lambda x : x.replace('.',''))
data['Hydropower[MWh]']=data['Hydropower[MWh]'].map(lambda x: x.replace(',','.'))
data['Hydropower[MWh]']= data['Hydropower[MWh]'].replace('-', np.nan)
data['Hydropower[MWh]']= data['Hydropower[MWh]'].astype(float)

data['Wind offshore[MWh]']=data['Wind offshore[MWh]'].map(lambda x : x.replace('.',''))
data['Wind offshore[MWh]']=data['Wind offshore[MWh]'].map(lambda x: x.replace(',','.'))
data['Wind offshore[MWh]']= data['Wind offshore[MWh]'].replace('-', np.nan)
data['Wind offshore[MWh]']= data['Wind offshore[MWh]'].astype(float)

data['Wind onshore[MWh]']=data['Wind onshore[MWh]'].map(lambda x : x.replace('.',''))
data['Wind onshore[MWh]']=data['Wind onshore[MWh]'].map(lambda x: x.replace(',','.'))
data['Wind onshore[MWh]']= data['Wind onshore[MWh]'].replace('-', np.nan)
data['Wind onshore[MWh]']= data['Wind onshore[MWh]'].astype(float)

data['Photovoltaics[MWh]']=data['Photovoltaics[MWh]'].map(lambda x : x.replace('.',''))
data['Photovoltaics[MWh]']=data['Photovoltaics[MWh]'].map(lambda x: x.replace(',','.'))
data['Photovoltaics[MWh]']= data['Photovoltaics[MWh]'].replace('-', np.nan)
data['Photovoltaics[MWh]']= data['Photovoltaics[MWh]'].astype(float)

group= data.groupby(by=[data.Date,data.Time],as_index=False).sum()
group.to_excel(r'C:\Thesis\Input Resources\Excel\generation_germany_2016.xlsx', sheet_name='generation-2016')

# data.replace(r'-', np.nan, regex=True)
#data['Time']=data['Time'].apply(lambda x: datetime.strptime(x, '%H:%M').hour)