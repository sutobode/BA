import pandas as pd, json, numpy as np
x=pd.read_excel("data/raw/online_retail_II.xlsx",sheet_name=None,dtype={"Invoice":str,"StockCode":str})
a,b=x["Year 2009-2010"],x["Year 2010-2011"]
d=pd.concat([a[a.InvoiceDate<"2010-12-01"],b[b.InvoiceDate>="2010-12-01"]]).drop_duplicates()
non=["POST","DOT","C2","C3","M","m","D","S","BANK CHARGES","AMAZONFEE","CRUK","B","GIFT"]
sc=d.StockCode.astype(str)
np_=sc.isin(non)|sc.str.startswith(("ADJUST","TEST","gift_"))
v=d[d["Customer ID"].notna()&~d.Invoice.str[0].str.isalpha()&(d.Quantity>0)&(d.Price>0)&~np_]
o=v.assign(val=v.Quantity*v.Price).groupby(["Invoice","Customer ID"],as_index=False).agg(ts=("InvoiceDate","min"),val=("val","sum"))
tr=o[(o.ts>="2009-12-03")&(o.ts<"2011-01-01")]
aov=tr.groupby("Customer ID").val.mean()
out={"orders_train_period":len(tr),"order_value_q":tr.val.quantile([.1,.25,.5,.75,.9,.99]).round(2).to_dict(),
     "customer_aov_q":aov.quantile([.1,.25,.5,.75,.9,.99]).round(2).to_dict(),"customer_aov_mean":round(aov.mean(),2),
     "top1pct_customers_share_of_value":round(tr.groupby("Customer ID").val.sum().sort_values(ascending=False).pipe(lambda s:s.iloc[:max(1,len(s)//100)].sum()/s.sum()),3)}
json.dump(out,open("scripts/profiling/_value_stats.json","w"),indent=1,default=str); print(out)
