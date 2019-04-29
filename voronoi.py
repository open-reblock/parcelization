import os

import fiona
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.spatial as spatial
import shapely
from shapely.geometry import LineString, Point, Polygon, shape


def index(gdf):
    gdf["index"] = list(range(len(gdf)))
    return gdf

def get_test_points():
    return index(gpd.read_file("data/west-point-monrovia/monrovia-1.json"))

def naive_centroid_voronoi(gdf):
    voronoi = spatial.Voronoi(list(zip(gdf.centroid.x, gdf.centroid.y)))
    spatial.voronoi_plot_2d(voronoi, ax=plt.gca())
    gdf.plot(alpha=0.1, ax=plt.gca(), column="index")
    plt.autoscale()
    plt.show()

def dissolved_buffer_voronoi(gdf, buffer_radius = 0.00001):
    # buffer
    print("buffer")
    buffered = gpd.GeoDataFrame()
    buffered["geometry"] = gdf.buffer(buffer_radius)
    buffered = index(buffered)
    buffered.plot(column="index")
    plt.title("buffered building footprints")
    plt.show()

    # dissolve
    print("dissolve")
    print("unioning polygons")
    buffered_polygons = list(buffered.unary_union)
    
    print("building gdf")
    buffered_union = gpd.GeoDataFrame(geometry=buffered_polygons)
    buffered_union.plot()
    plt.title("buffered union")
    plt.show()

    # fill 
    print("fill")
    filled_polygons = index(gpd.GeoDataFrame(geometry=[polygon.exterior for polygon in buffered_polygons]))
    filled_polygons.plot(column="index")
    plt.title("filled polygons")
    plt.show()

    # centroids 

    # intersect 

def corner_voronoi():
    pass

if __name__ == "__main__":
    # path = 'data/private/lagos_todo/lagos_priorities.shp'
    # gdf = gpd.read_file(path)
    # gdf.plot()
    # print(gdf.columns)
    # plt.show()
    
    # naive_centroid_voronoi(get_test_points())
    # naive_centroid_voronoi(index(gpd.read_file("data/private/hoima/hoima_set.shp")))

    dissolved_buffer_voronoi(get_test_points())
