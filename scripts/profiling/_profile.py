import pandas as pd, json, re
r=lambda f: pd.read_csv(f,dtype={"Invoice":str,"StockCode":str,"Description":str,"Country":str},parse_dates=["InvoiceDate"])
a=r("data/raw/_sheet_Year_2009_2010.csv"); b=r("data/raw/_sheet_Year_2010_2011.csv")
out={}
out["sheet_a"]=[len(a),str(a.InvoiceDate.min()),str(a.InvoiceDate.max())]
out["sheet_b"]=[len(b),str(b.InvoiceDate.min()),str(b.InvoiceDate.max())]
ov_dates=b.InvoiceDate<=a.InvoiceDate.max(); out["sheet_b_rows_in_a_period"]=int(ov_dates.sum())
ov=pd.merge(a[a.InvoiceDate>=b.InvoiceDate.min()],b[b.InvoiceDate<=a.InvoiceDate.max()],how="inner",on=list(a.columns))
out["identical_rows_in_overlap_period"]=len(ov)
out["overlap_invoices_shared"]=len(set(a.Invoice[a.InvoiceDate>=b.InvoiceDate.min()])&set(b.Invoice))
df=pd.concat([a,b],ignore_index=True)
out["rows_concat"]=len(df); out["exact_dup_rows_concat"]=int(df.duplicated().sum())
d=df.drop_duplicates()
out["rows_dedup"]=len(d)
inv=d.Invoice.astype(str)
out["date_range"]=[str(d.InvoiceDate.min()),str(d.InvoiceDate.max())]
out["missing_customer_rows_pct"]=round(d["Customer ID"].isna().mean()*100,2)
lv=d.Quantity*d.Price
out["missing_customer_revenue_pct_of_positive"]=round(lv[(lv>0)&d["Customer ID"].isna()].sum()/lv[lv>0].sum()*100,2)
out["missing_description_rows"]=int(d.Description.isna().sum())
out["invoice_prefixes"]=inv.str.extract(r"^([A-Za-z]*)")[0].value_counts().to_dict()
isC=inv.str.startswith("C")
out["C_rows"]=int(isC.sum()); out["C_rows_qty_pos"]=int((isC&(d.Quantity>0)).sum())
out["qty_neg_not_C"]=int(((d.Quantity<0)&~isC).sum())
out["qty_neg_not_C_with_customer"]=int(((d.Quantity<0)&~isC&d["Customer ID"].notna()).sum())
out["qty_neg_not_C_price_zero"]=int(((d.Quantity<0)&~isC&(d.Price==0)).sum())
out["qty_zero"]=int((d.Quantity==0).sum())
out["price_zero"]=int((d.Price==0).sum()); out["price_neg"]=int((d.Price<0).sum())
out["price_neg_invoice_prefix"]=inv[d.Price<0].str[0].value_counts().to_dict()
out["A_invoice_desc"]=d.loc[inv.str.startswith("A"),"Description"].value_counts().head(3).to_dict()
sc=d.StockCode.astype(str)
special=~sc.str.match(r"^\d{5}[A-Za-z]{0,2}$")
out["special_stockcodes_top"]=sc[special].value_counts().head(25).to_dict()
out["special_stockcode_rows"]=int(special.sum())
out["customer_id_is_integer"]=bool((d["Customer ID"].dropna()%1==0).all())
out["unique_customers"]=int(d["Customer ID"].nunique()); out["unique_invoices"]=int(inv.nunique()); out["countries"]=int(d.Country.nunique())
out["top_countries"]=d.Country.value_counts().head(5).to_dict()
out["multi_customer_invoices"]=int(d.dropna(subset=["Customer ID"]).groupby("Invoice")["Customer ID"].nunique().gt(1).sum())
out["multi_date_invoices"]=int(d.groupby("Invoice")["InvoiceDate"].nunique().gt(1).sum())
out["line_value_quantiles"]=lv.quantile([0.001,0.01,0.5,0.99,0.999]).round(2).to_dict()
out["max_abs_qty_rows"]=d.loc[d.Quantity.abs().nlargest(4).index,["Invoice","StockCode","Quantity","Price","Customer ID"]].astype(str).values.tolist()
m=d.set_index("InvoiceDate").resample("MS").Invoice.nunique(); out["invoices_per_month"]={str(k.date()):int(v) for k,v in m.items()}
# valid orders & snapshot prevalence
v=d[d["Customer ID"].notna()&~isC&(d.Quantity>0)&(d.Price>0)&~special]
orders=v.assign(val=v.Quantity*v.Price).groupby(["Invoice","Customer ID"],as_index=False).agg(ts=("InvoiceDate","min"),val=("val","sum"))
out["valid_orders"]=len(orders)
prev={}
for T in pd.date_range("2010-06-01","2011-09-01",freq="MS"):
    h=orders[(orders.ts<T)&(orders.ts>=T-pd.Timedelta(days=180))]
    f=set(orders[(orders.ts>=T)&(orders.ts<T+pd.Timedelta(days=90))]["Customer ID"])
    el=h["Customer ID"].unique(); prev[str(T.date())]=[len(el),round(sum(c in f for c in el)/len(el),3)]
out["snapshot_eligible_prevalence"]=prev
json.dump(out,open("data/raw/_profile.json","w"),indent=1,default=str)
print(json.dumps(out,indent=1,default=str))
