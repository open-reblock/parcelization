# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 19:47:05 2018

@author: Annie
"""
file_name = "lagos_test.csv" 

    
import pandas as pd 

import_df = pd.read_csv(file_name)

columnhead = ""
if 'verification/A0_Boundary' in import_df:
    columnhead = 'verification/A0_Boundary'
elif 'C2a. Settlement Boundary' in import_df:
    columnhead = 'C2a. Settlement Boundary'
elif 'section_C/C2_Boundary' in import_df:
    columnhead = 'section_C/C2_Boundary'
    
export_df = import_df[['device_id',columnhead]].copy()
export_df[columnhead] = export_df[columnhead].fillna("no bounds") 
export_df

'''
def switchcoords(text):
    text= text.split(";")
    polygon = "POLYGON(("
    for i in text:
        line = i.split()
        coord = line[1] +" " + line[0]
        polygon = polygon + coord
    polygon = polygon +"))"
    return polygon
'''
def switchcoords(text):
    text= text.split(";")
    if len(text) < 3: #invalid number of coords
        return text
    coords = [] # list of x y coords
    for i in text:
        line = i.split()
        coord = line[1] +" " + line[0]
        coords.append(coord)
    fcoord = coords[0]
    lcoord = coords.append(fcoord)
    polygon = "POLYGON((" + ",".join(coords) + "))" #polygon string
    return polygon

export_df[columnhead] = export_df[columnhead].apply(switchcoords)
#check output dataframe contains desired fields 
print(export_df['device_id'])
print(export_df[columnhead])


export_df.to_csv('lagos_test_wkt.csv')
