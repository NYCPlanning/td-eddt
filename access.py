import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import shapely
from shapely import wkt


pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/EDDT/'
doserver='http://159.65.64.166:8801/'


# Create 2020 Block
nycbk20=gpd.read_file(path+'tl_2021_36_tabblock20/tl_2021_36_tabblock20.shp')
nycbk20.crs=4269
nycbk20['blockid']=nycbk20['GEOID20'].copy()
nycbk20['county']=[str(x)[0:5] for x in nycbk20['blockid']]
nycbk20=nycbk20.loc[nycbk20['county'].isin(['36005','36047','36061','36081','36085']),['blockid','geometry']].reset_index(drop=True)
nycbk20=nycbk20.to_crs(4326)
nycbk20.to_file(path+'nycbk20.geojson',driver='GeoJSON')

# Create 2020 Block Point
nycbkpt20=gpd.read_file(path+'tl_2021_36_tabblock20/tl_2021_36_tabblock20.shp')
nycbkpt20.crs=4269
nycbkpt20['blockid']=nycbkpt20['GEOID20'].copy()
nycbkpt20['county']=[str(x)[0:5] for x in nycbkpt20['blockid']]
nycbkpt20['lat']=pd.to_numeric(nycbkpt20['INTPTLAT20'])
nycbkpt20['long']=pd.to_numeric(nycbkpt20['INTPTLON20'])
nycbkpt20=nycbkpt20.loc[nycbkpt20['county'].isin(['36005','36047','36061','36081','36085']),['blockid','lat','long']].reset_index(drop=True)
nycbkpt20=gpd.GeoDataFrame(nycbkpt20,geometry=[shapely.geometry.Point(xy) for xy in zip(pd.to_numeric(nycbkpt20['long']), pd.to_numeric(nycbkpt20['lat']))],crs=4326)
puma=gpd.read_file(path+'puma.geojson')
puma.crs=4326
puma['puma']=puma[['GEOID10']].copy()
puma=puma[['puma','geometry']].reset_index(drop=True)
nycbkpt20=gpd.sjoin(nycbkpt20,puma,how='left',op='intersects')
nycbkpt20=nycbkpt20[['blockid','puma','geometry']].reset_index(drop=True)
nycbkpt20.to_file(path+'nycbkpt20.geojson',driver='GeoJSON')


# Access to ADA Subway Stations
subwayada=gpd.read_file(path+'subway.geojson')
subwayada.crs=4326
subwayada=subwayada[subwayada['ADA']!=0].reset_index(drop=True)
# Nearest intersection
node=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/location/node.shp')
node.crs=4326
node=node['geometry']
node=shapely.geometry.MultiPoint(node)
nr=[shapely.ops.nearest_points(x,node)[1] for x in subwayada['geometry']]
for i in subwayada.index:
    subwayada.loc[i,'intlat']=nr[i].y
    subwayada.loc[i,'intlong']=nr[i].x
# Distance from site to nearest intersection
frompt=subwayada.copy()
frompt=gpd.GeoDataFrame(frompt,geometry=[shapely.geometry.Point(xy) for xy in zip(pd.to_numeric(frompt['GTFS_Longitude']), pd.to_numeric(frompt['GTFS_Latitude']))],crs=4326)
frompt=frompt.to_crs(6539)
frompt=frompt['geometry']
topt=subwayada.copy()
topt=gpd.GeoDataFrame(topt,geometry=[shapely.geometry.Point(xy) for xy in zip(pd.to_numeric(topt['intlong']), pd.to_numeric(topt['intlat']))],crs=4326)
topt=topt.to_crs(6539)
topt=topt['geometry']
dist=frompt.distance(topt)
subwayada['distance']=dist
# Walk time from site to nearest intersection
for i in subwayada.index:
    url=doserver+'otp/routers/default/plan?fromPlace='
    url+=str(subwayada.loc[i,'GTFS_Latitude'])+','+str(subwayada.loc[i,'GTFS_Longitude'])
    url+='&toPlace='+str(subwayada.loc[i,'intlat'])+','+str(subwayada.loc[i,'intlong'])+'&mode=WALK'
    headers={'Accept':'application/json'}
    req=requests.get(url=url,headers=headers)
    js=req.json()
    if list(js.keys())[1]=='error':
        subwayada.loc[i,'walktime']=np.nan
    else:
        subwayada.loc[i,'walktime']=js['plan']['itineraries'][0]['legs'][0]['duration']
subwayada=gpd.GeoDataFrame(subwayada,geometry=[shapely.geometry.Point(x,y) for x,y in zip(subwayada['intlong'],subwayada['intlat'])],crs=4326)
subwayada.to_file(path+'subwayada.geojson',driver='GeoJSON')
# Get OTP Walksheds
subwayada=gpd.read_file(path+'subwayada.geojson')
subwayada.crs=4326
subwayada['qtml']=''
for i in subwayada.index:
    try:
        url=doserver+'otp/routers/default/isochrone?batch=true&mode=WALK'
        url+='&fromPlace='+str(subwayada.loc[i,'geometry'].y)+','+str(subwayada.loc[i,'geometry'].x)
        url+='&cutoffSec=300'
        headers={'Accept':'application/json'}
        req=requests.get(url=url,headers=headers)
        js=req.json()
        iso=gpd.GeoDataFrame.from_features(js,crs=4326)
        subwayada.loc[i,'qtml']=iso.loc[0,'geometry'].wkt
    except:
        subwayada.loc[i,'qtml']=''
        print(str(subwayada.loc[i,'Station_ID'])+' no geometry!')
subwayada=subwayada[subwayada['qtml']!=''].reset_index(drop=True)
subwayada=gpd.GeoDataFrame(subwayada,geometry=subwayada['qtml'].map(wkt.loads),crs=4326)
subwayada=subwayada.drop('qtml',axis=1)
subwayada.to_file(path+'subwayadaotp.geojson',driver='GeoJSON')
# Summarize by PUMA
subwayadaotp=gpd.read_file(path+'subwayadaotp.geojson')
subwayadaotp.crs=4326
nycbk20=gpd.read_file(path+'nycbk20.geojson')
nycbk20.crs=4326
nycbkpt20=gpd.read_file(path+'nycbkpt20.geojson')
nycbkpt20.crs=4326
pop=pd.read_csv(path+'pop20.csv',dtype={'blockid':str,'pop20':float})
pumasubwayada=gpd.sjoin(nycbk20,subwayadaotp,how='inner',op='intersects')
pumasubwayada['subwayada']=1
pumasubwayada=pumasubwayada[['blockid','subwayada']].drop_duplicates(keep='first').reset_index(drop=True)
pumasubwayada=pd.merge(nycbkpt20,pumasubwayada,how='left',on='blockid')
pumasubwayada['subwayada']=np.where(pd.isna(pumasubwayada['subwayada']),0,pumasubwayada['subwayada'])
pumasubwayada=pd.merge(pumasubwayada,pop,how='left',on='blockid')
pumasubwayada=pumasubwayada.groupby(['puma','subwayada'],as_index=False).agg({'pop20':'sum'}).reset_index(drop=True)
pumasubwayada=pumasubwayada.pivot(index='puma',columns='subwayada',values='pop20').reset_index(drop=False)
pumasubwayada.columns=['puma','nonada','ada']
pumasubwayada=pumasubwayada.fillna(0)
pumasubwayada['total']=pumasubwayada['nonada']+pumasubwayada['ada']
pumasubwayada['pct']=pumasubwayada['ada']/pumasubwayada['total']
pumasubwayada.to_csv(path+'pumasubwayada.csv',index=False)


# Access to Subway Stations and SBS Stops
subway=gpd.read_file(path+'subway.geojson')
subway.crs=4326
subway['type']='subway'
subway['lat']=subway['GTFS_Latitude']
subway['long']=subway['GTFS_Longitude']
subway=subway[['type','lat','long','geometry']].reset_index(drop=True)
sbs=gpd.read_file(path+'busstops.geojson')
sbs.crs=4326
sbs=sbs[sbs['routes'].str.contains('-SBS')].reset_index(drop=True)
sbs['type']='sbs'
sbs['lat']=sbs['geometry'].y
sbs['long']=sbs['geometry'].x
sbs=sbs[['type','lat','long','geometry']].reset_index(drop=True)
subwaysbs=pd.concat([subway,sbs],axis=0,ignore_index=True)
# Nearest intersection
node=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/location/node.shp')
node.crs=4326
node=node['geometry']
node=shapely.geometry.MultiPoint(node)
nr=[shapely.ops.nearest_points(x,node)[1] for x in subwaysbs['geometry']]
for i in subwaysbs.index:
    subwaysbs.loc[i,'intlat']=nr[i].y
    subwaysbs.loc[i,'intlong']=nr[i].x
# Distance from site to nearest intersection
frompt=subwaysbs.copy()
frompt=gpd.GeoDataFrame(frompt,geometry=[shapely.geometry.Point(xy) for xy in zip(pd.to_numeric(frompt['long']), pd.to_numeric(frompt['lat']))],crs=4326)
frompt=frompt.to_crs(6539)
frompt=frompt['geometry']
topt=subwaysbs.copy()
topt=gpd.GeoDataFrame(topt,geometry=[shapely.geometry.Point(xy) for xy in zip(pd.to_numeric(topt['intlong']), pd.to_numeric(topt['intlat']))],crs=4326)
topt=topt.to_crs(6539)
topt=topt['geometry']
dist=frompt.distance(topt)
subwaysbs['distance']=dist
# Walk time from site to nearest intersection
for i in subwaysbs.index:
    url=doserver+'otp/routers/default/plan?fromPlace='
    url+=str(subwaysbs.loc[i,'lat'])+','+str(subwaysbs.loc[i,'long'])
    url+='&toPlace='+str(subwaysbs.loc[i,'intlat'])+','+str(subwaysbs.loc[i,'intlong'])+'&mode=WALK'
    headers={'Accept':'application/json'}
    req=requests.get(url=url,headers=headers)
    js=req.json()
    if list(js.keys())[1]=='error':
        subwaysbs.loc[i,'walktime']=np.nan
    else:
        subwaysbs.loc[i,'walktime']=js['plan']['itineraries'][0]['legs'][0]['duration']
subwaysbs=gpd.GeoDataFrame(subwaysbs,geometry=[shapely.geometry.Point(x,y) for x,y in zip(subwaysbs['intlong'],subwaysbs['intlat'])],crs=4326)
subwaysbs.to_file(path+'subwaysbs.geojson',driver='GeoJSON')
# Get OTP Walksheds
subwaysbs=gpd.read_file(path+'subwaysbs.geojson')
subwaysbs.crs=4326
subwaysbs['qtml']=''
for i in subwaysbs.index:
    try:
        url=doserver+'otp/routers/default/isochrone?batch=true&mode=WALK'
        url+='&fromPlace='+str(subwaysbs.loc[i,'geometry'].y)+','+str(subwaysbs.loc[i,'geometry'].x)
        url+='&cutoffSec=300'
        headers={'Accept':'application/json'}
        req=requests.get(url=url,headers=headers)
        js=req.json()
        iso=gpd.GeoDataFrame.from_features(js,crs=4326)
        subwaysbs.loc[i,'qtml']=iso.loc[0,'geometry'].wkt
    except:
        subwaysbs.loc[i,'qtml']=''
        print(str(i)+' no geometry!')
subwaysbs=subwaysbs[subwaysbs['qtml']!=''].reset_index(drop=True)
subwaysbs=gpd.GeoDataFrame(subwaysbs,geometry=subwaysbs['qtml'].map(wkt.loads),crs=4326)
subwaysbs=subwaysbs.drop('qtml',axis=1)
subwaysbs.to_file(path+'subwaysbsotp.geojson',driver='GeoJSON')
# Summarize by PUMA
subwaysbsotp=gpd.read_file(path+'subwaysbsotp.geojson')
subwaysbsotp.crs=4326
nycbk20=gpd.read_file(path+'nycbk20.geojson')
nycbk20.crs=4326
nycbkpt20=gpd.read_file(path+'nycbkpt20.geojson')
nycbkpt20.crs=4326
pop=pd.read_csv(path+'pop20.csv',dtype={'blockid':str,'pop20':float})
pumasubwaysbs=gpd.sjoin(nycbk20,subwaysbsotp,how='inner',op='intersects')
pumasubwaysbs['subwaysbs']=1
pumasubwaysbs=pumasubwaysbs[['blockid','subwaysbs']].drop_duplicates(keep='first').reset_index(drop=True)
pumasubwaysbs=pd.merge(nycbkpt20,pumasubwaysbs,how='left',on='blockid')
pumasubwaysbs['subwaysbs']=np.where(pd.isna(pumasubwaysbs['subwaysbs']),0,pumasubwaysbs['subwaysbs'])
pumasubwaysbs=pd.merge(pumasubwaysbs,pop,how='left',on='blockid')
pumasubwaysbs=pumasubwaysbs.groupby(['puma','subwaysbs'],as_index=False).agg({'pop20':'sum'}).reset_index(drop=True)
pumasubwaysbs=pumasubwaysbs.pivot(index='puma',columns='subwaysbs',values='pop20').reset_index(drop=False)
pumasubwaysbs.columns=['puma','nonsubwaysbs','subwaysbs']
pumasubwaysbs=pumasubwaysbs.fillna(0)
pumasubwaysbs['total']=pumasubwaysbs['nonsubwaysbs']+pumasubwaysbs['subwaysbs']
pumasubwaysbs['pct']=pumasubwaysbs['subwaysbs']/pumasubwaysbs['total']
pumasubwaysbs.to_csv(path+'pumasubwaysbs.csv',index=False)






