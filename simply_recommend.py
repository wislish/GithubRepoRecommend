# -*- coding: utf-8 -*-
import pandas as pd
from scipy.stats import pearsonr


df = pd.read_csv("starred_repos_level_3.csv",index_col=0)
sim_score = {} 

# choose the pearsor as the similar measure way.
for i in range(df.shape[0]):
    ss = pearsonr(df.iloc[0,:], df.iloc[i,:])
    sim_score.update({i: ss[0]})
    
sf = pd.Series(sim_score).to_frame('similarity')
most_similar = sf.sort_values('similarity',ascending=False).iloc[1].name

print(df.index[most_similar])

#df.iloc[most_similar,:]
print(df.iloc[most_similar,:][df.iloc[most_similar,:]==1])