# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:55:48 2017

@author: Rdebbout
"""

import os
import numpy as np
import geopandas as gpd
import georasters as gr

DIRS = {0:16,1:32,2:64,3:128,4:1,5:2,6:4,7:8}

def ringCells(p):
    '''
    '''
    zero = (p[0],p[1]+1)
    one = (p[0]+1,p[1]+1)
    two = (p[0]+1,p[1])
    three = (p[0]+1,p[1]-1)
    four = (p[0],p[1]-1)
    five = (p[0]-1,p[1]-1)
    six = (p[0]-1,p[1])
    seven = (p[0]-1,p[1]+1)
    return [zero,one,two,three,four,five,six,seven]

def evalRing(ring,ras):
    '''
    '''
    for c in range(len(ring)):
        if c == 0 and ras.raster[ring[c]] == 16:
            hold.append(ring[c])
        if c == 1 and ras.raster[ring[c]] == 32:
            hold.append(ring[c])
        if c == 2 and ras.raster[ring[c]] == 64:
            hold.append(ring[c])
        if c == 3 and ras.raster[ring[c]] == 128:
            hold.append(ring[c])
        if c == 4 and ras.raster[ring[c]] == 1:
            hold.append(ring[c])
        if c == 5 and ras.raster[ring[c]] == 2:
            hold.append(ring[c])
        if c == 6 and ras.raster[ring[c]] == 4:
            hold.append(ring[c])
        if c == 7 and ras.raster[ring[c]] == 8:
            hold.append(ring[c])
    return hold   
 
    
def evalRing(ring,ras):
    '''
    '''
    for c in DIRS:
        if ras.raster[ring[c]] == DIRS[c]:
            hold.append(ring[c])
    return hold 


def Watershed(fdrf,ptf,val=47):
    ''' 2-D Array (row,col)
    '''  
    NDV, xsize, ysize, tf, Projection, DataType = gr.get_geo_info(fdrf)
    arr = gr.from_file(fdrf)
    (xmin, xsize, x, ymax, y, ysize) = arr.geot
    pt = gpd.read_file(ptf)
    lon,lat = list(pt.geometry[0].coords)[0]
    here = gr.map_pixel(lon, lat,xsize,ysize,xmin,ymax)    
    init = ringCells(here)
    hold = []
    hold = evalRing(init,arr)
    for x in hold:
        init = ringCells(x)
        hold = evalRing(init,arr)     
    hold.append(here)
    
    # try to update tf and shrink array
    dd = np.array(hold)
    r_min, col_min = np.amin(dd,axis=0)
    r_max, col_max = np.amax(dd,axis=0)
#    # below is for creating array after tranform adjust
#    # may be too intensive to justify
#    (r_max - r_min, col_max - col_min)

    # shift transform to reduce NoData in the output raster
    shifted_tf = (tf[0] + r_min * tf[-1],tf[1],tf[2],tf[3] - col_min * tf[1], tf[4],tf[5])
    # insert val into the cells of the raster
    out = np.zeros(arr.shape)
    for idx in hold:
        out[idx] = val
        
    new = out[r_min:r_max,col_min:col_max]
    
    go = gr.GeoRaster(new,shifted_tf, 0)
    go.projection = Projection
    go.datatype = DataType
    
    fn = os.path.basename(ptf).split('.')[0]   
    loc = os.path.dirname(ptf)
    go.to_tiff('{}/{}_watershed_ed'.format(loc,fn))

if __name__ == '__main__':
    flow = '/home/rick/projects/splitCats/fdr.tif'
    ptfn = '/home/rick/projects/splitCats/point_5070.shp'
    Watershed(flow,ptfn,55)
    
    
    

#gdalwarp -q -cutline /home/rick/projects/splitCats/cat_5070.shp 
#-tr 30.0 30.0 -of GTiff -co COMPRESS=LZW  
#/media/rick/gitSum/NHDPlusv21/NHDPlusPN/NHDPlus17/NHDPlusFdrFac17c/fdr
#/home/rick/projects/splitCats/fdr2.tif  
##############################################################################
#kk = []

#for x, y in zip((range(0,10)),(range(10,20))):
#    kk.append((x,y))
#    
#mm = []
#for x, y in zip((range(0,10)),(range(20,30))):
#    mm.append((x,y))
#    
#yy = mm[:3]
#yy[0] = (0,20)
#
#import numpy as np  # this is where you use pandas!
#
#rr = np.array(mm)
#dd = np.array(yy)

# sort tuples on x val

# try solution from the NHD Lakes QA script

#dd in rr
#
#import pandas as pd
#
#ww = pd.DataFrame(dd, columns=['lon','lat'], index=[47 for i in range(len(dd))])
#aa = pd.DataFrame(rr, columns=['lon','lat'])

# stack

# copy

# drop_duplicates -- iterate here


# would it always be he smallest one that gets the val? ..yes!

# index DF with val (COMID), separate and make 
# one table w/ dups dropped to iterate

# hold dict of key=COMID, val=length of retained array thru 
# evalRing process to select the one to keep

# find all of the indexes in the DF where x/y exist,
# append/hold that index in new DF/drop from existing

# can I have a DF with index duplicated, like with UID??
##############################################################################
# Notes  !!!!! USE queues !!!!!!!!!!!!!!!!! revolve array of tuples...........

# sort length for each zone and process shortest ----> longest, slicing/deleting as you go

# find array coords of raster zone perimeters
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

#ds = ringCells(pp)
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

