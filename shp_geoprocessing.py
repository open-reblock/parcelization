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
import matplotlib.pyplot as plt 
import fiona 

os.chdir('file path here')
bldgs_filename = 'xxx.shp'
bounds_filename = 'yyy.shp'

'reading/checking .shp files'
set_bounds = gpd.read_file(bounds_filename)
set_bounds = set_bounds.to_crs(epsg= 26393)
sb_gdf = gpd.GeoDataFrame(set_bounds, crs = set_bounds.crs)
sb_gdf
set_bounds = set_bounds.plot(alpha = .1)
set_bounds.plot()

set_bldgs = gpd.read_file(bldgs_filename)
set_bldgs = set_bldgs.to_crs(epsg = 26393)
sbds_gdf = gpd.GeoDataFrame(set_bldgs, crs = set_bldgs.crs)

set_bldgs.plot(ax = set_bounds)

'calculating land use stats'
bound_area =float(sb_gdf['section_13'])
sbds_gdf['area'] = sbds_gdf['geometry'].area
bld_area = (sbds_gdf['area'].sum())
percent_built = bld_area / bound_area
print(percent_built)


'find intersect of bound and building shp, create new shp'
bldgs_inbnds = []
for index1, sets in set_bldgs.iterrows():
    for index2, bounds in set_bounds.iterrows():
       if sets['geometry'].intersects(bounds['geometry']):
          bldgs_inbnds.append({'geometry': sets['geometry'].intersection(bounds['geometry'])})
bldgs_inbnds = gpd.GeoDataFrame(bldgs_inbnds,columns=['geometry'])
bldgs_inbnds.to_file('intersection.shp')


"performing geoprocessing on buildings in ona bounds"
'1. buffer'
set_intersect = gpd.read_file('lagosp0.shp')
set_intersect.crs = {'init': 'epsg:26393'}
set_intersect['geometry']
set_intersect.plot()
set_buff = set_intersect.buffer(.00001)
set_buff.plot(edgecolor = 'black')

'2. dissolve' 
set_diss = set_buff.unary_union
if set_diss.geom_type == 'MultiPolygon':
    set_diss_polys = []
    for polygon in set_diss:
        set_diss_polys.append(polygon)
set_diss_polys
sd_polys = gpd.GeoDataFrame(crs = set_intersect.crs, geometry = set_diss_polys)
sd_polys.plot()
#set_diss.to_file('set_diss.shp')
#set_diss_filled = fiona.open('set_diss.shp')

'3. fill holes'
set_diss_filled= []
for poly in set_diss_polys:
    set_diss_filling = Polygon(poly.exterior)
    set_diss_filled.append(set_diss_filling)
set_diss_filled
sd_polys_filled = gpd.GeoDataFrame(crs = set_intersect.crs, geometry = set_diss_filled)
sd_polys_filled.plot()

'4. centroids from blds for voronoi' 
set_cent = set_intersect.copy()
set_cent.geometry = set_cent.centroid
set_cent.crs = set_intersect.crs
set_cent

'5. voronoi timeee' 
set_x = set_cent.geometry.x
set_y = set_cent.geometry.y

set_xy = np.array(list(tuple(zip(set_x, set_y))))
set_xy

set_vor = spatial.Voronoi(set_xy)
spatial.voronoi_plot_2d(set_vor)


set_lines = [  
        shapely.geometry.LineString(set_vor.vertices[line])
        for line in set_vor.ridge_vertices
        if -1 not in line
]
set_lines

set_vor_poly = list(shapely.ops.polygonize(set_lines))
print(set_vor_poly)
set_vor_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:26393'}, geometry = set_vor_poly)


#set_vor_gdf.plot()


#hoima_vor = pytess.voronoi(hoima_xy)
#hoima_vorpolys = [Polygon(hoima_vor[0][1]) for i in hoima_vor]
#hoima_vor_gdf = gpd.GeoDataFrame(crs = {'init': 'epsg:3857'}, geometry = hoima_vorpolys)
#hoima_vor_gdf.plot()

'6. intersecting clean dissolved settlment w voronoi tess'
vor_diss = []
for index1, sets in sd_polys_filled.iterrows():
    for index2, bounds in set_vor_gdf.iterrows():
       if sets['geometry'].intersects(bounds['geometry']):
          vor_diss.append({'geometry': sets['geometry'].intersection(bounds['geometry'])})
vor_diss = gpd.GeoDataFrame(vor_diss,columns=['geometry'])
vor_diss.plot(edgecolor = 'black')
vor_diss.to_file('intsct_vor.shp')

vor_diss = gpd.read_file('intsct_vor.shp')
vor_diss.plot(edgecolor = 'black')
vor_diss
