import pandas as pd
import numpy as np
import datetime
from datetime import datetime
data= pd.read_csv(r'C:\Thesis\Input Resources\Kraftwerksliste.csv',sep=';', encoding= 'latin_1')

data.columns=['PP_number', 'Company', 'PP_name',
       'PLZ', 'Ort',
       'Addresse', 'Bundesland', 'Blockname',
       'start',
       'status',
       'fuel',
       'type_1',
       'type_2',
       'main_fuel',
       'EEG',
       'heat_coupling',
       'capacity',
       'Bezeichnung Verknüpfungspunkt (Schaltanlage) mit dem Stromnetz der Allgemeinen Versorgung gemäß Netzbetreiber',
       'connection', 'transmission_company'] #Capacity is nominal net capacity
data['capacity'].loc[data.capacity.notnull()] = data[data.capacity.notnull()].capacity.map(lambda x : x.replace('.',''))
data['capacity'].loc[data.capacity.notnull()] = data[data.capacity.notnull()].capacity.map(lambda x : x.replace(',','.'))
data.capacity= data.capacity.astype(float)

# statuses:
'''['in Betrieb', 'Vorläufig Stillgelegt (mit StA)',
       'Gesetzlich an Stilllegung gehindert',
       'Vorläufig Stillgelegt (ohne StA)', 'Sicherheitsbereitschaft',
       'Sonderfall', 'Saisonale Konservierung',
       'gesetzlich an Stilllegung gehindert',
       'Endgültig Stillgelegt 2011 (ohne StA)',
       'Endgültig Stillgelegt 2012 (ohne StA)',
       'Endgültig Stillgelegt 2013 (mit StA)',
       'Endgültig Stillgelegt 2013 (ohne StA)',
       'Endgültig Stillgelegt 2014 (mit StA)',
       'Endgültig Stillgelegt 2014 (ohne StA)',
       'Endgültig Stillgelegt 2015 (mit StA)',
       'Endgültig Stillgelegt 2015 (ohne StA)',
       'Endgültig Stillgelegt 2016 (mit StA)',
       'Endgültig Stillgelegt 2016 (ohne StA)',
       'Endgültig Stillgelegt 2017 (mit StA)',
       'Endgültig Stillgelegt 2017 (ohne StA)',
       'Endgültig Stillgelegt 2018 (mit StA)',
       'Endgültig Stillgelegt 2019 (mit StA)',
       'Endgültig Stillgelegt 2018 (ohne StA)', 'Wegfall IWA nach DE']'''

# Fuel types:
'''(['Windenergie (Onshore-Anlage)', 'Erdgas',
       'Solare Strahlungsenergie', 'Laufwasser', 'Biomasse',
       'Mehrere Energieträger', 'Steinkohle', 'Abfall',
       'Mineralölprodukte', 'Speicherwasser (ohne Pumpspeicher)',
       'Pumpspeicher', 'Braunkohle', 'Sonstige Speichertechnologien',
       'andere Gase', 'Kernenergie', 'Sonstige Energieträger',
       'Grubengas', 'sonstige Speichertechnologien', 'Klärschlamm',
       'Windenergie (Offshore-Anlage)', 'Deponiegas', 'Geothermie',
       'Klärgas', 'Sonstige Energieträger (nicht erneuerbar)',
       'Unbekannter Energieträger'], dtype=object)
'''
data.loc[data['status'] == 'In Betrieb', 'status'] = 'in Betrieb'

#show the sum
data.loc[(data['fuel']=='Geothermie')&((data['status'] == 'in Betrieb') | \
                                       (data['status'] == 'Gesetzlich an Stilllegung gehindert')|\
                                       (data['status'] == 'Sicherheitsbereitschaft')|\
                                       (data['status'] == 'Saisonale Konservierung')|\
                                       (data['status'] == 'Sonderfall')|\
                                       (data['status'] == 'Sicherheitsbereitschaft')|\
                                       (data['status'] == 'gesetzlich an Stilllegung gehindert')),'capacity'].sum()
#group= data.groupby(by=['fuel','status'],as_index=False).sum()
#group.to_excel(r'C:\Thesis\Input Resources\2019_demand_germany.xlsx', sheet_name='Demand')

# data.replace(r'-', np.nan, regex=True)
#data['Time']=data['Time'].apply(lambda x: datetime.strptime(x, '%H:%M').hour)