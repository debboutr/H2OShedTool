# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:55:48 2017

@author: Rdebbout
"""
import numpy as np
import rasterio as rs
import georasters as gr

# shape = (w x h)

arr = np.array(range(48)).reshape(6,8)

shp = arr.shape

# order is [col,row]

print np.where(arr==42)

# find the pour point cell
pp = (3,3)
arr[pp]

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
    
ds = makeDirections(pp)
for p in ds:
    print arr[p]