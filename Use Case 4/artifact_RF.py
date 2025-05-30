import sklearn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import stability as st
import sys


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

train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.75)

# We set a max depth to avoid that all the features are selected for each tree
rf = RandomForestClassifier(n_estimators = N_trees, max_depth=4)
rf.fit(train_features, train_labels)

df_f = pd.DataFrame(columns = df.columns)

for i in range(0,N_trees):
    temp = []
    for name, importance in zip(df.columns, rf.estimators_[i].feature_importances_):
        temp.append(importance)
    df_f = df_f.append(pd. Series(temp, index = df. columns),ignore_index=True)

print("Features importance is:")
print(df_f.mean().sort_values())

df_f[df_f > 0] = 1

print(df_f)

stab1=st.getStability(df_f.to_numpy())

print("Features stability is: "+str(stab1))
