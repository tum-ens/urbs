import pandas as pd
import numpy as np
import datetime
from datetime import datetime
data= pd.read_csv(r'C:\Thesis\Input Resources\Realisierter_Stromverbrauch_201901010000_202001012345_1.csv',sep=';')
data.columns=['Date','Time','Load']
data['Time']=data['Time'].apply(lambda x: datetime.strptime(x, '%H:%M').hour)
data['Date']=data['Date'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y').date())
data['Load']=data.Load.map(lambda x : x.replace('.',''))
data['Load']=data.Load.map(lambda x: x.replace(',','.'))
data['Load']= data.Load.replace('-', np.nan)
data.Load= data.Load.astype(float)
group= data.groupby(by=[data.Date,data.Time],as_index=False).sum()
group.to_excel(r'C:\Thesis\Input Resources\2019_demand_germany.xlsx', sheet_name='Demand')

# data.replace(r'-', np.nan, regex=True)
#data['Time']=data['Time'].apply(lambda x: datetime.strptime(x, '%H:%M').hour)