import pandas as pd 
df=pd.read_csv("implicit_hate_v1_stg3_posts".tsv, sep="/t")
df.to_excel("re.xlsx", index=false)
print("tsv converted")