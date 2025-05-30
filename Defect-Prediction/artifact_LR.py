import sklearn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import sys

import stability as st

df =  pd.read_csv(sys.argv[1])

N_trees = 30

labels = np.array(df['bug'])
df= df.drop('bug', axis = 1)
df= df.drop('_id', axis = 1)
df= df.drop('__', axis = 1) #This feature has the same values of the bug column, for this reason it is removed
df= df.drop('Unnamed: 0', axis = 1)
features = np.array(df)

# print(df)
# print(labels)

df_f = pd.DataFrame(columns = df.columns)

for i in range(0,N_trees):
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.75, shuffle = True)
    model = LogisticRegression()
    # fit the model
    model.fit(train_features, train_labels)
    # get importance
    importance = model.coef_[0]
    df_f = df_f.append(pd. Series(importance, index = df. columns),ignore_index=True)

#print(df_f)

print("Features importance is:")
print(df_f.mean().sort_values())

df_f[df_f > 0] = 1
df_f[df_f < 0] = 0

stab1=st.getStability(df_f.to_numpy())

print("Features stability is: "+str(stab1))

