from pathlib import Path
from ona_prep import main, colors
import shapefile
import matplotlib.pyplot as plt
import osmnx as ox
from descartes import PolygonPatch

parcel_files = [
		"data/private/lagos_parcels/lagosp_setinbound_section_7_Ojora Abete.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Ago Egun.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Arobadade.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Daramola.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Ebute Ilaje.shp",
		"data/private/lagos_parcels/lagosp_setinbound_section__7_Isale Akoka.shp"
	]

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
    output_filename = "lagos_focus_merge.shp"
    
    main(data_prefix, ona_csv_path, ids, geometry_column, settlement_name_column, output_filename, 0.01)

if __name__ == "__main__":
    lagos_focus()

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
    fig, ax = ox.plot_graph(road_network, close=False, show=False)

    for polygon in original_polygons:
        ax.add_patch(PolygonPatch(polygon, fc='#bb5a40', ec='k', linewidth=0, alpha=0.6, zorder=10))

    plt.autoscale()
    plt.show()

    fig, ax = ox.plot_graph(road_network, close=False, show=False)
    for (polygon, color) in zip(polygons, colors):
        ax.add_patch(PolygonPatch(polygon, fc=color, ec='k', linewidth=0, alpha=0.8, zorder=10))
    
    plt.autoscale()
    plt.show()



    plt.show()

            