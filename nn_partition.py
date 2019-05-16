from itertools import cycle, product

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytess
import rtree
import scipy.spatial as spatial
import shapely
from descartes import PolygonPatch
from shapely.geometry import LineString, Point, Polygon, shape, MultiPoint
from shapely.ops import nearest_points

colors = cycle([
    "#1a281f", "#635255", "#ce7b91", "#c0e8f9", "#b8d3d1", 
    "#413c58", "#a3c4bc", "#bfd7b5", "#e7efc5", "#f2dda4", 
    "#c03221", "#f2d0a4", "#545e75", "#3f826d", "#605b56", 
    "#837a75", "#acc18a", "#dafeb7", "#f2fbe0"])

sample_pts = [Point(x, y) for (x, y) in [(-10.8074, 6.32927), (-10.8077, 6.32898), (-10.8076, 6.32926)]]

def index(gdf):
    gdf["index"] = list(range(len(gdf)))
    return gdf

def get_test_buildings():
    return index(gpd.read_file("data/west-point-monrovia/monrovia-1.json"))

def get_test_boundary():
    return gpd.read_file("data/west-point-monrovia/monrovia-1-boundary.json")

def make_bounded_grid(boundary, num_x_pts, num_y_pts=None):
    bounding_box = boundary.bounds
    if num_y_pts is None:
        num_y_pts = num_x_pts
    (xmin, ymin, xmax, ymax) = bounding_box
    (xs, dx) = np.linspace(xmin, xmax, num_x_pts, endpoint=False, retstep=True)
    (ys, dy) = np.linspace(ymin, ymax, num_y_pts, endpoint=False, retstep=True)
    grid = product(xs[1:], ys[1:])
    return ((pt for pt in map(Point, grid) if boundary.contains(pt)), dx, dy)

def get_nearest_footprint(point, footprints):
    footprints["geometry"].apply(lambda geom: next(pt.xy for pt in nearest_points(point, geom) if pt != point))

def nearest_to_exterior(pt, footprints):
    return footprints["geometry"].apply(lambda poly: poly.exterior.distance(pt)).idxmin()

def nearest_by_index(pt, idx):
    return list(idx.nearest(pt, 1))

def main(buildings, boundary, show=False):
    #buildings_union = buildings.unary_union
    spatial_index  = buildings.sindex
    
    # (grid_centers, _, _) = make_bounded_grid(boundary["geometry"][0], 100)
    (grid_centers, _, _) = make_bounded_grid(boundary, 100)
    grid_centers = gpd.GeoSeries(list(grid_centers))#.difference(buildings_union)
    grid_centers = grid_centers[grid_centers.is_empty == False]

    # partitions = gpd.GeoDataFrame({
    #     "geometry": grid_centers,
    #     "nearest" : [next(spatial_index.nearest(pt.coords[0], 1)) for pt in grid_centers]
    # }).groupby("nearest")["geometry"].apply(lambda pts: MultiPoint(list(pts)).convex_hull)
    # for (color, mp) in zip(colors, partitions):
    #     plt.gca().add_patch(PolygonPatch(mp, fc=color, ec=color))
    # boundary.plot(facecolor="white", edgecolor="grey", ax=plt.gca())
    # buildings.plot(facecolor="white", edgecolor="black", ax=plt.gca(), zorder=20)
    # plt.show()

    partitions = gpd.GeoDataFrame({
        "geometry": grid_centers,
        "nearest" : [next(spatial_index.nearest(pt.coords[0], 1)) for pt in grid_centers]
    }).groupby("nearest")["geometry"].apply(
        #lambda pts: MultiPoint(list(pts)).convex_hull.simplify(tolerance = 0.0000001, preserve_topology=True))
        lambda pts: MultiPoint(list(pts)).convex_hull)

    if show:
        for (color, partition) in zip(colors, partitions):
            try:
                plt.gca().add_patch(PolygonPatch(partition, fc=color, ec=color))
            except ValueError:
                pass
        # boundary.plot(facecolor="white", edgecolor="grey", ax=plt.gca())
        buildings.plot(facecolor="white", edgecolor="black", ax=plt.gca(), zorder=20)
        plt.gca().add_patch(PolygonPatch(boundary, fc="white", ec="black", zorder=-1))
        plt.show()

    return partitions


if __name__ == "__main__":
    # main(get_test_buildings(), get_test_boundary())
    main(gpd.read_file("data/private/hoima/hoima_set.shp"), gpd.read_file("data/private/hoima/hoima_bounds.shp"))
