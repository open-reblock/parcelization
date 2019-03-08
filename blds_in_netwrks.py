# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 11:08:13 2019

@author: Annie
"""

'lets make a polygon outta a road network and then intersect it w buildingsss'
import pandas as pd
import geopandas as gpd
import os
import shapely
from shapely.geometry import Point, LineString, Polygon, shape
import osmnx as ox 
import fiona 

os.chdir('c:\\Users\\Annie\\Downloads')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', -1)


set_bound = fiona.open('lagos_test_bound.shp')
set_bound
as_shape = set_bound.next()
bound_asshape = shape(as_shape['geometry'])

set_rds = ox.core.graph_from_polygon(polygon = bound_asshape, network_type = 'drive')
set_rds = ox.project_graph(set_rds)
 
set_rds_gdf = ox.save_load.graph_to_gdfs(set_rds, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
print(set_rds_gdf['geometry'])
rd_poly = list([shapely.ops.polygonize(set_rds_gdf['geometry']) for n in set_rds_gdf['geometry']])
rd_poly

rd_poly_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:3857'}, geometry = rd_poly)
rd_poly_gdf.plot()
