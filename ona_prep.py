#!venv/bin/python

from itertools import cycle
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import pandas as pd
import shapefile
from descartes import PolygonPatch
from networkx.readwrite import json_graph
from shapely.geometry import LineString, MultiLineString, Polygon, mapping
from shapely.ops import cascaded_union

colors = cycle([
    "#1a281f", "#635255", "#ce7b91", "#c0e8f9", "#b8d3d1", 
    "#413c58", "#a3c4bc", "#bfd7b5", "#e7efc5", "#f2dda4", 
    "#c03221", "#f2d0a4", "#545e75", "#3f826d", "#605b56", 
    "#837a75", "#acc18a", "#dafeb7", "#f2fbe0"])

def diff_polygonize(region, linestrings, epsilon=0.00005):
    # https://gis.stackexchange.com/a/58674
    # suggest epsilon of 0.0001 for generating graphics, and 0.00005 to generate shapefiles
    return region.difference(MultiLineString(linestrings).buffer(epsilon))

def geometry_text_to_polygon(geometry_string):
    points = [tuple(float(xy) for xy in coordinate.split()[1::-1]) for coordinate in geometry_string.split(";")]
    return Polygon(points)

def edge_to_geometry(nodes, edge):
    if "geometry" in edge.keys():
        return edge["geometry"]
    src = nodes[edge["source"]]
    tgt = nodes[edge["target"]]
    return LineString([(src["x"], src["y"]), (tgt["x"], tgt["y"])])

def linestrings_from_network(graph):
    json_graph_rep = json_graph.node_link_data(graph)
    nodes = {node["id"]: node for node in json_graph_rep["nodes"]}
    edges = json_graph_rep["links"]
    return [edge_to_geometry(nodes, edge) for edge in edges]

def get_osm_graph(data_prefix, _id, name, polygon):
    try:
        return ox.graph_from_polygon(polygon, network_type="all_private", retain_all=True)
    except Exception as e:
        print(_id, name, e)
        return None

def main(data_prefix, ona_csv_path, ids, geometry_column, settlement_name_column, output_filename, network_search_buffer = 0.001, parcel_files=None, export_shapefile=False):
    # network_search_buffer: suggest 0.001 for single-settlement zoom-ins, 0.01 for graph construction

    print("reading data")
    ona = pd.read_csv(data_prefix/ona_csv_path)
    ona = ona.loc[ona["_id"].isin(ids)]
    ona = ona[["_id", settlement_name_column, geometry_column]]
    ona[geometry_column] = ona[geometry_column].apply(geometry_text_to_polygon)
    original_polygons = list(ona[geometry_column])
    multipolygon = cascaded_union(original_polygons)
    buffered_multipolygon = multipolygon.buffer(network_search_buffer)
    print("getting graph")
    road_network = ox.graph_from_polygon(buffered_multipolygon, network_type="all_private", retain_all=True)#, clean_periphery=False, simplify=True)
    
    print("parsing graph")
    linestrings = linestrings_from_network(road_network)
    polygons = diff_polygonize(buffered_multipolygon, linestrings)

    print("plotting")
    # fig, ax = ox.plot_graph(road_network, close=False, show=False)

    # for polygon in original_polygons:
    #     ax.add_patch(PolygonPatch(polygon, fc='#bb5a40', ec='k', linewidth=0, alpha=0.6, zorder=10))

    # plt.autoscale()
    # plt.show()

    fig, ax = ox.plot_graph(road_network, close=False, show=False)
    for (polygon, color) in zip(polygons, colors):
        ax.add_patch(PolygonPatch(polygon, fc=color, ec='k', linewidth=0, alpha=0.8, zorder=10))
    
    if parcel_files is not None:
        for pf in parcel_files:
            with shapefile.Reader(pf) as shp:
                for sr in shp.shapeRecords():
                    print(sr.record)
                    plt.gca().add_patch(PolygonPatch(sr.shape, fc="white", ec='white', linewidth=1, alpha=0.2, zorder=10))
    plt.autoscale()
    plt.show()

    if export_shapefile:
        print("exporting shapefile")
        with shapefile.Writer(data_prefix/output_filename) as shp:
            shp.field("index", "N")
            for (index, polygon) in enumerate(polygons):
                shp.record(index)
                shp.shape(mapping(polygon))

def freetown():
    data_prefix = Path("data/private/sierra_leone")

    ona_csv_path = "sdi_boundaries_2019_01_29_05_18_33_811857.csv"

    ids = set([
        12227565,
        13792377,
        12483794,
        12483646,
        12572108,
        12575839,
        13792326,
        12575032,
        2316424,
        12731894,
        12731669,
        12480824,
        12482641,
        5120040,
        5120025,
        5119968,
        1037833,
        12484335,
        16181451,
        16176788,
        16176404,
        16081266,
        2316927,
        2316558,
        2316856,
        1037824,
        1077121,
        1037845,
        12484697,
        12480901,
        1248109
    ]) - set([1037845, 2316856, 5119968, 12482641, 12484697, 12572108 ]) # ignore known geometry issues
    geometry_column = "section_C/C2_Boundary"
    settlement_name_column = "section_B/B7_Settlement_Name_Community"
    # output_filename = "freetown_blocks.shp"
    # output_filename = "dwarzark.shp"
    output_filename = "freetown_extended.shp"

    main(data_prefix, ona_csv_path, ids, geometry_column, settlement_name_column, output_filename, 0.015)

def lagos_focus():
    data_prefix = Path("data/private/nigeria")

    ona_csv_path = "sdi_boundaries_2019_03_07_01_45_19_506653.csv"
    ids = set([
        #??????   #afolabi alasia 
        3483778,  #ago egun bariga 
        33451457, #arobadade 
        4473536,  #daramola
        6437202,  #ebutte illaje 
        16751038, #isale akoka
        # 3652431,  #Ojora/Abete #broken geometry
        1387685   #Orisumibare
    ])
    geometry_column = "section_C/C2_Boundary"
    settlement_name_column = "section_B/B7_Settlement_Name_Community"
    output_filename = "lagos_focus.shp"
    parcel_files = [
		"data/private/lagos_parcels/lagosp_setinbound_section_7_Ojora Abete.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Ago Egun.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Arobadade.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Daramola.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Ebute Ilaje.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Isale Akoka.shp"
	]
    
    main(data_prefix, ona_csv_path, ids, geometry_column, settlement_name_column, output_filename, 0.001, export_shapefile=False, parcel_files=parcel_files)

# def sl_wmb():
#     data_prefix = Path("data/private/sierra_leone_wmb")
#     ona_csv_path = "sdi_boundaries_2019_01_29_05_18_33_811857.csv"
#     ids = set([
#         5120025,
#         5120040,
#         5119968,
#         12482641,
#         12480824,
#         12731669,
#     ])

#     geometry_column = "section_C/C2_Boundary"
#     settlement_name_column = "section_B/B7_Settlement_Name_Community"
#     output_filename = "sierra_leone_wmb.shp"

#     ona = pd.read_csv(data_prefix/ona_csv_path)
#     ona = ona.loc[ona["_id"].isin(ids)]
#     ona = ona[["_id", settlement_name_column, geometry_column]]
#     ona[geometry_column] = ona[geometry_column].apply(geometry_text_to_polygon)

#     with shapefile.Writer(data_prefix/output_filename) as shp:
#         shp.field("id", "N")
#         shp.field("name", "C")
#         for (_id, name, geom) in ona.itertuples(index=False):
#             shp.record(_id, name)
#             # shp.record(name)
#             shp.shape(mapping(geom))

if __name__ == "__main__":
    freetown()