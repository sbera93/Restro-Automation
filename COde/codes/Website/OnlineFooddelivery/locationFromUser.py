# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 20:33:04 2020

@author: ningesh
"""


import pandas as pd 
import numpy as np
import warnings
import operator
import os
import json

from math import radians, cos, sin, asin, sqrt 


warnings.filterwarnings('ignore')


def distance(lat1, lat2, lon1, lon2): 
      
    # The math module contains a function named 
    # radians which converts from degrees to radians. 
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2) 
       
    # Haversine formula  
    dlon = lon2 - lon1  
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  
    c = 2 * asin(sqrt(a))  
     
    # Radius of earth in kilometers. Use 3956 for miles 
    r = 6371
       
    # calculate the result 
    return(c * r) 
      
      
def lattilongilocation(lat1,lon1):

    place_titles = pd.read_csv('geoplaces2.csv')
    place_titles.head()

    dflatilongi=place_titles[['placeID','latitude','longitude','name']]

    alldatasorting={}
    alldatawithlatlong={}
    for ik in range(len(dflatilongi)):
        lati22=dflatilongi['latitude'][ik]
        longi22=dflatilongi['longitude'][ik]
        opoflat=distance(lat1, lati22, lon1, longi22)
        locationid=dflatilongi['placeID'][ik]
        name=dflatilongi['name'][ik]
        alldatasorting[locationid]=opoflat
        alldatawithlatlong[locationid]=str(lati22)+"_"+str(longi22)+"_"+name

    sorted_d = sorted(alldatasorting.items(), key=operator.itemgetter(1))


    nearby=10
    keyvalue=[]
    for i in range(10):
        print(alldatawithlatlong[sorted_d[i][0]])
        keyvalue.append(alldatawithlatlong[sorted_d[i][0]])
    
    
    python2json = json.dumps(keyvalue)
    print(python2json)
    return python2json
