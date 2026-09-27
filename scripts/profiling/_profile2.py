import pandas as pd, json
r=lambda f: pd.read_csv(f,dtype={"Invoice":str,"StockCode":str,"Description":str,"Country":str},parse_dates=["InvoiceDate"])
a=r("data/raw/_sheet_Year_2009_2010.csv"); b=r("data/raw/_sheet_Year_2010_2011.csv")
cut=pd.Timestamp("2010-12-01")
aO=a[a.InvoiceDate>=cut]; bO=b[b.InvoiceDate<=a.InvoiceDate.max()]
o={}
o["overlap_rows_A,B"]=[len(aO),len(bO)]
o["overlap_invoice_sets_equal"]=set(aO.Invoice)==set(bO.Invoice)
key=list(a.columns)
ca=aO.fillna({"Customer ID":-1,"Description":""}).value_counts(key); cb=bO.fillna({"Customer ID":-1,"Description":""}).value_counts(key)
o["overlap_multiset_equal"]=bool(ca.sort_index().equals(cb.sort_index()))
o["within_sheet_dups_A_B"]=[int(a.duplicated().sum()),int(b.duplicated().sum())]
d=pd.concat([a[a.InvoiceDate<cut],b]); o["rows_after_overlap_rule"]=len(d); o["within_dups_after"]=int(d.duplicated().sum())
sc=d.StockCode.astype(str)
sp=~sc.str.match(r"^\d{5}")
g=d[sp].groupby(sc[sp]).agg(n=("Invoice","size"),desc=("Description",lambda s:s.dropna().mode().iloc[0] if s.notna().any() else ""),with_cust=("Customer ID",lambda s:int(s.notna().sum())))
o["special_codes"]=g.sort_values("n",ascending=False).head(30).reset_index().values.tolist()
o["special_codes_count"]=len(g)
o["5digit_regex_all_letters_suffix_examples"]=sc[sc.str.match(r"^\d{5}[A-Za-z]+$")].head(5).tolist()
dd=d.drop_duplicates(); c=dd[dd.Invoice.str.startswith("C")&dd["Customer ID"].notna()]
o["cancel_rows_with_customer"]=len(c); o["cancel_value_with_customer"]=round(float((c.Quantity*c.Price).sum()),2)
pos=dd[~dd.Invoice.str[0].str.isalpha()&dd["Customer ID"].notna()&(dd.Price>0)]
o["positive_value_with_customer"]=round(float((pos.Quantity*pos.Price).sum()),2)
first=pos.groupby("Customer ID").InvoiceDate.min()
cc=c.join(first.rename("first_buy"),on="Customer ID")
o["cancel_rows_before_first_purchase_or_no_purchase"]=int((cc.first_buy.isna()|(cc.InvoiceDate<cc.first_buy)).sum())
print(json.dumps(o,indent=1,default=str))
json.dump(o,open("data/raw/_profile2.json","w"),indent=1,default=str)
