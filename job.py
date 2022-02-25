import pandas as pd


pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/EDDT/'


hd=pd.DataFrame(columns=['orgct','destbk','time'])
hd.to_csv(path+'travelshed.csv',mode='w',index=False,header=True)
rd=pd.read_csv('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/nyctract/resbk3.csv',dtype=float,converters={'blockid':str},chunksize=10000)
for ck in rd:
    tp=pd.melt(ck,id_vars=['blockid'])
    tp=tp[tp['value']<=30].reset_index(drop=True)
    tp['orgct']=[x.replace('RES','') for x in tp['variable']]
    tp['destbk']=tp['blockid'].copy()
    tp['time']=tp['value'].copy()
    tp=tp[['orgct','destbk','time']].reset_index(drop=True)
    tp.to_csv(path+'travelshed.csv',mode='a',index=False,header=False)


wac=pd.DataFrame()
for i in ['ct','nj','ny','pa']:
    tp=pd.read_csv('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/lehd/'+str(i)+'_wac_S000_JT00_2019.csv',dtype=str)
    tp=tp[['w_geocode','C000']]
    wac=pd.concat([wac,tp],axis=0)
wac.columns=['destbk','wac']
wac['wac']=pd.to_numeric(wac['wac'])


df=pd.read_csv(path+'travelshed.csv',dtype=str)
df=pd.merge(df,wac,on='destbk',how='left')
df=df.fillna(0)
df=df.groupby(['orgct'],as_index=False).agg({'wac':'sum'}).reset_index(drop=True)
cttopuma=pd.read_csv(path+'cttopuma.csv',dtype=str)
cttopuma.columns=['orgct','puma']
df=pd.merge(df,cttopuma,how='left',on='orgct')
pop=pd.read_csv(path+'pop1519.csv',dtype={'tractid':str,'pop1519':float})
pop.columns=['orgct','pop']
df=pd.merge(df,pop,how='left',on='orgct')
df['wacpop']=df['wac']*df['pop']
df=df.groupby(['puma'],as_index=False).agg({'wacpop':'sum','pop':'sum'}).reset_index(drop=True)
df['wac']=df['wacpop']/df['pop']
df=df[['puma','wac','pop']].reset_index(drop=True)
df.to_csv(path+'job.csv',index=False)




