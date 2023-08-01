from netCDF4 import Dataset
import numpy as np
from datetime import datetime
import os

def create_scm_restart(input_restart,lon,lat,face,xi,yi):

    output_restart = os.path.basename(input_restart)
    ncFid = Dataset(input_restart,mode='r')
    cube_res = len(ncFid.dimensions['lon'])
    i_index = xi
    j_index = yi + (cube_res * face)
    ncFidOut = Dataset("scm_"+output_restart,mode='w',format='NETCDF4')
    unknown_dim1_size = None
    if 'unknown_dim1' in ncFid.dimensions:
       unknown_dim1_size = len(ncFid.dimensions['unknown_dim1'])
    lev_size = None
    if 'lev' in ncFid.dimensions:
       lev_size = len(ncFid.dimensions['lev'])
    edge_size = None
    if 'edge' in ncFid.dimensions:
       edge_size = len(ncFid.dimensions['edge'])

    time_size = None
    if 'time' in ncFid.dimensions:
       time_size = len(ncFid.dimensions['time'])
    if time_size != None:
       time_dim = ncFidOut.createDimension('time',time_size)
       time_var = ncFidOut.createVariable('time','i4',('time'))
       for att in ncFid.variables['time'].ncattrs():
          setattr(ncFidOut.variables['time'],att,getattr(ncFid.variables['time'],att))
       time_var[:] = ncFid.variables['time'][:]

    lon_dim = ncFidOut.createDimension('lon',1)
    lat_dim = ncFidOut.createDimension('lat',1)
    if lev_size != None:
       lev_dim = ncFidOut.createDimension('lev',lev_size)
    if edge_size != None:
       edge_dim = ncFidOut.createDimension('edge',edge_size)
    if unknown_dim1_size != None:
       unknown_dim1_dim = ncFidOut.createDimension('unknown_dim1',edge_size)

    lon_var = ncFidOut.createVariable('lon','f8',('lon'))
    setattr(ncFidOut.variables['lon'],'units','degrees_east')
    setattr(ncFidOut.variables['lon'],'long_name','longitude')
    lat_var = ncFidOut.createVariable('lat','f8',('lat'))
    setattr(ncFidOut.variables['lat'],'units','degrees_north')
    setattr(ncFidOut.variables['lat'],'long_name','latitude')
    lon_var[:] = lon
    lat_var[:] = lat

    if lev_size != None:
       lev_var= ncFidOut.createVariable('lev','f8',('lev'))
       for att in ncFid.variables['lev'].ncattrs():
         setattr(ncFidOut.variables['lev'],att,getattr(ncFid.variables['lev'],att))
       lev_var[:] = range(1,lev_size+1)
    if edge_size != None:
       edge_var= ncFidOut.createVariable('edge','f8',('edge'))
       for att in ncFid.variables['edge'].ncattrs():
         setattr(ncFidOut.variables['edge'],att,getattr(ncFid.variables['edge'],att))
       edge_var[:] = range(1,edge_size+1)

    exclude_vars = ['time','lon','lat','lev','edge','unknown_dim1']
    for var in ncFid.variables:
        if var not in exclude_vars:
           temp = ncFid.variables[var][:]
           dim_names = ncFid.variables[var].dimensions
           data_type = ncFid.variables[var].dtype
           tout = ncFidOut.createVariable(var,data_type,dim_names)
           for att in ncFid.variables[var].ncattrs(): 
               if att != "_FillValue":
                      setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
           field_size = ncFid.variables[var].ndim
           if field_size ==4: 
              tout[:,:,:,:] = temp[:,:,j_index,i_index]
           elif field_size ==3: 
              tout[:,:,:] = temp[:,j_index,i_index]
           elif field_size ==2: 
              tout[:,:] = temp[j_index,i_index]
           elif field_size ==1: 
              tout[:] = temp[:]

    ncFid.close()
    ncFidOut.close()
