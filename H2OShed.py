# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:55:48 2017

@author: Rdebbout
"""

import os
import gdal
import numpy as np
import pysal as ps
import pandas as pd
import geopandas as gpd
import georasters as gr

hold = []
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
    for c in DIRS:
        if ras.raster[ring[c]] == DIRS[c]:
            hold.append(ring[c])
    return hold 

def makeRat(fn):
    '''
    __author__ =  "Matt Gregory <matt.gregory@oregonstate.edu >"
    Adds a Raster Attribute Table to the .tif.aux.xml file, then passes those
    values to rat_to_df function to return the RAT in a pandas DataFrame.

    Arguments
    ---------
    fn               : raster filename
    '''
    ds = gdal.Open(fn)
    rb = ds.GetRasterBand(1)
    nd = rb.GetNoDataValue()
    data = rb.ReadAsArray()
    # Get unique values in the band and return counts for COUNT val
    u = np.array(np.unique(data, return_counts=True))
    #  remove NoData value
    u = np.delete(u, np.argwhere(u==nd), axis=1)
    
    # Create and populate the RAT
    rat = gdal.RasterAttributeTable()
    rat.CreateColumn('Value', gdal.GFT_Integer, gdal.GFU_Generic)
    rat.CreateColumn('Count', gdal.GFT_Integer, gdal.GFU_Generic)
    for i in range(u[0].size):
        rat.SetValueAsInt(i, 0, int(u[0][i]))
        rat.SetValueAsInt(i, 1, int(u[1][i]))
    
    # Associate with the band
    rb.SetDefaultRAT(rat)
    
    # Close the dataset and persist the RAT
    ds = None 
        #return the rat to build DataFrame
    df = rat_to_df(rat)
    return df
       
##############################################################################


def rat_to_df(in_rat):
    """
    __author__ =  "Matt Gregory <matt.gregory@oregonstate.edu >"
    Given a GDAL raster attribute table, convert to a pandas DataFrame
    Parameters
    ----------
    in_rat : gdal.RasterAttributeTable
        The input raster attribute table
    Returns
    -------
    df : pd.DataFrame
        The output data frame
    """
    # Read in each column from the RAT and convert it to a series infering
    # data type automatically
    s = [pd.Series(in_rat.ReadAsArray(i), name=in_rat.GetNameOfCol(i))
         for i in xrange(in_rat.GetColumnCount())]

    # Concatenate all series together into a dataframe and return
    return pd.concat(s, axis=1)
       
##############################################################################

def DF2dbf(df, dbf_path, my_specs=None):
    '''
    Convert a pandas.DataFrame into a dbf.

    __author__  = "Dani Arribas-Bel <darribas@asu.edu> "
    ...

    Arguments
    ---------
    df          : DataFrame
                  Pandas dataframe object to be entirely written out to a dbf
    dbf_path    : str
                  Path to the output dbf. It is also returned by the function
    my_specs    : list
                  List with the field_specs to use for each column.
                  Defaults to None and applies the following scheme:
                    * int: ('N', 14, 0)
                    * float: ('N', 14, 14)
                    * str: ('C', 14, 0)
    '''
    if my_specs:
        specs = my_specs
    else:
        type2spec = {int: ('N', 20, 0),
                     np.int64: ('N', 20, 0),
                     float: ('N', 36, 15),
                     np.float64: ('N', 36, 15),
                     str: ('C', 14, 0),
                     np.int32: ('N', 14, 0)
                     }
        types = [type(df[i].iloc[0]) for i in df.columns]
        specs = [type2spec[t] for t in types]
    db = ps.open(dbf_path, 'w')
    db.header = list(df.columns)
    db.field_spec = specs
    for i, row in df.T.iteritems():
        db.write(row)
    db.close()
    return dbf_path    

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

    # shift transform to reduce NoData in the output raster
    shifted_tf = (tf[0] - r_min * tf[-1],tf[1],tf[2],tf[3] - col_min * tf[1], tf[4],tf[5])
    # insert val into the cells of the raster
    out = np.zeros(arr.shape)
    for idx in hold:
        out[idx] = val
        
    new = out[r_min:(r_max+1),col_min:(col_max+1)]   
    go = gr.GeoRaster(new,shifted_tf, 0)
    go.projection = Projection
    go.datatype = DataType    
    fn = os.path.basename(ptf).split('.')[0]   
    loc = os.path.dirname(ptf)
    go.to_tiff('{}/{}_watershed_small'.format(loc,fn))
    df = makeRat('{}/{}_watershed_small.tif'.format(loc,fn))
    DF2dbf(df, '{}/{}_watershed_small.tif.vat.dbf'.format(loc,fn))

if __name__ == '__main__':
    flow = 'D:/Projects/temp/junk/tool_test/fdr'
    ptfn = 'D:/Projects/temp/junk/tool_test/point.shp'
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

