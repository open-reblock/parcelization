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


os.chdir('c:\\Users\\Annie\\Downloads')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', -1)

hoima_set = gpd.read_file("hoima_bldgs.shp")
hoima_set = hoima_set.to_crs(epsg = 3857)
#hoima_set.plot()

hoima_bounds = gpd.read_file('hoima_bound1.shp')
hoima_bounds = hoima_bounds.to_crs(epsg=3857)
hoima_bounds
hoima_bounds = hoima_bounds.plot(alpha = .1)
hoima_set.plot(ax = hoima_bounds)
"find intersect of bound and building shp, create new shp"
bldgs_inbnds = []
for index1, sets in hoima_set.iterrows():
    for index2, bounds in hoima_bounds.iterrows():
       if sets['geometry'].intersects(bounds['geometry']):
          bldgs_inbnds.append({'geometry': sets['geometry'].intersection(bounds['geometry'])})
bldgs_inbnds = gpd.GeoDataFrame(bldgs_inbnds,columns=['geometry'])
bldgs_inbnds.to_file('intersection.shp')

e"performing geoprocessing on buildings in ona bounds"
hoima_set = gpd.read_file('intersection.shp')
hoima_set.crs = {'init': 'epsg:3857'}
hoima_buff = hoima_set.buffer(5)
#hoima_buff.plot(edgecolor = 'black')

hoima_diss = hoima_buff.unary_union
hoima_diss= gpd.GeoDataFrame(crs = hoima_buff.crs, geometry = [hoima_diss])
hoima_diss.plot(edgecolor= 'black')

hoima_cent = hoima_set.copy()
hoima_cent.geometry = hoima_cent.centroid
hoima_cent.crs = hoima_set.crs
hoima_cent

hoima_x = hoima_cent.geometry.x
hoima_y = hoima_cent.geometry.y


#hoima_xy = [ [x,y] for (x,y) in list(zip(hoima_x, hoima_y))]
hoima_xy = np.array(list(tuple(zip(hoima_x, hoima_y))))
hoima_xy

hoima_vor = spatial.Voronoi(hoima_xy)
spatial.voronoi_plot_2d(hoima_vor)
plt.show()

hoima_lines = [  
        shapely.geometry.LineString(hoima_vor.vertices[line])
        for line in hoima_vor.ridge_vertices
        if -1 not in line
]
hoima_lines

hoima_vor_poly = list(shapely.ops.polygonize(hoima_lines))
print(hoima_vor_poly)
hoima_vor_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:3857'}, geometry = hoima_vor_poly)
hoima_vor_gdf.plot()


#hoima_vor = pytess.voronoi(hoima_xy)
#hoima_vorpolys = [Polygon(hoima_vor[0][1]) for i in hoima_vor]
#hoima_vor_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:3857'}, geometry = hoima_vorpolys)
#hoima_vor_gdf.plot()
'intersecting dissolved settlment w voronoi tess'
vor_diss = []
for index1, sets in hoima_diss.iterrows():
    for index2, bounds in hoima_vor_gdf.iterrows():
       if sets['geometry'].intersects(bounds['geometry']):
          vor_diss.append({'geometry': sets['geometry'].intersection(bounds['geometry'])})
vor_diss = gpd.GeoDataFrame(vor_diss,columns=['geometry'])
vor_diss.to_file('intsct_vor.shp')

vor_diss = gpd.read_file('intsct_vor.shp')
vor_diss.plot(edgecolor = 'black')
vor_diss

'cleaning up non-overlapping buffers'
eps = .01
fx = vor_diss.buffer(eps, 1, join_style=JOIN_STYLE.mitre).buffer(-eps, 1, join_style=JOIN_STYLE.mitre)
fx.plot()
