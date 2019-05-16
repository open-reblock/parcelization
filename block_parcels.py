import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import shapefile
from descartes import PolygonPatch
from progressbar import progressbar
from shapely.geometry import mapping

from nn_partition import main as get_parcels

def main(blocks, all_buildings, output_filename=None):
    parcels = []
    for block in progressbar(blocks.itertuples(), max_value=len(blocks)):
        buildings = all_buildings[all_buildings.intersects(block.geometry)]
        try: 
            parcels.append(get_parcels(buildings, block.geometry, show=False))
        except Exception as e:
            print(e)
            print("exception occured during parcelizing: {}".format(block))
    
    print("number of parcels: {}".format(len(parcels)))
    if output_filename:
        print("exporting parcels to shapefile")
        concatenated = pd.concat(parcels)
        gpd.GeoSeries(concatenated[concatenated.apply(lambda g:g.type) == "Polygon"]).to_file(output_filename)
    return parcels

def narrow_footprints():
    buildings = gpd.read_file('data/private/sierra_leone/1172_sierra_leono_building_4326.shp')
    block_union = blocks.unary_union
    # https://geoffboeing.com/2016/10/r-tree-spatial-index-python/
    print("building spatial index")
    sindex = buildings.sindex
    possible_matches = buildings.iloc[list(sindex.intersection(block_union.bounds))]
    possible_matches.sindex
    possible_matches.to_file('data/private/sierra_leone/dg_freetown_footprint.shp')

if __name__ == "__main__":
    blocks    = gpd.read_file('data/private/sierra_leone/freetown_extended.shp')
    buildings = gpd.read_file('data/private/sierra_leone/dg_freetown_footprint.shp')
    print("building spatial index")
    sindex = buildings.sindex
    print("number of blocks: {}".format(len(blocks)))
    parcels = main(blocks, buildings, "data/private/sierra_leone/freetown_parcels.shp")
