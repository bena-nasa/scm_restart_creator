#!/usr/bin/env python

from Geolocation import Geolocation
from column_select import create_scm_restart
import sys
import numpy as np
import math
import time
import argparse

def parse_args():

   p = argparse.ArgumentParser(description='forcing_converter',formatter_class=argparse.RawDescriptionHelpFormatter)
   p.add_argument('input_restart',type=str,help='input file yaml file',default=None)
   p.add_argument('coord_file',type=str,help='input file yaml file',default=None)
   p.add_argument('lon',type=float,help='input file yaml file',default=None)
   p.add_argument('lat',type=float,help='input file yaml file',default=None)
   return vars(p.parse_args())

if __name__ == '__main__':
   sys.path.append(".")
   args = parse_args()
   input_restart = args['input_restart']
   coord_file = args['coord_file']
   lon = args['lon']
   lat = args['lat']
   lons = np.array([lon])
   lats = np.array([lat])
   geoloc = Geolocation(coord_file)

   lons = lons*math.pi/180.0
   lats = lats*math.pi/180.0
   face,ii,jj=geoloc.getIndices(lons,lats)
   print(face,ii,jj)
   create_scm_restart(input_restart,lon,lat,face[0],ii[0],jj[0])
