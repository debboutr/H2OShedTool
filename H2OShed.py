# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:55:48 2017

@author: Rdebbout
"""
import numpy as np
import rasterio as rs
import geopandas as gpd
import georasters as gr



def makeDirections(pp):    
    zero = (pp[0],pp[1]+1)
    one = (pp[0]+1,pp[1]+1)
    two = (pp[0]+1,pp[1])
    three = (pp[0]+1,pp[1]-1)
    four = (pp[0],pp[1]-1)
    five = (pp[0]-1,pp[1]-1)
    six = (pp[0]-1,pp[1])
    seven = (pp[0]-1,pp[1]+1)
    return [zero,one,two,three,four,five,six,seven]

def circleCell(dirs):
    for i in range(len(dirs)):
        if i == 0 and arr.raster[dirs[i]] == 16:
            hold.append(dirs[i])
        if i == 1 and arr.raster[dirs[i]] == 32:
            hold.append(dirs[i])
        if i == 2 and arr.raster[dirs[i]] == 64:
            hold.append(dirs[i])
        if i == 3 and arr.raster[dirs[i]] == 128:
            hold.append(dirs[i])
        if i == 4 and arr.raster[dirs[i]] == 1:
            hold.append(dirs[i])
        if i == 5 and arr.raster[dirs[i]] == 2:
            hold.append(dirs[i])
        if i == 6 and arr.raster[dirs[i]] == 4:
            hold.append(dirs[i])
        if i == 7 and arr.raster[dirs[i]] == 8:
            hold.append(dirs[i])
    return hold    
        
#    yes.append(hold)
#    if len(hold) > 0:
#        for x in hold:
#            dirs = makeDirections(x)
#            circleCell(dirs)
#    else:
#        return yes

   
# find the pour point cell with georasters
raster = 'D:/Projects/H2OShed_Tool/wsALSS-1065/fdr'
NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(raster)
arr = gr.from_file(raster)

(xmin, xsize, x, ymax, y, ysize) = arr.geot

pt = gpd.read_file('D:/Projects/H2OShed_Tool/wsALSS-1065/PointShape.shp')
lon,lat = list(pt.geometry[0].coords)[0]

here = gr.map_pixel(lon, lat,xsize,ysize,xmin,ymax)
#arr.raster[here]

init = makeDirections(here)


hold = []


hold = circleCell(init)
for x in hold:
    init = makeDirections(x)
    circleCell(init)
        
hold.append(here)
out = np.zeros(arr.shape)
val = 47
for idx in hold:
    out[idx] = val
go = gr.GeoRaster(out,arr.geot, 0)
go.projection = Projection
go.datatype = DataType

go.to_tiff('D:/Projects/H2OShed_Tool/wsALSS-1065/yeah')


##############################################################################
# Notes

#appending to hold obj in the loop seems to work, but not likely the best way 
#to manage

#multiple pour points will probably find full-watersheds for each and then
#isolate which zones specific cells are unique and subtract the rest into other

#w/ lake polygon, could we just find cell which has greatest flow accum and run
#w/ the cells that accumulate to highest fac cell as well as those of the lake?


##############################################################################
# shape = (w x h)

#arr = np.array(range(48)).reshape(6,8)
#
#shp = arr.shape

# order is [col,row]

#pp = (3,3)
#arr[pp]

#ds = makeDirections(pp)
#for p in ds:
#    print arr[p]

#t = arr.raster.filled()
#t[-39,25]
#for x in t[:,25]:
#    print x
#    
#arr.map_pixel(lon,lat)
#
#arr.raster[38,25]

