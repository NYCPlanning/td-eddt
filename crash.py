import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import shapely
from shapely import wkt


pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/EDDT/'

# Simplify LION
lion=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2020/COVID19/STREET CLOSURE/sidewalk/input/lion/lion.shp')
lion.crs=4326
lionsp=lion[['SegmentID','PhysicalID','RB_Layer','FeatureTyp','SegmentTyp','NonPed','RW_TYPE','TrafDir','geometry']].reset_index(drop=True)
lionsp['segmentid']=pd.to_numeric(lionsp['SegmentID'])
lionsp=lionsp[pd.notna(lionsp['segmentid'])].reset_index(drop=True)
lionsp['physicalid']=pd.to_numeric(lionsp['PhysicalID'])
lionsp=lionsp[pd.notna(lionsp['physicalid'])].reset_index(drop=True)
lionsp['rblayer']=[' '.join(x.split()).upper() if pd.notna(x) else '' for x in lionsp['RB_Layer']]
lionsp=lionsp[np.isin(lionsp['rblayer'],['B','R'])].reset_index(drop=True)
lionsp['featuretype']=[' '.join(x.split()).upper() if pd.notna(x) else '' for x in lionsp['FeatureTyp']]
lionsp=lionsp[np.isin(lionsp['featuretype'],['0','6','C'])].reset_index(drop=True)
lionsp['segmenttype']=[' '.join(x.split()).upper() if pd.notna(x) else '' for x in lionsp['SegmentTyp']]
lionsp=lionsp[np.isin(lionsp['segmenttype'],['B','R','U','S'])].reset_index(drop=True)
lionsp['rwtype']=pd.to_numeric(lionsp['RW_TYPE'])
lionsp=lionsp[np.isin(lionsp['rwtype'],[1,2,3,4,9,13])].reset_index(drop=True)
lionsp['trafficdir']=[' '.join(x.split()).upper() if pd.notna(x) else '' for x in lionsp['TrafDir']]
lionsp=lionsp[np.isin(lionsp['trafficdir'],['T','W','A'])].reset_index(drop=True)
lionsp=lionsp[['segmentid','physicalid','rblayer','featuretype','segmenttype','rwtype','trafficdir','geometry']].reset_index(drop=True)
lionsp=lionsp.drop_duplicates(['segmentid'],keep='first').reset_index(drop=True)
lionsp.to_file(path+'lionsp.geojson',driver='GeoJSON')


# Crash Data
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
lionsp=gpd.read_file(path+'lionsp.geojson')
lionsp.crs=4326
lionsp=gpd.overlay(lionsp,puma,how='intersection')
lionsp=lionsp.to_crs(6539)
lionsp['mile']=lionsp['geometry'].length/5280
lionsp=lionsp.groupby(['puma'],as_index=False).agg({'mile':'sum'})
df=pd.merge(df,lionsp,how='left',on='puma')
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





# Vision Zero View Data
df=gpd.read_file('C:/Users/Y_Ma2/Desktop/allinjuries.geojson')
df.crs=4326
df['pedinj']=df['PedInj'].copy()
df['cycinj']=df['BikeInj'].copy()
df['motinj']=df['MVInj'].copy()
df['totinj']=df['Injuries'].copy()
df=df[['pedinj','cycinj','motinj','totinj','geometry']].reset_index(drop=True)
puma=gpd.read_file('C:/Users/Y_Ma2/Desktop/puma.geojson')
puma.crs=4326
puma['puma']=puma[['GEOID10']].copy()
puma=puma[['puma','geometry']].reset_index(drop=True)
df=gpd.sjoin(df,puma,how='left',op='intersects')
df=df.groupby(['puma'],as_index=False).agg({'pedinj':'sum','cycinj':'sum','motinj':'sum','totinj':'sum'}).reset_index(drop=True)
df.to_csv('C:/Users/Y_Ma2/Desktop/injury.csv',index=False)

df=gpd.read_file('C:/Users/Y_Ma2/Desktop/allfatalities.geojson')
df.crs=4326
df['pedkill']=df['PedFatal'].copy()
df['cyckill']=df['BikeFatal'].copy()
df['motkill']=df['MVFatal'].copy()
df['totkill']=df['Fatalities'].copy()
df=df[['pedkill','cyckill','motkill','totkill','geometry']].reset_index(drop=True)
puma=gpd.read_file('C:/Users/Y_Ma2/Desktop/puma.geojson')
puma.crs=4326
puma['puma']=puma[['GEOID10']].copy()
puma=puma[['puma','geometry']].reset_index(drop=True)
df=gpd.sjoin(df,puma,how='left',op='intersects')
df=df.groupby(['puma'],as_index=False).agg({'pedkill':'sum','cyckill':'sum','motkill':'sum','totkill':'sum'}).reset_index(drop=True)
df.to_csv('C:/Users/Y_Ma2/Desktop/fatality.csv',index=False)
