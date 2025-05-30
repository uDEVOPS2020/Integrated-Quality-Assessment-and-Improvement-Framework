import pandas as pd

df = pd.read_csv("score.txt", header=None, sep="\t")
# print(df[df.shape[1]-1])
df = df.sort_values(by=[0,df.shape[1]-1],ascending=[True,False])

df.to_csv("ordered.csv", index=True)