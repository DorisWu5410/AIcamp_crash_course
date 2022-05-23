#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 20 13:47:58 2022

@author: jiahuiwu
"""

import pandas as pd

from datetime import datetime as dt
import seaborn as sns


df_07 = pd.read_csv("df_count_07.csv")
df_08 = pd.read_csv("df_count_08.csv")



#Add day of week
def getDayOfWeek(date):
    return dt.fromisoformat(date).weekday() 

df_07["dayOfWeek"] = df_07["pickup_timeslot"].apply(getDayOfWeek)

df_08["dayOfWeek"] = df_08["pickup_timeslot"].apply(getDayOfWeek)



# add latitude and longitude of each zone

import geopandas as gpd

zone = gpd.read_file("NYC Taxi Zones.geojson")
# zone = zone.to_crs(epsg=4326)
all_polygon = zone['geometry']
zone_ID_col = [int(eval(i)) for i in list(zone['location_id'])]


def getZoneCen(zoneID):
    try:
        idx = zone_ID_col.index(zoneID)
        location = all_polygon[idx].centroid.wkt
        location = location.strip('POINT (')
        location = location.strip(')')
        location = location.split(' ')
        location = [float("%.4f" % float(s)) for s in location]
        return(location)
    except:
        return 0
    
    
def add_lat_long(df):
    lat_long = list(df["PUlocationID"].apply(getZoneCen))
    df = df.loc[[i for i in range(len(lat_long)) if lat_long[i] != 0],]
    lat_long = list(filter(lambda num: num != 0, lat_long))
    df["lat"] = [i[0] for i in lat_long]
    df["long"] = [i[1] for i in lat_long]
    return df


df_07 = add_lat_long(df_07)
df_08 = add_lat_long(df_08)

df_07 = df_07.drop(columns = "Unnamed: 0")
df_08 = df_08.drop(columns = "Unnamed: 0")

df_07.to_csv("df_07cleaned.csv",index=False)
df_08.to_csv("df_08cleaned.csv",index=False)

sns.histplot(df_07["count"],binwidth=3)



# calculate average at each time in each weekdays

df_07["PU_time"] = df_07["pickup_timeslot"].apply(lambda x: x[11:])
df_08["PU_time"] = df_08["pickup_timeslot"].apply(lambda x: x[11:])


df_07_avg = df_07.groupby(["PU_time", "dayOfWeek", "lat", "long", "PUlocationID"]).mean()
df_07_avg.reset_index(inplace = True)

df_08_avg = df_08.groupby(["PU_time", "dayOfWeek", "lat", "long", "PUlocationID"]).mean()
df_08_avg.reset_index(inplace = True)

df_07_avg.to_csv("df_07_avg.csv",index=False)
df_08_avg.to_csv("df_08_avg.csv",index=False)
