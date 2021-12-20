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
df=df[(df['year']==2020)].reset_index(drop=True)
df['lat']=df['LATITUDE'].copy()
df['long']=df['LONGITUDE'].copy()
df['pedinj']=df['NUMBER OF PEDESTRIANS INJURED'].copy()
df['cycinj']=df['NUMBER OF CYCLIST INJURED'].copy()
df['motinj']=df['NUMBER OF MOTORIST INJURED'].copy()
df['totinj']=df['NUMBER OF PERSONS INJURED'].copy()
df['pedkill']=df['NUMBER OF PEDESTRIANS KILLED'].copy()
df['cyckill']=df['NUMBER OF CYCLIST KILLED'].copy()
df['motkill']=df['NUMBER OF MOTORIST KILLED'].copy()
df['totkill']=df['NUMBER OF PERSONS KILLED'].copy()
df=df[['pedinj','cycinj','motinj','totinj','pedkill','cyckill','motkill','totkill','lat','long']].reset_index(drop=True)
df=gpd.GeoDataFrame(df,geometry=[shapely.geometry.Point(x,y) for x,y in zip(df['long'],df['lat'])],crs=4326)
puma=gpd.read_file(path+'puma.geojson')
puma.crs=4326
puma['puma']=puma[['GEOID10']].copy()
puma=puma[['puma','geometry']].reset_index(drop=True)
df=gpd.sjoin(df,puma,how='left',op='intersects')
df=df.groupby(['puma'],as_index=False).agg({'pedinj':'sum','cycinj':'sum','motinj':'sum','totinj':'sum',
                                            'pedkill':'sum','cyckill':'sum','motkill':'sum','totkill':'sum'}).reset_index(drop=True)
nycbkpt20=gpd.read_file(path+'nycbkpt20.geojson',driver='GeoJSON')
nycbkpt20.crs=4326
pop=pd.read_csv(path+'pop20.csv',dtype={'blockid':str,'pop20':float})
pop=pd.merge(nycbkpt20,pop,how='left',on='blockid')
pop=pop.groupby(['puma'],as_index=False).agg({'pop20':'sum'}).reset_index(drop=True)
df=pd.merge(df,pop,how='left',on='puma')
df.to_csv(path+'crash.csv',index=False)



# df=pd.read_csv(path+'crash.csv',dtype={'puma':str})
# puma=gpd.read_file(path+'puma.geojson')
# puma.crs=4326
# puma['puma']=puma[['GEOID10']].copy()
# puma=puma[['puma','geometry']].reset_index(drop=True)
# df=pd.merge(puma,df,on='puma',how='left')
# df['injrate']=df['totinj']/df['pop20']*100000
# df['killrate']=df['totinj']/df['pop20']*100000
# df.to_file(path+'crash.geojson',driver='GeoJSON')













