import pandas as pd
import geopandas as gpd
import shapely

pd.set_option('display.max_columns', None)

df=pd.read_csv('C:/Users/mayij/Desktop/Motor_Vehicle_Collisions_-_Crashes.csv')
df['date']=pd.to_datetime(df['CRASH DATE'],format='%m/%d/%Y',errors='coerce')
df['year']=df['date'].dt.year
df['month']=df['date'].dt.month

k=df[(pd.notna(df['LATITUDE'])&(pd.notna(df['LONGITUDE']))&(df['LATITUDE']!=0)&(df['LONGITUDE']!=0))].reset_index(drop=True)
k=df.copy()
k=k[(k['year']==2021)&(k['month']==9)].reset_index(drop=True)
k=k[(k['year']==2020)].reset_index(drop=True)

sum(k['NUMBER OF PERSONS INJURED'])
sum(k['NUMBER OF PERSONS KILLED'])
k=gpd.GeoDataFrame(k,geometry=[shapely.geometry.Point(x,y) for x,y in zip(k['LONGITUDE'],k['LATITUDE'])],crs=4326)
k.to_file('C:/Users/mayij/Desktop/test.geojson',driver='GeoJSON')

k=df['date'].value_counts().reset_index(drop=False).sort_values('index')
k=k['COLLISION_ID'].value_counts().reset_index(drop=False).sort_values('index')


k=df.copy()
k=k[(k['year']==2020)&(k['month']==8)].reset_index(drop=True)
k=k[k['NUMBER OF PERSONS KILLED']==1]
k=k[k['NUMBER OF PEDESTRIANS KILLED']==1]
k=k[k['NUMBER OF CYCLIST INJURED']>0]










