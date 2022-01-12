import pandas as pd
import geopandas as gpd
import numpy as np

pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/EDDT/'

nycbkpt20=gpd.read_file(path+'nycbkpt20.geojson')
nycbkpt20.crs=4326

pop=pd.read_csv(path+'pop20.csv',dtype={'blockid':str,'pop20':float})

park=gpd.read_file(path+'Walk-to-a-Park Service area/geo_export_dec3519e-1bf8-407b-867e-4cf03b9b76b4.shp')
park.crs=4326
park['park']=1
park=park[['park','geometry']].reset_index(drop=True)

bkpark=gpd.sjoin(nycbkpt20,park,how='left',op='intersects')
bkpark=bkpark[['blockid','puma','park','geometry']].reset_index(drop=True)
k=pd.merge(bkpark,pop,how='inner',on='blockid')
k['poppark']=k['pop20']*k['park']
k=k.groupby('puma',as_index=False).agg({'pop20':'sum','poppark':'sum'}).reset_index(drop=True)
k['pct']=k['poppark']/k['pop20']
k.to_csv(path+'park.csv',index=False)
