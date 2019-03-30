import json
import sys

from shapely.geometry import asShape, mapping
from shapely.ops import polygonize

highway_whitelist = {'primary', 'secondary', 'tertiary', 'residential', 'trunk'}

def main(argv=None):
    if argv is None:
        argv = sys.argv
    filename = argv[1]

    with open(filename) as input_file:
        unfiltered_geojson = json.load(input_file)
    
    polygons = run_polygonization_pipeline(unfiltered_geojson)

    with open("polygons_" + filename, 'w') as output_file:
        json.dump(polygons, output_file)


def run_polygonization_pipeline(unfiltered_geojson):
    filtered_streets = filter_to_streets(unfiltered_geojson)
    segmented_streets = segment_streets(filtered_streets)
    polygons = polygonize_streets(segmented_streets)

    return polygons

def filter_to_streets(geojson):
    geojson['features'] = [feature for feature in geojson['features'] if feature['properties']['highway'] in highway_whitelist]
    return geojson

def segment_streets(multipoint_lines):
    output = {
        "type": "FeatureCollection",
        "features": []
    }

    for feature in multipoint_lines['features']:
        output['features'] += [
            get_line_feature(current, feature['geometry']['coordinates'][i+1], feature['properties']) 
            for (i, current) in enumerate(feature['geometry']['coordinates'][:-1])]
    return output

def get_line_feature(start, stop, properties):
    return {"type": "Feature",
            "properties": properties, 
            "geometry": {
                "type": "LineString",
                "coordinates": [start, stop]
            }
        }

def polygonize_streets(streets):
    lines = []
    for feature in streets['features']:
        lines.append(asShape(feature['geometry']))

    polys = list(polygonize(lines))

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for poly in polys:
        geojson['features'].append({
            "type": "Feature",
            "properties": {},
            "geometry": mapping(poly)
        })

    return geojson


if __name__ == "__main__":
    main()
