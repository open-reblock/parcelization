# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 09:45:09 2019

@author: Annie
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import scipy.spatial as spatial
import os
import shapely
from shapely.geometry import Point, LineString, Polygon, shape
from shapely.geometry import JOIN_STYLE
import matplotlib.pyplot as plt 
import pytess

bldgs_filename = 'hoima_bldgs.shp'
bounds_filename = 'hoima_bound1.shp'

os.chdir('c:\\Users\\Annie\\Downloads')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', -1)

set_bldgs = gpd.read_file(bldgs_filename)
set_bldgs = set_bldgs.to_crs(epsg = 3857)
#set_bldgs.plot()

set_bounds = gpd.read_file(bounds_filename)
set_bounds = set_bounds.to_crs(epsg=3857)

#set_bounds = set_bounds.plot(alpha = .1)
#set_bldgs.plot(ax = set_bounds)

"find intersect of bound and building shp, create new shp"
bldgs_inbnds = []
for index1, sets in set_bldgs.iterrows():
    for index2, bounds in set_bounds.iterrows():
       if sets['geometry'].intersects(bounds['geometry']):
          bldgs_inbnds.append({'geometry': sets['geometry'].intersection(bounds['geometry'])})
bldgs_inbnds = gpd.GeoDataFrame(bldgs_inbnds,columns=['geometry'])
bldgs_inbnds.to_file('intersection.shp')

"performing geoprocessing on buildings in ona bounds"
set_intersect = gpd.read_file('intersection.shp')
set_intersect.crs = {'init': 'epsg:3857'}
set_buff = set_intersect.buffer(5)
#hoima_buff.plot(edgecolor = 'black')

set_diss = set_buff.unary_union
set_diss= gpd.GeoDataFrame(crs = set_buff.crs, geometry = [set_diss])
#set_diss.plot(edgecolor= 'black')

set_cent = set_intersect.copy()
set_cent.geometry = set_cent.centroid
set_cent.crs = set_intersect.crs
set_cent

set_x = set_cent.geometry.x
set_y = set_cent.geometry.y


#hoima_xy = [ [x,y] for (x,y) in list(zip(hoima_x, hoima_y))]
set_xy = np.array(list(tuple(zip(set_x, set_y))))
set_xy

set_vor = spatial.Voronoi(set_xy)
spatial.voronoi_plot_2d(set_vor)
#plt.show()

set_lines = [  
        shapely.geometry.LineString(set_vor.vertices[line])
        for line in set_vor.ridge_vertices
        if -1 not in line
]
set_lines

set_vor_poly = list(shapely.ops.polygonize(set_lines))
print(set_vor_poly)
set_vor_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:3857'}, geometry = set_vor_poly)
#set_vor_gdf.plot()


#hoima_vor = pytess.voronoi(hoima_xy)
#hoima_vorpolys = [Polygon(hoima_vor[0][1]) for i in hoima_vor]
#hoima_vor_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:3857'}, geometry = hoima_vorpolys)
#hoima_vor_gdf.plot()

'intersecting dissolved settlment w voronoi tess'
vor_diss = []
for index1, sets in set_diss.iterrows():
    for index2, bounds in set_vor_gdf.iterrows():
       if sets['geometry'].intersects(bounds['geometry']):
          vor_diss.append({'geometry': sets['geometry'].intersection(bounds['geometry'])})
vor_diss = gpd.GeoDataFrame(vor_diss,columns=['geometry'])
vor_diss.to_file('intsct_vor.shp')

vor_diss = gpd.read_file('intsct_vor.shp')
vor_diss.plot(edgecolor = 'black')
vor_diss

'cleaning up non-overlapping buffers- wip!!!!'
eps = .01
fx = vor_diss.buffer(eps, 1, join_style=JOIN_STYLE.mitre).buffer(-eps, 1, join_style=JOIN_STYLE.mitre)
fx.plot()
