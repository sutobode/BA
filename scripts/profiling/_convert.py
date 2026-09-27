import pandas as pd, time, json
t=time.time()
x=pd.read_excel(r"data/raw/online_retail_II.xlsx",sheet_name=None,dtype={"Invoice":str,"StockCode":str},engine="openpyxl")
meta={}
for k,v in x.items():
    meta[k]={"shape":list(v.shape),"columns":list(v.columns),"dtypes":{c:str(d) for c,d in v.dtypes.items()},"min":str(v.iloc[:,4].min()) if v.shape[1]>4 else None}
    v.to_csv(f"data/raw/_sheet_{k.replace(' ','_').replace('-','_')}.csv",index=False)
json.dump(meta,open("data/raw/_sheets_meta.json","w"),indent=1)
print("done",round(time.time()-t,1),"s",meta)
