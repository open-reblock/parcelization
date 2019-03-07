# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 11:08:13 2019

@author: Annie
"""

'lets make a polygon outta a road network and then intersect it w buildingsss'
import numpy as np
import pandas as pd
import geopandas as gpd
import scipy.spatial as spatial
import os
import shapely
from shapely.geometry import Point, LineString, Polygon, shape
import pytess
import osmnx as ox  

os.chdir('c:\\Users\\Annie\\Downloads')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', -1)

set_rds = ox.core.graph_from_polygon(polygon = bound_asshape, network_type = 'drive')
set_rds = ox.project_graph(set_rds)
#ox.plot_graph(set_rds)
#set_rds = ox.save_graph_shapefile(set_rds, filename = 'lagos_test_ntwrk')

set_rds_gdf
as_shape = set_bound.next()

rd_asshape = shape(as_shape['geometry'])

rd_poly = list(shapely.ops.polygonize(rd_lines))
print(hoima_vor_poly)
hoima_vor_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:3857'}, geometry = hoima_vor_poly)
hoima_vor_gdf.plot()