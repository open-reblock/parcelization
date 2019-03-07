# parcelization
scripts for automating building parcelization 

1. boundary_wkt   
Intakes and outputs CSVs with coordinates formatted as wkt

2. shp_prep  
Takes a csv with wkt of a settlements boundaries, parameterizes a bounding box according to polygon of set bounds, pulls buildings and roads topology from Open Street Maps, and writes them to a shapefile. Generates three .shp outputs: bounds, bldgs, rds

3. shp_geoprocessing  
Runs variety of geoprocessing operations on settlement boundaries, bldgs, and rds. Generates rough non-overlapping building parcel map of a given settlement 

4. blds_in_netwkrs   
will this be a thing tbd. but supposed to be script that polygonizes rd networks where available 
