import os

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytess
import scipy.spatial as spatial
import shapely
from descartes import PolygonPatch
from shapely.geometry import LineString, Point, Polygon, shape


def index(gdf):
    gdf["index"] = list(range(len(gdf)))
    return gdf

def get_test_buildings():
    return index(gpd.read_file("data/west-point-monrovia/monrovia-1.json"))

def get_test_boundary():
    return gpd.read_file("data/west-point-monrovia/monrovia-1-boundary.json")["geometry"][0]

def naive_centroid_voronoi(buildings):
    voronoi = spatial.Voronoi(list(zip(buildings.centroid.x, buildings.centroid.y)))
    spatial.voronoi_plot_2d(voronoi, ax=plt.gca())
    buildings.plot(alpha=0.1, column="index")
    plt.autoscale()
    plt.show()

def plot_line(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, color="white", linewidth=2, solid_capstyle='round', zorder=1)

def bounded_centroid_voronoi(buildings, boundary):
    voronoi = spatial.Voronoi(
        list(zip(buildings.centroid.x, buildings.centroid.y)))
        # list(zip(*boundary.exterior.coords.xy)))
    voronoi_edges = [
        LineString(voronoi.vertices[line]) for line in voronoi.ridge_vertices if -1 not in line
    ]
    voronoi_polygons = gpd.GeoDataFrame(
        geometry=[boundary.intersection(polygon) for polygon in shapely.ops.polygonize(voronoi_edges)])

    # plot buildings and bounds first 

    ax = plt.gca()
    buildings.plot(ax=ax, alpha=0.3, facecolor="white", zorder=5)
    plot_line(ax, boundary.boundary)
    ax.axis('off')
    ax.margins(0)
    ax.tick_params(which='both', direction='in')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.autoscale()
    plt.savefig("voronoi_parcels.png", transparent=True, dpi=300, bbox_inches="tight")
    axes_lims = plt.axis()
    plt.show()

    # voronoi_polygons.plot(ax=plt.gca(), facecolor="red", edgecolor="black", alpha=0.5)   
    ax = plt.gca() 
    spatial.voronoi_plot_2d(voronoi, ax=ax, show_points=False, show_vertices=False, line_colors=tuple(_/256.0 for _ in [134, 188, 168]), line_width=2)
    ax.plot(voronoi.points[:,0], voronoi.points[:,1], '.', color=tuple(_/256.0 for _ in [62, 101, 88]))
    # ax.plot(voronoi.vertices[:,0], voronoi.vertices[:,1], 'o', color=tuple(_/256.0 for _ in [134, 188, 168]))
    buildings.plot(ax=ax, alpha=0.5, facecolor="white", zorder=-1)
    plot_line(ax, boundary.boundary)
    ax.axis('off')
    ax.margins(0)
    ax.tick_params(which='both', direction='in')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.axis(axes_lims)
    plt.savefig("voronoi_polygons.png", transparent=True, dpi=300, bbox_inches="tight")
    plt.show()

def dissolved_buffer_voronoi(gdf, buffer_radius = 0.00001):
    # buffer
    print("buffer")
    buffered = index(gpd.GeoDataFrame({"geometry": gdf.buffer(buffer_radius)}))
    # buffered.plot(column="index")
    # plt.title("buffered building footprints")
    # plt.show()

    # union and fill in holes in union
    print("union and fill")
    filled_polygons = index(gpd.GeoDataFrame(geometry=[Polygon(polygon.exterior) for polygon in buffered.unary_union]))
    filled_polygons.plot(column="index", edgecolor="black")
    plt.title("filled, unioned polygons")
    plt.show()

    # voronoi from building centroids 
    voronoi = spatial.Voronoi(list(zip(gdf.centroid.x, gdf.centroid.y)))
    spatial.voronoi_plot_2d(voronoi, ax=plt.gca())
    gdf.plot(alpha=0.1, column="index", ax=plt.gca())
    plt.autoscale()
    plt.show()
    voronoi_edges = [
        LineString(voronoi.vertices[line]) for line in voronoi.ridge_vertices if -1 not in line
    ]
    voronoi_polygons = gpd.GeoDataFrame(geometry=list(shapely.ops.polygonize(voronoi_edges)))

    # intersect 
    # intersections = filled_polygons.join(voronoi_polygons, rsuffix='_voronoi', how="left", op="intersects")
    intersections = gpd.sjoin(filled_polygons, voronoi_polygons, how="left", op="intersects")
    intersection_geometry = gpd.GeoDataFrame(geometry=intersections
        .join(voronoi_polygons, rsuffix="_voronoi")
        .apply(lambda row: row["geometry"].intersection(row["geometry_voronoi"]), axis=1))
    
    intersection_geometry.plot(edgecolor="red")
    spatial.voronoi_plot_2d(voronoi, ax=plt.gca())
    gdf.plot(alpha=0.1, column="index", ax=plt.gca())
    plt.show()


def corner_voronoi(buildings, boundary):
    building_points = buildings["geometry"].apply(lambda poly: list(zip(*poly.exterior.coords.xy))).sum()
    # building_points_x, building_points_y = list(zip(*building_points))
    # voronoi = spatial.Voronoi(building_points + list(zip(*boundary.exterior.coords.xy)), qhull_options='Qbb Qc Qx Tv')
    # spatial.voronoi_plot_2d(voronoi, ax=plt.gca())

    voronoi_points, voronoi_polygons = zip(*pytess.voronoi(building_points + list(zip(*boundary.exterior.coords.xy))))

    gpd.GeoDataFrame(geometry=[Polygon(p) for p in voronoi_polygons]).plot(ax=plt.gca())

    gpd.GeoDataFrame(geometry=[Point(p) for p in voronoi_points if p]).plot(ax=plt.gca(), facecolor="white", zorder=10)

    buildings.plot(ax=plt.gca(), zorder=5, facecolor="red")
    plt.gca().add_patch(PolygonPatch(boundary, fc='#999999', ec='#999999', alpha=0.1))

    plt.show()

    # [v.point_region[i] for (i, pt) in enumerate(v.points) if plgn.touches(Point(pt))]

    # return voronoi


if __name__ == "__main__":
    bounded_centroid_voronoi(get_test_buildings(), get_test_boundary())

    # dissolved_buffer_voronoi(get_test_buildings())
    # naive_centroid_voronoi(index(gpd.read_file("data/private/hoima/hoima_set.shp")))

    # corner_voronoi(get_test_buildings(), get_test_boundary()) 
    # dissolved_buffer_voronoi(index(gpd.read_file("data/private/hoima/hoima_set.shp"))) 
