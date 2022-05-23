#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 21 18:04:16 2022

@author: jiahuiwu
"""

import folium
import geopandas as gpd
from folium import plugins
from shapely.geometry import Polygon, mapping
import branca.colormap as cm
import pandas as pd


path = gpd.datasets.get_path('nybb')
NY = gpd.read_file(path)
NY.head()
NY.plot(figsize=(6, 6))
NY = NY.to_crs(epsg=4326)
NY.head()
NY.to_file("my_file.csv", driver="GeoJSON")
zone = gpd.read_file("NYC Taxi Zones.geojson")
zone = zone.to_crs(epsg=4326)
all_polygon = zone['geometry']
zone_ID_col = list(zone['location_id'])


def generateBasemap():
    map1 = folium.Map(location=[40.7, -73.98], zoom_start=11, max_bounds=True, max_zoom = 13, min_zoom = 10, tiles='cartodbpositron')
    
    for _,r in NY.iterrows():
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                               style_function=lambda x: {'fillColor': "#00000000",'color':"#333333",'weight':2.5})
        geo_j.add_to(map1)
                          
    
    
    for _, r in zone.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                               style_function=lambda x: {'color':'#333333','weight':1, 'fillColor': "#00000000"})
        folium.Popup(r['location_id'] + " " + r['zone']+' (' + r['borough']+')').add_to(geo_j)
        geo_j.add_to(map1)
    
    return(map1)


basemap = generateBasemap()
basemap.save("basemap.html")







df_07 = pd.read_csv("df_07cleaned.csv")
df_07['PUlocationID'] = df_07["PUlocationID"].apply(lambda x: int(x))



def set_color(value):
    cmap = cm.step.YlOrRd_09.to_linear().scale(1,57)
    return(pd.Series(value).map(cmap)[0])




def generate_feature(df):
    
    feature_list = []
    for _,point in df.iterrows():
        subzone = zone.loc[zone["location_id"] == str(point['PUlocationID']),]
        geo = list(subzone['geometry'])[0].simplify(0.001)
                
        fillcolor = set_color(point["count"])
              
        boundary = mapping(geo)['coordinates']
        coor = []
        if len(boundary)>1:
            for poly in boundary:
                coor = coor + [[i[0], i[1]] for i in poly[0]]  
        else:
            coor =  [[i[0], i[1]] for i in boundary[0]]
    
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coor],
            },
            "properties": {
                "time": str(point["pickup_timeslot"]),
                'style': {'color' : "gray", "fillColor" : fillcolor, "fillOpacity": 1, 'weight':0.7},
                    # 'iconstyle':{
                    #     'fillColor': fillcolor,
                    #     'fillOpacity': 0.8,
                    #     'stroke': 'true',
                    # }
                'popup':  str(point['PUlocationID']) + " " + list(subzone["zone"])[0] + ' (' + list(subzone['borough'])[0]+ ') :' + str(point["count"])
            },
        }
        feature_list.append(feature)
                
    return feature_list

feature_0702 = generate_feature(df_07.loc[df_07["pickup_timeslot"].apply(lambda x: x[:10])=="2019-07-02",])
feature_test = generate_feature(df_07.iloc[:10,])


def drawMap(feature_list, name):
    map1 = generateBasemap()
    plugins.TimestampedGeoJson(feature_list,
                          period = 'PT1H',
                          duration = 'PT1H',
                          transition_time = 1200,
                          auto_play = True).add_to(map1)

    cmap = cm.step.YlOrRd_09.to_linear().scale(0,60)
    _ = cmap.add_to(map1)
    cmap.caption = "count of pick_up"

    map1.save(name + ".html")
    
drawMap(feature_0702, "07_02_2019")

