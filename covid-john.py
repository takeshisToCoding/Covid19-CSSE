import pandas as pd
import sys
import matplotlib.pyplot as plt
import os
from datetime import date


john_hopkins_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

john_hopkins_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

john_hopkins_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'


def getData(url,save=True):
    
  datum = pd.read_csv(url)
  if save:
    today = date.today().strftime('%d-%m-%Y')
    file_name = os.path.basename(url)
    datum.to_csv(today+file_name)
  return datum

def processDataset(df,count_type='Confirmed'):
  '''Remove unnecesary geographical data and preprocess the dataset'''
  #df_geo = df.loc[:,:'Long']
  df_cases = df.drop(['Lat','Long'],axis=1) 
  maping = {'Province/State':'Province','Country/Region':'Country'}
  df_cases.rename(columns=maping,inplace=True)  
  df_cases.set_index(['Country','Province'],inplace=True)
  
  stacked_df = df_cases.stack().reset_index()
  maping = {'level_2':'Date', 0: count_type}
  stacked_df.rename(columns=maping,inplace=True)
  stacked_df['Date'] = pd.to_datetime(stacked_df['Date'])
 
  return stacked_df 

if __name__=='__main__':
   
  raw_confirmed = getData(john_hopkins_confirmed,True)
  raw_deaths = getData(john_hopkins_deaths,False)
  raw_recovered = getData(john_hopkins_recovered,False)
  # print("Header")
  # print(list(raw_dataset.columns))
  covid_confirmed = processDataset(raw_confirmed)
  covid_deaths = processDataset(raw_deaths,'Deaths')
  covid_recovered = processDataset(raw_recovered,'Recovered')
  print("Headers")
  print(covid_confirmed.tail())
  print(covid_deaths.tail())
  print(covid_recovered.tail())

  #Merging
  covid_df = pd.merge(covid_confirmed,covid_deaths,on=['Country','Province','Date'])
  covid_df = pd.merge(covid_df,covid_recovered,on=['Country','Province','Date']) 
  print(covid_df.head())
  covid_mx = covid_df.loc[covid_df['Country']=='Mexico']
  
  print(covid_mx.tail())
  #plt.plot(covid_mx['Date'],covid_mx[['Confirmed','Deaths','Recovered']])
  data_cols = ['Confirmed','Deaths','Recovered']
  covid_mx.set_index('Date')[data_cols].plot()
  plt.show()
  
  today = date.today().strftime('%d-%m-%Y')  
  covid_df.to_csv('covid-19-data-'+today+'.csv')
