# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 10:29:28 2019

@author: Annie
"""
"this program takes a csv with wkt of a settlements boundaries," 
"finds the min max coords of the bounds and uses those values to" 
"parameterize a bounding box to download settlement buildings and roads?"
"and writes them to a shapefile; script prod 3 .shp outputs: bounds, bldgs, rds" 

wkt_file_name = "lagos_priority_wkt.csv"


import osmnx as ox 
import pandas as pd
import geopandas as gpd
import shapely.wkt
from shapely.geometry import shape 
import matplotlib as plt
import os 
import fiona

pd.set_option('display.max_colwidth', -1)
os.chdir('c:\\Users\\Annie\\Downloads')

'1. creating settlement boundary .shp'
set_wkt = pd. read_csv(wkt_file_name)

columnhead = ""
if 'verification/A0_Boundary' in wkt_file_name:
    columnhead = 'verification/A0_Boundary'
elif 'C2a. Settlement Boundary' in wkt_file_name:
    columnhead = 'C2a. Settlement Boundary'
elif 'section_C/C2_Boundary' in wkt_file_name:
    columnhead = 'section_C/C2_Boundary'


geometry = set_wkt[columnhead].map(shapely.wkt.loads)
set_wkt = set_wkt.drop(columnhead, axis=1)
crs = {'init': 'epsg:4326'}
gdf = gpd.GeoDataFrame(set_wkt, crs=crs, geometry=geometry)
gdf.to_file('lagos_priorities.shp')

#at some point add way to export bounds cut by settlement

'2. pulling osm bld/rd topology in .shp within settlement boundaries'

set_bounds = []
with fiona.open('Lagos_priorities.shp') as input:
    for feat in input: 
        geom = shape(feat['geometry'])
        set_bounds.append(geom)
set_bounds

for i in range(len(set_bounds)):
    if set_bounds[i] == 1:
        print(i)

def get_blds(shape,i):
    set_osm = ox.buildings.create_buildings_gdf(polygon = shape)
    set_bd = set_osm.drop(labels = 'nodes' , axis = 1)
    set_bd  = set_bd.to_file('lagosp'+str(i)+'.shp')
    return set_bd

for i in range(len(set_bounds)):
    get_blds(set_bounds[i],i)

def get_rds (shape, j):
    rds_osm = ox.core.graph_from_polygon(polygon = shape, network_type = 'drive')
    rds_osm = ox.project_graph(rds_osm)
    ox.plot_graph(set_rds)
    rds_osm = ox.save_graph_shapefile(rds_osm, filename = 'lagosp_rds'+str(j)+'.shp')
    return rds_osm

for j in range(len(set_bounds)):
    get_rds(set_bounds[j],j)

    
    

'''code im hoarding:
    "reading ona file and outputting min max coords for bbox"
ona_file_name = "lagos_test.csv"
ona_csv = pd.read_csv(ona_file_name)

columnhead = ""
if 'verification/A0_Boundary' in ona_csv:
    columnhead = 'verification/A0_Boundary'
elif 'C2a. Settlement Boundary' in ona_csv:
    columnhead = 'C2a. Settlement Boundary'
elif 'section_C/C2_Boundary' in ona_csv:
    columnhead = 'section_C/C2_Boundary'

ona_csv[columnhead]


set_bounds = ona_csv[columnhead].to_string().replace(';',' ')

set_bounds = set_bounds.split(' ')

set_bounds = [float( s.lstrip('0')) for s in set_bounds if s != '0' and s != '']

set_bounds1 = [f for f in set_bounds if len(str(f))>5 ]
set_bounds1
odd= set_bounds1[1::2]
even = set_bounds1[::2]
odd
x_high= (max(odd))
x_low = (min(odd))
 
y_high= (max(even))
y_low = (min(even))


#set_bounds = gpd.read_file('lagos_priorities.shp')
#set_bounds = set_bounds.to_crs(epsg= 3857 )
#set_bounds.plot()
#set_bounds

#sb_df = pd.DataFrame()
#sb_df = sb_df.append(set_bounds)
#sb_df.insert(0,'id',sb_df.index.astype(int))
#print(sb_df)

#set_bound = fiona.open('Lagos_priorities.shp')
#set_bound = gpd.read_file("hoima_bound1.shp")
#set_bound
#as_shape = set_bound.next()
#bound_asshape = shape(as_shape['geometry'])

#set_osm = ox.buildings.create_buildings_gdf(polygon = hoima_asshape, north = y_high, south = y_low, east = x_high, west = x_low) 

set_osm = ox.buildings.create_buildings_gdf(polygon = bound_asshape)
set_bd = set_osm.drop(labels = 'nodes' , axis = 1)
set_bd  = set_bd.to_file('lagos_test_bldgs.shp')

set_bd = gpd.read_file("lagos_test_bldgs.shp")
set_bd = set_bd.to_crs(epsg = 3587)


#set_rds = ox.core.graph_from_bbox(y_high, y_low, x_high, x_low, network_type = 'drive', retain_all = 'True')
set_rds = ox.core.graph_from_polygon(polygon = bound_asshape, network_type = 'drive')
set_rds = ox.project_graph(set_rds)
#ox.plot_graph(set_rds)
#set_rds = ox.save_graph_shapefile(set_rds, filename = 'lagos_test_ntwrk')
set_rds_gdf = ox.save_load.graph_to_gdfs(set_rds, nodes=True, edges=True, node_geometry=True, fill_edge_geometry=True)

ntwrk_edges = gpd.read_file("edges.shp")
ntwrk_edges = ntwrk_edges.to_crs(epsg = 3587)

set_bd.plot(ax = ntwrk_edges.plot())

ntwrk_edges

'''
