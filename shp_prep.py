# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 10:29:28 2019

@author: Annie
"""
"this program takes a csv with wkt of a settlements boundaries," 
"finds the min max coords of the bounds and uses those values to" 
"parameterize a bounding box to download settlement buildings and roads?"
"and writes them to a shapefile; script prod 3 .shp outputs: bounds, bldgs, rds" 

ona_file_name = "lagos_test.csv"
wkt_file_name = "lagos_test_wkt.csv"


import osmnx as ox 
import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import shape 
import itertools 
import os 
import fiona

pd.set_option('display.max_colwidth', -1)
os.chdir('c:\\Users\\Annie\\Downloads')


"reading ona file and outputting min max coords for bbox"
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


"getting osm topology"
set_wkt = pd. read_csv(wkt_file_name)

geometry = set_wkt[columnhead].map(wkt.loads)
set_wkt = set_wkt.drop(columnhead, axis=1)
crs = {'init': 'epsg:4326'}
gdf = gpd.GeoDataFrame(set_wkt, crs=crs, geometry=geometry)
gdf.to_file('lagos_test_bound.shp')

set_bound = fiona.open('lagos_test_bound.shp')
set_bound
#set_bound = gpd.read_file("hoima_bound1.shp")

as_shape = set_bound.next()

bound_asshape = shape(as_shape['geometry'])



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
