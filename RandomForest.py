#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 22 15:08:10 2022

@author: jiahuiwu
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

import matplotlib.pyplot as plt
import plotly.express as px
import plotly

df_07_avg = pd.read_csv("df_07_avg.csv")
df_08_avg = pd.read_csv("df_08_avg.csv")


regressor = RandomForestRegressor(n_estimators = 100, random_state = 0)

regressor.fit(df_07_avg.iloc[:,:-1], df_07_avg["count"])

pred = regressor.predict(df_08_avg.iloc[:,:-1])


df = pd.DataFrame()
df["true"] = df_08_avg["count"]
df["predicted"] = pred 


fig = px.scatter(df, x = "true", y = "predicted", title='true value vs predcted value')
plotly.offline.plot(fig, filename='scatter.html')


plt.scatter(df_08_avg["count"], pred, s=1)
plt.plot([0, 40], [0, 40], 'k-', color = 'r')
plt.xlabel("predict")
plt.ylabel("true")


df_08_avg['pred'] = pred 

df_08_avg.to_csv("df_08_avg_pred.csv",index=False)



            
