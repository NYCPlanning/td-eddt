import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import shapely
from shapely import wkt


pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/EDDT/'


df=pd.read_csv(path+'Motor_Vehicle_Collisions_-_Crashes.csv')
df['date']=pd.to_datetime(df['CRASH DATE'],format='%m/%d/%Y',errors='coerce')
df['year']=df['date'].dt.year
df['month']=df['date'].dt.month
df=df[(pd.notna(df['LATITUDE'])&(pd.notna(df['LONGITUDE']))&(df['LATITUDE']!=0)&(df['LONGITUDE']!=0))].reset_index(drop=True)
df=df[(df['year']==2019)].reset_index(drop=True)
df['lat']=df['LATITUDE'].copy()
df['long']=df['LONGITUDE'].copy()
df['pedinj']=df['NUMBER OF PEDESTRIANS INJURED'].copy()
df['cycinj']=df['NUMBER OF CYCLIST INJURED'].copy()
df['motinj']=df['NUMBER OF MOTORIST INJURED'].copy()
df['totinj']=df['NUMBER OF PERSONS INJURED'].copy()
df['pedfat']=df['NUMBER OF PEDESTRIANS KILLED'].copy()
df['cycfat']=df['NUMBER OF CYCLIST KILLED'].copy()
df['motfat']=df['NUMBER OF MOTORIST KILLED'].copy()
df['totfat']=df['NUMBER OF PERSONS KILLED'].copy()
df=df[['pedinj','cycinj','motinj','totinj','pedfat','cycfat','motfat','totfat','lat','long']].reset_index(drop=True)
df=gpd.GeoDataFrame(df,geometry=[shapely.geometry.Point(x,y) for x,y in zip(df['long'],df['lat'])],crs=4326)
puma=gpd.read_file(path+'puma.geojson')
puma.crs=4326
puma['puma']=puma[['GEOID10']].copy()
puma=puma[['puma','geometry']].reset_index(drop=True)
df=gpd.sjoin(df,puma,how='left',op='intersects')
df=df.groupby(['puma'],as_index=False).agg({'pedinj':'sum','cycinj':'sum','motinj':'sum','totinj':'sum',
                                            'pedfat':'sum','cycfat':'sum','motfat':'sum','totfat':'sum'}).reset_index(drop=True)
df.to_csv(path+'crash.csv',index=False)




df=pd.merge(puma,df,on='puma',how='left')
df.to_file(path+'crash.geojson',driver='GeoJSON')








