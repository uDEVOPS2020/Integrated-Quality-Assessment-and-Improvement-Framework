import pandas as pd
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("testFeatures.csv")

df['ranking'] = df['code']+(1/(df['respTime']+1))*100

df = df.sort_values(by=['specId','ranking'],ascending=[True,False])

df = df.drop(['testId','state','code','severity','respTime','url'], axis=1)

df['method'][df['method']=='GET'] = 0
df['method'][df['method']=='POST'] = 1
df['method'][df['method']=='PUT'] = 2
df['method'][df['method']=='DELETE'] = 3
df['method'][df['method']=='PATCH'] = 4
df['method'][df['method']=='HEAD'] = 5
df['method'][df['method']=='OPTIONS'] = 6

n = 1
for index, row in df.iterrows():
    print(str(row['ranking'])+" qid:"+str(row['specId'])+" ", end='')
    for i in range(n,row.size-1):
        print(str(i-n+1)+":"+str(row[i])+" ", end='')
    print()

# df = df.reset_index()
# df.to_csv("info_vs.csv", index=True)