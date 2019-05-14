import json

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

def plot_gradient(gradient, boundary, buildings, ax=None, color=pink, building_color="white", building_edge_color="black", name=None):
    if ax is None:
        ax = plt.gca()
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

def get_gradient(buildings, boundary, buffer_radius = 0.00001, show=False, **kwargs):
    boundary_geometry = boundary["geometry"][0]
    gradient = []
    buffered_union = buildings.unary_union

    while not buffered_union.contains(boundary_geometry):
        buffered_union = buffered_union.buffer(buffer_radius)
        gradient.append(buffered_union)
        print(len(gradient))
    if show:
        plot_gradient(gradient, boundary, buildings, **kwargs)

    return gradient

def process_diff(gradient, buildings, boundary):
    ax = plt.gca()
    boundary.plot(ax=ax, zorder=-20)
    buildings.plot(ax=ax, zorder=-19, facecolor="white")
    # diff = gradient[-1]
    # for poly in gradient[-2::-1]:
    #     diff = diff.difference(poly)
    diff = gradient[0]
    for poly in gradient[1:]:
        diff = poly.difference(diff)
    # print(diff)
    ax.add_patch(PolygonPatch(diff, fc = "white", ec="black", zorder=2))
    ax.axis('off')
    ax.margins(0)
    ax.tick_params(which='both', direction='in')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.autoscale()
    plt.show()

# process_diff(gradient, boundary)

if __name__ == "__main__":
    buildings = get_test_buildings() #gpd.read_file("data/private/hoima/hoima_set.shp")
    boundary  = get_test_boundary() #gpd.read_file("data/private/hoima/hoima_bounds.shp")
    gradient = get_gradient(buildings, boundary, 0.00001, color=purple, show=False)
    diff = gradient[-1].difference(gradient[-2])
    process_diff(gradient, buildings, boundary)

    # with open('hoima_gradient_diff_0.00001.geojson', 'wb') as dst:
    #     json.dumps(gpd.GeoSeries(diff).to_json())