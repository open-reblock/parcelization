import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytess
import scipy.spatial as spatial
import shapely
from descartes import PolygonPatch
from shapely.geometry import LineString, Point, Polygon, shape

coral  = "#FA7268"
green  = "#7FFF00"
pink   = "#FF1493"
purple = "#8A2BE2"

def get_test_buildings():
    return gpd.read_file("data/west-point-monrovia/monrovia-1.json")

def get_test_boundary():
    return gpd.read_file("data/west-point-monrovia/monrovia-1-boundary.json")

def main(buildings, boundary, color=pink, buffer_radius = 0.00001, building_color="white", building_edge_color="black", name=None):
    boundary_geometry = boundary["geometry"][0]
    gradient = []
    buffered_union = buildings.unary_union

    ax = plt.gca()

    while not buffered_union.contains(boundary_geometry):
        buffered_union = buffered_union.buffer(buffer_radius)
        gradient.append(buffered_union)
        print(len(gradient))
    alpha = 1.1/(len(gradient) - 1)
    for poly in gradient:
        ax.add_patch(PolygonPatch(poly, fc=color, alpha=alpha))
    boundary.plot(ax=ax, facecolor="white")
    buildings.plot(ax=ax, facecolor=building_color, edgecolor=building_edge_color, zorder=20, linewidth=0.1)


    ax.axis('off')
    ax.margins(0)
    ax.tick_params(which='both', direction='in')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    if name is not None:
        plt.savefig(name, dpi=300, bbox_inches="tight")
    plt.show()

def redhook(color, buffer, **kwargs):
    buildings = gpd.read_file("data/redhook_shp/redhook_planet_osm_polygon_polygons.shp")
    boundary = gpd.read_file("data/redhook_shp/subset-boundary.geojson")

    # buildings = buildings[buildings.intersects(boundary)]

    main(buildings, boundary, color, buffer, **kwargs)


if __name__ == "__main__":
    # main(get_test_buildings(), get_test_boundary(), pink, name="westpoint.png")

    redhook("black", 0.00025, building_color=coral, building_edge_color="white", name="redhook.png")
    
    # main(get_test_buildings(), get_test_boundary(), buffer_radius = 0.000001)
    
    # main(gpd.read_file(
    #     "data/private/hoima/hoima_set.shp"), 
    #     gpd.read_file("data/private/hoima/hoima_bounds.shp"), 
    #     purple, 0.0001, name="hoima.png")

    # main(gpd.read_file(
    #     "data/private/hoima/hoima_set.shp"), 
    #     gpd.read_file("data/private/hoima/hoima_bounds.shp"), 
    #     purple, 0.00001)